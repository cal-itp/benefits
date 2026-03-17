import psycopg
import pytest
from django.core.management.base import CommandError
from django.db import DEFAULT_DB_ALIAS
from psycopg import sql

from benefits.core.management.commands.ensure_db import Command

# ignore UserWarnings about modifying settings.DATABASE, the whole purpose of these tests!
pytestmark = pytest.mark.filterwarnings("ignore:Overriding setting DATABASES")

DB_TEST_ALIAS = "testdb"  # Define a clear alias for these tests


@pytest.fixture
def command(mocker):
    """Provides an instance of the Command, with stdout/stderr mocked."""
    cmd = Command()
    cmd.stdout.write = mocker.MagicMock()
    cmd.stderr.write = mocker.MagicMock()
    return cmd


@pytest.fixture
def mock_call_command(mocker):
    return mocker.patch("benefits.core.management.commands.ensure_db.call_command")


@pytest.fixture
def mock_get_user_model(mocker):
    MockUser = mocker.MagicMock()
    MockUser.objects.using(DEFAULT_DB_ALIAS).filter.return_value.exists.return_value = False
    return mocker.patch("benefits.core.management.commands.ensure_db.get_user_model", return_value=MockUser)


def test_admin_connection_success(command, mock_psycopg_connect, mock_admin_connection, mock_os_environ, settings):
    mock_psycopg_connect.return_value = mock_admin_connection
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "test_db_host",
            "PORT": "1234",
        }
    }
    mock_os_environ["POSTGRES_PASSWORD"] = "pg_super_secret"
    mock_os_environ["POSTGRES_USER"] = "pg_admin_user"
    mock_os_environ["POSTGRES_DB"] = "pg_maintenance_db"

    conn = command._admin_connection()

    mock_psycopg_connect.assert_called_once_with(
        host="test_db_host",
        port="1234",
        user="pg_admin_user",
        password="pg_super_secret",
        dbname="pg_maintenance_db",
        autocommit=True,
    )
    assert conn == mock_admin_connection


def test_admin_connection_no_postgres_password(command, mock_os_environ, settings):
    settings.DATABASES = {DEFAULT_DB_ALIAS: {"HOST": "db", "PORT": "5432"}}
    mock_os_environ.pop("POSTGRES_PASSWORD", None)

    with pytest.raises(
        CommandError, match="POSTGRES_PASSWORD environment variable not set. Cannot establish admin connection."
    ):
        command._admin_connection()


def test_admin_connection_psycopg_error(command, mock_psycopg_connect, mock_os_environ, settings):
    settings.DATABASES = {DEFAULT_DB_ALIAS: {"HOST": "db", "PORT": "5432"}}
    mock_os_environ["POSTGRES_PASSWORD"] = "pg_super_secret"
    mock_psycopg_connect.side_effect = psycopg.OperationalError("DB connection failed")

    with pytest.raises(CommandError, match="Admin connection to PostgreSQL failed: DB connection failed"):
        command._admin_connection()


