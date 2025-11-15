"""Test per il modulo string_operations"""

import pytest
import sys
from pathlib import Path
from PIL import Image

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia import hide_message, get_message


class TestStringOperations:
    """Test per le operazioni su stringhe"""

    def test_hide_and_recover_message(self):
        """Test nascondere e recuperare messaggio"""
        # Crea immagine di test
        img = Image.new("RGB", (100, 100), color="white")
        message = "Test message for steganography!"

        # Nascondi messaggio
        img_with_message = hide_message(img, message)
        assert img_with_message is not None

        # Recupera messaggio
        recovered = get_message(img_with_message)
        assert recovered == message

    def test_recover_from_empty_image(self):
        """Test recupero da immagine vuota dovrebbe fallire"""
        img = Image.new("RGB", (50, 50), color="white")

        with pytest.raises(ValueError, match="Nessun messaggio valido trovato"):
            get_message(img)

    def test_message_with_special_characters(self):
        """Test con caratteri speciali"""
        img = Image.new("RGB", (100, 100), color="white")
        message = "Ciao! àèéìòù @#$%"

        img_with_message = hide_message(img, message)
        recovered = get_message(img_with_message)
        assert recovered == message
