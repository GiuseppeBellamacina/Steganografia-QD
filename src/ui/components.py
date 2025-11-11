"""
Componenti helper per l'interfaccia Streamlit
"""

import tempfile
import os
from typing import Optional
import streamlit as st


def save_uploaded_file(uploaded_file, suffix: str = "") -> Optional[str]:
    """Salva un file caricato in una posizione temporanea"""
    if uploaded_file is not None:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{uploaded_file.name}{suffix}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None


def display_backup_options(
    data_type_key: str, show_manual: bool = True
) -> tuple[Optional[str], bool, bool]:
    """
    Mostra le opzioni di backup e recupero parametri

    Returns:
        Tuple di (backup_file_path, use_recent, manual_params)
    """
    st.subheader("🔧 Gestione Parametri")

    # Radio button per scelta parametri
    options = ["Automatico (usa variabili recenti)", "File backup (.dat)"]
    if show_manual:
        options.append("Inserimento manuale")

    param_choice = st.radio(
        "Come vuoi recuperare i parametri?",
        options,
        key=f"param_choice_{data_type_key}",
        horizontal=True,
    )

    backup_file_path = None
    use_recent = param_choice == "Automatico (usa variabili recenti)"
    manual_params = param_choice == "Inserimento manuale"

    if param_choice == "File backup (.dat)":
        backup_file = st.file_uploader(
            "Carica file backup (.dat)",
            type=["dat"],
            key=f"backup_upload_{data_type_key}",
        )
        if backup_file:
            backup_file_path = save_uploaded_file(backup_file)

    return backup_file_path, use_recent, manual_params



