import pytest
from django.utils import translation
from django.utils.decorators import decorator_from_middleware

from benefits.core.middleware import ResetUnsupportedLanguage


@pytest.fixture
def decorated_view(mocked_view):
    return decorator_from_middleware(ResetUnsupportedLanguage)(mocked_view)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path, initial_lang, expected_lang, should_reset",
    [
        ("/benefits/eligibility/", "ko", "en", True),
        ("/benefits/eligibility/", "es", "es", False),
        ("/metro-mobility-wallet/", "ko", "ko", False),
    ],
)
def test_reset_unsupported_language(
    app_request, mocked_view, decorated_view, settings, path, initial_lang, expected_lang, should_reset
):
    settings.LANGUAGES_CORE = [("en", "English"), ("es", "Español")]
    settings.LANGUAGE_CODE = "en"
    app_request.path = path
    translation.activate(initial_lang)

    decorated_view(app_request)

    # ensure the (decorated) mocked view was called
    mocked_view.assert_called_once()

    assert translation.get_language() == expected_lang

    if should_reset:
        assert app_request.LANGUAGE_CODE == settings.LANGUAGE_CODE

    translation.deactivate()
