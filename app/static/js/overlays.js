/**
 * A registry to keep track of all overlays being shown.
 * Usually, there should be just one overlay at any time, but technically
 * speaking it’s not safe to rely on that.
 */
export class OverlayTracker {
  _currentOverlays = new Set();

  hasOverlays() {
    return this._currentOverlays.size > 0;
  }

  trackStatus(overlayElement, isShown) {
    if (isShown) {
      this._currentOverlays.add(overlayElement);
    } else {
      this._currentOverlays.delete(overlayElement);
    }
  }
}
