const agencies = require("../../fixtures/transit-agencies");
const users = require("../../fixtures/users.json");

const eligibility_url = "/eligibility/confirm";

describe("Eligibility confirmation flow", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Let’s do it!").click();
    cy.contains("Ready to continue").click();
  });

  it("Confirms an eligible user", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#name").type(users.eligible.name);
    cy.get("input[type='submit']").click();

    cy.contains("Great! You’re eligible for a discount!");
  });

  it("Rejects an ineligible user", () => {
    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.get("input[type='submit']").click();

    cy.contains("We can’t confirm your age");
    cy.contains(
      "You may still be eligible for a discount, but we can’t verify your age"
    );
  });

  it("Validates an invalid number/id field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("#name").type(users.invalidSub.name);
    cy.get("input[type='submit']").click();

    cy.contains("Check your input. The format looks wrong.");
    cy.get("#id_sub").then(($e) => {
      expect($e).to.have.css("border-color", "rgb(222, 12, 12)");
    });
  });

  it("Validates an empty name field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("input[type='submit']").click();

    cy.get("input:invalid").should("have.length", 1);
  });
});
