import copy
import json
import os
import pandas as pd
import shutil
import spacy
import sys

from google.oauth2 import service_account
from googleapiclient import discovery


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from data.preparer import load_amazon_dataset
from data.preparer import load_film_dataset
from data.preparer import load_news_dataset
from data.preparer import load_youtube_dataset
from datetime import datetime
from synthesizer.gll import CONCEPT
from synthesizer.gll import ConceptWrapper
from synthesizer.gll import ConnectiveType
from synthesizer.gll import DELIMITER
from synthesizer.gll import ID
from synthesizer.gll import KeyType
from synthesizer.gll import Label
from synthesizer.parser import nlp
from synthesizer.synthesizer import Synthesizer
from verifier.DB import LF_DB
from verifier.DB import interactionDB
from verifier.modeler import Modeler
from verifier.translator import find_indices

# youtube - spam vs notspam 
# amazon - positive vs negative sentiment 
# film - comedy vs drama (wikipedia movie plots)
# news - gun politics or electronics forum posts

# MODE can be "Youtube" or "Amazon" or "Film" or "News"
MODE = "Youtube"
USER_ID = "testing"



if MODE == "Amazon":
    TASK_DESCRIPTION = "For the following task, you will be asked to create labeling functions to classify Amazon reviews as positive (5 stars) or negative (1 star)."
    labels = Label(name="Amazon Reviews Classification: Sentiment")
    labels.add_label(lname="negative")
    labels.add_label(lname="positive")

    df_train, df_dev, df_valid, df_test, df_test_heldout = load_amazon_dataset(delimiter=DELIMITER)

elif MODE =="Youtube":
    TASK_DESCRIPTION = "For the following task, you will be asked to create labeling functions to classify Youtube comments as SPAM (irrelevant or inappropriate messages sent on the Internet to a large number of recipients) or NOT SPAM."
    labels = Label(name="Youtube Comments Classification: Spam or Not Spam")
    labels.add_label(lname="NON-SPAM")
    labels.add_label(lname="SPAM")

    df_train, df_dev, df_valid, df_test, df_test_heldout = load_youtube_dataset(delimiter=DELIMITER)

elif MODE == "Film":
    TASK_DESCRIPTION = "You will practice using this tool by generating labeling functions that classify movie plot descriptions as DRAMA or COMEDY."
    labels = Label(name="Wikipedia plot summary classification: comedy or drama.")
    labels.add_label(lname="COMEDY")
    labels.add_label(lname="DRAMA")

    df_train, df_dev, df_valid, df_test, df_test_heldout = load_film_dataset()

elif (MODE == "News") or (MODE == "Debug"):
    TASK_DESCRIPTION = "You will practice using this tool by generating labeling functions that classify newsnet posts as belonging to the forum on GUNS or ELECTRONICS."
    labels = Label(name="Newsnet classification: guns or electronics.")
    labels.add_label(lname="ELECTRONICS")
    labels.add_label(lname="GUNS")

    df_train, df_dev, df_valid, df_test, df_test_heldout = load_news_dataset()

# pre-compute NER tags
from synthesizer.parser import nlp
with nlp.disable_pipes("tagger", "parser"):
    def ner_tags(row):
        doc = nlp(row.text)
        for ent in doc.ents:
            row[ent.label_] = (doc[ent.start-1].idx, doc[ent.end-2].idx + len(doc[ent.end-2].text))
        return row
    POSSIBLE_NER = ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']
    for NE in POSSIBLE_NER:
        df_train[NE] = False
        df_dev[NE] = False
    df_train = df_train.apply(ner_tags, axis=1)
    df_dev = df_dev.apply(ner_tags, axis=1)
    df_test_heldout = df_test_heldout.apply(ner_tags, axis=1)
print("DATASET SIZES:")
print("train: {}\ndev: {}\nvalid: {}\ntest: {}".format(len(df_train), len(df_dev), len(df_valid), len(df_test)))


all_concepts = ConceptWrapper()

modeler = Modeler(df_train, df_dev, df_valid, df_test, df_test_heldout)

stat_history = pd.DataFrame()
stats = {}

def get_labels():
    return labels.to_dict()


def get_connective():
    return ConnectiveType


def get_keytype():
    return KeyType


def get_all_concepts():
    return all_concepts.get_dict()


def create_concept(concept):
    if concept["name"] not in all_concepts.get_dict():
        all_concepts.add_element(name=concept['name'], elements=concept['tokens'])
        update_stats({"concept": concept['name'], "len": len(concept['tokens'])}, "create_concept")

def get_concept(cname):
    return all_concepts.get_elements(cname)

def update_tokens(cname, tokens):
    all_concepts.add_element(name=cname, elements=tokens)
    update_stats({"concept": cname, "len": len(tokens)}, "update_concept")
    if modeler.count > 0:
        modeler.apply_lfs()
        modeler.fit_label_model()
        global stats
        stats.update(modeler.get_label_model_stats())
        

