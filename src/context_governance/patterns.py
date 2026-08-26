from __future__ import annotations

import re
from functools import lru_cache


@lru_cache(maxsize=256)
def _compile_glob(pattern: str) -> re.Pattern[str]:
    pattern = pattern.replace("\\", "/").lstrip("./")
    parts: list[str] = ["^"]
    index = 0
    while index < len(pattern):
        if pattern[index : index + 3] == "**/":
            parts.append("(?:.*/)?")
            index += 3
        elif pattern[index : index + 2] == "**":
            parts.append(".*")
            index += 2
        elif pattern[index] == "*":
            parts.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(pattern[index]))
            index += 1
    parts.append("$")
    return re.compile("".join(parts))


def matches(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(_compile_glob(pattern).match(normalized) for pattern in patterns)
