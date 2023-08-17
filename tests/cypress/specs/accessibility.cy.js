import "cypress-axe";
import "@cypress-audit/pa11y/commands";
import "@cypress-audit/lighthouse/commands";

const helpers = require("../plugins/helpers");
const users = require("../fixtures/users.json");
const a11yOpts = {
  includedImpacts: ["critical"],
};
const pa11yOpts = {
  ignore: ["WCAG2AA.Principle1.Guideline1_4.1_4_3.G18.Fail"], // Color Contrast
  threshold: 4, // Color Contrast for Skip Nav, some other text/buttons
};
const lighthouseOpts = {
  accessibility: 100,
  "best-practices": 100,
};

describe("Accessibility specs", function () {
  beforeEach(() => {
    cy.injectAxe();
  });

  context("Landing page", function () {
    before(() => {
      cy.visit("/");
    });
    it("has no critical a11y errors", () => {
      // cy.pa11y(pa11yOpts);
      // cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
    });
  });

  context("Agency index page", function () {
    before(() => {
      cy.visit("/mst");
    });
    xit("has no critical a11y errors", () => {
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
    });
  });

  context("Help page", function () {
    before(() => {
      cy.visit("/");
      cy.contains("Help").click();
    });
    xit("has no critical a11y errors", () => {
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
    });
  });

  context("Eligibility page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
    });
    xit("has no critical a11y errors", () => {
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
    });
  });

  context("Eligibility start page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      cy.contains("Choose this Benefit").click();
    });
    xit("has no critical a11y errors", () => {
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
    });
  });

  context("Agency Card form page", function () {
    before(() => {
      cy.visit("/");
      helpers.selectAgency();
      helpers.selectCourtesyCard();
    });
    xit("has no critical a11y errors", () => {
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
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
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
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
      cy.pa11y(pa11yOpts);
      cy.lighthouse(lighthouseOpts);
      cy.checkA11y(null, a11yOpts);
    });
  });
});
