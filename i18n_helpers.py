"""
Helper functions for i18n in routers.
"""
from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from jinja2.ext import i18n
from i18n import get_locale_from_request, get_all_translations

def get_templates_with_i18n(request: Request):
    """Get templates with i18n support for the current request."""
    locale = get_locale_from_request(request)
    translations = get_all_translations(locale)
    
    # Create a custom Jinja2Templates instance with i18n
    env = Environment(
        loader=FileSystemLoader("templates"),
        extensions=[i18n]
    )
    
    # Add translation functions
    def gettext(message):
        return translations.get(message, message)
    
    def ngettext(singular, plural, n):
        if n == 1:
            return translations.get(singular, singular)
        return translations.get(plural, plural)
    
    env.globals.update(
        _=gettext,
        gettext=gettext,
        ngettext=ngettext,
        locale=locale,
        translations=translations
    )
    
    return Jinja2Templates(env=env)
