"""Geometric pattern generation — powered by Python's math module.

Every pattern is computed server-side using trigonometry, then sent
as SVG path data to the React client. This is the kind of computation
that Python handles beautifully and JavaScript doesn't have in its
standard library at the same level.
"""

from __future__ import annotations

import colorsys
import math
from typing import Sequence


# ── SVG Path Helpers ────────────────────────────────────────────


def _points_to_path(points: Sequence[tuple[float, float]], close: bool = True) -> str:
    if not points:
        return ""
    parts = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
    for x, y in points[1:]:
        parts.append(f"L {x:.2f} {y:.2f}")
    if close:
        parts.append("Z")
    return " ".join(parts)


def _hue_to_hex(hue: float, saturation: float = 0.75, lightness: float = 0.6) -> str:
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"


# ── Pattern Algorithms ──────────────────────────────────────────


def spirograph(
    R: float = 100,
    r: float = 63,
    d: float = 80,
    steps: int = 4000,
    cx: float = 200,
    cy: float = 200,
) -> dict:
    """Hypotrochoid curve — the classic Spirograph toy, computed with trig."""
    gcd = math.gcd(int(R), int(r))
    revolutions = int(r / gcd)
    t_max = 2 * math.pi * revolutions
    points = []
    for i in range(steps + 1):
        t = t_max * i / steps
        x = cx + (R - r) * math.cos(t) + d * math.cos((R - r) * t / r)
        y = cy + (R - r) * math.sin(t) - d * math.sin((R - r) * t / r)
        points.append((x, y))

    return {
        "paths": [{"d": _points_to_path(points, close=False), "color": "#A78BFA"}],
        "type": "spirograph",
        "params": {"R": R, "r": r, "d": d},
    }


def rose_curve(
    k: float = 5,
    amplitude: float = 150,
    steps: int = 2000,
    cx: float = 200,
    cy: float = 200,
) -> dict:
    """Mathematical rose curve: r = cos(k*theta)."""
    # Need more revolutions for non-integer k
    revolutions = 2 if k == int(k) and int(k) % 2 == 1 else 4
    points = []
    for i in range(steps + 1):
        t = revolutions * math.pi * i / steps
        r = amplitude * math.cos(k * t)
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t)
        points.append((x, y))

    return {
        "paths": [{"d": _points_to_path(points, close=False), "color": "#F472B6"}],
        "type": "rose",
        "params": {"k": k, "amplitude": amplitude},
    }


def mandala(
    petals: int = 12,
    layers: int = 4,
    base_radius: float = 40,
    cx: float = 200,
    cy: float = 200,
) -> dict:
    """Radially symmetric mandala pattern."""
    paths = []
    for layer in range(1, layers + 1):
        radius = base_radius * layer
        hue = (layer - 1) / layers
        color = _hue_to_hex(hue, saturation=0.7, lightness=0.65)

        for i in range(petals):
            angle = 2 * math.pi * i / petals
            next_angle = 2 * math.pi * (i + 0.5) / petals

            # Petal shape: two arcs meeting at a tip
            tip_x = cx + radius * 1.3 * math.cos(angle)
            tip_y = cy + radius * 1.3 * math.sin(angle)
            left_x = cx + radius * 0.5 * math.cos(angle - 0.3)
            left_y = cy + radius * 0.5 * math.sin(angle - 0.3)
            right_x = cx + radius * 0.5 * math.cos(angle + 0.3)
            right_y = cy + radius * 0.5 * math.sin(angle + 0.3)

            d = (
                f"M {left_x:.2f} {left_y:.2f} "
                f"Q {cx + radius * 0.9 * math.cos(angle - 0.15):.2f} "
                f"{cy + radius * 0.9 * math.sin(angle - 0.15):.2f} "
                f"{tip_x:.2f} {tip_y:.2f} "
                f"Q {cx + radius * 0.9 * math.cos(angle + 0.15):.2f} "
                f"{cy + radius * 0.9 * math.sin(angle + 0.15):.2f} "
                f"{right_x:.2f} {right_y:.2f} Z"
            )
            paths.append({"d": d, "color": color, "opacity": 0.7})

    return {
        "paths": paths,
        "type": "mandala",
        "params": {"petals": petals, "layers": layers, "base_radius": base_radius},
    }


def star_polygon(
    points: int = 7,
    outer_radius: float = 160,
    inner_radius: float = 70,
    cx: float = 200,
    cy: float = 200,
) -> dict:
    """Star polygon with alternating inner/outer vertices."""
    vertices = []
    for i in range(points * 2):
        angle = math.pi * i / points - math.pi / 2
        r = outer_radius if i % 2 == 0 else inner_radius
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        vertices.append((x, y))

    return {
        "paths": [{"d": _points_to_path(vertices), "color": "#FBBF24", "opacity": 0.85}],
        "type": "star",
        "params": {"points": points, "outer_radius": outer_radius, "inner_radius": inner_radius},
    }


