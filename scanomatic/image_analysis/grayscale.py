import os
import configparser
from collections.abc import Callable
from dataclasses import dataclass

import scanomatic
import scanomatic.io.paths as paths
from scanomatic.io.logger import get_logger

_GRAYSCALE_PATH = paths.Paths().analysis_grayscales
_GRAYSCALE_FALLBACK_PATH = os.path.join(
    os.path.dirname(scanomatic.get_location()),
    "data",
    "config",
    "grayscales.cfg",
)
_GRAYSCALE_CONFIGS = configparser.ConfigParser()
_GRAYSCALE_VALUE_TYPES: dict[str, Callable] = {
    'default': bool,
    'targets': eval,
    'sections': int,
    'width': float,
    'min_width': float,
    'lower_than_half_width': float,
    'higher_than_half_width': float,
    'length': float,
}
_logger = get_logger("Grayscale settings")


@dataclass
class Grayscale:
    default: bool
    width: float
    length: float
    lower_than_half_width: float
    higher_than_half_width: float
    min_width: float
    sections: int
    targets: list[float]


def get_grayscale_names() -> list[str]:
    if _GRAYSCALE_CONFIGS.sections() == []:
        loaded = False
        for candidate in (_GRAYSCALE_PATH, _GRAYSCALE_FALLBACK_PATH):
            if not os.path.isfile(candidate):
                continue
            loaded = bool(_GRAYSCALE_CONFIGS.read(candidate))
            if loaded:
                if candidate != _GRAYSCALE_PATH:
                    _logger.warning(
                        "Using bundled grayscale settings fallback at: "
                        + candidate,
                    )
                break

        if not loaded:
            _logger.critical(
                "Settings for grayscales not found at: "
                + _GRAYSCALE_PATH
                + " or "
                + _GRAYSCALE_FALLBACK_PATH,
            )
    return _GRAYSCALE_CONFIGS.sections()


def get_grayscale(grayscale_name: str) -> Grayscale:
    if grayscale_name in get_grayscale_names():
        return Grayscale(**{
            k: _GRAYSCALE_VALUE_TYPES[k](v) for k, v in
            _GRAYSCALE_CONFIGS.items(grayscale_name)
        })
    else:
        raise Exception("{0} not among known grayscales {1}".format(
            grayscale_name,
            get_grayscale_names(),
        ))
