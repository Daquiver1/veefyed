"""Skin enums."""

from enum import Enum


class SkinType(str, Enum):
    """Skin type enums."""

    oily = "Oily"
    dry = "Dry"
    combination = "Combination"
    normal = "Normal"


class SkinIssue(str, Enum):
    """Skin issue enums."""

    acne = "Acne"
    hyperpigmentation = "Hyperpigmentation"
    wrinkles = "Wrinkles"
    redness = "Redness"
