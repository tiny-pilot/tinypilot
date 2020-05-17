# Python3 Seed

[![CircleCI](https://circleci.com/gh/mtlynch/python3_seed.svg?style=svg)](https://circleci.com/gh/mtlynch/python3_seed)

## Overview

A boilerplate Python 3 project set up for unit tests and continuous integration.

Specifically:

* Enforces Python style rules with [YAPF](https://github.com/google/yapf)
* Enforces style rules on docstrings using [DocStringChecker](https://chromium.googlesource.com/chromiumos/chromite/+/master/cli/cros/lint.py)
* Perfoms static analysis with [pyflakes](https://github.com/megies/pyflakes)
* Sorts imports with [isort](https://github.com/timothycrosley/isort)

## Installation

```bash
mkdir -p ./venv
virtualenv --python python3 ./venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```

## Customization

To customize this for your project:

1. Change `COPYRIGHT` to your name.
1. Change `LICENSE` to [a license of your choosing](https://choosealicense.com/).
1. Change the CircleCI badge in `README.md` to your own Circle CI project badge.
1. Change the app name in `app/main.py` from `Python Seed` to your app's name.
1. Rename `app/dummy.py` and `tests/test_dummy.py` to the module names of your choosing.
1. Begin working.

## Run

```bash
./app/main.py
```
