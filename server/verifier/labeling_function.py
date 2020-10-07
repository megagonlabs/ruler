import inspect
import marshal
import types

from datetime import datetime
from snorkel.labeling import LabelingFunction as SnorkelLF
from synthesizer.gll import CONDS
from synthesizer.gll import CONNECTIVE
from synthesizer.gll import DIRECTION
from synthesizer.gll import LABEL
from synthesizer.gll import WEIGHT
from verifier.translator import to_lf


def make_lf(instance, concepts):
    """wrapper to return a LabelingFunction object from an explanation dictionary
    
    Args:
        instance (dict): describes the LABEL, DIRECTION, CONNECTIVE, and CONDITIONS of the rule
        concepts (dict): all the defined concepts
 
    Returns:
        LabelingFunction
    """
    try:
        concepts = concepts.get_dict()
    except AttributeError:
        pass
    return LabelingFunction(
        name=lf_to_hash(instance),
        f=to_lf,
        resources=dict(instance=instance, concepts=concepts),
    )

def lf_to_hash(lf_dict):
    """Create a unique string representing an LF
    
    Args:
        lf_dict (dict): A labeling function (LF)
    
    Returns:
        str: unique hash
    """
    def conditions_to_string(cond_list):
        conds = []
        for x in cond_list:
            conds.append("".join([str(val) for val in x.values()]))
        return "-".join(sorted(conds))
    lf_hash = ""
    for key, value in sorted(lf_dict.items()):
        if key == "Conditions":
            lf_hash += conditions_to_string(value)
        else:
            if key in ["Connective", "Direction", "Label", "Context"]:
                lf_hash += "_" + str(value)
    return lf_hash

class LabelingFunction(SnorkelLF):

    """Summary
    
    Attributes:
        active (bool): if the LF is active (If it's inactive we still save it, just don't apply to a dataset)
        as_string (str): if it's a custom function, the string definition of the function.
        GLL_fields (list): names of required fields for a Generalized Labeling Language function
        stats (dict): most recently computed statistics (like coverage, accuracy, conflict)
        time_created (datetime): when it was created
        time_submitted (datetime): when it was submitted to the modeler
        uuid (str): UUID identifier. This should change whenever a change occurs that will affect the function's labeling signature.
            Currently, only updating a concept will do this.
        name (str): Unique name for this function. The name will never change over the lifetime of the function
    """
    
    def __init__(self,  
            name, # a unique name is required
            f,
            as_string=None,
            active = True, 
            stats = {},
            time_created = datetime.now(), 
            **kwargs):
        super().__init__(name=name, f=f, **kwargs)

        # TODO hard coding these is a little hacky
        self.GLL_fields = [CONDS, CONNECTIVE, DIRECTION, LABEL, WEIGHT]

        self.time_created = time_created
        self.active = active
        self.stats = stats
        self.as_string = as_string

        # Set UUID. Unlike name, this changes when the function updates (ex: concept changes) 
        self.uuid = name

    def new_uuid(self):
        self.uuid = self.uuid + "_i"

    def submit(self):
        self.time_submitted = datetime.now()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self, stats):
        self.stats.update(stats)    

    def to_json(self):
        obj = {
            "name": self.name,
            "resources": self._resources, 
            # TODO make sure all resources are json serializable
            "active": self.active,
            "stats": self.stats,
            "time_created": str(self.time_created)
        }        
        return obj

    def has_GLL_repr(self):
        return "instance" in self._resources

    def GLL_repr(self):
        """Get a human-readable representation of this LF.
        If it's Ruler-generated, it has a GLL (Generalized Labeling Language) representation,
        otherwise, there is a field "as_string" showing the function definition as a string.
        """
        rep = {}
        if self.has_GLL_repr():
            rep = self._resources['instance']
        else:
            rep = {field: None for field in self.GLL_fields}

            # See if we can observe the output label(s)
            if "Polarity Train" in self.stats:
                rep[LABEL] = self.stats["Polarity Train"]

            # add string representation of function
            if self.as_string is not None:
                rep["as_string"] = self.as_string
        rep['active'] = self.active
        return rep

    @staticmethod
    def read_json(json_obj):
        name = json_obj.pop('name')
        return LabelingFunction(name=name, f=to_lf, **json_obj)
