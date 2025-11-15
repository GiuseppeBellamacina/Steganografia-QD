"""Test per il modulo backup"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from config.constants import DataType
from steganografia.backup import backup_system


class TestBackupSystem:
    """Test per il sistema di backup"""

    def test_backup_operations(self):
        """Test operazioni di backup"""
        # Test salvataggio e caricamento parametri
        params = {"test_param": "test_value", "number": 42}

        # Salva parametri
        backup_system.save_backup_data(DataType.STRING, params)

        # Recupera ultimi parametri
        last_params = backup_system.get_last_params(DataType.STRING)
        assert last_params is not None
        assert last_params["test_param"] == "test_value"
        assert last_params["number"] == 42


class TestAdvancedBackup:
    """Test avanzati per sistema backup"""

    def test_backup_file_operations(self):
        """Test operazioni con file backup"""
        # Crea un file backup temporaneo
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dat", delete=False) as tmp:
            backup_file = tmp.name

        try:
            # Test salvataggio su file
            params = {"lsb": 3, "msb": 6, "div": 2.5, "test_data": "backup_test"}

            backup_system.save_backup_data(DataType.IMAGE, params, backup_file)

            # Test caricamento da file
            loaded_data = backup_system.load_backup_data(backup_file)
            assert loaded_data is not None
            assert loaded_data["type"] == DataType.IMAGE
            assert loaded_data["params"]["lsb"] == 3
            assert loaded_data["params"]["test_data"] == "backup_test"

        finally:
            if os.path.exists(backup_file):
                try:
                    os.unlink(backup_file)
                except OSError:
                    pass

    def test_backup_error_handling(self):
        """Test gestione errori backup"""
        # Test caricamento file inesistente
        result = backup_system.load_backup_data("file_che_non_esiste.dat")
        assert result is None

        # Test caricamento file corrotto - deve generare errore
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dat", delete=False) as tmp:
            tmp.write("dati corrotti non pickle")
            corrupted_file = tmp.name

        try:
            with pytest.raises(ValueError, match="Errore nel caricamento backup"):
                backup_system.load_backup_data(corrupted_file)
        finally:
            if os.path.exists(corrupted_file):
                try:
                    os.unlink(corrupted_file)
                except OSError:
                    pass
