def test_runtime_environment__default(settings):
    assert settings.RUNTIME_ENVIRONMENT() == "local"


def test_runtime_environment__dev(settings):
    settings.ALLOWED_HOSTS = ["dev-benefits.calitp.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "dev"


def test_runtime_environment__dev_and_test(settings):
    # if both dev and test are specified (edge case/error in configuration), assume dev
    settings.ALLOWED_HOSTS = ["test-benefits.calitp.org", "dev-benefits.calitp.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "dev"


def test_runtime_environment__dev_and_test_and_prod(settings):
    # if all 3 of dev and test and prod are specified (edge case/error in configuration), assume dev
    settings.ALLOWED_HOSTS = ["benefits.calitp.org", "test-benefits.calitp.org", "dev-benefits.calitp.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "dev"


def test_runtime_environment__local(settings):
    settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    assert settings.RUNTIME_ENVIRONMENT() == "local"


def test_runtime_environment__nonmatching(settings):
    # with only nonmatching hosts, return local
    settings.ALLOWED_HOSTS = ["example.com", "example2.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "local"


def test_runtime_environment__test(settings):
    settings.ALLOWED_HOSTS = ["test-benefits.calitp.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "test"


def test_runtime_environment__test_and_nonmatching(settings):
    # when test is specified with other nonmatching hosts, assume test
    settings.ALLOWED_HOSTS = ["test-benefits.calitp.org", "example.com"]
    assert settings.RUNTIME_ENVIRONMENT() == "test"


def test_runtime_environment__test_and_prod(settings):
    # if both test and prod are specified (edge case/error in configuration), assume test
    settings.ALLOWED_HOSTS = ["benefits.calitp.org", "test-benefits.calitp.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "test"


def test_runtime_environment__prod(settings):
    settings.ALLOWED_HOSTS = ["benefits.calitp.org"]
    assert settings.RUNTIME_ENVIRONMENT() == "prod"


def test_runtime_environment__prod_and_nonmatching(settings):
    # when prod is specified with other nonmatching hosts, assume prod
    settings.ALLOWED_HOSTS = ["benefits.calitp.org", "https://example.com"]
    assert settings.RUNTIME_ENVIRONMENT() == "prod"
