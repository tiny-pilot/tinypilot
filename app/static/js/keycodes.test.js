import { describe, it } from "mocha";
import assert from "assert";
import { findKeyCode } from "./keycodes.js";

describe("findKeyCode", () => {
  it("maps keys by language code", () => {
    assert.strictEqual(findKeyCode("@", "en-US"), "Digit2");
    assert.strictEqual(findKeyCode("@", "en-GB"), "Quote");
  });
});
