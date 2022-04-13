describe("Enrollment success page", () => {
  beforeEach(() => {
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

  it("If there is an AuthProvider, show the Login.gov sign out instructions", () => {});
});
