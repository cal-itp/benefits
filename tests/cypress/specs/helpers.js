const agencies = require("../fixtures/transit-agencies");

const agency = agencies[0].fields;

export const selectAgency = () => {
  cy.location("pathname").should("eq", "/");

  cy.contains("Choose Your Provider").click();
  cy.contains(agency.long_name).click();
};

export const selectCourtesyCard = () => {
  cy.location("pathname").should("eq", `/eligibility/${agency.slug}`);

  // TODO find a more robust way to do this
  cy.get('#form-verifier-selection [type="radio"]').check("2");
  cy.get("#form-verifier-selection button[type='submit']").click();
  cy.contains("Continue").click();
};
