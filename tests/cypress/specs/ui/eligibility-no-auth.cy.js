const agencies = require("../../fixtures/transit-agencies");

const verifier_selection_url = "/eligibility";

describe("Multiple Verifier, no AuthProvider: Verifier selection page spec", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Get started").click();
  });

  it("User sees two radio buttons", () => {
    cy.get("input:radio").should("have.length", 2);
    cy.contains("MST Courtesy Cardholder");
    cy.contains("Senior Discount Program");
  });

  it("User must select a radio button, or else see a validation message", () => {
    cy.get("input:radio").should("have.length", 2);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.contains("Continue").click();
    cy.url().should("include", verifier_selection_url);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.get("input:invalid").should("have.length", 2);
    cy.get("input:radio")
      .first()
      .invoke("prop", "validationMessage")
      .should("not.equal", "");
  });
});
