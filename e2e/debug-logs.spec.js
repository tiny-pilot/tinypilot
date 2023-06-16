import { test, expect } from "@playwright/test";

/**
 * Read the contents of the clipboard. To do this, create a new browser tab with
 * an <input> element, simulate hitting Control+V to paste into the <input>, and
 * read what it pasted.
 *
 * Playwright can't yet read or paste from the clipboard, so this is a workaround.
 * https://github.com/microsoft/playwright/issues/15860
 */
async function readClipboardContents(page) {
  // Create a new browser tab so that none of the event handlers in the
  // tab-under-test prevent the test from pasting the clipboard contents.
  const freshPage = await page.context().newPage();

  // Create an input element so the test has a place to paste the clipboard
  // contents into.
  const input = await freshPage.evaluateHandle(() => {
    return document.body.appendChild(document.createElement("input"));
  });

  const isMac = process.platform === "darwin";
  const modifier = isMac ? "Meta" : "Control";
  await input.press(`${modifier}+KeyV`);

  return await input.inputValue();
}

test("loads debug logs and generates a shareable URL for them", async ({
  page,
}) => {
  await page.goto("/");

  await page.getByText("System", { exact: true }).hover();
  await page.getByText("Logs", { exact: true }).click();
  await expect(page.getByRole("heading", { name: "Debug Logs" })).toBeVisible();

  await page.getByRole("button", { name: "Get Shareable URL" }).click();
  await page.getByRole("button", { name: "Copy" }).click();
  const copiedUrl = await readClipboardContents(page);
  await expect(copiedUrl).toMatch(
    new RegExp("^https://logs.tinypilotkvm.com/.*")
  );

  await expect(page.locator("#logs-success .logs-output")).toContainText(
    "TinyPilot version: "
  );

  await page.getByRole("button", { name: "Close" }).click();
  await expect(
    page.getByRole("heading", { name: "Debug Logs" })
  ).not.toBeVisible();
});
