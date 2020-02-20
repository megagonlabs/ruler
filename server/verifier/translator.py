"""Summary
"""
import re
from snorkel.labeling import LabelingFunction
from synthesizer.gll import *
from synthesizer.parser import nlp

def raw_stringify(s):
    s = s.lower()
    return "(?:(?<=\W)|(?<=^))({})(?=\W|$)".format(re.escape(s))

def find_indices(k, v, text):
    if v == KeyType[TOKEN]:
        k = raw_stringify(k)
        text = text.lower()
        return [(m.start(), m.end()) for m in re.finditer(k, text)]
    elif v == KeyType[REGEXP]:
        return [(m.start(), m.end()) for m in re.finditer(k, text)]
    elif v == KeyType[NER]:
        with nlp.disable_pipes("tagger", "parser"):
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == k:
                    return [(doc[ent.start-1].idx, doc[ent.end-2].idx + len(doc[ent.end-2].text))]
        return []
    else:
        return []

def to_lf(x, instance, concepts):
    """from one instance (in dict) to one labeling function
    
    Args:
        x (TYPE): Description
        instance (TYPE): Description
        concepts (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    label = instance.get(LABEL)
    direction = bool(instance.get(DIRECTION))
    conn = instance.get(CONNECTIVE)
    conds = instance.get(CONDS)

    matched_idxes = []

    for crnt_cond in conds:
        # crnt_cond is a dict
        k, v = next(iter(crnt_cond.items()))
        idx = []

        # if current condition is a named entity type, see if it's pre-computed
        if v == KeyType[NER]:
            try:
                if x[k]:
                    idx.extend([x[k]])
            except KeyError:
                idx.extend(find_indices(k, v, x.text))
        else:
            idx.extend(find_indices(k, v, x.text))

        if v == KeyType[CONCEPT]:
            # match a concept
            assert k in concepts.keys()
            for crnt_token, crnt_type in concepts[k].items():
                idx.extend(find_indices(crnt_token, crnt_type, x.text))

        matched_idxes.append(idx)

        if not direction:
            if conn == ConnectiveType[OR]:
                # no direction, OR
                if any(len(m) > 0 for m in matched_idxes):
                    return label
            else:
                # no direction, AND
                if all(len(m) > 0 for m in matched_idxes):
                    return label

        else:
            assert conn == ConnectiveType[AND]
            assert len(matched_idxes) == 2
            if all(len(m) > 0 for m in matched_idxes):
                min_idx = matched_idxes[0][0][0]
                max_idx = matched_idxes[1][-1][0]

                if min_idx < max_idx:
                    return label

    return -1


# wrapper to return a LabelingFunction object
def make_lf(instance, concepts):
    """Summary
    
    Args:
        instance (TYPE): Description
        concepts (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    return LabelingFunction(
        name=str(instance["name"]),
        f=to_lf,
        resources=dict(instance=instance, concepts=concepts),
    )
