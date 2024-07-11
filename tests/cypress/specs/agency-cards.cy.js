const helpers = require("../plugins/helpers");
const users = require("../fixtures/users.json");

describe("Agency Cards", () => {
  beforeEach(() => {
    cy.visit("/");

    helpers.selectAgency();
    helpers.selectAgencyCard();
  });

  it("Confirms an eligible user", () => {
    helpers.rateLimitWait();

    cy.get("#sub").type(users.eligible.sub);
    cy.get("#name").type(users.eligible.name);
    cy.get("#form-eligibility-verification button[type='submit']").click();

    cy.contains("We found your record!");
  });

  it("Rejects an ineligible user", () => {
    helpers.rateLimitWait();

    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.get("#form-eligibility-verification button[type='submit']").click();

    cy.contains("may not have been entered correctly");
  });

  it("Validates an empty name field", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#form-eligibility-verification button[type='submit']").click();

    cy.get("input:invalid").should("have.length", 1);
  });
});
