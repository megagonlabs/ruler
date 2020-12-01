import os

# Names of the directories to store models and datasets
dir_path = os.path.dirname(os.path.realpath(__file__))
MODELS_PATH = os.path.join(dir_path, "models")
DATASETS_PATH = os.path.join(dir_path, "datasets")

# Ruler will preprocess your data (detecting named entities, for example) and store them in a csv file
PROCESSED_FILE_NAME = 'processed.csv'



# CUSTOMIZABLE SETTINGS

# If the size of the labelled data is smaller than MIN_LABELLED_SIZE, a warning will be logged
MIN_LABELLED_SIZE = 20

# To keep response times short, you can cap the number of unlabelled training examples to use when developing your model
DEFAULT_MAX_TRAINING_SIZE = 3000