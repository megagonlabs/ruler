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
DIRECTION = 'Direction'
CONDS = 'Conditions'
WEIGHT = 'Weight'
LABEL = 'Label'
ID = 'ID'

AND = 'AND'
OR = 'OR'
TOKEN = 'TOKEN'
REGEXP = 'REGEXP'
CONCEPT = 'CONCEPT'
NER = 'NER'

ConnectiveType = {AND: 0, OR: 1}

KeyType = {TOKEN: 0, CONCEPT: 1, NER: 2, REGEXP: 3}


class ConceptWrapper:
    filename = 'concept_collection.json'
    def __init__(self, d={}):
        self.dict = d

    def __str__(self):
        return self.name

    def get_dict(self):
        return self.dict

    def add_element(self, name: str, elements):
        self.dict[name] = elements

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



# user defined token, usually a word
class Token:
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


# user defined binary relationship
class Relationship:
    def __init__(self, type: RelationshipType):
        self.list = [] # a list of Token
        self.type = type

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
        else:
            for crnt_instance in instances:
                crnt_instance[CONNECTIVE] = ConnectiveType[AND]

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
                crnt_cond_concept = {crnt_token.concept_name: KeyType[CONCEPT]}
                for crnt_instance in cp_instances:
                    crnt_instance[CONDS].append(crnt_cond_concept)

            elif crnt_token.ner_type is not None:
                # make a copy too, the new one is for adding ner
                cp_instances = copy.deepcopy(instances)
                crnt_cond_ner = {crnt_token.ner_type: KeyType[NER]}
                for crnt_instance in cp_instances:
                    crnt_instance[CONDS].append(crnt_cond_ner)

            # add token into instances
            crnt_cond_token = {crnt_token.text.lower(): KeyType[TOKEN]}
            for crnt_instance in instances:
                crnt_instance[CONDS].append(crnt_cond_token)

            # merge the cp_instances into instances
            if cp_instances is not None:
                instances.extend(cp_instances)

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
