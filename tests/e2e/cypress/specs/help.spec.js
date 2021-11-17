const agencies = require("../fixtures/transit-agencies");

describe("Help page spec", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Clicking on Help takes user to Help", () => {
    cy.contains("Help").click();

    cy.location("pathname").should("eq", "/help");
  });

  it("Contains a back link", () => {
    cy.contains("Help").click();

    cy.contains("Go back").then(($e) => {
      expect($e).attr("href").eql("/");
    });
  });

  it("Allows user to go back", () => {
    cy.contains("Help").click();

    cy.contains("Go back").click();

    cy.location("pathname").should("eq", "/");
  });

  it("Has help information for all transit agencies", () => {
    cy.contains("Help").click();

    agencies.forEach(function (agency) {
      cy.contains(agency.fields.long_name);
      cy.contains(agency.fields.phone);
    });
  });

  it("Has help information for correct transit agency if clicking Help from a transit page", () => {
    let chosenAgency = agencies[0];
    let otherAgency = agencies[1];
    cy.contains(chosenAgency.fields.short_name).click();
    cy.contains("Help").click();

    cy.contains(chosenAgency.fields.long_name);
    cy.contains(chosenAgency.fields.phone);
    cy.should("not.contain", otherAgency.fields.long_name);
    cy.should("not.contain", otherAgency.fields.phone);
  });
});
