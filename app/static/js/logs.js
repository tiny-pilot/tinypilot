const NEWLINE = "\n";
const SENSITIVE_MARKER_START = "[SENSITIVE]";
const SENSITIVE_MARKER_END = "[/SENSITIVE]";

/**
 * Filters out all log lines that are flagged as sensitive. That includes:
 * - the entire first line that contains the `[SENSITIVE]` start marker
 * - the entire last line that contains the `[/SENSITIVE]` end marker
 * - all lines in between those markers
 *
 * This function doesn’t make any other assumptions on how the log lines are
 * formatted.
 * @param logText {string}
 * @returns {string}
 */
export function filterSensitiveData(logText) {
  // Note: this implementation is not perfectly accurate in regards to certain
  // edge cases (e.g. multiple redundant markers on the same line). For our
  // purposes, it’s good enough, though.
  let isWithinMarkers = false;
  return logText
    .split(NEWLINE)
    .filter((logLine) => {
      const containsStartMarker = logLine.includes(SENSITIVE_MARKER_START);
      const containsEndMarker = logLine.includes(SENSITIVE_MARKER_END);
      if (containsStartMarker) {
        isWithinMarkers = true;
      }
      if (containsEndMarker) {
        isWithinMarkers = false;
      }
      return !(containsStartMarker || containsEndMarker || isWithinMarkers);
    })
    .join(NEWLINE);
}
