"""
Operazioni di steganografia per i file binari
"""

import sys
import os
from typing import Optional, Tuple
from os.path import getsize

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
from PIL import Image
from config.constants import DataType, CompressionMode, ErrorMessages
from .bit_operations import set_last_n_bits, string_to_bytes
from .validator import ParameterValidator
from .backup import backup_system
from .file_utils import compress_file, cleanup_temp_files, find_div


class BinarySteganography:
    """Classe per operazioni di steganografia su file binari"""

    @staticmethod
    def hide_binary_file(
        img: Image.Image,
        file_path: str,
        compression_mode: int = CompressionMode.NO_ZIP,
        n: int = 0,
        div: float = 0,
        backup_file: Optional[str] = None,
    ) -> Tuple[Image.Image, int, float, int]:
        """
        Nasconde un file binario o una cartella in un'immagine

        Args:
            img: Immagine dove nascondere il file
            file_path: Percorso del file da nascondere
            compression_mode: Modalità di compressione
            n: Numero di bit da modificare per pixel
            div: Divisore per la distribuzione
            backup_file: File dove salvare i parametri

        Returns:
            Tupla con (immagine_risultato, n_finale, div_finale, dimensione_file)
        """
        # Validazione parametri
        ParameterValidator.validate_n(n)
        ParameterValidator.validate_compression_mode(compression_mode)

        # Determina canali
        channels = 3
        if img.mode == "RGBA":
            channels = 4
        if img.mode not in ["RGB", "RGBA"]:
            img = img.convert("RGB")

        # Comprimi file se richiesto
        working_file = compress_file(file_path, compression_mode)

        try:
            # Ottieni dimensione file
            total_bytes = getsize(working_file)

            # Calcolo automatico di n se necessario
            if n == 0:
                n = 1
                while (img.width * img.height) * channels * n < total_bytes * 8:
                    n += 1
                    if n > 8:
                        raise ValueError(
                            ErrorMessages.IMAGE_TOO_SMALL_FILE.format(
                                file_size=total_bytes,
                                width=img.width,
                                height=img.height,
                            )
                        )

            # Verifica dimensioni
            ParameterValidator.validate_image_size_for_file(
                img, total_bytes, n, channels
            )

            # Converte immagine in array
            arr = np.array(img).flatten().copy()
            total_pixels_ch = len(arr)

            # Calcola o valida DIV
            if div == 0:
                div = find_div(total_pixels_ch, working_file, n)
            else:
                ParameterValidator.validate_div_for_file(
                    div, total_pixels_ch, total_bytes, n
                )

            # Inizia a nascondere il file
            print("Nascondendo file...")
            rsv = ""
            ind, pos = 0.0, 0

            # Leggi file
            with open(working_file, "rb") as f:
                f.seek(0)
                for _ in range(total_bytes):
                    byte = f.read(1)
                    bits = format(ord(byte), "08b")
                    bits = rsv + bits
                    rsv = ""
                    while len(bits) >= n:
                        tmp = bits[:n]
                        bits = bits[n:]
                        # Setta gli ultimi n bit del pixel
                        arr[pos] = set_last_n_bits(arr[pos], tmp, n)
                        ind += div
                        pos = round(ind)
                    if len(bits) > 0:
                        rsv = bits

            # Gestisci bit rimanenti
            while len(rsv) > 0:
                tmp = rsv[:n]
                rsv = rsv[n:]
                arr[pos] = set_last_n_bits(arr[pos], tmp, n)
                ind += div
                pos = round(ind)

            percentage = format(
                ((total_bytes * 8) / ((img.width * img.height) * channels * n)) * 100,
                ".2f",
            )
            print(
                f"TERMINATO - Percentuale di pixel usati con n={n} e div={div}: {percentage}%"
            )

            # Crea immagine risultato
            result_img = Image.fromarray(arr.reshape(img.height, img.width, channels))

            # Salva i parametri per il recupero
            params = {
                "n": n,
                "div": div,
                "size": total_bytes,
                "zipMode": compression_mode,
                "method": "binary",
                "original_file": file_path,
                "channels": channels,
            }
            backup_system.save_backup_data(DataType.BINARY, params, backup_file)

            return (result_img, n, div, total_bytes)

        finally:
            # Pulizia file temporanei
            if compression_mode != CompressionMode.NO_ZIP:
                cleanup_temp_files()