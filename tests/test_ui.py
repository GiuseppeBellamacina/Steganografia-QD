"""
Test per i moduli UI - components.py, layout.py, image_utils.py
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from PIL import Image

import streamlit as st


# ============================================
# Test per components.py
# ============================================

class TestSaveUploadedFile:
    """Test per la funzione save_uploaded_file"""
    
    def test_save_uploaded_file_success(self):
        """Test salvataggio file caricato con successo"""
        from src.ui.components import save_uploaded_file
        
        # Crea mock di un file caricato
        mock_file = MagicMock()
        mock_file.name = "test_image.png"
        mock_file.getbuffer.return_value = b"fake image data"
        
        with patch('src.ui.components.tempfile.gettempdir', return_value="/tmp"):
            with patch('builtins.open', mock_open()) as mock_file_open:
                result = save_uploaded_file(mock_file)
                
                assert result is not None
                mock_file_open.assert_called_once()
    
    def test_save_uploaded_file_with_suffix(self):
        """Test salvataggio file con suffix"""
        from src.ui.components import save_uploaded_file
        
        mock_file = MagicMock()
        mock_file.name = "image.png"
        mock_file.getbuffer.return_value = b"data"
        
        with patch('src.ui.components.tempfile.gettempdir', return_value="/tmp"):
            with patch('builtins.open', mock_open()):
                result = save_uploaded_file(mock_file, suffix="_backup")
                
                assert "_backup" in result
    
    def test_save_uploaded_file_none(self):
        """Test quando file è None"""
        from src.ui.components import save_uploaded_file
        
        result = save_uploaded_file(None)
        
        assert result is None


class TestDisplayBackupOptions:
    """Test per la funzione display_backup_options"""
    
    @patch('streamlit.subheader')
    @patch('streamlit.radio')
    @patch('streamlit.file_uploader')
    def test_display_backup_options_automatic(self, mock_uploader, mock_radio, mock_subheader):
        """Test opzione automatico"""
        from src.ui.components import display_backup_options
        
        mock_radio.return_value = "Automatico (usa variabili recenti)"
        
        backup_path, use_recent, manual = display_backup_options("test_key")
        
        assert use_recent is True
        assert manual is False
        assert backup_path is None
    
    @patch('streamlit.subheader')
    @patch('streamlit.radio')
    @patch('streamlit.file_uploader')
    def test_display_backup_options_file(self, mock_uploader, mock_radio, mock_subheader):
        """Test opzione file backup"""
        from src.ui.components import display_backup_options
        
        mock_radio.return_value = "File backup (.dat)"
        mock_uploader.return_value = None
        
        backup_path, use_recent, manual = display_backup_options("test_key")
        
        assert use_recent is False
        assert manual is False
        assert backup_path is None
    
    @patch('streamlit.subheader')
    @patch('streamlit.radio')
    def test_display_backup_options_manual(self, mock_radio, mock_subheader):
        """Test opzione inserimento manuale"""
        from src.ui.components import display_backup_options
        
        mock_radio.return_value = "Inserimento manuale"
        
        backup_path, use_recent, manual = display_backup_options("test_key", show_manual=True)
        
        assert use_recent is False
        assert manual is True
        assert backup_path is None


class TestDisplayImageInfo:
    """Test per la funzione display_image_info"""
    
    @patch('streamlit.columns')
    @patch('streamlit.image')
    @patch('streamlit.write')
    def test_display_image_info(self, mock_write, mock_image, mock_columns):
        """Test visualizzazione informazioni immagine"""
        from src.ui.components import display_image_info
        
        # Crea mock columns
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)
        
        mock_uploaded = MagicMock()
        mock_uploaded.type = "image/png"
        
        mock_img = MagicMock()
        mock_img.width = 800
        mock_img.height = 600
        mock_img.mode = "RGB"
        
        display_image_info(mock_uploaded, mock_img, "Test Image")
        
        mock_columns.assert_called_once()


class TestCleanupTempFile:
    """Test per la funzione cleanup_temp_file"""
    
    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    def test_cleanup_temp_file_success(self, mock_remove, mock_exists):
        """Test pulizia file temporaneo con successo"""
        from src.ui.components import cleanup_temp_file
        
        cleanup_temp_file("/tmp/test_file.txt")
        
        mock_remove.assert_called_once_with("/tmp/test_file.txt")
    
    @patch('os.path.exists', return_value=False)
    @patch('os.remove')
    def test_cleanup_temp_file_not_exists(self, mock_remove, mock_exists):
        """Test pulizia quando file non esiste"""
        from src.ui.components import cleanup_temp_file
        
        cleanup_temp_file("/tmp/nonexistent.txt")
        
        mock_remove.assert_not_called()
    
    @patch('os.path.exists', return_value=True)
    @patch('os.remove', side_effect=Exception("Permission denied"))
    def test_cleanup_temp_file_error(self, mock_remove, mock_exists):
        """Test quando c'è errore durante pulizia"""
        from src.ui.components import cleanup_temp_file
        
        # Non deve lanciare eccezione
        cleanup_temp_file("/tmp/test.txt")


