import uuid
from typing import Any

BASE62_ALPHABET = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
BASE62_BASE = 62


def uuid_to_base62(uuid_val: str | uuid.UUID) -> str:
    """Convert a standard UUID string or object into a Base62 string."""
    if isinstance(uuid_val, str):
        u = uuid.UUID(uuid_val.strip())
    elif isinstance(uuid_val, uuid.UUID):
        u = uuid_val
    else:
        raise TypeError("uuid_val must be a string or uuid.UUID instance")

    num = u.int
    if num == 0:
        return BASE62_ALPHABET[0]

    digits: list[str] = []
    while num > 0:
        num, rem = divmod(num, BASE62_BASE)
        digits.append(BASE62_ALPHABET[rem])
    return "".join(reversed(digits))


def base62_to_uuid(base62_str: str) -> str:
    """Convert a Base62 string back into a hyphenated UUID string."""
    if not isinstance(base62_str, str) or not base62_str:
        raise ValueError("Base62 string must be a non-empty string")

    num = 0
    for char in base62_str:
        idx = BASE62_ALPHABET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid character '{char}' in Base62 string")
        num = num * BASE62_BASE + idx

    if num >= (1 << 128):
        raise ValueError("Base62 value out of range for 128-bit UUID")

    return str(uuid.UUID(int=num))


def uc_first(string: str) -> str:
    return str(string)[0].upper() + str(string)[1:] if string else ''


def split_date_string(data: str | None) -> str | None:
    return '.'.join(map(str, data.split('T')[0].split('-')[::-1])) \
        if data else ''


def format_date(
        date_from: str | None,
        date_to: str | None) -> str | None:
    if date_from and date_to:
        parts_from = date_from.split('.')
        parts_to = date_to.split('.')
        if len(parts_from) == 3 and len(parts_to) == 3:
            try:
                day_from, month_from, year_from = parts_from
                day_to, month_to, year_to = parts_to
                if (int(day_from) == 1 and int(month_from) == 1
                        and int(day_to) == 31 and int(month_to) == 12):
                    if year_from == year_to:
                        return year_from
                    return f'{year_from} – {year_to}'
            except ValueError:
                pass
    return f'between {date_from} and {date_to}' if date_to else date_from


def flatten_list_and_remove_duplicates(list_: list[Any]) -> list[Any]:
    result: list[Any] = []
    for sublist in list_:
        for item in sublist:
            if item not in result:
                result.append(item)
    return result
