"""
Sistema di backup e recupero dei parametri di steganografia
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pickle
from os.path import exists
from typing import Optional, Dict, Any
from config.constants import DataType


class ParameterBackup:
    """Gestione del backup e recupero dei parametri"""

    def __init__(self):
        self._last_string_params: Optional[Dict[str, Any]] = None
        self._last_image_params: Optional[Dict[str, Any]] = None
        self._last_binary_params: Optional[Dict[str, Any]] = None

    def save_backup_data(
        self, data_type: str, params: Dict[str, Any], backup_file: Optional[str] = None
    ) -> None:
        """Salva i parametri di occultamento in un file binario e nelle variabili locali"""

        # Salva nelle variabili locali per uso immediato
        if data_type == DataType.STRING:
            self._last_string_params = params
        elif data_type == DataType.IMAGE:
            self._last_image_params = params
        elif data_type == DataType.BINARY:
            self._last_binary_params = params

        # Salva su file se specificato
        if backup_file:
            try:
                with open(backup_file, "wb") as f:
                    backup_data = {"type": data_type, "params": params}
                    pickle.dump(backup_data, f)
                print(f"Parametri salvati in {backup_file}")
            except Exception as e:
                raise ValueError(f"Errore nel salvataggio backup: {e}")

    def load_backup_data(self, backup_file: str) -> Optional[Dict[str, Any]]:
        """Carica i parametri di occultamento da un file binario"""
        try:
            if exists(backup_file):
                with open(backup_file, "rb") as f:
                    backup_data = pickle.load(f)
                print(f"Parametri caricati da {backup_file}")
                return backup_data

            print(f"File backup {backup_file} non trovato")
            return None
        except Exception as e:
            raise ValueError(f"Errore nel caricamento backup: {e}")

    def get_last_params(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Ottiene gli ultimi parametri usati per il tipo di dato specificato"""
        if data_type == DataType.STRING:
            return self._last_string_params
        if data_type == DataType.IMAGE:
            return self._last_image_params
        if data_type == DataType.BINARY:
            return self._last_binary_params
        return None


# Istanza globale del sistema di backup
backup_system = ParameterBackup()
