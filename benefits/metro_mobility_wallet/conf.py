from django.conf import settings

EXTRA_LANGUAGES = [
    ("zh-hans", "Chinese simplified"),
    ("zh-hant", "Chinese traditional"),
    ("ko", "Korean"),
    ("ja", "Japanese"),
    ("vi", "Vietnamese"),
    ("th", "Thai"),
    ("ru", "Russian"),
    ("hy", "Armenian"),
]

# mirror naming of settings.LANGUAGES
LANGUAGES_METRO = list(settings.LANGUAGES) + EXTRA_LANGUAGES
