import re


def test_version():
    from benefits import __version__, VERSION

    assert __version__ is not None
    assert __version__ == VERSION
    assert re.match(r"\d+\.\d+\..+", __version__)
