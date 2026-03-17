import os

import psycopg
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from psycopg import Connection, sql


class Command(BaseCommand):
    help = (
        "Ensures databases and their users exist, runs migrations, "
        "and creates a superuser if specified by environment variables and not already present."
    )

    def _admin_connection(self, database=None):
        # Try to get HOST/PORT from the default database settings first
        # Fallback to environment variables if not found in settings
        default_db_settings = settings.DATABASES.get(DEFAULT_DB_ALIAS, {})
        db_host = default_db_settings.get("HOST")
        db_port = default_db_settings.get("PORT")

        postgres_maintenance_db = os.environ.get("POSTGRES_DB", "postgres")
        target_db = database or postgres_maintenance_db
        admin_user = os.environ.get("POSTGRES_USER", "postgres")
        admin_password = os.environ.get("POSTGRES_PASSWORD")

        if not admin_password:
            raise CommandError("POSTGRES_PASSWORD environment variable not set. Cannot establish admin connection.")

        self.stdout.write(f"Attempting admin connection as user: {admin_user} to database: {target_db}")
        try:
            conn = psycopg.connect(
                host=db_host,
                port=db_port,
                user=admin_user,
                password=admin_password,
                dbname=target_db,
                autocommit=True,  # Ensure commands are executed immediately
            )
            return conn
        except psycopg.Error as e:
            raise CommandError(f"Admin connection to PostgreSQL failed: {e}") from e

    def _reset(self, admin_conn: Connection):
        self.stdout.write(self.style.WARNING("Resetting database users and databases..."))
        cursor = admin_conn.cursor()
        # This is the role executing this _reset method (e.g. 'postgres')
        admin_user = admin_conn.info.user
        try:
            for db_alias, db_config in settings.DATABASES.items():
                validated_config = self._validate_config(db_alias, db_config)
                if not validated_config:
                    continue  # Skip this alias if validation failed

                db_name, db_user, _ = validated_config  # db_user is the app user, e.g. 'django'
                try:
                    self.stdout.write(f"Preparing to reset {db_user} and {db_name}...")

                    # 1. Attempt to transfer ownership of any objects owned by db_user to admin_user.
                    #    This allows admin_user (if not full superuser) to drop databases owned by db_user.
                    #    If db_user does not exist, psycopg.errors.UndefinedObject will be raised.
                    #    We catch this and pass, as there would be no objects to reassign.
                    try:
                        reassign_query = sql.SQL("REASSIGN OWNED BY {owned_by_role} TO {new_owner_role}").format(
                            owned_by_role=sql.Identifier(db_user), new_owner_role=sql.Identifier(admin_user)
                        )
                        cursor.execute(reassign_query)
                    except psycopg.errors.UndefinedObject:
                        # If db_user doesn't exist, there's nothing to reassign. Pass silently.
                        pass

                    # 2. Drop the database
                    # If REASSIGN OWNED was successful and db_user owned it, admin_user is now the owner.
                    drop_db_query = sql.SQL("DROP DATABASE IF EXISTS {db} WITH (FORCE)").format(db=sql.Identifier(db_name))
                    cursor.execute(drop_db_query)
                    self.stdout.write(f"Database {db_name} dropped.")

                    # 3. Revoke the app role from the admin role to break membership
                    try:
                        revoke_query = sql.SQL("REVOKE {role_to_revoke} FROM {grantee_admin}").format(
                            role_to_revoke=sql.Identifier(db_user), grantee_admin=sql.Identifier(admin_user)
                        )
                        cursor.execute(revoke_query)
                    except psycopg.errors.UndefinedObject:
                        # Expected if db_user (app_role) or admin_user doesn't exist.
                        pass

                    # 4. Drop the role
                    drop_role_query = sql.SQL("DROP USER IF EXISTS {user}").format(user=sql.Identifier(db_user))
                    cursor.execute(drop_role_query)
                    self.stdout.write(f"Role {db_user} dropped.")
                    self.stdout.write(self.style.SUCCESS(f"Database {db_name} and role {db_user} reset successfully."))
                except psycopg.Error as e:
                    self.stderr.write(self.style.ERROR(f"Failed database reset for database {db_alias}: {e}"))
                    if hasattr(e, "diag") and e.diag and e.diag.message_detail:
                        self.stderr.write(self.style.ERROR(f"DETAIL: {e.diag.message_detail}"))
                    raise

        finally:
            if cursor:
                cursor.close()

    def _validate_config(self, db_alias: str, db_config: dict) -> tuple[str, str, str] | None:
        """
        Validates the database configuration for PostgreSQL engine and completeness.
        Returns (db_name, db_user, db_password) or None if validation fails.
        """
        if db_config.get("ENGINE") != "django.db.backends.postgresql":
            self.stdout.write(self.style.WARNING(f"Skipping database {db_alias}, ENGINE is not PostgreSQL."))
            return None

        db_name = db_config.get("NAME")
        db_user = db_config.get("USER")
        db_password = db_config.get("PASSWORD")

        if not all([db_name, db_user, db_password]):
            self.stderr.write(
                self.style.ERROR(
                    f"Skipping database {db_alias} with incomplete configuration (missing NAME, USER, or PASSWORD)."
                )
            )
            return None
        return db_name, db_user, db_password

    def _user_exists(self, cursor: psycopg.Cursor, username: str) -> bool:
        """Checks if a PostgreSQL user exists."""
        cursor.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", [username])
        return cursor.fetchone() is not None

    def _create_database_user(self, cursor: psycopg.Cursor, admin_user: str, db_alias: str, username: str, password: str):
        """Creates a PostgreSQL user."""
        self.stdout.write(f"User: {username} for database: {db_alias} not found. Creating...")
        try:
            # Use sql.Literal for the password to ensure it's correctly quoted
            query = sql.SQL("CREATE USER {user} WITH PASSWORD {password_literal}").format(
                user=sql.Identifier(username), password_literal=sql.Literal(password)
            )
            cursor.execute(query)
            # grant the specific username role to the admin_user
            # to allow the admin_user to create database(s) on behalf of the db_user
            query = sql.SQL("GRANT {user} TO {admin}").format(user=sql.Identifier(username), admin=sql.Identifier(admin_user))
            cursor.execute(query)
            self.stdout.write(self.style.SUCCESS("User created successfully"))
        except psycopg.Error as e:
            self.stderr.write(self.style.ERROR(f"Failed to create user {username} for database {db_alias}: {e}"))
            raise

    def _database_exists(self, cursor: psycopg.Cursor, db_name: str) -> bool:
        """Checks if a PostgreSQL database exists."""
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [db_name])
        return cursor.fetchone() is not None

    def _create_database(self, cursor: psycopg.Cursor, db_alias: str, db_name: str, owner_username: str):
        """Creates a PostgreSQL database with the specified owner."""
        self.stdout.write(f"Database {db_name} not found. Creating...")
        # Ensure owner exists before attempting to create the database
        if not self._user_exists(cursor, owner_username):
            self.stderr.write(
                self.style.ERROR(
                    f"Cannot create database: {db_name} because user: {owner_username} does not exist or was not created"
                )
            )
            raise CommandError(f"Owner user {owner_username} for database {db_name} not found during database creation.")
        try:
            # Use sql.Literal for the password to ensure it's correctly quoted
            query = sql.SQL("CREATE DATABASE {db} WITH OWNER {owner} ENCODING {encoding}").format(
                db=sql.Identifier(db_name),
                owner=sql.Identifier(owner_username),
                encoding=sql.Literal("UTF-8"),
            )
            cursor.execute(query)
            self.stdout.write(self.style.SUCCESS("Database created successfully"))
        except psycopg.Error as e:
            self.stderr.write(self.style.ERROR(f"Failed to create database {db_name} for alias {db_alias}: {e}"))
            raise

    def _ensure_schema_permissions(self, db_name: str, db_user_to_grant: str):
        """
        Grants USAGE and CREATE permissions on the public schema of a newly created database to the specified user.
        Connects to the target database using admin credentials. Failure is considered critical as it's for a new database.
        """
        self.stdout.write(f"Ensuring schema permissions for user: {db_user_to_grant} in database: {db_name}")
        admin_conn = None
        try:
            admin_conn = self._admin_connection(db_name)
            with admin_conn.cursor() as cursor:
                grant_query = sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {user}").format(
                    user=sql.Identifier(db_user_to_grant)
                )
                cursor.execute(grant_query)
                self.stdout.write("Schema permissions confirmed")
        except psycopg.Error as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to grant schema permissions for user: {db_user_to_grant} in database: {db_name} : {e}"
                )
            )
            raise CommandError(f"Failed to set schema permissions for newly created database: {db_name}.") from e
        finally:
            if admin_conn:
                admin_conn.close()

    def _ensure_users_and_db(self, admin_conn: Connection):
        self.stdout.write(self.style.MIGRATE_HEADING("Checking and creating database users and databases..."))
        cursor = admin_conn.cursor()
        try:
            for db_alias, db_config in settings.DATABASES.items():
                validated_config = self._validate_config(db_alias, db_config)
                if not validated_config:
                    continue  # Skip this alias if validation failed

                db_name, db_user, db_password = validated_config

                # Ensure DB User Exists
                if not self._user_exists(cursor, db_user):
                    self._create_database_user(cursor, admin_conn.info.user, db_alias, db_user, db_password)
                else:
                    self.stdout.write(f"User found: {db_user}")

                # Ensure Database Exists
                if not self._database_exists(cursor, db_name):
                    self._create_database(cursor, db_alias, db_name, db_user)  # db_user is the owner
                    self._ensure_schema_permissions(db_name, db_user)
                else:
                    self.stdout.write(f"Database found: {db_name}")
        finally:
            if cursor:
                cursor.close()
        self.stdout.write("Database and user checks complete.")

    def _run_migrations(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Running migrations..."))
        for db_alias in settings.DATABASES.keys():
            if settings.DATABASES[db_alias].get("ENGINE") != "django.db.backends.postgresql":
                self.stdout.write(
                    self.style.WARNING(f"Skipping migrations for database: {db_alias}. ENGINE is not PostgreSQL.")
                )
                continue
            try:
                self.stdout.write(f"For database: {db_alias}")
                call_command("migrate", database=db_alias, interactive=False)
                self.stdout.write(self.style.SUCCESS(f"Migrations complete for database: {db_alias}"))
            except Exception as e:  # Catch more general errors from call_command
                self.stderr.write(self.style.ERROR(f"Error running migrations for database: {db_alias}: {str(e)}"))
                # Re-raise as CommandError to potentially stop the whole process if a migration fails
                raise CommandError(f"Migration failed for {db_alias}.") from e

        # initialize the cache table according to Django's requirements
        # https://docs.djangoproject.com/en/5.2/topics/cache/#creating-the-cache-table
        self.stdout.write("Configuring db-backed cache...")
        call_command("createcachetable")

        self.stdout.write("All migrations processed.")

    def _ensure_superuser(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Checking for superuser..."))
        DJANGO_SUPERUSER_USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        DJANGO_SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if DJANGO_SUPERUSER_USERNAME:
            User = get_user_model()
            # Check against the default database
            if User.objects.using(DEFAULT_DB_ALIAS).filter(username=DJANGO_SUPERUSER_USERNAME).exists():
                self.stdout.write(f"Superuser: {DJANGO_SUPERUSER_USERNAME} already exists in database: {DEFAULT_DB_ALIAS}")
            else:
                if DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD:
                    self.stdout.write(f"Superuser: {DJANGO_SUPERUSER_USERNAME} not found. Creating...")
                    # Note: createsuperuser --no-input relies on DJANGO_SUPERUSER_PASSWORD env var implicitly for password.
                    # Explicitly passing username and email makes it clearer.
                    call_command(
                        "createsuperuser",
                        interactive=False,
                        username=DJANGO_SUPERUSER_USERNAME,
                        email=DJANGO_SUPERUSER_EMAIL,
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Cannot create superuser: {DJANGO_SUPERUSER_USERNAME}. "
                            "DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD environment variables are not set."
                        )
                    )
        else:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME environment variable not set. Skipping superuser creation.")

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Completely reset the database(s) (DESTRUCTIVE).")

    def handle(self, *args, **options):
        # database and user setup (requires admin connection)
        admin_conn = None
        reset = options.get("reset", False)
        try:
            admin_conn = self._admin_connection()
            if reset:
                self._reset(admin_conn)
            self._ensure_users_and_db(admin_conn)
        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return
        finally:
            if admin_conn and not admin_conn.closed:
                admin_conn.close()

        # migrations
        self._run_migrations()

        # superuser
        self._ensure_superuser()

        self.stdout.write(self.style.SUCCESS("ensure_db command finished successfully."))
