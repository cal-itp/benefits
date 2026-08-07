from datetime import datetime

import pytest
from django.utils.formats import date_format

from benefits.locale.en.formats import DATE_FORMAT as DATE_FORMAT_EN
from benefits.locale.es.formats import DATE_FORMAT as DATE_FORMAT_ES


@pytest.fixture
def date_december():
    return datetime(2024, 12, 1)


@pytest.fixture
def date_march():
    return datetime(2024, 3, 1)


def test_en_DATE_FORMAT_december(date_december):
    assert date_format(date_december, DATE_FORMAT_EN) == "December 1, 2024"


def test_en_DATE_FORMAT_march(date_march):
    assert date_format(date_march, DATE_FORMAT_EN) == "March 1, 2024"


def test_es_DATE_FORMAT_december(settings, date_december):
    settings.LANGUAGE_CODE = "es"
    assert date_format(date_december, DATE_FORMAT_ES) == "1 de diciembre de 2024"


def test_es_DATE_FORMAT_march(settings, date_march):
    settings.LANGUAGE_CODE = "es"
    assert date_format(date_march, DATE_FORMAT_ES) == "1 de marzo de 2024"
