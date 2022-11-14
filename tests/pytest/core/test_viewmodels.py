from django.utils import translation
from django.utils.translation import gettext as _
import pytest

from benefits.core.viewmodels import ErrorPage


@pytest.mark.parametrize(
    "error_page_function,title,headline,paragraphs",
    [
        pytest.param(
            ErrorPage.server_error,
            "core.pages.server_error.title",
            "core.pages.server_error.title",
            ["core.pages.server_error.p[0]"],
            id="server_error",
        ),
        pytest.param(
            ErrorPage.not_found,
            "core.pages.not_found.title",
            "core.pages.not_found.headline",
            ["core.pages.not_found.p[0]"],
            id="not_found",
        ),
        pytest.param(
            ErrorPage.user_error,
            "core.pages.user_error.title",
            "core.pages.user_error.headline",
            ["core.pages.user_error.p[0]"],
            id="user_error",
        ),
    ],
)
def test_ErrorPage_translations(error_page_function, title, headline, paragraphs):
    translation.activate("en")

    error_page = error_page_function()
    english_title = _(title)
    english_headline = _(headline)
    english_paragraphs = [_(paragraph) for paragraph in paragraphs]

    assert error_page.title == english_title
    assert error_page.headline == english_headline
    assert error_page.paragraphs == english_paragraphs

    translation.activate("es")

    error_page = error_page_function()
    spanish_title = _(title)
    spanish_headline = _(headline)
    spanish_paragraphs = [_(paragraph) for paragraph in paragraphs]

    assert error_page.title != english_title
    assert error_page.headline != english_headline
    assert error_page.paragraphs != english_paragraphs

    assert error_page.title == spanish_title
    assert error_page.headline == spanish_headline
    assert error_page.paragraphs == spanish_paragraphs
