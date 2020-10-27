import numpy as np
import pandas as pd
import unittest
import warnings

from api.dataset import Dataset
from synthesizer.gll import *
from types import SimpleNamespace
from verifier.labeling_function import LabelingFunction, make_lf
from verifier.modeler import Modeler

class modelerTest(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=Warning) 

        self.m = Modeler(cardinality=2)

        self.concepts = {}
        lfs = [
            make_lf({
                "name": "test_lf_1", 
                DIRECTION: 0, 
                CONDS: [{
                    "string": "no problems",
                    "type": KeyType[TOKEN],
                    "TYPE_": "TOKEN",
                    "case_sensitive": False
                }], 
                LABEL: 1, 
                CONNECTIVE: 0
            }, concepts=self.concepts),
            make_lf({   
                "name": "test_lf_2", 
                DIRECTION: 0, 
                CONDS: [{
                    "TYPE_": "TOKEN", 
                    "case_sensitive": False, 
                    "string": "positive", 
                    "type": KeyType[TOKEN]
                }, {
                    "TYPE_": "TOKEN", 
                    "case_sensitive": True, 
                    "string": "its", 
                    "type": KeyType[TOKEN]
                }], 
                LABEL: 1, 
                CONNECTIVE: 0
            }, concepts=self.concepts)
        ]
        self.lfs = lfs
        self.m.add_lfs(lfs)

        self.assertEqual(set([lf.name for lf in self.m.get_lfs()]), set([lf.name for lf in self.lfs]))

        # some data to test on
        def createDfSplit(p):
            df_size = 20
            num_pos = int(df_size*p)
            df = pd.DataFrame({
                "label": np.append(np.zeros(num_pos), np.ones(df_size- num_pos)),
                })
            df["label"] = df["label"].astype('int32')
            df["text"] = df["label"].map({1:"positive", 0: "negative"})
            return df
        self.df_train, self.df_dev, self.df_valid, self.df_test = [createDfSplit(p) for p in [0.5, 0.5, 0.5, 0.5]]
        self.dataset_train = Dataset(self.df_train)
        self.dataset_dev = Dataset(self.df_dev)


    def test_apply(self):
        label_matrix_1 = self.m.apply(self.dataset_train)
        label_matrix_2 = self.m.apply(self.df_train)

        self.assertTrue((label_matrix_1==label_matrix_2).all())
        self.assertEqual(label_matrix_1.shape, (len(self.df_train), len(self.lfs)))

    def test_add_remove(self):
        m = Modeler(cardinality=2)
        m.add_lfs(self.lfs)
        # One of these LFs is already in the model. Only the second one should be added.
        num_lfs = len(self.m.get_lfs())
        lfs_to_add = [
            make_lf({"name": 1, DIRECTION: 0, CONDS: [{
                "string": "no problems",
                "type": 0,
                "TYPE_": "TOKEN",
                "case_sensitive": False
              }], LABEL: 1, CONNECTIVE: 0}, concepts=self.concepts),            
            make_lf({"name": 1, DIRECTION: 0, CONDS: [{
                "string": "the",
                "type": 0,
                "TYPE_": "TOKEN",
                "case_sensitive": False
              }], LABEL: 1, CONNECTIVE: 0}, concepts=self.concepts),
        ]

        m.add_lfs(lfs_to_add)
        self.assertEqual(num_lfs + 1, len(m.get_lfs()))

        label_matrix_added = m.apply(self.dataset_train)
        self.assertEqual(label_matrix_added.shape, (len(self.dataset_train), num_lfs + 1))

        # test remove
        m.remove_lfs([lf.name for lf in lfs_to_add])
        self.assertEqual(num_lfs-1, len(self.m.get_lfs()))

        label_matrix_removed = m.apply(self.dataset_train)
        self.assertEqual(label_matrix_removed.shape, (len(self.dataset_train), num_lfs-1))

    def test_custom_funcs(self):
        test_dir_name = "test_1"
        m = Modeler(cardinality=2)
        m.add_lfs(self.lfs)
        m.fit(self.dataset_train)
        m.save('models/' + test_dir_name)
        # write custom function to file
        with open("models/{}/custom_functions.py".format(test_dir_name), "w") as file:
            file.write(
                "def my_func(x):\n    if len(x.text)> 10:\n        return True\n    return False\nmy_lfs=[my_func]"
            )
        # load and apply
        m = Modeler.load("models/" + test_dir_name)
        m.fit(self.dataset_train)
        L = m.apply(self.df_train)
        self.assertEqual(L.shape, (len(self.df_train), len(self.lfs) + 1))

    def test_fit(self):
        self.m.fit(self.df_train)
        self.m.fit(self.dataset_train)

    def test_predict(self):
        self.m.fit(self.dataset_train)
        probs_train = self.m.predict(self.dataset_train)
        probs_test = self.m.predict(self.df_test)


    def test_fit_predict(self):
        probs_train = self.m.fit_predict(self.dataset_train)
        probs_test = self.m.fit_predict(self.df_test)

    def test_save_and_load(self):
        test_dir_name = "test_0"
        m = Modeler(cardinality=2)
        m.add_lfs(self.lfs)
        m.fit(self.dataset_train)
        m.save('models/' + test_dir_name)

        m2 = Modeler.load('models/' + test_dir_name)

        L1 = m.apply(self.df_train)
        L2 = m2.apply(self.df_train)

        self.assertTrue((L1==L2).all(), "{}\n{}".format(L1, L2))

    def test_analyze_lfs(self):
        # test on pandas DataFrame
        analysis_train = self.m.analyze_lfs(self.df_train)

        # and on Dataset
        analysis_train2 = self.m.analyze_lfs(self.dataset_train)
        self.assertTrue((analysis_train==analysis_train2).all().all())

        analysis_dev = self.m.analyze_lfs(self.dataset_dev)

        for lf in self.m.get_lfs():
            lf_name = lf.name
            stat = analysis_dev.loc[lf_name]
            self.assertTrue('Polarity' in stat)
            self.assertTrue(stat['Coverage'] <= 1)
            self.assertTrue(stat['Conflicts'] >= 0)
            self.assertTrue(stat['Overlaps'] >= 0)

    def test_update_concept(self):
        concepts = {"neg_words": {}}
        new_lf = make_lf({
                "name": "test_lf_1", 
                DIRECTION: 0, 
                CONDS: [{
                    "string": "neg_words",
                    "type": KeyType[CONCEPT],
                    "TYPE_": CONCEPT,
                    "case_sensitive": False
                }], 
                LABEL: 0, 
                CONNECTIVE: 0
            }, concepts=concepts)

        # apply LF with empty concepts
        m = Modeler(cardinality=2)
        m.add_lfs([new_lf])
        L = m.apply(self.dataset_train)

        # update the concept
        concepts["neg_words"] = [{"string": "p", "token_text": "negative", "type": KeyType[REGEXP], "case_sensitive": False}]
        concepts["HATS"] = []

        m.update_concept("neg_words")

        # re apply LFs
        L_new = m.apply(self.dataset_train)

        self.assertTrue((L != L_new).any())
        self.assertEqual(L.shape, L_new.shape)


    def test_multi_class_model(self):
        # TODO make sure modeler works on 3+ class classification tasks
        pass
