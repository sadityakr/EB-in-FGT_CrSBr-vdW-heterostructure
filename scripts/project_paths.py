# ---
# description: |
#   Resolves and exports key project directory paths as module-level constants.
#   Deprecated: prefer using PROJECT_ROOT from setup_notebook() in new notebooks.
# entry_point: from scripts.project_paths import BASE_DIR, RESULTS_DIR, FIGURES_DIR
# dependencies: []
# input: |
#   No arguments. Detects project root by checking whether the CWD contains
#   'notebooks' in the path; if so, steps one level up.
# process: |
#   Computes BASE_DIR, then derives subdirectory paths relative to it.
#   create_directories() can be called to ensure all directories exist.
# output: |
#   Module-level path constants: BASE_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
#   FIGURES_DIR, RESULTS_DIR.
# last_updated: 2026-04-12
# ---

import os

# Automatically find the project root (one level up if running from notebooks/)
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), '..')) if 'notebooks' in os.getcwd() else os.getcwd()

# Important subfolders
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

# Create necessary folders if they don't exist
def create_directories():
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, RESULTS_DIR]:
        os.makedirs(directory, exist_ok=True)
