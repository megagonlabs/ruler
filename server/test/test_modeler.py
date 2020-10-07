import numpy as np
import pandas as pd
import unittest

from snorkel.labeling import LabelingFunction
from types import SimpleNamespace
from verifier.modeler import Modeler


class modelerTest(unittest.TestCase):
    def setUp(self):
        def createDfSplit(p):
            df_size = 20
            num_pos = int(df_size*p)
            df = pd.DataFrame({
                "label": np.append(np.zeros(num_pos), np.ones(df_size- num_pos)),
                })
            df["label"] = df["label"].astype('int32')
            df["text"] = df["label"].map({1:"positive", 0: "negative"})
            return df

        df_train, df_dev, df_valid, df_test = [createDfSplit(p) for p in [0.5, 0.5, 0.5, 0.5]]
        self.m = Modeler(df_train, df_dev, df_valid, df_test)
        lfs = {
            "1":    LabelingFunction(name="1",  f=lambda x: 1), 
            "0":    LabelingFunction(name="0",  f=lambda x: 0),
            "pos":  LabelingFunction(name="pos",f=lambda x: 1 if x.text=="positive" else -1), 
            "neg":  LabelingFunction(name="neg",f=lambda x: 1 if x.text=="negative" else 0)
        }
        self.lfs = lfs
        self.m.add_lfs(lfs)
        self.m.apply_lfs()
        self.m.fit_label_model()

    def test_analyze_lfs(self):
        analysis = self.m.analyze_lfs()
        self.assertTrue((analysis["Coverage Dev."].values==[1, 1, 0.5, 1]).all())
        self.assertTrue((analysis["Emp. Acc."]==[0.5, 0.5, 1, 0]).all())

    def test_lf_mistakes(self):
        analysis = self.m.analyze_lfs()
        for lfid, lf in self.lfs.items():
            mistakes = self.m.lf_mistakes(lfid)
            if analysis.loc[lfid]["Emp. Acc."]== 1.0:
                self.assertEqual(len(mistakes), 0)
            for ex in mistakes:
                x = SimpleNamespace(text=ex["text"])
                self.assertTrue(lf(x)!=-1)


    def test_lf_examples(self):
        for lfid, lf in self.lfs.items():
            examples = self.m.lf_examples(lfid)
            for ex in examples:
                x = SimpleNamespace(text=ex["text"])
                self.assertTrue(lf(x)!=-1)

    def test_get_label_model_stats(self):
        stats = self.m.get_label_model_stats()

    def test_pred_prob(self):
        probs = self.m.label_model.predict_proba(L=self.m.L_train)
        for i in range(5):
            probs2 = self.m.label_model.predict_proba(L=self.m.L_train)
            self.assertTrue((probs==probs2).all())

    def test_train(self):
        # make sure stats stay the same
        stats1 = self.m.train()
        stats1 = self.m.train()
        print(stats1)
        for i in range(5):
            stats2 = self.m.train()
            print(stats2)
            self.assertEqual(stats1, stats2)
            #self.assertTrue((stats1==stats2).all())

    def test_next_text(self):
        text = self.m.next_text()

    def test_filter_identical_signature(self):
        lfs = {"dupe": LabelingFunction(name="dupe", f=lambda x: 1)}
        self.m.add_lfs(lfs)
        self.m.apply_lfs()
        self.m.fit_label_model()
        a = self.m.analyze_lfs()
        self.assertEqual(a.loc["dupe"]["Duplicate"], "1")

