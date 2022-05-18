const agencies = require("../../fixtures/transit-agencies");

describe("Single Verifier, No AuthProvider: Enrollment success page", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting DEFTl will go down the single verifier flow
    cy.contains(agencies[1].fields.short_name).click();
    cy.contains("Get started").click();
    cy.contains("Continue").click();
    // https://github.com/cypress-io/cypress/issues/18690
    cy.window().then((win) => (win.location.href = "/enrollment/success"));
  });

  it("Has the appropriate English copy for all flows", () => {
    cy.contains("Success! Your discount is now linked to your bank card.");
    cy.contains("You were not charged anything today.");
  });

  it("Has the appropriate Spanish copy for all flows", () => {
    cy.contains("Español").click();
    cy.contains(
      "¡Éxito! Su descuento está ahora vinculado a su tarjeta bancaria."
    );
    cy.contains("No se le ha cobrado nada hoy.");
  });
});
