from datetime import datetime
import json
import os
import pandas as pd
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from data.preparer import load_youtube_dataset

from synthesizer.gll import ConceptWrapper
from synthesizer.gll import ConnectiveType
from synthesizer.gll import DELIMITER
from synthesizer.gll import ID, CONCEPT
from synthesizer.gll import KeyType
from synthesizer.gll import Label
from synthesizer.synthesizer import Synthesizer
from verifier.DB import LF_DB
from verifier.DB import interactionDB
from verifier.modeler import Modeler
from verifier.translator import find_indices

# youtube - spam vs notspam 
MODE = "Youtube"
USER_ID = "guest"

elif MODE =="Youtube":
    TASK_DESCRIPTION = "For the following task, you will be asked to write 10 labeling functions to classify Youtube comments as SPAM (irrelevant or inappropriate messages sent on the Internet to a large number of recipients) or NOT SPAM."
    labels = Label(name="Youtube Comments Classification: Spam or Not Spam")
    labels.add_label(lname="NON-SPAM")
    labels.add_label(lname="SPAM")

    df_train, df_dev, df_valid, df_test = load_youtube_dataset(delimiter=DELIMITER)

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


all_concepts = ConceptWrapper()

modeler = Modeler(df_train, df_dev, df_valid, df_test)

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
    all_concepts.add_element(name=concept['name'], elements=concept['tokens'])


def get_concept(cname):
    return all_concepts.get_elements(cname)


def update_tokens(cname, tokens):
    all_concepts.add_element(name=cname, elements=tokens)


def delete_concept(cname):
    all_concepts.delete_concept(cname)

def make_annotations(k, v, text, concept=0):
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
    for start, end in find_indices(k, v, text):
        annotations.append({
            "id": start,
            "start_offset": start, 
            "end_offset": end, 
            "label": concept,
            "link": None})
    return annotations

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

def next_text(annotate_concepts=True):
    text = modeler.next_text()
    global tutorial_index
    if tutorial_index==-1:
        tutorial_index += 1
        return {
            "text": TASK_DESCRIPTION+"\n You have 30 minutes to create a set of labeling functions that balances accuracy (f1/recall/precision) as well as training set size. You may consult the internet.\n Click 'skip' when you are ready to begin.", 
            "annotations": []}
    # elif (MODE == "Film") and (tutorial_index < len(tutorial_texts)):
    #     text = tutorial_texts[tutorial_index]
    #     tutorial_index += 1
    elif tutorial_index==0:
        # record start time
        tutorial_index += 1
        stat_history.append({"time": datetime.now(), "num_lfs": 0}, ignore_index=True)

    result = {"text": text}
    if annotate_concepts:
        annotations = []
        for concept, tokens in get_all_concepts().items():
            for k, v in tokens.items():
                annotations.extend(make_annotations(k, v, text, concept))
        annotations = sorted(annotations, key=lambda x: (x["start_offset"], -x["end_offset"]))
        result["annotations"] = []
        left_idx = 0
        result["annotations"] = filter_annotations(annotations)
    return result

def lf_to_hash(lf_dict):
    def conditions_to_string(cond_list):
        conds = []
        for x in cond_list:
            token, key = list(x.items())[0]
            conds.append(str(token) + str(key))
        return "-".join(conds)
    lf_hash = ""
    for key, value in lf_dict.items():
        if key == "Conditions":
            lf_hash += conditions_to_string(value)
        else:
            lf_hash += "_" + str(value)
    return lf_hash

def submit_interaction(interaction):
    index = interactionDB.add(interaction)
    text_origin = interaction["text_origin"]
    annotations = interaction["annotations"]
    label = int(interaction["label"])

    crnt_syn = Synthesizer(text_origin, annotations, label, DELIMITER, all_concepts.get_dict())
    crnt_instances = crnt_syn.run()

    result = {}
    for i in range(len(crnt_instances)):
        crnt_instances[i]["interaction_idx"] = index
        # TODO LFID should be unique given set of conditions, etc
        lf_hash = lf_to_hash(crnt_instances[i])
        crnt_instances[i]["name"] = lf_hash
        if not lf_hash in LF_DB:
            result[lf_hash] = crnt_instances[i]
    return result


def submit_instances(lf_dicts):
    new_lfs = LF_DB.add_lfs(lf_dicts, all_concepts)

    modeler.add_lfs(new_lfs)

    modeler.apply_lfs()

    modeler.fit_label_model()
    global stats
    stats.update(modeler.get_label_model_stats())
    stat_history.append({"time": datetime.now(), "num_lfs": len(LF_DB)}.update(stats))

    return get_lf_stats()


def get_interaction_idx(idx):
    return interactionDB.get(idx)

def delete_lfs(lf_ids):
    for lf_id in lf_ids:
        LF_DB.delete(lf_id)
    lf_count = modeler.remove_lfs(lf_ids)

    global stats

    if lf_count > 0:
        modeler.apply_lfs()
        modeler.fit_label_model()

        stats.update(modeler.get_label_model_stats())
        stat_history.append({"time": datetime.now(), "num_lfs": len(LF_DB)}.update(stats))


def get_stats():
    """return statistics over the development set"""
    return {**stats}

def get_lf_stats():
    """return lf-specific statistics over the training and dev sets"""
    stats_df = modeler.analyze_lfs()
    if stats_df is not None:
        stats = json.loads(stats_df.to_json(orient="index"))
        res = LF_DB.update(stats)
        return res
    return {}

def get_lf_label_examples(lf_id):
    result = modeler.lf_examples(lf_id)
    concepts = all_concepts.get_dict()
    for ex in result:
        for cond in LF_DB.get(lf_id)["Conditions"]:
            for k, v in cond.items():
                annotations = []
                if v == KeyType[CONCEPT]:
                    # match a concept
                    assert k in concepts.keys()
                    for crnt_token, crnt_type in concepts[k].items():
                        annotations.extend(make_annotations(crnt_token, crnt_type, ex["text"], k))
                else:
                    annotations.extend(make_annotations(k, v, ex["text"], 0))
        ex['annotations'] = filter_annotations(annotations)
    return result

def save_model(data):
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

    stat_history.to_csv(os.path.join(dirname, "statistics_history.csv"))

def load_model(dirname: str):
    modeler.load(dirname)
    modeler.apply_lfs()

    LF_DB.load(dirname)

    interactionDB.load(dirname)

    all_concepts.load(dirname)
    
