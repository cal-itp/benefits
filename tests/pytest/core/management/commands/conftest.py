import psycopg
import pytest


@pytest.fixture
def mock_psycopg_cursor(mocker):
    cursor = mocker.MagicMock(spec=psycopg.Cursor)
    cursor.fetchone.return_value = None
    cursor.close = mocker.MagicMock()
    return cursor


@pytest.fixture
def mock_admin_connection(mocker, mock_psycopg_cursor):
    connection = mocker.MagicMock(spec=psycopg.Connection)
    connection.cursor.return_value = mock_psycopg_cursor
    connection.closed = False

    def mock_close():
        connection.closed = True

    connection.close = mock_close
    return connection


@pytest.fixture
def mock_os_environ(mocker):
    env_dict = {}
    mocker.patch("os.environ", env_dict)
    return env_dict


@pytest.fixture
def mock_psycopg_connect(mocker):
    return mocker.patch("psycopg.connect")
