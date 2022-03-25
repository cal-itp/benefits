const agencies = require("../../fixtures/transit-agencies");

const eligibility_url = "/eligibility/confirm";

describe("Eligibility confirmation page spec", () => {
  it.skip("User can navigate to the confirmation page", () => {
    cy.visit("/");
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Let’s do it!").click();
    cy.contains("Continue").click();
    cy.url().should("include", eligibility_url);
  });
});

describe("Eligibility confirmation form spec", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Let’s do it!").click();
    cy.contains("Continue").click();
  });

  it.skip("Has a driver’s license or ID number form label and corresponding field", () => {
    cy.get("input:focus").should("have.length", 0);
    cy.contains("CA driver’s license or ID number *").click();

    cy.get("input:focus").should("have.length", 1);
  });

  it.skip("Has a last name form label and corresponding form field", () => {
    cy.get("input:focus").should("have.length", 0);
    cy.contains("Last name (as it appears on ID) *").click();

    cy.get("input:focus").should("have.length", 1);
  });
});
