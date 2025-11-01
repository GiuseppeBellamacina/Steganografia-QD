import streamlit as st
import tempfile
import os
from PIL import Image
import io
from typing import Optional
from steganografia import (
    hide_message, get_message,
    hide_image, get_image,
    hide_bin_file, get_bin_file,
    NO_ZIP, FILE, DIR
)

# Configurazione pagina
st.set_page_config(
    page_title="Steganografia App",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Steganografia - Nascondere e Recuperare Dati")
st.markdown("---")

# Sidebar per la navigazione principale
st.sidebar.title("Opzioni")
mode = st.sidebar.selectbox(
    "Cosa vuoi fare?",
    ["Nascondere dati", "Recuperare dati"]
)

data_type = st.sidebar.selectbox(
    "Tipo di dati",
    ["Stringhe", "Immagini", "File binari"]
)