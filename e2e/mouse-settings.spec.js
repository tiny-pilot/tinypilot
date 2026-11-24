import { test, expect } from "@playwright/test";

// This is a workaround for our unusual HTML pattern of styling checkboxes as
// toggles. We should use a locator based on the checkbox label once we fix
// https://github.com/tiny-pilot/tinypilot/issues/1638.
const locateToggle = (page, cssSelector) => {
  return page.locator(".toggle").filter({ has: page.locator(cssSelector) });
};

async function openMouseSettingsDialog(page) {
  await page.getByRole("menuitem", { name: "System" }).hover();
  await page.getByRole("menuitem", { name: "Mouse Settings" }).click();
  await expect(
    page.getByRole("heading", { name: "Mouse Settings" }),
  ).toBeVisible();
}

test.describe("mouse settings dialog", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await openMouseSettingsDialog(page);
  });

  test("closes mouse settings dialog", async ({ page }) => {
    await page.getByRole("button", { name: "Close", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "Mouse Settings" }),
    ).not.toBeVisible();
  });

  test("persists the invert scroll direction setting", async ({ page }) => {
    const checkbox = page.locator("#invert-scroll-direction");

    // We don't assume a particular initial state, because these tests might
    // run against a live device.
    const initialValue = await checkbox.isChecked();

    await locateToggle(page, "#invert-scroll-direction").click();
    await expect(checkbox).toBeChecked({ checked: !initialValue });

    // Reload the page and reopen the dialog, so that the checkbox state is
    // populated from the server rather than from the previous interaction.
    await page.reload();
    await openMouseSettingsDialog(page);
    await expect(checkbox).toBeChecked({ checked: !initialValue });

    // Restore the initial state.
    await locateToggle(page, "#invert-scroll-direction").click();
    await expect(checkbox).toBeChecked({ checked: initialValue });
    await page.reload();
    await openMouseSettingsDialog(page);
    await expect(checkbox).toBeChecked({ checked: initialValue });
  });
});
