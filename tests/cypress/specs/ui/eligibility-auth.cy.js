const agencies = require("../../fixtures/transit-agencies");

const eligibility_start_url = "/eligibility/start";

describe("Multiple verifier, with AuthProvider: Eligibility start page spec", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Get started").click();
    // Selecting first radio button, Senior Discount Program, will go down Login.gov flow
    cy.get("input:radio").first().click();
    cy.contains("Continue").click();
  });

  it("Has the correct URL", () => {
    cy.url().should("include", eligibility_start_url);
  });

  it("Has the correct copy for Senior Discount Program instructions", () => {
    cy.contains("You will need a few items to connect your discount:");
    cy.contains("Your bank card details");
    cy.get(".media-list").children().should("have.length", 2);
  });

  it("Has the correct copy for Authorization instructions", () => {
    cy.get(".media-list").contains(
      "A Login.gov account with identity verification",
    );
    cy.contains("Login.gov is a safe way to sign in to government services.");
    cy.contains("Learn more about Login.gov");
  });

  it("Has a Login.gov button label", () => {
    cy.contains("Get started with");
  });
});