class TestCreateDownloadButton:
    """Test per la funzione create_download_button"""
    
    @patch('streamlit.download_button')
    def test_create_download_button(self, mock_button):
        """Test creazione pulsante download"""
        from src.ui.components import create_download_button
        
        data = b"test data"
        create_download_button(data, "test.txt", "text/plain", "Download")
        
        mock_button.assert_called_once()
        call_kwargs = mock_button.call_args[1]
        assert call_kwargs['label'] == "Download"
        assert call_kwargs['file_name'] == "test.txt"


# ============================================
# Test per layout.py
# ============================================

class TestAppLayout:
    """Test per la classe AppLayout"""
    
    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.markdown')
    def test_setup_page(self, mock_markdown, mock_title, mock_set_page):
        """Test configurazione pagina"""
        from src.ui.layout import AppLayout
        
        AppLayout.setup_page()
        
        mock_set_page.assert_called_once()
        mock_title.assert_called_once()
    
    @patch('streamlit.sidebar')
    def test_setup_sidebar(self, mock_sidebar_obj):
        """Test configurazione sidebar"""
        from src.ui.layout import AppLayout
        
        mock_sidebar = MagicMock()
        mock_sidebar.selectbox = MagicMock(side_effect=["Nascondere dati", "Stringhe"])
        
        with patch('streamlit.sidebar', mock_sidebar):
            mode, data_type = AppLayout.setup_sidebar()
            
            assert mode == "Nascondere dati"
            assert data_type == "Stringhe"
    
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    def test_display_host_image_section(self, mock_uploader, mock_subheader):
        """Test sezione immagine host"""
        from src.ui.layout import AppLayout
        
        mock_uploader.return_value = MagicMock()
        
        result = AppLayout.display_host_image_section()
        
        mock_subheader.assert_called_once()
        mock_uploader.assert_called_once()
    
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    def test_display_hidden_image_section(self, mock_uploader, mock_subheader):
        """Test sezione immagine nascosta"""
        from src.ui.layout import AppLayout
        
        mock_uploader.return_value = MagicMock()
        
        result = AppLayout.display_hidden_image_section()
        
        mock_subheader.assert_called_once()
        mock_uploader.assert_called_once()
    
    @patch('streamlit.markdown')
    def test_display_footer(self, mock_markdown):
        """Test visualizzazione footer"""
        from src.ui.layout import AppLayout
        
        AppLayout.display_footer()
        
        assert mock_markdown.call_count >= 2


