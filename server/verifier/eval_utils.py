# evaluation utilities
import numpy as np
import pandas as pd
import sys

from sklearn import metrics
from snorkel.utils import probs_to_preds
from snorkel.labeling import filter_unlabeled_dataframe

def lf_analysis(modeler, train_data, dev_data=None):
    # get analysis over training and dev sets
    if not modeler.has_lfs():
        print("lf_analysis called with no LFs")
        return None
    analys_train = modeler.analyze_lfs(train_data)
    stats_to_include = ["Polarity", "Coverage", "Conflicts", "Overlaps"]   
    analys_train.rename(columns = {
        stat: stat + " Train" for stat in stats_to_include
    }, inplace = True)

    if dev_data is not None:
        # if development data is available
        analys_dev = modeler.analyze_lfs(dev_data, labels=dev_data["label"].values)
        analys_dev.rename(columns = {
            stat: stat + " Dev." for stat in stats_to_include
        }, inplace = True)
        analys_dev.drop(["j"], axis=1, inplace=True)

        # Merge these analyses
        analysis = analys_train.merge(analys_dev, how="inner", left_index=True, right_index=True)
    else:
        analysis = analys_train

    # Add GLL metadata
    analysis = pd.concat([analysis, modeler.GLL_repr()], axis=1)
    
    # Add weights
    analysis['Weight'] = modeler.get_weights()

    # Field "LABEL" may be empty for custom functions. We can fill it using observed labels.
    analysis["Label"].fillna(analysis["Polarity Train"])

    # Detect duplicate labeling signatures
    analysis["Duplicate"] = None
    for dupe, OG in detect_duplicate_labeling_signature(modeler, [train_data, dev_data]).items():
        print("Duplicate labeling signature detected")
        print(dupe, OG)
        analysis.at[dupe, "Duplicate"] = OG

    return analysis

def lf_examples(labeling_function, data, max_examples = 5):
    label_vector = apply_one_lf(labeling_function, data)
    examples = data[label_vector!=-1]
    samples = examples.sample(min(max_examples, len(examples)), random_state=13)
    return samples["text"].values

def lf_mistakes(labeling_function, data, max_examples = 5):
    label_vector = apply_one_lf(labeling_function, data)
    examples = data[(label_vector!=-1) & (label_vector != data["label"].values)]
    samples = examples.sample(min(max_examples, len(examples)), random_state=13)
    return samples["text"].values

def apply_one_lf(labeling_function, data):
    try:
        label_matrix = data.apply_lfs([labeling_function])
    except AttributeError:
        applier = PandasLFApplier(lfs=[labeling_function])
        label_matrix = applier.apply(df = data)
    return label_matrix

def detect_duplicate_labeling_signature(modeler, datasets: list):
    label_matrix = np.vstack([modeler.apply(dset) for dset in datasets])
    seen_signatures = {} 
    dupes = {}
    lfs = modeler.get_lfs()
    signatures = [hash(label_matrix[:,i].tostring()) for i in range(len(lfs))]
    for i, s in enumerate(signatures):
        lf = lfs[i]
        if s in seen_signatures:
            dupes[lf.name] = seen_signatures[s]
        else:
            seen_signatures[s] = lf.name
    return dupes

def get_label_model_stats():
    pass

def get_stats_from_modeler(modeler, dataset, metrics_to_use=["f1", "precision", "recall"], average='weighted'):
    L = modeler.apply(dataset)
    y = modeler.predict(dataset)

    df_train_filtered, probs_train_filtered = filter_unlabeled_dataframe(
            X=dataset.df, y=y, L=L
        )
    coverage = len(probs_train_filtered)/len(dataset)
    preds = probs_to_preds(modeler.predict(dataset))
    ground_truth = dataset["label"].values

    res = {
        #"accuracy": metrics.accuracy_score(ground_truth, preds),
        "f1": metrics.f1_score(ground_truth, preds, average=average),
        "precision": metrics.precision_score(ground_truth, preds, average=average),
        "recall": metrics.recall_score(ground_truth, preds, average=average),
        "coverage": coverage
    }
    return res

def get_stats_from_probs(probs, ground_truth):
    preds = probs_to_preds(probs)
    return {
        "f1": metrics.f1_score(ground_truth, preds),
        "precision": metrics.precision_score(ground_truth, preds),
        "recall": metrics.recall_score(ground_truth, preds),
    }

