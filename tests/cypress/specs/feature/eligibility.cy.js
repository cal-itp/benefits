const helpers = require("../helpers");
const users = require("../../fixtures/users.json");

describe("Eligibility confirmation flow", () => {
  beforeEach(() => {
    cy.visit("/");

    helpers.selectAgency();
    helpers.selectCourtesyCard();
  });

  it("Confirms an eligible user", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#name").type(users.eligible.name);
    cy.get("#form-eligibility-verification button[type='submit']").click();

    cy.contains("Your eligibility is confirmed!");
  });

  it("Rejects an ineligible user", () => {
    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.get("#form-eligibility-verification button[type='submit']").click();

    cy.contains("could not be verified");
  });

  it("Validates an empty name field", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#form-eligibility-verification button[type='submit']").click();

    cy.get("input:invalid").should("have.length", 1);
  });
});
