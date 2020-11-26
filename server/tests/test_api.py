import json
import pandas as pd
import time
import unittest

from api.dataset import Dataset
from api.endpoints import *
from verifier.labeling_function import LabelingFunction

class apiTest(unittest.TestCase):
    def setUp(self):
        self.project = project
        self.labels = {"POS": 1, "NEG": 0}

        post_labels(self.labels)

        sample = [
            [0,"Terrible",0],
            [1,"Fantastic",1], 
            [2,"Terrible",0],
            [3,"Terrible",0]]
        df_train = pd.DataFrame(sample, columns=["idx", "text", "label"])

        sample = [
            [0,"People ask me ""Who was that singing? It was amazing!""",1],
            [1,"Best purchase ever",1], 
            [2,"After a while, the batteries would not hold a charge. ",0],
            [3,"So many bugs!",0],
            [4,"Terrible",0],
            [5,"Fantastic",1], 
            [6,"Terrible",0],
            [7,"Terrible",0]]
        df_dev = pd.DataFrame(sample, columns=["idx", "text", "label"])

        
        self.project.set_datasets({
            "train": Dataset(df_train),
            "dev": Dataset(df_dev),
            "valid": Dataset(df_dev),
            "test": Dataset(df_dev),
            })
        self.project.dataset_path = "datasets/sentiment_example"

        while not project.ready():
            time.sleep(1)

        def _test_lf(x):
            if "e" in x.text:
                return 1
            else:
                return 0
        self.test_lf = LabelingFunction(name="e",f=_test_lf)

    def test_get_labels(self):
        labels = get_labels()
        self.assertEqual(self.labels, labels)
        # Make sure object is json serializable
        json.dumps(labels)

    def test_get_connective(self):
        conn = get_connective()
        self.assertEqual(conn, {'OR': 0, 'AND': 1})
        # Make sure object is json serializable
        json.dumps(conn)

    def test_get_keytype(self):
        keyt = get_keytype()
        self.assertEqual(keyt, {'TOKEN': 0, 'CONCEPT': 1, 'NER': 2, 'REGEXP': 3})
        # Make sure object is json serializable
        json.dumps(keyt)

    def test_concepts(self):
        c = get_all_concepts()
        self.assertEqual(c, {})

        create_concept({"name": "negation", "tokens": []})
        c = get_all_concepts()
        self.assertEqual(c, {"negation": []})

        update_concept("negation", [{'string': 'not'}])
        c = get_all_concepts()
        self.assertEqual(c, {"negation": [{'key': 'not#None#None', 'string': 'not'}]})
        # Make sure object is json serializable
        json.dumps(c)

        delete_concept("negation")
        c = get_all_concepts()
        self.assertEqual(c, {})

    def test_next_text(self):
        res0 = next_text()
        res1 = next_text()
        self.assertTrue(res0 != res1)
        # Make sure object is json serializable
        json.dumps(res0)

    def test_next_text_with_modeler(self): 
        self.project.modeler.add_lfs([self.test_lf])
        res0 = next_text()
        # Make sure object is json serializable
        json.dumps(res0)


    def test_interaction(self):
        res0 = next_text()
        interaction = {
            "label": 1,
            "annotations":[
                {
                    "id":85,
                    "label":0,
                    "start_offset":85,
                    "end_offset":92,
                    "text":"a while",
                    "link": None,
                    "type":"annotation"
                }
            ],
            "text":"What more can I say about these? They're plain old medicine cups. I've had these for a while and have no problems.",
            "index":0
        }
        old_lf_stats = get_lf_stats()

        lf_dicts = submit_interaction(interaction)
        # Make sure object is json serializable
        json.dumps(lf_dicts)
        lf_stats = submit_instances(lf_dicts)
        json.dumps(lf_stats)
        self.assertEqual(len(lf_stats), len(lf_dicts) + len(old_lf_stats))

        lf_stats2 = get_lf_stats()
        self.assertEqual(lf_stats, lf_stats2)

        lr_stats = get_logreg_stats()
        for stat in ['f1', 'precision', 'recall']:
            self.assertTrue(stat in lr_stats)

    def test_get_interaction_idx(self):
        res0 = next_text()
        res1 = next_text()
        int0 = get_interaction_idx(0)
        self.assertEqual(int0, res0)
        int1 = get_interaction_idx(1)
        self.assertEqual(int1, res1)
        # Make sure object is json serializable
        json.dumps(int1)


    def test_get_lf_stats(self):
        self.project.modeler.add_lfs([self.test_lf])
        self.project.modeler.fit(self.project.train)
        lf_stats = get_lf_stats()
        self.assertTrue(self.test_lf.name in lf_stats)
        for lf_id in lf_stats.keys():
            stat = lf_stats[lf_id]
            self.assertEqual(len(stat['Polarity Train']), 2)
            self.assertTrue(stat['Coverage Train'] <= 1)
            self.assertTrue(stat['Conflicts Train'] >= 0)
            self.assertTrue(stat['Conflicts Dev.'] >= 0)
            self.assertTrue(stat['Emp. Acc.'] >= 0)
            self.assertTrue(stat['Incorrect'] >= 0)
            self.assertTrue(stat['Correct'] >= 0)
            self.assertTrue('Conditions' in stat)
            self.assertTrue('active' in stat)

            if stat['Emp. Acc.'] > 0:
                self.assertTrue(stat['Correct'] > 0)
            if stat['Emp. Acc.'] < 1.:
                self.assertTrue(stat['Incorrect'] > 0)
        # Make sure object is json serializable
        json.dumps(lf_stats)

    def test_get_lf_label_examples(self):
        self.project.modeler.add_lfs([self.test_lf])
        ex_and_mistakes = get_lf_label_examples(self.test_lf.name)
        for field in "examples", "mistakes":
            self.assertTrue(len(ex_and_mistakes[field]) > 0)
            for item in ex_and_mistakes[field]:
                self.assertTrue(isinstance(item["text"], str)) 
                self.assertTrue(len(item["annotations"])>=0)
        json.dumps(ex_and_mistakes)

    def test_get_resources(self):
        m = get_models()
        d = get_datasets()
        for l in [m, d]:
            for item in l:
                self.assertTrue(len(item) > 0)
        select_model(m[0])
        select_dataset(d[0])

    def test_create_model(self):
        create_new_model("test_model")
        m = get_models()
        self.assertTrue("test_model" in m)
        select_model("test_model")

    def test_zip_model(self):
        mod = zip_model()
        # Make sure object is json serializable
        json.dumps(mod)

    def test_save_model(self):
        self.project.modeler.add_lfs([self.test_lf])
        self.project.save("models/test_model")