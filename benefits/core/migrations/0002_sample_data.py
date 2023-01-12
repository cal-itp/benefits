"""Data migration which loads sample data.
Set environment variable DJANGO_LOAD_SAMPLE_DATA to False to skip loading sample data.
"""
from django.conf import settings
from django.db import migrations
from django.utils.translation import gettext_lazy as _


def load_sample_data(app, *args, **kwargs):
    if not settings.LOAD_SAMPLE_DATA:
        print("  LOAD_SAMPLE_DATA is set to False, skipping sample data")
        return

    EligibilityType = app.get_model("core", "EligibilityType")

    senior_type = EligibilityType.objects.create(name="senior", label="Senior", group_id="group1")
    courtesy_card_type = EligibilityType.objects.create(name="courtesy_card", label="Courtesy Card", group_id="group2")

    PemData = app.get_model("core", "PemData")

    server_public_key = PemData.objects.create(
        label="Eligibility server public key",
        remote_url="https://raw.githubusercontent.com/cal-itp/eligibility-server/dev/keys/server.pub",
    )

    client_private_key = PemData.objects.create(
        text="""
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1pt0ZoOuPEVPJJS+5r884zcjZLkZZ2GcPwr79XOLDbOi46on
Ca79kjRnhS0VUK96SwUPS0z9J5mDA5LSNL2RoxFb5QGaevnJY828NupzTNdUd0sY
JK3kRjKUggHWuB55hwJcH/Dx7I3DNH4NL68UAlK+VjwJkfYPrhq/bl5z8ZiurvBa
5C1mDxhFpcTZlCfxQoas7D1d+uPACF6mEMbQNd3RaIaSREO50NvNywXIIt/OmCiR
qI7JtOcn4eyh1I4j9WtlbMhRJLfwPMAgY5epTsWcURmhVofF2wVoFbib3JGCfA7t
z/gmP5YoEKnf/cumKmF3e9LrZb8zwm7bTHUViwIDAQABAoIBAQCIv0XMjNvZS9DC
XoXGQtVpcxj6dXfaiDgnc7hZDubsNCr3JtT5NqgdIYdVNQUABNDIPNEiCkzFjuwM
uuF2+dRzM/x6UCs/cSsCjXYBCCOwMwV/fjpEJQnwMQqwTLulVsXZYYeSUtXVBf/8
0tVULRty34apLFhsyX30UtboXQdESfpmm5ZsqsZJlYljw+M7JxRMneQclI19y/ya
hPWlfhLB9OffVEJXGaWx1NSYnKoCMKqE/+4krROr6V62xXaNyX6WtU6XiT7C6R5A
PBxfhmoeFdVCF6a+Qq0v2fKThYoZnV4sn2q2An9YPfynFYnlgzdfnAFSejsqxQd0
fxYLOtMBAoGBAP1jxjHDJngZ1N+ymw9MIpRgr3HeuMP5phiSTbY2tu9lPzQd+TMX
fhr1bQh2Fd/vU0u7X0yPnTWtUrLlCdGnWPpXivx95GNGgUUIk2HStFdrRx+f2Qvk
G8vtLgmSbjQ26UiHzxi9Wa0a41PWIA3TixkcFrS2X29Qc4yd6pVHmicfAoGBANjR
Z8aaDkSKLkq5Nk1T7I0E1+mtPoH1tPV/FJClXjJrvfDuYHBeOyUpipZddnZuPGWA
IW2tFIsMgJQtgpvgs52NFI7pQGJRUPK/fTG+Ycocxo78TkLr/RIj8Kj5brXsbZ9P
3/WBX5GAISTSp1ab8xVgK/Tm07hGupKVqnY2lCAVAoGAIql0YjhE2ecGtLcU+Qm8
LTnwpg4GjmBnNTNGSCfB7IuYEsQK489R49Qw3xhwM5rkdRajmbCHm+Eiz+/+4NwY
kt5I1/NMu7vYUR40MwyEuPSm3Q+bvEGu/71pL8wFIUVlshNJ5CN60fA8qqo+5kVK
4Ntzy7Kq6WpC9Dhh75vE3ZcCgYEAty99uXtxsJD6+aEwcvcENkUwUztPQ6ggAwci
je9Z/cmwCj6s9mN3HzfQ4qgGrZsHpk4ycCK655xhilBFOIQJ3YRUKUaDYk4H0YDe
Osf6gTP8wtQDH2GZSNlavLk5w7UFDYQD2b47y4fw+NaOEYvjPl0p5lmb6ebAPZb8
FbKZRd0CgYBC1HTbA+zMEqDdY4MWJJLC6jZsjdxOGhzjrCtWcIWEGMDF7oDDEoix
W3j2hwm4C6vaNkH9XX1dr5+q6gq8vJQdbYoExl22BGMiNbfI3+sLRk0zBYL//W6c
tSREgR4EjosqQfbkceLJ2JT1wuNjInI0eR9H3cRugvlDTeWtbdJ5qA==
-----END RSA PRIVATE KEY-----
""",
        label="Benefits client private key",
    )

    client_public_key = PemData.objects.create(
        text="""
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1pt0ZoOuPEVPJJS+5r88
4zcjZLkZZ2GcPwr79XOLDbOi46onCa79kjRnhS0VUK96SwUPS0z9J5mDA5LSNL2R
oxFb5QGaevnJY828NupzTNdUd0sYJK3kRjKUggHWuB55hwJcH/Dx7I3DNH4NL68U
AlK+VjwJkfYPrhq/bl5z8ZiurvBa5C1mDxhFpcTZlCfxQoas7D1d+uPACF6mEMbQ
Nd3RaIaSREO50NvNywXIIt/OmCiRqI7JtOcn4eyh1I4j9WtlbMhRJLfwPMAgY5ep
TsWcURmhVofF2wVoFbib3JGCfA7tz/gmP5YoEKnf/cumKmF3e9LrZb8zwm7bTHUV
iwIDAQAB
-----END PUBLIC KEY-----
""",
        label="Benefits client public key",
    )

    dummy_cert = PemData.objects.create(
        text="""
-----BEGIN CERTIFICATE-----
PEM DATA
-----END CERTIFICATE-----
""",
        label="Dummy certificate",
    )

    AuthProvider = app.get_model("core", "AuthProvider")

    auth_provider = AuthProvider.objects.create(
        sign_in_button_label=_("eligibility.buttons.signin"),
        sign_out_button_label=_("eligibility.buttons.signout"),
        client_name="benefits-oauth-client-name",
        client_id="benefits-oauth-client-id",
        authority="https://example.com",
        scope="verify:senior",
        claim="senior",
    )

    EligibilityVerifier = app.get_model("core", "EligibilityVerifier")

    verifier1 = EligibilityVerifier.objects.create(
        name="OAuth claims via Login.gov",
        eligibility_type=senior_type,
        auth_provider=auth_provider,
        selection_label=_("eligibility.pages.index.login_gov.label"),
        selection_label_description=_("eligibility.pages.index.login_gov.description"),
        start_title=_("eligibility.pages.start.login_gov.title"),
        start_headline=_("eligibility.pages.start.login_gov.headline"),
        start_item_heading=_("eligibility.pages.start.login_gov.start_item.heading"),
        start_item_details=_("eligibility.pages.start.login_gov.start_item.details"),
        start_help_anchor="login-gov",
        unverified_title=_("eligibility.pages.unverified.login_gov.title"),
        unverified_blurb=_("eligibility.pages.unverified.login_gov.p[0]"),
        eligibility_confirmed_item_heading=_("enrollment.pages.index.login_gov.eligibility_confirmed_item.heading"),
        eligibility_confirmed_item_details=_(
            "enrollment.pages.index.login_gov.eligibility_confirmed_item.details%(transit_agency_short_name)s"
        ),
        enrollment_success_confirm_item_details=_("enrollment.pages.success.login_gov.confirm_item.details"),
        enrollment_success_expiry_item_heading=None,
        enrollment_success_expiry_item_details=None,
    )

    verifier2 = EligibilityVerifier.objects.create(
        name="Test Eligibility Verifier 2",
        api_url="http://server:8000/verify",
        api_auth_header="X-Server-API-Key",
        api_auth_key="server-auth-token",
        eligibility_type=courtesy_card_type,
        public_key=server_public_key,
        jwe_cek_enc="A256CBC-HS512",
        jwe_encryption_alg="RSA-OAEP",
        jws_signing_alg="RS256",
        auth_provider=None,
        selection_label=_("eligibility.pages.index.mst_cc.label"),
        selection_label_description=_("eligibility.pages.index.mst_cc.description"),
        start_title=_("eligibility.pages.start.mst_cc.title"),
        start_headline=_("eligibility.pages.start.mst_cc.headline"),
        start_item_heading=_("eligibility.pages.start.mst_cc.start_item.heading"),
        start_item_details=_("eligibility.pages.start.mst_cc.start_item.details"),
        start_help_anchor="mst-courtesy-card",
        form_title=_("eligibility.pages.confirm.mst_cc.title"),
        form_headline=_("eligibility.pages.confirm.mst_cc.headline"),
        form_blurb=_("eligibility.pages.confirm.mst_cc.p[0]"),
        form_sub_label=_("eligibility.forms.confirm.mst_cc.fields.sub"),
        form_sub_help_text=_("eligibility.forms.confirm.mst_cc.fields.sub.help_text"),
        form_sub_placeholder="12345",
        form_sub_pattern=r"\d{5}",
        form_input_mode="numeric",
        form_max_length=5,
        form_name_label=_("eligibility.forms.confirm.mst_cc.fields.name"),
        form_name_help_text=_("eligibility.forms.confirm.mst_cc.fields.name.help_text"),
        form_name_placeholder="Garcia",
        form_name_max_length=255,
        unverified_title=_("eligibility.pages.unverified.mst_cc.title"),
        unverified_blurb=_("eligibility.pages.unverified.mst_cc.p[0]"),
        eligibility_confirmed_item_heading=None,
        eligibility_confirmed_item_details=None,
        enrollment_success_confirm_item_details=_("enrollment.pages.success.mst_cc.confirm_item.details"),
        enrollment_success_expiry_item_heading=_("enrollment.pages.success.mst_cc.expiry_item.heading"),
        enrollment_success_expiry_item_details=_("enrollment.pages.success.mst_cc.expiry_item.details"),
    )

    PaymentProcessor = app.get_model("core", "PaymentProcessor")

    payment_processor = PaymentProcessor.objects.create(
        name="Test Payment Processor",
        api_base_url="http://server:8000",
        api_access_token_endpoint="access-token",
        api_access_token_request_key="request_access",
        api_access_token_request_val="REQUEST_ACCESS",
        card_tokenize_url="http://server:8000/static/tokenize.js",
        card_tokenize_func="tokenize",
        card_tokenize_env="test",
        client_cert=dummy_cert,
        client_cert_private_key=client_private_key,
        client_cert_root_ca=dummy_cert,
        customer_endpoint="customer",
        customers_endpoint="customers",
        group_endpoint="group",
    )

    TransitAgency = app.get_model("core", "TransitAgency")

    mst_agency = TransitAgency.objects.create(
        slug="mst",
        short_name="MST (sample)",
        long_name="Monterey-Salinas Transit (sample)",
        agency_id="mst",
        merchant_id="mst",
        info_url="https://mst.org/benefits",
        phone="888-678-2871",
        active=True,
        private_key=client_private_key,
        public_key=client_public_key,
        jws_signing_alg="RS256",
        payment_processor=payment_processor,
        eligibility_index_intro=_("eligibility.pages.index.p[0].mst"),
    )
    mst_agency.eligibility_types.set([senior_type, courtesy_card_type])
    mst_agency.eligibility_verifiers.set([verifier1, verifier2])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_sample_data),
    ]