class TestDynamicInstructions:
    """Test per la classe DynamicInstructions"""
    
    @patch('streamlit.sidebar')
    @patch('streamlit.markdown')
    def test_show_instructions_hide_string(self, mock_markdown, mock_sidebar):
        """Test istruzioni per nascondere stringhe"""
        from src.ui.layout import DynamicInstructions
        
        with patch('streamlit.sidebar', MagicMock()):
            DynamicInstructions.show_instructions("Nascondere dati", "Stringhe")
            
            mock_markdown.assert_called()
    
    @patch('streamlit.sidebar')
    @patch('streamlit.markdown')
    def test_show_instructions_hide_image(self, mock_markdown, mock_sidebar):
        """Test istruzioni per nascondere immagini"""
        from src.ui.layout import DynamicInstructions
        
        with patch('streamlit.sidebar', MagicMock()):
            DynamicInstructions.show_instructions("Nascondere dati", "Immagini")
            
            mock_markdown.assert_called()
    
    @patch('streamlit.sidebar')
    @patch('streamlit.markdown')
    def test_show_instructions_recover_string(self, mock_markdown, mock_sidebar):
        """Test istruzioni per recuperare stringhe"""
        from src.ui.layout import DynamicInstructions
        
        with patch('streamlit.sidebar', MagicMock()):
            DynamicInstructions.show_instructions("Recuperare dati", "Stringhe")
            
            mock_markdown.assert_called()
    
    @patch('streamlit.empty')
    def test_clear_instructions(self, mock_empty):
        """Test pulizia istruzioni"""
        from src.ui.layout import DynamicInstructions
        
        with patch('streamlit.sidebar', MagicMock()):
            DynamicInstructions.clear_instructions()
            
            mock_empty.assert_called()


# ============================================
# Test per image_utils.py
# ============================================

class TestImageDisplay:
    """Test per la classe ImageDisplay"""
    
    def _create_test_image(self):
        """Helper per creare un'immagine di test"""
        img = Image.new('RGB', (800, 600), color='red')
        return img
    
    @patch('streamlit.markdown')
    @patch('streamlit.image')
    @patch('streamlit.error')
    def test_show_resized_image_pil(self, mock_error, mock_image, mock_markdown):
        """Test visualizzazione immagine PIL ridimensionata"""
        from src.ui.image_utils import ImageDisplay
        
        img = self._create_test_image()
        
        ImageDisplay.show_resized_image(img, "Test", max_width=400, max_height=300)
        
        mock_markdown.assert_called()
        mock_image.assert_called()
    
    @patch('streamlit.markdown')
    @patch('streamlit.image')
    @patch('streamlit.error')
    def test_show_resized_image_bytes(self, mock_error, mock_image, mock_markdown):
        """Test visualizzazione immagine da bytes"""
        from src.ui.image_utils import ImageDisplay
        
        img = self._create_test_image()
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        ImageDisplay.show_resized_image(img_bytes.getvalue(), "Test")
        
        mock_markdown.assert_called()
    
    @patch('streamlit.error')
    def test_show_resized_image_error(self, mock_error):
        """Test gestione errore con dati invalidi"""
        from src.ui.image_utils import ImageDisplay
        
        ImageDisplay.show_resized_image(b"invalid data", "Test")
        
        mock_error.assert_called()
    
    @patch('streamlit.columns')
    @patch('src.ui.image_utils.ImageDisplay.show_resized_image')
    def test_show_image_comparison(self, mock_show, mock_columns):
        """Test confronto immagini affiancate"""
        from src.ui.image_utils import ImageDisplay
        
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)
        
        img1 = self._create_test_image()
        img2 = self._create_test_image()
        
        ImageDisplay.show_image_comparison(img1, img2)
        
        mock_columns.assert_called_once()
        assert mock_show.call_count == 2
    
    def test_get_image_info_pil(self):
        """Test ottenimento info immagine PIL"""
        from src.ui.image_utils import ImageDisplay
        
        img = self._create_test_image()
        
        info = ImageDisplay.get_image_info(img)
        
        assert info is not None
        assert 'width' in info or 'size' in info
    
    @patch('src.ui.image_utils.st.expander')
    def test_show_image_details(self, mock_expander):
        """Test visualizzazione dettagli immagine"""
        from src.ui.image_utils import ImageDisplay
        
        mock_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=None)
        
        mock_file = self._create_test_image()
        
        ImageDisplay.show_image_details(mock_file, "Test Details")
        
        mock_expander.assert_called()


