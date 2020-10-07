import pandas as pd
import unittest

from api.dataset import Dataset
from api.project import Project


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
        sample = [
            ["0","lekanaVEVO1","2014-07-22T15:27:55","i love this so much.",0],
            ["1","lekanaVEVO1","2014-07-22T15:27:50","i love this so much. AND also I Generate Free Leads on Auto Pilot &amp; You Can  Too! http://www.MyLeaderGate.com/moretraffic﻿",1],
            ["2","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["3","Erica Ross","2014-07-27T02:51:43","\"Hey guys! Please join me in my fight to help abused/mistreated animals! All  fund will go to helping pay for vet bills/and or helping them find homes! I  will place an extra emphasis on helping disabled animals, ones otherwise  would just be put to sleep by other animal organizations. Donate please. http://www.gofundme.com/Angels-n-Wingz﻿\"",1],
            ["4","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["6","Tom","2014-08-01T12:27:48","So good",0],
            ["7","Myra","2014-08-01T12:27:48","Great",0]
        ]
        df = pd.DataFrame(sample, columns=["COMMENT_ID","AUTHOR","DATE","text","label"])
        dataset = Dataset(df)

        test_datasets_dict = {
            "train": dataset,
            "dev": dataset,
            "test": dataset,
            "valid": dataset
        }
        self.project.set_datasets(test_datasets_dict)

    def test_prep_datasets(self):
        self.project.prep_datasets('test_dataset', test_split=False)

    def test_readiness(self):
        # TODO: assert labels and cardinality match
        # make sure that if self.project.ready() is true, all the endpoints work
        pass