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

export class StateDisablingCloseEvent extends CustomEvent {
  /**
   * Event warning that we enter a state that disables the close behavior.
   */
  constructor() {
    super("state-disabling-close", {
      bubbles: true,
      composed: true,
    });
  }
}

export class StateAllowingCloseEvent extends CustomEvent {
  /**
   * Event warning that we enter a state that allows the close behavior.
   */
  constructor() {
    super("state-allowing-close", {
      bubbles: true,
      composed: true,
    });
  }
}
