"""
Unit tests for language switching functionality.
"""
import pytest
from unittest.mock import Mock
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from main import switch_language


class TestLanguageSwitching:
    """Test language switching route functionality."""
    
    def test_switch_language_valid_korean(self):
        """Test switching to Korean language."""
        request = Mock()
        request.headers = {'referer': 'http://localhost:8000/'}
        
        response = switch_language('ko', request)
        
        assert response.status_code == 307  # Temporary redirect
        assert 'lang=ko' in response.headers['location']
    
    def test_switch_language_valid_english(self):
        """Test switching to English language."""
        request = Mock()
        request.headers = {'referer': 'http://localhost:8000/'}
        
        response = switch_language('en', request)
        
        assert response.status_code == 307
        assert 'lang=en' in response.headers['location']
    
    def test_switch_language_invalid_language(self):
        """Test switching to invalid language (should default to Korean)."""
        request = Mock()
        request.headers = {'referer': 'http://localhost:8000/'}
        
        response = switch_language('invalid', request)
        
        assert response.status_code == 307
        assert 'lang=ko' in response.headers['location']
    
    def test_switch_language_preserves_other_parameters(self):
        """Test that other URL parameters are preserved."""
        request = Mock()
        request.headers = {'referer': 'http://localhost:8000/dashboard?account_id=123&other=value'}
        
        response = switch_language('en', request)
        
        location = response.headers['location']
        assert 'lang=en' in location
        assert 'account_id=123' in location
        assert 'other=value' in location
    
    def test_switch_language_replaces_existing_lang(self):
        """Test that existing lang parameter is replaced, not appended."""
        request = Mock()
        request.headers = {'referer': 'http://localhost:8000/?lang=ko&other=value'}
        
        response = switch_language('en', request)
        
        location = response.headers['location']
        assert location.count('lang=') == 1  # Should only appear once
        assert 'lang=en' in location
        assert 'lang=ko' not in location
        assert 'other=value' in location
    
    def test_switch_language_no_referer(self):
        """Test language switching when no referer header."""
        request = Mock()
        request.headers = {}
        
        response = switch_language('en', request)
        
        assert response.status_code == 307
        assert response.headers['location'] == '/?lang=en'
    
    def test_switch_language_complex_url(self):
        """Test language switching with complex URL structure."""
        request = Mock()
        request.headers = {'referer': 'https://example.com:8080/path/to/page?param1=value1&lang=ko&param2=value2#fragment'}
        
        response = switch_language('en', request)
        
        location = response.headers['location']
        parsed = urlparse(location)
        query_params = parse_qs(parsed.query)
        
        assert parsed.scheme == 'https'
        assert parsed.netloc == 'example.com:8080'
        assert parsed.path == '/path/to/page'
        assert parsed.fragment == 'fragment'
        assert query_params['lang'] == ['en']
        assert query_params['param1'] == ['value1']
        assert query_params['param2'] == ['value2']
    
    def test_switch_language_multiple_switches(self):
        """Test multiple consecutive language switches."""
        # Simulate multiple switches
        current_url = 'http://localhost:8000/'
        
        # First switch: no lang -> ko
        request1 = Mock()
        request1.headers = {'referer': current_url}
        response1 = switch_language('ko', request1)
        new_url1 = response1.headers['location']
        
        # Second switch: ko -> en
        request2 = Mock()
        request2.headers = {'referer': new_url1}
        response2 = switch_language('en', request2)
        new_url2 = response2.headers['location']
        
        # Third switch: en -> ko
        request3 = Mock()
        request3.headers = {'referer': new_url2}
        response3 = switch_language('ko', request3)
        new_url3 = response3.headers['location']
        
        # Verify no parameter accumulation
        assert new_url1 == 'http://localhost:8000/?lang=ko'
        assert new_url2 == 'http://localhost:8000/?lang=en'
        assert new_url3 == 'http://localhost:8000/?lang=ko'
        
        # Verify each URL has exactly one lang parameter
        for url in [new_url1, new_url2, new_url3]:
            assert url.count('lang=') == 1


class TestURLParsingLogic:
    """Test the URL parsing logic used in language switching."""
    
    def test_url_parsing_simple_url(self):
        """Test parsing a simple URL without parameters."""
        url = 'http://localhost:8000/'
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['lang'] = ['en']
        
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        
        assert new_url == 'http://localhost:8000/?lang=en'
    
    def test_url_parsing_with_existing_params(self):
        """Test parsing URL with existing parameters."""
        url = 'http://localhost:8000/dashboard?account_id=123&other=value'
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['lang'] = ['ko']
        
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        
        assert 'lang=ko' in new_url
        assert 'account_id=123' in new_url
        assert 'other=value' in new_url
    
    def test_url_parsing_replace_existing_lang(self):
        """Test replacing existing lang parameter."""
        url = 'http://localhost:8000/?lang=ko&other=value'
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['lang'] = ['en']  # Replace existing lang
        
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        
        assert new_url == 'http://localhost:8000/?lang=en&other=value'
        assert 'lang=ko' not in new_url
        assert 'lang=en' in new_url
    
    def test_url_parsing_preserves_fragment(self):
        """Test that URL fragment is preserved."""
        url = 'http://localhost:8000/page#section1'
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['lang'] = ['en']
        
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        
        assert new_url == 'http://localhost:8000/page?lang=en#section1'
