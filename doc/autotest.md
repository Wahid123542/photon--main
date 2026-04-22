## Autotest

1. ```python test.py``` at the root path allows you to run both ```main.py``` and ```src/traffic-generator.py``` simultaneously in a single terminal!
2. some input requests (like a team member ID) is replaced with a constant value in a debug mode for a shortened QA process, which is activated temporalily by casting ```$env:APP_MODE="DEV";``` for WindowsOS Powershell and ```APP_MODE=DEV``` for macOS bash.
3. to pause the running program, use ```Ctrl+C```!