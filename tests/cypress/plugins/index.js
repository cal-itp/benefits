module.exports = (on, config) => {
  // add OS environment variables into Cypress.env
  config.env = config.env || {};
  config.env.DJANGO_RATE_LIMIT = process.env.DJANGO_RATE_LIMIT;
  config.env.DJANGO_RATE_LIMIT_PERIOD = process.env.DJANGO_RATE_LIMIT_PERIOD;

  return config;
};
