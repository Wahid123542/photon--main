#!/bin/bash
cd "$(dirname "$0")"

if [ -d "venv" ]; then
    source venv/bin/activate

    # Force PyQt6's bundled Qt6 libs to load before any system Qt6 libs
    PYQT6_QT_LIBS="$(python3 -c "import os, PyQt6; print(os.path.join(os.path.dirname(PyQt6.__file__), 'Qt6', 'lib'))" 2>/dev/null)"
    if [ -n "$PYQT6_QT_LIBS" ] && [ -d "$PYQT6_QT_LIBS" ]; then
        export LD_LIBRARY_PATH="$PYQT6_QT_LIBS:${LD_LIBRARY_PATH:-}"
    fi

    # Prevent GStreamer from touching X11 display (avoids XCB race during window move + audio init)
    export GST_GL_WINDOW=offscreen
    # Disable MIT-SHM shared memory extension (known cause of XCB segfaults on Linux VMs)
    export QT_XCB_NO_MITSHM=1

    echo "Environment activated. Launching Photon..."
    python3 main.py
else
    echo "Error: venv not found. Please run ./wininstall.sh first."
    exit 1
fi
