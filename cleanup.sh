#!/bin/bash
set -e

echo "--- Deactivating virtual environment if active ---"
deactivate 2>/dev/null || true

echo "--- Removing virtual environment ---"
rm -rf venv

echo "--- Removing executable permissions from run.sh ---"
chmod -x run.sh

echo "--- Removing installed Python packages in user site (if any) ---"
pip3 uninstall -y psycopg2-binary pygame || true

echo "--- Cleanup complete ---"
