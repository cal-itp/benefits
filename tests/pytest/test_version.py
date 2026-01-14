import re


def test_version():
    from benefits import VERSION, __version__

    assert __version__ is not None
    assert __version__ == VERSION
    assert re.match(r"\d+\.\d+\..+", __version__)
