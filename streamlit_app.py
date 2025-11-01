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
    elif data_type == "Immagini":
        st.subheader("🖼️ Nascondere Immagine")
        st.info("💡 L'immagine host deve essere più grande di quella da nascondere")
        
        secret_image = st.file_uploader(
            "Carica l'immagine da nascondere",
            type=['png', 'jpg', 'jpeg'],
            key="secret_image"
        )
        
        if secret_image:
            col1, col2 = st.columns(2)
            with col1:
                st.image(secret_image, caption="Immagine da nascondere", width=400)
            with col2:
                secret_img = Image.open(secret_image)
                st.write(f"**Dimensioni:** {secret_img.width} x {secret_img.height}")
                st.write(f"**Modalità:** {secret_img.mode}")
        
        # Parametri
        st.subheader("⚙️ Parametri")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lsb = st.number_input("LSB (bit da modificare)", min_value=0, max_value=8, value=0, 
                                 help="0 = automatico")
        with col2:
            msb = st.number_input("MSB (bit da nascondere)", min_value=1, max_value=8, value=8)
        with col3:
            div = st.number_input("Divisore", min_value=0.0, value=0.0, 
                                 help="0.0 = automatico")
        
        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input("Nome file output", value="image_with_hidden_image.png", key="img_output")
        with col2:
            save_backup = st.checkbox("Salva parametri su file", key="img_backup_save")
            backup_name = ""
            if save_backup:
                backup_name = st.text_input("Nome file backup", value="image_backup.dat", key="img_backup_name")
        
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
                            result = hide_image(img1, img2, lsb, msb, int(div), backup_file)
                        
                        if result:  # Controllo successo
                            result_img, final_lsb, final_msb, final_div, w, h = result
                            st.success("✅ Immagine nascosta con successo!")
                            
                            st.info(f"📊 Parametri utilizzati: LSB={final_lsb}, MSB={final_msb}, DIV={final_div:.2f}")
                            
                            # Mostra anteprima dell'immagine risultato
                            st.image(result_img, caption="Anteprima immagine con immagine nascosta", width=400)
                            
                            # Converti l'immagine in buffer per il download
                            img_buffer = io.BytesIO()
                            result_img.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            # Download risultato
                            st.download_button(
                                "📥 Scarica immagine con immagine nascosta",
                                img_buffer.getvalue(),
                                file_name=output_name,
                                mime="image/png"
                            )
                            
                            # Rimuovi file temporaneo se esiste
                            if os.path.exists(output_name):
                                os.remove(output_name)
                            
                            # Download backup
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
                            st.error("❌ Errore durante l'occultamento dell'immagine")
                    else:
                        st.error("❌ Errore nel salvare le immagini")
                
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica entrambe le immagini!")
    
    # FILE BINARI
    elif data_type == "File binari":
        st.subheader("📁 Nascondere File Binario")
        st.info("💡 La compressione riduce la dimensione del file da nascondere")
        
        secret_file = st.file_uploader(
            "Carica il file da nascondere",
            key="secret_file"
        )
        
        if secret_file:
            st.write(f"**Nome file:** {secret_file.name}")
            st.write(f"**Dimensione:** {len(secret_file.getvalue())} bytes")
            st.write(f"**Tipo:** {secret_file.type}")
        
        # Parametri
        st.subheader("⚙️ Parametri")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            zip_mode = st.selectbox(
                "Modalità compressione",
                [NO_ZIP, FILE, DIR],
                format_func=lambda x: {NO_ZIP: "Nessuna", FILE: "Comprimi file", DIR: "Comprimi directory"}[x]
            )
        with col2:
            n = st.number_input("N (bit da modificare)", min_value=0, max_value=8, value=0,
                               help="0 = automatico")
        with col3:
            div = st.number_input("Divisore", min_value=0.0, value=0.0, key="bin_div",
                                 help="0.0 = automatico")
        
        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input("Nome file output", value="image_with_file.png", key="bin_output")
        with col2:
            save_backup = st.checkbox("Salva parametri su file", key="bin_backup_save")
            backup_name = ""
            if save_backup:
                backup_name = st.text_input("Nome file backup", value="binary_backup.dat", key="bin_backup_name")
        
        if st.button("🔒 Nascondi File", type="primary"):
            if host_image and secret_file:
                try:
                    # Salva file temporaneamente
                    host_path = save_uploaded_file(host_image)
                    secret_path = save_uploaded_file(secret_file)
                    
                    if host_path and secret_path:
                        img = Image.open(host_path)
                        
                        # Nascondi file
                        backup_file = backup_name if save_backup else None
                        with st.spinner("Nascondendo file..."):
                            result = hide_bin_file(img, secret_path, zip_mode, n, int(div), backup_file)
                        
                        if result:  # Controllo successo
                            result_img, final_n, final_div, size = result
                            st.success("✅ File nascosto con successo!")
                            
                            st.info(f"📊 Parametri utilizzati: N={final_n}, DIV={final_div:.2f}, SIZE={size} bytes")
                            
                            # Mostra anteprima dell'immagine risultato
                            st.image(result_img, caption="Anteprima immagine con file nascosto", width=400)
                            
                            # Converti l'immagine in buffer per il download
                            img_buffer = io.BytesIO()
                            result_img.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            # Download risultato
                            st.download_button(
                                "📥 Scarica immagine con file nascosto",
                                img_buffer.getvalue(),
                                file_name=output_name,
                                mime="image/png"
                            )
                            
                            # Rimuovi file temporaneo se esiste
                            if os.path.exists(output_name):
                                os.remove(output_name)
                            
                            # Download backup
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
                            st.error("❌ Errore durante l'occultamento del file")
                    else:
                        st.error("❌ Errore nel salvare i file")
                        
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine e un file!")

