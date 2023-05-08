import json
import pandas as pd

class Config:

    def __init__(self, file):
        self.config_as_json = None
        self.load_config(file)

    def load_config(self, file):
        with open(file) as f:
            self.config_as_json = json.load(f)

    def get_config_as_json(self):
        return self.config_as_json

    def get_ontologies(self):
        o_as_list = []
        for o in self.config_as_json:
            o_as_list.append(o["ontology"])
        return o_as_list

