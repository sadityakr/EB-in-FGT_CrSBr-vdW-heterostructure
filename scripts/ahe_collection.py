# ---
# description: |
#   Batch-loads all AHE hysteresis files (.h5 or .txt) from a folder into a
#   keyed dictionary and collects scalar attributes (T, HEB, W, AHE, offsets,
#   coercivities) into a pandas DataFrame for downstream analysis.
# entry_point: from scripts.ahe_collection import AHE_Collection
# dependencies:
#   - numpy
#   - pandas
#   - scripts.data_loader (AHE_hysteresis)
# input: |
#   folder_path: directory containing .h5 or .txt measurement files.
#   custom_keys: optional dict mapping filename → label string.
#   plotting: bool, passed through to AHE_hysteresis (default False).
# process: |
#   Iterates over all .h5/.txt files in folder_path, instantiates one
#   AHE_hysteresis per file, and aggregates scalar attributes into arrays
#   and a DataFrame.
# output: |
#   AHE_Collection object with .measurements dict, .attributes DataFrame,
#   and individual arrays (.heb_values, .w_values, .T_values, etc.).
# last_updated: 2026-04-12
# ---

import os
import numpy as np
import pandas as pd
from scripts.data_loader import AHE_hysteresis


class AHE_Collection:
    def __init__(self, folder_path, custom_keys=None, plotting=False):
        self.plotting = plotting
        self.folder_path = folder_path
        self.custom_keys = custom_keys or {}
        self.measurements = self._load_all()
        self.attributes = None
        self.collect_attributes()

    def _load_all(self):
        ahe_loops = {}
        for filename in os.listdir(self.folder_path):
            if filename.endswith(('.txt', '.h5')):
                filepath = os.path.join(self.folder_path, filename)
                temp_obj = AHE_hysteresis(filepath, plotting=self.plotting)
                key = self.custom_keys.get(filename, temp_obj.label)
                temp_obj.label = key
                ahe_loops[key] = temp_obj
        return ahe_loops

    def collect_attributes(self):
        self.labels = []
        self.T_values = []
        self.heb_values = []
        self.offset_values = []
        self.vahe_values = []
        self.w_values = []
        self.c1_values = []
        self.c2_values = []

        for key, obj in self.measurements.items():
            self.labels.append(key)
            self.T_values.append(obj.T)
            self.heb_values.append(obj.heb)
            self.offset_values.append(obj.offset)
            self.vahe_values.append(obj.vahe)
            self.w_values.append(obj.w)
            self.c1_values.append(obj.c1)
            self.c2_values.append(obj.c2)

        self.labels = np.array(self.labels)
        self.T_values = np.array(self.T_values)
        self.heb_values = np.array(self.heb_values)
        self.offset_values = np.array(self.offset_values)
        self.vahe_values = np.array(self.vahe_values)
        self.w_values = np.array(self.w_values)
        self.c1_values = np.array(self.c1_values)
        self.c2_values = np.array(self.c2_values)

        self.attributes = pd.DataFrame({
            "label":  self.labels,
            "T":      self.T_values,
            "HEB":    self.heb_values,
            "offset": self.offset_values,
            "AHE":    self.vahe_values,
            "W":      self.w_values,
            "C1":     self.c1_values,
            "C2":     self.c2_values,
        })
