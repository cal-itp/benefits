const agencies = require("../fixtures/transit-agencies");

const agency = agencies[0].fields;

// from nginx.conf
export const RATE_LIMIT = 12;
// 12 requests/minute ==> 5 seconds in milliseconds
export const WAIT_TIME = (60 / RATE_LIMIT) * 1000;

export const rateLimitWait = () => {
  cy.wait(WAIT_TIME);
};

export const selectAgency = () => {
  cy.location("pathname").should("eq", "/");

  cy.contains("Choose your Provider").click();
  cy.contains(agency.long_name).click();

  cy.location("pathname").should("eq", `/eligibility/${agency.slug}`);

  return agency;
};

export const selectCourtesyCard = () => {
  cy.location("pathname").should("eq", `/eligibility/${agency.slug}`);

  // TODO find a more robust way to do this
  cy.get('#form-verifier-selection [type="radio"]').check("3");
  cy.get("#form-verifier-selection button[type='submit']").click();
  cy.contains("Continue").click();
};
