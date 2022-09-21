from django.utils import translation
from django.utils.translation import gettext as _
import pytest

from benefits.core.viewmodels import ErrorPage


@pytest.mark.parametrize(
    "error_page_function,title,content_title,paragraphs",
    [
        pytest.param(
            ErrorPage.server_error,
            "core.pages.server_error.title",
            "core.pages.server_error.title",
            ["core.pages.server_error.p[0]", "core.pages.server_error.p[1]"],
            id="server_error",
        ),
        pytest.param(
            ErrorPage.not_found,
            "core.pages.not_found.title",
            "core.pages.not_found.content_title",
            ["core.pages.not_found.p[0]"],
            id="not_found",
        ),
        pytest.param(
            ErrorPage.user_error,
            "core.pages.user_error.title",
            "core.pages.user_error.content_title",
            ["core.pages.user_error.p[0]"],
            id="user_error",
        ),
    ],
)
def test_ErrorPage_translations(error_page_function, title, content_title, paragraphs):
    translation.activate("en")

    error_page = error_page_function()
    english_title = f"{_('core.pages.index.prefix')}: {_(title)}"
    english_content_title = _(content_title)
    english_paragraphs = [_(paragraph) for paragraph in paragraphs]

    assert error_page.title == english_title
    assert error_page.content_title == english_content_title
    assert error_page.paragraphs == english_paragraphs

    translation.activate("es")

    error_page = error_page_function()
    spanish_title = f"{_('core.pages.index.prefix')}: {_(title)}"
    spanish_content_title = _(content_title)
    spanish_paragraphs = [_(paragraph) for paragraph in paragraphs]

    assert error_page.title != english_title
    assert error_page.content_title != english_content_title
    assert error_page.paragraphs != english_paragraphs

    assert error_page.title == spanish_title
    assert error_page.content_title == spanish_content_title
    assert error_page.paragraphs == spanish_paragraphs
