"""Translate a dictionary explaining a labeling rule into a function
"""
import re
import sys

from synthesizer.gll import *
from synthesizer.parser import nlp

def raw_stringify(s):
    """From a regex create a regular expression that finds occurences of the string as entire words
    
    Args:
        s (string): the string to look for
    
    Returns:
        string: a regular expession that looks for this string surrounded by non word characters
    """
    return "(?:(?<=\W)|(?<=^))({})(?=\W|$)".format(re.escape(s))

def find_indices(cond_dict: dict, text: str):
    """Find all instances of this condition in the text
    """
    v = cond_dict["type"]
    k = cond_dict["string"]
    case_sensitive = True if cond_dict.get("case_sensitive") else False

    if v == KeyType[NER]:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == k:
                return [(doc[ent.start].idx, doc[ent.end-1].idx + len(doc[ent.end-1].text))]
        return []
    if case_sensitive:
        return [(m.start(), m.end()) for m in re.finditer(k, text)]
    else:
        return [(m.start(), m.end()) for m in re.finditer(k, text, re.IGNORECASE)]

def to_lf(x, instance, concepts):
    """from one instance (in dict) to one labeling function
    
    Args:
        x: Object with an attribute "text", which is a string 
        instance (dict): describes the LABEL, DIRECTION, CONNECTIVE, and CONDITIONS of the rule
        concepts (dict): all the defined concepts
    
    Returns:
        int: the label assigned by this function
    """
    label = instance.get(LABEL)
    direction = bool(instance.get(DIRECTION))
    conn = instance.get(CONNECTIVE)
    conds = instance.get(CONDS)
    context = instance.get(CONTEXT)

    text = x.text

    matched_idxes = []

    for crnt_cond in conds:
        # crnt_cond is a dict
        v = crnt_cond["type"]
        k = crnt_cond["string"]
        assert(v in KeyType.values())
        idx = []

        # if current condition is a named entity type, see if it's pre-computed
        if v == KeyType[NER]:
            try:
                if x[k]:
                    idx.extend([x[k]])
            except (KeyError, TypeError):
                idx.extend(find_indices(crnt_cond, text))
        elif v == KeyType[CONCEPT]:
            # match a concept
            assert k in concepts, "{} has no element {}".format(concepts, k)
            try:
                print(concepts.get_dict())
            except AttributeError:
                pass
            for crnt_token in concepts[k]:
                idx.extend(find_indices(crnt_token, text))
        else:
            idx.extend(find_indices(crnt_cond, text))

        matched_idxes.append(idx)

        if (conn == ConnectiveType[AND]) and (len(idx)==0):
            return -1


    if not direction:
        if conn == ConnectiveType[OR]:
            # no direction, OR
            if any(len(m) > 0 for m in matched_idxes):
                return label
        else:
            # no direction, AND
            if all(len(m) > 0 for m in matched_idxes):
                if conn == ConnectiveType[AND]:
                    if conn == ConnectiveType[AND]:
                        doc = nlp(text)
                        if (len(list(doc.sents))==1):
                            return label
                        for sent in doc.sents:
                            if to_lf(sent, instance, concepts):
                                return label
                    else:
                        return label
    else:
        assert len(matched_idxes) == 2
        if all(len(m) > 0 for m in matched_idxes):
            min_idx = matched_idxes[0][0][0]
            max_idx = matched_idxes[1][-1][0]

            if min_idx < max_idx:
                if conn == ConnectiveType[AND]:
                    if context == ContextType[SENTENCE]:
                        doc = nlp(text)
                        if (len(list(doc.sents))==1):
                            return label
                        for sent in doc.sents:
                            if to_lf(sent, instance, concepts):
                                return label   
                    else:
                        return label 
    return -1