def test_reset_success(command, mock_admin_connection, mock_psycopg_cursor, settings, mocker):
    """Test successful database reset."""
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"},
        "db2": {"ENGINE": "django.db.backends.postgresql", "NAME": "db2", "USER": "u2", "PASSWORD": "p2"},
        "other_db": {"ENGINE": "django.db.backends.sqlite3", "NAME": "other"},
    }
    mock_admin_connection.cursor.return_value = mock_psycopg_cursor
    mock_admin_connection.info.user = "admin"

    command._reset(mock_admin_connection)

    reassign_role = sql.SQL("REASSIGN OWNED BY {owned_by_role} TO {new_owner_role}")
    revoke_role = sql.SQL("REVOKE {role_to_revoke} FROM {grantee_admin}")
    drop_db = sql.SQL("DROP DATABASE IF EXISTS {db} WITH (FORCE)")
    drop_user = sql.SQL("DROP USER IF EXISTS {user}")

    calls = [
        mocker.call(reassign_role.format(owned_by_role=sql.Identifier("u1"), new_owner_role=sql.Identifier("admin"))),
        mocker.call(drop_db.format(db=sql.Identifier("db1"))),
        mocker.call(revoke_role.format(role_to_revoke=sql.Identifier("u1"), grantee_admin=sql.Identifier("admin"))),
        mocker.call(drop_user.format(user=sql.Identifier("u1"))),
        mocker.call(reassign_role.format(owned_by_role=sql.Identifier("u2"), new_owner_role=sql.Identifier("admin"))),
        mocker.call(drop_db.format(db=sql.Identifier("db2"))),
        mocker.call(revoke_role.format(role_to_revoke=sql.Identifier("u2"), grantee_admin=sql.Identifier("admin"))),
        mocker.call(drop_user.format(user=sql.Identifier("u2"))),
    ]
    mock_psycopg_cursor.execute.assert_has_calls(calls)


def test_reset_psycopg_error(command, mock_admin_connection, mock_psycopg_cursor, settings):
    """Test psycopg error during database reset."""
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"},
        "db2": {"ENGINE": "django.db.backends.postgresql", "NAME": "db2", "USER": "u2", "PASSWORD": "p2"},
        "other_db": {"ENGINE": "django.db.backends.sqlite3", "NAME": "other"},
    }
    mock_admin_connection.cursor.return_value = mock_psycopg_cursor
    mock_admin_connection.info.user = "admin"
    mock_psycopg_cursor.execute.side_effect = psycopg.Error()

    with pytest.raises(psycopg.Error) as e:
        command._reset(mock_admin_connection)
        command.stderr.write.assert_called_once_with(command.style.ERROR(f"Failed database reset for database db1: {e}"))


def test_validate_config_success(command):
    """Test _validate_config with valid PostgreSQL config."""
    db_alias = "postgres_db"
    valid_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_name",
        "USER": "test_user",
        "PASSWORD": "test_password",
    }
    expected_details = ("test_name", "test_user", "test_password")

    details = command._validate_config(db_alias, valid_config)

    assert details == expected_details


def test_validate_config_wrong_engine(command):
    """Test _validate_config skips non-PostgreSQL engine."""
    db_alias = "sqlite_db"
    invalid_config = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test_name",
    }

    details = command._validate_config(db_alias, invalid_config)

    assert details is None
    command.stdout.write.assert_called_once_with(
        command.style.WARNING(f"Skipping database {db_alias}, ENGINE is not PostgreSQL.")
    )


@pytest.mark.parametrize(
    "incomplete_config",
    [
        {
            "ENGINE": "django.db.backends.postgresql",
            # missing NAME
            "USER": "test_user",
            "PASSWORD": "test_password",
        },
        {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_name",
            # missing USER
            "PASSWORD": "test_password",
        },
        {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_name",
            "USER": "test_user",
            # missing PASSWORD
        },
    ],
)
def test_validate_config_incomplete(command, incomplete_config):
    """Test _validate_config skips incomplete config (missing NAME)."""
    db_alias = "incomplete_db"

    details = command._validate_config(db_alias, incomplete_config)

    assert details is None
    command.stderr.write.assert_called_once_with(
        command.style.ERROR(f"Skipping database {db_alias} with incomplete configuration (missing NAME, USER, or PASSWORD).")
    )


@pytest.mark.parametrize("user_exists", [False, True])
def test_user_exists(command, mock_psycopg_cursor, user_exists):
    test_username = "existing_user"
    mock_psycopg_cursor.fetchone.return_value = (1,) if user_exists else None

    result = command._user_exists(mock_psycopg_cursor, test_username)

    assert result is user_exists
    mock_psycopg_cursor.execute.assert_called_once_with(
        "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", [test_username]
    )


