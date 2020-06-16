import json
import numpy as np
import os
import pickle
import sys

from math import log
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel
from snorkel.labeling import PandasLFApplier
from snorkel.labeling import filter_unlabeled_dataframe
from snorkel.utils import preds_to_probs

from synthesizer.gll import *
from verifier.util import *


class Modeler:
    def __init__(self, df_train, df_dev, df_valid, df_test, df_heldout, lfs={}, label_model=None):
        
        df_train["seen"] = 0
        self.df_train = df_train.reset_index()
        self.df_dev = df_dev
        self.df_valid = df_valid
        self.df_test = df_test
        self.df_heldout = df_heldout

        self.Y_dev = df_dev.label.values
        self.Y_valid = df_valid.label.values
        self.Y_test = df_test.label.values
        self.Y_heldout = df_heldout.label.values

        self.lfs = lfs
        self.count = len(lfs)

        self.L_train = None
        self.L_dev = None
        self.L_heldout = None

        if label_model is None:
            cardinality = len(df_valid.label.unique())
            self.label_model = LabelModel(cardinality=cardinality, verbose=True)
        else: 
            self.label_model = label_model

        self.vectorizer = CountVectorizer(ngram_range=(1, 2))
        self.vectorizer.fit(df_train.text.tolist())

    def get_lfs(self):
        return list(self.lfs.values())

    def add_lfs(self, new_lfs: dict):
        self.lfs.update(new_lfs)
        if len(self.lfs)> 0:
            self.apply_lfs()
        self.count = len(self.lfs)

    def remove_lfs(self, old_lf_ids: list):
        for lf_id in old_lf_ids:
            del self.lfs[lf_id]
        if len(self.lfs)> 0:
            self.apply_lfs()
        self.count = len(self.lfs)
        return len(self.lfs)

    def apply_lfs(self):
        print("applying")

        lfs = self.get_lfs()

        applier = PandasLFApplier(lfs=lfs)
        self.L_train = applier.apply(df=self.df_train)
        self.L_dev = applier.apply(df=self.df_dev)
        self.L_heldout = applier.apply(df=self.df_heldout)

    def find_duplicate_signature(self):
        label_matrix = np.vstack([self.L_train, self.L_dev])
        seen_signatures = {} 
        dupes = {}
        lfs = self.get_lfs()
        signatures = [hash(label_matrix[:,i].tostring()) for i in range(len(lfs))]
        for i, s in enumerate(signatures):
            lf = lfs[i]
            if s in seen_signatures:
                dupes[lf.name] = seen_signatures[s]
            else:
                seen_signatures[s] = lf.name
        return dupes


    def lf_examples(self, lf_id, n=5):
        lf = self.lfs[lf_id]
        applier = PandasLFApplier(lfs=[lf])
        L_train = applier.apply(df=self.df_train)
        labeled_examples = self.df_train[L_train!=-1]
        samples = labeled_examples.sample(min(n, len(labeled_examples)), random_state=13)
        return [{"text": t} for t in samples["text"].values]

    def lf_mistakes(self, lf_id, n=5):
        lf = self.lfs[lf_id]
        applier = PandasLFApplier(lfs=[lf])
        L_dev = applier.apply(df=self.df_dev).squeeze()
        labeled_examples = self.df_dev[(L_dev!=-1) & (L_dev != self.df_dev["label"])]
        samples = labeled_examples.sample(min(n, len(labeled_examples)), random_state=13)
        return [{"text": t} for t in samples["text"].values]

    def fit_label_model(self):
        assert self.L_train is not None

        self.label_model.fit(L_train=self.L_train, n_epochs=1000, lr=0.001, log_freq=100, seed=123)


    def analyze_lfs(self):
        if len(self.lfs) > 0:
            try:
                df = LFAnalysis(L=self.L_train, lfs=self.get_lfs()).lf_summary()
            except ValueError:
                self.apply_lfs()
                df = LFAnalysis(L=self.L_train, lfs=self.get_lfs()).lf_summary()
            dev_df = LFAnalysis(L=self.L_dev, lfs=self.get_lfs()).lf_summary(Y=self.Y_dev)
            df = df.merge(dev_df, how="outer", suffixes=(" Training", " Dev."), left_index=True, right_index=True)
            df["Weight"] = self.label_model.get_weights()
            df["Duplicate"] = None
            for dupe, OG in self.find_duplicate_signature().items():
                print("Duplicate labeling signature detected")
                print(dupe, OG)
                df.at[dupe, "Duplicate"] = OG

            return df
        return None

    def get_label_model_stats(self):
        result = self.label_model.score(L=self.L_dev, Y=self.Y_dev, metrics=["f1", "precision", "recall"])

        probs_train = self.label_model.predict_proba(L=self.L_train)
        df_train_filtered, probs_train_filtered = filter_unlabeled_dataframe(
            X=self.df_train, y=probs_train, L=self.L_train
        )
        result["training_label_coverage"] = len(probs_train_filtered)/len(probs_train)
        exp = self.df_dev["label"].value_counts()[1] / len(self.df_dev)
        result["expected_class_0_ratio"] = exp
        result["class_0_ratio"] = (probs_train_filtered[:,0]>0.5).sum()/len(probs_train_filtered)
        print((probs_train_filtered[:,0]>0.5).sum())
        if len(probs_train_filtered) == 0:
            result["class_0_ratio"] = 0

        return result

    def get_heldout_stats(self):
        if self.L_heldout is not None:
            return self.label_model.score(L=self.L_heldout, Y=self.Y_heldout, metrics=["f1", "precision", "recall"])
        return {}

    def train(self):
        probs_train = self.label_model.predict_proba(L=self.L_train)

        df_train_filtered, probs_train_filtered = filter_unlabeled_dataframe(
            X=self.df_train, y=probs_train, L=self.L_train
        )

        if len(df_train_filtered) == 0:
            print("Labeling functions cover none of the training examples!", file=sys.stderr)
            return {"micro_f1": 0}

        #from tensorflow.keras.utils import to_categorical
        #df_train_filtered, probs_train_filtered = self.df_dev, to_categorical(self.df_dev["label"].values)
        

        vectorizer = self.vectorizer
        X_train = vectorizer.transform(df_train_filtered.text.tolist())

        X_dev = vectorizer.transform(self.df_dev.text.tolist())
        X_valid = vectorizer.transform(self.df_valid.text.tolist())
        X_test = vectorizer.transform(self.df_test.text.tolist())

        self.keras_model = get_keras_logreg(input_dim=X_train.shape[1])

        self.keras_model.fit(
            x=X_train,
            y=probs_train_filtered,
            validation_data=(X_valid, preds_to_probs(self.Y_valid, 2)),
            callbacks=[get_keras_early_stopping()],
            epochs=20,
            verbose=0,
        )

        preds_test = self.keras_model.predict(x=X_test).argmax(axis=1)

        #return preds_test
        return self.get_stats(self.Y_test, preds_test)

    def get_heldout_lr_stats(self):
        X_heldout = self.vectorizer.transform(self.df_heldout.text.tolist())

        preds_test = self.keras_model.predict(x=X_heldout).argmax(axis=1)
        return self.get_stats(self.Y_heldout, preds_test)

    def get_stats(self, Y_test, preds_test):

        label_classes = np.unique(self.Y_test)
        accuracy = metrics.accuracy_score(Y_test, preds_test)
        precision_0, precision_1 = metrics.precision_score(Y_test, preds_test, labels=label_classes, average=None)
        recall_0, recall_1 = metrics.recall_score(Y_test, preds_test, labels=label_classes, average=None)
        test_f1 = metrics.f1_score(Y_test, preds_test, labels=label_classes)

        #recall_0, recall_1 = metrics.precision_recall_fscore_support(self.Y_test, preds_test, labels=label_classes)["recall"]
        return {
            "micro_f1": test_f1,
            "recall_0": recall_0,
            "precision_0": precision_0,
            "accuracy": accuracy,
            "recall_1": recall_1,
            "precision_1": precision_1
        }

    def entropy(self, prob_dist):
        #return(-(L_row_i==-1).sum())
        return(-sum([x*log(x) for x in prob_dist]))

    def next_text(self):
        subset_size = 50

        min_times_seen = self.df_train["seen"].min()
        least_seen_examples = self.df_train[self.df_train["seen"]==min_times_seen]

        if ((len(self.lfs) == 0) or (len(least_seen_examples)==1) or (self.L_train is None)):
            #return one of the least seen examples, chosen randomly
            res_idx = least_seen_examples.sample(1).index[0]
        else: 
            #take a sample of size subset_size, compute entropy, and return the example with highest entropy
            subset = least_seen_examples.sample(min(subset_size, len(least_seen_examples)))
            L_train = self.L_train[self.df_train.index.isin(subset.index)]
            probs = self.label_model.predict_proba(L=L_train)
            entropy = [self.entropy(x) for x in probs] # get entropy for each text example
            subset = subset[entropy==max(entropy)]
            res_idx = subset.sample(1).index[0]
        self.df_train.at[res_idx, "seen"] += 1
        return {"text": self.df_train.at[res_idx, "text"], "id": int(res_idx)}

    def text_at(self, index):
        self.df_train.at[index, "seen"] += 1
        return {"text": self.df_train.at[index, "text"], "id": int(index)}

    def save(self, dir_name):
        self.label_model.save(os.path.join(dir_name, 'label_model.pkl'))
        with open(os.path.join(dir_name, 'model_lfs.pkl'), "wb+") as file:
            pickle.dump(self.lfs, file)

    def load(self, dir_name):
        with open(os.path.join(dir_name, 'model_lfs.pkl'), "rb") as file:
            lfs = pickle.load(file)
            label_model = LabelModel.load(os.path.join(dir_name, 'label_model.pkl'))
            self.lfs = lfs
            self.label_model = label_model
