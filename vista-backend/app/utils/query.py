"""Query-string parsing helpers for routers."""


def parse_bool_flag(value: str | None) -> bool:
    """Parse `?random=1` or `?random=true` style flags."""
    return value in ("1", "true", "True")
