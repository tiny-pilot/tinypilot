import { describe, it } from "mocha";
import assert from "assert";
import { filterSensitiveData } from "./logs.js";

describe("filterSensitiveData", () => {
  it("returns the logs as is if there is no sensitive data", () => {
    const logTextWithoutSensitiveData = `
2020-01-01T00:00:01Z INFO Something happened
2020-01-01T00:00:02Z INFO Some other thing happened
2020-01-01T00:00:03Z ERROR Something else happened
2020-01-01T00:00:04Z INFO Some regular message
`;
    const filteredLogs = filterSensitiveData(logTextWithoutSensitiveData);
    assert.strictEqual(filteredLogs, logTextWithoutSensitiveData);
  });

  it("removes all lines that are flagged as sensitive", () => {
    const filteredLogs = filterSensitiveData(`
2020-01-01T00:00:01Z INFO Something happened
2020-01-01T00:00:02Z INFO Some other thing happened
2020-01-01T00:00:03Z INFO [SENSITIVE] This message contains sensitive data [/SENSITIVE]
2020-01-01T00:00:04Z ERROR Something else happened
2020-01-01T00:00:05Z DEBUG [SENSITIVE] That’s a secret message
which spans multiple lines
of the log text [/SENSITIVE]
2020-01-01T00:00:06Z INFO Some regular message
`);
    const expectedOutput = `
2020-01-01T00:00:01Z INFO Something happened
2020-01-01T00:00:02Z INFO Some other thing happened
2020-01-01T00:00:04Z ERROR Something else happened
2020-01-01T00:00:06Z INFO Some regular message
`;
    assert.strictEqual(filteredLogs, expectedOutput);
  });
});
