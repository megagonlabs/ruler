from enum import Enum
import copy
import json
import os


class RelationshipType(Enum):
    SET = 0
    UNDIRECTED = 1
    DIRECTED = 2


DELIMITER = '#'
CONNECTIVE = 'Connective'
CONTEXT = 'Context'
DIRECTION = 'Direction'
CONDS = 'Conditions'
WEIGHT = 'Weight'
LABEL = 'Label'
ID = 'ID'

AND = 'AND' # all conditions occuring anywhere in the text
OR = 'OR' # any of the conditions occuring

TOKEN = 'TOKEN'
REGEXP = 'REGEXP'
CONCEPT = 'CONCEPT'
NER = 'NER'

SENTENCE = "SENTENCE"

ConnectiveType = {OR: 0, AND: 1}

ContextType = {SENTENCE: 1}

KeyType = {TOKEN: 0, CONCEPT: 1, NER: 2, REGEXP: 3}


class ConceptWrapper:
    filename = 'concept_collection.json'
    def __init__(self, d={}):
        self.dict = d

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.dict.keys())

    def get_dict(self):
        return self.dict

    def add_element(self, name: str, elements):
        # make sure there are no duplicates in elements:
        def unique_hash(elt):
            string_id = "#".join([elt.get("string"), str(elt.get("case_sensitive")), str(elt.get("type"))])
            elt["key"] = string_id
            return string_id
        elt_hashes = {unique_hash(elt): elt for elt in elements}
        self.dict[name] = list(elt_hashes.values())

    def get_elements(self, name: str):
        return self.dict[name]

    def delete_element(self, name: str, elements):
        assert name in self.dict.keys()
        for element in elements:
            self.dict[name].remove(element)

    def delete_concept(self, name: str):
        assert name in self.dict.keys()
        del self.dict[name]

    def save(self, dirname):
        with open(os.path.join(dirname, self.filename), "w+") as file:
            json.dump(self.dict, file)

    def load(self, dirname):
        with open(os.path.join(dirname, self.filename), "r") as file:
            self.dict = json.load(file)


class Token:

    """user defined token, usually a word 
    
    Attributes:
        concept_name (string): if the token is assigned to a concept, the name of the concept
        ner_type (string): spacy-defined Named Entity code (for example, ORDINAL for "first")
        sent_idx (int): Which sentence in the document the token belongs to
        text (string): the text of the token
    """
    
    def __init__(self, T):
        self.text = T
        self.sent_idx = -1
        self.concept_name = None
        self.ner_type = None

    def __str__(self):
        return self.text

    def assign_concept(self, c):
        self.concept_name = c

    def assign_sent_idx(self, i):
        self.sent_idx = i

    def assign_ner_type(self, ner):
        self.ner_type = ner


class Relationship:

    """user defined relationshpi between a set of Tokens. 
    Can be OR, AND (directional or non-directional)
    
    Attributes:
        list (Token): List of annotated spans
        same_sentence (bool): Whether or not the conditions must occur in the same sentence
        type (int): A code describing the relationship type (AND, OR, etc.)
    """
    
    def __init__(self, type: RelationshipType):
        self.list = [] # a list of Token
        self.type = type
        self.context = None

    def __str__(self):
        pass

    # add the Token to relationship, depending on the rel_code
    # rel_code: None SET
    # 0-100: UNDIRECTED
    # negative (<-100): positive (>100) DIRECTED: negative -> positive
    def add(self, token: Token, rel_code):
        if rel_code is None:
            assert self.type == RelationshipType.SET
            self.list.append(token)
        elif abs(rel_code) < 100:
            assert self.type == RelationshipType.UNDIRECTED
            self.list.append(token)
        else:
            assert self.type == RelationshipType.DIRECTED
            if rel_code < 0:
                self.list.insert(0, token)
            else:
                self.list.insert(1, token)

    # return a list of instances
    def get_instances(self, concepts):
        instances = []
        if len(self.list) == 0:
            return instances

        # init first instance
        crnt_instance = {CONDS: []}
        instances.append(crnt_instance)

        if self.type == RelationshipType.SET:
            for crnt_instance in instances:
                crnt_instance[CONNECTIVE] = ConnectiveType[OR]
                crnt_instance["CONNECTIVE_"] = OR
        else:
            for crnt_instance in instances:
                crnt_instance[CONNECTIVE] = ConnectiveType[AND]
                crnt_instance["CONNECTIVE_"] = AND

        if self.type == RelationshipType.DIRECTED:
            for crnt_instance in instances:
                crnt_instance[DIRECTION] = True
        else:
            for crnt_instance in instances:
                crnt_instance[DIRECTION] = False

        for crnt_token in self.list:
            cp_instances = None
            if crnt_token.concept_name is not None:
                # copy previous instances, one for adding token, the other for adding concept
                cp_instances = copy.deepcopy(instances)
                crnt_cond_concept = Condition(crnt_token.concept_name, CONCEPT)
                for crnt_instance in cp_instances:
                    crnt_instance[CONDS].append(crnt_cond_concept)

            elif crnt_token.ner_type is not None:
                # make a copy too, the new one is for adding ner
                cp_instances = copy.deepcopy(instances)
                crnt_cond_ner = Condition(crnt_token.ner_type, NER)
                for crnt_instance in cp_instances:
                    crnt_instance[CONDS].append(crnt_cond_ner)
            # add token into instances
            crnt_cond_token = Condition(crnt_token.text.lower(), TOKEN, False)
            for crnt_instance in instances:
                crnt_instance[CONDS].append(crnt_cond_token)
            # merge the cp_instances into instances
            if cp_instances is not None:
                instances.extend(cp_instances)

        cp_instances = []

        for crnt_instance in instances:
            if crnt_instance[CONNECTIVE] == ConnectiveType[AND]:
                # if the connective type is AND, and the conditions are in the same sentence, 
                # create a duplicate instance with the connective type AND_SENTENCE
                sentence_idx = self.list[0].sent_idx
                same_sent = True
                for token in self.list:
                    if token.sent_idx != sentence_idx:
                        same_sent = False
                if same_sent:
                    print("same sentence!")
                    new_instance = copy.deepcopy(crnt_instance)
                    new_instance[CONTEXT] = ContextType[SENTENCE]
                    new_instance["CONTEXT_"] = SENTENCE
                    cp_instances.append(new_instance)

        if len(cp_instances) > 0:
            instances.extend(cp_instances)
        print("all instances: ")
        for crnt_instance in instances:
            print(crnt_instance)
        return instances


# for classification problem, this is the label class
class Label:
    def __init__(self, name):
        self.task_name = name
        self.dict = {"ABSTAIN": -1}
        self.count = 0

    def add_label(self, lname: str):
        self.dict[lname] = self.count
        self.count += 1

    def to_int(self, lname: str):
        return self.dict[lname]

    def to_name(self, i: int):
        for k, v in self.dict.items():
            if i == v:
                return k

    def to_dict(self):
        crnt_keys = list(self.dict.keys())
        crnt_keys.remove("ABSTAIN")
        return {lname: self.dict[lname] for lname in crnt_keys}

def Condition(string, type_str, case_sensitive=False):
    return {
        "string": string, 
        "type": KeyType[type_str], 
        "TYPE_": type_str,
        "case_sensitive": case_sensitive 
    }
