const helpers = require("./helpers");

const verifier_selection_url = "/eligibility";

describe("Benefit selection", () => {
  beforeEach(() => {
    cy.visit("/");
    helpers.selectAgency();
  });

  it("User sees two radio buttons", () => {
    cy.get("input:radio").should("have.length", 2);
    cy.contains("Courtesy Card");
    cy.contains("65 years");
  });

  it("User must select a radio button, or else see a validation message", () => {
    cy.get("input:radio").should("have.length", 2);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.get("#form-verifier-selection").submit();

    cy.url().should("include", verifier_selection_url);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.get("input:invalid").should("have.length", 2);
    cy.get("input:radio")
      .first()
      .invoke("prop", "validationMessage")
      .should("not.equal", "");
  });
});
