const helpers = require("../plugins/helpers");

const flow_selection_url = "/eligibility";

describe("Benefit selection", () => {
  beforeEach(() => {
    cy.visit("/");
    helpers.selectAgency();
  });

  it("User sees 5 radio buttons", () => {
    cy.get("input:radio").should("have.length", 5);
    cy.contains("Agency Card");
    cy.contains("65 years");
  });

  it("User must select a radio button, or else see a validation message", () => {
    cy.get("input:radio").should("have.length", 5);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.get("#form-flow-selection").submit();

    cy.url().should("include", flow_selection_url);
    cy.get("input:radio:checked").should("have.length", 0);
    cy.get("input:invalid").should("have.length", 5);
    cy.get("input:radio")
      .first()
      .invoke("prop", "validationMessage")
      .should("not.equal", "");
  });
});
