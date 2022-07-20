from django.db import migrations
from django.utils.translation import gettext_lazy as _


def load_initial_data(app, *args, **kwargs):
    EligibilityType = app.get_model("core", "EligibilityType")

    type1 = EligibilityType.objects.create(name="type1", label="Eligibility Type 1", group_id="group1")
    type2 = EligibilityType.objects.create(name="type2", label="Eligibility Type 2", group_id="group2")

    PemData = app.get_model("core", "PemData")

    server_public_key = PemData.objects.create(
        text="""
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyYo6Pe9OSfPGX0oQXyLA
blOwrMgc/j1JlF07b1ahq1lc3FH0XEk3Dzqbt9NuQs8hz6493vBNtNWTpVmvbGe4
VX3UjhpEARhN3m4jf/Z2OEuDt2A9q19NLSjgeyhieLkYLwN1ezYXrkn7cfOngcJM
nGDXp45CaA+g3DzasrjETnKUdqecCzJ3FJ/RRwfibrju7eS/8s6H03nvydzeAJzT
kEv7Fic2JJEUhh2rJhyLxt+qKkIYeBG+5fBri4miaS8FPnD/yjZzEAFsQc7n0dGq
DAhSJS8tYNmXFmGlaCfRUBNV3mvOx0vFPuH21WQ5KKZxZP0e64/uQdotbPIImiyR
JwIDAQAB
-----END PUBLIC KEY-----

""",
        label="Eligibility server public key",
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
IW2tFIsMgJQtgpvgs52NFI7pQGJR/fTG+Ycocxo78TkLr/RIj8Kj5brXsbZ9P
3/WBX5GAISTSp1ab8xVgK/Tm07hGVqnY2lCAVAoGAIql0YjhE2ecGtLcU+Qm8
LTnwpg4GjmBnNTNGSCfB7IuYEsQK489R49Qw3xhwM5rkdRajmbCHm+Eiz+/+4NwY
kt5I1/NMu7vYUR40MwyEuPSm3Q+bvEGu/71pL8wFIUVlshNJ5CN60fA8qqo+5kVK
4Ntzy7Kq6WpC9Dhh75vE3ZcCgYEAty99uXtxsJD6+aEwcvcENkUwUztPQ6ggAwci
je9Z/cmwCj6s9mN3HzfQ4qgGrZs4ycCK655xhilBFOIQJ3YRUKUaDYk4H0YDe
Osf6gTP8wtQDH2GZSNlavLk5w7UFDYQD2b47y4fw+NaOEYvjPl0p5lmb6ebAPZb8
FbKZRd0CgYBC1HTbA+zMEqDdY4MWJJLC6jZsjdxOGhzjrCtWcIWEGMDF7oDDEoix
W3j2hwm4C6vaNkH9XX1dr5+q6gq8vJQdbYoExl22BGMiNbfI3+sLRk0zBYL//W6c
tSREgR4EjosqQfbkceLJ2JT1wuNjInI0eR9H3cRugvlDTeWtbdJ5qA==
-----END RSA PRIVATE KEY-----
""",
        label="Benefits client private key",
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
        scope="verify:type1",
        claim="type1",
    )

    EligibilityVerifier = app.get_model("core", "EligibilityVerifier")

    EligibilityVerifier.objects.create(
        name="Test Eligibility Verifier 1",
        api_url="http://server:5000/verify",
        api_auth_header="X-Server-API-Key",
        api_auth_key="server-auth-token",
        eligibility_type=type1,
        public_key=server_public_key,
        jwe_cek_enc="A256CBC-HS512",
        jwe_encryption_alg="RSA-OAEP",
        jws_signing_alg="RS256",
        auth_provider=auth_provider,
        selection_label=_("eligibility.pages.index.dmv.label"),
        selection_label_description=None,
        start_content_title=_("eligibility.pages.start.dmv.content_title"),
        start_item_name=_("eligibility.pages.start.dmv.items[0].title"),
        start_item_description=_("eligibility.pages.start.dmv.items[0].text"),
        start_blurb=_("eligibility.pages.start.dmv.p[0]"),
        form_title=_("eligibility.pages.confirm.dmv.title"),
        form_content_title=_("eligibility.pages.confirm.dmv.content_title"),
        form_blurb=_("eligibility.pages.confirm.dmv.p[0]"),
        form_sub_label=_("eligibility.forms.confirm.dmv.fields.sub"),
        form_sub_placeholder="A1234567",
        form_sub_pattern=".+",
        form_name_label=_("eligibility.forms.confirm.dmv.fields.name"),
        form_name_placeholder="Rodriguez",
        form_name_max_length=255,
        unverified_title=_("eligibility.pages.unverified.dmv.title"),
        unverified_content_title=_("eligibility.pages.unverified.dmv.content_title"),
        unverified_blurb=_("eligibility.pages.unverified.dmv.p[0]"),
    )

    EligibilityVerifier.objects.create(
        name="Test Eligibility Verifier 2",
        api_url="http://server:5000/verify",
        api_auth_header="X-Server-API-Key",
        api_auth_key="server-auth-token",
        eligibility_type=type2,
        public_key=server_public_key,
        jwe_cek_enc="A256CBC-HS512",
        jwe_encryption_alg="RSA-OAEP",
        jws_signing_alg="RS256",
        auth_provider=None,
        selection_label=_("eligibility.pages.index.mst.label"),
        selection_label_description=_("eligibility.pages.index.mst.description"),
        start_content_title=_("eligibility.pages.start.mst.content_title"),
        start_item_name=_("eligibility.pages.start.mst.items[0].title"),
        start_item_description=_("eligibility.pages.start.mst.items[0].text"),
        start_blurb=_("eligibility.pages.start.mst.p[0]"),
        form_title=_("eligibility.pages.confirm.mst.title"),
        form_content_title=_("eligibility.pages.confirm.mst.content_title"),
        form_blurb=_("eligibility.pages.confirm.mst.p[0]"),
        form_sub_label=_("eligibility.forms.confirm.mst.fields.sub"),
        form_sub_placeholder="B1234567",
        form_sub_pattern=".+",
        form_name_label=_("eligibility.forms.confirm.mst.fields.name"),
        form_name_placeholder="Garcia",
        form_name_max_length=255,
        unverified_title=_("eligibility.pages.unverified.mst.title"),
        unverified_content_title=_("eligibility.pages.unverified.mst.content_title"),
        unverified_blurb=_("eligibility.pages.unverified.mst.p[0]"),
    )

    EligibilityVerifier.objects.create(
        name="OAuth claims via Login.gov",
        eligibility_type=type1,
        auth_provider=auth_provider,
        selection_label=_("eligibility.pages.index.oauth.label"),
        selection_label_description=None,
        start_content_title=_("eligibility.pages.start.oauth.content_title"),
        start_item_name=_("eligibility.pages.start.oauth.items[0].title"),
        start_item_description=_("eligibility.pages.start.oauth.items[0].text"),
        start_blurb=_("eligibility.pages.start.oauth.p[0]"),
        unverified_title=_("eligibility.pages.unverified.oauth.title"),
        unverified_content_title=_("eligibility.pages.unverified.oauth.content_title"),
        unverified_blurb=_("eligibility.pages.unverified.oauth.p[0]"),
    )

    PaymentProcessor = app.get_model("core", "PaymentProcessor")

    PaymentProcessor.objects.create(
        name="Test Payment Processor",
        api_base_url="http://server:5000",
        api_access_token_endpoint="access-token",
        api_access_token_request_key="request_access",
        api_access_token_request_val="REQUEST_ACCESS",
        card_tokenize_url="http://localhost:5000/static/tokenize.js",
        card_tokenize_func="tokenize",
        card_tokenize_env="test",
        client_cert=dummy_cert,
        client_cert_private_key=client_private_key,
        client_cert_root_ca=dummy_cert,
        customer_endpoint="customer",
        customers_endpoint="customers",
        group_endpoint="group",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
