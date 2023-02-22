const helpers = require("./helpers");

describe("Spanish language", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Gives user Spanish language option", () => {
    cy.get("#header").should("contain", "Español");
    cy.get("#header").should("not.contain", "English");
  });

  it("Changes the language to Spanish and does not change URL", () => {
    cy.location("pathname").should("eq", "/");

    cy.contains("Español").click();

    cy.get("#header").should("not.contain", "Español");
    cy.get("#header").should("contain", "English");
    cy.location("pathname").should("eq", "/");
  });

  it("Changes the language from Spanish back to English", () => {
    cy.contains("Español").click();

    cy.get("#header").should("not.contain", "Español");
    cy.get("#header").should("contain", "English");
    cy.contains("English").click();

    cy.get("#header").should("contain", "Español");
    cy.get("#header").should("not.contain", "English");
  });

  it("Changes the language to Spanish from any page", () => {
    const agency = helpers.selectAgency();

    cy.contains("Español").click();

    cy.get("#header").should("not.contain", "Español");
    cy.get("#header").should("contain", "English");
    cy.location("pathname").should("eq", `/eligibility/${agency.slug}`);
  });
});
