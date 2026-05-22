# TODO dedupe this file with other implementations elsewhere
from __future__ import annotations

import random
import re
import string
from typing import Union

_ID_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
_NON_ALPHANUM_RE = re.compile(r"[^a-zA-Z0-9-]+")
_REPEATED_DASH_RE = re.compile(r"-{2,}")
_NO_SPECIAL_NUMBERS_TO_TEXT_MAP = {
    0: "zero",
    1: "one",
}
_NUMBERS_TO_TEXT_MAP = {
    0: "no",
    1: "a",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}


def make_id() -> str:
    return "".join(random.choices(_ID_CHARS, k=12))


def trim_slug_str(s: str, length: int, max_under: Union[int, None] = None) -> str:
    max_under = max_under if max_under is not None else length // 6
    if len(s) <= length:
        return s
    for i in range(1, max_under + 1):
        if s[length - i] == "-":
            return s[: length - i]
    return s[:length]


def slugify_str(s: str, lower: bool = False, trim_kwargs: Union[dict, None] = None) -> str:
    lowered = s.lower() if lower else s
    formatted = _NON_ALPHANUM_RE.sub("-", lowered.replace("'", ""))
    formatted = _REPEATED_DASH_RE.sub("-", formatted).strip("-")
    return trim_slug_str(formatted, **trim_kwargs) if trim_kwargs is not None else formatted


def get_number_text(n: int, /, *, definite: bool = False, no_special: bool = False) -> str:
    if definite and n == 1:
        return "the"
    no_special_text = _NO_SPECIAL_NUMBERS_TO_TEXT_MAP.get(n)
    if no_special and no_special_text is not None:
        return no_special_text
    return _NUMBERS_TO_TEXT_MAP.get(n, str(n))


def get_item_count_text(
    n: int,
    singular: str,
    /,
    *,
    definite: bool = False,
    no_special: bool = False,
    unusual_plural: str | None = None,
    as_text: bool = True,
) -> str:
    plural = unusual_plural if unusual_plural is not None else f"{singular}s"
    number_text = get_number_text(n, definite=definite, no_special=no_special) if as_text else n
    return f"{number_text} {singular if n == 1 else plural}"
