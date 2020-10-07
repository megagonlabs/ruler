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
        path = 'datasets/test_dataset/processed.csv'
        self.dataset.save(path)
        L = self.dataset.apply_lfs(self.lfs) 
        d2 = Dataset.load(path)
        L2 = d2.apply_lfs(self.lfs)
        self.assertTrue((L==L2).all())
        #os.remove(path)


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
        sample = [
            ["z12pgdhovmrktzm3i23es5d5junftft3f","lekanaVEVO1","2014-07-22T15:27:50","i love this so much. AND also I Generate Free Leads on Auto Pilot &amp; You Can  Too! http://www.MyLeaderGate.com/moretraffic﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z13yx345uxepetggz04ci5rjcxeohzlrtf4","Pyunghee","2014-07-27T01:57:16","http://www.billboard.com/articles/columns/pop-shop/6174122/fan-army-face-off-round-3 Vote for SONES please....we're against vips....please help us.. &gt;.&lt;﻿",1],
            ["z12lsjvi3wa5x1vwh04cibeaqnzrevxajw00k","Erica Ross","2014-07-27T02:51:43","\"Hey guys! Please join me in my fight to help abused/mistreated animals! All  fund will go to helping pay for vet bills/and or helping them find homes! I  will place an extra emphasis on helping disabled animals, ones otherwise  would just be put to sleep by other animal organizations. Donate please. http://www.gofundme.com/Angels-n-Wingz﻿\"",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["z13jcjuovxbwfr0ge04cev2ipsjdfdurwck","Aviel Haimov","2014-08-01T12:27:48","http://psnboss.com/?ref=2tGgp3pV6L this is the song﻿",1],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["5","Ted","2014-08-01T12:27:48","This is the best music video I ever saw",0],
            ["6","Tom","2014-08-01T12:27:48","So good",0],
            ["7","Myra","2014-08-01T12:27:48","Great",0]
        ]
        df = pd.DataFrame(sample, columns=["COMMENT_ID","AUTHOR","DATE","CONTENT","CLASS"])

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
            "data": ['From: v064mb9k@ubvmsd.cc.buffalo.edu (NEIL B. GANDLER)\nSubject: Need info on 88-89 Bonneville\nOrganization: University at Buffalo\nLines: 10\nNews-Software: VAX/VMS VNEWS 1.41\nNntp-Posting-Host: ubvmsd.cc.buffalo.edu\n\n\n I am a little confused on all of the models of the 88-89 bonnevilles.\nI have heard of the LE SE LSE SSE SSEI. Could someone tell me the\ndifferences are far as features or performance. I am also curious to\nknow what the book value is for prefereably the 89 model. And how much\nless than book value can you usually get them for. In other words how\nmuch are they in demand this time of year. I have heard that the mid-spring\nearly summer is the best time to buy.\n\n\t\t\tNeil Gandler\n',
                'From: Rick Miller <rick@ee.uwm.edu>\nSubject: X-Face?\nOrganization: Just me.\nLines: 17\nDistribution: world\nNNTP-Posting-Host: 129.89.2.33\nSummary: Go ahead... swamp me.  <EEP!>\n\nI\'m not familiar at all with the format of these "X-Face:" thingies, but\nafter seeing them in some folks\' headers, I\'ve *got* to *see* them (and\nmaybe make one of my own)!\n\nI\'ve got "dpg-view" on my Linux box (which displays "uncompressed X-Faces")\nand I\'ve managed to compile [un]compface too... but now that I\'m *looking*\nfor them, I can\'t seem to find any X-Face:\'s in anyones news headers!  :-(\n\nCould you, would you, please send me your "X-Face:" header?\n\nI *know* I\'ll probably get a little swamped, but I can handle it.\n\n\t...I hope.\n\nRick Miller  <rick@ee.uwm.edu> | <ricxjo@discus.mil.wi.us>   Ricxjo Muelisto\nSend a postcard, get one back! | Enposxtigu bildkarton kaj vi ricevos alion!\n          RICK MILLER // 16203 WOODS // MUSKEGO, WIS. 53150 // USA\n',
                'From: mathew <mathew@mantis.co.uk>\nSubject: Re: STRONG & weak Atheism\nOrganization: Mantis Consultants, Cambridge. UK.\nX-Newsreader: rusnews v1.02\nLines: 9\n\nacooper@mac.cc.macalstr.edu (Turin Turambar, ME Department of Utter Misery) writes:\n> Did that FAQ ever got modified to re-define strong atheists as not those who\n> assert the nonexistence of God, but as those who assert that they BELIEVE in \n> the nonexistence of God?\n\nIn a word, yes.\n\n\nmathew\n'],
            "filenames": ['/Users/sara/scikit_learn_data/20news_home/20news-bydate-test/rec.autos/103343',
                '/Users/sara/scikit_learn_data/20news_home/20news-bydate-test/comp.windows.x/67445',
                '/Users/sara/scikit_learn_data/20news_home/20news-bydate-test/alt.atheism/53603'],
            "target_names": ['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc'],
            "target": [7, 5, 0],
            "DESCR": 'This is the 20 newsgroups dataset'
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