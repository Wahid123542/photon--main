#!/bin/bash
set -e

echo "--- Installing System Dependencies ---"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv build-essential \
python3-dev python3-pyqt6 python3-pyqt6.qtmultimedia \
libpq-dev postgresql-client dos2unix

echo "--- Converting scripts to Unix format ---"
for f in install.sh run.sh; do
    [ -f "$f" ] && dos2unix "$f" || true
done

echo "--- Setting up Virtual Environment ---"
rm -rf venv
python3 -m venv venv --system-site-packages
source venv/bin/activate

echo "--- Upgrading pip, setuptools, wheel ---"
pip install --upgrade pip setuptools wheel

echo "--- Installing Python Libraries ---"
# Skip PyQt6 since system package is used
pip install psycopg2-binary pygame

if [ -f requirements.txt ]; then
    echo "--- Installing from requirements.txt (without PyQt6) ---"
    grep -v "PyQt6" requirements.txt > temp_reqs.txt
    pip install -r temp_reqs.txt
    rm temp_reqs.txt
fi

chmod +x run.sh

echo "------------------------------------"
echo "Installation complete!"
echo "Run project with: ./run.sh"
