import json
import numpy as np
import os
import pandas as pd
import pickle
import sys

from datetime import datetime
from importlib import import_module
from importlib import invalidate_caches
from importlib import reload
from math import log
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel
from snorkel.labeling import PandasLFApplier
from snorkel.labeling import filter_unlabeled_dataframe
from snorkel.utils import preds_to_probs
from synthesizer.gll import CONCEPT
from synthesizer.gll import CONDS
from synthesizer.gll import KeyType


from verifier.labeling_function import LabelingFunction

class Modeler:
    """Used to fit, predict, apply, 
    and stores metadata related to labeling functions.
    
    Attributes:
        cardinality (int): Number of label classes 
        label_model (Snorkel LabelModel): Model that combines labels from different functions. 
            you can pass your own LabelModel to iterate on or create a new one with Ruler.
        lf_db (LF_DB): A database of labeling functions.
    """
    
    def __init__(self, lf_db=None, label_model=None, cardinality: int=2):
            """
            Args:
                lf_db (LF_DB, optional): A database of labeling functions.
                label_model (Snorkel LabelModel, optional): Model that combines labels from different functions. 
                    you can pass your own LabelModel to iterate on or create a new one with Ruler.
                cardinality (int, optional): Number of label classes 
            """
            if lf_db is None:
                self.lf_db = LFDB({})
                assert len(self.get_lfs())==0, self.get_lfs()
            else:
                self.lf_db = lf_db

            self.cardinality = cardinality

            if label_model is None:
                self.label_model = LabelModel(cardinality=self.cardinality, verbose=True)
            else: 
                self.label_model = label_model
                assert self.cardinality == label_model.cardinality

    def __getitem__(self, lf_id):
        """
        Returns:
            LabelingFunction: see labeling_function.py for specs
        """
        return self.lf_db[lf_id]

    def get_lfs(self, include_inactive=False):
        """Get all labeling functions. If include_inactive=False, do not include deactivated LFs.
        
        Args:
            include_inactive (bool, optional): Whether to include deactivated LFs
        
        Returns:
            list(LabelingFunction)
        """
        return self.lf_db.get_lfs(include_inactive=include_inactive)

    def has_lfs(self):
        """Determine whether the model has any active labeling functions.
        
        Returns:
            bool: whether the model has any active labeling functions.
        """
        return len(self.get_lfs()) > 0

    def add_lfs(self, new_lfs: list):
        """Add new labeling functions
        
        Args:
            new_lfs (list(LabelingFunction)): See labeling_function.py for specs.
        """
        self.lf_db.add_lfs(new_lfs)

    def remove_lfs(self, old_lf_ids: list):
        """Deactivate the given labeling functions
        
        Args:
            old_lf_ids (list(str)): IDs of the labeling functions to deactivate
        """
        for lf_id in old_lf_ids:
            self.lf_db.deactivate(lf_id)

    def apply(self, dataset, lfs=None):
        """Apply the labeling functions to the given dataset.
        If the dataset is a Dataset (defined in api/dataset.py) it will cache 
        previous labels for faster application. If the dataset is a pandas DataFrame,
        performance will be slower.
        
        Args:
            dataset (Dataset or pandas.DataFrame): the data to apply LFs on. Must have 
                attribute "text"
            lfs (None, optional): if no labeling functions are passed, default to 
                all active labeling functions.
        
        Returns:
            matrix: size (number of examples in dataset)*(number of LFs)
        
        Raises:
            AttributeError: If apply is called when the modeler has no active labeling functions
                and none are passed.
        """
        if not self.has_lfs():
            raise AttributeError("modeler.apply was called with no labeling functions.")
        if lfs is None:
            lfs = self.get_lfs()
        if hasattr(dataset, "apply_lfs"):
            # if dataset is of the class Dataset, it has an optimized apply_lf function
            label_matrix = dataset.apply_lfs(lfs)
        else:
            # otherwise, a dataframe-like object was passed, and we need to use .apply
            # this is slower because it does not store previously computed labels
            applier = PandasLFApplier(lfs=lfs)
            label_matrix = applier.apply(df = dataset)
        return label_matrix

    def fit(self, dataset):
        """Fit the label model to the dataset. This is the model that combines outputs from all 
        active labeling functions into probabilistic labels.
        
        Args:
            dataset (Dataset or pandas.DataFrame): The dataset on which to fit the model, usually a large
            unlabelled dataset.
        """
        if self.has_lfs():
            label_matrix = self.apply(dataset)
            self.label_model.fit(L_train=label_matrix, n_epochs=1000, lr=0.001, log_freq=100, seed=123)

    def predict(self, dataset):
        """Predict probabilistic labels for the given dataset.
        
        Args:
            dataset (Dataset or pandas.DataFrame)
        
        Returns:
            matrix: size (number of examples in dataset)*(model cardinality)
        """
        label_matrix = self.apply(dataset)
        probs = self.label_model.predict_proba(L=label_matrix)
        return probs

    def fit_predict(self, dataset):
        """Fit model to the dataset and return predicted labels.
        
        Args:
            dataset (Dataset or pandas.DataFrame)
        
        Returns:
            matrix: size (number of examples in dataset)*(model cardinality)
        """
        self.fit(dataset)
        return self.predict(dataset)

    def save(self, path):
        """Save the modeler
        
        Args:
            path (str): path to a folder where the model will be saved.
        """

        try:
            os.mkdir(path)
        except FileExistsError as e:
            pass

        if not os.path.exists(os.path.join(path, "custom_functions.py")):
            with open(os.path.join(path, "custom_functions.py"), "w+") as file:
                file.write("# Place your custom functions in this array\nmy_lfs = []")

        # save lfs
        self.lf_db.save(os.path.join(path, 'LF_DB.json'))
        # save label_model
        self.label_model.save(os.path.join(path, 'label_model.pkl'))

    @staticmethod
    def load(path):
        """Load a previously saved modeler.
        
        Args:
            path (str): path to the folder where the model is saved.
        
        Returns:
            Modeler
        """
        # load ruler lfs
        lf_db = LFDB.load(os.path.join(path, 'LF_DB.json'))
        # load custom lfs
        head, tail = os.path.split(path)
        sys.path.insert(0, head)
        custom_functions = import_module(tail + '.custom_functions')
        reload(custom_functions)
        my_lfs = custom_functions.my_lfs
        import inspect
        to_add = [LabelingFunction(f=lf, 
                    name=lf.__name__, 
                    as_string=inspect.getsource(lf)
                    ) for i, lf in enumerate(my_lfs)]
        lf_db.add_lfs(to_add)

        # load label_model
        label_model = LabelModel()
        label_model.load(os.path.join(path, 'label_model.pkl'))
        return Modeler(lf_db=lf_db, label_model=label_model, cardinality=label_model.cardinality)

    def get_weights(self):
        """Get the weights assigned to each labeling function
        
        Returns:
            list: weight for each active labeling function
        """
        if self.has_lfs():
            return self.label_model.get_weights()
        else:
            return []

    def analyze_lfs(self, dataset, labels=None):
        """Create a dataframe analysis of coverage, conflict, accuracy, etc for each LF.
        
        Args:
            dataset (Dataset or pandas.DataFrame): over which to compute coverage, conflicts, etc
            labels (None, optional): The ground truth labels for the dataset, used to compute accuracy.
        
        Returns:
            pandas.DataFrame: a row for each LF, and a column for each statistic.
        
        Raises:
            AttributeError: if modeler has no active labeling functions, no analysis can be performed.
        """
        if self.has_lfs():
            if labels is not None:
                L = self.apply(dataset)
                df = LFAnalysis(L=L, lfs=self.get_lfs()).lf_summary(Y=labels)

                # For some reason, the columns "Correct" and "Incorrect" are not correctly calculated by Snorkel LFAnalysis (irony)
                # We compute this manually
                n, m = L.shape
                Y = labels
                labels = np.unique(
                    np.concatenate((Y.flatten(), L.flatten(), np.array([-1])))
                )
                confusions = [
                    metrics.confusion_matrix(Y, L[:, i], labels)[1:, 1:] for i in range(m)
                ]
                corrects = [np.diagonal(conf).sum() for conf in confusions]
                incorrects = [
                    conf.sum() - correct for conf, correct in zip(confusions, corrects)
                ]

                df["Correct"] = corrects
                df["Incorrect"] = incorrects
            else:
                df = LFAnalysis(L=self.apply(dataset), lfs=self.get_lfs()).lf_summary()
            return df
        else:
            raise AttributeError("analyze_lfs called when Modeler has no labeling functions.")

    def GLL_repr(self, include_inactive=False):
        """Get a human-readable (generalized labeling language) representation of the labeling functions.
        
        Args:
            include_inactive (bool, optional): Whether to include deactivated LFs
        
        Returns:
            dict: {lf ID: lf representation}
        """
        return self.lf_db.GLL_repr(include_inactive=include_inactive)

    def record_stats(self, stats: dict):
        """Record the latest statistics for the labeling functions
        
        Args:
            stats (dict): {LF ID: statistics dictionary}
        
        Returns:
            dict: the complete labeling function statistics, 
                potentially a superset of the passed statistics.
        """
        return self.lf_db.update(stats)

    def update_concept(self, concept: str, deleted=False):
        """When a concept is updated, update the uuids of the LFs that use that concept (since they 
        will have a new labelling signature)
        
        Args:
            concept (str): the concept that was updated
            deleted (bool, optional): whether the concept was deleted. 
                In this case, the relevant LFs will be deleted.
        """
        self.lf_db.update_concept(concept)


