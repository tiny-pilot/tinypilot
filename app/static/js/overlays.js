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
