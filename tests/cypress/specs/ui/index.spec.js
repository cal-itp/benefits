const agencies = require("../../fixtures/transit-agencies");

describe("Index page spec", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Gives user transit provider options to click", () => {
    cy.contains("Choose your transit provider");
    cy.contains(agencies[0].fields.short_name).then(($e) => {
      expect($e)
        .attr("href")
        .to.include("/" + agencies[0].fields.slug);
    });
    cy.contains(agencies[1].fields.short_name).then(($e) => {
      expect($e)
        .attr("href")
        .to.include("/" + agencies[1].fields.slug);
    });
  });

  it("Clicking transit option link takes user to a transit provider page", () => {
    cy.contains(agencies[0].fields.short_name).click();

    cy.contains("Get started").then(($e) => {
      expect($e).attr("href").to.include("/eligibility");
    });
  });

  it("Has a help page link", () => {
    cy.contains("Help");
  });
});
