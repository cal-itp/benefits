"""
The core application: Houses base templates and reusable models and components.
"""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreAppConfig(AppConfig):
    name = "benefits.core"
    label = "core"
    verbose_name = "Core"

    # Create staff group here instead of in a data migration.
    # Hat tip: https://lincolnloop.com/blog/ensuring-essential-data-exists-in-your-django-app-on-startup/

    def ready(self):
        # Connect a handler that runs after migrations
        post_migrate.connect(self.setup_group, sender=self)

    @staticmethod
    def setup_group(**kwargs):
        # Ensure the staff group exists.
        import datetime

        from django.conf import settings
        from django.contrib.auth.models import Group

        group, created = Group.objects.get_or_create(name=settings.STAFF_GROUP_NAME)

        if created:
            print(f"[{datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S")}] INFO Staff group '{group.name}' created.")
