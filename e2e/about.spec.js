import { test, expect } from "@playwright/test";

test("shows about page, license, privacy policy, and dependency pages and licenses", async ({
  page,
  context,
}, testInfo) => {
  await page.goto("/");
  await page.getByRole("menuitem", { name: "Help" }).hover();
  await page.getByRole("menuitem", { name: "About" }).click();
  await expect(
    page.getByRole("heading", { name: "About TinyPilot" })
  ).toBeVisible();

  const licensePagePromise = page.waitForEvent("popup");
  await page.getByRole("link", { name: "MIT license" }).click();
  const licensePage = await licensePagePromise;
  await expect(licensePage.locator("body")).toContainText(
    "Copyright 2022 TinyPilot, LLC"
  );
  await licensePage.close();

  {
    const privacyPolicyPagePromise = page.waitForEvent("popup");
    await page.getByRole("link", { name: "Privacy Policy" }).click();
    const privacyPolicyPage = await privacyPolicyPagePromise;
    await expect(privacyPolicyPage.locator("body")).toContainText(
      "PRIVACY POLICY"
    );
    await privacyPolicyPage.close();
  }

  {
    const flaskProjectPagePromise = page.waitForEvent("popup");
    await page
      .getByRole("link", { name: "Flask", exact: true })
      .first()
      .click();
    const flaskProjectPage = await flaskProjectPagePromise;
    await expect(flaskProjectPage).toHaveURL(
      new RegExp("https://flask.palletsprojects.com.*")
    );
    // We assert the presense of some text so the trace report shows the page render.
    await expect(flaskProjectPage.locator("body")).not.toBeEmpty();
    await flaskProjectPage.close();
  }

  {
    const flaskLicensePagePromise = page.waitForEvent("popup");
    await page
      .getByRole("listitem")
      .filter({ hasText: "Flask (License)" })
      .getByRole("link", { name: "License" })
      .click();
    const flaskLicensePage = await flaskLicensePagePromise;
    await expect(flaskLicensePage).toHaveURL(
      new RegExp(".*licensing/Flask/license.*")
    );
    await expect(flaskLicensePage.locator("body")).not.toBeEmpty();
    await flaskLicensePage.close();
  }

  {
    const janusProjectPagePromise = page.waitForEvent("popup");
    await page
      .getByRole("link", { name: "Janus", exact: true })
      .first()
      .click();
    const janusProjectPage = await janusProjectPagePromise;
    await expect(janusProjectPage).toHaveURL(
      new RegExp("https://janus.conf.meetecho.com.*")
    );
    await expect(janusProjectPage.locator("body")).not.toBeEmpty();
    await janusProjectPage.close();
  }

  {
    const janusLicensePagePromise = page.waitForEvent("popup");
    await page
      .getByRole("listitem")
      .filter({ hasText: "Janus (License)" })
      .getByRole("link", { name: "License" })
      .click();
    const janusLicensePage = await janusLicensePagePromise;
    await expect(janusLicensePage).toHaveURL(
      new RegExp(
        "https://raw.githubusercontent.com/tiny-pilot/janus-gateway/.*"
      )
    );
    await expect(janusLicensePage.locator("body")).not.toBeEmpty();
    await janusLicensePage.close();
  }

  {
    const links = await page.locator("a.license").all();
    // Increase our test's total timeout to allow for all popups pages to load.
    const popupLoadTimeout = 5000;
    testInfo.setTimeout(testInfo.timeout + popupLoadTimeout * links.length);
    for (const link of links) {
      // Prepare to capture popup page.
      const popupPromise = page.waitForEvent("popup");
      // Prepare to capture final page response that isn't a redirect.
      const responsePromise = context.waitForEvent("response", {
        predicate: (response) => {
          const isRedirect =
            response.status() >= 300 && response.status() <= 399;
          return !isRedirect;
        },
        timeout: popupLoadTimeout,
      });
      // Trigger popup page.
      await link.click();
      try {
        const response = await responsePromise;
        expect(response.status()).toBe(200);
      } catch (error) {
        // Log the failing popup page URL.
        const popup = await popupPromise;
        console.error(`failed to load license page: ${popup.url()}`);
        throw error;
      }
    }
  }

  await page.getByRole("button", { name: "Close", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "About TinyPilot" })
  ).not.toBeVisible();

  await page.close();
});
