import { test, expect } from "@playwright/test";

// This is a workaround for our unusual HTML pattern of styling checkboxes as
// toggles. We should use a locator based on the checkbox label once we fix
// https://github.com/tiny-pilot/tinypilot/issues/1638.
const locateToggle = (page, cssSelector) => {
  return page.locator(".toggle").filter({ has: page.locator(cssSelector) });
};

/**
 * Enable user authentication and create test users with specified roles.
 *
 * @param {Page} page - A Playwright Page object representing an authenticated
 *     browser session.
 * @param {string} username - The username to create.
 * @param {string} password - The password for the user.
 */
async function setupUserAuthentication(page, username, password) {
  await page.goto("/");
  await page.getByRole("menuitem", { name: "System" }).hover();
  await page.getByRole("menuitem", { name: "Security" }).hover();
  await page.getByRole("menuitem", { name: "Users" }).click();

  const dialog = page.locator("#manage-users-dialog");
  await expect(
    dialog.getByRole("heading", { name: "Manage Users" })
  ).toBeVisible();

  // Enable authentication if not already enabled.
  const authToggle = page.locator(".toggle").filter({
    has: page.locator("#require-authentication"),
  });
  const isChecked = await authToggle
    .locator("#require-authentication")
    .isChecked();

  if (!isChecked) {
    await authToggle.click();
    await expect(
      dialog.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
  } else {
    // Already enabled, add user directly.
    await page.getByRole("button", { name: "Add User" }).click();
    await expect(
      dialog.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
  }

  // Add user.
  await page.getByRole("textbox", { name: "Username" }).fill(username);
  await page
    .locator("#manage-users-dialog")
    .getByLabel("Password:", { exact: true })
    .fill(password);
  await page.getByLabel("Confirm password:", { exact: true }).fill(password);

  await page.getByRole("button", { name: "Add User" }).click();
  await expect(
    dialog.getByRole("heading", { name: "Manage Users" })
  ).toBeVisible();

  await dialog.getByRole("button", { name: "Close", exact: true }).click();
}

/**
 * Disable user authentication and clean up all users.
 *
 * This is used to revert the system state for subsequent testing.
 *
 * @param {Page} page - A Playwright Page object representing an authenticated
 *     browser session.
 */
async function disableUserAuthentication(page, browser, username, password) {
  await test.step("Disable user authentication", async () => {
    await page.reload();

    // If we're on the login page, try to authenticate first (if credentials provided).
    if (page.url().includes("/login")) {
      if (username && password) {
        await loginAsUser(page, username, password);
      } else {
        // If no credentials provided, navigate back and allow the guest check later.
        await page.goto("/");
      }
    }

    await expect(page).toHaveURL("/");
    await expect(page.getByRole("menuitem", { name: "System" })).toBeVisible();
    await page.getByRole("menuitem", { name: "System" }).hover();
    await page.getByRole("menuitem", { name: "Security" }).hover();
    await page.getByRole("menuitem", { name: "Users" }).click();

    const securityDialog = page.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await locateToggle(page, "#require-authentication").click();
    await expect(
      securityDialog.getByRole("heading", {
        name: "Disable User Authentication",
      })
    ).toBeVisible();
    await securityDialog
      .getByRole("button", { name: "Delete All Users" })
      .click();

    // We should be back on main screen of the Manage Users dialog.
    await expect(
      securityDialog.getByRole("heading", {
        name: "Manage Users",
      })
    ).toBeVisible();
    await securityDialog
      .getByRole("button", { name: "Close", exact: true })
      .click();
    await expect(
      securityDialog.getByRole("heading", {
        name: "Manage Users",
      })
    ).not.toBeVisible();
  });

  const guestPage = await (await browser.newContext()).newPage();
  await test.step("Confirm unauthenticated page access", async () => {
    await guestPage.goto("/");
    await expect(guestPage).toHaveURL("/");
    await expect(
      guestPage.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
  });
}

/**
 * Login as a specific user.
 *
 * @param {Page} page - A Playwright Page object.
 * @param {string} username - The username to login with.
 * @param {string} password - The password to login with.
 */
async function loginAsUser(page, username, password) {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Log In" })).toBeVisible();
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Log In" }).click();
  await expect(page).toHaveURL("/");
}

test.describe("change password", () => {
  test("ADMIN user can change their own password", async ({ browser }) => {
    const adminPage = await (await browser.newContext()).newPage();
    const newPage = await (await browser.newContext()).newPage();

    await test.step("Setup: Enable authentication and create ADMIN user", async () => {
      await setupUserAuthentication(
        adminPage,
        "admin-user",
        "adminpass",
        "ADMIN"
      );
    });

    await test.step("Admin logs in with original password", async () => {
      await loginAsUser(newPage, "admin-user", "adminpass");
    });

    await test.step("Admin opens change password dialog", async () => {
      await newPage.getByRole("menuitem", { name: "admin-user" }).hover();
      await newPage
        .getByRole("menuitem", { name: "Change My Password" })
        .click();

      // Wait for the change password form to be visible.
      const changePasswordForm = newPage.locator("change-password-dialog");
      await expect(changePasswordForm).toBeVisible();
    });

    await test.step("Admin enters new password", async () => {
      const changePasswordForm = newPage.locator("change-password-dialog");
      await changePasswordForm
        .locator("input[name='password']")
        .fill("newadminpass123");
      await changePasswordForm
        .locator("input[name='password-confirm']")
        .fill("newadminpass123");
    });

    await test.step("Admin saves password", async () => {
      const saveButton = newPage
        .locator("change-password-dialog")
        .getByRole("button", { name: "Save Password" });
      await saveButton.click();

      // Dialog should close after successful password change
      const changePasswordForm = newPage.locator("change-password-dialog");
      await expect(changePasswordForm).not.toBeVisible();
    });

    await test.step("Admin logs out and logs in with new password", async () => {
      await newPage.getByRole("menuitem", { name: "admin-user" }).hover();
      await newPage.getByRole("menuitem", { name: "Logout" }).click();
      await expect(newPage).toHaveURL("/login");

      await loginAsUser(newPage, "admin-user", "newadminpass123");
      await expect(
        newPage.getByRole("menuitem", { name: "admin-user" })
      ).toBeVisible();
    });

    await test.step("Cleanup: Disable authentication", async () => {
      await disableUserAuthentication(
        adminPage,
        browser,
        "admin-user",
        "newadminpass123"
      );
    });

    await adminPage.close();
    await newPage.close();
  });

  test("change password validation", async ({ browser }) => {
    const adminPage = await (await browser.newContext()).newPage();
    const userPage = await (await browser.newContext()).newPage();

    await test.step("Setup: Enable authentication and create ADMIN user", async () => {
      await setupUserAuthentication(
        adminPage,
        "admin-user",
        "adminpass",
        "ADMIN"
      );
    });

    // Login and navigate to "Change My Password" dialog.
    await test.step("Admin logs in", async () => {
      await loginAsUser(userPage, "admin-user", "adminpass");
    });
    await userPage.getByRole("menuitem", { name: "admin-user" }).hover();
    await userPage
      .getByRole("menuitem", { name: "Change My Password" })
      .click();

    const changePasswordForm = userPage.locator("change-password-dialog");
    await expect(changePasswordForm).toBeVisible();
    const saveButton = changePasswordForm.getByRole("button", {
      name: "Save Password",
    });

    await test.step("Not confirmed", async () => {
      await changePasswordForm
        .locator("input[name='password']")
        .fill("newpass1");
      await saveButton.isDisabled();

      await changePasswordForm.locator("input[name='password']").fill("");
      await changePasswordForm
        .locator("input[name='password-confirm']")
        .fill("a");
      await saveButton.isDisabled();
    });

    await test.step("Mismatched passwords", async () => {
      await changePasswordForm
        .locator("input[name='password']")
        .fill("newpass1");
      await changePasswordForm
        .locator("input[name='password-confirm']")
        .fill("newpass2");

      await saveButton.click();

      await expect(changePasswordForm.locator("#error-message")).toHaveText(
        "Passwords do not match",
        { ignoreCase: false }
      );
    });

    await test.step("Too short password", async () => {
      await changePasswordForm.locator("input[name='password']").fill("short");
      await changePasswordForm
        .locator("input[name='password-confirm']")
        .fill("short");

      await saveButton.click();

      await expect(changePasswordForm.locator("#error-message")).toHaveText(
        "Password must be 6-60 characters in length",
        { ignoreCase: false }
      );
    });

    await test.step("Cleanup: Disable authentication", async () => {
      await disableUserAuthentication(
        adminPage,
        browser,
        "admin-user",
        "adminpass"
      );
    });

    await adminPage.close();
    await userPage.close();
  });
});
