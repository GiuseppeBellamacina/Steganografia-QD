"""
Test per app.py - Applicazione principale Streamlit
"""

import pytest
from unittest.mock import patch, MagicMock, call
import sys
from pathlib import Path


@pytest.fixture
def mock_streamlit():
    """Fixture per moccare streamlit"""
    with patch('streamlit.set_page_config'), \
         patch('streamlit.title'), \
         patch('streamlit.markdown'), \
         patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.error'), \
         patch('streamlit.code'):
        yield


@pytest.fixture
def mock_modules(mock_streamlit):
    """Fixture per moccare i moduli UI"""
    with patch('app.AppLayout') as mock_layout, \
         patch('app.DynamicInstructions') as mock_instructions, \
         patch('app.HideDataPages') as mock_hide, \
         patch('app.RecoverDataPages') as mock_recover, \
         patch('app.ResultDisplay') as mock_display:
        
        # Setup dei mock objects
        mock_layout.setup_page = MagicMock()
        mock_layout.setup_sidebar = MagicMock(return_value=("Nascondere dati", "Stringhe"))
        mock_layout.display_footer = MagicMock()
        
        mock_instructions.show_instructions = MagicMock()
        
        mock_hide_instance = MagicMock()
        mock_hide.return_value = mock_hide_instance
        
        mock_recover_instance = MagicMock()
        mock_recover.return_value = mock_recover_instance
        
        mock_display.show_error_message = MagicMock()
        
        yield {
            'layout': mock_layout,
            'instructions': mock_instructions,
            'hide': mock_hide,
            'hide_instance': mock_hide_instance,
            'recover': mock_recover,
            'recover_instance': mock_recover_instance,
            'display': mock_display
        }


def test_main_hide_string_mode(mock_modules):
    """Test della main con modalità nascondere stringhe"""
    # Importa dopo i mock
    from app import main
    
    mock_modules['layout'].setup_sidebar.return_value = ("Nascondere dati", "Stringhe")
    
    main()
    
    mock_modules['layout'].setup_page.assert_called_once()
    mock_modules['layout'].setup_sidebar.assert_called_once()
    mock_modules['instructions'].show_instructions.assert_called_once_with("Nascondere dati", "Stringhe")
    mock_modules['hide_instance'].hide_string_page.assert_called_once()
    mock_modules['layout'].display_footer.assert_called_once()


def test_main_hide_image_mode(mock_modules):
    """Test della main con modalità nascondere immagini"""
    from app import main
    
    mock_modules['layout'].setup_sidebar.return_value = ("Nascondere dati", "Immagini")
    
    main()
    
    mock_modules['hide_instance'].hide_image_page.assert_called_once()


def test_main_hide_binary_mode(mock_modules):
    """Test della main con modalità nascondere file binari"""
    from app import main
    
    mock_modules['layout'].setup_sidebar.return_value = ("Nascondere dati", "File binari")
    
    main()
    
    mock_modules['hide_instance'].hide_binary_page.assert_called_once()


def test_main_recover_string_mode(mock_modules):
    """Test della main con modalità recuperare stringhe"""
    from app import main
    
    mock_modules['layout'].setup_sidebar.return_value = ("Recuperare dati", "Stringhe")
    
    main()
    
    mock_modules['recover_instance'].recover_string_page.assert_called_once()


def test_main_recover_image_mode(mock_modules):
    """Test della main con modalità recuperare immagini"""
    from app import main
    
    mock_modules['layout'].setup_sidebar.return_value = ("Recuperare dati", "Immagini")
    
    main()
    
    mock_modules['recover_instance'].recover_image_page.assert_called_once()


def test_main_recover_binary_mode(mock_modules):
    """Test della main con modalità recuperare file binari"""
    from app import main
    
    mock_modules['layout'].setup_sidebar.return_value = ("Recuperare dati", "File binari")
    
    main()
    
    mock_modules['recover_instance'].recover_binary_page.assert_called_once()


def test_main_exception_handling(mock_modules):
    """Test della gestione delle eccezioni nella main"""
    from app import main
    
    # Forza un'eccezione
    mock_modules['layout'].setup_page.side_effect = ValueError("Errore di test")
    
    main()
    
    mock_modules['display'].show_error_message.assert_called_once()
    call_args = mock_modules['display'].show_error_message.call_args
    assert "Errore nell'applicazione" in call_args[0][0]
