const endpoints = [
  "cgi",
  "cpaneladmin/",
  "eligibility/app",
  "n/jenkins/script",
  "sample/api",
];
const files = [
  ".env",
  "data.json",
  "n/SWNetPerfMon.db.i18n.ashx",
  "robots.txt",
  "secrets/prod.yaml",
  "sp/startSLO.ping",
  "wp-admin/login.php",
];
const targets = endpoints.concat(files);

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
  targets.forEach((target) => {
    it(`nginx returns 404 for known scraper target pattern: /${target}`, () => {
      visit(target).then((res) => {
        expect(res.status).to.eq(NOT_FOUND);
        expect(res.body).to.contain("nginx");
        expect(res.body).not.to.contain("Cal-ITP");
      });
    });
  });
});
