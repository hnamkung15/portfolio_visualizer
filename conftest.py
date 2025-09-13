"""
Pytest configuration and fixtures for the portfolio visualizer test suite.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Provide a test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Provide a mock database session."""
    mock_db = Mock()
    mock_db.query.return_value.order_by.return_value.all.return_value = []
    mock_db.query.return_value.get.return_value = None
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.delete.return_value = None
    return mock_db


@pytest.fixture
def mock_templates():
    """Provide mock i18n templates."""
    mock_template_response = Mock()
    mock_template_response.return_value = Mock()
    mock_templates = Mock()
    mock_templates.TemplateResponse = mock_template_response
    return mock_templates


@pytest.fixture
def korean_translations():
    """Provide Korean translations for testing."""
    from i18n import get_all_translations
    return get_all_translations('ko')


@pytest.fixture
def english_translations():
    """Provide English translations for testing."""
    from i18n import get_all_translations
    return get_all_translations('en')


@pytest.fixture
def mock_request():
    """Provide a mock request object."""
    request = Mock()
    request.query_params = {}
    request.headers = {}
    return request


@pytest.fixture
def temp_templates_dir():
    """Provide a temporary directory for template testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        templates_dir = os.path.join(temp_dir, 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        yield templates_dir


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # Mock any external dependencies that might cause issues in tests
    with patch('main.Base.metadata.create_all'):
        yield


@pytest.fixture
def sample_account_data():
    """Provide sample account data for testing."""
    return {
        'id': 1,
        'owner': 'John Doe',
        'bank_name': 'Test Bank',
        'account_name': 'Test Account',
        'account_country': 'US',
        'account_currency_type': 'USD',
        'account_type': 'Checking',
        'account_category': 'Personal',
        'order': 0
    }


@pytest.fixture
def sample_transaction_data():
    """Provide sample transaction data for testing."""
    return {
        'id': 1,
        'date': '2024-01-01',
        'account_id': 1,
        'amount': 1000.0,
        'type': 'Deposit',
        'description': 'Test transaction',
        'symbol': 'AAPL',
        'price': 150.0,
        'quantity': 10.0,
        'fee': 5.0,
        'fx_rate': 1.0
    }


# Pytest markers for different test categories
pytestmark = [
    pytest.mark.i18n,
]
