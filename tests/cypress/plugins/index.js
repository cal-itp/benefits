module.exports = (on, config) => {
  // add OS environment variables into Cypress.env
  config.env = config.env || {};

  return config;
};
