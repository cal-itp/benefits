const eligibility_url = "/eligibility/confirm";

/**
 * Submit the eligibility confirmation form using a direct POST request.
 * @param {string} csrfmiddlewaretoken Django CSRF token from the form hidden input.
 * @param {string} sub DL/ID number
 * @param {string} name Last name
 * @param {boolean} failOnStatusCode True to fail the cy.request() for non-200 response codes. False to continue for non-200 codes.
 * @returns The result of cy.request()
 */
function post_confirm(csrfmiddlewaretoken, sub, name, failOnStatusCode) {
  return cy.request({
    method: "POST",
    url: eligibility_url,
    followRedirect: false,
    failOnStatusCode: failOnStatusCode,
    // submit body as application/x-www-form-urlencoded
    form: true,
    // the same body a user-initiated form-submission sends
    body: {
      csrfmiddlewaretoken,
      sub,
      name,
    },
  });
}

export { eligibility_url, post_confirm };
