"""
Applicazione Streamlit principale per la Steganografia
Utilizza l'architettura modulare refactored
"""

import streamlit as st
import sys
from pathlib import Path

# Aggiungi il percorso src al Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import dei moduli refactored
from ui.layout import AppLayout, DynamicInstructions
from ui.hide_pages import HideDataPages
from ui.recover_pages import RecoverDataPages
from ui.image_utils import ResultDisplay

def main():
    """Funzione principale dell'applicazione"""
    try:
        # Setup della pagina
        AppLayout.setup_page()
        
        # Setup della sidebar e ottenimento delle scelte utente
        mode, data_type = AppLayout.setup_sidebar()
        
        # Mostra istruzioni dinamiche
        DynamicInstructions.show_instructions(mode, data_type)
        
        # Routing verso le pagine appropriate
        if mode == "Nascondere dati":
            hide_pages = HideDataPages()
            
            if data_type == "Stringhe":
                hide_pages.hide_string_page()
            elif data_type == "Immagini":
                hide_pages.hide_image_page()
            else:  # File binari
                hide_pages.hide_binary_page()
                
        else:  # Recuperare dati
            recover_pages = RecoverDataPages()
            
            if data_type == "Stringhe":
                recover_pages.recover_string_page()
            elif data_type == "Immagini":
                recover_pages.recover_image_page()
            else:  # File binari
                recover_pages.recover_binary_page()
        
        # Footer
        AppLayout.display_footer()
        
    except Exception as e:
        # Gestione errori globali
        ResultDisplay.show_error_message(
            f"Errore nell'applicazione: {str(e)}",
            [
                "Ricarica la pagina",
                "Verifica che tutti i file siano presenti",
                "Controlla i log per dettagli aggiuntivi"
            ]
        )
        
        # In modalità debug, mostra anche il traceback
        if st.sidebar.checkbox("🐛 Mostra dettagli debug"):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()