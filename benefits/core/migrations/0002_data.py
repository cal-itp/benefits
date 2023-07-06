"""Data migration which loads configuration data for Benefits.
"""
import json
import os

from django.db import migrations
from django.utils.translation import gettext_lazy as _


def load_data(app, *args, **kwargs):
    EligibilityType = app.get_model("core", "EligibilityType")

    mst_senior_type = EligibilityType.objects.create(
        name="senior", label="Senior Discount (MST)", group_id=os.environ.get("MST_SENIOR_GROUP_ID", "group1")
    )
    mst_veteran_type = EligibilityType.objects.create(
        name="veteran",
        label="Veteran Discount (MST)",
        group_id=os.environ.get("MST_VETERAN_GROUP_ID", "group3"),
    )
    mst_courtesy_card_type = EligibilityType.objects.create(
        name="courtesy_card",
        label="Courtesy Card Discount (MST)",
        group_id=os.environ.get("MST_COURTESY_CARD_GROUP_ID", "group2"),
    )
    sacrt_senior_type = EligibilityType.objects.create(
        name="senior", label="Senior Discount (SacRT)", group_id=os.environ.get("SACRT_SENIOR_GROUP_ID", "group3")
    )

    PemData = app.get_model("core", "PemData")

    server_public_key = PemData.objects.create(
        label="Eligibility server public key",
        remote_url=os.environ.get(
            "SERVER_PUBLIC_KEY_URL", "https://raw.githubusercontent.com/cal-itp/eligibility-server/dev/keys/server.pub"
        ),
    )

    default_client_private_key = """
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
"""

    client_private_key = PemData.objects.create(
        text=os.environ.get("CLIENT_PRIVATE_KEY", default_client_private_key),
        label="Benefits client private key",
    )

    default_client_public_key = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1pt0ZoOuPEVPJJS+5r88
4zcjZLkZZ2GcPwr79XOLDbOi46onCa79kjRnhS0VUK96SwUPS0z9J5mDA5LSNL2R
oxFb5QGaevnJY828NupzTNdUd0sYJK3kRjKUggHWuB55hwJcH/Dx7I3DNH4NL68U
AlK+VjwJkfYPrhq/bl5z8ZiurvBa5C1mDxhFpcTZlCfxQoas7D1d+uPACF6mEMbQ
Nd3RaIaSREO50NvNywXIIt/OmCiRqI7JtOcn4eyh1I4j9WtlbMhRJLfwPMAgY5ep
TsWcURmhVofF2wVoFbib3JGCfA7tz/gmP5YoEKnf/cumKmF3e9LrZb8zwm7bTHUV
iwIDAQAB
-----END PUBLIC KEY-----
"""

    client_public_key = PemData.objects.create(
        text=os.environ.get("CLIENT_PUBLIC_KEY", default_client_public_key),
        label="Benefits client public key",
    )

    dummy_cert_text = """
