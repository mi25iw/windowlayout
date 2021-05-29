import json
import os
import subprocess
import sys
import time

from .window import Window

LAYOUT_FILE = os.path.expanduser("~/.windowlayout.json")
DEFAULT_LAYOUT = "default"
ENV_TAG = "PY_WINDOWLAYOUT_ID"


def load_layout(filename=None):
    filename = filename or LAYOUT_FILE
    if os.path.exists(filename):
        with open(filename, encoding='utf-8-sig') as f:
            return json.load(f)

    return {"programs": {}, "layouts": {}}


def save_layout(layout, filename=None):
    filename = filename or LAYOUT_FILE
    with open(filename, "w", encoding='utf-8') as f:
        f.write(json.dumps(layout, indent=4))

    return filename


def add_current_layout(layout_name=None, layout_file=None):
    '''Gets the current layout of visible windows'''

    data = load_layout(layout_file)

    # Auto-generate layout name, if needed
    if layout_name is None:
        layout_name = DEFAULT_LAYOUT
        if data is not None:
            i = 0
            while layout_name in data["layouts"]:
                i += 1
                layout_name = f"saved_{i}"

    data["layouts"][layout_name] = {}

    for w in Window.get_visible():
        try:
            cmd = w.process.commandline()
        except Exception:  # can get an access denied error, so have a fallback
            cmd = w.process.exe()

        # Generate unique program ID for this program in case there are
        # multiple instances
        pname = os.path.basename(w.process.exe())
        pname = os.path.splitext(pname)[0].lower()
        name = pname
        i = 0
        while name in data["programs"]:
            i += 1
            name = f"{pname}{i}"

        # Add all relevant program info so user can easily tweak as needed
        data["programs"][name] = {
            "command": cmd,
            "detected_command": cmd,
            "detected_title": w.title,
            "detected_class": w.wclass,
            "suppress_start": False,
        }

        # Capture where the window is
        rect = w.rect
        data["layouts"][layout_name][name] = {
            "left": rect[0],
            "top": rect[1],
            "right": rect[2],
            "bottom": rect[3],
        }

    output_file = save_layout(data, layout_file)

    return layout_name, output_file


def find_window(name, progspec, pid, windows):
    result = None
    expected_cmd = progspec.get("detected_command", progspec.get("command"))
    for w in windows:
        p = w.process

        # First check by tag and PID
        try:
            if p.environ().get(ENV_TAG) == name:
                return w
        except Exception:  # can get an access denied error
            pass

        if p.pid == pid:
            return w

        # High-priority checks are done, so of the remaining, just pick the
        # first match
        if result is not None:
            continue

        # Then try to get the command
        try:
            cmd = w.process.commandline()
        except Exception:  # can get an access denied error
            cmd = w.process.exe()

        # If command matches, look for additional filtering criteria
        if expected_cmd == cmd:

            # Check window title
            title = progspec.get("detected_title")
            if title is not None and title != w.title:
                continue

            # Check window class name
            wclass = progspec.get("detected_class")
            if wclass is not None and wclass != w.wclass:
                continue

            # Matches - but don't return it yet. Keep checking for a match
            # based on the ENV_TAG or pid
            result = w

    return result


def apply_layout(layout, layout_file):
    # Load data
    data = load_layout(layout_file)

    # Track which windows we've moved so far
    used = []

    # Get list of visible windows
    windows = Window.get_visible()

    # Iterate over each program we need to place in the layout
    for program, bounds in data["layouts"][layout].items():

        # Get info about the program itself so we can find its windows
        ps = data["programs"][program]
        w = find_window(program, ps, None, windows)

        # If the window is none, try to create it
        if w is None:
            # Some things like Spotify mysteriously don't work if started
            # by this program. So we allow skipping in this case
            if ps.get("suppress_start"):
                continue

            print(f"Starting {ps['command']}")
            # Stick an ID in the environment running the program so we can
            # find it later. Sometimes this works, sometimes the window runs
            # in another process anyway
            env = os.environ.copy()
            env[ENV_TAG] = program
            proc = subprocess.Popen(ps["command"], env=env)

            # Try to find the window every 10ms for up to 1s
            for _ in range(100):

                # Find new visible windows
                new_windows = [
                    x for x in Window.get_visible()
                    if x not in used
                ]

                # Try to find out new one
                w = find_window(program, ps, proc.pid, new_windows)

                # Found it
                if w is not None:
                    break

                # Didn't find it, wait a few milliseconds and try again
                time.sleep(0.010)

            # In case we can't find it, print an error
            if w is None:
                sys.stderr.write(f"Unable to create window for {program}\n")
                continue

        # Don't let it be moved again
        used.append(w)
        if w in windows:
            windows.remove(w)

        # Move the window
        w.rect = (
            bounds["left"],
            bounds["top"],
            bounds["right"],
            bounds["bottom"],
        )
