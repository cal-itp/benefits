const { defineConfig } = require("cypress");
const { pa11y, prepareAudit } = require("@cypress-audit/pa11y");
const { lighthouse } = require("@cypress-audit/lighthouse");

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
      on("before:browser:launch", (browser = {}, launchOptions) => {
        prepareAudit(launchOptions);
      });

      on("task", {
        lighthouse: lighthouse(),
        pa11y: pa11y(),
      });

      return require("./plugins/index.js")(on, config);
    },
    specPattern: "specs/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: false,
  },
});