def test_create_database_user_success(command, mock_psycopg_cursor, mocker):
    admin_user = "admin_user"
    db_alias = "test_alias"
    test_username = "new_db_user"
    test_password = "secure_password"

    command._create_database_user(mock_psycopg_cursor, admin_user, db_alias, test_username, test_password)

    create_sql = sql.SQL("CREATE USER {user} WITH PASSWORD {password_literal}").format(
        user=sql.Identifier(test_username), password_literal=sql.Literal(test_password)
    )
    grant_sql = sql.SQL("GRANT {user} TO {admin}").format(user=sql.Identifier(test_username), admin=sql.Identifier(admin_user))

    calls = [mocker.call(create_sql), mocker.call(grant_sql)]
    mock_psycopg_cursor.execute.assert_has_calls(calls)


def test_create_database_user_failure(command, mock_psycopg_cursor):
    admin_user = "admin_user"
    db_alias = "fail_alias"
    test_username = "doomed_user"
    test_password = "bad_password"
    db_error = psycopg.ProgrammingError("Test DB creation error")
    mock_psycopg_cursor.execute.side_effect = db_error

    with pytest.raises(psycopg.ProgrammingError, match="Test DB creation error"):
        command._create_database_user(mock_psycopg_cursor, admin_user, db_alias, test_username, test_password)

    expected_sql = sql.SQL("CREATE USER {user} WITH PASSWORD {password_literal}").format(
        user=sql.Identifier(test_username), password_literal=sql.Literal(test_password)
    )
    mock_psycopg_cursor.execute.assert_called_once_with(expected_sql)

    command.stdout.write.assert_any_call(f"User: {test_username} for database: {db_alias} not found. Creating...")
    command.stderr.write.assert_any_call(
        command.style.ERROR(f"Failed to create user {test_username} for database {db_alias}: {db_error}")
    )


@pytest.mark.parametrize("db_exists", [True, False])
def test_database_exists(command, mock_psycopg_cursor, db_exists):
    """Test _database_exists when database is found."""
    test_dbname = "existing_db"
    mock_psycopg_cursor.fetchone.return_value = (1,) if db_exists else None

    result = command._database_exists(mock_psycopg_cursor, test_dbname)

    assert result is db_exists
    mock_psycopg_cursor.execute.assert_called_once_with("SELECT 1 FROM pg_database WHERE datname = %s", [test_dbname])


def test_create_database_success(command, mock_psycopg_cursor, mocker):
    """Test _create_database successfully creates a database."""
    db_alias = "test_db_alias"
    test_dbname = "new_db"
    test_owner = "db_owner"

    # Mock the internal call to _user_exists within _create_database to simulate owner exists
    mocker.patch.object(command, "_user_exists", return_value=True)

    command._create_database(mock_psycopg_cursor, db_alias, test_dbname, test_owner)

    command._user_exists.assert_called_once_with(mock_psycopg_cursor, test_owner)

    expected_sql = sql.SQL("CREATE DATABASE {db} WITH OWNER {owner} ENCODING {encoding}").format(
        db=sql.Identifier(test_dbname),
        owner=sql.Identifier(test_owner),
        encoding=sql.Literal("UTF-8"),
    )
    mock_psycopg_cursor.execute.assert_called_once_with(expected_sql)


