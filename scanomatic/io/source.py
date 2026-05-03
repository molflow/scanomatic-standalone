import json
import os
from subprocess import PIPE, Popen, call
from typing import Any, Optional

import requests

from scanomatic import get_version
from scanomatic.io.logger import get_logger

from .paths import Paths

_logger = get_logger("Source Checker")


def _read_source_version(base_path) -> Optional[str]:
    try:
        with open(os.path.join(base_path, "scanomatic", "__init__.py")) as fh:
            for line in fh:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip()

    except (TypeError, IOError, IndexError):
        pass

    return None


def _load_source_information() -> dict[str, Any]:
    try:
        with open(Paths().source_location_file, 'r') as fh:
            return json.load(fh)
    except ValueError:
        try:
            with open(Paths().source_location_file, 'r') as fh:
                return {'location': fh.read(), 'branch': None}
        except IOError:
            pass
    except IOError:
        pass

    return {'location': None, 'branch': None}


def get_source_information(test_info=False, force_location=None):

    data = _load_source_information()

    if force_location:
        data['location'] = force_location

    data['version'] = _read_source_version(
        data['location'] if force_location is None else force_location
    )

    if test_info:
        if not has_source(data['location']):
            data['location'] = None
        if (
            not data['branch']
            and data['location']
            and is_under_git_control(data['location'])
        ):
            data['branch'] = get_active_branch(data['location'])

    return data


def has_source(path=None) -> bool:
    if path is None:
        path = get_source_information()['location']

    if path:
        return os.path.isdir(path)
    else:
        return False


def _git_root_navigator(f):

    def _wrapped(path):

        directory = os.getcwd()
        os.chdir(path)
        ret = f(path)
        os.chdir(directory)
        return ret

    return _wrapped


def _manual_git_branch_test() -> Optional[str]:
    try:
        with open(os.path.join(".git", "HEAD")) as fh:
            return fh.readline().split("/")[-1]
    except (IOError, IndexError, TypeError):
        return None


@_git_root_navigator
def is_under_git_control(path) -> bool:
    try:
        retcode = call(['git', 'rev-parse'])
    except OSError:
        retcode = -1
    return retcode == 0


@_git_root_navigator
def get_active_branch(path) -> Optional[str]:
    branch = None
    try:
        p = Popen(['git', 'branch', '--list'], stdout=PIPE)
        o, _ = p.communicate()
    except OSError:
        branch = _manual_git_branch_test()
    else:
        branch = "master"
        for line in o.split(b"\n"):
            if line.startswith(b"*"):
                branch = line.strip(b"* ").decode()
                break
    return branch


def git_version(
    git_repo='https://raw.githubusercontent.com/local-minimum/scanomatic',
    branch='master',
    suffix='scanomatic/__init__.py',
) -> str:
    global _logger
    uri = "/".join((git_repo, branch, suffix))
    for line in requests.get(uri).text.split("\n"):
        if line.startswith("__version__"):
            return line.split("=")[-1].strip('" ')

    _logger.warning(
        f"Could not access any valid version information from uri {uri}",
    )
    return ""


def parse_version(version: Optional[str] = get_version()) -> tuple[int, ...]:
    if version is None:
        return 0, 0

    return tuple(
        int("".join(c for c in v if c in "0123456789"))
        for v in version.split(".")
        if any((c in "0123456789" and c) for c in v)
    )


def highest_version(v1, v2):
    global _logger
    comparable = min(len(v) for v in (v1, v2))
    for i in range(comparable):
        if v1[i] == v2[i]:
            continue
        elif v1[i] > v2[i]:
            return v1
        else:
            return v2

    if len(v1) >= len(v2):
        return v1
    elif len(v2) > len(v1):
        return v2

    _logger.warning("None of the versions is a version!")
    return None


def next_subversion(branch, current=None) -> tuple[int, ...]:
    online_version = git_version(branch=branch)
    version = parse_version(
        highest_version(
            online_version,
            current if current is not None else get_version(),
        ),
    )
    return increase_version(version)


def increase_version(version: tuple[int, ...]) -> tuple[int, ...]:
    new_version = list(version)
    if len(new_version) == 2:
        new_version += [1]
    elif len(version) == 1:
        new_version += [0, 11]
    else:
        new_version[-1] += 1

    return tuple(new_version)


def get_minor_release_version(
    current_version: tuple[int, ...],
) -> tuple[int, ...]:
    version = list(current_version[:2])
    if len(version) == 0:
        return (0, 1)
    elif len(version) == 1:
        return tuple(version + [1])
    else:
        version[-1] += 1
        return tuple(version)


def get_major_release_version(
    current_version: tuple[int, ...],
) -> tuple[int]:
    version = current_version[:1]
    if len(version) > 0:
        return (version[0] + 1,)
    else:
        return (1,)
