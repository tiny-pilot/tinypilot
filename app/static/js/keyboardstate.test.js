import { describe, it } from "mocha";
import assert from "assert";
import { KeyboardState } from "./keyboardstate.js";

describe("KeyboardState", () => {
  it("should override cached state with event state", () => {
    const keyboardState = new KeyboardState();
    const events = [
      {
        code: "ControlLeft",
        key: "Control",
        altKey: false,
        ctrlKey: true,
        metaKey: false,
        shiftKey: false,
        location: 1,
      },
      {
        code: "",
        key: "Alt",
        altKey: true,
        ctrlKey: true,
        metaKey: false,
        shiftKey: false,
        location: 0,
      },
      {
        code: "KeyE",
        key: "€",
        altKey: false,
        ctrlKey: false,
        metaKey: false,
        shiftKey: false,
        location: 0,
      },
    ];
    for (const event of events) {
      keyboardState.onKeyDown(event);
    }
    assert.strictEqual(true, keyboardState.isKeyPressed("KeyE"));
    assert.strictEqual(false, keyboardState.isKeyPressed("ControlLeft"));
    assert.strictEqual(false, keyboardState.isKeyPressed("AltRight"));
  });

  describe("#getAllPressedKeys()", () => {
    it("should return an array of pressed keys", () => {
      const keyboardState = new KeyboardState();
      keyboardState.onKeyDown({
        code: "KeyE",
        altKey: true,
        ctrlKey: true,
      });
      keyboardState.onKeyDown({
        code: "KeyF",
        altKey: true,
        ctrlKey: true,
      });

      assert.strictEqual(true, keyboardState.isKeyPressed("KeyE"));
      assert.strictEqual(true, keyboardState.isKeyPressed("AltLeft"));
      assert.strictEqual(true, keyboardState.isKeyPressed("ControlLeft"));
      assert.strictEqual(true, keyboardState.isKeyPressed("KeyF"));
      assert.deepEqual(
        new Set(["KeyE", "AltLeft", "ControlLeft", "KeyF"]),
        new Set(keyboardState.getAllPressedKeys())
      );
    });
  });
});