def test_create_database_owner_does_not_exist(command, mock_psycopg_cursor, mocker):
    """_create_database fails with CommandError if the owner does not exist."""
    db_alias = "test_db_alias_fail"
    test_dbname = "another_new_db"
    test_owner = "non_existent_owner"

    # Mock _user_exists to return False for the owner check
    mocker.patch.object(command, "_user_exists", return_value=False)
    # Keep a reference to the original execute mock to check it wasn't called for CREATE DB
    original_execute_mock = mock_psycopg_cursor.execute

    with pytest.raises(
        CommandError, match=f"Owner user {test_owner} for database {test_dbname} not found during database creation."
    ):
        command._create_database(mock_psycopg_cursor, db_alias, test_dbname, test_owner)

    command._user_exists.assert_called_once_with(mock_psycopg_cursor, test_owner)

    # Ensure CREATE DATABASE was not attempted by checking the calls to the cursor's execute
    for call_obj in original_execute_mock.call_args_list:
        if isinstance(call_obj.args[0], sql.SQL) and "CREATE DATABASE" in str(call_obj.args[0]):
            pytest.fail("CREATE DATABASE should not have been called when owner is missing")

    command.stdout.write.assert_any_call(f"Database {test_dbname} not found. Creating...")
    command.stderr.write.assert_any_call(
        command.style.ERROR(
            f"Cannot create database: {test_dbname} because user: {test_owner} does not exist or was not created"
        )
    )


def test_create_database_db_creation_psycopg_error(command, mock_psycopg_cursor, mocker):
    """Test _create_database propagates psycopg error during DB creation."""
    db_alias = "test_db_alias_psycopg_fail"
    test_dbname = "fail_creation_db"
    test_owner = "owner_for_fail_db"
    db_error = psycopg.ProgrammingError("DB creation system error")

    mocker.patch.object(command, "_user_exists", return_value=True)  # Owner exists
    # Mock the execute call that attempts to create the database to raise an error
    mock_psycopg_cursor.execute.side_effect = db_error

    with pytest.raises(psycopg.ProgrammingError, match="DB creation system error"):
        command._create_database(mock_psycopg_cursor, db_alias, test_dbname, test_owner)

    command._user_exists.assert_called_once_with(mock_psycopg_cursor, test_owner)
    # The failing call to execute should be the CREATE DATABASE one
    expected_sql = sql.SQL("CREATE DATABASE {db} WITH OWNER {owner} ENCODING {encoding}").format(
        db=sql.Identifier(test_dbname), owner=sql.Identifier(test_owner), encoding=sql.Literal("UTF-8")
    )
    mock_psycopg_cursor.execute.assert_called_once_with(expected_sql)

    command.stdout.write.assert_any_call(f"Database {test_dbname} not found. Creating...")
    command.stderr.write.assert_any_call(
        command.style.ERROR(f"Failed to create database {test_dbname} for alias {db_alias}: {db_error}")
    )


def test_ensure_schema_permissions_success(command, mock_admin_connection, mocker):
    """Test successful schema permission grant."""
    db_name = "test_db"
    db_user = "test_user"
    mocker.patch.object(command, "_admin_connection", return_value=mock_admin_connection)
    mock_cursor = command._admin_connection.return_value.cursor.return_value.__enter__.return_value

    command._ensure_schema_permissions(db_name, db_user)

    # Verify admin connection was made with correct database
    command._admin_connection.assert_called_once_with(db_name)

    # Verify grant query was executed with correct SQL
    expected_sql = sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {user}").format(user=sql.Identifier(db_user))
    mock_cursor.execute.assert_called_once_with(expected_sql)

    # Verify connection was closed
    assert mock_admin_connection.closed is True


def test_ensure_schema_permissions_psycopg_error(command, mock_admin_connection, mocker):
    """Test handling of psycopg error during schema permission grant."""
    db_name = "error_db"
    db_user = "error_user"
    mocker.patch.object(command, "_admin_connection", return_value=mock_admin_connection)
    mock_cursor = command._admin_connection.return_value.cursor.return_value.__enter__.return_value

    # Set up the cursor to raise an error
    mock_cursor.execute.side_effect = psycopg.Error()

    with pytest.raises(CommandError, match=f"Failed to set schema permissions for newly created database: {db_name}."):
        command._ensure_schema_permissions(db_name, db_user)

    # Verify connection was closed even after error
    assert mock_admin_connection.closed


