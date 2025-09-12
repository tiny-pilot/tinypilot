import { determineRedirectParams } from "./login.js";
import { describe, it } from "mocha";
import assert from "assert";

describe("determineRedirectParams", () => {
  it("returns base redirect parameters if redirect query is absent", () => {
    assert.deepStrictEqual(determineRedirectParams(null), {
      pathname: "/",
      search: "",
    });
  });

  it("returns redirect parameters from redirect query", () => {
    assert.deepStrictEqual(determineRedirectParams("/foo"), {
      pathname: "/foo",
      search: "",
    });
    assert.deepStrictEqual(determineRedirectParams("/?foo=bar"), {
      pathname: "/",
      search: "foo=bar",
    });
    assert.deepStrictEqual(
      determineRedirectParams("/foo/bar-baz?test=123&question=what?"),
      {
        pathname: "/foo/bar-baz",
        search: "test=123&question=what?",
      }
    );
  });

  it("doesn’t decode URL entities, but takes them over as is", () => {
    assert.deepStrictEqual(determineRedirectParams("/%2Ffoo"), {
      pathname: "/%2Ffoo",
      search: "",
    });
    assert.deepStrictEqual(determineRedirectParams("/%3Ffoo%3Dbar"), {
      pathname: "/%3Ffoo%3Dbar",
      search: "",
    });
  });

  it("rejects missing initial slash", () => {
    assert.deepStrictEqual(determineRedirectParams("foo"), {
      pathname: "/",
      search: "",
    });
    assert.deepStrictEqual(determineRedirectParams("?foo=bar"), {
      pathname: "/",
      search: "",
    });
  });

  it("disregards (potentially) malicious redirect params", () => {
    // Note that most of these are already implicitly covered by the “missing
    // initial slash” test. We test for them anyway, to lean on the safe side,
    // and to demonstrate potential attack scenarios for future reference.
    assert.deepStrictEqual(determineRedirectParams("http://evil-site.com"), {
      pathname: "/",
      search: "",
    });
    assert.deepStrictEqual(determineRedirectParams("https://evil-site.com"), {
      pathname: "/",
      search: "",
    });
    assert.deepStrictEqual(
      determineRedirectParams("javascript:fetch('http://evil.com')"),
      {
        pathname: "/",
        search: "",
      }
    );
    assert.deepStrictEqual(
      determineRedirectParams(
        "data:text/html,Open <a href='http://evil.com'>TinyPilot</a>"
      ),
      {
        pathname: "/",
        search: "",
      }
    );
    assert.deepStrictEqual(determineRedirectParams("//evil-site.com"), {
      pathname: "/",
      search: "",
    });
  });
});
