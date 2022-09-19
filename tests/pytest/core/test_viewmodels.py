from django.utils import translation
from django.utils.translation import gettext as _

from benefits.core.viewmodels import ErrorPage


def test_ErrorPage_error_translations():
    translation.activate("en")

    error_page = ErrorPage.error()
    english_title = f"{_('core.pages.index.prefix')}: {_('core.pages.server_error.title')}"
    english_content_title = _("core.pages.server_error.title")
    english_paragraphs = [_("core.pages.server_error.p[0]"), _("core.pages.server_error.p[1]")]

    assert error_page.title == english_title
    assert error_page.content_title == english_content_title
    assert error_page.paragraphs == english_paragraphs

    translation.activate("es")

    error_page = ErrorPage.error()
    spanish_title = f"{_('core.pages.index.prefix')}: {_('core.pages.server_error.title')}"
    spanish_content_title = _("core.pages.server_error.title")
    spanish_paragraphs = [_("core.pages.server_error.p[0]"), _("core.pages.server_error.p[1]")]

    assert error_page.title != english_title
    assert error_page.content_title != english_content_title
    assert error_page.paragraphs != english_paragraphs

    assert error_page.title == spanish_title
    assert error_page.content_title == spanish_content_title
    assert error_page.paragraphs == spanish_paragraphs


def test_ErrorPage_not_found_translations():
    translation.activate("en")

    error_page = ErrorPage.not_found()
    english_title = f"{_('core.pages.index.prefix')}: {_('core.pages.not_found.title')}"
    english_content_title = _("core.pages.not_found.content_title")
    english_paragraphs = [_("core.pages.not_found.p[0]")]

    assert error_page.title == english_title
    assert error_page.content_title == english_content_title
    assert error_page.paragraphs == english_paragraphs

    translation.activate("es")

    error_page = ErrorPage.not_found()
    spanish_title = f"{_('core.pages.index.prefix')}: {_('core.pages.not_found.title')}"
    spanish_content_title = _("core.pages.not_found.content_title")
    spanish_paragraphs = [_("core.pages.not_found.p[0]")]

    assert error_page.title != english_title
    assert error_page.content_title != english_content_title
    assert error_page.paragraphs != english_paragraphs

    assert error_page.title == spanish_title
    assert error_page.content_title == spanish_content_title
    assert error_page.paragraphs == spanish_paragraphs