def test_ensure_schema_permissions_admin_connection_failure(command, mocker):
    """Test handling of admin connection failure."""
    db_name = "nonexistent_db"
    db_user = "some_user"

    # Mock _admin_connection to raise an error
    mocker.patch.object(command, "_admin_connection", side_effect=CommandError())

    with pytest.raises(CommandError):
        command._ensure_schema_permissions(db_name, db_user)

    command._admin_connection.assert_called_once_with(db_name)


def test_ensure_users_and_db_creates_new_user_and_db(command, mock_admin_connection, mock_psycopg_cursor, settings, mocker):
    admin_user = "admin_user"
    db_name_val = "example_db"
    db_user_val = "example_user"
    db_password_val = "example_password"
    db_config_dict = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name_val,
        "USER": db_user_val,
        "PASSWORD": db_password_val,
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config_dict}

    # Mock helper methods
    mocker.patch.object(command, "_validate_config", return_value=(db_name_val, db_user_val, db_password_val))
    mocker.patch.object(command, "_user_exists", return_value=False)  # User does not exist
    mock_create_user = mocker.patch.object(command, "_create_database_user")
    mocker.patch.object(command, "_database_exists", return_value=False)  # Database does not exist
    mock_create_db = mocker.patch.object(command, "_create_database")
    mock_ensure_schema_permissions = mocker.patch.object(command, "_ensure_schema_permissions")
    mock_admin_connection.info.user = admin_user

    command._ensure_users_and_db(mock_admin_connection)

    # Verify calls to helpers
    command._validate_config.assert_called_once_with(DB_TEST_ALIAS, db_config_dict)
    command._user_exists.assert_called_once_with(mock_psycopg_cursor, db_user_val)
    mock_create_user.assert_called_once_with(mock_psycopg_cursor, admin_user, DB_TEST_ALIAS, db_user_val, db_password_val)
    command._database_exists.assert_called_once_with(mock_psycopg_cursor, db_name_val)
    mock_create_db.assert_called_once_with(mock_psycopg_cursor, DB_TEST_ALIAS, db_name_val, db_user_val)
    mock_ensure_schema_permissions.assert_called_once_with(db_name_val, db_user_val)

    mock_psycopg_cursor.close.assert_called_once()


def test_ensure_users_and_db_user_exists_db_not_exists(command, mock_admin_connection, mock_psycopg_cursor, settings, mocker):
    db_name_val = "another_example_db"
    db_user_val = "current_user"
    db_password_val = "pwd123"
    db_config_dict = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name_val,
        "USER": db_user_val,
        "PASSWORD": db_password_val,
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config_dict}

    mocker.patch.object(command, "_validate_config", return_value=(db_name_val, db_user_val, db_password_val))
    mocker.patch.object(command, "_user_exists", return_value=True)  # User exists
    mock_create_user = mocker.patch.object(command, "_create_database_user")
    mocker.patch.object(command, "_database_exists", return_value=False)  # DB does not exist
    mock_create_db = mocker.patch.object(command, "_create_database")
    mock_ensure_schema_permissions = mocker.patch.object(command, "_ensure_schema_permissions")

    command._ensure_users_and_db(mock_admin_connection)

    command._validate_config.assert_called_once_with(DB_TEST_ALIAS, db_config_dict)
    command._user_exists.assert_called_once_with(mock_psycopg_cursor, db_user_val)
    mock_create_user.assert_not_called()
    command._database_exists.assert_called_once_with(mock_psycopg_cursor, db_name_val)
    mock_create_db.assert_called_once_with(mock_psycopg_cursor, DB_TEST_ALIAS, db_name_val, db_user_val)
    mock_ensure_schema_permissions.assert_called_once_with(db_name_val, db_user_val)


