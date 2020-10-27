import numpy as np
import os
import pandas as pd
import unittest

from api.dataset import Dataset, DataPreparer
from verifier.labeling_function import LabelingFunction


class datasetTest(unittest.TestCase):

    def setUp(self):
        lfs = [
            LabelingFunction(name="1",  f=lambda x: 1), 
            LabelingFunction(name="0",  f=lambda x: 0),
            LabelingFunction(name="pos",f=lambda x: 1 if x.text=="positive" else -1), 
            LabelingFunction(name="neg",f=lambda x: 1 if x.text=="negative" else 0)
        ]
        self.lfs = lfs

        sample = [
            [0,"People ask me ""Who was that singing? It was amazing!""",1, 'dev'],
            [1,"Best purchase ever",1, 'dev'], 
            [2,"After about a year, the batteries would not hold a charge. ",0, 'dev'],
            [3,"So many bugs!",0, 'dev'],
            [4,"What a terrible product", -1, 'train'],
            [5,"What a terrible product", -1, 'train'],
            [6,"Nice stuff they're doing these days with the innovation and such", -1, 'train'],
            [7,"This is not what I wanted for Christmas", -1, 'train'],
        ]
        df = pd.DataFrame(sample, columns=["idx", "text", "label", "split"])
        self.dataset = Dataset(df)

        self.data_preparer = DataPreparer()

    def test_apply(self):
        L = self.dataset.apply_lfs(self.lfs) 
        self.assertEqual(L.shape, (len(self.dataset), len(self.lfs)))

        L2 = self.dataset.apply_lfs(self.lfs) 
        self.assertTrue((L==L2).all())

    def test_save(self):
        path = 'datasets/sentiment_example/processed.csv'
        self.dataset.save(path)
        L = self.dataset.apply_lfs(self.lfs) 
        d2 = Dataset.load(path)
        L2 = d2.apply_lfs(self.lfs)
        self.assertTrue((L==L2).all())

    """Make sure data upload works for the formats we want to support
     """
    def test_upload_amazon_reviews(self):
        sample = [
            [0,"People ask me ""Who was that singing? It was amazing!""",1],
            [1,"Best purchase ever",1], 
            [2,"Best purchase ever",1], 
            [3,"Best purchase ever",1], 
            [4,"Best purchase ever",1], 
            [5,"Best purchase ever",1], 
            [6,"After about a year, the batteries would not hold a charge. ",0],
            [7,"After about a year, the batteries would not hold a charge. ",0],
            [8,"After about a year, the batteries would not hold a charge. ",0],
            [9,"After about a year, the batteries would not hold a charge. ",0],
            [10,"So many bugs!",0]]

        df = pd.DataFrame(sample)

        data_preparer = DataPreparer()

        pdf = data_preparer.set_headers(df)
        df_split = data_preparer.make_splits(pdf, test_split=False)

        df_final = data_preparer.precompute_values(df_split)
        dsets = data_preparer.split(df_final)

        for dset in dsets.values():
            dset.apply_lfs(self.lfs)
        self.assertEqual(len(dsets['dev']['label'].value_counts()), 2)

    def test_upload_youtube_comments(self):
        df = pd.read_csv("datasets/spam_example/example_dataset.csv", header=0)

        data_preparer = DataPreparer()

        pdf = data_preparer.set_headers(df)
        df_split = data_preparer.make_splits(pdf)
        df_final = data_preparer.precompute_values(df_split)
        dsets = data_preparer.split(df_final)

        for split in ['train', 'test', 'dev', 'valid']:
            dsets[split].apply_lfs(self.lfs)

        self.assertEqual(len(dsets['dev']['label'].value_counts()), 2)


    def test_upload_newsgroups(self):
        sample = {
            "data": ['My harddrive catches on fire every time a watch cat videos. Do I need to download more RAM?',
                'From: Sasha <iluvguns>\nSubject: Specialty Ammo\n Where do people buy silver bullets in bulk?',
                'Send me your address and I\'ll mail you gunpowder. First ten people to comment!'],
            "filenames": ['/file/path/one',
                '/file/path/two',
                '/file/path/three'],
            "target_names": ['comp.electronics', 'politics.guns', 'politics.guns'],
            "target": [7, 5, 0],
            "DESCR": 'This is a sample in the format of the 20 newsgroups dataset'
        }

        df = pd.DataFrame(sample)

        data_preparer = DataPreparer()

        pdf = data_preparer.set_headers(df)

        df_split = data_preparer.make_splits(pdf, test_split=False)
        df_final = data_preparer.precompute_values(df_split)
        dsets = data_preparer.split(df_final)

        for dset in dsets.values():
            dset.apply_lfs(self.lfs)

        self.assertEqual(len(df_final['label'].value_counts()), 3)


if __name__ == '__main__':
    unittest.main()