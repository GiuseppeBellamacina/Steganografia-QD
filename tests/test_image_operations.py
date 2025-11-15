"""Test per il modulo image_operations"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
from PIL import Image

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia.core import get_image, hide_image


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

    def test_hide_with_custom_parameters(self):
        """Test nascondere immagine con parametri personalizzati"""
        host_img = Image.new("RGB", (200, 200), color="green")
        secret_img = Image.new("RGB", (50, 50), color="yellow")

        # Nascondi con parametri custom (div=0 per calcolo automatico)
        result_img, lsb, msb, div, w, h = hide_image(host_img, secret_img, lsb=2, msb=6)

        assert result_img is not None
        assert lsb == 2
        assert msb == 6
        assert div > 0  # div calcolato automaticamente
        assert w == 50 and h == 50

    def test_hide_and_recover_with_backup_file(self):
        """Test nascondere e recuperare immagine con file di backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            host_img = Image.new("RGB", (150, 150), color="purple")
            secret_img = Image.new("RGB", (40, 40), color="orange")

            backup_path = os.path.join(temp_dir, "backup.json")
            output_path = os.path.join(temp_dir, "recovered.png")

            # Nascondi con backup file
            result_img, _, _, _, _, _ = hide_image(
                host_img, secret_img, backup_file=backup_path
            )

            assert os.path.exists(backup_path)

            # Recupera usando backup file
            recovered_img = get_image(result_img, output_path, backup_file=backup_path)

            assert recovered_img is not None
            assert recovered_img.size == (40, 40)
            assert os.path.exists(output_path)

    def test_recover_without_parameters(self):
        """Test recupero immagine senza parametri usando backup automatico"""
        with tempfile.TemporaryDirectory() as temp_dir:
            host_img = Image.new("RGB", (150, 150), color="cyan")
            secret_img = Image.new("RGB", (30, 30), color="magenta")
            output_path = os.path.join(temp_dir, "recovered.png")

            # Nascondi (salva parametri nel backup automatico)
            result_img, _, _, _, _, _ = hide_image(host_img, secret_img)

            # Recupera senza parametri (usa backup automatico)
            recovered_img = get_image(result_img, output_path)

            assert recovered_img is not None
            assert recovered_img.size == (30, 30)

    def test_grayscale_image_conversion(self):
        """Test conversione automatica di immagini in scala di grigi"""
        host_gray = Image.new("L", (100, 100), color=128)
        secret_gray = Image.new("L", (30, 30), color=200)

        # Nascondi (dovrebbe convertire a RGB automaticamente)
        result_img, _, _, _, _, _ = hide_image(host_gray, secret_gray)

        assert result_img is not None
        assert result_img.mode == "RGB"

    def test_hide_rgba_images(self):
        """Test nascondere immagini RGBA"""
        host_img = Image.new("RGBA", (120, 120), color=(255, 0, 0, 255))
        secret_img = Image.new("RGBA", (30, 30), color=(0, 0, 255, 255))

        # Nascondi (dovrebbe convertire a RGB)
        result_img, _, _, _, _, _ = hide_image(host_img, secret_img)

        assert result_img is not None
        assert result_img.mode == "RGB"

    def test_automatic_lsb_calculation(self):
        """Test calcolo automatico di lsb"""
        host_img = Image.new("RGB", (200, 200), color="white")
        secret_img = Image.new("RGB", (50, 50), color="black")

        # Nascondi senza specificare lsb (lsb=0 trigger calcolo automatico)
        result_img, lsb, _, _, _, _ = hide_image(host_img, secret_img, lsb=0)

        assert result_img is not None
        assert lsb > 0  # LSB dovrebbe essere stato calcolato automaticamente
        assert lsb <= 8

    def test_hide_with_different_msb_values(self):
        """Test nascondere con diversi valori di msb"""
        for msb_val in [4, 6, 8]:
            host_img = Image.new("RGB", (150, 150), color="blue")
            secret_img = Image.new("RGB", (30, 30), color="red")

            result_img, _, msb, _, _, _ = hide_image(host_img, secret_img, msb=msb_val)

            assert result_img is not None
            assert msb == msb_val

    def test_recover_missing_params_error(self):
        """Test errore quando parametri mancanti e nessun backup"""
        from steganografia.backup import backup_system

        # Pulisce backup
        backup_system._last_image_params = None

        img = Image.new("RGB", (100, 100), color="gray")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.png")

            # Tenta di recuperare senza parametri e senza backup
            with pytest.raises(ValueError):
                get_image(img, output_path)

    def test_hide_small_secret_image(self):
        """Test nascondere immagine molto piccola"""
        with tempfile.TemporaryDirectory() as temp_dir:
            host_img = Image.new("RGB", (200, 200), color="navy")
            secret_img = Image.new("RGB", (10, 10), color="gold")
            output_path = os.path.join(temp_dir, "recovered.png")

            # Nascondi immagine piccola
            result_img, lsb, msb, div, w, h = hide_image(host_img, secret_img)

            # Recupera
            recovered_img = get_image(result_img, output_path, lsb, msb, div, w, h)

            assert recovered_img is not None
            assert recovered_img.size == (10, 10)
