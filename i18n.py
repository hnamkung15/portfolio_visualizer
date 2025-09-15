"""
Internationalization utilities for the portfolio visualizer.
"""
import os
from babel import Locale, UnknownLocaleError
from babel.support import Format
from babel.messages.frontend import extract_messages
from jinja2 import Environment, FileSystemLoader
from jinja2.ext import i18n

# Supported languages
SUPPORTED_LANGUAGES = {
    'ko': 'Korean',
    'en': 'English'
}

DEFAULT_LANGUAGE = 'ko'

def get_locale_from_request(request):
    """Extract locale from request parameters or headers."""
    # Check URL parameter first
    locale = request.query_params.get('lang')
    if locale and locale in SUPPORTED_LANGUAGES:
        return locale
    
    # Check Accept-Language header
    accept_language = request.headers.get('accept-language', '')
    if accept_language:
        # Parse Accept-Language header (simple implementation)
        for lang in accept_language.split(','):
            lang = lang.split(';')[0].strip()
            if lang in SUPPORTED_LANGUAGES:
                return lang
            # Check language code without country code
            lang_code = lang.split('-')[0]
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
    
    return DEFAULT_LANGUAGE

def get_locale_info(locale_code):
    """Get locale information for the given code."""
    try:
        locale = Locale(locale_code)
        return {
            'code': locale_code,
            'name': SUPPORTED_LANGUAGES.get(locale_code, locale_code),
            'locale': locale
        }
    except UnknownLocaleError:
        return {
            'code': DEFAULT_LANGUAGE,
            'name': SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
            'locale': Locale(DEFAULT_LANGUAGE)
        }

def setup_jinja2_i18n(template_dir):
    """Set up Jinja2 with i18n support."""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        extensions=[i18n]
    )
    
    # Add translation functions to Jinja2 environment
    def gettext(message):
        """Simple gettext implementation - will be replaced with actual translations."""
        return message
    
    def ngettext(singular, plural, n):
        """Simple ngettext implementation."""
        if n == 1:
            return singular
        return plural
    
    env.globals.update(
        _=gettext,
        gettext=gettext,
        ngettext=ngettext,
        locale=get_locale_info
    )
    
    return env

