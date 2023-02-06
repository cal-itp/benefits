"""This migration simply ensures that data migrations (assumed to be files that start with 0002) will run sequentially.
It does so by looking for all migration files starting with "0002" and declaring them in its dependency list.
"""
import os

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    migrations_directory = os.path.join(settings.BASE_DIR, "benefits", "core", "migrations")
    dependencies = [("core", file.replace(".py", "")) for file in os.listdir(migrations_directory) if file.startswith("0002")]

    operations = []
