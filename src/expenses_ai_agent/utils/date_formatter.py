from datetime import datetime
from zoneinfo import ZoneInfo


def format_datetime(datetime_str: str, timezone_str: str | None = None) -> str:
    dt = datetime.fromisoformat(datetime_str)
    if timezone_str is not None:
        dt = dt.astimezone(ZoneInfo(timezone_str))

    return dt.strftime("%A, %d %B %Y %I:%M%p")
