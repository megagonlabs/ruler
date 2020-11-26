import numpy as np
import os
import pandas as pd

from snorkel.labeling import PandasLFApplier
from synthesizer.parser import nlp

from config import DATASETS_PATH
from config import DEFAULT_MAX_TRAINING_SIZE
from config import MIN_LABELLED_SIZE
from config import PROCESSED_FILE_NAME

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename: str):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Dataset:
    def __init__(self, dataframe):
        assert 'text' in dataframe.columns
        if not "seen" in dataframe.columns:
            dataframe.loc[:,"seen"] = 0
        self.df = dataframe

    def __len__(self):
        return len(self.df)

    def __getitem__(self, x):
        return self.df[x]

    def __contains__(self, x):
        return x in self.df

    @staticmethod
    def load(path, force_prep = False):
        df = pd.read_csv(path)
        df['seen'] = 0
        return Dataset(df)

    def save(self, path, y=None):
        """Save the dataset to a file, with versioning.
        
        Args:
            path (string): path to file
            y (matrix, optional): Model predictions. If passed, they will be saved with the data.
        """
        if y is not None:
            for i in range(y.shape[1]):
                self.df["pred_{}".format(i)] = y[:,i]
        self.df.to_csv(path)

    def apply_lfs(self, lfs: list):
        if len(lfs) == 0:
            raise ValueError("Apply_lfs was called with no lfs (api/dataset.py")

        # uuid should change anytime the LF changes
        lf_ids = [lf.uuid for lf in lfs]
        to_apply = [lf for lf in lfs if not lf.uuid in self.df.columns]

        if len(to_apply) > 0:
            applier = PandasLFApplier(lfs=to_apply)
            f_outputs = applier.apply(df=self.df)
            for i, lf in enumerate(to_apply):
                lf_id = lf.uuid
                self.df.at[:,lf_id] = f_outputs[:,i]
        return self.df[lf_ids].values



