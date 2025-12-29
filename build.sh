#!/bin/bash
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install setuptools wheel
python -m pip install -r requirements.txt
echo "Build completed!"