# RECUPERARE DATI
else:  # mode == "Recuperare dati"
    st.header("📤 Recuperare Dati")
    
    # Caricamento immagine con dati nascosti
    st.subheader("🖼️ Immagine con dati nascosti")
    hidden_image = st.file_uploader(
        "Carica l'immagine che contiene i dati nascosti",
        type=['png', 'jpg', 'jpeg'],
        key="hidden_image"
    )
    
    if hidden_image:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(hidden_image, caption="Immagine con dati nascosti", width=400)
        with col2:
            img = Image.open(hidden_image)
            st.write(f"**Dimensioni:** {img.width} x {img.height}")
            st.write(f"**Modalità:** {img.mode}")
    
    st.markdown("---")
    
    # STRINGHE
    if data_type == "Stringhe":
        st.subheader("📝 Recuperare Stringa")
        
        # Per le stringhe non servono parametri particolari
        st.info("💡 Le stringhe non richiedono parametri speciali - il recupero è automatico!")
        
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
                        
                        if message:
                            st.success("✅ Messaggio recuperato!")
                            st.text_area("Messaggio nascosto:", value=message, height=100)
                            
                            # Download come file di testo
                            st.download_button(
                                "📥 Scarica messaggio come file di testo",
                                message.encode('utf-8'),
                                file_name="messaggio_recuperato.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("❌ Nessun messaggio trovato nell'immagine")
                    else:
                        st.error("❌ Errore nel salvare l'immagine")
                
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine!")
    
    # IMMAGINI
    elif data_type == "Immagini":
        st.subheader("🖼️ Recuperare Immagine")
        
        # Opzioni parametri
        backup_file_path, use_recent, manual_params = display_backup_options("image_get", show_manual=True)
        
        # Parametri manuali se richiesti
        lsb = msb = div = width = height = None
        if manual_params:
            st.subheader("⚙️ Parametri Manuali")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                lsb = st.number_input("LSB", min_value=1, max_value=8, value=1, key="manual_lsb")
            with col2:
                msb = st.number_input("MSB", min_value=1, max_value=8, value=8, key="manual_msb")
            with col3:
                div = st.number_input("DIV", min_value=0.1, value=1.0, key="manual_div")
            with col4:
                width = st.number_input("Larghezza", min_value=1, value=100, key="manual_width")
            with col5:
                height = st.number_input("Altezza", min_value=1, value=100, key="manual_height")
        
        output_name = st.text_input("Nome file output", value="recovered_image.png", key="img_recover_output")
        
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
                                img, output_name, lsb, msb, div, width, height, backup_file_path
                            )
                        
                        if recovered_img:
                            st.success("✅ Immagine recuperata!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(recovered_img, caption="Immagine recuperata", width=400)
                            with col2:
                                st.write(f"**Dimensioni:** {recovered_img.width} x {recovered_img.height}")
                                st.write(f"**Modalità:** {recovered_img.mode}")
                            
                            # Converti l'immagine in buffer per il download
                            img_buffer = io.BytesIO()
                            recovered_img.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            # Download
                            st.download_button(
                                "📥 Scarica immagine recuperata",
                                img_buffer.getvalue(),
                                file_name=output_name,
                                mime="image/png"
                            )
                            
                            # Rimuovi file temporaneo se esiste
                            if os.path.exists(output_name):
                                os.remove(output_name)
                        else:
                            st.error("❌ Impossibile recuperare l'immagine")
                    else:
                        st.error("❌ Errore nel salvare l'immagine")
                
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine!")
    
    # FILE BINARI
    elif data_type == "File binari":
        st.subheader("📁 Recuperare File Binario")
        
        # Opzioni parametri
        backup_file_path, use_recent, manual_params = display_backup_options("binary_get", show_manual=True)
        
        # Parametri manuali se richiesti
        zip_mode = n = div = size = None
        if manual_params:
            st.subheader("⚙️ Parametri Manuali")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                zip_mode = st.selectbox(
                    "ZipMode",
                    [NO_ZIP, FILE, DIR],
                    format_func=lambda x: {NO_ZIP: "Nessuna", FILE: "File", DIR: "Directory"}[x],
                    key="manual_zipmode"
                )
            with col2:
                n = st.number_input("N", min_value=1, max_value=8, value=1, key="manual_n")
            with col3:
                div = st.number_input("DIV", min_value=0.1, value=1.0, key="manual_div_bin")
            with col4:
                size = st.number_input("SIZE (bytes)", min_value=1, value=1000, key="manual_size")
        
        output_name = st.text_input("Nome file output", value="recovered_file.bin", key="bin_recover_output")
        
        if st.button("🔓 Recupera File", type="primary"):
            if hidden_image:
                try:
                    # Salva immagine temporaneamente
                    hidden_path = save_uploaded_file(hidden_image)
                    if hidden_path:
                        img = Image.open(hidden_path)
                        
                        # Recupera file
                        with st.spinner("Recuperando file..."):
                            get_bin_file(img, output_name, zip_mode, n, div, size, backup_file_path)
                        
                        if os.path.exists(output_name):
                            st.success("✅ File recuperato!")
                            
                            file_size = os.path.getsize(output_name)
                            st.write(f"**File recuperato:** {output_name}")
                            st.write(f"**Dimensione:** {file_size} bytes")
                            
                            # Download
                            with open(output_name, "rb") as f:
                                st.download_button(
                                    "📥 Scarica file recuperato",
                                    f.read(),
                                    file_name=output_name,
                                    mime="application/octet-stream"
                                )
                            # Rimuovi file temporaneo
                            os.remove(output_name)
                        else:
                            st.error("❌ Impossibile recuperare il file")
                    else:
                        st.error("❌ Errore nel salvare l'immagine")
                
                except Exception as e:
                    st.error(f"❌ Errore: {str(e)}")
            else:
                st.warning("⚠️ Carica un'immagine!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🔒 <strong>Steganografia App</strong> - Nascondere e recuperare dati in modo sicuro</p>
        <p><em>Sviluppato con ❤️ usando Streamlit</em></p>
    </div>
    """,
    unsafe_allow_html=True
)
