import "cypress-axe";

const helpers = require("../plugins/helpers");
const users = require("../fixtures/users.json");

describe("Accessibility specs", function () {
  beforeEach(() => {
    cy.injectAxe();
  });

  context("Landing page", function () {
    before(() => {
      cy.visit("/");
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
    });
  });

  context("Agency index page", function () {
    before(() => {
      cy.visit("/mst");
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
    });
  });

  context("Help page", function () {
    before(() => {
      cy.visit("/");
      cy.contains("Help").click();
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
    });
  });

  context("Eligibility page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
    });
  });

  context("Eligibility start page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      cy.contains("Choose this Benefit").click();
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
    });
  });

  context("Agency Card form page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      helpers.selectCourtesyCard();
    });
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
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
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
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
    it("has no critical a11y errors", () => {
      cy.checkA11y(null, {
        includedImpacts: ["critical"],
      });
    });
  });
});
