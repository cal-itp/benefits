const agencies = require("../../fixtures/transit-agencies");

const verifier_selection_url = "/eligibility";
const eligibility_confirm_url = "/eligibility/confirm";
const eligibility_start_url = "/eligibility/start";

describe("Single verifier: Eligibility confirmation page spec", () => {
  it("User can navigate to the confirmation page", () => {
    cy.visit("/");
    // Selecting DEFTl will go down the single verifier flow
    cy.contains(agencies[1].fields.short_name).click();
    cy.contains("Get started").click();
    cy.contains("Continue").click();
    cy.url().should("include", eligibility_confirm_url);
  });
});

describe("Multiple Verifier, no AuthProvider: Verifier selection page spec", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Get started").click();
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
    cy.get("input:radio").last().click();
    cy.get("input:radio:checked").should("have.length", 1);
    cy.contains("Continue").click();
    cy.url().should("include", eligibility_start_url);
  });
});

describe("Multiple verifier, no AuthProvider: Eligibility confirmation form spec", () => {
  beforeEach(() => {
    cy.visit("/");
    // Selecting ABC will go down the multiple verifier flow
    cy.contains(agencies[0].fields.short_name).click();
    cy.contains("Get started").click();
    // Selecting last radio button, MST Courtesy Cardholder will go down flow without authorization step
    cy.get("input:radio").last().click();
    cy.contains("Continue").click();
  });

  it("Has a Courtesy Card number form label and corresponding field", () => {
    cy.contains(
      "You’ll need to do two things to link your transit discount to your bank card."
    );
    cy.get(".media-list").children().should("have.length", 2);
    cy.contains("Continue").click();
    cy.get("input:focus").should("have.length", 0);
    cy.contains("MST Courtesy Card number *").click();

    cy.get("input:focus").should("have.length", 1);
    cy.url().should("include", eligibility_confirm_url);
  });

  it("Has a last name form label and corresponding form field", () => {
    cy.contains("Your MST Courtesy Card");
    cy.contains("An active card that has not expired");
    cy.contains("Continue").click();
    cy.get("input:focus").should("have.length", 0);
    cy.contains("Last name (as it appears on Courtesy Card) *").click();

    cy.get("input:focus").should("have.length", 1);
    cy.url().should("include", eligibility_confirm_url);
  });
});
