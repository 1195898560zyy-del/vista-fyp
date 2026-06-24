"""Map aspect-ratio strings to each image provider's orientation parameter."""

from __future__ import annotations


def unsplash_orientation(ratio: str) -> str:
    if ratio.startswith("1:1"):
        return "squarish"
    if ratio in ("4:3", "16:9"):
        return "landscape"
    if ratio in ("3:4", "9:16"):
        return "portrait"
    return ""


def pexels_orientation(ratio: str) -> str:
    if ratio.startswith("1:1"):
        return "square"
    if ratio in ("4:3", "16:9"):
        return "landscape"
    if ratio in ("3:4", "9:16"):
        return "portrait"
    return ""


def pixabay_orientation(ratio: str) -> str:
    if ratio.startswith("1:1"):
        return ""
    if ratio in ("4:3", "16:9"):
        return "horizontal"
    if ratio in ("3:4", "9:16"):
        return "vertical"
    return ""
