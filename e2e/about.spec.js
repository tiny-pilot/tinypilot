import { test, expect } from "@playwright/test";

test("shows about page, license, privacy policy, and dependency pages and licenses", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByText("Help", { exact: true }).hover();
  await page.getByText("About", { exact: true }).click();
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
    await page.getByRole("link", { name: "Flask" }).first().click();
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
    const cryptographyProjectPagePromise = page.waitForEvent("popup");
    await page.getByRole("link", { name: "cryptography" }).first().click();
    const cryptographyProjectPage = await cryptographyProjectPagePromise;
    await expect(cryptographyProjectPage).toHaveURL(
      new RegExp("https://cryptography.io.*")
    );
    await expect(cryptographyProjectPage.locator("body")).not.toBeEmpty();
    await cryptographyProjectPage.close();
  }

  {
    const cryptographyLicensePagePromise = page.waitForEvent("popup");
    await page
      .getByRole("listitem")
      .filter({ hasText: "cryptography (License)" })
      .getByRole("link", { name: "License" })
      .click();
    const cryptographyLicensePage = await cryptographyLicensePagePromise;
    await expect(cryptographyLicensePage).toHaveURL(new RegExp("cryptography"));
    await expect(cryptographyLicensePage.locator("body")).not.toBeEmpty();
    await cryptographyLicensePage.close();
  }

  await page.getByRole("button", { name: "Close" }).click();
  await expect(
    page.getByRole("heading", { name: "About TinyPilot" })
  ).not.toBeVisible();

  await page.close();
});
