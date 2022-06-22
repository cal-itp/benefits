from benefits.logging import get_config


def test_get_config_no_azure():
    config = get_config()
    assert "azure" not in config["handlers"]
    assert "azure" not in config["loggers"]


def test_get_config_with_azure():
    config = get_config(enable_azure=True)
    assert "azure" in config["handlers"]
    assert "azure" in config["loggers"]
