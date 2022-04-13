describe("Enrollment success page", () => {
  beforeEach(() => {
    cy.visit("/enrollment/success");
  });

  it("Has the appropriate English copy", () => {
    cy.contains("Success! Your discount is now linked to your bank card.");
  });

  it("Has the appropriate Spanish copy", () => {
    cy.contains("Español").click();
    cy.contains(
      "Felicidades! Su descuento ahora está vinculado a su tarjeta bancaria."
    );
  });
});
