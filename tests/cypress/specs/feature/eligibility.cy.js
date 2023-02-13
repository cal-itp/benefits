const agencies = require("../../fixtures/transit-agencies");
const users = require("../../fixtures/users.json");

describe("Eligibility confirmation flow", () => {
  beforeEach(() => {
    cy.visit("/");

    // agency selection
    cy.contains("Choose Your Provider").click();
    cy.contains(agencies[0].fields.long_name).click();

    // select Courtesy Card
    // TODO find a more robust way to do this
    cy.get('#form-verifier-selection [type="radio"]').check("2");
    cy.get("#form-verifier-selection button[type='submit']").click();
    cy.contains("Continue").click();
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
