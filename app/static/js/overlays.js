/**
 * A registry to keep track of all overlays being shown.
 * Usually, there should be just one overlay at any time, but technically
 * speaking it’s not safe to rely on that.
 */
export class OverlayTracker {
  currentOverlays = new Set();

  hasOverlays() {
    return this.currentOverlays.size > 0;
  }

  trackStatus(overlayElement, isShown) {
    if (isShown) {
      this.currentOverlays.add(overlayElement);
    } else {
      this.currentOverlays.delete(overlayElement);
    }
  }
}
