from typing import Optional, Any


def uc_first(string: str) -> str:
    return str(string)[0].upper() + str(string)[1:] if string else ''


def split_date_string(data: Optional[str]) -> Optional[str]:
    return '.'.join(map(str, data.split('T')[0].split('-')[::-1])) \
        if data else ''


def format_date(
        date_from: Optional[str],
        date_to: Optional[str]) -> Optional[str]:
    if date_from and date_to:
        parts_from = date_from.split('.')
        parts_to = date_to.split('.')
        if len(parts_from) == 3 and len(parts_to) == 3:
            try:
                day_from, month_from, year_from = parts_from
                day_to, month_to, year_to = parts_to
                if (int(day_from) == 1 and int(month_from) == 1 and
                        int(day_to) == 31 and int(month_to) == 12):
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
