# Contributing

Thanks for being interested in TinyPilot! This document is meant to help developers get up to speed on TinyPilot so that they can start development with as little frustration as possible.

## Setting up a development environment

The steps below show you how to quickly set up a development environment for TinyPilot.

### Requirements

* Python 3.7 or higher
* Node.js 13.x or higher

### Install packages

To install TinyPilot's dev packages, run the following command:

```bash
python3.7 -m venv venv && \
  . venv/bin/activate && \
  pip install --requirement requirements.txt && \
  pip install --requirement dev_requirements.txt && \
  npm install prettier@2.0.5
```

TinyPilot uses [ShellCheck](https://github.com/koalaman/shellcheck) to do
static analysis on its bash scripts.
[Install ShellCheck](https://github.com/koalaman/shellcheck#installing) through
your package manager:

```bash
# Debian/Ubuntu/Mint
sudo apt-get install shellcheck
# macOS
brew install shellcheck
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

The TinyPilot server backend uses several privileged scripts (created in [ansible-role-tinypilot](https://github.com/mtlynch/ansible-role-tinypilot)). Those scripts exist on a provisioned TinyPilot device, but they don't exist on a dev machine.

To set up symlinks that mock out those scripts and facilitate development, run the following command:

```bash
sudo ./dev-scripts/enable-mock-scripts
```

### Run in dev mode

To run TinyPilot on a non-Pi machine, run:

```bash
./dev-scripts/serve-dev
```

## Architecture

For a high-level view of TinyPilot's architecture, see the [ARCHITECTURE](ARCHITECTURE.md) file.

## Code style conventions

TinyPilot follows Google code style conventions:

* [Python](https://google.github.io/styleguide/pyguide.html)
* [HTML/CSS](https://google.github.io/styleguide/htmlcssguide.html)
* [Shell](https://google.github.io/styleguide/shellguide.html)
* ~~[JavaScript](https://google.github.io/styleguide/jsguide.html)~~ - We are "loosely inspired" by the JS style guide, but don't observe it strictly

TinyPilot uses automated linters and formatters as much as possible to automate style conventions.

## Proposing changes

* If you're making a small change, submit a PR to show your proposal.
* If you're making a large change (over 100 LOC or three hours of dev time), [file an issue](https://github.com/mtlynch/tinypilot/issues/new/choose) first to talk through the proposed change. This prevents you from wasting time on a change that has a low chance of being accepted.

See the [pull request template](.github/pull_request_template.md) for more details on submitting a pull request.
