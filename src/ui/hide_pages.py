"""
Pagine per nascondere dati nell'interfaccia Streamlit
"""

import io
import os
import streamlit as st
from PIL import Image

from config.constants import CompressionMode
from .components import (
    save_uploaded_file,
    cleanup_temp_file,
    create_download_button,
)
  def hide_string_page():
        """Pagina per nascondere stringhe"""
        from src.steganografia import hide_message

        st.subheader("📝 Nascondere Stringa")

        # Upload dell'immagine host
        host_image = st.file_uploader(
            "🖼️ Carica l'immagine host:",
            type=["png", "jpg", "jpeg"],
            key="hide_string_host_image",
        )

        # Mostra anteprima dell'immagine host
        if host_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                host_image, "🖼️ Immagine Host", max_width=400
            )
            ImageDisplay.show_image_details(host_image, "Dettagli Immagine Host")

        message = st.text_area(
            "🔒 Inserisci il messaggio da nascondere:",
            height=100,
            placeholder="Scrivi qui il tuo messaggio segreto...",
        )

        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input(
                "Nome file output", value="image_with_message.png"
            )
        with col2:
            save_backup = st.checkbox("Salva parametri su file")
            backup_name = ""
            if save_backup:
                backup_name = st.text_input(
                    "Nome file backup", value="string_backup.dat"
                )