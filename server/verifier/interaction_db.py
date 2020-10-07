from datetime import datetime
import json
import os
import pandas as pd
from verifier.labeling_function import make_lf


class InteractionDBSingleton:
    filename = "interactionDB.json"
    def __init__(self):
        self.db = {}
        self.count = 0

    def add(self, interaction: dict):
        if "index" in interaction:
            index = interaction["index"]
            interaction['time_submitted'] = str(datetime.now())
            self.db[index].update(interaction)
        else:
            index = self.count
            interaction["index"] = index
            interaction['time_first_seen'] = str(datetime.now())
            self.db[index] = interaction
            self.count += 1
        return index

    def update(self, index: int, selected_lf_ids: list):
        self.db[index]["lfs"] = selected_lf_ids

    def get(self, index: int):
        return self.db[index]

    def save(self, dirname):
        with open(os.path.join(dirname, self.filename), "w+") as file:
            json.dump({
                "db": self.db,
                "count": self.count
                }, file, default=str)

    def load(self, dirname):
        with open(os.path.join(dirname, self.filename), "r") as file:
            data = json.load(file)
            self.db = data['db']
            self.count = data['count']

interactionDB = InteractionDBSingleton()