import { test, expect } from "@playwright/test";

test("shows about page, license, privacy policy, and dependency pages and licenses", async ({
  page,
  baseURL,
}) => {
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
    const paths = await Promise.all(
      links.map((link) => link.getAttribute("href"))
    );
    const responses = await Promise.all(
      paths.map((path) => fetch(`${baseURL}${path}`))
    );
    const failedResponses = responses.filter((res) => res.status !== 200);
    expect(
      failedResponses.length,
      `License link broken for URLs: ${failedResponses
        .map((response) => response.url)
        .join(", ")}`
    ).toBe(0);
  }

  await page.getByRole("button", { name: "Close", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "About TinyPilot" })
  ).not.toBeVisible();

  await page.close();
});
