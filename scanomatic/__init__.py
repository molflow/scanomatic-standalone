"""Part of analysis work-flow that holds a grid arrays"""
import os
from importlib.metadata import PackageNotFoundError, version as pkg_version

__author__ = "Martin Zackrisson"
__copyright__ = "Swedish copyright laws apply"
__credits__ = ["Martin Zackrisson", "Mats Kvarnstroem", "Andreas Skyman", ""]
__license__ = "GPL v3.0"
__version__ = "3.0.0"
__maintainer__ = "Martin Zackrisson"
__status__ = "Development"

__branch = "main"
_distribution_name = "scanomatic-standalone"


def get_version() -> str:
    try:
        return pkg_version(_distribution_name)
    except PackageNotFoundError:
        return __version__


def get_branch() -> str:
    return __branch


def get_location() -> str:
    return os.path.dirname(__file__)
