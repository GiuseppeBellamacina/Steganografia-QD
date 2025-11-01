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

st.sidebar.markdown("---")

# Funzioni helper
def save_uploaded_file(uploaded_file, suffix="") -> Optional[str]:
    """Salva un file caricato in una posizione temporanea"""
    if uploaded_file is not None:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{uploaded_file.name}{suffix}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def display_backup_options(data_type_key, show_manual=True):
    """Mostra le opzioni di backup e recupero parametri"""
    st.subheader("🔧 Gestione Parametri")
    
    # Radio button per scelta parametri
    options = ["Automatico (usa variabili recenti)", "File backup (.dat)"]
    if show_manual:
        options.append("Inserimento manuale")
    
    param_choice = st.radio(
        "Come vuoi recuperare i parametri?",
        options,
        key=f"param_choice_{data_type_key}",
        horizontal=True
    )
    
    backup_file_path = None
    use_recent = param_choice == "Automatico (usa variabili recenti)"
    manual_params = param_choice == "Inserimento manuale"
    
    if param_choice == "File backup (.dat)":
        backup_file = st.file_uploader(
            "Carica file backup (.dat)",
            type=['dat'],
            key=f"backup_upload_{data_type_key}"
        )
        if backup_file:
            backup_file_path = save_uploaded_file(backup_file)
    
    return backup_file_path, use_recent, manual_params

# NASCONDERE DATI
if mode == "Nascondere dati":
    st.header("📥 Nascondere Dati")
    
    # Caricamento immagine host
    st.subheader("🖼️ Immagine di destinazione")
    host_image = st.file_uploader(
        "Carica l'immagine su cui nascondere i dati",
        type=['png', 'jpg', 'jpeg'],
        key="host_image"
    )
    
    if host_image:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(host_image, caption="Immagine di destinazione", width=400)
        with col2:
            img = Image.open(host_image)
            st.write(f"**Dimensioni:** {img.width} x {img.height}")
            st.write(f"**Modalità:** {img.mode}")
            st.write(f"**Formato:** {host_image.type}")
    
    st.markdown("---")
    
    # STRINGHE
    if data_type == "Stringhe":
        st.subheader("📝 Nascondere Stringa")
        
        message = st.text_area(
            "Inserisci il messaggio da nascondere:",
            height=100,
            placeholder="Scrivi qui il tuo messaggio segreto..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input("Nome file output", value="image_with_message.png")
        with col2:
            save_backup = st.checkbox("Salva parametri su file")
            backup_name = ""
            if save_backup:
                backup_name = st.text_input("Nome file backup", value="string_backup.dat")
        
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
                        st.image(result_img, caption="Anteprima immagine con messaggio nascosto", width=400)
                        
                        # Converti l'immagine in buffer per il download
                        img_buffer = io.BytesIO()
                        result_img.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        
                        # Download risultato
                        st.download_button(
                            "📥 Scarica immagine con messaggio nascosto",
                            img_buffer.getvalue(),
                            file_name=output_name,
                            mime="image/png"
                        )
                        
                        # Rimuovi file temporaneo se esiste
                        if os.path.exists(output_name):
                            os.remove(output_name)
                        
                        # Download file backup se creato
                        if backup_file and os.path.exists(backup_file):
                            with open(backup_file, "rb") as f:
                                st.download_button(
                                    "💾 Scarica file backup parametri",
                                    f.read(),
                                    file_name=backup_file,
                                    mime="application/octet-stream"
                                )
                            # Rimuovi file temporaneo
                            os.remove(backup_file)
                    else:
                        st.error("❌ Errore nel salvare l'immagine")
                
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine e inserisci un messaggio!")    # IMMAGINI