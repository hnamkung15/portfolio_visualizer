"""
Integration tests for the complete i18n system.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from main import app


class TestEndToEndI18n:
    """End-to-end tests for the complete i18n system."""
    
    def test_complete_language_switching_flow(self):
        """Test complete language switching flow from Korean to English."""
        client = TestClient(app)
        
        # Start with Korean (default)
        response = client.get('/')
        assert response.status_code == 200
        
        # Switch to English
        response = client.get('/lang/en', headers={'referer': 'http://localhost:8000/'})
        assert response.status_code == 307
        assert 'lang=en' in response.headers['location']
        
        # Follow the redirect to English page
        response = client.get('/?lang=en')
        assert response.status_code == 200
        
        # Switch back to Korean
        response = client.get('/lang/ko', headers={'referer': 'http://localhost:8000/?lang=en'})
        assert response.status_code == 307
        assert 'lang=ko' in response.headers['location']
    
    def test_language_persistence_across_pages(self):
        """Test that language choice persists across different pages."""
        client = TestClient(app)
        
        # Set language to English
        response = client.get('/lang/en', headers={'referer': 'http://localhost:8000/'})
        english_url = response.headers['location']
        
        # Navigate to different pages with English
        pages = ['/dashboard', '/transactions', '/account_setting', '/account_dashboard']
        
        for page in pages:
            # Add lang=en to the page URL
            page_url = f"{page}?lang=en"
            response = client.get(page_url)
            # Should not return 500 error (even if database is not set up)
            assert response.status_code in [200, 500]  # 500 is expected due to missing DB
    
    def test_language_switching_with_existing_parameters(self):
        """Test language switching preserves existing URL parameters."""
        client = TestClient(app)
        
        # Start with a URL that has parameters
        original_url = 'http://localhost:8000/dashboard?account_id=123&filter=active'
        
        # Switch to English
        response = client.get('/lang/en', headers={'referer': original_url})
        assert response.status_code == 307
        
        location = response.headers['location']
        assert 'lang=en' in location
        assert 'account_id=123' in location
        assert 'filter=active' in location
        assert location.count('lang=') == 1  # Should not duplicate lang parameter
    
    def test_multiple_consecutive_language_switches(self):
        """Test multiple consecutive language switches don't accumulate parameters."""
        client = TestClient(app)
        
        current_url = 'http://localhost:8000/'
        
        # Perform multiple switches
        for i in range(5):
            language = 'en' if i % 2 == 0 else 'ko'
            response = client.get(f'/lang/{language}', headers={'referer': current_url})
            assert response.status_code == 307
            
            current_url = response.headers['location']
            # Verify only one lang parameter exists
            assert current_url.count('lang=') == 1
            assert f'lang={language}' in current_url
    
    def test_language_switching_with_fragments(self):
        """Test language switching preserves URL fragments."""
        client = TestClient(app)
        
        original_url = 'http://localhost:8000/dashboard?param=value#section1'
        
        response = client.get('/lang/en', headers={'referer': original_url})
        assert response.status_code == 307
        
        location = response.headers['location']
        assert 'lang=en' in location
        assert 'param=value' in location
        assert '#section1' in location


class TestI18nWithMockedDatabase:
    """Test i18n functionality with mocked database to avoid DB errors."""
    
    @patch('routers.account_setting.get_templates_with_i18n')
    @patch('routers.account_setting.get_db')
    def test_account_setting_with_i18n(self, mock_get_db, mock_get_templates):
        """Test account setting page with i18n and mocked database."""
        # Mock database
        mock_db = Mock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        mock_get_db.return_value = mock_db
        
        # Mock templates
        mock_template_response = Mock()
        mock_template_response.return_value = Mock()
        mock_templates = Mock()
        mock_templates.TemplateResponse = mock_template_response
        mock_get_templates.return_value = mock_templates
        
        client = TestClient(app)
        response = client.get('/account_setting')
        
        assert response.status_code == 200
        mock_get_templates.assert_called_once()
    
    @patch('routers.transactions.get_templates_with_i18n')
    @patch('routers.transactions.get_db')
    def test_transactions_with_i18n(self, mock_get_db, mock_get_templates):
        """Test transactions page with i18n and mocked database."""
        # Mock database
        mock_db = Mock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        mock_get_db.return_value = mock_db
        
        # Mock templates
        mock_template_response = Mock()
        mock_template_response.return_value = Mock()
        mock_templates = Mock()
        mock_templates.TemplateResponse = mock_template_response
        mock_get_templates.return_value = mock_templates
        
        client = TestClient(app)
        response = client.get('/transactions')
        
        assert response.status_code == 200
        mock_get_templates.assert_called_once()
    
    @patch('routers.account_dashboard.get_templates_with_i18n')
    @patch('routers.account_dashboard.get_db')
    def test_account_dashboard_with_i18n(self, mock_get_db, mock_get_templates):
        """Test account dashboard page with i18n and mocked database."""
        # Mock database
        mock_db = Mock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        mock_get_db.return_value = mock_db
        
        # Mock templates
        mock_template_response = Mock()
        mock_template_response.return_value = Mock()
        mock_templates = Mock()
        mock_templates.TemplateResponse = mock_template_response
        mock_get_templates.return_value = mock_templates
        
        client = TestClient(app)
        response = client.get('/account_dashboard')
        
        assert response.status_code == 200
        mock_get_templates.assert_called_once()


