import json
import os
import pickle
import sys

from snorkel.labeling import PandasLFApplier
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel
from snorkel.labeling import filter_unlabeled_dataframe
from sklearn.feature_extraction.text import CountVectorizer
from snorkel.analysis import metric_score
from snorkel.utils import preds_to_probs

from verifier.util import *


class Modeler:
    def __init__(self, df_train, df_dev, df_valid, df_test, lfs={}, label_model=None):
        df_train["seen"] = False
        self.df_train = df_train
        self.df_dev = df_dev
        self.df_valid = df_valid
        #self.df_test = df_test
        #self.Y_train = df_train.label.values
        self.Y_dev = df_dev.label.values
        self.Y_valid = df_valid.label.values

        self.lfs = lfs

        self.L_train = None
        self.L_dev = None
        self.L_valid = None
        cardinality = len(df_valid.label.unique())

        if label_model is None:
            self.label_model = LabelModel(cardinality=cardinality, verbose=True)
        else: 
            self.label_model = label_model

    def get_lfs(self):
        return list(self.lfs.values())

    def add_lfs(self, new_lfs: dict):
        self.lfs.update(new_lfs)

    def remove_lfs(self, old_lf_ids: list):
        for lf_id in old_lf_ids:
            del self.lfs[lf_id]
        return len(self.lfs)

    def apply_lfs(self):
        applier = PandasLFApplier(lfs=self.get_lfs())
        self.L_train = applier.apply(df=self.df_train)
        self.L_dev = applier.apply(df=self.df_dev)
        #self.L_valid = applier.apply(df=self.df_valid)

    def lf_examples(self, lf_id, n=5):
        lf = self.lfs[lf_id]
        applier = PandasLFApplier(lfs=[lf])
        L_train = applier.apply(df=self.df_train)
        labeled_examples = self.df_train[L_train!=-1]
        samples = labeled_examples.sample(min(n, len(labeled_examples)), random_state=13)
        return [{"text": t} for t in samples["text"].values]

    def fit_label_model(self):
        assert self.L_train is not None

        self.label_model.fit(L_train=self.L_train, n_epochs=1000, lr=0.001, log_freq=100, seed=123)

    def analyze_lfs(self):
        if len(self.lfs) > 0:
            df = LFAnalysis(L=self.L_train, lfs=self.get_lfs()).lf_summary()
            dev_df = LFAnalysis(L=self.L_dev, lfs=self.get_lfs()).lf_summary(Y=self.Y_dev)
            df["Weight"] = self.label_model.get_weights()
            df['dev_set_accuracy'] =  dev_df["Emp. Acc."]
            df["dev_set_coverage"] = dev_df["Coverage"]
            return df
        return None

    def get_label_model_stats(self):
        result = self.label_model.score(L=self.L_dev, Y=self.Y_dev, metrics=["f1", "precision", "recall"])

        probs_train = self.label_model.predict_proba(L=self.L_train)
        df_train_filtered, probs_train_filtered = filter_unlabeled_dataframe(
            X=self.df_train, y=probs_train, L=self.L_train
        )
        result["training_label_coverage"] = len(probs_train_filtered)/len(probs_train)
        result["training_label_size"] = len(probs_train_filtered)

        return result

    def train(self):
        probs_train = self.label_model.predict_proba(L=self.L_train)

        df_train_filtered, probs_train_filtered = filter_unlabeled_dataframe(
            X=self.df_train, y=probs_train, L=self.L_train
        )
        if len(df_train_filtered) == 0:
            print("Labeling functions cover none of the training examples!", file=sys.stderr)
            return [0, 0, 0, 0]

        vectorizer = CountVectorizer(ngram_range=(1, 2))
        X_train = vectorizer.fit_transform(df_train_filtered.text.tolist())

        X_dev = vectorizer.transform(self.df_dev.text.tolist())
        X_valid = vectorizer.transform(self.df_valid.text.tolist())
        #X_test = vectorizer.transform(self.df_test.text.tolist())

        keras_model = get_keras_logreg(input_dim=X_train.shape[1])

        keras_model.fit(
            x=X_train,
            y=probs_train_filtered,
            validation_data=(X_valid, preds_to_probs(self.Y_valid, 2)),
            callbacks=[get_keras_early_stopping()],
            epochs=20,
            verbose=0,
        )

        preds_dev = keras_model.predict(x=X_dev).argmax(axis=1)
        dev_precision = metric_score(golds=self.Y_dev, preds=preds_dev, metric="precision")
        dev_recall = metric_score(golds=self.Y_dev, preds=preds_dev, metric="recall")
        dev_f1 = metric_score(golds=self.Y_dev, preds=preds_dev, metric="f1")
        dev_label_coverage = len(probs_train_filtered)/len(probs_train)

        return {
            "precision": dev_precision, 
            "recall": dev_recall, 
            "f1": dev_f1,
            "%_data_labeled": dev_label_coverage
        }

    def next_text(self):
        # TODO
        subset_size = 3

        if len(self.lfs) > 1:
            sums = [x.sum() for x in self.L_train]
            min_sum = min(sums)
            print("Minimum label sum is {}".format(min_sum))
            subset = self.df_train[(sums == min_sum) & (~self.df_train["seen"])]
        else:
            subset = self.df_train[~self.df_train['seen']]
        try:
            res_idx = subset.index[0]
        except IndexError as e:
            print("Could not retrieve the next text. Size of training set: ")
            print(len(self.df_train))
            raise(e)
        self.df_train.at[res_idx, "seen"] = True
        return subset["text"].values[0]

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
