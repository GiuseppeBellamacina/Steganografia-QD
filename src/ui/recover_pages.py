"""
Pagine per recuperare dati dall'interfaccia Streamlit
"""

import io
import os
from PIL import Image
import streamlit as st

from config.constants import CompressionMode
from .components import (
    save_uploaded_file,
    display_backup_options,
    cleanup_temp_file,
    create_download_button,
)


class RecoverDataPages:
    """Gestisce le pagine per recuperare dati"""

    @staticmethod
    def recover_string_page():
        """Pagina per recuperare stringhe"""
        from src.steganografia import get_message

        st.subheader("📝 Recuperare Stringa")

        # Upload dell'immagine con dati nascosti
        hidden_image = st.file_uploader(
            "🖼️ Carica l'immagine con messaggio nascosto:",
            type=["png", "jpg", "jpeg"],
            key="recover_string_hidden_image",
        )

        # Mostra anteprima dell'immagine
        if hidden_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                hidden_image, "🔒 Immagine con Messaggio", max_width=400
            )

        # Per le stringhe non servono parametri particolari
        st.info(
            "💡 Le stringhe non richiedono parametri speciali - il recupero è automatico!"
        )

        if st.button("🔓 Recupera Messaggio", type="primary"):
            if hidden_image:
                try:
                    # Salva immagine temporaneamente
                    hidden_path = save_uploaded_file(hidden_image)
                    if hidden_path:
                        img = Image.open(hidden_path)

                        # Recupera messaggio
                        with st.spinner("Recuperando messaggio..."):
                            message = get_message(img)

                        if message and message.strip():
                            st.success("✅ Messaggio recuperato!")

                            # Mostra informazioni sul messaggio
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "Lunghezza messaggio", f"{len(message)} caratteri"
                                )
                            with col2:
                                st.metric(
                                    "Dimensione in byte",
                                    f"{len(message.encode('utf-8'))} byte",
                                )

                            st.text_area(
                                "Messaggio nascosto:", value=message, height=100
                            )

                            # Download come file di testo
                            create_download_button(
                                message.encode("utf-8"),
                                "messaggio_recuperato.txt",
                                "text/plain",
                                "📥 Scarica messaggio come file di testo",
                            )
                        else:
                            st.error("❌ Nessun messaggio valido trovato nell'immagine")
                            st.info("💡 Possibili cause:")
                            st.write("• L'immagine non contiene un messaggio nascosto")
                            st.write("• L'immagine è stata modificata o compressa")
                            st.write("• Il messaggio è corrotto o non leggibile")
                    else:
                        st.error("❌ Errore nel salvare l'immagine")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine!")

    @staticmethod
    def recover_image_page():
        """Pagina per recuperare immagini"""
        from src.steganografia import get_image

        st.subheader("🖼️ Recuperare Immagine")

        # Upload dell'immagine con dati nascosti
        hidden_image = st.file_uploader(
            "🖼️ Carica l'immagine con immagine nascosta:",
            type=["png", "jpg", "jpeg"],
            key="recover_image_hidden_image",
        )

        # Mostra anteprima dell'immagine
        if hidden_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                hidden_image, "🔒 Immagine con Dati Nascosti", max_width=400
            )

        # Opzioni parametri
        backup_file_path, _, manual_params = display_backup_options(
            "image_get", show_manual=True
        )

        # Parametri manuali se richiesti
        lsb = msb = div = width = height = None
        if manual_params:
            st.subheader("⚙️ Parametri Manuali")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                lsb = st.number_input(
                    "LSB", min_value=1, max_value=8, value=1, key="manual_lsb"
                )
            with col2:
                msb = st.number_input(
                    "MSB", min_value=1, max_value=8, value=8, key="manual_msb"
                )
            with col3:
                div = st.number_input("DIV", min_value=0.1, value=1.0, key="manual_div")
            with col4:
                width = st.number_input(
                    "Larghezza", min_value=1, value=100, key="manual_width"
                )
            with col5:
                height = st.number_input(
                    "Altezza", min_value=1, value=100, key="manual_height"
                )

        output_name = st.text_input(
            "Nome file output", value="recovered_image.png", key="img_recover_output"
        )

        if st.button("🔓 Recupera Immagine", type="primary"):
            if hidden_image:
                try:
                    # Salva immagine temporaneamente
                    hidden_path = save_uploaded_file(hidden_image)
                    if hidden_path:
                        img = Image.open(hidden_path)

                        # Recupera immagine
                        with st.spinner("Recuperando immagine..."):
                            recovered_img = get_image(
                                img,
                                output_name,
                                lsb,
                                msb,
                                div,
                                width,
                                height,
                                backup_file_path,
                            )

                        if recovered_img:
                            st.success("✅ Immagine recuperata!")

                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(
                                    recovered_img,
                                    caption="Immagine recuperata",
                                    width=400,
                                )
                            with col2:
                                st.write(
                                    f"**Dimensioni:** {recovered_img.width} x {recovered_img.height}"
                                )
                                st.write(f"**Modalità:** {recovered_img.mode}")

                            # Converti l'immagine in buffer per il download
                            img_buffer = io.BytesIO()
                            recovered_img.save(img_buffer, format="PNG")
                            img_buffer.seek(0)

                            # Download
                            create_download_button(
                                img_buffer.getvalue(),
                                output_name,
                                "image/png",
                                "📥 Scarica immagine recuperata",
                            )

                            # Cleanup
                            cleanup_temp_file(output_name)
                        else:
                            st.error("❌ Impossibile recuperare l'immagine")
                    else:
                        st.error("❌ Errore nel salvare l'immagine")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine!")

    @staticmethod
    def recover_binary_page():
        """Pagina per recuperare file binari"""
        from src.steganografia import get_bin_file

        st.subheader("📁 Recuperare File Binario")

        # Upload dell'immagine con dati nascosti
        hidden_image = st.file_uploader(
            "🖼️ Carica l'immagine con file nascosto:",
            type=["png", "jpg", "jpeg"],
            key="recover_binary_hidden_image",
        )

        # Mostra anteprima dell'immagine
        if hidden_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                hidden_image, "🔒 Immagine con File Nascosto", max_width=400
            )
            ImageDisplay.show_image_details(hidden_image, "Dettagli Immagine")

        # Opzioni parametri
        backup_file_path, _, manual_params = display_backup_options(
            "binary_get", show_manual=True
        )

        # Parametri manuali se richiesti
        zip_mode = n = div = size = None
        if manual_params:
            st.subheader("⚙️ Parametri Manuali")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                zip_mode = st.selectbox(
                    "ZipMode",
                    [CompressionMode.NO_ZIP, CompressionMode.FILE, CompressionMode.DIR],
                    format_func=lambda x: {
                        CompressionMode.NO_ZIP: "Nessuna",
                        CompressionMode.FILE: "File",
                        CompressionMode.DIR: "Directory",
                    }[x],
                    key="manual_zipmode",
                )
            with col2:
                n = st.number_input(
                    "N", min_value=1, max_value=8, value=1, key="manual_n"
                )
            with col3:
                div = st.number_input(
                    "DIV", min_value=0.1, value=1.0, key="manual_div_bin"
                )
            with col4:
                size = st.number_input(
                    "SIZE (bytes)", min_value=1, value=1000, key="manual_size"
                )

        output_name = st.text_input(
            "Nome file output", value="recovered_file.bin", key="bin_recover_output"
        )

        if st.button("🔓 Recupera File", type="primary"):
            if hidden_image:
                try:
                    # Salva immagine temporaneamente
                    hidden_path = save_uploaded_file(hidden_image)
                    if hidden_path:
                        img = Image.open(hidden_path)

                        # Recupera file
                        with st.spinner("Recuperando file..."):
                            get_bin_file(
                                img,
                                output_name,
                                zip_mode,
                                n,
                                div,
                                size,
                                backup_file_path,
                            )

                        if os.path.exists(output_name):
                            st.success("✅ File recuperato!")

                            file_size = os.path.getsize(output_name)
                            st.write(f"**File recuperato:** {output_name}")
                            st.write(f"**Dimensione:** {file_size} bytes")

                            # Download
                            with open(output_name, "rb") as f:
                                create_download_button(
                                    f.read(),
                                    output_name,
                                    "application/octet-stream",
                                    "📥 Scarica file recuperato",
                                )
                            # Cleanup
                            cleanup_temp_file(output_name)
                        else:
                            st.error("❌ Impossibile recuperare il file")
                    else:
                        st.error("❌ Errore nel salvare l'immagine")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine!")