def test_ensure_users_and_db_skips_non_postgres(command, mock_admin_connection, mock_psycopg_cursor, settings):
    db_alias_sqlite = "sqlite_db"
    settings.DATABASES = {
        DB_TEST_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"},
        db_alias_sqlite: {"ENGINE": "django.db.backends.sqlite3", "NAME": "test.db"},
    }
    mock_psycopg_cursor.fetchone.return_value = (1,)  # Assume PG db and user exist

    command._ensure_users_and_db(mock_admin_connection)

    command.stdout.write.assert_any_call(
        command.style.WARNING(f"Skipping database {db_alias_sqlite}, ENGINE is not PostgreSQL.")
    )


def test_ensure_users_and_db_incomplete_config(command, mock_admin_connection, settings, mocker):
    db_config_incomplete = {"ENGINE": "django.db.backends.postgresql", "NAME": "db1"}
    settings.DATABASES = {DB_TEST_ALIAS: db_config_incomplete}

    def validate_side_effect(alias, config):
        return None

    mock_validate = mocker.patch.object(command, "_validate_config", side_effect=validate_side_effect)
    mock_user_exists = mocker.patch.object(command, "_user_exists")
    mock_database_exists = mocker.patch.object(command, "_database_exists")

    command._ensure_users_and_db(mock_admin_connection)

    mock_validate.assert_called_once_with(DB_TEST_ALIAS, db_config_incomplete)
    mock_user_exists.assert_not_called()
    mock_database_exists.assert_not_called()


def test_ensure_users_and_db_user_creation_fails(command, mocker, mock_admin_connection, mock_psycopg_cursor, settings):
    admin_user = "admin_user"
    db_name_val = "fail_db"
    db_user_val = "fail_user"
    db_password_val = "fp"
    db_config_dict = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name_val,
        "USER": db_user_val,
        "PASSWORD": db_password_val,
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config_dict}

    mocker.patch.object(command, "_validate_config", return_value=(db_name_val, db_user_val, db_password_val))
    mocker.patch.object(command, "_user_exists", return_value=False)
    mock_create_user = mocker.patch.object(command, "_create_database_user", side_effect=psycopg.ProgrammingError())
    mock_database_exists = mocker.patch.object(command, "_database_exists")
    mock_admin_connection.info.user = admin_user

    with pytest.raises(psycopg.ProgrammingError):
        command._ensure_users_and_db(mock_admin_connection)

    command._validate_config.assert_called_once_with(DB_TEST_ALIAS, db_config_dict)
    command._user_exists.assert_called_once_with(mock_psycopg_cursor, db_user_val)
    mock_create_user.assert_called_once_with(mock_psycopg_cursor, admin_user, DB_TEST_ALIAS, db_user_val, db_password_val)
    mock_database_exists.assert_not_called()


def test_ensure_users_and_db_creation_fails_owner_missing(
    command, mock_admin_connection, mock_psycopg_cursor, settings, mocker
):
    db_name_val = "ownerless_db"
    db_user_val = "ghost_user"
    db_password_val = "gp"
    db_config_dict = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name_val,
        "USER": db_user_val,
        "PASSWORD": db_password_val,
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config_dict}

    mocker.patch.object(command, "_validate_config", return_value=(db_name_val, db_user_val, db_password_val))
    mocker.patch.object(command, "_user_exists", return_value=True)  # Initial user check is fine
    mock_create_user = mocker.patch.object(command, "_create_database_user")
    mocker.patch.object(command, "_database_exists", return_value=False)  # DB needs creation
    mock_create_db = mocker.patch.object(command, "_create_database", side_effect=CommandError())

    with pytest.raises(CommandError):
        command._ensure_users_and_db(mock_admin_connection)

    command._validate_config.assert_called_once_with(DB_TEST_ALIAS, db_config_dict)
    command._user_exists.assert_called_once_with(mock_psycopg_cursor, db_user_val)
    mock_create_user.assert_not_called()
    command._database_exists.assert_called_once_with(mock_psycopg_cursor, db_name_val)
    mock_create_db.assert_called_once_with(mock_psycopg_cursor, DB_TEST_ALIAS, db_name_val, db_user_val)


