"""Test per il modulo image_operations"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia import hide_image, get_image


class TestImageOperations:
    """Test per le operazioni su immagini"""

    def test_hide_and_recover_image(self):
        """Test nascondere e recuperare immagine"""
        # Crea immagini di test
        host_img = Image.new("RGB", (100, 100), color="red")
        secret_img = Image.new("RGB", (50, 50), color="blue")

        # Nascondi immagine
        result = hide_image(host_img, secret_img)
        assert result is not None

        result_img, lsb, msb, div, w, h = result
        assert result_img is not None
        assert w == 50 and h == 50

        # Recupera immagine
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_name = tmp.name

        try:
            recovered_img = get_image(result_img, tmp_name, lsb, msb, div, w, h)
            assert recovered_img is not None
            assert recovered_img.size == (50, 50)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def test_image_too_small_error(self):
        """Test errore quando immagine host è troppo piccola"""
        host_img = Image.new("RGB", (10, 10), color="red")
        secret_img = Image.new("RGB", (50, 50), color="blue")

        with pytest.raises(ValueError):
            hide_image(host_img, secret_img)
