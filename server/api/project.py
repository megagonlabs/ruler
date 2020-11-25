import numpy as np
import os
import pandas as pd
import sys
import time
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from api.dataset import allowed_file
from api.dataset import DATASETS_PATH
from api.dataset import DataPreparer
from api.dataset import Dataset
from api.version_file import VersionFile
from synthesizer.gll import ConceptWrapper
from synthesizer.gll import DELIMITER
from synthesizer.gll import Label
from tqdm import tqdm
from verifier.modeler import Modeler
from werkzeug.utils import secure_filename

tqdm.pandas(desc="model launch progress")

DATASETS_PATH = 'datasets/'

class Project:
    def __init__(self, 
            concepts={}, 
            name=None, 
            datasets=None, 
            labels=None,
            cardinality=2,
            modeler=None
        ):
        self.concepts = ConceptWrapper()
        for concept, elements in concepts.items():
            self.concepts.add_element(concept, elements)

        self.name = name
        if labels is not None:
            self.labels = labels
        else:
            self.labels = Label(name=self.name)

        if datasets is not None:
            self.set_datasets(datasets)
        else:
            self.train = None

        self.data_preparer = None

        if modeler is not None:
            self.modeler = modeler
            self.cardinality = modeler.cardinality
        else:
            self.modeler = Modeler(cardinality=cardinality)
            self.cardinality = cardinality

    ## STATUS CHECK ##
    def ready(self):
        """Make sure project is ready to launch/use"""
        for item in ['concepts', 'train', 'labels']:
            if self.__dict__[item] is None:
                print("{} is missing from project (project.py)".format(item))
                return False
        return True

    def progress(self):
        if self.data_preparer is not None:
            return self.data_preparer.progress()
        else:
            if self.ready():
                return 1
            else:
                return 0

    ## DATASETS ##
    def prep_datasets(self, dataset_path, test_split=True):
        """Preprocess the data 
        (if necessary. If it's been processed, it will load the prepared version.)

        Args:
            dataset_path (string): path to folder or file containing the data to use
        """
        path = os.path.join(DATASETS_PATH, dataset_path)
        assert os.path.exists(path), 'Path \'{}\' not found'.format(path)
        if self.name is None:
            self.name = str(dataset_path)
        self.data_preparer = DataPreparer()
        datasets_dict = self.data_preparer.prepare(dataset_path, test_split=test_split)
        self.set_datasets(datasets_dict)
        self.data_preparer = None

    def set_datasets(self, datasets_dict: dict):
        """Set data splits
        
        Args:
            datasets_dict (dict): {"data_split_name": Dataset}
        """
        self.train = datasets_dict['train']
        self.dev = datasets_dict['dev']
        try:
            self.test = datasets_dict['test']
            self.valid = datasets_dict['valid']
        except KeyError:
            #print("WARNING (project.py) no test or validation set was provided.")
            pass

    ## NAME ##
    def set_name(self, name):
        """(Optional) name this project
        If no name is provided, the name of the dataset
        will be used.
        
        Args:
            name (string)
        """
        self.name = name
        self.labels.change_name(name)

    ## LABELS ##
    def add_labels(self, labels: dict):
        """Define the names of the labels for the project
        
        Args:
            labels (dict): {"LABEL_NAME": label_key (int)}
        """
        self.status = "Creating labels"
        for lname, value in labels.items():
            self.labels.add_label(lname, value)

    def get_labels(self):
        return self.labels.to_dict()

    def save(self, path):
        self.modeler.save(path)
        self.labels.save(os.path.join(path, "labels.json"))
        self.concepts.save(os.path.join(path, "concept_collection.json"))
        self.save_datasets()

    def save_datasets(self):
        for dset_name in ["train", "dev", "test", "valid"]:
            if self.__hasattr__(dset_name):
                dset = self.__get__(dset_name)
                logging.info("[DATA] {} dataset save success")
                probabilistic_labels = self.modeler.predict(dset)

                path = os.path.join(DATASETS_PATH, self.name)
                # add datetime to file name (version control)
                path = VersionFile(path)
                dset.save(path=path, y=probabilistic_labels)

            else:
                logging.info("[DATA] {} dataset save failed (dataset not found)".format(dset_name))


    def load_model(self, path):
        self.modeler = Modeler.load(path)
        self.concepts = ConceptWrapper.load(os.path.join(path, "concept_collection.json"))
        self.labels = Label.load(os.path.join(path, "labels.json"))

    ## LOAD EXISTING/PRE-DEFINED TASK ##
    @staticmethod
    def initialize_from_task(MODE="Amazon"):
        """Load data for the provided mode, preprocess, and initialize model
        
        Args:
            MODE (str, optional): The task for which to load data
        
        Returns:
            Project
        
        Raises:
            Error: If the mode is not recognized
        """
        labels = []
        task_name = ""
        dataset_path = ""

        if MODE == "Amazon":
            labels = ["negative", "positive"],
            task_name ="Amazon Reviews Classification: Sentiment"
            dataset_path = "Amazon Reviews"
            
        elif MODE =="Youtube":
            labels = ["NON-SPAM", "SPAM"]
            task_name = "Youtube Comments Classification: Spam or Not Spam"
            dataset_path = "Youtube Comments"
            
        elif MODE == "Film":
            labels = ["COMEDY", "DRAMA"]
            task_name = "Wikipedia plot summary classification: comedy or drama."
            
        elif MODE == "News":
            labels = ["ELECTRONICS", "GUNS"]
            task_name = "Newsnet classification: guns or electronics."
        else:
            raise Error('MODE={} is not recognized. MODE must be one of \
                Amazon, Youtube, Film, or News'.format(MODE))

        project = Project(name=task_name, labels=labels)
        project.prep_dataset(dataset_path)
        return project


def add_file(file, dataset_uuid: str, label_col="label", text_col="text"):
    # save file
    if file and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        file_path = os.path.join(DATASETS_PATH, dataset_uuid, file_name)
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        file.save(file_path)


if __name__=='__main__':
    p = Project.initialize_from_task("Amazon")
    modeler = p.modeler
