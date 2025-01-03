from django.db import models

from .common import SecretNameField


class ClaimsProvider(models.Model):
    """An entity that provides claims for eligibility verification."""

    id = models.AutoField(primary_key=True)
    sign_out_button_template = models.TextField(default="", blank=True, help_text="Template that renders sign-out button")
    sign_out_link_template = models.TextField(default="", blank=True, help_text="Template that renders sign-out link")
    client_name = models.TextField(help_text="Unique identifier used to register this claims provider with Authlib registry")
    client_id_secret_name = SecretNameField(
        help_text="The name of the secret containing the client ID for this claims provider"
    )
    authority = models.TextField(help_text="The fully qualified HTTPS domain name for an OAuth authority server")
    scheme = models.TextField(help_text="The authentication scheme to use")

    @property
    def supports_sign_out(self):
        return bool(self.sign_out_button_template) or bool(self.sign_out_link_template)

    @property
    def client_id(self):
        secret_name_field = self._meta.get_field("client_id_secret_name")
        return secret_name_field.secret_value(self)

    def __str__(self) -> str:
        return self.client_name
