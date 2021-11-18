const agencies = require("../fixtures/transit-agencies");
const users = require("../fixtures/users.json");

describe("Confirms a user’s eligibility status", () => {
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

  it.skip("From the confirmation page, confirms an eligible user", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#name").type(users.eligible.name);
    cy.get("input[type='submit']").click();

    cy.contains("Great! You’re eligible for a discount!");
  });

  it("From the confirmation page, confirms an ineligible user", () => {
    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.get("input[type='submit']").click();

    cy.contains("We can’t confirm your age");
    cy.contains(
      "You may still be eligible for a discount, but we can’t verify your age"
    );
  });

  it("From the confirmation page, validates an invalid number/id field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("#name").type(users.invalidSub.name);
    cy.get("input[type='submit']").click();

    cy.contains("Check your input. The format looks wrong.");
    cy.get("#id_sub").then(($e) => {
      expect($e).to.have.css("border-color", "rgb(222, 12, 12)");
    });
  });

  it("From the confirmation page, validates an empty name field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("input[type='submit']").click();

    cy.get("input:invalid").should("have.length", 1);
  });
});
