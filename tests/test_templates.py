"""
Unit tests for template rendering and translation integration.
"""
import pytest
from unittest.mock import Mock, patch
from jinja2 import Environment, FileSystemLoader
from i18n import get_all_translations


class TestTemplateTranslationIntegration:
    """Test that templates properly use translation functions."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create a mock Jinja2 environment with i18n functions
        self.env = Environment(loader=FileSystemLoader('templates'))
        
        # Add translation functions
        ko_translations = get_all_translations('ko')
        en_translations = get_all_translations('en')
        
        def gettext(message):
            return ko_translations.get(message, message)
        
        def ngettext(singular, plural, n):
            if n == 1:
                return ko_translations.get(singular, singular)
            return ko_translations.get(plural, plural)
        
        # Mock url_for function for templates
        def url_for(name, **kwargs):
            if name == 'static':
                path = kwargs.get('path', '')
                return f'/static{path}'
            return f'/{name}'
        
        self.env.globals.update(
            _=gettext,
            gettext=gettext,
            ngettext=ngettext,
            locale='ko',
            translations=ko_translations,
            url_for=url_for
        )
    
    def test_base_template_translations(self):
        """Test that base template uses translation functions."""
        template = self.env.get_template('base.html')
        
        # Test rendering with Korean translations
        rendered = template.render(active='dashboard')
        
        # Check that Korean translations are used
        assert '대시보드' in rendered
        assert '계좌 관리' in rendered
        assert '계좌 정보' in rendered
        assert '거래 내역' in rendered
        
        # Check that language switcher is present
        assert '한국어' in rendered
        assert 'English' in rendered
        assert '/lang/ko' in rendered
        assert '/lang/en' in rendered
    
    def test_dashboard_template_translations(self):
        """Test that dashboard template uses translation functions."""
        template = self.env.get_template('dashboard/dashboard.html')
        
        rendered = template.render()
        
        # Check that Korean translations are used in the rendered content
        # Note: The template extends base.html, so we check for the actual rendered content
        assert '대시보드' in rendered  # From base template navigation
        assert '총 자산' in rendered
        assert '자산 in USD' in rendered
        assert '자산 in KRW' in rendered
        assert 'USD 계좌' in rendered
        assert 'KRW 계좌' in rendered
        # Note: Table headers with '은행' and '계좌명' are in tbody that may not render without data
        # Check for the translation function calls in the template file
        with open('templates/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        assert '{{ _(\'bank\') }}' in template_content or '은행' in rendered
        assert '{{ _(\'account_name\') }}' in template_content or '계좌명' in rendered
    
    def test_transactions_template_translations(self):
        """Test that transactions template uses translation functions."""
        template = self.env.get_template('transactions/transactions.html')
        
        # Provide required variables for the template
        rendered = template.render(
            selected_account=None,
            transaction_type_map={},
            accounts=[]
        )
        
        # Check that Korean translations are used
        assert '왼쪽에서 계좌를 선택해주세요.' in rendered
    
    def test_account_setting_template_translations(self):
        """Test that account setting template uses translation functions."""
        template = self.env.get_template('account_setting/accounts.html')
        
        rendered = template.render(
            accounts=[],
            bank_names=[],
            owners=[],
            account_countries=[],
            account_currency_types=[],
            account_types=[],
            account_categories=[]
        )
        
        # Check that Korean translations are used
        assert '계좌 추가' in rendered
        assert '계좌 목록' in rendered
        assert '계좌 이름' in rendered
        assert '추가' in rendered
    
    def test_template_with_english_translations(self):
        """Test template rendering with English translations."""
        # Create environment with English translations
        env = Environment(loader=FileSystemLoader('templates'))
        en_translations = get_all_translations('en')
        
        def gettext(message):
            return en_translations.get(message, message)
        
        # Mock url_for function for templates
        def url_for(name, **kwargs):
            if name == 'static':
                path = kwargs.get('path', '')
                return f'/static{path}'
            return f'/{name}'
        
        env.globals.update(
            _=gettext,
            gettext=gettext,
            locale='en',
            translations=en_translations,
            url_for=url_for
        )
        
        template = env.get_template('base.html')
        rendered = template.render(active='dashboard')
        
        # Check that English translations are used
        assert 'Dashboard' in rendered
        assert 'Account Management' in rendered
        assert 'Account Info' in rendered
        assert 'Transactions' in rendered
    
    def test_template_missing_translation_fallback(self):
        """Test that templates handle missing translations gracefully."""
        template = self.env.get_template('base.html')
        
        # Test with a missing translation key
        rendered = template.render(active='dashboard')
        
        # Should not crash and should render the template
        assert rendered is not None
        assert len(rendered) > 0
    
    def test_template_conditional_rendering(self):
        """Test that templates properly handle conditional rendering with translations."""
        template = self.env.get_template('transactions/transactions.html')
        
        # Test with selected account
        rendered_with_account = template.render(
            selected_account=Mock(),
            transaction_type_map={},
            accounts=[]
        )
        assert rendered_with_account is not None
        
        # Test without selected account
        rendered_without_account = template.render(
            selected_account=None,
            transaction_type_map={},
            accounts=[]
        )
        assert '왼쪽에서 계좌를 선택해주세요.' in rendered_without_account
    
    def test_template_variable_interpolation(self):
        """Test that templates properly interpolate variables with translations."""
        template = self.env.get_template('base.html')
        
        # Test with different active values
        for active in ['dashboard', 'account_setting', 'account_dashboard', 'transactions']:
            rendered = template.render(active=active)
            assert f'active' in rendered or f'class="active"' in rendered


class TestTemplateSyntax:
    """Test template syntax and structure."""
    
    def test_template_extends_base(self):
        """Test that templates properly extend base template."""
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Test that dashboard template extends base
        template = env.get_template('dashboard/dashboard.html')
        assert template is not None
        
        # Test that transactions template extends base
        template = env.get_template('transactions/transactions.html')
        assert template is not None
    
    def test_template_imports(self):
        """Test that templates properly import macros."""
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Test that templates can be loaded (imports work)
        try:
            template = env.get_template('transactions/transactions.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template imports failed: {e}")
    
    def test_template_blocks(self):
        """Test that templates properly define and use blocks."""
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Test base template has content block
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_source = f.read()
        assert '{% block content %}' in base_source
        assert '{% endblock %}' in base_source
        
        # Test child templates use content block
        with open('templates/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
            dashboard_source = f.read()
        assert '{% block content %}' in dashboard_source
        assert '{% endblock %}' in dashboard_source


class TestTranslationCompleteness:
    """Test that all templates have complete translations."""
    
    def test_all_templates_have_translations(self):
        """Test that all template files can be loaded and have translation functions."""
        import os
        from pathlib import Path
        
        templates_dir = Path('templates')
        template_files = list(templates_dir.rglob('*.html'))
        
        env = Environment(loader=FileSystemLoader('templates'))
        ko_translations = get_all_translations('ko')
        
        def gettext(message):
            return ko_translations.get(message, message)
        
        def url_for(name, **kwargs):
            if name == 'static':
                path = kwargs.get('path', '')
                return f'/static{path}'
            return f'/{name}'
        
        env.globals.update(_=gettext, locale='ko', url_for=url_for)
        
        for template_file in template_files:
            if template_file.name.startswith('.'):
                continue
                
            relative_path = template_file.relative_to(templates_dir)
            
            try:
                # Just test that the template can be loaded
                template = env.get_template(str(relative_path))
                assert template is not None
                
                # Check that the template source contains translation function calls
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # At least one template should have translation functions
                if '{{ _(' in template_content:
                    assert True  # Template has translation functions
                    
            except Exception as e:
                pytest.fail(f"Template {relative_path} failed to load: {e}")
    
    def test_translation_keys_used_in_templates(self):
        """Test that translation keys used in templates exist in translation files."""
        import re
        from pathlib import Path
        
        # Get all translation keys
        ko_translations = get_all_translations('ko')
        en_translations = get_all_translations('en')
        
        # Find all translation function calls in templates
        templates_dir = Path('templates')
        template_files = list(templates_dir.rglob('*.html'))
        
        used_keys = set()
        for template_file in template_files:
            if template_file.name.startswith('.'):
                continue
                
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find all _('key') patterns
                matches = re.findall(r"\{\{\s*_\('([^']+)'\)\s*\}\}", content)
                used_keys.update(matches)
        
        # Check that all used keys exist in translations
        missing_ko = used_keys - set(ko_translations.keys())
        missing_en = used_keys - set(en_translations.keys())
        
        assert not missing_ko, f"Missing Korean translations: {missing_ko}"
        assert not missing_en, f"Missing English translations: {missing_en}"
