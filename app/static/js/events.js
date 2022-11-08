export class DialogClosedEvent extends CustomEvent {
  /**
   * Event that will close the overlay.
   */
  constructor() {
    super("dialog-closed", {
      bubbles: true,
      composed: true,
    });
  }
}

export class DialogFailedEvent extends CustomEvent {
  /**
   * Event that closes the dialog and displays the error dialog instead.
   * @param errorInfo object with the following properties:
   * - title (string) A concise summary of the error.
   * - message (string, optional) A user-friendly and helpful message that
   *   ideally gives the user some guidance what to do now. Defaults to a
   *   generic message.
   * - details (string|Error, optional) The technical error details, e.g. the
   *   original error message from the API or library call.
   */
  constructor(errorInfo) {
    super("dialog-failed", {
      detail: errorInfo,
      bubbles: true,
      composed: true,
    });
  }
}

export class DialogCloseStateChangedEvent extends CustomEvent {
  /**
   * Event that advises a state change affecting the dialog close
   * behavior: `canBeClosed` (defaults to true), informs that the
   * new state allows, or not, the dialog to be closed.
   */
  constructor(canBeClosed = true) {
    super("dialog-close-state-changed", {
      detail: {
        canBeClosed,
      },
      bubbles: true,
      composed: true,
    });
  }
}

export class VideoStreamingModeChangedEvent extends CustomEvent {
  /**
   * Event, which indicates that the video streaming mode has changed.
   * @param mode {string} The new mode, e.g.: `MJPEG` or `H264`.
   */
  constructor(mode) {
    super("video-streaming-mode-changed", {
      detail: {
        mode,
      },
      bubbles: true,
      composed: true,
    });
  }
}
