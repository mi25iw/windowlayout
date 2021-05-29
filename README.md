# windowlayout

Minimalist package to manage a layout of windows in Python.
Currently, only windows is supported, and I've only used this on Windows 10.

## Background

I have a lot of monitor space and got tired of rearranging my windows manually.
I quickly cobbled together a tool to let me save and restore window arrangements.
You are now reading about this tool.

## Usage

1. Install with pip (`pip install windowlayout`) on Python 3.6 or greater
1. Open your favorite programs and arrange them to your liking on your monitor
1. Save the current layout as a starting point: `python -m windowlayout save`
1. **Edit `~/.windowlayout.json` to tweak it (see below)**
1. When you want this window layout again, run `python -m windowlayout apply`
1. For alternate layouts, specify a name after `save` or `apply`.

## Configuration

By default, layout data is stored in `~/.windowlayout.json`.
The `-f`/`--layout-file` argument can be used to specify another file.
The layout data has two main sections: `programs`, and `layouts`.

**NOTE:** Usually you will have all sorts of vauge background windows you can't identify after running save.
You should remove anything from your layout that you don't recognize.
Also, if you don't need the title or class fields to distinguish between programs, don't use them.

### Program Configuration

The `"programs"` json object specifies named programs that you may use in layouts.
They have the following fields

* `command`: The command line string to run to start the program (required)
* `detected_command`: The command line string to look for to find an already running window of this program (if not specified, `command` is used)
* `detected_title`: If specified, the window title must match this string when finding an already running instance of the window
* `detected_class`: If specified, the window class must match this string when finding an already running instance of the window
* `suppress_start`: If true (default is false if unspecified), do not attempt to start the program if a pre-existing window is not found

The `detected_command` field exists because sometimes you need run one command to start a program but the process owning the window doesn't have the same command.
The `detected_title` is useful when a process may have multiple windows but only one is the "real" one.
The `suppress_start` flag was added because when I start Spotify while this program is running, the Spotify UI freezes and I haven't debugged why.

### Layout Configuration

The `"layouts"` json object contains definitions for the available layouts you can apply.
The default layout when no layout is specified is named `"default"`.

Each layout is a json object where the property names reference a named program in the `"programs"` object.
If you want to have multiple windows with the same program, you need multiple entries in the `"programs"` object.
Normally you need this anyway so you can specify command-line arguments for the different windows.

The property value is another json object specifying the left, top, bottom, and right coordinates of the window.
These coordinates are in pixels and may be negative depending on the monitor layout.
The top / left coordinates are 0, and values increase towards bottom / right.

The simplest way to define a layout is to arrange the windows roughly how you want them and save the layout.
Then prune the list of programs down to what you care about and remove restrictions you don't need (like `detected_title` being the empty string).

If you want to create a second layout and have already crafted an initial one, consider using the `-f` argument to specify an alternate file.
That way, all the stuff you removed the first time doesn't get added back when it is detected again.
