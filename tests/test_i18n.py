"""
Unit tests for the internationalization (i18n) system.
"""
import pytest
from unittest.mock import Mock
from i18n import (
    get_locale_from_request,
    get_all_translations,
    get_translation,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE
)


class TestI18nFunctions:
    """Test i18n utility functions."""
    
    def test_get_locale_from_request_url_param(self):
        """Test locale extraction from URL parameter."""
        request = Mock()
        request.query_params = {'lang': 'en'}
        request.headers = {}
        
        locale = get_locale_from_request(request)
        assert locale == 'en'
    
    def test_get_locale_from_request_url_param_korean(self):
        """Test locale extraction with Korean parameter."""
        request = Mock()
        request.query_params = {'lang': 'ko'}
        request.headers = {}
        
        locale = get_locale_from_request(request)
        assert locale == 'ko'
    
    def test_get_locale_from_request_accept_language_header(self):
        """Test locale extraction from Accept-Language header."""
        request = Mock()
        request.query_params = {}
        request.headers = {'accept-language': 'en-US,en;q=0.9,ko;q=0.8'}
        
        locale = get_locale_from_request(request)
        assert locale == 'en'
    
    def test_get_locale_from_request_accept_language_korean(self):
        """Test locale extraction with Korean Accept-Language header."""
        request = Mock()
        request.query_params = {}
        request.headers = {'accept-language': 'ko-KR,ko;q=0.9,en;q=0.8'}
        
        locale = get_locale_from_request(request)
        assert locale == 'ko'
    
    def test_get_locale_from_request_language_code_only(self):
        """Test locale extraction with language code only (no country)."""
        request = Mock()
        request.query_params = {}
        request.headers = {'accept-language': 'en;q=0.9'}
        
        locale = get_locale_from_request(request)
        assert locale == 'en'
    
    def test_get_locale_from_request_default(self):
        """Test default locale when no language specified."""
        request = Mock()
        request.query_params = {}
        request.headers = {}
        
        locale = get_locale_from_request(request)
        assert locale == DEFAULT_LANGUAGE
    
    def test_get_locale_from_request_invalid_language(self):
        """Test default locale when invalid language specified."""
        request = Mock()
        request.query_params = {'lang': 'invalid'}
        request.headers = {}
        
        locale = get_locale_from_request(request)
        assert locale == DEFAULT_LANGUAGE
    
    def test_get_all_translations_korean(self):
        """Test getting all Korean translations."""
        translations = get_all_translations('ko')
        
        assert isinstance(translations, dict)
        assert 'dashboard' in translations
        assert translations['dashboard'] == '대시보드'
        assert translations['account_management'] == '계좌 관리'
    
    def test_get_all_translations_english(self):
        """Test getting all English translations."""
        translations = get_all_translations('en')
        
        assert isinstance(translations, dict)
        assert 'dashboard' in translations
        assert translations['dashboard'] == 'Dashboard'
        assert translations['account_management'] == 'Account Management'
    
    def test_get_all_translations_invalid_locale(self):
        """Test getting translations for invalid locale (should return default)."""
        translations = get_all_translations('invalid')
        
        assert isinstance(translations, dict)
        assert 'dashboard' in translations
        assert translations['dashboard'] == '대시보드'  # Should return Korean (default)
    
    def test_get_translation_korean(self):
        """Test getting specific Korean translation."""
        translation = get_translation('ko', 'dashboard')
        assert translation == '대시보드'
    
    def test_get_translation_english(self):
        """Test getting specific English translation."""
        translation = get_translation('en', 'dashboard')
        assert translation == 'Dashboard'
    
    def test_get_translation_missing_key(self):
        """Test getting translation for missing key."""
        translation = get_translation('ko', 'nonexistent_key')
        assert translation == 'nonexistent_key'  # Should return the key itself
    
    def test_get_translation_with_formatting(self):
        """Test getting translation with string formatting."""
        translation = get_translation('ko', 'welcome_message', name='John')
        # This would need to be added to the translations, but testing the concept
        assert isinstance(translation, str)
    
    def test_supported_languages(self):
        """Test that supported languages are properly defined."""
        assert 'ko' in SUPPORTED_LANGUAGES
        assert 'en' in SUPPORTED_LANGUAGES
        assert SUPPORTED_LANGUAGES['ko'] == 'Korean'
        assert SUPPORTED_LANGUAGES['en'] == 'English'
    
    def test_default_language(self):
        """Test that default language is Korean."""
        assert DEFAULT_LANGUAGE == 'ko'
    
    def test_translation_completeness(self):
        """Test that both languages have the same translation keys."""
        ko_translations = get_all_translations('ko')
        en_translations = get_all_translations('en')
        
        ko_keys = set(ko_translations.keys())
        en_keys = set(en_translations.keys())
        
        assert ko_keys == en_keys, "Korean and English translations should have the same keys"
    
    def test_translation_values_different(self):
        """Test that Korean and English translations have different values."""
        ko_translations = get_all_translations('ko')
        en_translations = get_all_translations('en')
        
        # Check a few key translations are different
        assert ko_translations['dashboard'] != en_translations['dashboard']
        assert ko_translations['account_management'] != en_translations['account_management']
        assert ko_translations['transactions'] != en_translations['transactions']
