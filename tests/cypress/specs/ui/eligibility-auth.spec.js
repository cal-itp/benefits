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
    cy.contains(
      "Great, you’ll need to do three things to link your transit discount to your bank card."
    );
    cy.contains("Provide your California ID number");
    cy.get(".media-list").children().should("have.length", 3);
  });

  it("Has the correct copy for Authorization instructions", () => {
    cy.get(".media-list").contains("Sign in to your Login.gov account");
    cy.contains(
      "You will be able to create an account if you’re not already signed up."
    );
    cy.contains("Learn more about Login.gov");
  });

  it("Has a Login.gov button label", () => {
    cy.contains("Create an account or sign in with");
  });
});
