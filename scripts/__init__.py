"""
EB-in-FGT/CrSBr analysis scripts.
Modular data loaders and analysis tools for AHE hysteresis measurements.
"""

from .data_loader import AHE_hysteresis
from .ahe_collection import AHE_Collection
from .utils import setup_notebook

__all__ = [
    "AHE_hysteresis",
    "AHE_Collection",
    "setup_notebook",
]

__version__ = "0.1.0"
