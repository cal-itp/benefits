"""Data migration which loads configuration data for Benefits.
"""

import json
import os

from django.db import migrations


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
    sbmtd_senior_type = EligibilityType.objects.create(
        name="senior", label="Senior Discount (SBMTD)", group_id=os.environ.get("SBMTD_SENIOR_GROUP_ID", "group4")
    )
    sbmtd_mobility_pass_type = EligibilityType.objects.create(
        name="mobility_pass",
        label="Mobility Pass Discount (SBMTD)",
        group_id=os.environ.get("SBMTD_MOBILITY_PASS_GROUP_ID", "group5"),
    )

    PemData = app.get_model("core", "PemData")

    mst_server_public_key = PemData.objects.create(
        label="Eligibility server public key",
        remote_url=os.environ.get(
            "MST_SERVER_PUBLIC_KEY_URL", "https://raw.githubusercontent.com/cal-itp/eligibility-server/main/keys/server.pub"
        ),
    )

    sbmtd_server_public_key = PemData.objects.create(
        label="Eligibility server public key",
        remote_url=os.environ.get(
            "SBMTD_SERVER_PUBLIC_KEY_URL", "https://raw.githubusercontent.com/cal-itp/eligibility-server/main/keys/server.pub"
        ),
    )

    client_private_key = PemData.objects.create(
        text_secret_name="client-private-key",
        label="Benefits client private key",
    )

    client_public_key = PemData.objects.create(
        text_secret_name="client-public-key",
        label="Benefits client public key",
    )

    mst_payment_processor_client_cert = PemData.objects.create(
        text_secret_name="mst-payment-processor-client-cert",
        label="MST payment processor client certificate",
    )

    mst_payment_processor_client_cert_private_key = PemData.objects.create(
        text_secret_name="mst-payment-processor-client-cert-private-key",
        label="MST payment processor client certificate private key",
    )

    mst_payment_processor_client_cert_root_ca = PemData.objects.create(
        text_secret_name="mst-payment-processor-client-cert-root-ca",
        label="MST payment processor client certificate root CA",
    )

    sacrt_payment_processor_client_cert = PemData.objects.create(
        text_secret_name="sacrt-payment-processor-client-cert",
        label="SacRT payment processor client certificate",
    )

    sacrt_payment_processor_client_cert_private_key = PemData.objects.create(
        text_secret_name="sacrt-payment-processor-client-cert-private-key",
        label="SacRT payment processor client certificate private key",
    )

    sacrt_payment_processor_client_cert_root_ca = PemData.objects.create(
        text_secret_name="sacrt-payment-processor-client-cert-root-ca",
        label="SacRT payment processor client certificate root CA",
    )

    sbmtd_payment_processor_client_cert = PemData.objects.create(
        text_secret_name="sbmtd-payment-processor-client-cert",
        label="SBMTD payment processor client certificate",
    )

    sbmtd_payment_processor_client_cert_private_key = PemData.objects.create(
        text_secret_name="sbmtd-payment-processor-client-cert-private-key",
        label="SBMTD payment processor client certificate private key",
    )

    sbmtd_payment_processor_client_cert_root_ca = PemData.objects.create(
        text_secret_name="sbmtd-payment-processor-client-cert-root-ca",
        label="SBMTD payment processor client certificate root CA",
    )

    AuthProvider = app.get_model("core", "AuthProvider")

    senior_auth_provider = AuthProvider.objects.create(
        sign_out_button_template="core/includes/button--sign-out--login-gov.html",
        sign_out_link_template="core/includes/link--sign-out--login-gov.html",
        client_name=os.environ.get("SENIOR_AUTH_PROVIDER_CLIENT_NAME", "senior-benefits-oauth-client-name"),
        client_id_secret_name="auth-provider-client-id",
        authority=os.environ.get("AUTH_PROVIDER_AUTHORITY", "https://example.com"),
        scope=os.environ.get("SENIOR_AUTH_PROVIDER_SCOPE", "verify:senior"),
        claim=os.environ.get("SENIOR_AUTH_PROVIDER_CLAIM", "senior"),
        scheme=os.environ.get("SENIOR_AUTH_PROVIDER_SCHEME", "dev-cal-itp_benefits"),
    )

    veteran_auth_provider = AuthProvider.objects.create(
        sign_out_button_template="core/includes/button--sign-out--login-gov.html",
        sign_out_link_template="core/includes/link--sign-out--login-gov.html",
        client_name=os.environ.get("VETERAN_AUTH_PROVIDER_CLIENT_NAME", "veteran-benefits-oauth-client-name"),
        client_id_secret_name="auth-provider-client-id",
        authority=os.environ.get("AUTH_PROVIDER_AUTHORITY", "https://example.com"),
        scope=os.environ.get("VETERAN_AUTH_PROVIDER_SCOPE", "verify:veteran"),
        claim=os.environ.get("VETERAN_AUTH_PROVIDER_CLAIM", "veteran"),
        scheme=os.environ.get("VETERAN_AUTH_PROVIDER_SCHEME", "vagov"),
    )

    EligibilityVerifier = app.get_model("core", "EligibilityVerifier")

    mst_senior_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("MST_SENIOR_VERIFIER_NAME", "OAuth claims via Login.gov (MST)"),
        active=os.environ.get("MST_SENIOR_VERIFIER_ACTIVE", "True").lower() == "true",
        eligibility_type=mst_senior_type,
        auth_provider=senior_auth_provider,
        selection_label_template="eligibility/includes/selection-label--senior.html",
        start_template="eligibility/start--senior.html",
    )

    mst_veteran_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("MST_VETERAN_VERIFIER_NAME", "VA.gov - Veteran (MST)"),
        active=os.environ.get("MST_VETERAN_VERIFIER_ACTIVE", "True").lower() == "true",
        eligibility_type=mst_veteran_type,
        auth_provider=veteran_auth_provider,
        selection_label_template="eligibility/includes/selection-label--veteran.html",
        start_template="eligibility/start--veteran.html",
    )

    mst_courtesy_card_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("COURTESY_CARD_VERIFIER_NAME", "Eligibility Server Verifier"),
        active=os.environ.get("COURTESY_CARD_VERIFIER_ACTIVE", "True").lower() == "true",
        api_url=os.environ.get("COURTESY_CARD_VERIFIER_API_URL", "http://server:8000/verify"),
        api_auth_header=os.environ.get("COURTESY_CARD_VERIFIER_API_AUTH_HEADER", "X-Server-API-Key"),
        api_auth_key_secret_name="courtesy-card-verifier-api-auth-key",
        eligibility_type=mst_courtesy_card_type,
        public_key=mst_server_public_key,
        jwe_cek_enc=os.environ.get("COURTESY_CARD_VERIFIER_JWE_CEK_ENC", "A256CBC-HS512"),
        jwe_encryption_alg=os.environ.get("COURTESY_CARD_VERIFIER_JWE_ENCRYPTION_ALG", "RSA-OAEP"),
        jws_signing_alg=os.environ.get("COURTESY_CARD_VERIFIER_JWS_SIGNING_ALG", "RS256"),
        auth_provider=None,
        selection_label_template="eligibility/includes/selection-label--mst-courtesy-card.html",
        start_template="eligibility/start--mst-courtesy-card.html",
        form_class="benefits.eligibility.forms.MSTCourtesyCard",
    )

    sacrt_senior_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("SACRT_SENIOR_VERIFIER_NAME", "OAuth claims via Login.gov (SacRT)"),
        active=os.environ.get("SACRT_SENIOR_VERIFIER_ACTIVE", "False").lower() == "true",
        eligibility_type=sacrt_senior_type,
        auth_provider=senior_auth_provider,
        selection_label_template="eligibility/includes/selection-label--senior.html",
        start_template="eligibility/start--senior.html",
    )

    sbmtd_senior_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("SBMTD_SENIOR_VERIFIER_NAME", "OAuth claims via Login.gov (SBMTD)"),
        active=os.environ.get("SBMTD_SENIOR_VERIFIER_ACTIVE", "False").lower() == "true",
        eligibility_type=sbmtd_senior_type,
        auth_provider=senior_auth_provider,
        selection_label_template="eligibility/includes/selection-label--senior.html",
        start_template="eligibility/start--senior.html",
    )

    sbmtd_mobility_pass_verifier = EligibilityVerifier.objects.create(
        name=os.environ.get("MOBILITY_PASS_VERIFIER_NAME", "Eligibility Server Verifier"),
        active=os.environ.get("MOBILITY_PASS_VERIFIER_ACTIVE", "True").lower() == "true",
        api_url=os.environ.get("MOBILITY_PASS_VERIFIER_API_URL", "http://server:8000/verify"),
        api_auth_header=os.environ.get("MOBILITY_PASS_VERIFIER_API_AUTH_HEADER", "X-Server-API-Key"),
        api_auth_key_secret_name="mobility-pass-verifier-api-auth-key",
        eligibility_type=sbmtd_mobility_pass_type,
        public_key=sbmtd_server_public_key,
        jwe_cek_enc=os.environ.get("MOBILITY_PASS_VERIFIER_JWE_CEK_ENC", "A256CBC-HS512"),
        jwe_encryption_alg=os.environ.get("MOBILITY_PASS_VERIFIER_JWE_ENCRYPTION_ALG", "RSA-OAEP"),
        jws_signing_alg=os.environ.get("MOBILITY_PASS_VERIFIER_JWS_SIGNING_ALG", "RS256"),
        auth_provider=None,
        selection_label_template="eligibility/includes/selection-label--sbmtd-mobility-pass.html",
        start_template="eligibility/start--sbmtd-mobility-pass.html",
        form_class="benefits.eligibility.forms.SBMTDMobilityPass",
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

    sbmtd_payment_processor = PaymentProcessor.objects.create(
        name=os.environ.get("SBMTD_PAYMENT_PROCESSOR_NAME", "Test Payment Processor"),
        api_base_url=os.environ.get("SBMTD_PAYMENT_PROCESSOR_API_BASE_URL", "http://server:8000"),
        api_access_token_endpoint=os.environ.get("SBMTD_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT", "access-token"),
        api_access_token_request_key=os.environ.get("SBMTD_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY", "request_access"),
        api_access_token_request_val=os.environ.get("SBMTD_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL", "REQUEST_ACCESS"),
        card_tokenize_url=os.environ.get("SBMTD_PAYMENT_PROCESSOR_CARD_TOKENIZE_URL", "http://server:8000/static/tokenize.js"),
        card_tokenize_func=os.environ.get("SBMTD_PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC", "tokenize"),
        card_tokenize_env=os.environ.get("SBMTD_PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV", "test"),
        client_cert=sbmtd_payment_processor_client_cert,
        client_cert_private_key=sbmtd_payment_processor_client_cert_private_key,
        client_cert_root_ca=sbmtd_payment_processor_client_cert_root_ca,
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
        index_template="core/index--mst.html",
        eligibility_index_template="eligibility/index--mst.html",
        enrollment_success_template="enrollment/success--mst.html",
        help_template="core/includes/help--mst.html",
    )
    mst_agency.eligibility_types.set([mst_senior_type, mst_veteran_type, mst_courtesy_card_type])
    mst_agency.eligibility_verifiers.set([mst_senior_verifier, mst_veteran_verifier, mst_courtesy_card_verifier])

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
        index_template="core/index--sacrt.html",
        eligibility_index_template="eligibility/index--sacrt.html",
        enrollment_success_template="enrollment/success--sacrt.html",
    )
    sacrt_agency.eligibility_types.set([sacrt_senior_type])
    sacrt_agency.eligibility_verifiers.set([sacrt_senior_verifier])

    sbmtd_agency = TransitAgency.objects.create(
        slug="sbmtd",
        short_name=os.environ.get("SBMTD_AGENCY_SHORT_NAME", "SBMTD (sample)"),
        long_name=os.environ.get("SBMTD_AGENCY_LONG_NAME", "Santa Barbara MTD (sample)"),
        agency_id="sbmtd",
        merchant_id=os.environ.get("SBMTD_AGENCY_MERCHANT_ID", "sbmtd"),
        info_url="https://sbmtd.gov/taptoride/",
        phone="805-963-3366",
        active=os.environ.get("SBMTD_AGENCY_ACTIVE", "True").lower() == "true",
        private_key=client_private_key,
        public_key=client_public_key,
        jws_signing_alg=os.environ.get("SBMTD_AGENCY_JWS_SIGNING_ALG", "RS256"),
        payment_processor=sbmtd_payment_processor,
        index_template="core/index--sbmtd.html",
        eligibility_index_template="eligibility/index--sbmtd.html",
        enrollment_success_template="enrollment/success--sbmtd.html",
        help_template="core/includes/help--sbmtd.html",
    )
    sbmtd_agency.eligibility_types.set([sbmtd_senior_type, sbmtd_mobility_pass_type])
    sbmtd_agency.eligibility_verifiers.set([sbmtd_senior_verifier, sbmtd_mobility_pass_verifier])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
