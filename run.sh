#!/bin/bash

# Photo Upscaler CLI - Easy run script

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
    source .venv/bin/activate
    python3 setup.py
else
    source .venv/bin/activate
fi

python upscaler.py "$@"
