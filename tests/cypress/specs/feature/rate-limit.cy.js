const agencies = require("../../fixtures/transit-agencies");
const users = require("../../fixtures/users.json");
const { eligibility_url, post_confirm } = require("../../plugins/eligibility");

describe("Rate limiting feature spec", () => {
  beforeEach(() => {
    cy.visit("/" + agencies[0].fields.slug);
    cy.visit(eligibility_url);
  });

  it("Limits excess requests", () => {
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
          // continue on non-200 status codes to check response
          post_confirm(csrfmiddlewaretoken, sub, name, false).then((res) => {
            if (i < RATE_LIMIT) {
              // allow up to API_RATE_LIMIT requests
              expect(res.status).to.eq(200);
            } else {
              // we've gone beyond API_RATE_LIMIT
              expect(res.status).to.eq(400);
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
          post_confirm(csrfmiddlewaretoken, sub, name, true).then((res) => {
            // these requests should all succeed
            expect(res.status).to.eq(200);
          });
        }
      });
  });
});
