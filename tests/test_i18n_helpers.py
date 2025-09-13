"""
Unit tests for i18n helper functions.
"""
import pytest
from unittest.mock import Mock, patch
from i18n_helpers import get_templates_with_i18n


class TestI18nHelpers:
    """Test i18n helper functions."""
    
    @patch('i18n_helpers.get_locale_from_request')
    @patch('i18n_helpers.get_all_translations')
    def test_get_templates_with_i18n_korean(self, mock_get_translations, mock_get_locale):
        """Test getting templates with Korean i18n."""
        # Setup mocks
        mock_get_locale.return_value = 'ko'
        mock_translations = {
            'dashboard': '대시보드',
            'account_management': '계좌 관리'
        }
        mock_get_translations.return_value = mock_translations
        
        # Create mock request
        request = Mock()
        
        # Call function
        templates = get_templates_with_i18n(request)
        
        # Verify mocks were called
        mock_get_locale.assert_called_once_with(request)
        mock_get_translations.assert_called_once_with('ko')
        
        # Verify templates object is created
        assert templates is not None
        assert hasattr(templates, 'TemplateResponse')
    
    @patch('i18n_helpers.get_locale_from_request')
    @patch('i18n_helpers.get_all_translations')
    def test_get_templates_with_i18n_english(self, mock_get_translations, mock_get_locale):
        """Test getting templates with English i18n."""
        # Setup mocks
        mock_get_locale.return_value = 'en'
        mock_translations = {
            'dashboard': 'Dashboard',
            'account_management': 'Account Management'
        }
        mock_get_translations.return_value = mock_translations
        
        # Create mock request
        request = Mock()
        
        # Call function
        templates = get_templates_with_i18n(request)
        
        # Verify mocks were called
        mock_get_locale.assert_called_once_with(request)
        mock_get_translations.assert_called_once_with('en')
        
        # Verify templates object is created
        assert templates is not None
        assert hasattr(templates, 'TemplateResponse')
    
    @patch('i18n_helpers.get_locale_from_request')
    @patch('i18n_helpers.get_all_translations')
    def test_get_templates_with_i18n_translation_functions(self, mock_get_translations, mock_get_locale):
        """Test that translation functions are properly set up in Jinja2 environment."""
        # Setup mocks
        mock_get_locale.return_value = 'ko'
        mock_translations = {
            'dashboard': '대시보드',
            'test_key': '테스트 값'
        }
        mock_get_translations.return_value = mock_translations
        
        # Create mock request
        request = Mock()
        
        # Call function
        templates = get_templates_with_i18n(request)
        
        # Get the Jinja2 environment
        env = templates.env
        
        # Test gettext function
        gettext_func = env.globals['_']
        assert gettext_func('dashboard') == '대시보드'
        assert gettext_func('test_key') == '테스트 값'
        assert gettext_func('nonexistent') == 'nonexistent'  # Should return key if not found
        
        # Test ngettext function
        ngettext_func = env.globals['ngettext']
        assert ngettext_func('item', 'items', 1) == 'item'
        assert ngettext_func('item', 'items', 2) == 'items'
        
        # Test locale and translations globals
        assert env.globals['locale'] == 'ko'
        assert env.globals['translations'] == mock_translations
    
    @patch('i18n_helpers.get_locale_from_request')
    @patch('i18n_helpers.get_all_translations')
    def test_get_templates_with_i18n_jinja2_extensions(self, mock_get_translations, mock_get_locale):
        """Test that Jinja2 environment has i18n extensions loaded."""
        # Setup mocks
        mock_get_locale.return_value = 'ko'
        mock_get_translations.return_value = {}
        
        # Create mock request
        request = Mock()
        
        # Call function
        templates = get_templates_with_i18n(request)
        
        # Get the Jinja2 environment
        env = templates.env
        
        # Check that i18n extension is loaded
        extension_names = [ext.__class__.__name__ for ext in env.extensions.values()]
        assert 'InternationalizationExtension' in extension_names
    
    @patch('i18n_helpers.get_locale_from_request')
    @patch('i18n_helpers.get_all_translations')
    def test_get_templates_with_i18n_template_loader(self, mock_get_translations, mock_get_locale):
        """Test that template loader is properly configured."""
        # Setup mocks
        mock_get_locale.return_value = 'ko'
        mock_get_translations.return_value = {}
        
        # Create mock request
        request = Mock()
        
        # Call function
        templates = get_templates_with_i18n(request)
        
        # Get the Jinja2 environment
        env = templates.env
        
        # Check that FileSystemLoader is used
        assert hasattr(env.loader, 'searchpath')
        assert 'templates' in env.loader.searchpath
    
    def test_get_templates_with_i18n_different_requests(self):
        """Test that different requests return different template instances."""
        with patch('i18n_helpers.get_locale_from_request') as mock_get_locale, \
             patch('i18n_helpers.get_all_translations') as mock_get_translations:
            
            # Setup mocks for first request
            mock_get_locale.return_value = 'ko'
            mock_get_translations.return_value = {'test': '테스트'}
            
            request1 = Mock()
            templates1 = get_templates_with_i18n(request1)
            
            # Setup mocks for second request
            mock_get_locale.return_value = 'en'
            mock_get_translations.return_value = {'test': 'Test'}
            
            request2 = Mock()
            templates2 = get_templates_with_i18n(request2)
            
            # Verify different template instances
            assert templates1 is not templates2
            
            # Verify different translations
            assert templates1.env.globals['translations']['test'] == '테스트'
            assert templates2.env.globals['translations']['test'] == 'Test'
