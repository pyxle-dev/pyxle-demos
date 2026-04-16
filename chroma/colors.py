"""Color science utilities — powered by Python's colorsys.

This module demonstrates why Python is a natural fit for server-side
web development: the standard library has tools for color manipulation,
math, and data processing that JavaScript simply doesn't ship with.
"""

from __future__ import annotations

import colorsys
import math
import random


# ── Conversion ──────────────────────────────────────────────────


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)


def hsl_to_hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return rgb_to_hex(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


# ── Color Analysis ──────────────────────────────────────────────


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.1 relative luminance."""
    r, g, b = hex_to_rgb(hex_color)

    def linearize(c: int) -> float:
        v = c / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """WCAG contrast ratio between two colors (1.0–21.0)."""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def is_light(hex_color: str) -> bool:
    """True if the color is visually light (text should be dark)."""
    return relative_luminance(hex_color) > 0.179


def describe_color(hex_color: str) -> str:
    """Human-readable color description from HSL analysis."""
    h, s, l = hex_to_hsl(hex_color)

    if s < 10:
        if l > 90:
            return "White"
        if l < 10:
            return "Black"
        return "Gray"

    hue_names = [
        (15, "Red"), (45, "Orange"), (65, "Yellow"), (150, "Green"),
        (195, "Cyan"), (255, "Blue"), (285, "Purple"), (330, "Pink"),
        (361, "Red"),
    ]
    hue_name = "Red"
    for threshold, name in hue_names:
        if h < threshold:
            hue_name = name
            break

    prefix = ""
    if l > 75:
        prefix = "Light "
    elif l < 30:
        prefix = "Dark "

    if s < 40:
        prefix = "Muted " + prefix.strip() + " " if prefix else "Muted "

    return f"{prefix}{hue_name}".strip()


# ── Harmony Algorithms ──────────────────────────────────────────


def _rotate_hue(h: float, degrees: float) -> float:
    return (h + degrees) % 360


def generate_complementary(base_hex: str) -> list[str]:
    h, s, l = hex_to_hsl(base_hex)
    return [
        base_hex,
        hsl_to_hex(h, max(s - 15, 10), min(l + 20, 90)),
        hsl_to_hex(h, s, l),
        hsl_to_hex(_rotate_hue(h, 180), max(s - 15, 10), min(l + 20, 90)),
        hsl_to_hex(_rotate_hue(h, 180), s, l),
    ]


def generate_analogous(base_hex: str) -> list[str]:
    h, s, l = hex_to_hsl(base_hex)
    return [
        hsl_to_hex(_rotate_hue(h, -30), s, l),
        hsl_to_hex(_rotate_hue(h, -15), max(s - 10, 10), min(l + 10, 90)),
        base_hex,
        hsl_to_hex(_rotate_hue(h, 15), max(s - 10, 10), min(l + 10, 90)),
        hsl_to_hex(_rotate_hue(h, 30), s, l),
    ]


def generate_triadic(base_hex: str) -> list[str]:
    h, s, l = hex_to_hsl(base_hex)
    return [
        base_hex,
        hsl_to_hex(h, max(s - 20, 10), min(l + 25, 90)),
        hsl_to_hex(_rotate_hue(h, 120), s, l),
        hsl_to_hex(_rotate_hue(h, 120), max(s - 20, 10), min(l + 25, 90)),
        hsl_to_hex(_rotate_hue(h, 240), s, l),
    ]


def generate_split_complementary(base_hex: str) -> list[str]:
    h, s, l = hex_to_hsl(base_hex)
    return [
        base_hex,
        hsl_to_hex(h, max(s - 15, 10), min(l + 15, 90)),
        hsl_to_hex(_rotate_hue(h, 150), s, l),
        hsl_to_hex(_rotate_hue(h, 180), max(s - 10, 10), min(l + 20, 90)),
        hsl_to_hex(_rotate_hue(h, 210), s, l),
    ]


def generate_monochromatic(base_hex: str) -> list[str]:
    h, s, l = hex_to_hsl(base_hex)
    return [
        hsl_to_hex(h, s, max(l - 30, 10)),
        hsl_to_hex(h, s, max(l - 15, 15)),
        base_hex,
        hsl_to_hex(h, max(s - 15, 10), min(l + 15, 85)),
        hsl_to_hex(h, max(s - 25, 10), min(l + 30, 92)),
    ]


HARMONY_GENERATORS = {
    "complementary": generate_complementary,
    "analogous": generate_analogous,
    "triadic": generate_triadic,
    "split-complementary": generate_split_complementary,
    "monochromatic": generate_monochromatic,
}


def generate_palette(base_hex: str, harmony: str = "analogous") -> list[str]:
    generator = HARMONY_GENERATORS.get(harmony, generate_analogous)
    return generator(base_hex)


def random_palette() -> tuple[str, list[str], str]:
    """Generate a random palette. Returns (base_hex, colors, harmony)."""
    h = random.randint(0, 359)
    s = random.randint(50, 95)
    l = random.randint(35, 65)
    base = hsl_to_hex(h, s, l)
    harmony = random.choice(list(HARMONY_GENERATORS.keys()))
    colors = generate_palette(base, harmony)
    return base, colors, harmony


def analyze_color(hex_color: str) -> dict:
    """Full analysis of a single color."""
    h, s, l = hex_to_hsl(hex_color)
    r, g, b = hex_to_rgb(hex_color)
    return {
        "hex": hex_color.upper(),
        "rgb": {"r": r, "g": g, "b": b},
        "hsl": {"h": h, "s": s, "l": l},
        "name": describe_color(hex_color),
        "luminance": round(relative_luminance(hex_color), 4),
        "isLight": is_light(hex_color),
        "contrastOnWhite": contrast_ratio(hex_color, "#FFFFFF"),
        "contrastOnBlack": contrast_ratio(hex_color, "#000000"),
    }


def analyze_palette(colors: list[str]) -> list[dict]:
    """Analyze every color in a palette."""
    return [analyze_color(c) for c in colors]