def delete_concept(cname):
    all_concepts.delete_concept(cname)
    update_stats({"concept": cname}, "delete_concept")

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

    global tutorial_index, stat_history
    result = None

    demo_examples = [
        101, #subscribe
        248, # wow
        355, 
        233,
        215,
        394,
        479,
        164
        ]
    if (MODE == "Youtube") and (tutorial_index <= len(demo_examples)):
        if tutorial_index==0:
            update_stats({}, "begin")
        
        result = modeler.text_at(demo_examples[tutorial_index])
        tutorial_index += 1
    
    if result is None:
        result = modeler.next_text()
    
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

def lf_to_hash(lf_dict):
    def conditions_to_string(cond_list):
        conds = []
        for x in cond_list:
            conds.append("".join([str(val) for val in x.values()]))
        return "-".join(sorted(conds))
    lf_hash = ""
    for key, value in sorted(lf_dict.items()):
        if key == "Conditions":
            lf_hash += conditions_to_string(value)
        else:
            if key in ["Connective", "Direction", "Label", "Context"]:
                lf_hash += "_" + str(value)
    return lf_hash

def submit_interaction(interaction):
    index = interactionDB.add(interaction)
    text = interaction["text"]
    annotations = interaction["annotations"]
    label = int(interaction["label"])

    crnt_syn = Synthesizer(text, annotations, label, DELIMITER, all_concepts.get_dict())
    crnt_instances = crnt_syn.run()

    result = {}
    for i in range(len(crnt_instances)):
        crnt_instances[i]["interaction_idx"] = index
        # TODO LFID should be unique given set of conditions, etc
        lf_hash = lf_to_hash(crnt_instances[i])
        crnt_instances[i]["name"] = lf_hash
        result[lf_hash] = crnt_instances[i]
    update_stats({**interaction, "len": len(annotations)}, "submit_interaction")
    update_stats({"suggested_lf_ids": list(result.keys())}, "suggest_lfs")
    return result


def submit_instances(lf_dicts):
    update_stats({"lf_ids": list(lf_dicts.keys())},"submit_lfs")
    new_lfs = LF_DB.add_lfs(lf_dicts, all_concepts)
    modeler.add_lfs(new_lfs)

    modeler.fit_label_model()
    global stats
    stats.update(modeler.get_label_model_stats())
    return get_lf_stats()


def get_interaction_idx(idx):
    update_stats({"index": idx}, "get_interaction_idx")
    return interactionDB.get(idx)

def delete_lfs(lf_ids):
    for lf_id in lf_ids:
        LF_DB.deactivate(lf_id)
    lf_count = modeler.remove_lfs(lf_ids)
    update_stats({"lf_ids": lf_ids}, "delete_lfs")

    global stats, stat_history

    if lf_count > 0:
        modeler.fit_label_model()

        stats.update(modeler.get_label_model_stats())


def get_stats():
    """return statistics over the development set"""
    update_stats({**stats, "data": "dev"}, "stats")
    return stats

def get_lf_stats():
    """return lf-specific statistics over the training and dev sets"""
    stats_df = modeler.analyze_lfs()
    stats = {}
    if stats_df is not None:
        stats = json.loads(stats_df.to_json(orient="index"))
    res = LF_DB.update(stats)
    return res


def get_logreg_stats():
    stats = modeler.train()
    update_stats({**stats, "data": "test"}, "train_model")
    return stats

def get_lf_label_examples(lf_id):
    examples = modeler.lf_examples(lf_id)
    mistakes = modeler.lf_mistakes(lf_id)
    concepts = all_concepts.get_dict()
    update_stats({"lf_id": lf_id, "examples": len(examples), "mistakes": len(mistakes)}, "get_lf_label_examples")
    for result in [examples, mistakes]:
        for ex in result:
            annotations = []
            for cond in LF_DB.get(lf_id)["Conditions"]:
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
    return {"examples": examples, "mistakes": mistakes}

def save_model(data):
    update_stats({**stats, "data": "dev"}, "final_stats")
    dirname = USER_ID + '/' + MODE
    try:
        os.mkdir(USER_ID)
    except FileExistsError:
        pass
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

    modeler.save(dirname)

    LF_DB.save(dirname)

    interactionDB.save(dirname)

    all_concepts.save(dirname)

    global stat_history
    stat_history["time_delta"] = stat_history["time"] - stat_history["time"].iloc[0]
    stat_history["tool"] = "Ruler"
    stat_history["task"] = MODE
    stat_history["user"] = USER_ID
    stat_history.to_csv(os.path.join(dirname, "statistics_history.csv"))

    zipfile = USER_ID + '_' + MODE

    shutil.make_archive(zipfile, 'zip', base_dir=dirname)

    print("Files saved to directory " + dirname)
    print('zipped to ' + zipfile)

def load_model(dirname: str):
    all_concepts.load(dirname)
    print(all_concepts.get_dict())

    LF_DB.load(dirname, all_concepts)

    interactionDB.load(dirname)
    global stat_history
    stat_history = pd.read_csv(os.path.join(dirname, "statistics_history.csv"))

    modeler.load(dirname)
    modeler.apply_lfs()


def update_stats(new_stats_dict: dict, action: str):
    pass