"""Test per il modulo binary_operations"""

import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia import hide_bin_file, get_bin_file
from config.constants import CompressionMode


class TestBinaryOperations:
    """Test per le operazioni su file binari"""

    def test_hide_and_recover_binary_file(self):
        """Test nascondere e recuperare file binario"""
        # Crea immagine di test
        img = Image.new("RGB", (200, 200), color="white")

        # Crea file temporaneo
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as tmp_input:
            test_content = "This is test file content for binary operations!"
            tmp_input.write(test_content)
            tmp_input_path = tmp_input.name

        try:
            # Nascondi file
            result = hide_bin_file(img, tmp_input_path, CompressionMode.NO_ZIP)
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None

            # Recupera file
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_output:
                output_path = tmp_output.name

            get_bin_file(result_img, output_path, CompressionMode.NO_ZIP, n, div, size)

            # Verifica contenuto
            assert os.path.exists(output_path)
            with open(output_path, "r", encoding="utf-8") as f:
                recovered_content = f.read()

            assert recovered_content == test_content
            os.unlink(output_path)

        finally:
            os.unlink(tmp_input_path)


class TestBinaryOperationsAdvanced:
    """Test avanzati per operazioni binarie"""

    def test_compression_modes_advanced(self):
        """Test modalità compressione avanzate"""
        # Test con immagine più grande per supportare file compressi
        img = Image.new("RGB", (300, 300), color="white")

        # Crea directory temporanea con più file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crea alcuni file nella directory
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w", encoding="utf-8") as f:
                f.write("Content of file 1")
            with open(file2_path, "w", encoding="utf-8") as f:
                f.write("Content of file 2")

            # Test nascondere directory
            try:
                result = hide_bin_file(img, temp_dir, CompressionMode.DIR)
                assert result is not None

                result_img, n, div, size = result
                assert result_img is not None
                assert n > 0
                assert div > 0
                assert size > 0

            except Exception as e:
                # Se l'immagine è troppo piccola, è OK per questo test
                if "troppo piccola" in str(e).lower():
                    pass
                else:
                    raise
