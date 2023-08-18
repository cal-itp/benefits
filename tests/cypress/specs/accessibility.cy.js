import "cypress-axe";

const helpers = require("../plugins/helpers");
const users = require("../fixtures/users.json");
const opts = {
  includedImpacts: ["critical"],
};

describe("Accessibility specs", function () {
  context("Landing page", function () {
    before(() => {
      cy.visit("/");
      cy.injectAxe();
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y();
    });
  });

  context("Agency index page", function () {
    before(() => {
      cy.visit("/mst");
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });

  context("Help page", function () {
    before(() => {
      cy.visit("/");
      cy.contains("Help").click();
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });

  context("Eligibility page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });

  context("Eligibility start page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      cy.contains("Choose this Benefit").click();
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });

  context("Agency Card form page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      helpers.selectCourtesyCard();
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });

  context("Enrollment index page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      helpers.selectCourtesyCard();
      cy.get("#sub").type(users.eligible.sub);
      cy.get("#name").type(users.eligible.name);
      cy.get("#form-eligibility-verification button[type='submit']").click();
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });

  context("Enrollment success page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      helpers.selectCourtesyCard();
      cy.get("#sub").type(users.eligible.sub);
      cy.get("#name").type(users.eligible.name);
      cy.get("#form-eligibility-verification button[type='submit']").click();
      cy.visit("/enrollment/success");
    });
    xit("has no critical a11y errors", () => {
      cy.checkA11y(null, opts);
    });
  });
});
