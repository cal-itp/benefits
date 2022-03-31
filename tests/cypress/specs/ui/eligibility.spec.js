const agencies = require("../../fixtures/transit-agencies");

const verifier_selection_url = "/eligibility";
const eligibility_confirm_url = "/eligibility/confirm";
const eligibility_start_url = "/eligibility/start";

describe.skip("Single verifier: Eligibility confirmation page spec", () => {
  it("User can navigate to the confirmation page", () => {
    cy.visit("/");
    // Selecting DEFTl will go down the single verifier flow
    cy.contains(agencies[1].fields.short_name).click();
    cy.contains("Let’s do it!").click();
    cy.contains("Continue").click();
    cy.url().should("include", eligibility_confirm_url);
  });
});

describe("Multiple Verifier: Verifier selection page spec", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Let’s do it!").click();
  });

  it("User can navigate to the Verifier Selection page", () => {
    cy.contains("Continue");
    cy.url().should("include", verifier_selection_url);
    cy.contains("Select the discount option that best applies to you:");
  });

  it("User sees two radio buttons", () => {
    cy.get("input:radio").should("have.length", 2);
    cy.contains("MST Courtesy Cardholder");
    cy.contains("Senior Discount Program");
  });

  it("User must select a radio button, or else see a validation message", () => {
    cy.get("input:radio").should("have.length", 2);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.contains("Continue").click();
    cy.url().should("include", verifier_selection_url);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.get("input:invalid").should("have.length", 2);
    cy.get("input:radio")
      .first()
      .invoke("prop", "validationMessage")
      .should("not.equal", "");
  });

  it("User can click a radio button and click Continue", () => {
    cy.get("input:radio:checked").should("have.length", 0);
    cy.contains("Senior Discount Program").click();
    cy.get("input:radio:checked").should("have.length", 1);
    cy.contains("Continue").click();
    cy.url().should("include", eligibility_start_url);
  });
});

describe.skip("Multiple verifier: Eligibility confirmation form spec", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Let’s do it!").click();
    cy.contains("Senior Discount Program").click();
    cy.contains("Continue").click();
    cy.contains("Great, you’ll need two things before we get started...");
  });

  it("Has a driver’s license or ID number form label and corresponding field", () => {
    cy.contains("Continue").click();
    cy.get("input:focus").should("have.length", 0);
    cy.contains("CA driver’s license or ID number *").click();

    cy.get("input:focus").should("have.length", 1);
    cy.url().should("include", eligibility_confirm_url);
  });

  it("Has a last name form label and corresponding form field", () => {
    cy.contains("Continue").click();
    cy.get("input:focus").should("have.length", 0);
    cy.contains("Last name (as it appears on ID) *").click();

    cy.get("input:focus").should("have.length", 1);
    cy.url().should("include", eligibility_confirm_url);
  });
});
