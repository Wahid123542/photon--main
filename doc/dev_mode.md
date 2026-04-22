# Dev mode

## Why dev mode?
This technique is for a better QA experience.

At least, it can achieve...
- skip the splashscreen waiting time
- avoid typing in info to the table to test APIs every time

## Commands to toggle dev mode
(all written for PowerShell)

set the program to a developer mode
```powershell: set to a developer mode
$env:APP_MODE="DEV";
python main.py

```
set the program to a release mode

```powershell: set to a release mode
$env:APP_MODE="";
python main.py

```

## How to implement "if dev mode" in code
Please use a function at [src/util.py](../src/util.py).

Below is a demonstration.

```py:example.py
from util import isDevMode

if __name__ == "__main__":
  if isDevMode():
    print("dev mode!")
  else:
    print("release mode!")

```