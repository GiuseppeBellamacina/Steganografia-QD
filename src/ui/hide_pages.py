"""
Pagine per nascondere dati nell'interfaccia Streamlit
"""

import io
import os

import streamlit as st
from PIL import Image

from config.constants import CompressionMode

from .components import cleanup_temp_file, create_download_button, save_uploaded_file


class HideDataPages:
    """Gestisce le pagine per nascondere dati"""

    @staticmethod
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

        output_name = st.text_input(
            "📁 Nome file output", value="image_with_message.png"
        )

        if st.button("🔒 Nascondi Messaggio", type="primary"):
            if host_image and message:
                # Pulisci risultati precedenti
                if "hide_string_result" in st.session_state:
                    del st.session_state["hide_string_result"]
                try:
                    # Salva immagine temporaneamente
                    host_path = save_uploaded_file(host_image)
                    if host_path:
                        img = Image.open(host_path)

                        # Nascondi messaggio
                        with st.spinner("Nascondendo messaggio..."):
                            result_img = hide_message(img, message)

                        st.success("✅ Messaggio nascosto con successo!")

                        # Salva il risultato per il download
                        img_buffer = io.BytesIO()
                        result_img.save(img_buffer, format="PNG")

                        # Salva in session_state per evitare reload (include anteprima)
                        st.session_state["hide_string_result"] = {
                            "data": img_buffer.getvalue(),
                            "filename": output_name,
                            "preview_image": result_img,  # Mantieni l'anteprima
                        }

                        # Cleanup
                        cleanup_temp_file(output_name)
                    else:
                        st.error("❌ Errore nel salvare l'immagine")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine e inserisci un messaggio!")

        # Sezione download se ci sono risultati
        if "hide_string_result" in st.session_state:
            st.markdown("---")
            st.subheader("📥 Download Risultati")

            result_data = st.session_state["hide_string_result"]

            # Mostra sempre l'anteprima dell'immagine risultato
            if "preview_image" in result_data:
                st.image(
                    result_data["preview_image"],
                    caption="Anteprima immagine con messaggio nascosto",
                    width=400,
                )

            create_download_button(
                result_data["data"],
                result_data["filename"],
                "image/png",
                "📥 Scarica immagine con messaggio nascosto",
            )

    @staticmethod
    def hide_image_page():
        """Pagina per nascondere immagini"""
        from src.steganografia import hide_image

        st.subheader("🖼️ Nascondere Immagine")
        st.info("💡 L'immagine host deve essere più grande di quella da nascondere")

        # Upload dell'immagine host
        host_image = st.file_uploader(
            "🖼️ Carica l'immagine host:",
            type=["png", "jpg", "jpeg"],
            key="hide_image_host_image",
        )

        # Mostra anteprima dell'immagine host
        if host_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                host_image, "🖼️ Immagine Host", max_width=300
            )
            ImageDisplay.show_image_details(host_image, "Dettagli Immagine Host")

        secret_image = st.file_uploader(
            "🔒 Carica l'immagine da nascondere",
            type=["png", "jpg", "jpeg"],
            key="secret_image",
        )

        # Mostra anteprima dell'immagine da nascondere
        if secret_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                secret_image, "🔒 Immagine da Nascondere", max_width=300
            )
            ImageDisplay.show_image_details(
                secret_image, "Dettagli Immagine da Nascondere"
            )

        # Controllo compatibilità dimensioni
        if host_image and secret_image:
            from .image_utils import ImageDisplay

            host_info = ImageDisplay.get_image_info(host_image)
            secret_info = ImageDisplay.get_image_info(secret_image)

            if host_info and secret_info:
                host_pixels = host_info["size_pixels"]
                secret_pixels = secret_info["size_pixels"]

                if host_pixels < secret_pixels:
                    st.error(
                        f"❌ **Incompatibilità dimensioni**: L'immagine host ({host_pixels:,} pixel) è più piccola dell'immagine da nascondere ({secret_pixels:,} pixel)"
                    )
                    st.info(
                        "💡 L'immagine host deve avere almeno la stessa quantità di pixel dell'immagine da nascondere"
                    )
                elif host_pixels < secret_pixels * 2:
                    st.warning(
                        f"⚠️ **Attenzione**: L'immagine host ({host_pixels:,} pixel) è solo {host_pixels/secret_pixels:.1f}x più grande dell'immagine da nascondere ({secret_pixels:,} pixel)"
                    )
                    st.info(
                        "💡 Per migliori risultati, usa un'immagine host almeno 2x più grande"
                    )
                else:
                    st.success(
                        f"✅ **Dimensioni compatibili**: L'immagine host ({host_pixels:,} pixel) è {host_pixels/secret_pixels:.1f}x più grande dell'immagine da nascondere ({secret_pixels:,} pixel)"
                    )

        # Parametri
        st.subheader("⚙️ Parametri")
        col1, col2, col3 = st.columns(3)

        with col1:
            lsb = st.number_input(
                "LSB (bit da modificare)",
                min_value=0,
                max_value=8,
                value=0,
                help="0 = automatico",
            )
        with col2:
            msb = st.number_input(
                "MSB (bit da nascondere)", min_value=1, max_value=8, value=8
            )
        with col3:
            div = st.number_input(
                "Divisore", min_value=0.0, value=0.0, help="0.0 = automatico"
            )

        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input(
                "Nome file output",
                value="image_with_hidden_image.png",
                key="img_output",
            )
        with col2:
            save_backup = st.checkbox("Salva parametri su file", key="img_backup_save")
            backup_name = ""
            if save_backup:
                backup_name = st.text_input(
                    "Nome file backup", value="image_backup.dat", key="img_backup_name"
                )

        if st.button("🔒 Nascondi Immagine", type="primary"):
            if host_image and secret_image:
                # Pulisci risultati precedenti
                if "hide_image_results" in st.session_state:
                    del st.session_state["hide_image_results"]
                try:
                    # Salva immagini temporaneamente
                    host_path = save_uploaded_file(host_image)
                    secret_path = save_uploaded_file(secret_image)

                    if host_path and secret_path:
                        img1 = Image.open(host_path)
                        img2 = Image.open(secret_path)

                        # Nascondi immagine
                        backup_file = backup_name if save_backup else None
                        with st.spinner("Nascondendo immagine..."):
                            result = hide_image(
                                img1, img2, lsb, msb, int(div), backup_file
                            )

                        if result:  # Controllo successo
                            result_img, final_lsb, final_msb, final_div, _, _ = result
                            st.success("✅ Immagine nascosta con successo!")

                            # Salva risultati per il download
                            img_buffer = io.BytesIO()
                            result_img.save(img_buffer, format="PNG")

                            downloads = {
                                "image": {
                                    "data": img_buffer.getvalue(),
                                    "filename": output_name,
                                    "mime": "image/png",
                                    "label": "📥 Scarica immagine con immagine nascosta",
                                },
                                "preview_image": result_img,  # Mantieni anteprima
                                "preview_info": f"📊 Parametri utilizzati: LSB={final_lsb}, MSB={final_msb}, DIV={final_div:.2f}",
                            }

                            # Aggiungi backup se richiesto
                            if backup_file and os.path.exists(backup_file):
                                with open(backup_file, "rb") as f:
                                    downloads["backup"] = {
                                        "data": f.read(),
                                        "filename": backup_file,
                                        "mime": "application/octet-stream",
                                        "label": "💾 Scarica file backup parametri",
                                    }
                                cleanup_temp_file(backup_file)

                            st.session_state["hide_image_results"] = downloads

                            # Cleanup
                            cleanup_temp_file(output_name)
                        else:
                            st.error("❌ Errore durante l'occultamento dell'immagine")
                    else:
                        st.error("❌ Errore nel salvare le immagini")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica entrambe le immagini!")

        # Sezione download se ci sono risultati
        if "hide_image_results" in st.session_state:
            st.markdown("---")
            st.subheader("📥 Download Risultati")

            downloads = st.session_state["hide_image_results"]

            # Mostra sempre l'anteprima e info
            if "preview_image" in downloads:
                if "preview_info" in downloads:
                    st.info(downloads["preview_info"])
                st.image(
                    downloads["preview_image"],
                    caption="Anteprima immagine con immagine nascosta",
                    width=400,
                )

            # Download immagine
            if "image" in downloads:
                img_data = downloads["image"]
                create_download_button(
                    img_data["data"],
                    img_data["filename"],
                    img_data["mime"],
                    img_data["label"],
                )

            # Download backup se presente
            if "backup" in downloads:
                backup_data = downloads["backup"]
                create_download_button(
                    backup_data["data"],
                    backup_data["filename"],
                    backup_data["mime"],
                    backup_data["label"],
                )

    @staticmethod
    def hide_binary_page():
        """Pagina per nascondere file binari"""
        from src.steganografia import hide_bin_file

        st.subheader("📁 Nascondere File Binario")
        st.info("💡 La compressione riduce la dimensione del file da nascondere")

        # Upload dell'immagine host
        host_image = st.file_uploader(
            "🖼️ Carica l'immagine host:",
            type=["png", "jpg", "jpeg"],
            key="hide_binary_host_image",
        )

        # Mostra anteprima dell'immagine host
        if host_image:
            from .image_utils import ImageDisplay

            ImageDisplay.show_resized_image(
                host_image, "🖼️ Immagine Host", max_width=400
            )
            ImageDisplay.show_image_details(host_image, "Dettagli Immagine Host")

        secret_file = st.file_uploader(
            "Carica il file da nascondere", key="secret_file"
        )

        if secret_file:
            st.write(f"**Nome file:** {secret_file.name}")
            st.write(f"**Dimensione:** {len(secret_file.getvalue())} bytes")
            if hasattr(secret_file, "type"):
                st.write(f"**Tipo:** {secret_file.type}")

        # Parametri
        st.subheader("⚙️ Parametri")
        col1, col2, col3 = st.columns(3)

        with col1:
            zip_mode = st.selectbox(
                "Modalità compressione",
                [CompressionMode.NO_ZIP, CompressionMode.FILE, CompressionMode.DIR],
                format_func=lambda x: {
                    CompressionMode.NO_ZIP: "Nessuna",
                    CompressionMode.FILE: "Comprimi file",
                    CompressionMode.DIR: "Comprimi directory",
                }[x],
            )
        with col2:
            n = st.number_input(
                "N (bit da modificare)",
                min_value=0,
                max_value=8,
                value=0,
                help="0 = automatico",
            )
        with col3:
            div = st.number_input(
                "Divisore",
                min_value=0.0,
                value=0.0,
                key="bin_div",
                help="0.0 = automatico",
            )

        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input(
                "Nome file output", value="image_with_file.png", key="bin_output"
            )
        with col2:
            save_backup = st.checkbox("Salva parametri su file", key="bin_backup_save")
            backup_name = ""
            if save_backup:
                backup_name = st.text_input(
                    "Nome file backup", value="binary_backup.dat", key="bin_backup_name"
                )

        if st.button("🔒 Nascondi File", type="primary"):
            if host_image and secret_file:
                # Pulisci risultati precedenti
                if "hide_binary_results" in st.session_state:
                    del st.session_state["hide_binary_results"]
                try:
                    # Salva file temporaneamente
                    host_path = save_uploaded_file(host_image)
                    secret_path = save_uploaded_file(secret_file)

                    if host_path and secret_path:
                        img = Image.open(host_path)

                        # Nascondi file
                        backup_file = backup_name if save_backup else None
                        with st.spinner("Nascondendo file..."):
                            result = hide_bin_file(
                                img, secret_path, zip_mode, n, int(div), backup_file
                            )

                        if result:  # Controllo successo
                            result_img, final_n, final_div, size = result
                            st.success("✅ File nascosto con successo!")

                            # Salva risultati per il download
                            img_buffer = io.BytesIO()
                            result_img.save(img_buffer, format="PNG")

                            downloads = {
                                "image": {
                                    "data": img_buffer.getvalue(),
                                    "filename": output_name,
                                    "mime": "image/png",
                                    "label": "📥 Scarica immagine con file nascosto",
                                },
                                "preview_image": result_img,  # Mantieni anteprima
                                "preview_info": f"📊 Parametri utilizzati: N={final_n}, DIV={final_div:.2f}, SIZE={size} bytes",
                            }

                            # Aggiungi backup se richiesto
                            if backup_file and os.path.exists(backup_file):
                                with open(backup_file, "rb") as f:
                                    downloads["backup"] = {
                                        "data": f.read(),
                                        "filename": backup_file,
                                        "mime": "application/octet-stream",
                                        "label": "💾 Scarica file backup parametri",
                                    }
                                cleanup_temp_file(backup_file)

                            st.session_state["hide_binary_results"] = downloads

                            # Cleanup
                            cleanup_temp_file(output_name)
                        else:
                            st.error("❌ Errore durante l'occultamento del file")
                    else:
                        st.error("❌ Errore nel salvare i file")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine e un file!")

        # Sezione download se ci sono risultati
        if "hide_binary_results" in st.session_state:
            st.markdown("---")
            st.subheader("📥 Download Risultati")

            downloads = st.session_state["hide_binary_results"]

            # Mostra sempre l'anteprima e info
            if "preview_image" in downloads:
                if "preview_info" in downloads:
                    st.info(downloads["preview_info"])
                st.image(
                    downloads["preview_image"],
                    caption="Anteprima immagine con file nascosto",
                    width=400,
                )

            # Download immagine
            if "image" in downloads:
                img_data = downloads["image"]
                create_download_button(
                    img_data["data"],
                    img_data["filename"],
                    img_data["mime"],
                    img_data["label"],
                )

            # Download backup se presente
            if "backup" in downloads:
                backup_data = downloads["backup"]
                create_download_button(
                    backup_data["data"],
                    backup_data["filename"],
                    backup_data["mime"],
                    backup_data["label"],
                )