# ============================================
# Test per hide_pages.py
# ============================================

class TestHideDataPages:
    """Test per la classe HideDataPages"""
    
    def _create_test_image(self):
        """Helper per creare un'immagine di test"""
        img = Image.new('RGB', (800, 600), color='blue')
        return img
    
    @patch('src.ui.hide_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.text_area')
    @patch('streamlit.text_input')
    @patch('streamlit.button')
    def test_hide_string_page_no_upload(self, mock_button, mock_input, mock_area, mock_uploader, mock_subheader, mock_display):
        """Test pagina nascondere stringa senza upload"""
        from src.ui.hide_pages import HideDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = False
        
        HideDataPages.hide_string_page()
        
        mock_subheader.assert_called()
        mock_button.assert_called()
    
    @patch('src.ui.hide_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.text_area')
    @patch('streamlit.text_input')
    @patch('streamlit.button')
    def test_hide_string_page_with_upload_no_message(self, mock_button, mock_input, mock_area, mock_uploader, mock_subheader, mock_display):
        """Test pagina nascondere stringa con upload ma senza messaggio"""
        from src.ui.hide_pages import HideDataPages
        
        mock_file = MagicMock()
        mock_file.name = "test.png"
        mock_uploader.return_value = mock_file
        mock_area.return_value = ""
        mock_button.return_value = False
        
        HideDataPages.hide_string_page()
        
        mock_subheader.assert_called()
    
    @patch('streamlit.warning')
    @patch('src.ui.hide_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.text_area')
    @patch('streamlit.text_input')
    @patch('streamlit.button')
    def test_hide_string_page_button_no_image(self, mock_button, mock_input, mock_area, mock_uploader, mock_subheader, mock_display, mock_warning):
        """Test pagina nascondere stringa con button ma senza immagine"""
        from src.ui.hide_pages import HideDataPages
        
        mock_uploader.return_value = None
        mock_area.return_value = "test message"
        mock_button.return_value = True
        
        HideDataPages.hide_string_page()
        
        mock_warning.assert_called()
    
    @patch('src.ui.hide_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    def test_hide_image_page_no_upload(self, mock_button, mock_uploader, mock_subheader, mock_display):
        """Test pagina nascondere immagine senza upload"""
        from src.ui.hide_pages import HideDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = False
        
        HideDataPages.hide_image_page()
        
        mock_subheader.assert_called()
    
    @patch('src.ui.hide_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    def test_hide_binary_page_no_upload(self, mock_button, mock_uploader, mock_subheader, mock_display):
        """Test pagina nascondere file binari senza upload"""
        from src.ui.hide_pages import HideDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = False
        
        HideDataPages.hide_binary_page()
        
        mock_subheader.assert_called()


# ============================================
# Test per recover_pages.py
# ============================================

class TestRecoverDataPages:
    """Test per la classe RecoverDataPages"""
    
    @patch('src.ui.recover_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    @patch('streamlit.info')
    def test_recover_string_page_no_upload(self, mock_info, mock_button, mock_uploader, mock_subheader, mock_display):
        """Test pagina recuperare stringa senza upload"""
        from src.ui.recover_pages import RecoverDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = False
        
        RecoverDataPages.recover_string_page()
        
        mock_subheader.assert_called()
        mock_button.assert_called()
    
    @patch('streamlit.warning')
    @patch('src.ui.recover_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    @patch('streamlit.info')
    def test_recover_string_page_button_no_image(self, mock_info, mock_button, mock_uploader, mock_subheader, mock_display, mock_warning):
        """Test pagina recuperare stringa con button ma senza immagine"""
        from src.ui.recover_pages import RecoverDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = True
        
        RecoverDataPages.recover_string_page()
        
        mock_warning.assert_called()
    
    @patch('src.ui.recover_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    def test_recover_image_page_no_upload(self, mock_button, mock_uploader, mock_subheader, mock_display):
        """Test pagina recuperare immagine senza upload"""
        from src.ui.recover_pages import RecoverDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = False
        
        RecoverDataPages.recover_image_page()
        
        mock_subheader.assert_called()
        mock_button.assert_called()
    
    @patch('streamlit.warning')
    @patch('src.ui.recover_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    def test_recover_image_page_button_no_image(self, mock_button, mock_uploader, mock_subheader, mock_display, mock_warning):
        """Test pagina recuperare immagine con button ma senza immagine"""
        from src.ui.recover_pages import RecoverDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = True
        
        RecoverDataPages.recover_image_page()
        
        mock_warning.assert_called()
    
    @patch('src.ui.recover_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    def test_recover_binary_page_no_upload(self, mock_button, mock_uploader, mock_subheader, mock_display):
        """Test pagina recuperare file binari senza upload"""
        from src.ui.recover_pages import RecoverDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = False
        
        RecoverDataPages.recover_binary_page()
        
        mock_subheader.assert_called()
        mock_button.assert_called()
    
    @patch('streamlit.warning')
    @patch('src.ui.recover_pages.ImageDisplay')
    @patch('streamlit.subheader')
    @patch('streamlit.file_uploader')
    @patch('streamlit.button')
    def test_recover_binary_page_button_no_image(self, mock_button, mock_uploader, mock_subheader, mock_display, mock_warning):
        """Test pagina recuperare file con button ma senza immagine"""
        from src.ui.recover_pages import RecoverDataPages
        
        mock_uploader.return_value = None
        mock_button.return_value = True
        
        RecoverDataPages.recover_binary_page()
        
        mock_warning.assert_called()


class TestResultDisplay:
    """Test per la classe ResultDisplay"""
    
    @patch('streamlit.success')
    def test_show_success_message(self, mock_success):
        """Test visualizzazione messaggio di successo"""
        from src.ui.image_utils import ResultDisplay
        
        ResultDisplay.show_success_message("Test success")
        
        mock_success.assert_called_once()
    
    @patch('streamlit.success')
    @patch('streamlit.expander')
    @patch('streamlit.info')
    def test_show_success_message_with_details(self, mock_info, mock_expander, mock_success):
        """Test messaggio di successo con dettagli"""
        from src.ui.image_utils import ResultDisplay
        
        mock_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=None)
        
        ResultDisplay.show_success_message("Test", details="Details")
        
        mock_success.assert_called_once()
        mock_expander.assert_called_once()
    
    @patch('streamlit.error')
    def test_show_error_message(self, mock_error):
        """Test visualizzazione messaggio di errore"""
        from src.ui.image_utils import ResultDisplay
        
        ResultDisplay.show_error_message("Test error")
        
        mock_error.assert_called_once()
    
    @patch('streamlit.error')
    @patch('streamlit.expander')
    @patch('streamlit.write')
    def test_show_error_message_with_suggestions(self, mock_write, mock_expander, mock_error):
        """Test messaggio di errore con suggerimenti"""
        from src.ui.image_utils import ResultDisplay
        
        mock_ctx = MagicMock()
        mock_expander.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_expander.return_value.__exit__ = MagicMock(return_value=None)
        
        ResultDisplay.show_error_message("Error", suggestions=["Suggestion 1", "Suggestion 2"])
        
        mock_error.assert_called_once()
        mock_expander.assert_called_once()
    
    @patch('streamlit.warning')
    def test_show_warning_message(self, mock_warning):
        """Test visualizzazione messaggio di avvertimento"""
        from src.ui.image_utils import ResultDisplay
        
        ResultDisplay.show_warning_message("Test warning")
        
        mock_warning.assert_called_once()
    
    @patch('streamlit.warning')
    @patch('streamlit.caption')
    def test_show_warning_message_with_details(self, mock_caption, mock_warning):
        """Test messaggio di avvertimento con dettagli"""
        from src.ui.image_utils import ResultDisplay
        
        ResultDisplay.show_warning_message("Warning", details="Details")
        
        mock_warning.assert_called_once()
        mock_caption.assert_called_once()
    
    @patch('streamlit.download_button')
    def test_show_download_button(self, mock_download):
        """Test visualizzazione pulsante download"""
        from src.ui.image_utils import ResultDisplay
        
        ResultDisplay.show_download_button(b"data", "file.txt", "text/plain", "Download")
        
        mock_download.assert_called_once()


# ============================================
# Ulteriori test per hide_pages.py e recover_pages.py
# ============================================

def _make_image(path):
    img = Image.new("RGB", (100, 100), color="green")
    img.save(path, format="PNG")
    return img


def test_hide_string_page_success(monkeypatch, tmp_path):
    from src.ui.hide_pages import HideDataPages

    host_path = tmp_path / "host.png"
    _make_image(host_path)

    # Mocks
    monkeypatch.setattr(
        "src.ui.hide_pages.save_uploaded_file", lambda uploaded: str(host_path)
    )

    def fake_hide_message(img, message):
        return Image.open(str(host_path))

    monkeypatch.setattr("src.steganografia.hide_message", fake_hide_message, raising=False)
    monkeypatch.setattr("src.ui.hide_pages.cleanup_temp_file", lambda p: None)
    mock_create = MagicMock()
    monkeypatch.setattr("src.ui.hide_pages.create_download_button", mock_create)

    # Patch streamlit UI inputs
    monkeypatch.setattr("streamlit.file_uploader", lambda *a, **k: MagicMock(name="host", spec=[]))
    monkeypatch.setattr("streamlit.text_area", lambda *a, **k: "secret message")
    monkeypatch.setattr("streamlit.text_input", lambda *a, **k: "out.png")
    monkeypatch.setattr("streamlit.button", lambda *a, **k: True)
    monkeypatch.setattr("streamlit.success", lambda *a, **k: None)

    HideDataPages.hide_string_page()

    assert mock_create.called


def test_hide_image_page_success(monkeypatch, tmp_path):
    from src.ui.hide_pages import HideDataPages

    host_path = tmp_path / "host.png"
    secret_path = tmp_path / "secret.png"
    _make_image(host_path)
    _make_image(secret_path)

    seq = [str(host_path), str(secret_path)]

    def fake_save(uploaded):
        return seq.pop(0)

    monkeypatch.setattr("src.ui.hide_pages.save_uploaded_file", fake_save)

    def fake_hide_image(img1, img2, lsb, msb, div, backup_file):
        return Image.open(str(host_path)), 1, 8, 0.0, None, None

    monkeypatch.setattr("src.steganografia.hide_image", fake_hide_image, raising=False)
    monkeypatch.setattr("src.ui.hide_pages.cleanup_temp_file", lambda p: None)
    mock_create = MagicMock()
    monkeypatch.setattr("src.ui.hide_pages.create_download_button", mock_create)

    # Streamlit inputs
    monkeypatch.setattr("streamlit.file_uploader", lambda *a, **k: MagicMock(name="file", spec=[]))
    monkeypatch.setattr("streamlit.number_input", lambda *a, **k: 1)
    monkeypatch.setattr("streamlit.text_input", lambda *a, **k: "out.png")
    monkeypatch.setattr("streamlit.checkbox", lambda *a, **k: False)
    monkeypatch.setattr("streamlit.button", lambda *a, **k: True)
    monkeypatch.setattr("streamlit.success", lambda *a, **k: None)

    HideDataPages.hide_image_page()

    assert mock_create.called


def test_hide_binary_page_success(monkeypatch, tmp_path):
    from src.ui.hide_pages import HideDataPages

    host_path = tmp_path / "host.png"
    _make_image(host_path)

    tmp_file = tmp_path / "secret.bin"
    tmp_file.write_bytes(b"hello world")

    seq = [str(host_path), str(tmp_file)]

    def fake_save(uploaded):
        return seq.pop(0)

    monkeypatch.setattr("src.ui.hide_pages.save_uploaded_file", fake_save)

    def fake_hide_bin_file(img, secret_path, zip_mode, n, div, backup_file):
        return Image.open(str(host_path)), 1, 0.0, len(b"hello world")

    monkeypatch.setattr("src.steganografia.hide_bin_file", fake_hide_bin_file, raising=False)
    monkeypatch.setattr("src.ui.hide_pages.cleanup_temp_file", lambda p: None)
    mock_create = MagicMock()
    monkeypatch.setattr("src.ui.hide_pages.create_download_button", mock_create)

    # Streamlit: return mocks that have a `name` attribute (host then secret)
    file_mocks = [MagicMock(), MagicMock()]
    file_mocks[0].name = host_path.name
    file_mocks[1].name = tmp_file.name
    monkeypatch.setattr("streamlit.file_uploader", lambda *a, **k: file_mocks.pop(0))
    monkeypatch.setattr("streamlit.selectbox", lambda *a, **k: None)
    monkeypatch.setattr("streamlit.number_input", lambda *a, **k: 1)
    monkeypatch.setattr("streamlit.text_input", lambda *a, **k: "out.png")
    monkeypatch.setattr("streamlit.checkbox", lambda *a, **k: False)
    monkeypatch.setattr("streamlit.button", lambda *a, **k: True)

    HideDataPages.hide_binary_page()

    assert mock_create.called


def test_recover_string_page_success(monkeypatch, tmp_path):
    from src.ui.recover_pages import RecoverDataPages

    host_path = tmp_path / "hidden.png"
    _make_image(host_path)

    monkeypatch.setattr("src.ui.recover_pages.save_uploaded_file", lambda uploaded: str(host_path))
    monkeypatch.setattr("src.steganografia.get_message", lambda img: "hello world", raising=False)
    mock_create = MagicMock()
    monkeypatch.setattr("src.ui.recover_pages.create_download_button", mock_create)

    monkeypatch.setattr("streamlit.file_uploader", lambda *a, **k: MagicMock(name="file", spec=[]))
    monkeypatch.setattr("streamlit.button", lambda *a, **k: True)

    RecoverDataPages.recover_string_page()

    assert mock_create.called


def test_recover_image_page_success(monkeypatch, tmp_path):
    from src.ui.recover_pages import RecoverDataPages

    host_path = tmp_path / "hidden_img.png"
    _make_image(host_path)

    monkeypatch.setattr("src.ui.recover_pages.save_uploaded_file", lambda uploaded: str(host_path))

    def fake_get_image(img, output_name, lsb, msb, div, width, height, backup_file_path):
        return Image.open(str(host_path))

    monkeypatch.setattr("src.steganografia.get_image", fake_get_image, raising=False)
    monkeypatch.setattr("src.ui.recover_pages.display_backup_options", lambda *a, **k: (None, True, False))
    mock_create = MagicMock()
    monkeypatch.setattr("src.ui.recover_pages.create_download_button", mock_create)

    monkeypatch.setattr("streamlit.file_uploader", lambda *a, **k: MagicMock(name="file", spec=[]))
    monkeypatch.setattr("streamlit.button", lambda *a, **k: True)

    RecoverDataPages.recover_image_page()

    assert mock_create.called


def test_recover_binary_page_success(monkeypatch, tmp_path):
    from src.ui.recover_pages import RecoverDataPages

    host_path = tmp_path / "hidden_bin.png"
    _make_image(host_path)

    # fake get_bin_file that writes output file
    def fake_get_bin_file(img, output_name, zip_mode, n, div, size, backup_file_path):
        with open(output_name, "wb") as f:
            f.write(b"recovered-bytes")

    monkeypatch.setattr("src.ui.recover_pages.save_uploaded_file", lambda uploaded: str(host_path))
    monkeypatch.setattr("src.steganografia.get_bin_file", fake_get_bin_file, raising=False)
    mock_create = MagicMock()
    monkeypatch.setattr("src.ui.recover_pages.create_download_button", mock_create)

    monkeypatch.setattr("streamlit.file_uploader", lambda *a, **k: MagicMock(name="file", spec=[]))
    monkeypatch.setattr("streamlit.button", lambda *a, **k: True)

    RecoverDataPages.recover_binary_page()

    assert mock_create.called
