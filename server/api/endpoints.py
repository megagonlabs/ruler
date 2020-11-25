import copy
import json
import os
import pandas as pd
import shutil
import spacy
import sys
import threading
import time
import zipfile

from flask import send_file
from io import BytesIO
from numpy import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from api.active_sampler import next_text as get_next_text
from api.project import Project
from api.project import add_file
from datetime import datetime
from snorkel.labeling import filter_unlabeled_dataframe
from snorkel.utils import preds_to_probs
from synthesizer.gll import CONCEPT
from synthesizer.gll import ConnectiveType
from synthesizer.gll import DELIMITER
from synthesizer.gll import KeyType
from synthesizer.parser import nlp
from synthesizer.synthesizer import Synthesizer
from verifier import eval_utils
from verifier.eval_utils import detect_duplicate_labeling_signature
from verifier.interaction_db import interactionDB
from verifier.keraslogreg import KerasLogReg
from verifier.labeling_function import make_lf, lf_to_hash
from verifier.modeler import Modeler
from verifier.translator import find_indices


# fetch concepts wrapper, modeler, and label types
project = Project()

# DataFrame to store statistics over time
stat_history = pd.DataFrame()
stats = {}  

end_model = None

########################################
#############     LABELS   #############
########################################

def get_labels():
    """Get pre-defined labels for this project
    """
    return project.labels.to_dict()

def post_labels(labels: dict):
    """Define labels of a project
    
    Args:
        labels (dict): {lname(string): value (int)}
    """
    project.add_labels(labels)


########################################
#############   DATASETS   #############
########################################

def listdir(dirname: str):
    def should_ignore(file):
        if file.startswith('.'):
            return True
        if file.endswith(".zip"):
            return True
        if file.endswith(".md"):
            return True
        return False
    return sorted([f for f in os.listdir(dirname) if not should_ignore(f)], key=lambda f: f.lower())

def get_datasets():
    """List available datasets"""
    return listdir('datasets')

def get_dataset(dataset_uuid: str):
    """List files in a given dataset"""
    return listdir(os.path.join('datasets', dataset_uuid))

def post_data(file, dataset_uuid: str, label_col="label", text_col="text"):
    """Add file to a new or existing dataset
    
    Args:
        file (file): csv file
        dataset_uuid (str): ID of the dataset
        label_col (str, optional): name of the column with label data
        text_col (str, optional): name of the column with text data
    
    Returns:
        list(str): The available datasets
    """
    add_file(file, dataset_uuid, label_col, text_col)
    return get_datasets()

def select_dataset(config: dict):
    dataset_uuid = config.get('dataset_uuid')
    workThread = threading.Thread(target=lambda: project.prep_datasets(dataset_uuid))
    workThread.start()

def progress():
    """Get progress of the project launch (data preprocessing and model launching)
    
    Returns:
        float: a number from 0 to 1
    """
    return project.progress()


########################################
###########  MODELS  ###################
########################################
def get_models():
    """List available models"""
    return listdir('models')

def select_model(config: dict):
    model_name = config.get("model_name")
    model_path = os.path.join("models", model_name)
    project.load_model(model_path)

def create_new_model(model_name):
    project.set_name(model_name)
    project.modeler = Modeler(cardinality=project.cardinality)
    project.save(os.path.join("models", model_name))
    return get_models()

########################################
############# GLL OPERATORS ############
########################################
def get_connective():
    """
    Returns:
        Dictionary: the connectives an LF can use between conditions
           ex: AND, OR
    """
    return ConnectiveType

def get_keytype():
    """
    Returns:
        Dictionary: the types of conditions an LF can have 
           ex: Token, Regex, Concept
    """
    return KeyType

########################################
###########     CONCEPTS   #############
########################################

def get_all_concepts():
    """
    Returns:
        Dictionary: all the concepts that have been defined for this task
           Concepts contain elements that can be a token or a regular expression, 
           case-sensitive or not
    """
    return project.concepts.get_dict()

def create_concept(concept: dict):
    if concept["name"] not in project.concepts.get_dict():
        project.concepts.add_element(name=concept['name'], elements=concept['tokens'])
        update_stats({"concept": concept['name'], "len": len(concept['tokens'])}, "create_concept")

def get_concept(cname: str):
    return project.concepts.get_elements(cname)

