from datetime import date, timedelta


def parse_iso_date(text: str) -> str:
    import re

    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    return match.group(1) if match else ""


def format_date_offset(days: int) -> str:
    d = date.today() + timedelta(days=days)
    return d.isoformat()
