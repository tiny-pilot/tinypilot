// @ts-check
import { defineConfig, devices } from "@playwright/test";

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  retries: 0,
  /* Opt out of parallel tests, until we have fixed our test setup in that
     regard. See https://github.com/tiny-pilot/tinypilot/issues/1694 */
  workers: 1,
  reporter: "html",
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://0.0.0.0:9000",
    actionTimeout: 0,
    trace: "on",
    video: "on",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  outputDir: "e2e-results/",

  /* Do not start the local web server when running against a target TinyPilot server. */
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command:
          ". venv/bin/activate && export PORT=9000 && ./dev-scripts/serve-dev",
        url: "http://0.0.0.0:9000",
        reuseExistingServer: !process.env.CI,
      },
});
