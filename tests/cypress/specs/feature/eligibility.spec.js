const agencies = require("../../fixtures/transit-agencies");
const users = require("../../fixtures/users.json");

describe("Multiple verifier: Eligibility confirmation flow", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Get started").click();
    cy.contains("Continue").click();
    cy.contains("MST Courtesy Cardholder").click();
    cy.contains("Continue").click();
    cy.contains("Continue").click();
  });

  it("Confirms an eligible user", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#name").type(users.eligible.name);
    cy.contains("Check status").click();

    cy.contains("Great! You’re eligible for a discount!");
  });

  it("Rejects an ineligible user", () => {
    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.contains("Check status").click();

    cy.contains("We couldn’t locate you in our system");
  });

  it("Validates an invalid number/id field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("#name").type(users.invalidSub.name);
    cy.contains("Check status").click();

    cy.contains("Check your input. The format looks wrong.");
    cy.get("#id_sub").then(($e) => {
      expect($e).to.have.css("border-color", "rgb(222, 12, 12)");
    });
  });

  it("Validates an empty name field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.contains("Check status").click();

    cy.get("input:invalid").should("have.length", 1);
  });
});

describe("Single verifier: Eligibility confirmation flow", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting DEFtl will go down the multiple verifier flow
    cy.contains(agencies[1].fields.short_name).click();
    cy.contains("Get started").click();
    cy.contains("Continue").click();
  });

  it("Confirms an eligible user", () => {
    cy.get("#sub").type("B2345678");
    cy.get("#name").type("Hernandez");
    cy.contains("Check status").click();

    cy.contains("Great! You’re eligible for a discount!");
  });

  it("Rejects an ineligible user", () => {
    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.contains("Check status").click();

    cy.contains("We couldn’t locate you in our system");
  });

  it("Validates an invalid number/id field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("#name").type(users.invalidSub.name);
    cy.contains("Check status").click();

    cy.contains("Check your input. The format looks wrong.");
    cy.get("#id_sub").then(($e) => {
      expect($e).to.have.css("border-color", "rgb(222, 12, 12)");
    });
  });

  it("Validates an empty name field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.contains("Check status").click();

    cy.get("input:invalid").should("have.length", 1);
  });
});
