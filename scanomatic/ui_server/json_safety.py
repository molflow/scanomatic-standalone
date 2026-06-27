import math
from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Any

from flask.json import JSONEncoder


def sanitize_json_numbers(value: Any) -> Any:
    if value is None:
        return None

    if hasattr(value, "item") and callable(getattr(value, "item")):
        # Unwrap numpy scalar types to native Python values.
        try:
            return sanitize_json_numbers(value.item())
        except Exception:
            pass

    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value if math.isfinite(value) else None

    if isinstance(value, Enum):
        return value.name

    if hasattr(value, "tolist") and callable(getattr(value, "tolist")):
        return sanitize_json_numbers(value.tolist())

    if isinstance(value, Mapping):
        return {
            sanitize_json_numbers(k): sanitize_json_numbers(v)
            for k, v in value.items()
        }

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [sanitize_json_numbers(v) for v in value]

    return value


class SafeJSONEncoder(JSONEncoder):
    def encode(self, o: Any) -> str:
        return super().encode(sanitize_json_numbers(o))

    def iterencode(self, o: Any, _one_shot: bool = False):
        return super().iterencode(sanitize_json_numbers(o), _one_shot)
