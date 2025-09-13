"""
Unit tests for router functionality with i18n integration.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app


class TestRouterI18nIntegration:
    """Test that routers properly integrate with i18n system."""
    
    def test_root_endpoint_i18n(self):
        """Test that root endpoint uses i18n templates."""
        with patch('main.get_templates_with_i18n') as mock_get_templates:
            mock_templates = Mock()
            mock_templates.TemplateResponse.return_value = Mock()
            mock_get_templates.return_value = mock_templates
            
            client = TestClient(app)
            response = client.get('/')
            
            # Verify i18n templates were called
            mock_get_templates.assert_called_once()
            mock_templates.TemplateResponse.assert_called_once()
    
    def test_dashboard_endpoint_i18n(self):
        """Test that dashboard endpoint uses i18n templates."""
        with patch('routers.dashboard.get_templates_with_i18n') as mock_get_templates:
            mock_templates = Mock()
            mock_templates.TemplateResponse.return_value = Mock()
            mock_get_templates.return_value = mock_templates
            
            client = TestClient(app)
            response = client.get('/dashboard')
            
            # Verify i18n templates were called
            mock_get_templates.assert_called_once()
            mock_templates.TemplateResponse.assert_called_once()
    
    def test_transactions_endpoint_i18n(self):
        """Test that transactions endpoint uses i18n templates."""
        with patch('routers.transactions.get_templates_with_i18n') as mock_get_templates:
            mock_templates = Mock()
            mock_templates.TemplateResponse.return_value = Mock()
            mock_get_templates.return_value = mock_templates
            
            client = TestClient(app)
            response = client.get('/transactions')
            
            # Verify i18n templates were called
            mock_get_templates.assert_called_once()
            mock_templates.TemplateResponse.assert_called_once()
    
    def test_account_setting_endpoint_i18n(self):
        """Test that account setting endpoint uses i18n templates."""
        with patch('routers.account_setting.get_templates_with_i18n') as mock_get_templates:
            mock_templates = Mock()
            mock_templates.TemplateResponse.return_value = Mock()
            mock_get_templates.return_value = mock_templates
            
            client = TestClient(app)
            response = client.get('/account_setting')
            
            # Verify i18n templates were called
            mock_get_templates.assert_called_once()
            mock_templates.TemplateResponse.assert_called_once()
    
    def test_account_dashboard_endpoint_i18n(self):
        """Test that account dashboard endpoint uses i18n templates."""
        with patch('routers.account_dashboard.get_templates_with_i18n') as mock_get_templates:
            mock_templates = Mock()
            mock_templates.TemplateResponse.return_value = Mock()
            mock_get_templates.return_value = mock_templates
            
            client = TestClient(app)
            response = client.get('/account_dashboard')
            
            # Verify i18n templates were called
            mock_get_templates.assert_called_once()
            mock_templates.TemplateResponse.assert_called_once()


class TestLanguageSwitchingEndpoints:
    """Test language switching endpoint functionality."""
    
    def test_language_switch_korean(self):
        """Test switching to Korean language."""
        client = TestClient(app)
        response = client.get('/lang/ko', headers={'referer': 'http://localhost:8000/'})
        
        assert response.status_code == 307
        assert 'lang=ko' in response.headers['location']
    
    def test_language_switch_english(self):
        """Test switching to English language."""
        client = TestClient(app)
        response = client.get('/lang/en', headers={'referer': 'http://localhost:8000/'})
        
        assert response.status_code == 307
        assert 'lang=en' in response.headers['location']
    
    def test_language_switch_invalid_language(self):
        """Test switching to invalid language."""
        client = TestClient(app)
        response = client.get('/lang/invalid', headers={'referer': 'http://localhost:8000/'})
        
        assert response.status_code == 307
        assert 'lang=ko' in response.headers['location']  # Should default to Korean
    
    def test_language_switch_preserves_parameters(self):
        """Test that language switching preserves other URL parameters."""
        client = TestClient(app)
        response = client.get('/lang/en', headers={'referer': 'http://localhost:8000/dashboard?account_id=123&other=value'})
        
        location = response.headers['location']
        assert 'lang=en' in location
        assert 'account_id=123' in location
        assert 'other=value' in location
    
    def test_language_switch_replaces_existing_lang(self):
        """Test that language switching replaces existing lang parameter."""
        client = TestClient(app)
        response = client.get('/lang/en', headers={'referer': 'http://localhost:8000/?lang=ko&other=value'})
        
        location = response.headers['location']
        assert location.count('lang=') == 1
        assert 'lang=en' in location
        assert 'lang=ko' not in location
        assert 'other=value' in location


class TestTemplateRendering:
    """Test template rendering with i18n."""
    
    @patch('main.get_templates_with_i18n')
    def test_template_rendering_with_translations(self, mock_get_templates):
        """Test that templates are rendered with proper translations."""
        # Mock the i18n templates
        mock_template_response = Mock()
        mock_template_response.return_value = Mock()
        
        mock_templates = Mock()
        mock_templates.TemplateResponse = mock_template_response
        mock_get_templates.return_value = mock_templates
        
        # Mock the Jinja2 environment with translation functions
        mock_env = Mock()
        mock_env.globals = {
            '_': lambda x: f'TRANSLATED_{x}',
            'locale': 'ko',
            'translations': {'test': '테스트'}
        }
        mock_templates.env = mock_env
        
        client = TestClient(app)
        response = client.get('/')
        
        # Verify template was called with correct parameters
        mock_template_response.assert_called_once()
        call_args = mock_template_response.call_args
        assert call_args[0][0] == 'dashboard/dashboard.html'
        assert 'request' in call_args[0][1]
        assert 'active' in call_args[0][1]
        assert call_args[0][1]['active'] == 'dashboard'


class TestErrorHandling:
    """Test error handling in i18n system."""
    
    def test_missing_translation_key(self):
        """Test handling of missing translation keys."""
        from i18n import get_translation
        
        # Test that missing keys return the key itself
        result = get_translation('ko', 'nonexistent_key')
        assert result == 'nonexistent_key'
        
        result = get_translation('en', 'nonexistent_key')
        assert result == 'nonexistent_key'
    
    def test_invalid_locale_handling(self):
        """Test handling of invalid locale codes."""
        from i18n import get_all_translations, get_translation
        
        # Test that invalid locales return default translations
        ko_translations = get_all_translations('invalid')
        en_translations = get_all_translations('ko')
        
        # Should return Korean translations (default)
        assert ko_translations == en_translations
        
        # Test get_translation with invalid locale
        result = get_translation('invalid', 'dashboard')
        assert result == '대시보드'  # Should return Korean translation
    
    @patch('i18n_helpers.get_locale_from_request')
    def test_i18n_helper_error_handling(self, mock_get_locale):
        """Test error handling in i18n helpers."""
        # Test with exception in locale detection
        mock_get_locale.side_effect = Exception("Locale detection failed")
        
        from i18n_helpers import get_templates_with_i18n
        
        request = Mock()
        
        # Should not raise exception, should handle gracefully
        try:
            templates = get_templates_with_i18n(request)
            # If it doesn't raise an exception, that's good error handling
            assert templates is not None
        except Exception as e:
            # If it does raise an exception, it should be handled appropriately
            pytest.fail(f"i18n helper should handle exceptions gracefully: {e}")


class TestPerformance:
    """Test performance aspects of i18n system."""
    
    def test_translation_lookup_performance(self):
        """Test that translation lookups are fast."""
        import time
        from i18n import get_translation
        
        # Test multiple translation lookups
        start_time = time.time()
        
        for _ in range(1000):
            get_translation('ko', 'dashboard')
            get_translation('en', 'dashboard')
            get_translation('ko', 'account_management')
            get_translation('en', 'account_management')
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 4000 lookups in reasonable time (less than 1 second)
        assert duration < 1.0, f"Translation lookups took too long: {duration:.3f}s"
    
    def test_template_creation_performance(self):
        """Test that template creation is reasonably fast."""
        import time
        from i18n_helpers import get_templates_with_i18n
        
        request = Mock()
        
        start_time = time.time()
        
        # Create multiple template instances
        for _ in range(100):
            templates = get_templates_with_i18n(request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 template instances in reasonable time
        assert duration < 2.0, f"Template creation took too long: {duration:.3f}s"
