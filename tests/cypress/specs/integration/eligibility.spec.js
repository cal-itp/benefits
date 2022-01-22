const agencies = require("../../fixtures/transit-agencies");
const users = require("../../fixtures/users.json");

const eligibility_url = "/eligibility/confirm";

describe("Eligibility Confirmation flow", () => {
  beforeEach(() => {
    cy.visit("/" + agencies[0].fields.slug);
    cy.visit(eligibility_url);
  });

  it("Confirms an eligible user", () => {
    cy.get("#sub").type(users.eligible.sub);
    cy.get("#name").type(users.eligible.name);
    cy.get("input[type='submit']").click();

    cy.contains("Great! You’re eligible for a discount!");
  });

  it("Rejects an ineligible user", () => {
    cy.get("#sub").type(users.ineligible.sub);
    cy.get("#name").type(users.ineligible.name);
    cy.get("input[type='submit']").click();

    cy.contains("We can’t confirm your age");
    cy.contains(
      "You may still be eligible for a discount, but we can’t verify your age"
    );
  });

  it("Validates an invalid number/id field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("#name").type(users.invalidSub.name);
    cy.get("input[type='submit']").click();

    cy.contains("Check your input. The format looks wrong.");
    cy.get("#id_sub").then(($e) => {
      expect($e).to.have.css("border-color", "rgb(222, 12, 12)");
    });
  });

  it("Validates an empty name field", () => {
    cy.get("#sub").type(users.invalidSub.sub);
    cy.get("input[type='submit']").click();

    cy.get("input:invalid").should("have.length", 1);
  });

  it("Rate limits excess requests", () => {
    const sub = users.invalidSub.sub;
    const name = users.invalidSub.name;

    // start by making 5 times as many requests as allowed
    const RATE_LIMIT = Cypress.env("DJANGO_RATE_LIMIT");
    const N_REQUESTS = RATE_LIMIT * 5;

    // csrfmiddlewaretoken value needed to enable automated form submissions
    // there could be multiple forms on the page, so get() the one with the
    // action we are interested in
    cy.get(`form[action='${eligibility_url}'`)
      .find("input[name='csrfmiddlewaretoken']")
      .invoke("attr", "value")
      .then((csrfmiddlewaretoken) => {
        // make excess requests
        for (let i = 0; i < N_REQUESTS; i++) {
          cy.request({
            method: "POST",
            url: eligibility_url,
            followRedirect: false,
            // don't raise an exception for non-success status codes so we can inspect the response
            failOnStatusCode: false,
            // submit body as application/x-www-form-urlencoded
            form: true,
            // the same body a user-initiated form-submission sends
            body: {
              csrfmiddlewaretoken,
              sub,
              name,
            },
          }).then((res) => {
            if (i < RATE_LIMIT) {
              // allow up to API_RATE_LIMIT requests
              expect(res.status).to.eq(200);
            } else {
              // we've gone beyond API_RATE_LIMIT
              expect(res.status).to.eq(429);
            }
          });
        }

        // now wait for the rate limit to refresh
        const RATE_LIMIT_PERIOD = parseInt(
          Cypress.env("DJANGO_RATE_LIMIT_PERIOD")
        );
        // Cypress expects milliseconds, the rate limit period is expressed in seconds
        cy.wait(RATE_LIMIT_PERIOD * 1000);

        // and try again with a reasonable number of requests
        for (let i = 0; i < RATE_LIMIT - 1; i++) {
          cy.request({
            method: "POST",
            url: eligibility_url,
            followRedirect: false,
            // we expect all of these requests to succeed
            failOnStatusCode: true,
            // submit body as application/x-www-form-urlencoded
            form: true,
            // the same body a user-initiated form-submission sends
            body: {
              csrfmiddlewaretoken,
              sub,
              name,
            },
          }).then((res) => {
            // these requests should all succeed
            expect(res.status).to.eq(200);
          });
        }
      });
  });
});