#### Data preparation utils
class DataPreparer:
    """Converts the data into the correct format, precomputes values, and logs progress"""
    def __init__(self):
        self.launch_progress = 0

    def rename_column(self, old_col_name, new_col_name, df, print_debug=False):
        df = df.rename(columns={old_col_name: new_col_name})
        if print_debug:
            print("Using column \"{}\" for \"{}\"".format(old_col_name, new_col_name))
            print("Example: ")
            print(df[new_col_name].head())
        return df

    def progress(self):
        """Returns value between 0 and 1 describing how much of the data has been prepared"""
        return self.launch_progress

    def update(self, steps):
        """Update progress to approximate percentage of process completed"""
        self.launch_progress += (steps)/self.total

    def set_status(self, status):
        """Record what step of process we're on"""
        self.status = status
        print(status)

    def prepare(self, dataset_uuid, force_prep=False, test_split=True):
        processed_file_path = os.path.join(DATASETS_PATH, dataset_uuid, PROCESSED_FILE_NAME)

        if os.path.exists(processed_file_path) and not force_prep:
            df = pd.read_csv(processed_file_path)
            # Let's say loading the file is ~half the launch time
            # (if the file already exists)
            self.total = 2
            self.update(1)

        else:
            try:
                datafiles = [os.path.join(DATASETS_PATH, dataset_uuid, d) \
                    for d in os.listdir(os.path.join(DATASETS_PATH, dataset_uuid))]
            except NotADirectoryError:
                datafiles = [os.path.join(DATASETS_PATH, dataset_uuid)]
            df = self.process_files(datafiles, test_split=test_split)
            print("Saving processed files at {}".format(os.path.join(DATASETS_PATH, PROCESSED_FILE_NAME)))
            df.to_csv(processed_file_path)
        return self.split(df)

    def mask_labelled(self, label_col_series):
        return label_col_series.notnull()

    def process_files(self, files: list, delimiter=None, max_size=DEFAULT_MAX_TRAINING_SIZE, test_split=True):
        dfs = []
        for i, filename in enumerate(files):
            if allowed_file(filename):

                print("--- filename: " + filename)
                df = pd.read_csv(filename, header=0)
                # Add field indicating source file
                df["file"] = filename
                dfs.append(df)

        df_full = pd.concat(dfs)
        self.total = len(df_full)*(1.1) 

        df_full = self.set_headers(df_full)


        # Remove delimiter chars
        if delimiter is not None:
            df['text'].replace(regex=True, inplace=True, to_replace=delimiter, value=r'')
        df_full = df_full[df_full['text'].notna()]

        self.total = len(df_full)*(1.1) 

        df_split = self.make_splits(df_full, test_split=test_split)
        df_final = self.precompute_values(df_split)

        self.launch_progress = 1.0

        #transform to Datasets
        return df_final

    def split(self, df):
        return {
            data_split: Dataset(df[df['split']==data_split]) \
                for data_split in list(df['split'].value_counts().index)
        }        

    def make_splits(self, df, test_split=True, max_size=DEFAULT_MAX_TRAINING_SIZE):
        if len(df) < 10:
            test_split = False

        # shuffle the order
        df = df.sample(frac=1, random_state=123)

        # split the data into labelled and training (unlabelled)
        try:
            mask = self.mask_labelled(df.label)
        except KeyError:
            # no labels available
            # all the data is (unlabelled) training data
            df['split'] = 'train'
            return df

        labelled = df[mask]
        training = df[~mask]

        # if all the data provided is labelled, 
        # set some aside to use for interaction examples (training set)
        if len(training) == 0:
            np.random.seed(123)
            msk = np.random.rand(len(df)) < 0.5
            training = df[msk]
            labelled = df[~msk]

        # Make sure we have enough labelled data
        if len(labelled) <= MIN_LABELLED_SIZE:
            print("WARNING (dataset.py) Not enough labelled data. \
            (Only {} examples detected)".format(len(labelled)))

        labelled = labelled[:min(max_size, len(labelled))].reset_index(drop=True)
        if test_split:
            fifth = int(len(labelled)/5)
            labelled.at[:fifth*2, 'split'] = 'dev'
            labelled.at[fifth*2:fifth*3, 'split'] = 'valid'
            labelled.at[fifth*3:, 'split'] = 'test'
        else:
            labelled['split'] = 'dev'

        training = training[:min(max_size, len(training))]
        training['split'] = 'train'

        # reset index
        df_split = pd.concat([labelled, training])
        df_split = df_split.reset_index(drop=True)

        # make sure we have train and dev splits
        available_splits = list(df_split['split'].value_counts().index)
        for split_name in 'train', 'dev':
            assert split_name in available_splits

        return df_split

    def precompute_values(self, df):
        """Precompute values that labelling functions will need to use
        Currently only named entities are precomputed"""
        self.total = len(df)*(1.1) 

        with nlp.disable_pipes("tagger", "parser"):
            def ner_tags(row):
                self.update(1)
                doc = nlp(row.text)
                for ent in doc.ents:
                    row[ent.label_] = (doc[ent.start-1].idx, doc[ent.end-2].idx + len(doc[ent.end-2].text))
                return row
            POSSIBLE_NER = ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 
                'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 
                'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 
                'TIME', 'WORK_OF_ART']
            for NE in POSSIBLE_NER:
                df[NE] = False

            return df.apply(ner_tags, axis=1)

    def set_headers(self, df):
        if not 'text' in df.columns:
            obj_columns = df.select_dtypes(include=["object"], exclude=["number"])

            longest_avg_string_col = max(obj_columns, key=lambda x: df[x].apply(lambda x: len(str(x))).mean())
            df = self.rename_column(longest_avg_string_col, 'text', df)
            print(df)

        if 'label' in df.columns:
            return df

        for col in df.columns:
            if str(col).lower() in ['class', 'label', 'target']:
                df = self.rename_column(col, 'label', df)
                return df

        integer_columns = df.select_dtypes(include=['int64'])
        for col in integer_columns:
            if len(df[col].value_counts()) < min(20, len(df)):
                label_found = True
                df = self.rename_column(col, 'label', df)
                return df

        print("WARNING (dataset.py): No label column found. Try renaming your label column to 'label', if you have one.")
        df['label'] = None
        return df



if __name__=='__main__':
    dp = DataPreparer()
    datasets = dp.prepare('Amazon Reviews')


