import { test, expect } from "@playwright/test";

// This is a workaround for our unusual HTML pattern of styling checkboxes as
// toggles. We should use a locator based on the checkbox label once we fix
// https://github.com/tiny-pilot/tinypilot/issues/1638.
const locateToggle = (page, cssSelector) => {
  return page.locator(".toggle").filter({ has: page.locator(cssSelector) });
};

/**
 * Disable user authentication.
 *
 * This function is used to revert the system state for subsequent testing
 * rather than to actively verify functionality.
 *
 * Note that we'd ideally want to ensure a clean system state by removing the
 * TinyPilot database file before each test. However, this would not work for
 * when running these tests on a live device using `--base-url`.
 *
 * @param {Page} page - A Playwright Page object representing an authenticated
 *     browser session.
 * @param {Browser} browser - A Playwright Browser object.
 *
 */
async function disableUserAuthentication(page, browser) {
  await test.step("Disable user authentication", async () => {
    await page.reload();
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

/*
 *
 * This test is split between two browser session contexts as follows:
 *
 * |     | Session 1: alice              | Session 2: bob        |
 * | --- | ------------------------------| ----------------------|
 * | 1   | Enable authentication         |                       |
 * | 2   | Create the 'alice' user       |                       |
 * | 3   | Create the 'bob' user         |                       |
 * | 4   |                               | Create a new session  |
 * | 5   |                               | Login as 'bob'        |
 * | 6   |                               | Verify login success  |
 * | 7   | Change the password for 'bob' |                       |
 * | 8   |                               | Refresh the page      |
 * | 9   |                               | Verify auto-logout    |
 * | 10  | Disable authentication        |                       |
 * | 11  | Confirm user deletion         |                       |
 *
 * Steps 10 and 11 are intended to revert the system state for subsequent
 * testing rather than to actively verify the functionality.
 *
 */
test("invalidates an authenticated session", async ({ page, browser }) => {
  const bobPage = await (await browser.newContext()).newPage();

  await test.step("Enable authentication", async () => {
    await page.goto("/");
    await page.getByRole("menuitem", { name: "System" }).hover();
    await page.getByRole("menuitem", { name: "Security" }).hover();
    await page.getByRole("menuitem", { name: "Users" }).click();
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();
    await locateToggle(page, "#require-authentication").click();
    await expect(
      page.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
  });

  await test.step("Create the 'alice' user", async () => {
    await page.getByRole("textbox", { name: "Username" }).fill("alice");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("alicepass");
    await page
      .getByLabel("Confirm password:", { exact: true })
      .fill("alicepass");
    await page.getByRole("button", { name: "Add User" }).click();
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();
  });

  await test.step("Create the 'bob' user", async () => {
    await page.getByRole("button", { name: "Add User" }).click();
    await expect(
      page.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
    await page.getByRole("textbox", { name: "Username" }).fill("bob");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("bobpass");
    await page.getByLabel("Confirm password:", { exact: true }).fill("bobpass");
    await page.getByRole("button", { name: "Add User" }).click();
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();
  });

  await test.step("Login as 'bob'", async () => {
    await bobPage.goto("/");
    await expect(bobPage).toHaveURL("/login");
    await expect(
      bobPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();
    await bobPage.getByLabel("Username").fill("bob");
    await bobPage.getByLabel("Password").fill("bobpass");
    await bobPage.getByRole("button", { name: "Log In" }).click();
  });

  await test.step("Verify login success", async () => {
    await expect(bobPage).toHaveURL("/");
  });

  await test.step("Change the password for 'bob'", async () => {
    await page
      .getByRole("listitem")
      .filter({ hasText: "bob" })
      .getByRole("button", { name: "Edit" })
      .click();
    await expect(
      page.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("newbobpass");
    await page
      .getByLabel("Confirm password:", { exact: true })
      .fill("newbobpass");
    await page.getByRole("button", { name: "Save User" }).click();
  });

  await test.step("Refresh the page", async () => {
    await bobPage.reload();
  });

  await test.step("Verify auto-logout", async () => {
    await expect(bobPage).toHaveURL("/login");
    await expect(
      bobPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();
  });

  await disableUserAuthentication(page, browser);
});

test("adds and removes user authentication", async ({ page, browser }) => {
  await test.step("Enable authentication", async () => {
    await page.goto("/");
    await page.getByRole("menuitem", { name: "System" }).hover();
    await page.getByRole("menuitem", { name: "Security" }).hover();
    await page.getByRole("menuitem", { name: "Users" }).click();
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();
    await locateToggle(page, "#require-authentication").click();
  });

  await test.step("Add a user named alice", async () => {
    await expect(
      page.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
    await page.getByRole("textbox", { name: "Username" }).fill("alice");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("alicepass");
    await page
      .getByLabel("Confirm password:", { exact: true })
      .fill("alicepass");
    await page.getByRole("button", { name: "Add User" }).click();

    // We should be back on Manage Users page.
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();
    await page.getByRole("button", { name: "Add User" }).click();
  });

  await test.step("Add a user named bob", async () => {
    await expect(
      page.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();
    await page.getByRole("textbox", { name: "Username" }).fill("bob");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("bobpass");
    await page.getByLabel("Confirm password:", { exact: true }).fill("bobpass");
    await page.getByRole("button", { name: "Add User" }).click();

    // We should be back on Manage Users page.
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();
    await page.getByRole("button", { name: "Close", exact: true }).click();

    // We should now see a menu item for logging out.
    await page.getByRole("menuitem", { name: "System" }).hover();
    await expect(page.getByRole("menuitem", { name: "alice" })).toBeVisible();
  });

  // Visiting the TinyPilot app should prompt us for credentials, and alice's
  // credentials should succeed.
  await test.step("Login as alice", async () => {
    const guestPage = await (await browser.newContext()).newPage();
    await guestPage.goto("/");

    // We should be redirected to the login page.
    await expect(guestPage).toHaveURL("/login");
    await expect(
      guestPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();

    await guestPage.getByLabel("Username").fill("alice");
    await guestPage.getByLabel("Password").fill("alicepass");
    await guestPage.getByRole("button", { name: "Log In" }).click();

    await expect(guestPage).toHaveURL("/");

    // Verify we can log out.
    await guestPage.getByRole("menuitem", { name: "System" }).hover();
    await guestPage.getByRole("menuitem", { name: "alice" }).hover();
    await guestPage.getByRole("menuitem", { name: "Logout" }).click();

    await expect(guestPage).toHaveURL("/login");
  });

  // Visiting the TinyPilot app should prompt us for credentials, and bob's
  // credentials should succeed.
  await test.step("Login as bob", async () => {
    const guestPage = await (await browser.newContext()).newPage();
    await guestPage.goto("/");

    // We should be redirected to the login page.
    await expect(guestPage).toHaveURL("/login");
    await expect(
      guestPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();

    await guestPage.getByLabel("Username").fill("bob");
    await guestPage.getByLabel("Password").fill("bobpass");
    await guestPage.getByRole("button", { name: "Log In" }).click();

    await expect(guestPage).toHaveURL("/");

    // Verify we can log out.
    await guestPage.getByRole("menuitem", { name: "System" }).hover();
    await guestPage.getByRole("menuitem", { name: "bob" }).hover();
    await guestPage.getByRole("menuitem", { name: "Logout" }).click();

    await expect(guestPage).toHaveURL("/login");
  });

  // Visiting the TinyPilot app should prompt us for credentials, and incorrect
  // credentials should fail.
  await test.step("Login with wrong password fails", async () => {
    const guestPage = await (await browser.newContext()).newPage();
    await guestPage.goto("/");

    // We should be redirected to the login page.
    await expect(guestPage).toHaveURL("/login");
    await expect(
      guestPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();

    await guestPage.getByLabel("Username").fill("alice");
    await guestPage.getByLabel("Password").fill("wrongalicepass");
    await guestPage.getByRole("button", { name: "Log In" }).click();

    // We should still be on the login page and see an error message.
    await expect(guestPage).toHaveURL("/login");
    await expect(guestPage.locator("#error")).toContainText(
      "Error: Invalid username and password",
      { ignoreCase: false }
    );
  });

  // Visiting the TinyPilot app on a non-root path should prompt us for
  // credentials, and successfully logging in should redirect us to the
  // previous page.
  await test.step("Login should redirect to previous page", async () => {
    const guestPage = await (await browser.newContext()).newPage();
    await guestPage.goto("/?viewMode=standalone");

    // We should be redirected to the login page, and the originally requested
    // URL should be included in the ?redirect query parameter.
    await expect(guestPage).toHaveURL(
      "/login?redirect=%2F%3FviewMode%3Dstandalone"
    );
    await expect(
      guestPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();

    await guestPage.getByLabel("Username").fill("bob");
    await guestPage.getByLabel("Password").fill("bobpass");
    await guestPage.getByRole("button", { name: "Log In" }).click();

    // After the login, we are redirected to the previous (originally
    // requested) path.
    await expect(guestPage).toHaveURL("/?viewMode=standalone");
  });

  // The redirect-after-login mechanism should detect and ignore a fabricated,
  // malicious redirect parameter.
  await test.step("Login redirect should detect malicious URLs", async () => {
    const guestPage = await (await browser.newContext()).newPage();

    // Redirect param is: https://evil.com
    await guestPage.goto("/login?redirect=https%3A%2F%2Fevil.com");
    await expect(
      guestPage.getByRole("heading", { name: "Log In" })
    ).toBeVisible();

    await guestPage.getByLabel("Username").fill("bob");
    await guestPage.getByLabel("Password").fill("bobpass");
    await guestPage.getByRole("button", { name: "Log In" }).click();

    // After the login, we are redirected to the root path, and not to the
    // malicious URL.
    await expect(guestPage).toHaveURL("/");
  });

  await disableUserAuthentication(page, browser);
});

test.describe("rejects invalid input for creating a new user", async () => {
  // Note: We're not trying to exhaust every possible error, as unit tests cover
  // that, but we want to try a few to make sure everything is working
  // end-to-end.

  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.getByRole("menuitem", { name: "System" }).hover();
    await page.getByRole("menuitem", { name: "Security" }).hover();
    await page.getByRole("menuitem", { name: "Users" }).click();
    await expect(
      page.getByRole("heading", { name: "Manage Users" })
    ).toBeVisible();

    await locateToggle(page, "#require-authentication").click();

    await expect(
      page.getByRole("heading", { name: "User Authentication" })
    ).toBeVisible();

    // Verify the Add User button is disabled before we populate any fields.
    await page.getByRole("button", { name: "Add User" }).isDisabled();
  });

  test("username too long", async ({ page }) => {
    const maxUsernameLength = 20;
    await page
      .getByRole("textbox", { name: "Username" })
      .fill("A".repeat(maxUsernameLength + 1));
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("validPassword123");
    await page
      .getByLabel("Confirm password:", { exact: true })
      .fill("validPassword123");
    await page.getByRole("button", { name: "Add User" }).click();

    await expect(page.locator("#manage-users-dialog #error")).toHaveText(
      "Error: Username must be 1-20 characters in length",
      { ignoreCase: false }
    );
  });

  test("username with invalid characters", async ({ page }) => {
    await page.getByRole("textbox", { name: "Username" }).fill("inv@lidn^me");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("validPassword123");
    await page
      .getByLabel("Confirm password:", { exact: true })
      .fill("validPassword123");
    await page.getByRole("button", { name: "Add User" }).click();

    await expect(page.locator("#manage-users-dialog #error")).toHaveText(
      "Error: Username can only contain characters a-z, A-Z, 0-9, or .-_",
      { ignoreCase: false }
    );
  });

  test("mismatched passwords", async ({ page }) => {
    await page.getByRole("textbox", { name: "Username" }).fill("alice");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("abc123");
    await page.getByLabel("Confirm password:", { exact: true }).fill("xyz456");
    await page.getByRole("button", { name: "Add User" }).click();

    await expect(page.locator("#manage-users-dialog #error")).toHaveText(
      "Error: Passwords do not match",
      { ignoreCase: false }
    );
  });

  test("password too short", async ({ page }) => {
    await page.getByRole("textbox", { name: "Username" }).fill("alice");
    await page
      .locator("#manage-users-dialog")
      .getByLabel("Password:", { exact: true })
      .fill("short");
    await page.getByLabel("Confirm password:", { exact: true }).fill("short");
    await page.getByRole("button", { name: "Add User" }).click();

    await expect(page.locator("#manage-users-dialog #error")).toHaveText(
      "Error: Password must be 6-60 characters in length",
      { ignoreCase: false }
    );
  });
});

test("turning on user authentication invalidates other active sessions", async ({
  browser,
}) => {
  const session1 = await (await browser.newContext()).newPage();
  const session2 = await (await browser.newContext()).newPage();

  await test.step("Session 1: Confirm unauthenticated page access", async () => {
    await session1.goto("/");
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
  });

  await test.step("Session 2: Confirm unauthenticated page access", async () => {
    await session2.goto("/");
    await expect(session2).toHaveURL("/");
    await expect(
      session2.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
  });

  await test.step("Session 1: Enable user authentication by creating a user", async () => {
    await session1.goto("/");
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session1.getByRole("menuitem", { name: "System" }).hover();
    await session1.getByRole("menuitem", { name: "Security" }).hover();
    await session1.getByRole("menuitem", { name: "Users" }).click();

    const securityDialog = session1.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await locateToggle(session1, "#require-authentication").click();
    await securityDialog.getByLabel("Username").fill("bob");
    await securityDialog
      .getByLabel("Password:", { exact: true })
      .fill("bobpass");
    await securityDialog.getByLabel("Confirm password").fill("bobpass");
    await securityDialog.getByRole("button", { name: "Add User" }).click();
  });

  await test.step("Session 1: Confirm authenticated page access", async () => {
    await session1.reload();
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
  });

  await test.step("Session 2: Confirm restricted access", async () => {
    await expect(session2).toHaveURL("/");
    await expect(
      session2.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session2.getByRole("menuitem", { name: "System" }).hover();
    await session2.getByRole("menuitem", { name: "Security" }).hover();
    await session2.getByRole("menuitem", { name: "Users" }).click();

    const errorDialog = session2.locator("#error-dialog");
    await expect(errorDialog).toBeVisible();

    await expect(errorDialog.locator("#details")).toContainText(
      "Error: Not authorized"
    );
  });

  await test.step("Session 2: Refresh page and confirm redirect to login screen", async () => {
    await session2.reload();
    await expect(session2).toHaveURL("/login");
    await expect(
      session2.getByRole("heading", { name: "Log In" })
    ).toBeVisible();
  });

  await disableUserAuthentication(session1, browser);
});

test("changing user password invalidates other active sessions for the same user", async ({
  browser,
}) => {
  const session1 = await (await browser.newContext()).newPage();
  const session2 = await (await browser.newContext()).newPage();

  await test.step("Session 1: Enable user authentication by creating a user", async () => {
    await session1.goto("/");
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session1.getByRole("menuitem", { name: "System" }).hover();
    await session1.getByRole("menuitem", { name: "Security" }).hover();
    await session1.getByRole("menuitem", { name: "Users" }).click();

    const securityDialog = session1.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await locateToggle(session1, "#require-authentication").click();
    await securityDialog.getByLabel("Username").fill("bob");
    await securityDialog
      .getByLabel("Password:", { exact: true })
      .fill("bobpass");
    await securityDialog.getByLabel("Confirm password").fill("bobpass");
    await securityDialog.getByRole("button", { name: "Add User" }).click();
  });

  await test.step("Session 1: Confirm authenticated page access", async () => {
    await session1.reload();
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
  });

  await test.step("Session 2: Login as user", async () => {
    await session2.goto("/");
    await expect(session2).toHaveURL("/login");
    await session2.getByLabel("Username").fill("bob");
    await session2.getByLabel("Password").fill("bobpass");
    await session2.getByRole("button", { name: "Log In" }).click();
    await expect(session2).toHaveURL("/");
  });

  await test.step("Session 1: Change user password", async () => {
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session1.getByRole("menuitem", { name: "System" }).hover();
    await session1.getByRole("menuitem", { name: "Security" }).hover();
    await session1.getByRole("menuitem", { name: "Users" }).click();

    const securityDialog = session1.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await securityDialog
      .getByRole("listitem")
      .filter({ hasText: "bob" })
      .getByRole("button", { name: "Edit" })
      .click();
    await securityDialog
      .getByLabel("Password:", { exact: true })
      .fill("newbobpass");
    await securityDialog.getByLabel("Confirm password").fill("newbobpass");
    await securityDialog.getByRole("button", { name: "Save User" }).click();
  });

  await test.step("Session 2: Confirm restricted access", async () => {
    await expect(session2).toHaveURL("/");
    await expect(
      session2.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session2.getByRole("menuitem", { name: "System" }).hover();
    await session2.getByRole("menuitem", { name: "Security" }).hover();
    await session2.getByRole("menuitem", { name: "Users" }).click();

    const errorDialog = session2.locator("#error-dialog");
    await expect(errorDialog).toBeVisible();

    await expect(errorDialog.locator("#details")).toContainText(
      "Error: Not authorized"
    );
  });

  await test.step("Session 2: Refresh page and confirm redirect to login screen", async () => {
    await session2.reload();
    await expect(session2).toHaveURL("/login");
    await expect(
      session2.getByRole("heading", { name: "Log In" })
    ).toBeVisible();
  });

  await disableUserAuthentication(session1, browser);
});

test("deleting a user invalidates other active sessions for the same user", async ({
  browser,
}) => {
  const session1 = await (await browser.newContext()).newPage();
  const session2 = await (await browser.newContext()).newPage();

  await test.step("Session 1: Enable user authentication by creating a user", async () => {
    await session1.goto("/");
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session1.getByRole("menuitem", { name: "System" }).hover();
    await session1.getByRole("menuitem", { name: "Security" }).hover();
    await session1.getByRole("menuitem", { name: "Users" }).click();

    const securityDialog = session1.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await locateToggle(session1, "#require-authentication").click();
    await securityDialog.getByLabel("Username").fill("bob");
    await securityDialog
      .getByLabel("Password:", { exact: true })
      .fill("bobpass");
    await securityDialog.getByLabel("Confirm password").fill("bobpass");
    await securityDialog.getByRole("button", { name: "Add User" }).click();
  });

  await test.step("Session 1: Confirm authenticated page access", async () => {
    await session1.reload();
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
  });

  await test.step("Session 1: Create a user", async () => {
    await expect(session1).toHaveURL("/");
    await expect(
      session1.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session1.getByRole("menuitem", { name: "System" }).hover();
    await session1.getByRole("menuitem", { name: "Security" }).hover();
    await session1.getByRole("menuitem", { name: "Users" }).click();

    const securityDialog = session1.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await securityDialog.getByRole("button", { name: "Add User" }).click();
    await securityDialog.getByLabel("Username").fill("alice");
    await securityDialog
      .getByLabel("Password:", { exact: true })
      .fill("alicepass");
    await securityDialog.getByLabel("Confirm password").fill("alicepass");
    await session1.getByRole("button", { name: "Add User" }).click();
  });

  await test.step("Session 2: Login as user", async () => {
    await session2.goto("/");
    await expect(session2).toHaveURL("/login");
    await session2.getByLabel("Username").fill("alice");
    await session2.getByLabel("Password").fill("alicepass");
    await session2.getByRole("button", { name: "Log In" }).click();
    await expect(session2).toHaveURL("/");
  });

  await test.step("Session 1: Delete user", async () => {
    const securityDialog = session1.locator("#manage-users-dialog");
    await expect(securityDialog).toBeVisible();

    await securityDialog
      .getByRole("listitem")
      .filter({ hasText: "alice" })
      .getByRole("button", { name: "Edit" })
      .click();
    await securityDialog.getByRole("button", { name: "Remove User" }).click();
  });

  await test.step("Session 2: Confirm restricted access", async () => {
    await expect(session2).toHaveURL("/");
    await expect(
      session2.getByRole("menuitem", { name: "System" })
    ).toBeVisible();
    await session2.getByRole("menuitem", { name: "System" }).hover();
    await session2.getByRole("menuitem", { name: "Security" }).hover();
    await session2.getByRole("menuitem", { name: "Users" }).click();

    const errorDialog = session2.locator("#error-dialog");
    await expect(errorDialog).toBeVisible();

    await expect(errorDialog.locator("#details")).toContainText(
      "Error: Not authorized"
    );
  });

  await test.step("Session 2: Refresh page and confirm redirect to login screen", async () => {
    await session2.reload();
    await expect(session2).toHaveURL("/login");
    await expect(
      session2.getByRole("heading", { name: "Log In" })
    ).toBeVisible();
  });

  await test.step("Session 2: Confirm unable to login with user", async () => {
    await expect(session2).toHaveURL("/login");
    await session2.getByLabel("Username").fill("alice");
    await session2.getByLabel("Password").fill("alicepass");
    await session2.getByRole("button", { name: "Log In" }).click();

    // We should still be on the login page and see an error message.
    await expect(session2).toHaveURL("/login");
    await expect(session2.locator("#error")).toContainText(
      "Error: Invalid username and password",
      { ignoreCase: false }
    );
  });

  await disableUserAuthentication(session1, browser);
});
