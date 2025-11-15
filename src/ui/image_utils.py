"""
Utility per gestire e visualizzare le immagini nell'interfaccia Streamlit
"""

from io import BytesIO

import streamlit as st
from PIL import Image


class ImageDisplay:
    """Gestisce la visualizzazione delle immagini in Streamlit"""

    def show_resized_image(
        self, image_data, title: str, max_width: int = 400, max_height: int = 300
    ):
        """
        Mostra un'immagine ridimensionata per evitare di occupare troppo spazio

        Args:
            image_data: Dati dell'immagine (PIL Image o bytes)
            title: Titolo da mostrare sopra l'immagine
            max_width: Larghezza massima per la visualizzazione
            max_height: Altezza massima per la visualizzazione
        """
        if image_data is None:
            return

        try:
            # Converte in PIL Image se necessario
            if isinstance(image_data, bytes):
                pil_image = Image.open(BytesIO(image_data))
            elif hasattr(image_data, "read"):  # File-like object
                pil_image = Image.open(image_data)
            else:
                pil_image = image_data

            # Ottiene le dimensioni originali
            original_width, original_height = pil_image.size

            # Calcola le dimensioni per il ridimensionamento
            ratio = min(max_width / original_width, max_height / original_height)

            if ratio < 1:  # Solo se l'immagine è più grande dei limiti
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)

                # Crea una copia ridimensionata per la visualizzazione
                display_image = pil_image.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

                st.markdown(f"**{title}**")
                st.image(
                    display_image,
                    caption=f"Dimensioni originali: {original_width}x{original_height}px",
                )
            else:
                st.markdown(f"**{title}**")
                st.image(
                    pil_image,
                    caption=f"Dimensioni: {original_width}x{original_height}px",
                )

        except Exception as e:
            st.error(f"Errore nella visualizzazione dell'immagine: {str(e)}")

    def show_image_comparison(self, original_image, processed_image, max_width: int = 300):
        """
        Mostra due immagini affiancate per confronto

        Args:
            original_image: Immagine originale
            processed_image: Immagine processata
            max_width: Larghezza massima per ogni immagine
        """
        col1, col2 = st.columns(2)

        with col1:
            ImageDisplay.show_resized_image(
                original_image, "🖼️ Immagine Originale", max_width=max_width
            )

        with col2:
            ImageDisplay.show_resized_image(
                processed_image, "🔒 Immagine con Dati Nascosti", max_width=max_width
            )

    def get_image_info(self, image_data) -> dict:
        """
        Restituisce informazioni sull'immagine

        Args:
            image_data: Dati dell'immagine

        Returns:
            dict: Informazioni sull'immagine (dimensioni, formato, modalità)
        """
        try:
            if isinstance(image_data, bytes):
                pil_image = Image.open(BytesIO(image_data))
            elif hasattr(image_data, "read"):
                pil_image = Image.open(image_data)
            else:
                pil_image = image_data

            return {
                "width": pil_image.width,
                "height": pil_image.height,
                "format": pil_image.format,
                "mode": pil_image.mode,
                "size_pixels": pil_image.width * pil_image.height,
            }
        except Exception:
            return {}

    
    def show_image_details(self, image_data, title: str = "Dettagli Immagine"):
        """
        Mostra dettagli tecnici dell'immagine

        Args:
            image_data: Dati dell'immagine
            title: Titolo della sezione
        """
        info = ImageDisplay.get_image_info(image_data)

        if info:
            with st.expander(f"📊 {title}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Larghezza", f"{info['width']} px")
                    st.metric("Altezza", f"{info['height']} px")

                with col2:
                    st.metric("Pixel Totali", f"{info['size_pixels']:,}")
                    st.metric("Formato", info.get("format", "N/A"))
