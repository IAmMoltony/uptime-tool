#!/usr/bin/python3

"""
uptime tool
"""

import argparse
import sys
import time
import pathlib
import psutil
import platformdirs

__version__ = "1.0.1"


def get_uptime():
    """
    get the current system uptime
    """
    return time.time() - psutil.boot_time()


def hrtime(seconds):
    """
    convert seconds to a human readable time representation
    """
    intervals = (
        ("weeks", 604800),
        ("days", 86400),
        ("hours", 3600),
        ("minutes", 60),
        ("seconds", 1),
    )

    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip("s")
            result.append(f"{int(value)} {name}")
    return ", ".join(result)


def nonsense(action, flagname):
    """
    tell the user that this flag does not make sense when paired with
    the action and then exit
    """
    print(f"The '{flagname}' flag does not make sense with the '{action}' action")
    sys.exit(1)


def main():
    """
    the main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=["up", "record", "viewrec"], help="the action to preform"
    )
    parser.add_argument(
        "--seconds",
        "-s",
        action="store_true",
        help=(
            "when using the 'up' or 'viewrec' action, output the number of seconds instead of a"
            "formatted time"
        ),
    )
    parser.add_argument(
        "--rec-force",
        "-f",
        action="store_true",
        help=(
            "when using the 'record' action, record the uptime even if the currently recorded"
            "uptime is longer than the current uptime of the system"
        ),
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="be verbose")
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show version information and exit",
    )
    args = parser.parse_args()

    if args.seconds and args.action != "up" and args.action != "viewrec":
        nonsense(args.action, "--seconds")

    if args.rec_force and args.action != "record":
        nonsense(args.action, "--rec-force")

    uptime = get_uptime()
    data_dir_path = pathlib.Path(platformdirs.user_data_dir()) / "moltony_uptool"
    record_file_path = data_dir_path / "record.txt"

    if args.verbose:
        print(
            f"Data directory path: {data_dir_path}\nRecord file path: {record_file_path}"
        )

    if args.action == "up":
        if args.seconds:
            print(uptime)
        else:
            print(hrtime(uptime))
    elif args.action == "record":
        data_dir_path.mkdir(parents=True, exist_ok=True)

        no_exist = False
        if not record_file_path.exists():
            if args.verbose:
                print("Record file does not exist.")
            no_exist = True
            with open(str(record_file_path), "w", encoding="utf-8") as record_file:
                record_file.write(str(uptime))

        if not no_exist:
            record_uptime = 0
            with open(str(record_file_path), "r", encoding="utf-8") as record_file:
                record_uptime = float(record_file.read().strip())
            if uptime > record_uptime:
                if args.verbose:
                    print("Current uptime is longer than the recorded uptime.")
                with open(str(record_file_path), "w", encoding="utf-8") as record_file:
                    record_file.write(str(uptime))
    elif args.action == "viewrec":
        if not record_file_path.exists():
            print(0)
        else:
            with open(str(record_file_path), encoding="utf-8") as record_file:
                record_uptime = int(round(float(record_file.read().strip())))
                if args.seconds:
                    print(record_uptime)
                else:
                    print(hrtime(record_uptime))


if __name__ == "__main__":
    main()