-----BEGIN CERTIFICATE-----
PEM DATA
-----END CERTIFICATE-----
"""

    mst_payment_processor_client_cert = PemData.objects.create(
        text=os.environ.get("MST_PAYMENT_PROCESSOR_CLIENT_CERT", dummy_cert_text),
        label="MST payment processor client certificate",
    )

    mst_payment_processor_client_cert_private_key = PemData.objects.create(
        text=os.environ.get("MST_PAYMENT_PROCESSOR_CLIENT_CERT_PRIVATE_KEY", client_private_key.text),
        label="MST payment processor client certificate private key",
    )

    mst_payment_processor_client_cert_root_ca = PemData.objects.create(
        text=os.environ.get("MST_PAYMENT_PROCESSOR_CLIENT_CERT_ROOT_CA", dummy_cert_text),
        label="MST payment processor client certificate root CA",
    )

    sacrt_payment_processor_client_cert = PemData.objects.create(
        text=os.environ.get("SACRT_PAYMENT_PROCESSOR_CLIENT_CERT", dummy_cert_text),
        label="SacRT payment processor client certificate",
    )

    sacrt_payment_processor_client_cert_private_key = PemData.objects.create(
        text=os.environ.get("SACRT_PAYMENT_PROCESSOR_CLIENT_CERT_PRIVATE_KEY", client_private_key.text),
        label="SacRT payment processor client certificate private key",
    )

    sacrt_payment_processor_client_cert_root_ca = PemData.objects.create(
        text=os.environ.get("SACRT_PAYMENT_PROCESSOR_CLIENT_CERT_ROOT_CA", dummy_cert_text),
        label="SacRT payment processor client certificate root CA",
    )

    AuthProvider = app.get_model("core", "AuthProvider")

    senior_auth_provider = AuthProvider.objects.create(
        sign_out_button_label=_("eligibility.buttons.senior.signout"),
        client_name=os.environ.get("SENIOR_AUTH_PROVIDER_CLIENT_NAME", "senior-benefits-oauth-client-name"),
        client_id=os.environ.get("AUTH_PROVIDER_CLIENT_ID", "benefits-oauth-client-id"),
        authority=os.environ.get("AUTH_PROVIDER_AUTHORITY", "https://example.com"),
        scope=os.environ.get("SENIOR_AUTH_PROVIDER_SCOPE", "verify:senior"),
        claim=os.environ.get("SENIOR_AUTH_PROVIDER_CLAIM", "senior"),
        scheme=os.environ.get("SENIOR_AUTH_PROVIDER_SCHEME", "dev-cal-itp_benefits"),
    )

    veteran_auth_provider = AuthProvider.objects.create(
        client_name=os.environ.get("VETERAN_AUTH_PROVIDER_CLIENT_NAME", "veteran-benefits-oauth-client-name"),
        client_id=os.environ.get("AUTH_PROVIDER_CLIENT_ID", "benefits-oauth-client-id"),
        authority=os.environ.get("AUTH_PROVIDER_AUTHORITY", "https://example.com"),
        scope=os.environ.get("VETERAN_AUTH_PROVIDER_SCOPE", "verify:veteran"),
        claim=os.environ.get("VETERAN_AUTH_PROVIDER_CLAIM", "veteran"),
        scheme=os.environ.get("VETERAN_AUTH_PROVIDER_SCHEME", "vagov"),
    )

    EligibilityVerifier = app.get_model("core", "EligibilityVerifier")

    mst_oauth_claims_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("MST_OAUTH_VERIFIER_NAME", "OAuth claims via Login.gov (MST)"),
        bullets=[
            "eligibility.pages.start.login_gov.required_items[0]",
            "eligibility.pages.start.login_gov.required_items[1]",
            "eligibility.pages.start.login_gov.required_items[2]",
        ],
        eligibility_type=mst_senior_type,
        auth_provider=senior_auth_provider,
        selection_label=_("eligibility.pages.index.login_gov.label"),
        selection_label_description=_("eligibility.pages.index.login_gov.description"),
        start_template="eligibility/start__login_gov.html",
        start_help_anchor="login-gov",
        unverified_title=_("eligibility.pages.unverified.title"),
        unverified_blurb=_("eligibility.pages.unverified.p[0]"),
        eligibility_confirmed_item_heading=_("enrollment.pages.index.login_gov.eligibility_confirmed_item.heading"),
        eligibility_confirmed_item_details=_(
            "enrollment.pages.index.login_gov.eligibility_confirmed_item.details%(transit_agency_short_name)s"
        ),
        enrollment_success_confirm_item_details=_("enrollment.pages.success.login_gov.confirm_item.details"),
        enrollment_success_expiry_item_heading=None,
        enrollment_success_expiry_item_details=None,
    )

    mst_veteran_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("MST_VETERAN_VERIFIER_NAME", "VA.gov - Veteran (MST)"),
        bullets=[
            "eligibility.pages.start.veteran.required_items[0]",
            "eligibility.pages.start.veteran.required_items[1]",
            "eligibility.pages.start.veteran.required_items[2]",
            "eligibility.pages.start.veteran.required_items[3]",
        ],
        eligibility_type=mst_veteran_type,
        auth_provider=veteran_auth_provider,
        selection_label=_("eligibility.pages.index.veteran.label"),
        selection_label_description=_("eligibility.pages.index.veteran.description"),
        start_template="eligibility/start__veteran.html",
        unverified_title=_("eligibility.pages.unverified.title"),
        unverified_blurb=_("eligibility.pages.unverified.p[0]"),
        enrollment_success_confirm_item_details=_("enrollment.pages.success.veteran.confirm_item.details"),
        enrollment_success_expiry_item_heading=None,
        enrollment_success_expiry_item_details=None,
    )

    mst_courtesy_card_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("COURTESY_CARD_VERIFIER", "Eligibility Server Verifier"),
        api_url=os.environ.get("COURTESY_CARD_VERIFIER_API_URL", "http://server:8000/verify"),
        api_auth_header=os.environ.get("COURTESY_CARD_VERIFIER_API_AUTH_HEADER", "X-Server-API-Key"),
        api_auth_key=os.environ.get("COURTESY_CARD_VERIFIER_API_AUTH_KEY", "server-auth-token"),
        eligibility_type=mst_courtesy_card_type,
        public_key=server_public_key,
        jwe_cek_enc=os.environ.get("COURTESY_CARD_VERIFIER_JWE_CEK_ENC", "A256CBC-HS512"),
        jwe_encryption_alg=os.environ.get("COURTESY_CARD_VERIFIER_JWE_ENCRYPTION_ALG", "RSA-OAEP"),
        jws_signing_alg=os.environ.get("COURTESY_CARD_VERIFIER_JWS_SIGNING_ALG", "RS256"),
        auth_provider=None,
        selection_label=_("eligibility.pages.index.mst_cc.label"),
        selection_label_description=_("eligibility.pages.index.mst_cc.description"),
        start_template="eligibility/start__mst_courtesycard.html",
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

    sacrt_oauth_claims_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("SACRT_OAUTH_VERIFIER_NAME", "OAuth claims via Login.gov (SacRT)"),
        bullets=[
            "eligibility.pages.start.login_gov.required_items[0]",
            "eligibility.pages.start.login_gov.required_items[1]",
            "eligibility.pages.start.login_gov.required_items[2]",
        ],
        eligibility_type=sacrt_senior_type,
        auth_provider=senior_auth_provider,
        selection_label=_("eligibility.pages.index.login_gov.label"),
        selection_label_description=_("eligibility.pages.index.login_gov.description"),
        start_template="eligibility/start__login_gov.html",
        start_help_anchor="login-gov",
        unverified_title=_("eligibility.pages.unverified.title"),
        unverified_blurb=_("eligibility.pages.unverified.p[0]"),
        eligibility_confirmed_item_heading=_("enrollment.pages.index.login_gov.eligibility_confirmed_item.heading"),
        eligibility_confirmed_item_details=_(
            "enrollment.pages.index.login_gov.eligibility_confirmed_item.details%(transit_agency_short_name)s"
        ),
        enrollment_success_confirm_item_details=_("enrollment.pages.success.login_gov.confirm_item.details"),
        enrollment_success_expiry_item_heading=None,
        enrollment_success_expiry_item_details=None,
    )

    PaymentProcessor = app.get_model("core", "PaymentProcessor")

    mst_payment_processor = PaymentProcessor.objects.create(
        name=os.environ.get("MST_PAYMENT_PROCESSOR_NAME", "Test Payment Processor"),
        api_base_url=os.environ.get("MST_PAYMENT_PROCESSOR_API_BASE_URL", "http://server:8000"),
        api_access_token_endpoint=os.environ.get("MST_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT", "access-token"),
        api_access_token_request_key=os.environ.get("MST_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY", "request_access"),
        api_access_token_request_val=os.environ.get("MST_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL", "REQUEST_ACCESS"),
        card_tokenize_url=os.environ.get("MST_PAYMENT_PROCESSOR_CARD_TOKENIZE_URL", "http://server:8000/static/tokenize.js"),
        card_tokenize_func=os.environ.get("MST_PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC", "tokenize"),
        card_tokenize_env=os.environ.get("MST_PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV", "test"),
        client_cert=mst_payment_processor_client_cert,
        client_cert_private_key=mst_payment_processor_client_cert_private_key,
        client_cert_root_ca=mst_payment_processor_client_cert_root_ca,
        customer_endpoint="customer",
        customers_endpoint="customers",
        group_endpoint="group",
    )

    sacrt_payment_processor = PaymentProcessor.objects.create(
        name=os.environ.get("SACRT_PAYMENT_PROCESSOR_NAME", "Test Payment Processor"),
        api_base_url=os.environ.get("SACRT_PAYMENT_PROCESSOR_API_BASE_URL", "http://server:8000"),
        api_access_token_endpoint=os.environ.get("SACRT_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT", "access-token"),
        api_access_token_request_key=os.environ.get("SACRT_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY", "request_access"),
        api_access_token_request_val=os.environ.get("SACRT_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL", "REQUEST_ACCESS"),
        card_tokenize_url=os.environ.get("SACRT_PAYMENT_PROCESSOR_CARD_TOKENIZE_URL", "http://server:8000/static/tokenize.js"),
        card_tokenize_func=os.environ.get("SACRT_PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC", "tokenize"),
        card_tokenize_env=os.environ.get("SACRT_PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV", "test"),
        client_cert=sacrt_payment_processor_client_cert,
        client_cert_private_key=sacrt_payment_processor_client_cert_private_key,
        client_cert_root_ca=sacrt_payment_processor_client_cert_root_ca,
        customer_endpoint="customer",
        customers_endpoint="customers",
        group_endpoint="group",
    )

    TransitAgency = app.get_model("core", "TransitAgency")

    # load the sample data from a JSON file so that it can be accessed by Cypress as well
    sample_agency_data = os.path.join(os.path.dirname(__file__), "sample_agency.json")
    with open(sample_agency_data) as f:
        sample_agency = json.load(f)

    mst_agency = TransitAgency.objects.create(
        slug=sample_agency["slug"],
        short_name=os.environ.get("MST_AGENCY_SHORT_NAME", sample_agency["short_name"]),
        long_name=os.environ.get("MST_AGENCY_LONG_NAME", sample_agency["long_name"]),
        agency_id=sample_agency["agency_id"],
        merchant_id=sample_agency["merchant_id"],
        info_url=sample_agency["info_url"],
        phone=sample_agency["phone"],
        active=True,
        private_key=client_private_key,
        public_key=client_public_key,
        jws_signing_alg=os.environ.get("MST_AGENCY_JWS_SIGNING_ALG", "RS256"),
        payment_processor=mst_payment_processor,
        eligibility_index_intro=_("eligibility.pages.index.p[0].mst"),
    )
    mst_agency.eligibility_types.set([mst_senior_type, mst_veteran_type, mst_courtesy_card_type])
    mst_agency.eligibility_verifiers.set([mst_oauth_claims_verifier, mst_veteran_verifier, mst_courtesy_card_verifier])

    sacrt_agency = TransitAgency.objects.create(
        slug="sacrt",
        short_name=os.environ.get("SACRT_AGENCY_SHORT_NAME", "SacRT (sample)"),
        long_name=os.environ.get("SACRT_AGENCY_LONG_NAME", "Sacramento Regional Transit (sample)"),
        agency_id="sacrt",
        merchant_id=os.environ.get("SACRT_AGENCY_MERCHANT_ID", "sacrt"),
        info_url="https://sacrt.com/",
        phone="916-321-2877",
        active=os.environ.get("SACRT_AGENCY_ACTIVE", "True").lower() == "true",
        private_key=client_private_key,
        public_key=client_public_key,
        jws_signing_alg=os.environ.get("SACRT_AGENCY_JWS_SIGNING_ALG", "RS256"),
        payment_processor=sacrt_payment_processor,
        eligibility_index_intro=_("eligibility.pages.index.p[0].sacrt"),
    )
    sacrt_agency.eligibility_types.set([sacrt_senior_type])
    sacrt_agency.eligibility_verifiers.set([sacrt_oauth_claims_verifier])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
