import os
import sys
from argparse import ArgumentParser
from time import sleep

import psutil
import setproctitle

import scanomatic.server.interface_builder as interface_builder
from scanomatic.io.logger import get_logger
from scanomatic.ui_server import ui_server

_UI_LOGGER = get_logger("Scan-o-Matic launcher")
_SERVER_LOGGER = get_logger("Scan-o-Matic server launcher")


def _get_proc_name(proc):
    try:
        return proc.name()
    except TypeError:
        return proc.name


def scan_o_matic_main() -> None:
    parser = ArgumentParser(description="""Scan-o-Matic""")

    parser.add_argument(
        "--kill",
        default=False,
        dest="kill",
        action="store_true",
        help=(
            "Kill any running Scan-o-Matic server or UI Server before "
            "launching"
        ),
    )

    parser.add_argument(
        "--no-launch",
        default=False,
        dest="no_launch",
        action="store_true",
        help="Scan-o-Matic will not be launched (usable with --kill).",
    )

    parser.add_argument(
        "--port",
        type=int,
        dest="port",
        help="Manual override of default port",
    )

    parser.add_argument(
        "--host",
        type=str,
        dest="host",
        help="Manually setting host address of server",
    )

    parser.add_argument(
        "--no-browser",
        dest="browser",
        default=True,
        action="store_false",
        help="Open url to Scan-o-Matic in new tab (default True)",
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        default=False,
        action="store_true",
        help=(
            "Run in debug-mode. This makes the app vulnerable and insecure "
            "and should be used behind firewall and never on a production "
            "system that has real data in it."
        ),
    )

    parser.add_argument(
        "--service-relaunch",
        dest="relaunch",
        default=False,
        action="store_true",
        help=(
            "Shortcut for `--kill --no-browser` and ensuring `--no-launch` "
            "is not set."
        ),
    )

    args = parser.parse_args()

    if args.relaunch:
        _UI_LOGGER.info("Invoking `--kill --no-launch --no_browser`")
        args.kill = True
        args.no_launch = False
        args.browser = False

    if args.kill:
        procs = (
            p
            for p in psutil.process_iter()
            if _get_proc_name(p) in ["SoM Server", "SoM UI Server"]
        )
        for proc in procs:
            _UI_LOGGER.info(
                "Killing process '%s' with pid %s",
                _get_proc_name(proc),
                proc.pid,
            )
            proc.kill()

    if args.no_launch:
        _UI_LOGGER.info("Not launching...Done!")
        sys.exit()

    setproctitle.setproctitle("SoM UI Server")
    _UI_LOGGER.info("Waiting 1 second before launch... please hold.")
    sleep(1)
    _UI_LOGGER.info("Launching...")
    ui_server.launch(
        args.host,
        args.port,
        args.debug,
        open_browser_url=args.browser,
    )


def scan_o_matic_server_main() -> None:
    _SERVER_LOGGER.info("Launching RPC Server")
    setproctitle.setproctitle("SoM Server")
    basename = os.path.basename(sys.argv[0])[:15]

    procs = (
        psutil.get_process_list
        if hasattr(psutil, "get_process_list")
        else psutil.process_iter
    )

    for process in procs():
        try:
            if isinstance(process.name, str):
                name = process.name
            else:
                name = process.name()

            if isinstance(process.pid, int):
                pid = process.pid
            else:
                pid = process.pid()

            if name.startswith(basename) and os.getpid() != pid:
                _SERVER_LOGGER.critical(
                    "There is already a Scan-o-Matic server running, "
                    "request refused!",
                )
                sys.exit(9)

        except psutil.NoSuchProcess:
            pass

    _SERVER_LOGGER.info("Building interface")
    interface_builder.InterfaceBuilder()


if __name__ == "__main__":
    scan_o_matic_main()