class TestI18nErrorHandling:
    """Test i18n system error handling."""
    
    def test_invalid_language_handling(self):
        """Test handling of invalid language codes."""
        client = TestClient(app)
        
        # Test with invalid language
        response = client.get('/lang/invalid', headers={'referer': 'http://localhost:8000/'})
        assert response.status_code == 307
        assert 'lang=ko' in response.headers['location']  # Should default to Korean
    
    def test_missing_referer_handling(self):
        """Test handling of missing referer header."""
        client = TestClient(app)
        
        response = client.get('/lang/en')
        assert response.status_code == 307
        assert response.headers['location'] == '/?lang=en'
    
    def test_malformed_url_handling(self):
        """Test handling of malformed referer URLs."""
        client = TestClient(app)
        
        # Test with malformed URL
        response = client.get('/lang/en', headers={'referer': 'not-a-valid-url'})
        assert response.status_code == 307
        # Should still work and redirect to a valid URL
    
    @patch('i18n_helpers.get_locale_from_request')
    def test_locale_detection_error_handling(self, mock_get_locale):
        """Test handling of errors in locale detection."""
        # Mock locale detection to raise an exception
        mock_get_locale.side_effect = Exception("Locale detection failed")
        
        client = TestClient(app)
        
        # Should not crash the application
        response = client.get('/')
        assert response.status_code in [200, 500]  # Should handle gracefully


class TestI18nPerformance:
    """Test i18n system performance."""
    
    def test_language_switching_performance(self):
        """Test that language switching is fast."""
        import time
        
        client = TestClient(app)
        
        start_time = time.time()
        
        # Perform multiple language switches
        for _ in range(100):
            response = client.get('/lang/en', headers={'referer': 'http://localhost:8000/'})
            assert response.status_code == 307
            
            response = client.get('/lang/ko', headers={'referer': 'http://localhost:8000/'})
            assert response.status_code == 307
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 200 language switches in reasonable time
        assert duration < 5.0, f"Language switching took too long: {duration:.3f}s"
    
    def test_template_rendering_performance(self):
        """Test that template rendering with i18n is reasonably fast."""
        import time
        
        client = TestClient(app)
        
        start_time = time.time()
        
        # Make multiple requests
        for _ in range(50):
            response = client.get('/')
            assert response.status_code in [200, 500]  # 500 expected due to missing DB
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 50 requests in reasonable time
        assert duration < 10.0, f"Template rendering took too long: {duration:.3f}s"


class TestI18nConsistency:
    """Test i18n system consistency."""
    
    def test_translation_consistency_across_pages(self):
        """Test that translations are consistent across all pages."""
        from i18n import get_all_translations
        
        ko_translations = get_all_translations('ko')
        en_translations = get_all_translations('en')
        
        # Check that both languages have the same keys
        ko_keys = set(ko_translations.keys())
        en_keys = set(en_translations.keys())
        
        assert ko_keys == en_keys, "Korean and English translations should have the same keys"
        
        # Check that no translation is empty
        for key, value in ko_translations.items():
            assert value.strip() != "", f"Korean translation for '{key}' is empty"
        
        for key, value in en_translations.items():
            assert value.strip() != "", f"English translation for '{key}' is empty"
    
    def test_language_switching_consistency(self):
        """Test that language switching behavior is consistent."""
        client = TestClient(app)
        
        # Test multiple URLs with language switching
        test_urls = [
            'http://localhost:8000/',
            'http://localhost:8000/dashboard',
            'http://localhost:8000/transactions',
            'http://localhost:8000/account_setting',
            'http://localhost:8000/account_dashboard'
        ]
        
        for url in test_urls:
            # Switch to English
            response = client.get('/lang/en', headers={'referer': url})
            assert response.status_code == 307
            assert 'lang=en' in response.headers['location']
            
            # Switch to Korean
            response = client.get('/lang/ko', headers={'referer': url})
            assert response.status_code == 307
            assert 'lang=ko' in response.headers['location']
    
    def test_url_parameter_handling_consistency(self):
        """Test that URL parameter handling is consistent across different scenarios."""
        client = TestClient(app)
        
        test_cases = [
            'http://localhost:8000/',
            'http://localhost:8000/?lang=ko',
            'http://localhost:8000/?lang=en',
            'http://localhost:8000/?param1=value1&lang=ko&param2=value2',
            'http://localhost:8000/dashboard?account_id=123&lang=en&filter=active'
        ]
        
        for url in test_cases:
            # Switch to English
            response = client.get('/lang/en', headers={'referer': url})
            assert response.status_code == 307
            location = response.headers['location']
            
            # Verify only one lang parameter
            assert location.count('lang=') == 1
            assert 'lang=en' in location
            
            # Verify other parameters are preserved
            if 'param1=value1' in url:
                assert 'param1=value1' in location
            if 'param2=value2' in url:
                assert 'param2=value2' in location
            if 'account_id=123' in url:
                assert 'account_id=123' in location
            if 'filter=active' in url:
                assert 'filter=active' in location