def lissajous(
    a: int = 3,
    b: int = 4,
    delta: float = math.pi / 2,
    amplitude: float = 150,
    steps: int = 2000,
    cx: float = 200,
    cy: float = 200,
) -> dict:
    """Lissajous curve — two perpendicular oscillations."""
    points = []
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        x = cx + amplitude * math.sin(a * t + delta)
        y = cy + amplitude * math.sin(b * t)
        points.append((x, y))

    return {
        "paths": [{"d": _points_to_path(points, close=False), "color": "#34D399"}],
        "type": "lissajous",
        "params": {"a": a, "b": b, "delta": round(delta, 4), "amplitude": amplitude},
    }


def wave_interference(
    waves: int = 5,
    amplitude: float = 60,
    frequency_base: float = 3,
    width: float = 380,
    cx: float = 10,
    cy: float = 200,
    steps: int = 500,
) -> dict:
    """Stacked sine waves with increasing frequency."""
    paths = []
    for w in range(waves):
        freq = frequency_base + w * 0.7
        offset = (w - waves / 2) * 25
        hue = w / waves
        color = _hue_to_hex(hue, saturation=0.8, lightness=0.6)

        points = []
        for i in range(steps + 1):
            t = i / steps
            x = cx + t * width
            y = cy + offset + amplitude * math.sin(freq * 2 * math.pi * t)
            points.append((x, y))

        paths.append({"d": _points_to_path(points, close=False), "color": color})

    return {
        "paths": paths,
        "type": "waves",
        "params": {"waves": waves, "amplitude": amplitude, "frequency_base": frequency_base},
    }


# ── Pattern Registry ────────────────────────────────────────────


GENERATORS = {
    "spirograph": spirograph,
    "rose": rose_curve,
    "mandala": mandala,
    "star": star_polygon,
    "lissajous": lissajous,
    "waves": wave_interference,
}

PATTERN_INFO = {
    "spirograph": {"name": "Spirograph", "desc": "Hypotrochoid curves from nested circular motion", "icon": "○"},
    "rose": {"name": "Rose Curve", "desc": "Polar curves defined by r = cos(k\u00b7\u03b8)", "icon": "✿"},
    "mandala": {"name": "Mandala", "desc": "Radially symmetric petal patterns", "icon": "✦"},
    "star": {"name": "Star Polygon", "desc": "Regular star with alternating vertices", "icon": "★"},
    "lissajous": {"name": "Lissajous", "desc": "Two perpendicular harmonic oscillations", "icon": "∞"},
    "waves": {"name": "Wave Interference", "desc": "Stacked sine waves at varying frequencies", "icon": "〰"},
}


def generate_pattern(pattern_type: str, **kwargs) -> dict:
    generator = GENERATORS.get(pattern_type)
    if not generator:
        return {"paths": [], "type": pattern_type, "params": {}}
    return generator(**kwargs)


# ── Pre-computed Gallery ────────────────────────────────────────


GALLERY = [
    {"id": "classic-spirograph", "type": "spirograph", "name": "Classic Spirograph",
     "params": {"R": 100, "r": 63, "d": 80}},
    {"id": "tight-spirograph", "type": "spirograph", "name": "Tight Spiral",
     "params": {"R": 100, "r": 37, "d": 50}},
    {"id": "five-petal-rose", "type": "rose", "name": "Five-Petal Rose",
     "params": {"k": 5, "amplitude": 150}},
    {"id": "eight-petal-rose", "type": "rose", "name": "Eight-Petal Rose",
     "params": {"k": 4, "amplitude": 150}},
    {"id": "sun-mandala", "type": "mandala", "name": "Sun Mandala",
     "params": {"petals": 12, "layers": 4, "base_radius": 40}},
    {"id": "lotus-mandala", "type": "mandala", "name": "Lotus Mandala",
     "params": {"petals": 8, "layers": 5, "base_radius": 30}},
    {"id": "seven-star", "type": "star", "name": "Seven-Point Star",
     "params": {"points": 7, "outer_radius": 160, "inner_radius": 70}},
    {"id": "twelve-star", "type": "star", "name": "Twelve-Point Star",
     "params": {"points": 12, "outer_radius": 160, "inner_radius": 100}},
    {"id": "figure-eight", "type": "lissajous", "name": "Figure Eight",
     "params": {"a": 3, "b": 4, "delta": 1.5708, "amplitude": 150}},
    {"id": "knot", "type": "lissajous", "name": "Celtic Knot",
     "params": {"a": 5, "b": 6, "delta": 0.7854, "amplitude": 150}},
    {"id": "ocean-waves", "type": "waves", "name": "Ocean Waves",
     "params": {"waves": 5, "amplitude": 60, "frequency_base": 3}},
    {"id": "radio-waves", "type": "waves", "name": "Radio Waves",
     "params": {"waves": 7, "amplitude": 40, "frequency_base": 2}},
]


def get_gallery() -> list[dict]:
    """Return gallery items with pre-computed SVG data."""
    items = []
    for entry in GALLERY:
        pattern = generate_pattern(entry["type"], **entry["params"])
        items.append({
            **entry,
            "paths": pattern["paths"],
            "info": PATTERN_INFO.get(entry["type"], {}),
        })
    return items


def get_gallery_item(item_id: str) -> dict | None:
    for entry in GALLERY:
        if entry["id"] == item_id:
            pattern = generate_pattern(entry["type"], **entry["params"])
            return {
                **entry,
                "paths": pattern["paths"],
                "info": PATTERN_INFO.get(entry["type"], {}),
            }
    return None
