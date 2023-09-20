describe("Help page spec", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Allows user to go back", () => {
    cy.contains("Help").click();

    cy.contains("Go Back").click();

    cy.location("pathname").should("eq", "/");
  });

  it("Has headers that all have ids to be used for anchor links", () => {
    cy.contains("Help").click();

    cy.get("h2").each(($el, index, $list) => {
      cy.wrap($el[0].attributes).its("id").should("exist");
    });
  });
});
