"""
API principale per le operazioni di steganografia
"""

import sys
import os
from typing import Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from PIL import Image
from config.constants import CompressionMode
from .string_operations import StringSteganography
from .image_operations import ImageSteganography
from .binary_operations import BinarySteganography
from .backup import backup_system
from .file_utils import save_image


# Esporta le costanti per compatibilità
NO_ZIP = CompressionMode.NO_ZIP
FILE = CompressionMode.FILE
DIR = CompressionMode.DIR


# API per le stringhe
def hide_message(
    img: Image.Image, message: str, backup_file: Optional[str] = None
) -> Image.Image:
    """Nasconde una stringa in un'immagine"""
    return StringSteganography.hide_message(img, message, backup_file)


def get_message(img: Image.Image, backup_file: Optional[str] = None) -> str:
    """Recupera una stringa da un'immagine"""
    return StringSteganography.get_message(img, backup_file)


# API per le immagini
def hide_image(
    host_img: Image.Image,
    secret_img: Image.Image,
    lsb: int = 0,
    msb: int = 8,
    div: float = 0,
    backup_file: Optional[str] = None,
) -> Tuple[Image.Image, int, int, float, int, int]:
    """Nasconde un'immagine in un'altra"""
    return ImageSteganography.hide_image(
        host_img, secret_img, lsb, msb, div, backup_file
    )


def get_image(
    img: Image.Image,
    output_path: str,
    lsb: Optional[int] = None,
    msb: Optional[int] = None,
    div: Optional[float] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    backup_file: Optional[str] = None,
) -> Image.Image:
    """Recupera un'immagine da un'altra"""
    return ImageSteganography.get_image(
        img, output_path, lsb, msb, div, width, height, backup_file
    )


# API per i file binari
def hide_bin_file(
    img: Image.Image,
    file_path: str,
    compression_mode: int = NO_ZIP,
    n: int = 0,
    div: float = 0,
    backup_file: Optional[str] = None,
) -> Tuple[Image.Image, int, float, int]:
    """Nasconde un file binario in un'immagine"""
    return BinarySteganography.hide_binary_file(
        img, file_path, compression_mode, n, div, backup_file
    )


def get_bin_file(
    img: Image.Image,
    output_path: str,
    compression_mode: Optional[int] = None,
    n: Optional[int] = None,
    div: Optional[float] = None,
    size: Optional[int] = None,
    backup_file: Optional[str] = None,
) -> None:
    """Recupera un file binario da un'immagine"""
    BinarySteganography.get_binary_file(
        img, output_path, compression_mode, n, div, size, backup_file
    )
