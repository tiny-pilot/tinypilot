# Contributing

Thanks for being interested in TinyPilot! This document is meant to help developers get up to speed on TinyPilot so that they can start development with as little frustration as possible.

## Setting up a development environment

The steps below show you how to quickly set up a development environment for TinyPilot.

### Requirements

- Python 3.9 or higher
- Node.js 18.16.1 or higher
- [shellcheck](https://github.com/koalaman/shellcheck#installing)
- [bats](https://bats-core.readthedocs.io/en/stable/installation.html)
- Docker 20.10.x or higher

### Install packages

To install TinyPilot's dev packages, run the following command:

```bash
python3 -m venv venv && \
  . venv/bin/activate && \
  pip install --requirement dev_requirements.txt && \
  npm install && \
  sudo npx playwright install-deps && \
  ./dev-scripts/enable-multiarch-docker
```

### Run dev tests

To run TinyPilot's build scripts, run:

```bash
./dev-scripts/check-all
```

### Run end-to-end tests

To spawn a TinyPilot local dev server and run TinyPilot's end-to-end tests against that dev server, run:

```bash
./dev-scripts/run-e2e-tests
```

To run TinyPilot's end-to-end tests against a running TinyPilot device, first turn off HTTPS redirection. Open the device's page in your browser and click through the privacy error. Then, navigate the menu options `System > Security`. Turn off "Require encrypted connection (HTTPS)". Finally, run the tests by passing an http URL as the first argument like so:

```bash
./dev-scripts/run-e2e-tests http://tinypilot.local
```

### Enable Git hooks

If you're planning to contribute code to TinyPilot, it's a good idea to enable the standard Git hooks so that build scripts run before you commit. That way, you can see if basic tests pass in a few seconds rather than waiting a few minutes to watch them run in CircleCI.

```bash
./dev-scripts/enable-git-hooks
```

### Enable mock scripts and passwordless sudo access

The TinyPilot server backend uses several privileged scripts (provisioned to [`/opt/tinypilot-privileged/scripts/`](debian-pkg/opt/tinypilot-privileged/scripts)). Those scripts exist on a provisioned TinyPilot device, but they don't exist on a dev machine.

To set up symlinks that mock out those scripts and facilitate development, run the following command:

```bash
sudo ./dev-scripts/enable-mock-scripts
```

If you do not already have passwordless sudo enabled in general, you also need to allow the server backend to execute these privileged scripts and other services without interactively prompting you for a password. To do that, run:

```bash
sudo ./dev-scripts/enable-passwordless-sudo
```

### Run in dev mode

To run TinyPilot on a non-Pi machine, run:

```bash
./dev-scripts/serve-dev
```

### Open dialogs after page load

If you are doing UI development in a dialog, it can be cumbersome to having to open a dialog via the menu after every page refresh.

For convenience, you can append a parameter called `request` to the page URL, and specify the HTML id of the dialog as value. That will open the respective dialog straight away.

Example: `http://localhost:8000?request=about-dialog`

Technically, this assembles a `about-dialog-requested` event and dispatches it to the menu bar component.

## QA/Testing on a TinyPilot device

It’s useful to have a TinyPilot device set up for testing changes end-to-end and in a real production environment.

One upfront note about security: the following guides suggest intentionally loose security settings. This is a trade-off for development convenience. You should only take them over if your TinyPilot device resides in a private network, and if it isn’t connected to a target machine with sensitive data.

### Local SSH Setup

For convenient SSH access to your TinyPilot device, you should [generate a pair of dedicated SSH keys](https://www.raspberrypi.com/documentation/computers/remote-access.html#generate-new-ssh-keys) on your dev machine, e.g. `~/.ssh/tinypilot`.

By adding the following block to your `~/.ssh/config` file, your dev machine will pick up your SSH key for accessing the TinyPilot device, and your dev machine will also skip the integrity checks of the connection.

```
Host raspberrypi raspberrypi.local
  User root
  IdentityFile ~/.ssh/tinypilot
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
```

### Remote SSH Setup

On the remote machine, add your public SSH key to the `/root/.ssh/authorized_keys` file. If the file or directory doesn’t exist yet, you have to create it manually.

```bash
sudo su
mkdir -p /root/.ssh
echo 'YOUR_PUBLIC_SSH_KEY' > /root/.ssh/authorized_keys
```

In order to do this, you have to authenticate via username/password.

On TinyPilot Pro, the default username/password is `pilot`/`flyingsopi`. Remember to first enable SSH access via the security settings dialog in the TinyPilot Pro web UI.

### Flash SD-card with clean Raspberry Pi OS

For setting up a clean device, we recommend using the [“Raspberry Pi Imager” app](https://www.raspberrypi.com/software/) for flashing SD-cards. Make sure you use the following settings:

- Lite version of Raspberry Pi OS (i.e., no desktop environment)
- Enable SSH access
- Add your public SSH key as authorized key

By the way, for flashing the ready-made disk images of TinyPilot Pro, we recommend using the [“Balena Etcher” app](https://etcher.balena.io/).

### Initialize system on Voyager hardware

If you want to initialize a new system on Voyager hardware, you first need to set some configuration in place to make TinyPilot work with Voyager’s video capture chip.

```bash
# Create tinypilot system user and group.
addgroup --system tinypilot
adduser \
    --system \
    --shell /bin/bash \
    --ingroup tinypilot \
    --home "/home/tinypilot" \
    tinypilot

# Add uStreamer configuration.
echo "dtoverlay=tc358743" | sudo tee --append /boot/config.txt
```

### Install from source

To build and install your changes on device, perform the following steps:

1. [Install Docker](https://docs.docker.com/engine/install/raspbian/#install-using-the-convenience-script) (if you haven't already):
   ```bash
   curl -fsSL https://get.docker.com | sudo bash -
   ```
1. On the device, clone the TinyPilot repo to a temporary directory.
1. Check out the branch that has your changes.
1. Run the [`dev-scripts/device/install-from-source`](dev-scripts/device/install-from-source) script to build and install your branch's code. For example:
   ```bash
   sudo dev-scripts/device/install-from-source
   ```

### Installing a TinyPilot bundle

The canonical way to build bundles is on CircleCI. The `build_bundle` CircleCI job will store built bundles as artifacts.

For TinyPilot Community, you can just copy the URL to the artifact directly on CircleCI.

For TinyPilot Pro, CircleCI prevents anonymous downloads of CircleCI artifacts. To make the bundle URL available, you'll need to move the bundle from CircleCI to PicoShare:

1. Download the bundle file from CircleCI.
1. Upload the bundle file to TinyPilot's PicoShare server.
   - [See this (org-private) Wiki page for our internal sharing URL](https://github.com/tiny-pilot/tinypilot-pro/wiki/PicoShare-Server-for-Uploading-Dev-Bundles).
1. Copy the PicoShare URL for the TinyPilot bundle.

In order to install a TinyPilot bundle on device, run the following command:

```bash
curl \
  --silent \
  --show-error \
  --location \
  https://raw.githubusercontent.com/tiny-pilot/tinypilot/master/dev-scripts/device/install-bundle | \
  sudo bash -s -- \
    url-to-bundle-file # replace this line with your bundle URL
```

### Build a uStreamer Debian package

CircleCI builds the uStreamer Debian package for the `armhf` architecture on every commit to the [`ustreamer-debian` repo](https://github.com/tiny-pilot/ustreamer-debian), which is stored as a CircleCI artifact.

Follow these steps:

1. Make changes to the [`ustreamer-debian` Github repo](https://github.com/tiny-pilot/ustreamer-debian).
1. Push your changes to a branch on Github.
1. Find your job in `ustreamer-debian`'s CircleCI dashboard and click the `test` workflow.
1. Click the `build_debian_package` job.
   - If the [`build_debian_package` CircleCI job](https://github.com/tiny-pilot/ustreamer-debian/blob/2ace4a1d22a3c9108f5285e3dff0290c60e5b1cf/.circleci/config.yml#L25) fails for some reason, you can manually debug the code in CircleCI by clicking "rerun job with SSH" in the CircleCI dashboard and following their SSH instructions. Remember to cancel the CircleCI job once you're done debugging, in order to reduce CI costs.
1. When the job completes, go to the "Artifacts" tab of the `build_debian_package` job on CircleCI to find the uStreamer Debian packages.

   - We use `armhf`-based builds on physical devices and for testing in CircleCI.
   - [Docker platform names don't match Debian architecture names:](https://github.com/tiny-pilot/ustreamer-debian/blob/2ace4a1d22a3c9108f5285e3dff0290c60e5b1cf/Dockerfile#L46C1-L48)

     > Docker's platform names don't match Debian's platform names, so we translate
     > the platform name from the Docker version to the Debian version...

     Which means that when Docker's target platform is:

     - `linux/arm/v7`, CircleCI creates a `armhf` Debian package

### Install a uStreamer Debian package

Follow these steps to install a uStreamer Debian package on a physical device:

1. [Build a uStreamer Debian package](CONTRIBUTING.md#build-a-uStreamer-Debian-package).
1. Copy the URL of the uStreamer Debian package created in step (1).
1. SSH onto the device and run the following command:

   ```bash
   DEBIAN_PACKAGE_PATH=url-to-debian-package # Replace the Debian package URL here.
   DEBIAN_PACKAGE_FILE="$(mktemp)"
   curl \
     --silent \
     --show-error \
     --location \
     --output "${DEBIAN_PACKAGE_FILE}" \
     "${DEBIAN_PACKAGE_PATH}" && \
     sudo apt-get install --yes "${DEBIAN_PACKAGE_FILE}"
   ```

## Other dev workflows

### Scripting often-used procedures

For common procedures that you need to repeat often, it’s useful to encode them as bash scripts. We currently don’t provide off-the-shelf scripts here, because the dev setups and environments are too different.

As a tip: given that your SSH config is all set, you can script commands for the remote machine like this:

```bash
# Execute single command.
ssh raspberrypi "echo 'Hello World'"

# Execute multiple commands.
ssh raspberrypi << 'ENDSSH'
echo 'Hello ...'
echo '... World!'
ENDSSH
```

### Updating Python pip packages

We don't use any Python package management tools because we want to limit complexity, but it means we use a manual process to update the pip packages we use in production:

1. `deactivate` to exit the virtual env (if you're in one).
1. `rm -rf venv` to get rid of dev packages.
1. `sed '/# Indirect dependencies/q' requirements.txt | tee requirements.txt` to delete all the indirect dependencies from `requirements.txt`
1. Update the version number of the PyPI package you want to update.
1. Review the package's changelog, and look for any breaking changes since our last update.
1. `python3 -m venv venv && . venv/bin/activate && pip install --requirement requirements.txt` to reinstall production dependencies.
1. `pip freeze >> requirements.txt` to dump exact version numbers of all direct and indirect dependencies.
1. `awk '/^\s*$/ || !a[tolower($0)]++' requirements.txt | tee requirements.txt` to delete duplicate lines.
1. Update `app/license_notice.py` to match any changes in `requirements.txt`.

We don't track indirect dependencies for our dev dependencies (in `dev_requirements.txt`), so you can update those by simply changing the version number for any package.

### Building an ARMv7 bundle on a dev system

To build a TinyPilot install bundle on your dev system, you first need to configure a Docker builder for multi-architecture builds using QEMU. You only need to perform this step once per system:

```bash
./dev-scripts/enable-multiarch-docker
```

Once your dev system is configured for multi-architecture Docker builds, you can build install ARMv7 TinyPilot bundles with the following commands:

```bash
TARGET_PLATFORM='linux/arm/v7'

(rm debian-pkg/releases/tinypilot*.deb || true) && \
  ./dev-scripts/build-debian-pkg "${TARGET_PLATFORM}" && \
  mv debian-pkg/releases/tinypilot*.deb bundler/bundle && \
  ./bundler/create-bundle
```

The newly built install bundle will be in `./bundler/dist`.

## Architecture

For a high-level view of TinyPilot's architecture, see the [ARCHITECTURE](ARCHITECTURE.md) file.

## Options

TinyPilot accepts various options through environment variables:

| Environment Variable | Default     | Description                                           |
| -------------------- | ----------- | ----------------------------------------------------- |
| `HOST`               | `127.0.0.1` | Network interface to listen for incoming connections. |
| `PORT`               | `48000`     | HTTP port to listen for incoming connections.         |
| `DEBUG`              | undefined   | Set to `1` to enable debug logging.                   |

## Code style conventions

See [tinypilot/style-guides](https://github.com/tiny-pilot/style-guides).

## User interface style guide

We document UI patterns and components in a style guide, to maintain a consistent user experience throughout the web application.

After launching TinyPilot in debug mode, the style guide is available at [localhost:8000/styleguide](http://localhost:8000/styleguide).

## Web Components Conventions

TinyPilot implements most of its UI components through standard JavaScript, using [web components](https://css-tricks.com/an-introduction-to-web-components/). TinyPilot does not use any heavy frontend frameworks like Angular or React, nor does it use any broad libraries such as jQuery.

Strangely, it's uncommon for web applications to use web components directly as opposed to through a framework, so TinyPilot's developers have created their own conventions for implementing UI elements through web components.

### State changes

It's common for a component to change its appearance based on its internal state. For example, a dialog might be in an "initializing" state when it first opens and then reach a "ready" state when it's ready for user input.

In a framework like React or Vue, we'd use conditional rendering to change the UI depending on the component's internal state. With raw web components, conditional rendering is not possible. Instead, TinyPilot's convention is to add a `state` attribute to the root element with getter and setter methods that look like this:

```javascript
get _state() {
  return this.getAttribute("state");
}

set _state(newValue) {
  this.setAttribute("state", newValue);
}
```

We enumerate all possible state values in the `_states` property on the web component class, like so:

```javascript
class extends HTMLElement {
    _states = {
        INITIALIZING: "initializing",
        FETCH_FROM_URL: "fetch-from-url",
        VIEW: "view",
    };
```

The class property `_states` can then be used in the JavaScript component code:

```javascript
this._state = this._states.INITIALIZING;
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

We can then initialize the component when the dialog is opened by listening for the `overlay-shown` event:

```javascript
connectedCallback() {
  this.addEventListener("overlay-shown", () => {
    this._state = this._states.INITIALIZING);
  };
}
```

### Disable closing a dialog

For a component that is used within an overlay, there might be certain states that should prevent the user from closing the dialog. That’s typically the case when we are waiting for an action to complete (for example when loading something).

These particular states are listed in the `_statesWithoutDialogClose` class property, like so:

```javascript
class extends HTMLElement {
    _states = {
        INITIALIZING: "initializing",
        FETCH_FROM_URL: "fetch-from-url",
        VIEW: "view",
    };
    _statesWithoutDialogClose = new Set([this._states.INITIALIZING]);
```

Note: for consistency, we always use a `Set` here, even if it only contains a single element.

In the state setter, we emit an event to inform the enclosing overlay whether or not to show the `x` close button.

```javascript
set _state(newValue) {
    this.setAttribute("state", newValue);
    this.dispatchEvent(
    new DialogCloseStateChangedEvent(
        !this._statesWithoutDialogClose.has(newValue)
    )
    );
}
```

This event will be picked up by the `overlay-panel` which will hide the X close button.

### Create element references in `connectedCallback()`

If a component's JavaScript requires access to any of the elements in the web component's HTML, assign those elements an `id` attribute and store them in a member object called `this._elements`

```javascript
connectedCallback() {
  this.attachShadow({ mode: "open" });
  this.shadowRoot.appendChild(template.content.cloneNode(true));
  this._elements = {
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

### Use an underscore-prefix to name private members

For internal class members (i.e., functions or fields) of a web component that are only supposed to be used within the component, prepend the member name with an underscore like `_upload() { ... }` or `this._port = 8080`. Public members, e.g. functions that are invoked from the outside, should be prefix-free like `show()`.

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
<my-component style="--offset-top: 3rem"></my-component>
```

### Referencing DOM elements

In short, if your component has multiple [states](#state-changes) then prefer to reference an element using the `class` attribute to avoid naming conflicts. Otherwise, reference an element using the `id` attribute as needed.

More verbosely, in order to reference a DOM element using JavaScript, we need to first name the element using the `id` or `class` attribute.

For example, say we have a component that creates a user:

```html
<div class="btn-container">
  <button id="confirm-btn">Confirm Create<button>
</div>
```

```javascript
const confirmButton = document.querySelector("#confirm-btn");
const buttonContainer = document.querySelector(".btn-container");
```

The above example is a rather straightforward way of naming and selecting DOM elements. However, things can get complicated when the component has multiple [states](#state-changes).

For example, say that we expand our component to also delete a user:

```html
<div id="create">
  <div class="btn-container">
    <button id="confirm-create-btn">Confirm Create<button>
  </div>
</div>

<div id="delete">
  <div class="btn-container">
    <button id="confirm-delete-btn">Confirm Delete<button>
  </div>
</div>
```

```javascript
const confirmCreateButton = document.querySelector("#confirm-create-btn");
const confirmDeleteButton = document.querySelector("#confirm-delete-btn");

const confirmCreateButtonContainer = document.querySelector(
  "#create .btn-container"
);
const confirmDeleteButtonContainer = document.querySelector(
  "#delete .btn-container"
);
```

Notice how we needed to rename both our button IDs to distinguish between the create and delete buttons.

Also notice how we did not need to rename our button container classes because their query selector can be scoped to a specific component state.

In order to avoid namespacing individual element IDs, as we expand a component, we prefer to name an element using the `class` attribute and namespace the query selector instead.

So instead of this:

```javascript
document.querySelector("#confirm-create-btn");
document.querySelector("#confirm-delete-btn");
```

we do this:

```javascript
document.querySelector("#create .confirm-btn");
document.querySelector("#delete .confirm-btn");
```

Let's complete our example by pulling it altogether:

```html
<div id="create">
  <div class="btn-container">
    <button class="confirm-btn">Confirm Create<button>
  </div>
</div>

<div id="delete">
  <div class="btn-container">
    <button class="confirm-btn">Confirm Delete<button>
  </div>
</div>
```

```javascript
const confirmCreateButton = document.querySelector("#create .confirm-btn");
const confirmDeleteButton = document.querySelector("#delete .confirm-btn");
```

## Proposing changes

- If you're making a small change, submit a PR to show your proposal.
- If you're making a large change (over 100 LOC or three hours of dev time), [file an issue](https://github.com/tiny-pilot/tinypilot/issues/new/choose) first to talk through the proposed change. This prevents you from wasting time on a change that has a low chance of being accepted.

## How to get your PR merged quickly

- Read my guide, ["How to Make Your Code Reviewer Fall in Love with You,"](https://mtlynch.io/code-review-love/) to understand how to contribute effectively to an open source project.
- Give a clear, one-line title to your PR.
  - Good: `Fix dropped keystrokes on Firefox`
  - Bad: `Fix issue`
- If your PR is not ready for review, mark it as "draft."
- [Rebase your changes](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase) onto the latest `master` commit so that there are no merge conflicts.
- Your PR must pass build checks in CI before it will be considered for merge.
  - You'll see a green checkmark or red X next to your PR depending on whether your build passed or failed.
  - You are responsible for fixing formatting and tests to ensure that your code passes build checks in CI.

I try to review all PRs within one business day. If you've been waiting longer than this, feel free to comment on the PR to verify that it's on my radar.
