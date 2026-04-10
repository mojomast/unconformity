"""Detector collection."""

from .angular import detect_angular
from .buttress import detect_buttress
from .disconformity import detect_disconformity
from .nonconformity import detect_nonconformity
from .paraconformity import detect_paraconformity

__all__ = [
    "detect_angular",
    "detect_buttress",
    "detect_disconformity",
    "detect_nonconformity",
    "detect_paraconformity",
]
