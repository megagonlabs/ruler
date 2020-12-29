import pandas as pd
import unittest

from api.dataset import Dataset
from api.project import Project
from verifier.modeler import Modeler



class projectTest(unittest.TestCase):
    def setUp(self):
        self.project = Project()

    def test_name(self):
        self.project.set_name("test_project")
        self.assertEqual(self.project.name, "test_project")

    def test_labels(self):
        empty_labels = self.project.get_labels()
        self.assertEqual(empty_labels, {})

        labels = {"NOT_SPAM": 0, "SPAM": 1}
        self.project.add_labels(labels)
        fetched_labels = self.project.get_labels()
        self.assertEqual(fetched_labels, labels)

    def test_set_datasets(self):

        df = pd.read_csv('datasets/spam_example/processed.csv', header=0)
        dataset = Dataset(df)

        test_datasets_dict = {
            "train": dataset,
            "dev": dataset,
            "test": dataset,
            "valid": dataset
        }
        self.project.set_datasets(test_datasets_dict)

    def test_prep_datasets(self):
        self.project.prep_datasets('spam_example', test_split=False)

    def test_save(self):

        test_dir_name = "test_0"
        self.project.prep_datasets('spam_example', test_split=False)
        self.project.load_model("models/" + test_dir_name)

        self.project.save_datasets("datasets/spam_example/labelled.csv")



    def test_readiness(self):
        # TODO: assert labels and cardinality match
        # make sure that if self.project.ready() is true, all the endpoints work
        pass