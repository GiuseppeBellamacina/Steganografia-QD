"""Test per il modulo file_utils"""

import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia.file_utils import (
    save_image,
    compress_file,
    cleanup_temp_files,
    find_div,
)
from config.constants import CompressionMode


class TestFileUtils:
    """Test per le utility di file"""

    def test_save_image(self):
        """Test salvataggio immagine"""
        img = Image.new("RGB", (50, 50), color="red")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test salvataggio
            result = save_image(img, tmp_path)
            assert result is True
            assert os.path.exists(tmp_path)

            # Verifica che l'immagine sia stata salvata correttamente
            saved_img = Image.open(tmp_path)
            assert saved_img.size == (50, 50)
            saved_img.close()  # Chiudi l'immagine prima di cancellare
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except PermissionError:
                    pass  # Ignora errori di permessi su Windows


class TestFileUtilsAdvanced:
    """Test avanzati per file utils"""

    def test_compression_operations(self):
        """Test operazioni di compressione"""
        # Crea file temporaneo
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write("Test content for compression")
            test_file = tmp.name

        try:
            # Test compressione NO_ZIP (dovrebbe restituire il file originale)
            result = compress_file(test_file, CompressionMode.NO_ZIP)
            assert result == test_file

            # Test compressione FILE
            compressed = compress_file(test_file, CompressionMode.FILE)
            assert compressed != test_file
            assert compressed.endswith(".zip")
            assert os.path.exists(compressed)

            # Test cleanup
            cleanup_temp_files()

        finally:
            # Cleanup manuale
            for file in [test_file]:
                if os.path.exists(file):
                    try:
                        os.unlink(file)
                    except OSError:
                        pass

    def test_find_div_function(self):
        """Test funzione find_div"""
        # Crea un piccolo file test
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("small test content")
            test_file = tmp.name

        try:
            total_pixels = 10000
            n = 2

            div = find_div(total_pixels, test_file, n)
            assert div > 0
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
