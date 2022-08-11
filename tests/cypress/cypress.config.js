const { defineConfig } = require("cypress");

module.exports = defineConfig({
  downloadsFolder: "downloads",
  fixturesFolder: "fixtures",
  screenshotsFolder: "screenshots",
  viewportWidth: 1280,
  viewportHeight: 960,
  videosFolder: "videos",
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require("./plugins/index.js")(on, config);
    },
    specPattern: "specs/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: false,
  },
});
