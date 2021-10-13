# Contributing

Thanks for being interested in TinyPilot! This document is meant to help developers get up to speed on TinyPilot so that they can start development with as little frustration as possible.

## Setting up a development environment

The steps below show you how to quickly set up a development environment for TinyPilot.

### Requirements

* Python 3.7 or higher
* Node.js 14.17.5 or higher
* [shellcheck](https://github.com/koalaman/shellcheck#installing)

### Install packages

To install TinyPilot's dev packages, run the following command:

```bash
python3.7 -m venv venv && \
  . venv/bin/activate && \
  pip install --requirement requirements.txt && \
  pip install --requirement dev_requirements.txt && \
  npm install
```

### Run automated tests

To run TinyPilot's build scripts, run:

```bash
./dev-scripts/build
```

### Enable Git hooks

If you're planning to contribute code to TinyPilot, it's a good idea to enable the standard Git hooks so that build scripts run before you commit. That way, you can see if basic tests pass in a few seconds rather than waiting a few minutes to watch them run in CircleCI.

```bash
./hooks/enable_hooks
```

### Enable mock scripts

The TinyPilot server backend uses several privileged scripts (created in [ansible-role-tinypilot](https://github.com/tiny-pilot/ansible-role-tinypilot)). Those scripts exist on a provisioned TinyPilot device, but they don't exist on a dev machine.

To set up symlinks that mock out those scripts and facilitate development, run the following command:

```bash
sudo ./dev-scripts/enable-mock-scripts
```

### Run in dev mode

To run TinyPilot on a non-Pi machine, run:

```bash
./dev-scripts/serve-dev
```

## Setting up a device for QA/testing

For more complex changes it is useful to test your feature branch on a Raspberry Pi, in order to verify them in the real production environment.

### Setup SSH keys for login

1. [Generate SSH keys and upload your public key](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md) to your device. Please use strong keys, e.g., ED25519 or RSA 4096+.
2. Verify that you can login with your SSH keys.
3. On the device, disable password-based login by specifying `PasswordAuthentication no` in `/etc/ssh/sshd_config`. Reboot afterwards.

### SSH agent forwarding

In case you need SSH keys for accessing the Git repositories (e.g., for testing TinyPilot's Pro version), please enable SSH agent forwarding in your local `~/.ssh/config`.

```
Host tinypilot
  ForwardAgent yes
```

### Remote scripts

For carrying out common procedures on the device, see [here](dev-scripts/remote-scripts/README.md).

## Architecture

For a high-level view of TinyPilot's architecture, see the [ARCHITECTURE](ARCHITECTURE.md) file.

## Options

TinyPilot accepts various options through environment variables:

| Environment Variable | Default      | Description |
|----------------------|--------------|-------------|
| `HOST`               | `127.0.0.1`  | Network interface to listen for incoming connections. |
| `PORT`               | `8000`       | HTTP port to listen for incoming connections. |
| `DEBUG`              | undefined    | Set to `1` to enable debug logging. |

## Code style conventions

TinyPilot follows Google code style conventions:

* [Python](https://google.github.io/styleguide/pyguide.html)
* [HTML/CSS](https://google.github.io/styleguide/htmlcssguide.html)
* [Shell](https://google.github.io/styleguide/shellguide.html)
* ~~[JavaScript](https://google.github.io/styleguide/jsguide.html)~~ - We are "loosely inspired" by the JS style guide, but don't observe it strictly

TinyPilot uses automated linters and formatters as much as possible to automate style conventions.

## Web Components Conventions

TinyPilot implements most of its UI components through standard JavaScript, using [web components](https://css-tricks.com/an-introduction-to-web-components/). TinyPilot does not use any heavy frontend frameworks like Angular or React, nor does it use any broad libraries such as jQuery.

Strangely, it's uncommon for web applications to use web components directly as opposed to through a framework, so TinyPilot's developers have created their own conventions for implementing UI elements through web components.

### State changes

It's common for a component to change its appearance based on its internal state. For example, a dialog might be in an "initializing" state when it first opens and then reach a "ready" state when it's ready for user input.

In a framework like React or Vue, we'd use conditional rendering to change the UI depending on the component's internal state. With raw web components, conditional rendering is not possible. Instead, TinyPilot's convention is to add a `state` attribute to the root element with getter and setter methods that look like this:

```javascript
get state() {
  return this.getAttribute("state");
}

set state(newValue) {
  this.setAttribute("state", newValue);
}
```

We define the different states in the JavaScript component through the class attribute `states`. The states names need to be identical to the CSS states names that we define later.

```javascript
class extends HTMLElement {
    states = {
        INITIALIZING: "initializing",
        FETCH_FROM_URL: "fetch-from-url",
        VIEW: "view",
    };
```

 The class attribute `states` can then be used in the JavaScript component code:

```javascript
this.state = this.states.FETCH_FROM_URL;
```

We then use CSS rules based on the `state` attribute to control the component's appearance:

```html
<style>
  #initializing,
  #fetch-from-url {
    display: none;
  }

  :host([state="initializing"]) #initializing {
    display: block;
  }

  :host([state="fetch-from-url"]) #fetch-from-url {
    display: block;
  }
</style>

<div id="initializing">
  <h3>Retrieving Information</h3>
  <progress-spinner></progress-spinner>
</div>

<div id="fetch-from-url">
  <h3>Manage Virtual Media: Fetch from URL</h3>
  ...
</div>
```

This ensures that the elements in the `<div id="initializing">` only appear when the component's state is `initializing`.

Prefer to change a web component's appearance based on attributes and CSS rules as opposed to JavaScript that manipulates the `.style` attributes of elements within the component.

### Disable closing a dialog

For a component embedded in a dialog (using `overlay-panel`), we might want in some states to prevent the user from closing the dialog, typically when we are waiting for an action to complete (for example loading logs).

We define the states that require preventing the user from closing the dialog in the `statesWithoutDialogClose` component attribute:

```javascript
class extends HTMLElement {
    states = {
        INITIALIZING: "initializing",
        FETCH_FROM_URL: "fetch-from-url",
        VIEW: "view",
    };
    statesWithoutDialogClose = new Set([this.states.INITIALIZING]);
```

Note: even if there is only one state, we use the attribute `statesWithoutDialogClose` as a `Set` with only one element, for consistency.

Then we update the state setter to emit an event when the state changes, giving the information whether we should allow, or not, the user to close the dialog:

```javascript
set state(newValue) {
    this.setAttribute("state", newValue);
    this.dispatchEvent(
    new DialogCloseStateChangedEvent(
        !this.statesWithoutDialogClose.has(newValue)
    )
    );
}
```

This event will be picked up by the `overlay-panel` which will hide the X close button.

### Create element references in `connectedCallback()`

If a component's JavaScript requires access to any of the elements in the web component's HTML, assign those elements an `id` attribute and store them in a member object called `this.elements`

```javascript
connectedCallback() {
  this.attachShadow({ mode: "open" });
  this.shadowRoot.appendChild(template.content.cloneNode(true));
  this.elements = {
    noFilesText: this.shadowRoot.getElementById("no-backing-files"),
    table: this.shadowRoot.getElementById("backing-files-table"),
    tableBody: this.shadowRoot.getElementById("table-body"),
    uploadFromUrlInput: this.shadowRoot.getElementById(
      "fetch-from-url-input"
    ),
    uploadFromUrlInputError: this.shadowRoot.getElementById(
      "fetch-from-url-input-error"
    ),
  };
};
```

### Use underscore to represent private methods

Most of the functions in a web component are only intended for usage within the component. For these functions, prepend the function name with an underscore like `_upload() { ... }`. Functions that accept input from external callers should be prefix-free like `show()`.

### Use free functions where possible

If a function does not reference any of the web component's member variables through `this`, convert it to a free function outside of the `HTMLElement` subclass.

If a function only requires access to one or two member variables, consider making it a free function anyway and accessing those values through function parameters.

Free functions are easier to reason about than member functions, as free functions have access to fewer variables and functions that can change an object's state.

### Parameterizing style rules

Web components have a separate ["shadow DOM,"](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_shadow_DOM) which means that they don't inherit most CSS rules from their parent elements. In some cases, it's useful for a web component to accept style customization through the parent element's HTML.

TinyPilot's convention for this is to define CSS variables in the `:host` section like so:

```css
:host {
    --offset-top: 1rem;
}

h2 {
  margin-top: var(--offset-top);
}
```

Using CSS variables means that we can parameterize these values via the `style` attribute when we include instances of the component in HTML:

```html
<my-component style="--offset-top: 3rem">
```

## Proposing changes

* If you're making a small change, submit a PR to show your proposal.
* If you're making a large change (over 100 LOC or three hours of dev time), [file an issue](https://github.com/tiny-pilot/tinypilot/issues/new/choose) first to talk through the proposed change. This prevents you from wasting time on a change that has a low chance of being accepted.

## How to get your PR merged quickly

* Read my guide, ["How to Make Your Code Reviewer Fall in Love with You,"](https://mtlynch.io/code-review-love/) to understand how to contribute effectively to an open source project.
* Give a clear, one-line title to your PR.
  * Good: `Fix dropped keystrokes on Firefox`
  * Bad: `Fix issue`
* If your PR is not ready for review, mark it as "draft."
* [Rebase your changes](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase) onto the latest `master` commit so that there are no merge conflicts.
* Your PR must pass build checks in CI before it will be considered for merge.
  * You'll see a green checkmark or red X next to your PR depending on whether your build passed or failed.
  * You are responsible for fixing formatting and tests to ensure that your code passes build checks in CI.

I try to review all PRs within one business day. If you've been waiting longer than this, feel free to comment on the PR to verify that it's on my radar.
