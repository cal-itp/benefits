const endpoints = ["auth", "cgi", "eligibility/app", "login", "sample/api"];
const files = [".env", "wp-admin/login.php", "data.json", "secrets/prod.yaml"];

const visit = (partial_path) => {
  return cy.request({
    method: "GET",
    url: `/${partial_path}`,
    // allow cypress to continue on 404
    failOnStatusCode: false,
  });
};

const NOT_FOUND = 404;

describe("Scraper filtering spec", () => {
  endpoints.forEach((endpoint) => {
    it(`404s known scraper endpoint pattern: /${endpoint}`, () => {
      visit(endpoint).then((res) => {
        expect(res.status).to.eq(NOT_FOUND);
      });
    });
  });

  files.forEach((file) => {
    it(`404s known scraper file pattern: /${file}`, () => {
      visit(file).then((res) => {
        expect(res.status).to.eq(NOT_FOUND);
      });
    });
  });
});
