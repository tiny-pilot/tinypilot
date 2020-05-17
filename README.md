# PiKVM Backend

## Overview

The backend for PiKVM.

## Installation

```bash
mkdir -p ./venv
virtualenv --python python3 ./venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```

## Run

```bash
./serve
```
