/**
 * Copies the text content of a DOM Element to the clipboard.
 * @param {Element} element - The DOM Element of the text that you want copied.
 */
export function copyElementTextToClipboard(element) {
  // The fancy Async Clipboard API only works on pages served up by https
  // (i.e. not on the dev server).
  // Source: https://stackoverflow.com/a/25456308/3769045
  const range = document.createRange();
  const selection = window.getSelection();
  range.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(range);
  document.execCommand("copy");
  selection.removeAllRanges();
}
