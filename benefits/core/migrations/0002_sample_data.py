from django.db import migrations
from django.utils.translation import gettext_lazy as _


def load_initial_data(app, *args, **kwargs):
    AuthProvider = app.get_model("core", "AuthProvider")

    AuthProvider.objects.create(
        sign_in_button_label=_("eligibility.buttons.signin"),
        sign_out_button_label=_("eligibility.buttons.signout"),
        client_name="benefits-oauth-client-name",
        client_id="benefits-oauth-client-id",
        authority="https://example.com",
        scope="verify:type1",
        claim="type1",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
