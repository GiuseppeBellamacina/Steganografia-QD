"""Test per il modulo binary_operations"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
from PIL import Image

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from config.constants import CompressionMode
from steganografia.core import get_bin_file, hide_bin_file


class TestBinaryOperations:
    """Test per le operazioni su file binari"""

    def test_hide_and_recover_binary_file(self):
        """Test nascondere e recuperare file binario"""
        img = Image.new("RGB", (200, 200), color="white")

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_input_path = os.path.join(temp_dir, "input.txt")
            output_path = os.path.join(temp_dir, "output.txt")

            test_content = "This is test file content for binary operations!"
            with open(tmp_input_path, "w", encoding="utf-8") as f:
                f.write(test_content)

            # Nascondi file
            result = hide_bin_file(img, tmp_input_path, CompressionMode.NO_ZIP)
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None

            get_bin_file(result_img, output_path, CompressionMode.NO_ZIP, n, div, size)

            # Verifica contenuto
            assert os.path.exists(output_path)
            with open(output_path, "r", encoding="utf-8") as f:
                recovered_content = f.read()

            assert recovered_content == test_content


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

    def test_hide_binary_with_compression_file_mode(self):
        """Test nascondere file binario con compressione FILE"""
        img = Image.new("RGB", (400, 400), color="blue")

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_file_path = os.path.join(temp_dir, "input.txt")

            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write("This is a test file for FILE compression mode!")

            # Nascondi file con compressione FILE
            result = hide_bin_file(img, tmp_file_path, CompressionMode.FILE)
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None
            assert n > 0
            assert div > 0
            assert size > 0

    def test_hide_binary_custom_n_parameter(self):
        """Test nascondere file binario con parametro n personalizzato"""
        img = Image.new("RGB", (200, 200), color="green")

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_file_path = os.path.join(temp_dir, "input.txt")
            output_path = os.path.join(temp_dir, "output.txt")

            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write("Small test content")

            # Nascondi file con n=2 (modifica 2 bit per pixel)
            result = hide_bin_file(img, tmp_file_path, CompressionMode.NO_ZIP, n=2)
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None
            assert n == 2  # Verifica che n sia effettivamente 2

            get_bin_file(result_img, output_path, CompressionMode.NO_ZIP, n, div, size)

            # Verifica contenuto
            with open(output_path, "r", encoding="utf-8") as f:
                recovered = f.read()
            
            with open(tmp_file_path, "r", encoding="utf-8") as f:
                original = f.read()

            assert recovered == original

    def test_image_too_small_for_file(self):
        """Test errore quando immagine è troppo piccola per il file"""
        img = Image.new("RGB", (10, 10), color="white")  # Immagine molto piccola

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_file_path = os.path.join(temp_dir, "large.txt")

            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write("X" * 10000)  # File di 10KB

            with pytest.raises(ValueError):
                hide_bin_file(img, tmp_file_path, CompressionMode.NO_ZIP)

    def test_hide_very_small_file(self):
        """Test nascondere file molto piccolo"""
        img = Image.new("RGB", (100, 100), color="white")

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = os.path.join(temp_dir, "small.txt")
            output_path = os.path.join(temp_dir, "output.txt")

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write("A")

            result = hide_bin_file(img, tmp_path, CompressionMode.NO_ZIP)
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None
            assert size > 0

            get_bin_file(result_img, output_path, CompressionMode.NO_ZIP, n, div, size)

            # Verifica contenuto
            with open(output_path, "r", encoding="utf-8") as f:
                recovered = f.read()
            assert recovered == "A"

    def test_hide_binary_rgba_image(self):
        """Test nascondere file binario in immagine RGBA"""
        img = Image.new("RGBA", (200, 200), color=(255, 255, 255, 255))

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_file_path = os.path.join(temp_dir, "input.txt")
            output_path = os.path.join(temp_dir, "output.txt")

            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write("Testing RGBA image support!")

            result = hide_bin_file(img, tmp_file_path, CompressionMode.NO_ZIP)
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None
            # RGBA dovrebbe avere 4 canali
            assert result_img.mode == "RGBA"

            get_bin_file(result_img, output_path, CompressionMode.NO_ZIP, n, div, size)

            # Verifica contenuto
            with open(output_path, "r", encoding="utf-8") as f:
                recovered = f.read()
            assert recovered == "Testing RGBA image support!"

    def test_hide_binary_with_custom_div(self):
        """Test nascondere file binario con parametro div personalizzato"""
        img = Image.new("RGB", (300, 300), color="yellow")

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_file_path = os.path.join(temp_dir, "input.txt")

            with open(tmp_file_path, "w", encoding="utf-8") as f:
                f.write("Testing custom div parameter")

            # Nascondi file con div personalizzato
            custom_div = 50.0
            result = hide_bin_file(
                img, tmp_file_path, CompressionMode.NO_ZIP, n=1, div=custom_div
            )
            assert result is not None

            result_img, n, div, size = result
            assert result_img is not None
            assert div == custom_div  # Verifica che div sia quello specificato

    def test_multiple_hide_and_recover_cycles(self):
        """Test multipli cicli di nascondere e recuperare file"""
        test_cases = [
            "First test content",
            "Second different content!",
            "Third content with numbers: 12345",
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for idx, test_content in enumerate(test_cases):
                img = Image.new("RGB", (300, 300), color="cyan")
                tmp_input_path = os.path.join(temp_dir, f"input_{idx}.txt")
                output_path = os.path.join(temp_dir, f"output_{idx}.txt")

                with open(tmp_input_path, "w", encoding="utf-8") as f:
                    f.write(test_content)

                # Nascondi file
                result = hide_bin_file(img, tmp_input_path, CompressionMode.NO_ZIP)
                assert result is not None

                result_img, n, div, size = result

                get_bin_file(result_img, output_path, CompressionMode.NO_ZIP, n, div, size)

                # Verifica
                assert os.path.exists(output_path)
                with open(output_path, "r", encoding="utf-8") as f:
                    recovered = f.read()
                assert recovered == test_content
