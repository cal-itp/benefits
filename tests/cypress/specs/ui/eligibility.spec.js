const agencies = require("../../fixtures/transit-agencies");

describe("Eligibility Confirmation page spec", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Let’s do it!").click();
    cy.contains("Ready to continue").click();
  });

  it("Takes user to eligibility confirmation page", () => {
    cy.contains("Let’s see if we can confirm your age");
    cy.contains("CA driver’s license or ID number *");
  });

  it("Confirmation page has a form with a driver’s license or ID number form label and corresponding form field", () => {
    cy.get("input:focus").should("have.length", 0);
    cy.contains("CA driver’s license or ID number *").click();

    cy.get("input:focus").should("have.length", 1);
  });

  it("Confirmation page has a form with a lastname form label and corresponding form field", () => {
    cy.get("input:focus").should("have.length", 0);
    cy.contains("Last name (as it appears on ID) *").click();

    cy.get("input:focus").should("have.length", 1);
  });
});