def update_concept(cname: str, tokens: list):
    """Update the elements of a concept, and re-apply LFs since they may have changed
    """
    modeler = project.modeler
    project.concepts.add_element(name=cname, elements=tokens)
    update_stats({"concept": cname, "len": len(tokens)}, "update_concept")
    # update uuid on LFs that use this concept
    modeler.update_concept(cname)
    modeler.fit(project.train)
    return project.concepts.get_elements(cname)
        

def delete_concept(cname: str):
    project.concepts.delete_concept(cname)
    update_stats({"concept": cname}, "delete_concept")
    # delete LFs that use this concept
    project.modeler.update_concept(cname, deleted=True)


########################################
##### ANNOTATIONS OVER TEXT ############
########################################

def make_annotations(cond_dict: dict, text: str, concept=0):
    """Given a text and a condition, return all annotations over the text for that condition
    
    Args:
        k (string): a key describing the type of span to look for
        v (int): Describes the type of the key (ex: a token or regular expression)
        text (string): Text to annotate
        concept (string, optional): Concept to associate the annotation with, or 0 for no concept.
    
    Returns:
        list(dict): all possible annotations on the text for this condition
    """
    annotations = []
    for start, end in find_indices(cond_dict, text):
        annotations.append({
            "id": start,
            "start_offset": start, 
            "end_offset": end, 
            "label": concept,
            "link": None,
            "origin": cond_dict["string"]
        })
    return annotations

def NER(text):
    """Find all spacy-recognized named entities in the text
    
    Args:
        text (string)
    
    Yields:
        dict: Description of the named entity
    """
    with nlp.disable_pipes("tagger", "parser"):
        doc = nlp(text)
        for ent in doc.ents:
             yield {
                "id": '{}_{}'.format(ent.start, ent.label),
                "start_offset": doc[ent.start].idx, 
                "end_offset": doc[ent.end-1].idx + len(doc[ent.end-1].text), 
                "label": ent.label_,
                "explanation": spacy.explain(ent.label_)
            }

def filter_annotations(annotations):
    """Make sure annotations are in order and non-overlapping
    
    Args:
        annotations (list(dict))
    
    Returns:
       (list(dict)): a subset of the provided annotations
    """
    annotations = sorted(annotations, key=lambda x: (x["start_offset"], -x["end_offset"]))
    filtered_ann = []
    left_idx = 0
    for ann in annotations:
        if ann["start_offset"] >= left_idx:
            filtered_ann.append(ann)
            left_idx = ann["end_offset"]
    return filtered_ann

SHOW_EXPLANATION_TEXT = False
tutorial_index = 0
if SHOW_EXPLANATION_TEXT:
    tutorial_index = -1
    

def next_text(annotate_concepts=True, annotate_NER=True):
    result = get_next_text(project.modeler, project.train)

    if annotate_concepts:
        annotations = []
        for concept, tokens in get_all_concepts().items():
            for token in tokens:
                annotations.extend(make_annotations(token, result["text"], concept))
        annotations = sorted(annotations, key=lambda x: (x["start_offset"], -x["end_offset"]))
        result["annotations"] = []
        left_idx = 0
        result["annotations"] = filter_annotations(annotations)
    if annotate_NER:
        result["NER"] = list(NER(result["text"]))
    result["index"] = interactionDB.add(result)
    update_stats(result, "next_text")
    return result

def submit_interaction(interaction: dict):
    """Submit a label and annotations over a text example, and produce suggested LFs
    
    Args:
        interaction (dict): Must contain 'text' 'annotations' and 'label'
    
    Returns:
        dict: key (lf hash), value (lf)
    """
    index = interactionDB.add(interaction)
    text = interaction["text"]
    annotations = interaction["annotations"]
    label = int(interaction["label"])

    crnt_syn = Synthesizer(text, annotations, label, DELIMITER, project.concepts.get_dict())
    crnt_instances = crnt_syn.run()

    result = {}
    for i in range(len(crnt_instances)):
        crnt_instances[i]["interaction_idx"] = index
        # generate unique string representing this lf
        lf_hash = lf_to_hash(crnt_instances[i])
        crnt_instances[i]["name"] = lf_hash
        result[lf_hash] = crnt_instances[i]
    update_stats({**interaction, "len": len(annotations)}, "submit_interaction")
    update_stats({"suggested_lf_ids": list(result.keys())}, "suggest_lfs")
    return result


def submit_instances(lf_dicts: dict):
    """TODO docstring
    """
    modeler = project.modeler
    
    new_lfs = [make_lf(lf_dict, project.concepts) for lf_dict in lf_dicts.values()]
    modeler.add_lfs(new_lfs)

    update_stats({"lf_ids": [lf.name for lf in new_lfs]}, "submit_lfs")
    modeler.fit(project.train)
    lf_stats = get_lf_stats()
    return lf_stats


