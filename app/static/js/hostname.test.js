import { determineFutureOrigin } from "./hostname.js";
import { describe, it } from "mocha";
import assert from "assert";

describe("determineFutureOrigin", () => {
  it("returns origin by replacing old hostname with new hostname", () => {
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "https://new-tinypilot"
    );
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot.local/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "https://new-tinypilot.local"
    );
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot.domain.local/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "https://new-tinypilot.domain.local"
    );
  });
  it("returns origin using only new hostname", () => {
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot/"),
        undefined,
        "new-tinypilot"
      ),
      "https://new-tinypilot"
    );
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot.local/"),
        undefined,
        "new-tinypilot"
      ),
      "https://new-tinypilot"
    );
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot.domain.local/"),
        undefined,
        "new-tinypilot"
      ),
      "https://new-tinypilot"
    );
  });
  it("maintains port number", () => {
    assert.strictEqual(
      determineFutureOrigin(
        new URL("https://old-tinypilot:8080/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "https://new-tinypilot:8080"
    );
  });
  it("maintains protocol", () => {
    assert.strictEqual(
      determineFutureOrigin(
        new URL("http://old-tinypilot/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "http://new-tinypilot"
    );
    assert.strictEqual(
      determineFutureOrigin(
        new URL("ftp://old-tinypilot/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "ftp://new-tinypilot"
    );
  });
  it("strips pathname", () => {
    assert.strictEqual(
      determineFutureOrigin(
        new URL("http://old-tinypilot/some-path/"),
        "old-tinypilot",
        "new-tinypilot"
      ),
      "http://new-tinypilot"
    );
  });
});
