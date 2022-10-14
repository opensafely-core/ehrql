#!/bin/bash

# -B: don't write bytecode files
/opt/venv/bin/python3.9 -B -m databuilder "$@"
