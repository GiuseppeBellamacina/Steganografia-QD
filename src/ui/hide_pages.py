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

    if st.button("🔒 Nascondi Messaggio", type="primary"):
            if host_image and message:
                try:
                    # Salva immagine temporaneamente
                    host_path = save_uploaded_file(host_image)
                    if host_path:
                        img = Image.open(host_path)

                        # Nascondi messaggio
                        backup_file = backup_name if save_backup else None
                        with st.spinner("Nascondendo messaggio..."):
                            result_img = hide_message(img, message, backup_file)

                        st.success("✅ Messaggio nascosto con successo!")

                        # Mostra anteprima dell'immagine risultato
                        st.image(
                            result_img,
                            caption="Anteprima immagine con messaggio nascosto",
                            width=400,
                        )

                        # Converti l'immagine in buffer per il download
                        img_buffer = io.BytesIO()
                        result_img.save(img_buffer, format="PNG")
                        img_buffer.seek(0)

                        # Download risultato
                        create_download_button(
                            img_buffer.getvalue(),
                            output_name,
                            "image/png",
                            "📥 Scarica immagine con messaggio nascosto",
                        )

                        # Cleanup
                        cleanup_temp_file(output_name)

                        # Download file backup se creato
                        if backup_file and os.path.exists(backup_file):
                            with open(backup_file, "rb") as f:
                                create_download_button(
                                    f.read(),
                                    backup_file,
                                    "application/octet-stream",
                                    "💾 Scarica file backup parametri",
                                )
                            cleanup_temp_file(backup_file)
                    else:
                        st.error("❌ Errore nel salvare l'immagine")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine e inserisci un messaggio!")

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

                            st.info(
                                f"📊 Parametri utilizzati: LSB={final_lsb}, MSB={final_msb}, DIV={final_div:.2f}"
                            )

                            # Mostra anteprima dell'immagine risultato
                            st.image(
                                result_img,
                                caption="Anteprima immagine con immagine nascosta",
                                width=400,
                            )

                            # Converti l'immagine in buffer per il download
                            img_buffer = io.BytesIO()
                            result_img.save(img_buffer, format="PNG")
                            img_buffer.seek(0)

                            # Download risultato
                            create_download_button(
                                img_buffer.getvalue(),
                                output_name,
                                "image/png",
                                "📥 Scarica immagine con immagine nascosta",
                            )

                            # Cleanup
                            cleanup_temp_file(output_name)

                            # Download backup
                            if backup_file and os.path.exists(backup_file):
                                with open(backup_file, "rb") as f:
                                    create_download_button(
                                        f.read(),
                                        backup_file,
                                        "application/octet-stream",
                                        "💾 Scarica file backup parametri",
                                    )
                                cleanup_temp_file(backup_file)
                        else:
                            st.error("❌ Errore durante l'occultamento dell'immagine")
                    else:
                        st.error("❌ Errore nel salvare le immagini")

                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica entrambe le immagini!")


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