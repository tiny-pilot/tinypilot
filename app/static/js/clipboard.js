/**
 * Copies the text content of a DOM Element to the clipboard.
 * @param {Element} element - The DOM Element of the text that you want copied.
 */
export function copyElementTextToClipboard(element) {
  // Notice: we cannot use the browser’s native Clipboard API here, since that
  // is only available in secure contexts (HTTPS). TinyPilot can legitimately be
  // used without HTTPS, though, so we are not really able to use the Clipboard
  // API. However, the `document.execCommand` API is deprecated, so this
  // workaround might stop to work once browsers drop support for it.
  // See https://stackoverflow.com/a/25456308/3769045.
  const range = document.createRange();
  const selection = window.getSelection();
  range.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(range);
  document.execCommand("copy");
  selection.removeAllRanges();
}
