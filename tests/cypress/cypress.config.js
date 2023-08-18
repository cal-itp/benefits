const { defineConfig } = require("cypress");

module.exports = defineConfig({
  downloadsFolder: "downloads",
  fixturesFolder: "fixtures",
  screenshotsFolder: "screenshots",
  viewportWidth: 1280,
  viewportHeight: 960,
  videosFolder: "videos",
  e2e: {
    // Adding custom task logging, for better a11y output
    // ref: https://docs.cypress.io/api/commands/task#Usage
    // https://github.com/component-driven/cypress-axe#using-the-violationcallback-argument
    setupNodeEvents(on, config) {
      on("task", {
        log(message) {
          console.log(message);
          return null;
        },
        table(message) {
          console.table(message);

          return null;
        },
      });
    },
    specPattern: "specs/**/*.cy.{js,jsx,ts,tsx}",
  },
});
