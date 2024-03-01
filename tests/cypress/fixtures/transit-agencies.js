// extract the "fields" object from the first TransitAgency model fixture

const local_fixtures = require("../../../benefits/core/migrations/local_fixtures.json");
const local_agencies = local_fixtures.filter(
  (fixture) => fixture.model == "core.transitagency",
);
const first_agency_model = local_agencies[0];
const agencies = [{ fields: first_agency_model.fields }];

export default agencies;
