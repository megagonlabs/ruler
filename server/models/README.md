# Models
This is where all your saved models are stored. There are several files that describe a model:

### concept_collection.json
All of the concepts created in conjunction with this model, stored as json.

### custom_functions.py
__Directly edit this file with your custom python functions.__

Write your functions in this file, along with any necessary imports, and next you load the model those functions will be visible in the UI for you to debug (see false positives, conflicts, etc.)
Make sure you have all necessary dependencies for your functions available.

### label_model.pkl
The serialized label_model

### labels.json
Definitions of the label classes for your model/task.
For example: 

`{"name": "spam", "dict": {"ABSTAIN": -1, "labels": {"non spam": 0, "spam": 1}}, "count": 1}`

### LF_DB.json
The functions created with Ruler, in JSON format.