def get_interaction_idx(idx: int):
    update_stats({"index": idx}, "get_interaction_idx")
    return interactionDB.get(idx)

def delete_lfs(lf_ids: list):
    modeler = project.modeler
    modeler.remove_lfs(lf_ids)
    modeler.fit(project.train)

    update_stats({"lf_ids": lf_ids}, "delete_lfs")

def get_stats():
    """return statistics over the development set"""
    stats = eval_utils.get_stats_from_modeler(project.modeler, project.dev)
    update_stats({**stats, "data": "dev"}, "stats")
    return stats

def get_lf_stats():
    """return lf-specific statistics over the training and dev sets"""
    modeler = project.modeler

    stats_df = eval_utils.lf_analysis(project.modeler, project.train, project.dev)
    stats = {}
    if stats_df is not None:
        stats = json.loads(stats_df.to_json(orient="index"))
    modeler.record_stats(stats)
    return stats


def get_logreg_stats():
    global end_model
    cardinality = project.modeler.cardinality
    if end_model is None:
        end_model = KerasLogReg(cardinality=cardinality)

    X_valid = project.valid['text'].values
    Y_valid = preds_to_probs(project.valid['label'].values, cardinality)

    modeler = project.modeler
    L = modeler.apply(project.train)
    y = modeler.predict(project.train)
    df_train_filtered, probs_train_filtered = filter_unlabeled_dataframe(
        X=project.train.df, y=y, L=L
    )

    end_model.fit(df_train_filtered.text.values, probs_train_filtered, X_valid, Y_valid)

    preds = end_model.predict(project.test['text'].values)
    ground_truth = project.test['label'].values

    stats = eval_utils.get_stats_from_probs(preds, ground_truth)
    update_stats({**stats, "data": "test"}, "train_model")
    return stats

def get_lf_label_examples(lf_id):
    """For the lf with given ID, get labeled examples
    
    Args:
        lf_id (str)
    
    Returns:
        dict: {
                "examples": labeled examples from training set, 
                "mistakes": incorrectly labeled exampels from development set
              }
    """
    modeler = project.modeler
    lf = modeler[lf_id]
    examples = [{"text": e} for e in eval_utils.lf_examples(lf, project.train)]
    if hasattr(project, "dev"):
        mistakes = [{"text": e} for e in eval_utils.lf_mistakes(lf, project.dev)]
    else:
        mistakes = []

    concepts = project.concepts.get_dict()
    update_stats({"lf_id": lf_id, "examples": len(examples), "mistakes": len(mistakes)}, "get_lf_label_examples")
    for result in [examples, mistakes]:
        for ex in result:
            if lf.has_GLL_repr():
                # the labelling function has a GLL representation
                annotations = []
                for cond in lf.GLL_repr()["Conditions"]:
                    k = cond["string"]
                    v = cond["type"]
                    if v == KeyType[CONCEPT]:
                        # match a concept
                        assert k in concepts.keys()
                        for token_dict in concepts[k]:
                            annotations.extend(make_annotations(token_dict, ex["text"], k))
                    else:
                        annotations.extend(make_annotations(cond, ex["text"], 0))
                ex['annotations'] = filter_annotations(annotations)
            else: # it's a custom labeling function, we don't need to annotate
                ex["annotations"] = []
    return {"examples": examples, "mistakes": mistakes}

def zip_model(dirname=None):
    if dirname is None:
        dirname = "models/" + project.name + '_ruler_model'
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    modeler = project.modeler
    modeler.save(dirname)
    interactionDB.save(dirname)
    project.concepts.save(os.path.join(dirname, "concept_collection.json"))

    shutil.make_archive(dirname, 'zip', base_dir=dirname)

def download_model():
    """Save model to zip file and send to user's browser
    """
    dirname = "models/" + project.name
    zip_model(dirname=dirname)
    return send_file('../' + dirname + '.zip', as_attachment=True)

def download_data():
    dirname = "datasets/"


def load_model(dirname: str):
    project.concepts.load(dirname)

    interactionDB.load(dirname)
    global stat_history
    stat_history = pd.read_csv(os.path.join(dirname, "statistics_history.csv"))
    modeler = project.modeler
    modeler.load(dirname)


def update_stats(new_stats_dict: dict, action: str):
    pass