# Translation dictionaries
TRANSLATIONS = {
    'ko': {
        # Navigation
        'dashboard': '대시보드',
        'account_management': '계좌 관리',
        'account_info': '계좌 정보',
        'transactions': '거래 내역',
        
        # Dashboard
        'data_sync': 'Data Sync',
        'last_sync': '마지막 동기화: 아직 동기화되지 않았습니다.',
        'loading': '로딩 중...',
        'total_assets': '총 자산',
        'assets_usd': '자산 in USD',
        'assets_krw': '자산 in KRW',
        'usd_accounts': 'USD 계좌',
        'krw_accounts': 'KRW 계좌',
        'bank': '은행',
        'account_name': '계좌명',
        'balance_usd': '잔액(USD)',
        'balance_krw': '잔액(KRW)',
        'cash': '현금',
        'saving': '적금',
        'bond': '채권',
        'stock': '주식',
        'converted_krw': '환산(KRW)',
        'converted_usd': '환산(USD)',
        'invested_amount_usd': '투자금액(USD)',
        'invested_amount_krw': '투자금액(KRW)',
        'profit_amount_usd': '수익금액(USD)',
        'profit_amount_krw': '수익금액(KRW)',
        'return_rate': '수익률(%)',
        'fx_effect': '환율 효과(%)',
        'avg_rate': '(평균환율)',
        'fx_considered_profit_krw': '환율고려 수익금액(KRW)',
        'fx_considered_return_rate': '환율고려 수익률(%)',
        'total': '총계',
        'stock_details_usd': '보유 종목 상세 (USD)',
        'stock_details_krw': '보유 종목 상세 (KRW)',
        'stock_name': '주식 이름',
        'stock_code': '종목 코드',
        'quantity': '보유수량',
        'avg_price_usd': '평균매입가 (USD)',
        'avg_price_krw': '평균매입가 (KRW)',
        'current_price_usd': '현재가 (USD)',
        'current_price_krw': '현재가 (KRW)',
        'total_value_usd': '총 평가금액 (USD)',
        'total_value_krw': '총 평가금액 (KRW)',
        'total_gain_usd': '총 시세차익 (USD)',
        'total_gain_krw': '총 시세차익 (KRW)',
        'total_dividend_usd': '누적 배당금 (USD)',
        'total_dividend_krw': '누적 배당금 (KRW)',
        'asset_category_breakdown': '자산 카테고리 구성',
        
        # Transactions
        'select_account': '왼쪽에서 계좌를 선택해주세요.',
        
        # Account Settings
        'add_account': '계좌 추가',
        'account_list': '계좌 목록',
        'account_name_label': '계좌 이름',
        'add': '추가',
        'owner': 'owner',
        'bank': 'bank',
        'name': 'name',
        'country': 'country',
        'currency_type': 'currency_type',
        'type': 'type',
        'category': 'category',
        'delete': 'delete',
        
        # Language switcher
        'language': '언어',
        'korean': '한국어',
        'english': 'English',
        
        # Transactions
        'add_transaction': '거래 추가',
        'amount_required': '금액 (필수)',
        'symbol': '종목',
        'price': '가격',
        'quantity': '수량',
        'fee': '수수료',
        'fx_rate': '환율',
        'description': '설명',
        'transaction_list': '거래내역 목록',
        'date': '날짜',
        'type': '종류',
        'amount': '금액',
        'remaining': '잔여',
        'balance': '잔고',
        'action': '액션',
        'no_transactions': '거래내역이 없습니다.',
        'csv_upload': 'CSV 파일 업로드',
        'upload': '업로드',
        'account_list': '계좌 목록',
        
        # Account Dashboard
        'portfolio_status': '포트폴리오 현황',
        'stock_code': '종목코드',
        'stock_name': '종목명',
        'investment_amount': '투자 금액',
        'valuation_amount': '평가 금액',
        'valuation_profit': '평가 수익',
        'realized_profit': '청산 이익',
        'total_dividend': '총 배당금',
        'total_profit': '총 수익',
        'total': '합계',
        'graph': '그래프',
        'recompute_graph': 'Recompute Graph Result',
        'not_stock_account': '주식 계좌가 아닙니다. 주식 계좌를 선택해주세요.',
    },
    'en': {
        # Navigation
        'dashboard': 'Dashboard',
        'account_management': 'Account Management',
        'account_info': 'Account Info',
        'transactions': 'Transactions',
        
        # Dashboard
        'data_sync': 'Data Sync',
        'last_sync': 'Last sync: Not synced yet.',
        'loading': 'Loading...',
        'total_assets': 'Total Assets',
        'assets_usd': 'Assets in USD',
        'assets_krw': 'Assets in KRW',
        'usd_accounts': 'USD Accounts',
        'krw_accounts': 'KRW Accounts',
        'bank': 'Bank',
        'account_name': 'Account Name',
        'balance_usd': 'Balance (USD)',
        'balance_krw': 'Balance (KRW)',
        'cash': 'Cash',
        'saving': 'Saving',
        'bond': 'Bond',
        'stock': 'Stock',
        'converted_krw': 'Converted (KRW)',
        'converted_usd': 'Converted (USD)',
        'invested_amount_usd': 'Invested Amount (USD)',
        'invested_amount_krw': 'Invested Amount (KRW)',
        'profit_amount_usd': 'Profit Amount (USD)',
        'profit_amount_krw': 'Profit Amount (KRW)',
        'return_rate': 'Return Rate (%)',
        'fx_effect': 'FX Effect (%)',
        'avg_rate': '(Avg Rate)',
        'fx_considered_profit_krw': 'FX Considered Profit (KRW)',
        'fx_considered_return_rate': 'FX Considered Return Rate (%)',
        'total': 'Total',
        'stock_details_usd': 'Stock Holdings Detail (USD)',
        'stock_details_krw': 'Stock Holdings Detail (KRW)',
        'stock_name': 'Stock Name',
        'stock_code': 'Stock Code',
        'quantity': 'Quantity',
        'avg_price_usd': 'Avg Price (USD)',
        'avg_price_krw': 'Avg Price (KRW)',
        'current_price_usd': 'Current Price (USD)',
        'current_price_krw': 'Current Price (KRW)',
        'total_value_usd': 'Total Value (USD)',
        'total_value_krw': 'Total Value (KRW)',
        'total_gain_usd': 'Total Gain (USD)',
        'total_gain_krw': 'Total Gain (KRW)',
        'total_dividend_usd': 'Total Dividend (USD)',
        'total_dividend_krw': 'Total Dividend (KRW)',
        'asset_category_breakdown': 'Asset Category Breakdown',
        
        # Transactions
        'select_account': 'Please select an account from the left.',
        
        # Account Settings
        'add_account': 'Add Account',
        'account_list': 'Account List',
        'account_name_label': 'Account Name',
        'add': 'Add',
        'owner': 'Owner',
        'bank': 'Bank',
        'name': 'Name',
        'country': 'Country',
        'currency_type': 'Currency Type',
        'type': 'Type',
        'category': 'Category',
        'delete': 'Delete',
        
        # Language switcher
        'language': 'Language',
        'korean': '한국어',
        'english': 'English',
        
        # Transactions
        'add_transaction': 'Add Transaction',
        'amount_required': 'Amount (Required)',
        'symbol': 'Symbol',
        'price': 'Price',
        'quantity': 'Quantity',
        'fee': 'Fee',
        'fx_rate': 'FX Rate',
        'description': 'Description',
        'transaction_list': 'Transaction List',
        'date': 'Date',
        'type': 'Type',
        'amount': 'Amount',
        'remaining': 'Remaining',
        'balance': 'Balance',
        'action': 'Action',
        'no_transactions': 'No transactions found.',
        'csv_upload': 'CSV File Upload',
        'upload': 'Upload',
        'account_list': 'Account List',
        
        # Account Dashboard
        'portfolio_status': 'Portfolio Status',
        'stock_code': 'Stock Code',
        'stock_name': 'Stock Name',
        'investment_amount': 'Investment Amount',
        'valuation_amount': 'Valuation Amount',
        'valuation_profit': 'Valuation Profit',
        'realized_profit': 'Realized Profit',
        'total_dividend': 'Total Dividend',
        'total_profit': 'Total Profit',
        'total': 'Total',
        'graph': 'Graph',
        'recompute_graph': 'Recompute Graph Result',
        'not_stock_account': 'This is not a stock account. Please select a stock account.',
    }
}

def get_translation(locale_code, key, **kwargs):
    """Get translation for a key in the specified locale."""
    translations = TRANSLATIONS.get(locale_code, TRANSLATIONS[DEFAULT_LANGUAGE])
    return translations.get(key, key).format(**kwargs) if kwargs else translations.get(key, key)

def get_all_translations(locale_code):
    """Get all translations for a locale."""
    return TRANSLATIONS.get(locale_code, TRANSLATIONS[DEFAULT_LANGUAGE])
