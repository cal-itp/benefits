const users = require("../fixtures/users.json");
const helpers = require("./helpers");
const { eligibility_url, post_confirm } = require("../plugins/eligibility");

const SUCCESS_STATUS = 302;
const FAIL_STATUS = 503;

describe("Rate limiting feature spec", () => {
  beforeEach(() => {
    cy.visit("/");

    helpers.selectAgency();
    helpers.selectCourtesyCard();
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
        for (let i = 0; i < helpers.RATE_LIMIT; i++) {
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
    helpers.rateLimitWait();

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
        for (let i = 0; i < helpers.RATE_LIMIT; i++) {
          post_confirm(csrfmiddlewaretoken, sub, name, false).then((res) => {
            expect(res.status).to.eq(SUCCESS_STATUS);
            helpers.rateLimitWait();
          });
        }
      });
  });
});
