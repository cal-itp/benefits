const agencies = require("../../fixtures/transit-agencies");

describe("Single Verifier, No AuthProvider: Enrollment success page", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting DEFTl will go down the single verifier flow
    cy.contains(agencies[1].fields.short_name).click();
    cy.contains("Get started").click();
    cy.contains("Continue").click();
    cy.visit("/enrollment/success");
  });

  it("Has the appropriate English copy for all flows", () => {
    cy.contains("Success! Your discount is now linked to your bank card.");
    cy.contains("You were not charged anything today.");
  });

  it("Has the appropriate Spanish copy for all flows", () => {
    cy.contains("Español").click();
    cy.contains(
      "Felicidades! Su descuento ahora está vinculado a su tarjeta bancaria."
    );
    cy.contains("No te cobraron nada hoy.");
  });
});

describe.skip("Multiple Verifier, with AuthProvider: Enrollment success page", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Get started").click();
    // Selecting Senior Discount will go down the auth provider flow
    cy.get("input:radio").first().click();
    cy.contains("Continue").click();
    cy.contains("Create an account or sign in with");
    cy.visit("/enrollment/success");
  });

  it("Has the appropriate English copy for all flows and Login.gov instructions", () => {
    cy.contains("Success! Your discount is now linked to your bank card.");
    cy.contains("You were not charged anything today.");
  });

  it("Has the appropriate Spanish copy for all flows and Login.gov instructions", () => {
    cy.contains("Español").click();
    cy.contains(
      "Felicidades! Su descuento ahora está vinculado a su tarjeta bancaria."
    );
    cy.contains("No te cobraron nada hoy.");
  });
});
