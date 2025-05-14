from dataclasses import dataclass
import pytest


@dataclass
class AgencyFlow:
    agency: str
    flow: str


@dataclass
class AgencyCardCredentials:
    sub: str
    name: str


@dataclass
class PaymentCard:
    cardholder_name: str
    card_number: str
    expiration: str
    security_code: str


@pytest.fixture
def browser_context_args():
    return dict(user_agent="cal-itp/benefits-smoke-test")


@pytest.fixture
def agency_card_flows():
    return [
        (
            AgencyFlow(agency="California State Transit", flow="Agency Cardholder"),
            AgencyCardCredentials(sub="71162", name="Box"),
        ),
        (
            AgencyFlow(agency="Monterey-Salinas Transit", flow="Courtesy Card"),
            AgencyCardCredentials(sub="71162", name="Box"),
        ),
        (
            AgencyFlow(agency="Santa Barbara MTD", flow="Reduced Fare Mobility ID"),
            AgencyCardCredentials(sub="1234", name="Barbara"),
        ),
    ]


@pytest.fixture
def valid_payment_card():
    return PaymentCard(
        cardholder_name="Test User",
        card_number="4111 1111 1111 1111",
        expiration="12/34",
        security_code="123",
    )
