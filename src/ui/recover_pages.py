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
                # Pulisci risultati precedenti
                if "recover_image_result" in st.session_state:
                    del st.session_state["recover_image_result"]
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

                            # Salva per il download
                            img_buffer = io.BytesIO()
                            recovered_img.save(img_buffer, format="PNG")

                            st.session_state["recover_image_result"] = {
                                "data": img_buffer.getvalue(),
                                "filename": output_name,
                                "preview_image": recovered_img,  # Mantieni anteprima
                                "image_info": {
                                    "width": recovered_img.width,
                                    "height": recovered_img.height,
                                    "mode": recovered_img.mode,
                                },
                            }

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

        # Sezione download se ci sono risultati
        if "recover_image_result" in st.session_state:
            st.markdown("---")
            st.subheader("📥 Download Risultati")

            result_data = st.session_state["recover_image_result"]

            # Mostra sempre l'immagine recuperata
            if "preview_image" in result_data and "image_info" in result_data:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(
                        result_data["preview_image"],
                        caption="Immagine recuperata",
                        width=400,
                    )
                with col2:
                    info = result_data["image_info"]
                    st.write(f"**Dimensioni:** {info['width']} x {info['height']}")
                    st.write(f"**Modalità:** {info['mode']}")

            create_download_button(
                result_data["data"],
                result_data["filename"],
                "image/png",
                "📥 Scarica immagine recuperata",
            )