def test_ensure_users_and_db_user_and_db_already_exist(command, mock_admin_connection, mock_psycopg_cursor, settings, mocker):
    db_name_val = "existing_db"
    db_user_val = "existing_user"
    db_password_val = "existing_pass"
    db_config_dict = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name_val,
        "USER": db_user_val,
        "PASSWORD": db_password_val,
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config_dict}

    mocker.patch.object(command, "_validate_config", return_value=(db_name_val, db_user_val, db_password_val))
    mocker.patch.object(command, "_user_exists", return_value=True)  # User exists
    mock_create_user = mocker.patch.object(command, "_create_database_user")
    mocker.patch.object(command, "_database_exists", return_value=True)  # Database exists
    mock_create_db = mocker.patch.object(command, "_create_database")

    command._ensure_users_and_db(mock_admin_connection)

    command._validate_config.assert_called_once_with(DB_TEST_ALIAS, db_config_dict)
    command._user_exists.assert_called_once_with(mock_psycopg_cursor, db_user_val)
    mock_create_user.assert_not_called()
    command._database_exists.assert_called_once_with(mock_psycopg_cursor, db_name_val)
    mock_create_db.assert_not_called()

    command.stdout.write.assert_any_call(f"User found: {db_user_val}")
    command.stdout.write.assert_any_call(f"Database found: {db_name_val}")
    mock_psycopg_cursor.close.assert_called_once()


def test_run_migrations_success(command, mock_call_command, settings):
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"}
    }

    command._run_migrations()

    mock_call_command.assert_any_call("migrate", database=DEFAULT_DB_ALIAS, interactive=False)
    mock_call_command.assert_any_call("createcachetable")
    command.stdout.write.assert_any_call(command.style.SUCCESS(f"Migrations complete for database: {DEFAULT_DB_ALIAS}"))


def test_run_migrations_multiple_dbs(command, mock_call_command, settings):
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"},
        "tasks_db": {"ENGINE": "django.db.backends.postgresql", "NAME": "tasks", "USER": "u2", "PASSWORD": "p2"},
        "other_db": {"ENGINE": "django.db.backends.sqlite3", "NAME": "other"},
    }

    command._run_migrations()

    assert mock_call_command.call_count == 3
    mock_call_command.assert_any_call("migrate", database=DEFAULT_DB_ALIAS, interactive=False)
    mock_call_command.assert_any_call("migrate", database="tasks_db", interactive=False)
    mock_call_command.assert_any_call("createcachetable")
    command.stdout.write.assert_any_call(
        command.style.WARNING("Skipping migrations for database: other_db. ENGINE is not PostgreSQL.")
    )


def test_run_migrations_failure_raises_commanderror(command, mock_call_command, settings):
    db_alias_fail = DEFAULT_DB_ALIAS
    settings.DATABASES = {
        db_alias_fail: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"}
    }
    error_obj = Exception("Migration critical failure!")
    mock_call_command.side_effect = error_obj

    with pytest.raises(CommandError, match=f"Migration failed for {db_alias_fail}."):
        command._run_migrations()


def test_ensure_superuser_creates_if_not_exists(command, mock_os_environ, mock_get_user_model, mock_call_command):
    username = "new_super_user"
    email = "new_super@example.com"
    mock_os_environ["DJANGO_SUPERUSER_USERNAME"] = username
    mock_os_environ["DJANGO_SUPERUSER_EMAIL"] = email
    mock_os_environ["DJANGO_SUPERUSER_PASSWORD"] = "super_password123"

    command._ensure_superuser()

    mock_get_user_model.return_value.objects.using(DEFAULT_DB_ALIAS).filter(username=username).exists.assert_called_once()
    mock_call_command.assert_called_once_with("createsuperuser", interactive=False, username=username, email=email)


