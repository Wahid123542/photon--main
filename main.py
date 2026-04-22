# This file is a launcher for src/main.py

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR/"src"

sys.path.insert(0, str(SRC_DIR))

# path for the real main.py
from main import main
from util import isDevMode

if __name__ == "__main__":
  if isDevMode():
    print("--- running in dev mode ---")
  else:
    print("--- running in release mode ---")
  main()
