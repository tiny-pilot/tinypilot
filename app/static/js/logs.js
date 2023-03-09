const NEWLINE = "\n";
const SENSITIVE_MARKER_START = "[SENSITIVE]";
const SENSITIVE_MARKER_END = "[/SENSITIVE]";
const REDACTED_MESSAGE = "[SENSITIVE DATA REDACTED]";

/**
 * Redacts all log lines that are flagged as sensitive. That includes:
 * - the entire first line that contains the `[SENSITIVE]` start marker
 * - the entire last line that contains the `[/SENSITIVE]` end marker
 * - all lines in between those markers
 *
 * All affected log lines are replaced by `[SENSITIVE DATA REDACTED]`.
 *
 * This function doesn’t make any other assumptions on how the log lines are
 * formatted.
 *
 * @param {string} logText
 * @returns {string}
 */
export function redactSensitiveData(logText) {
  // Note: this implementation is not perfectly accurate in regards to certain
  // edge cases (e.g. multiple redundant markers on the same line). For our
  // purposes, it’s good enough, though.
  const resultingLines = [];
  let isWithinMarkers = false;
  for (const logLine of logText.split(NEWLINE)) {
    const containsStartMarker = logLine.includes(SENSITIVE_MARKER_START);
    const containsEndMarker = logLine.includes(SENSITIVE_MARKER_END);
    if (containsStartMarker) {
      isWithinMarkers = true;
    }
    if (containsEndMarker) {
      isWithinMarkers = false;
    }

    const isRedacted =
      containsStartMarker || containsEndMarker || isWithinMarkers;
    resultingLines.push(isRedacted ? REDACTED_MESSAGE : logLine);
  }
  return resultingLines.join(NEWLINE);
}
