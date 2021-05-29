import argparse
import sys

from .switcher import (
    DEFAULT_LAYOUT,
    add_current_layout,
    apply_layout,
)


def cmd_save(layout_name, layout_file):
    name, filename = add_current_layout(layout_name, layout_file)
    print(f"Saving layout {name} to {filename}")
    return 0


def cmd_apply(layout_name, layout_file):
    try:
        apply_layout(layout_name, layout_file)
    except FileNotFoundError:
        print("Layout file not found", file=sys.stderr)
        return 1
    except KeyError:
        print("Specified layout not found", file=sys.stderr)
        return 2

    return 0


def main(args):
    parser = argparse.ArgumentParser(
        description="The description of the script",
    )

    parser.add_argument(
        "-f",
        "--layout-file",
        help="Path to layout file to use",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    save = subparsers.add_parser(
        "save",
        help="Read the current layout and save to a file",
    )
    save.set_defaults(func=cmd_save)

    save.add_argument(
        "layout_name",
        nargs="?",
        default=None,
        help="Name of layout to save as",
    )

    apply = subparsers.add_parser(
        "apply",
        help="Apply the layout",
    )
    apply.set_defaults(func=cmd_apply)

    apply.add_argument(
        "layout_name",
        nargs="?",
        default=DEFAULT_LAYOUT,
        help="Name of layout to apply",
    )

    args = parser.parse_args(args)
    func = args.func
    kwargs = vars(args)
    del kwargs["func"]
    del kwargs["command"]
    return func(**kwargs)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
