"""
Layout e istruzioni per l'interfaccia Streamlit
"""

import streamlit as st


class AppLayout:
    """Gestisce il layout dell'applicazione"""

    @staticmethod
    def setup_page():
        """Configura la pagina iniziale"""
        st.set_page_config(
            page_title="Steganografia App", page_icon="🔒", layout="wide"
        )

        st.title("🔒 Steganografia - Nascondere e Recuperare Dati")
        st.markdown("---")

    @staticmethod
    def setup_sidebar():
        """Configura la sidebar e restituisce le scelte dell'utente"""
        st.sidebar.title("Opzioni")
        mode = st.sidebar.selectbox(
            "Cosa vuoi fare?", ["Nascondere dati", "Recuperare dati"]
        )

        data_type = st.sidebar.selectbox(
            "Tipo di dati", ["Stringhe", "Immagini", "File binari"]
        )

        st.sidebar.markdown("---")
        return mode, data_type

    @staticmethod
    def display_host_image_section():
        """Mostra la sezione per caricare l'immagine host"""
        st.subheader("🖼️ Immagine di destinazione")
        host_image = st.file_uploader(
            "Carica l'immagine su cui nascondere i dati",
            type=["png", "jpg", "jpeg"],
            key="host_image",
        )
        return host_image

    @staticmethod
    def display_hidden_image_section():
        """Mostra la sezione per caricare l'immagine con dati nascosti"""
        st.subheader("🖼️ Immagine con dati nascosti")
        hidden_image = st.file_uploader(
            "Carica l'immagine che contiene i dati nascosti",
            type=["png", "jpg", "jpeg"],
            key="hidden_image",
        )
        return hidden_image

    @staticmethod
    def display_footer():
        """Mostra il footer dell'applicazione"""
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center'>
                <p>🔒 <strong>Steganografia App</strong> - Nascondere e recuperare dati in modo sicuro</p>
                <p><em>Sviluppato con ❤️ usando Streamlit</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
