"""Test per il modulo bit_operations"""

import sys
from pathlib import Path

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from steganografia.bit_operations import binary_convert, binary_convert_back


class TestBitOperations:
    """Test per le operazioni sui bit"""

    def test_binary_convert(self):
        """Test conversione stringa -> binario"""
        text = "Hi!"
        binary = binary_convert(text)
        expected = "010010000110100100100001"  # H=72, i=105, !=33
        assert binary == expected

    def test_binary_convert_back(self):
        """Test conversione binario -> stringa"""
        binary = "010010000110100100100001"
        text = binary_convert_back(binary)
        assert text == "Hi!"

    def test_binary_roundtrip(self):
        """Test roundtrip conversione"""
        original = "Test message 123!"
        binary = binary_convert(original)
        converted_back = binary_convert_back(binary)
        assert converted_back == original
