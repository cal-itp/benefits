module.exports = (on, config) => {
  // add OS environment variables into Cypress.env
  config.env = config.env || {};
  config.env.DJANGO_RATE_LIMIT = 5;
  config.env.DJANGO_RATE_LIMIT_PERIOD = 60;

  return config;
};