class LFDB:
    """Stores labeling functions and their associated statistics.
    Functions generated by Ruler will be saved and loaded with save() and load(),
    respectively, but custom python functions must be written to the modeler's 
    custom python function file [path_to_modeler]/custom_functions.py
    
    Attributes:
        db (dict): {LF ID: LabelingFunction}
    """
    
    def __init__(self, db={}):
        self.db = db

    def __contains__(self, item: str):
        return item in self.db

    def __len__(self):
        return len(self.db)

    def __getitem__(self, lf_id):
        return self.db[lf_id]

    def get_lfs(self, include_inactive=False):
        """Get all labeling functions in DB
        
        Args:
            include_inactive (bool, optional): whether to include deactivated functions
        
        Returns:
            list(LabelingFunction)
        """
        if include_inactive:
            return list(self.db.values())
        else:
            return [lf for lf in self.db.values() if lf.active]

    def GLL_repr(self, include_inactive=False):
        GLL_representations = {lf.name: lf.GLL_repr() for lf in self.get_lfs(include_inactive=include_inactive)}
        return pd.DataFrame.from_dict(GLL_representations, orient="index")

    def add_lfs(self, new_lfs: list):
        """Add labeling functions
        
        Args:
            new_lfs (list(LabelingFunction))
        """
        for lf in new_lfs:
            name = lf.name
            if not name in self.db:
                lf.submit()
                lf.activate()
                self.db[name] = lf
            else:
                self.db[name].activate()

    def delete(self, lf_id: str):
        """Delete a labeling function
        
        Args:
            lf_id (str): the ID
        
        Returns:
            LabelingFunction: the deleted function
        """
        return self.db.pop(lf_id)

    def deactivate(self, lf_id: str):
        """Deactivate a labeling function. The function is still in the database, 
        but will not be used in modeler.apply
        
        Args:
            lf_id (str): the ID
        
        Returns:
            LabelingFunction: the deactivated function
        """
        self.db[lf_id].deactivate()
        return self.db[lf_id]

    def update_concept(self, concept: str, deleted=False):
        """When a concept is updated, update the uuids of the LFs that use that concept (since they 
        will have a new labelling signature)
        
        Args:
            concept (str): the concept that was updated
            deleted (bool, optional): whether the concept was deleted. 
                In this case, the relevant LFs will be deleted.
        """
        def condition_uses_concept(cond):
            if cond['type'] == KeyType[CONCEPT]:
                if cond['string'] == concept:
                    return True
            return False

        for lf_id, lf in self.db.items():
            conds = lf.GLL_repr()[CONDS]
            if conds is not None:
                if any([condition_uses_concept(cond) for cond in conds]):
                    if deleted:
                        self.delete(lf_id)
                    else:
                        lf.new_uuid()

    def update(self, stats: dict):
        """Update the recorded statistics over labeling functions
        
        Args:
            stats (dict): May include things like coverage, conflicts, accuracy, etc.
        
        Returns:
            dict: a copy of the current statistics. This may be a superset of the submitted statistics.
        """
        for lf_id, stats_dict in stats.items():
            self.db[lf_id].update(stats_dict)
        return self.db.copy()

    def save(self, path):
        """Save the labeling functions. Only the GLL (Generalized Labeling Language) functions that Ruler
        generates will be saved on this path. Any custom python functions must be submitted via a python file
        [path_to_modeler]/custom_functions.py, where they are stored.

        Args:
            path (string): Path to file where the json representation of the LF_DB will be written.
        """
        with open(path, "w+") as file:
            db_json = {
                lf_id: lf.to_json() \
                    for lf_id, lf in self.db.items() \
                    if lf.has_GLL_repr()
            }
            json.dump(db_json, file, default=str, indent=2)

    @staticmethod
    def load(path):
        """Load a previously saved GLL representations of labeling functions into a new LF_DB
        
        Args:
            path (string): Path to json representation of LF_DB
        
        Returns:
            LF_DB
        """
        with open(path, "r") as file:
            db_json = json.load(file)
            print(db_json)
            db = {
                lf_id: LabelingFunction.read_json(lf_json) \
                    for lf_id, lf_json in db_json.items()
            }
            return LFDB(db=db)
