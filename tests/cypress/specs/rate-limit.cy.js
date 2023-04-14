const agencies = require("../fixtures/transit-agencies");
const users = require("../fixtures/users.json");
const { eligibility_url, post_confirm } = require("../plugins/eligibility");

const RATE_LIMIT = 12;
// 5 seconds in milliseconds => allows 12 requests/minute
const WAIT_TIME = 5 * 1000;
const SUCCESS_STATUS = 302;
const FAIL_STATUS = 503;

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

    // csrfmiddlewaretoken value needed to enable automated form submissions
    // there could be multiple forms on the page, so get() the one with the
    // action we are interested in
    cy.get(`form[action='${eligibility_url}'`)
      .find("input[name='csrfmiddlewaretoken']")
      .invoke("attr", "value")
      .then((csrfmiddlewaretoken) => {
        // make successive requests with no wait time
        for (let i = 0; i < RATE_LIMIT; i++) {
          post_confirm(csrfmiddlewaretoken, sub, name, false).then((res) => {
            // the first request should succeed, subsequent should fail
            if (i == 0) {
              expect(res.status).to.eq(SUCCESS_STATUS);
            } else {
              expect(res.status).to.eq(FAIL_STATUS);
            }
          });
        }
      });
  });

  it("Allows requests with enough time in between", () => {
    // start with a wait, since the previous test already triggered the limit
    cy.wait(WAIT_TIME);

    const sub = users.ineligible.sub;
    const name = users.ineligible.name;

    // csrfmiddlewaretoken value needed to enable automated form submissions
    // there could be multiple forms on the page, so get() the one with the
    // action we are interested in
    cy.get(`form[action='${eligibility_url}'`)
      .find("input[name='csrfmiddlewaretoken']")
      .invoke("attr", "value")
      .then((csrfmiddlewaretoken) => {
        // make successive requests with time in between
        for (let i = 0; i < RATE_LIMIT; i++) {
          post_confirm(csrfmiddlewaretoken, sub, name, false).then((res) => {
            expect(res.status).to.eq(SUCCESS_STATUS);
            cy.wait(WAIT_TIME);
          });
        }
      });
  });
});