def test_ensure_superuser_already_exists(command, mock_os_environ, mock_get_user_model, mock_call_command):
    username = "current_super_user"
    mock_os_environ["DJANGO_SUPERUSER_USERNAME"] = username
    mock_get_user_model.return_value.objects.using(DEFAULT_DB_ALIAS).filter(username=username).exists.return_value = True

    command._ensure_superuser()

    command.stdout.write.assert_any_call(f"Superuser: {username} already exists in database: {DEFAULT_DB_ALIAS}")
    mock_call_command.assert_not_called()


@pytest.mark.usefixtures("mock_os_environ")
def test_ensure_superuser_username_not_set(command, mock_call_command):
    command._ensure_superuser()

    command.stdout.write.assert_any_call(
        "DJANGO_SUPERUSER_USERNAME environment variable not set. Skipping superuser creation."
    )
    mock_call_command.assert_not_called()


@pytest.mark.usefixtures("mock_get_user_model")
def test_ensure_superuser_creation_missing_email_env_var(command, mock_os_environ, mock_call_command):
    # mock_get_user_model has exists() returning False
    username = "incomplete_super"
    mock_os_environ["DJANGO_SUPERUSER_USERNAME"] = username
    mock_os_environ["DJANGO_SUPERUSER_PASSWORD"] = "super_password123"

    command._ensure_superuser()

    command.stdout.write.assert_any_call(
        command.style.WARNING(
            f"Cannot create superuser: {username}. DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD environment variables are not set."  # noqa: E501
        )
    )
    mock_call_command.assert_not_called()


def test_add_arguments(command, mocker):
    mock_parser = mocker.Mock()

    command.add_arguments(mock_parser)

    mock_parser.add_argument.assert_called_once_with(
        "--reset", action="store_true", help="Completely reset the database(s) (DESTRUCTIVE)."
    )


@pytest.mark.parametrize("reset", [True, False])
def test_handle_success(command, mocker, mock_admin_connection, reset):
    mocker.patch.object(command, "_admin_connection", return_value=mock_admin_connection)
    mocker.patch.object(command, "_reset")
    mocker.patch.object(command, "_ensure_users_and_db")
    mocker.patch.object(command, "_run_migrations")
    mocker.patch.object(command, "_ensure_superuser")

    command.handle(reset=reset)

    command._admin_connection.assert_called_once()
    command._ensure_users_and_db.assert_called_once_with(mock_admin_connection)
    command._run_migrations.assert_called_once()
    command._ensure_superuser.assert_called_once()
    assert mock_admin_connection.closed
    command.stdout.write.assert_any_call(command.style.SUCCESS("ensure_db command finished successfully."))

    if reset:
        command._reset.assert_called_once_with(mock_admin_connection)
    else:
        command._reset.assert_not_called()


def test_handle_admin_connection_fails(command, mocker):
    admin_connect_error_msg = "Admin connection totally failed"
    mocker.patch.object(command, "_admin_connection", side_effect=CommandError(admin_connect_error_msg))
    mock_ensure_users_db = mocker.patch.object(command, "_ensure_users_and_db")
    mock_migrations = mocker.patch.object(command, "_run_migrations")
    mock_superuser = mocker.patch.object(command, "_ensure_superuser")

    command.handle()

    command._admin_connection.assert_called_once()
    command.stderr.write.assert_any_call(command.style.ERROR(admin_connect_error_msg))
    mock_ensure_users_db.assert_not_called()
    mock_migrations.assert_not_called()
    mock_superuser.assert_not_called()


def test_handle_run_migrations_fails(command, mock_admin_connection, mocker):
    mocker.patch.object(command, "_admin_connection", return_value=mock_admin_connection)
    mocker.patch.object(command, "_ensure_users_and_db")
    mocker.patch.object(command, "_run_migrations", side_effect=Exception())
    mocker.patch.object(command, "_ensure_superuser")

    with pytest.raises(Exception):
        command.handle()

    command._ensure_superuser.assert_not_called()
    assert mock_admin_connection.closed
