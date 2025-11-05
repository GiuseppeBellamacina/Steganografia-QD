"""
Utilità per operazioni sui file e compressione
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import zipfile
from os import remove, walk
from os.path import getsize, join, relpath, exists
from config.constants import CompressionMode


def find_div(dim: int, file_path: str, n: int) -> float:
    """Calcola il valore di divisione per la distribuzione dei bit"""
    image_dim = dim * n
    div = (image_dim - n) / (getsize(file_path) * 8)
    return div

