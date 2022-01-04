describe("Payment Options page spec", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.contains("Payment Options").click();
  });

  it("Clicking on Payment Options takes user to Payment Options", () => {
    cy.location("pathname").should("eq", "/payment-options");
  });

  it("Contains a back link", () => {
    cy.contains("Go back").then(($e) => {
      expect($e).attr("href").eql("/");
    });
  });

  it("Allows user to go back", () => {
    cy.contains("Go back").click();

    cy.location("pathname").should("eq", "/");
  });
});
