import unittest

from synthesizer.gll import *
from verifier.translator import make_lf
from types import SimpleNamespace

class translatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_one_token(self):
        instance = {
            "name": "test_lf",
            LABEL: 1,
            DIRECTION: False,
            CONNECTIVE: ConnectiveType[OR],
            CONDS: [{"string": "great", "type": KeyType[TOKEN]}]
        }
        concepts = {}
        lf = make_lf(instance, concepts)
        Positives = [
            "This is great!!!", 
            "Great stuff.",
            "such ~GREAT~ work"]
        Negatives = [
            "The greatest of all time",
            "gre at",
            "Hi mom"
        ]
        for ex in Positives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), 1, msg=ex)
        for ex in Negatives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), -1, msg=ex)

    def test_one_concept(self):
        instance = {
            "name": "test_lf",
            LABEL: 1,
            DIRECTION: False,
            CONNECTIVE: ConnectiveType[OR],
            CONDS: [{"string": "emphasis", "type": KeyType[CONCEPT]}]
        }

        concepts = {
            "emphasis": [
                {"string": "very", "type": KeyType[TOKEN]},
                {"string": "so+", "type": KeyType[REGEXP], "case_sensitive": False},
                {"string": "[Ee]xtreme\w+", "type": KeyType[REGEXP], "case_sensitive": True}
            ]
        }
        lf = make_lf(instance, concepts)

        Positives = [
            "This is soooooo great!!!", 
            "I'm extremely impressed.",
            "VERY good test cases"]
        Negatives = [
            "The greatest of all time",
            "s good",
            "it's just not for me"
        ]

        for ex in Positives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), 1, msg=ex)

        for ex in Negatives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), -1, msg=ex)

    def test_OR(self):
        instance = {
            "name": "test_lf",
            LABEL: 1,
            DIRECTION: False,
            CONNECTIVE: ConnectiveType[OR],
            CONDS: [{"string": "emphasis", "type": KeyType[CONCEPT]}, {"string": "great", "type": KeyType[TOKEN], "case_sensitive": False}]
        }

        concepts = {
            "emphasis": [
                {"string": "very", "type": KeyType[TOKEN]},
                {"string": "so+", "type": KeyType[REGEXP], "case_sensitive": False},
                {"string": "[Ee]xtreme\w+", "type": KeyType[REGEXP], "case_sensitive": True}
            ]
        }
        lf = make_lf(instance, concepts)
        Positives = [
            "This is great!!!", 
            "Great stuff.",
            "such ~GREAT~ work",
            "This is soooooo great!!!", 
            "I'm extremely impressed.",
            "VERY good test cases"]
        Negatives = [
            "The best of all time",
            "s good",
            "it's just not for me"
        ]

        for ex in Positives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), 1, msg=ex)

        for ex in Negatives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), -1, msg=ex)


    def test_AND(self):
        instance = {
            "name": "test_lf",
            LABEL: 1,
            DIRECTION: False,
            CONNECTIVE: ConnectiveType[AND],
            CONDS: [{"string": "emphasis", "type": KeyType[CONCEPT]}, {"string": "great", "type": KeyType[TOKEN], "case_sensitive": False}]
        }

        concepts = {
            "emphasis": [
                {"string": "very", "type": KeyType[TOKEN]},
                {"string": "so+", "type": KeyType[REGEXP], "case_sensitive": False},
                {"string": "[Ee]xtreme\w+", "type": KeyType[REGEXP], "case_sensitive": True}
            ]
        }
        lf = make_lf(instance, concepts)
        Positives = [
            "This is sooooo great!!!", 
            "such extremely ~GREAT~ work",
            "I'm extremely impressed by the great work."]
        Negatives = [
            "The best of all time",
            "Great stuff.",
            "so very very good",
            "it's just not for me"
        ]

        for ex in Positives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), 1, msg=ex)

        for ex in Negatives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), -1, msg=ex)

    def test_directional(self):
        instance = {
            "name": "test_lf",
            LABEL: 1,
            DIRECTION: True,
            CONNECTIVE: ConnectiveType[AND],
            CONDS: [{"string": "emphasis", "type": KeyType[CONCEPT]}, {"string": "great", "type": KeyType[TOKEN], "case_sensitive": False}]
        }

        concepts = {
            "emphasis": [
                {"string": "very", "type": KeyType[TOKEN]},
                {"string": "so+", "type": KeyType[REGEXP], "case_sensitive": False},
                {"string": "[Ee]xtreme\w+", "type": KeyType[REGEXP], "case_sensitive": True}
            ]
        }
        lf = make_lf(instance, concepts)
        Positives = [
            "This is sooooo great!!!", 
            "This is SOOOO great!!!",
            "such extremely ~GREAT~ work",
            "I'm extremely impressed by the great work."]
        Negatives = [
            "The best of all time",
            "Great stuff.",
            "so very very good",
            "it's just not for me",
            "The great work is extremely impressive."
        ]

        for ex in Positives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), 1, msg=ex)

        for ex in Negatives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), -1, msg=ex)

    def test_NER(self):

        instance = {
            "name": "test_lf",
            LABEL: 1,
            DIRECTION: False,
            CONNECTIVE: ConnectiveType[OR],
            CONDS: [{"string": "ORG", "type": KeyType[NER]}]
        }
        concepts = {}
        lf = make_lf(instance, concepts)
        Positives = [
            "The FBI is here", 
            "I called the World Bank",
            "MVPD is here to serve."]
        Negatives = [
            "The greatest of all time",
            "gre at",
            "Hi mom"
        ]
        for ex in Positives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), 1, msg=ex)
        for ex in Negatives:
            x = SimpleNamespace(text=ex)
            self.assertEqual(lf(x), -1, msg=ex)

if __name__ == '__main__':
    unittest.main()
