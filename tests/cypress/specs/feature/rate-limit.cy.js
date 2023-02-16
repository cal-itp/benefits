const agencies = require("../../fixtures/transit-agencies");
const users = require("../../fixtures/users.json");
const { eligibility_url, post_confirm } = require("../../plugins/eligibility");

describe("Rate limiting feature spec", () => {
  beforeEach(() => {
    cy.visit("/");

    // agency selection
    cy.contains("Choose Your Provider").click();
    cy.contains(agencies[0].fields.long_name).click();

    // select Courtesy Card
    // TODO find a more robust way to do this
    cy.get('#form-verifier-selection [type="radio"]').check("2");
    cy.get("#form-verifier-selection button[type='submit']").click();
    cy.contains("Continue").click();
  });

  it("Limits excess requests", () => {
    const sub = users.ineligible.sub;
    const name = users.ineligible.name;

    // start by making 5 times as many requests as allowed
    // these should match the defaults in settings.py
    const RATE_LIMIT = 5;
    const N_REQUESTS = RATE_LIMIT * 5;
    const RATE_LIMIT_PERIOD = 60;

    const SUCCESS_STATUS = 302;

    // csrfmiddlewaretoken value needed to enable automated form submissions
    // there could be multiple forms on the page, so get() the one with the
    // action we are interested in
    cy.get(`form[action='${eligibility_url}'`)
      .find("input[name='csrfmiddlewaretoken']")
      .invoke("attr", "value")
      .then((csrfmiddlewaretoken) => {
        // make excess requests
        for (let i = 0; i < N_REQUESTS; i++) {
          // continue on non-successful status codes to check response
          post_confirm(csrfmiddlewaretoken, sub, name, false).then((res) => {
            if (i < RATE_LIMIT) {
              // allow up to API_RATE_LIMIT requests
              expect(res.status).to.eq(SUCCESS_STATUS);
            } else {
              // we've gone beyond API_RATE_LIMIT
              expect(res.status).to.eq(400);
            }
          });
        }

        // now wait for the rate limit to refresh
        // Cypress expects milliseconds, the rate limit period is expressed in seconds
        cy.wait(RATE_LIMIT_PERIOD * 1000);

        // and try again with a reasonable number of requests
        for (let i = 0; i < RATE_LIMIT - 1; i++) {
          post_confirm(csrfmiddlewaretoken, sub, name, true).then((res) => {
            // these requests should all succeed
            expect(res.status).to.eq(SUCCESS_STATUS);
          });
        }
      });
  });
});
