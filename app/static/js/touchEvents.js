export class TouchEvents {
  constructor() {
    this.touchStartTimestamp;
    this.isPointerMoving = false;
    this.longTouchDuration = 600; // Time in milliseconds for a touch to be considered a long touch this is arbitrary.
    this.touchTimeoutId = null;
    this.touchClientX = null;
    this.touchClientY = null;
    this.lastPos = null;
    const userAgentString = navigator.userAgent;
    this.browser = null;
    if (userAgentString.indexOf("Chrome") > -1) this.browser = "chrome";
    else if (userAgentString.indexOf("Firefox") > -1) this.browser = "firefox";
    else if (userAgentString.indexOf("Safari") > -1) this.browser = "safari";
  }

  touchStartAction(evt, screenElement) {
    // Evt needs to be disabled only on firefox and safari to avoid default long press action.
    if (this.browser === "safari" || this.browser === "firefox")
      evt.preventDefault();
    this.touchStartTimestamp = Date.now();
    this.touchClientX = evt.touches[0].clientX;
    this.touchClientY = evt.touches[0].clientY;
    // TouchTimeoutId will be triggered only if the touch duration is longer than 600ms.
    this.touchTimeoutId = setTimeout(() => {
      if (!this.isPointerMoving) {
        const mouseEvent = new MouseEvent("mousedown", {
          bubbles: true,
          cancelable: true,
          view: window,
          button: 0,
          buttons: 2,
          clientX: evt.touches[0].clientX,
          clientY: evt.touches[0].clientY,
        });
        screenElement.dispatchEvent(mouseEvent);
      }
    }, this.longTouchDuration);
  }

  touchEndAction(evt, screenElement) {
    evt.preventDefault();
    this.isPointerMoving = false;
    const touchEndTimestamp = Date.now();
    const touchDuration = touchEndTimestamp - this.touchStartTimestamp;
    /***
     * If touch duration is less than 600ms, it is considered as a normal touch
     * and left button down is dispatched which is followed by mouseup.
     ***/
    if (
      touchDuration < this.longTouchDuration &&
      this.touchTimeoutId !== null
    ) {
      clearTimeout(this.touchTimeoutId);
      // If normal touch dispatching mousedown event.
      let mouseEvent = new MouseEvent("mousedown", {
        bubbles: true,
        cancelable: true,
        view: window,
        button: 0,
        buttons: 1,
        clientX: this.touchClientX,
        clientY: this.touchClientY,
      });
      screenElement.dispatchEvent(mouseEvent);
      // An immediate mouse up event to simulate a mouse click.
      mouseEvent = new MouseEvent("mouseup", {
        bubbles: true,
        cancelable: true,
        view: window,
        button: 0,
        buttons: 0,
        clientX: this.touchClientX,
        clientY: this.touchClientY,
      });
      screenElement.dispatchEvent(mouseEvent);
    }
    // If long touch is finished then mouseup is dispatched.
    else {
      const mouseEvent = new MouseEvent("mouseup", {
        bubbles: true,
        cancelable: true,
        view: window,
        button: 0,
        buttons: 0,
        clientX: this.touchClientX,
        clientY: this.touchClientY,
      });
      screenElement.dispatchEvent(mouseEvent);
    }
  }

  touchMoveAction(evt, screenElement) {
    this.isPointerMoving = true;
    if (this.touchTimeoutId !== null) {
      clearTimeout(this.touchTimeoutId);
      this.touchTimeoutId = null;
    }
    const numberOfPoints = evt.touches.length;
    // Simulate a wheel event only if two touches are detected.
    if (numberOfPoints === 2) {
      const currentPos = evt.touches[0].clientY;
      const dist = currentPos - (this.lastPos || currentPos);
      const wheelEvent = new WheelEvent("wheel", {
        deltaY: 0 - dist,
        clientX: evt.touches[0].clientX,
        clientY: evt.touches[0].clientY,
      });
      screenElement.dispatchEvent(wheelEvent);
      this.lastPos = currentPos;
    }
  }
}
