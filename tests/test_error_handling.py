"""Test per error handling e edge cases"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia import (
    hide_message,
    get_message,
    hide_image,
    save_image,
    get_last_params,
)
from steganografia.validator import ParameterValidator
from steganografia.bit_operations import set_last_n_bits
from steganografia.backup import backup_system
from config.constants import CompressionMode, DataType


class TestErrorHandling:
    """Test per la gestione degli errori"""

    def test_corrupted_image_data(self):
        """Test con dati immagine corrotti"""
        img = Image.new("RGB", (50, 50), color="white")

        # Modifica alcuni pixel per simulare corruzione
        pixels = img.load()
        if pixels is not None:
            for i in range(10):
                for j in range(10):
                    pixels[i, j] = (255, 255, 255)

        # Dovrebbe generare errore nel recupero
        with pytest.raises(ValueError):
            get_message(img)

    def test_invalid_parameters(self):
        """Test con parametri invalidi"""
        # LSB maggiore di MSB
        with pytest.raises(ValueError):
            ParameterValidator.validate_lsb_msb_relationship(8, 4)

    def test_image_size_validations(self):
        """Test validazioni dimensioni immagine"""
        small_img = Image.new("RGB", (10, 10), color="white")

        # Test immagine troppo piccola per file
        with pytest.raises(ValueError):
            ParameterValidator.validate_image_size_for_file(small_img, 10000, 1, 3)

    def test_core_api_functions(self):
        """Test funzioni API del core"""
        # Test save_image
        img = Image.new("RGB", (50, 50), color="green")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = save_image(img, tmp_path)
            assert result is True

            # Test get_last_params con tipo valido
            get_last_params("string")
            # Può essere None se non ci sono parametri salvati

        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def test_additional_validators(self):
        """Test validatori aggiuntivi"""
        # Test MSB validation
        ParameterValidator.validate_msb(1)
        ParameterValidator.validate_msb(8)

        with pytest.raises(ValueError):
            ParameterValidator.validate_msb(0)

        with pytest.raises(ValueError):
            ParameterValidator.validate_msb(9)

        # Test N validation
        ParameterValidator.validate_n(0)  # 0 è valido (automatico)
        ParameterValidator.validate_n(1)
        ParameterValidator.validate_n(8)

        with pytest.raises(ValueError):
            ParameterValidator.validate_n(-1)

        with pytest.raises(ValueError):
            ParameterValidator.validate_n(9)


class TestEdgeCases:
    """Test per casi limite e edge cases"""

    def test_bit_operations_edge_cases(self):
        """Test casi limite operazioni bit"""
        # Test con n più grande della lunghezza bits
        result = set_last_n_bits(255, "101", 5)
        assert 0 <= result <= 255

        # Test normale
        result = set_last_n_bits(128, "101", 3)
        assert 0 <= result <= 255

    def test_string_operations_edge_cases(self):
        """Test casi limite operazioni stringa"""
        img = Image.new("RGB", (100, 100), color="white")

        # Messaggio molto corto
        short_message = "A"
        img_with_message = hide_message(img, short_message)
        recovered = get_message(img_with_message)
        assert recovered == short_message

        # Test messaggio ASCII normale
        ascii_message = "Hello World!"
        img_with_ascii = hide_message(img, ascii_message)
        recovered_ascii = get_message(img_with_ascii)
        assert recovered_ascii == ascii_message

    def test_automatic_parameter_calculation(self):
        """Test calcolo automatico parametri"""
        # Test LSB automatico con immagini
        host_img = Image.new("RGB", (200, 200), color="red")
        secret_img = Image.new("RGB", (50, 50), color="blue")

        # LSB=0 dovrebbe calcolare automaticamente
        result = hide_image(host_img, secret_img, lsb=0)
        _, final_lsb, _, _, w, h = result

        assert final_lsb > 0  # Dovrebbe aver calcolato un LSB valido
        assert w == 50 and h == 50

    def test_backup_data_types(self):
        """Test backup con diversi tipi di dati"""
        # Test con dati complessi
        complex_params = {
            "integers": [1, 2, 3],
            "floats": [1.5, 2.7],
            "nested": {"inner": {"value": 42}},
            "boolean": True,
        }

        # Salva e recupera
        backup_system.save_backup_data(DataType.BINARY, complex_params)
        recovered = backup_system.get_last_params(DataType.BINARY)

        assert recovered is not None
        assert recovered["integers"] == [1, 2, 3]
        assert recovered["nested"]["inner"]["value"] == 42


class TestCompressionModes:
    """Test per le modalità di compressione"""

    def test_compression_modes(self):
        """Test validazione modalità compressione"""
        # Test modalità valide
        ParameterValidator.validate_compression_mode(CompressionMode.NO_ZIP)
        ParameterValidator.validate_compression_mode(CompressionMode.FILE)
        ParameterValidator.validate_compression_mode(CompressionMode.DIR)

        # Test modalità invalida
        with pytest.raises(ValueError):
            ParameterValidator.validate_compression_mode(-1)
