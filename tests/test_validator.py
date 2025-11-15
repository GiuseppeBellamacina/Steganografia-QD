"""Test per il modulo validator"""

import sys
from pathlib import Path

import pytest
from PIL import Image

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia.validator import ParameterValidator


class TestValidator:
    """Test per il sistema di validazione"""

    def test_validate_lsb(self):
        """Test validazione LSB"""
        # Valori validi
        ParameterValidator.validate_lsb(0)  # automatico
        ParameterValidator.validate_lsb(1)
        ParameterValidator.validate_lsb(8)

        # Valori invalidi
        with pytest.raises(ValueError):
            ParameterValidator.validate_lsb(-1)

        with pytest.raises(ValueError):
            ParameterValidator.validate_lsb(9)

    def test_validate_message_size(self):
        """Test validazione dimensione messaggio"""
        img = Image.new("RGB", (10, 10), color="white")

        # Messaggio troppo lungo per immagine piccola
        long_message = "x" * 1000
        with pytest.raises(ValueError):
            ParameterValidator.validate_image_size_for_message(img, long_message)


class TestAdvancedValidation:
    """Test avanzati per validazione e casi edge"""

    def test_div_validations(self):
        """Test validazione divisori"""
        # Test div per immagini
        total_pixels_host = 10000
        total_pixels_secret = 2500
        lsb = 2
        msb = 8

        # DIV valido
        valid_div = (total_pixels_host * lsb) / (total_pixels_secret * msb)
        ParameterValidator.validate_div_for_images(
            valid_div, total_pixels_host, total_pixels_secret, lsb, msb
        )

        # DIV troppo grande dovrebbe fallire
        with pytest.raises(ValueError):
            ParameterValidator.validate_div_for_images(
                valid_div * 10, total_pixels_host, total_pixels_secret, lsb, msb
            )

    def test_div_for_files(self):
        """Test validazione div per file"""
        total_pixels = 30000
        file_size = 1000
        n = 2

        # DIV valido
        valid_div = (total_pixels * n) / (file_size * 8)
        ParameterValidator.validate_div_for_file(valid_div, total_pixels, file_size, n)

        # DIV eccessivo
        with pytest.raises(ValueError):
            ParameterValidator.validate_div_for_file(
                valid_div * 100, total_pixels, file_size, n
            )

    def test_recovery_params_validation(self):
        """Test validazione parametri di recovery"""
        # Tutti parametri validi
        ParameterValidator.validate_recovery_params(1, 8, 2.5, 100, 100)

        # Parametri mancanti critici
        with pytest.raises(ValueError):
            ParameterValidator.validate_recovery_params(None, 8, 2.5, 100, 100)

        with pytest.raises(ValueError):
            ParameterValidator.validate_recovery_params(1, None, 2.5, 100, 100)
