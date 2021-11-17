const agencies = require("../fixtures/transit-agencies.json");

describe("Index page spec", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("Gives user transit provider options to click", () => {
    cy.contains("Choose your transit provider");
    cy.contains(agencies[0].short_name).then(($e) => {
      expect($e)
        .attr("href")
        .to.include("/" + agencies[0].slug);
    });
    cy.contains(agencies[1].short_name).then(($e) => {
      expect($e)
        .attr("href")
        .to.include("/" + agencies[1].slug);
    });
  });

  it("Clicking transit option link takes user to a transit provider page", () => {
    cy.contains(agencies[0].short_name).click();

    cy.contains("Let’s do it!").then(($e) => {
      expect($e).attr("href").to.include("/eligibility");
    });
  });

  it("Has a payment options page link", () => {
    cy.contains("Payment Options");
  });

  it("Has a help page link", () => {
    cy.contains("Help");
  });
});
