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
                <p><em>Nascondere è un'arte, rivelare è una scienza</em></p>
                <p><em>Sviluppato con ❤️ usando Streamlit</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )


class DynamicInstructions:
    """Gestisce le istruzioni dinamiche nella sidebar"""

    @staticmethod
    def show_instructions(mode: str, data_type: str):
        """Mostra istruzioni dinamiche basate su modalità e tipo di dati"""
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📖 Istruzioni")

            if mode == "Nascondere dati":
                DynamicInstructions._show_hide_instructions(data_type)
            else:  # Recuperare dati
                DynamicInstructions._show_recover_instructions(data_type)

    @staticmethod
    def clear_instructions():
        """Pulisce le istruzioni dalla sidebar"""
        with st.sidebar:
            st.empty()

    @staticmethod
    def _show_hide_instructions(data_type: str):
        """Istruzioni per nascondere dati"""
        if data_type == "Stringhe":
            st.markdown(
                """
            **Nascondere Stringhe:**
            1. 📤 Carica l'immagine di destinazione
            2. ✍️ Scrivi il messaggio da nascondere
            3. 💾 Opzionalmente salva parametri su file
            4. 🔒 Clicca "Nascondi Messaggio"
            5. 📥 Scarica il risultato
            """
            )
        elif data_type == "Immagini":
            st.markdown(
                """
            **Nascondere Immagini:**
            1. 📤 Carica l'immagine host (più grande)
            2. 🖼️ Carica l'immagine da nascondere
            3. ⚙️ Imposta parametri LSB/MSB/DIV
            4. 💾 Opzionalmente salva parametri
            5. 🔒 Clicca "Nascondi Immagine"
            6. 📥 Scarica il risultato
            """
            )
        else:  # File binari
            st.markdown(
                """
            **Nascondere File:**
            1. 📤 Carica l'immagine di destinazione
            2. 📁 Carica il file da nascondere
            3. ⚙️ Scegli compressione e parametri
            4. 💾 Opzionalmente salva parametri
            5. 🔒 Clicca "Nascondi File"
            6. 📥 Scarica il risultato
            """
            )

    @staticmethod
    def _show_recover_instructions(data_type: str):
        """Istruzioni per recuperare dati"""
        if data_type == "Stringhe":
            st.markdown(
                """
            **Recuperare Stringhe:**
            1. 📤 Carica l'immagine con messaggio
            2. 🔓 Clicca "Recupera Messaggio"
            3. 📖 Leggi il messaggio recuperato
            4. 📥 Scarica come file di testo
            
            💡 **Nessun parametro richiesto!**
            """
            )
        elif data_type == "Immagini":
            st.markdown(
                """
            **Recuperare Immagini:**
            1. 📤 Carica l'immagine con dati nascosti
            2. 🔧 Scegli fonte parametri:
               - 🔄 Automatico (variabili recenti)
               - 📄 File backup (.dat)
               - ✋ Inserimento manuale
            3. 🔓 Clicca "Recupera Immagine"
            4. 📥 Scarica l'immagine recuperata
            """
            )
        else:  # File binari
            st.markdown(
                """
            **Recuperare File:**
            1. 📤 Carica l'immagine con file nascosto
            2. 🔧 Scegli fonte parametri:
               - 🔄 Automatico (variabili recenti)
               - 📄 File backup (.dat)
               - ✋ Inserimento manuale
            3. 🔓 Clicca "Recupera File"
            4. 📥 Scarica il file recuperato
            """
            )
