"""
run_web.py — no longer used as a standalone subprocess entry point.

The web server and camera now run as threads inside jeepbot_drive.py.
This file is kept for reference only. Run the robot with:

    python3 myconfig.py drive
"""

print(
    "NOTE: run_web.py is no longer needed.\n"
    "The web server starts automatically when you run:\n"
    "    python3 myconfig.py drive\n"
    "or:\n"
    "    python3 -c 'import myconfig; from jeepbot_drive import drive; drive(myconfig)'"
)
