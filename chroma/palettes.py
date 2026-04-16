"""Curated color palettes for the Chroma demo."""

from __future__ import annotations

PALETTES: list[dict] = [
    # ── Warm ────────────────────────────────────
    {"id": "sunset-glow", "name": "Sunset Glow", "mood": "warm",
     "colors": ["#FF6B6B", "#FF8E72", "#FFA45B", "#FFD166", "#F4E285"]},
    {"id": "autumn-harvest", "name": "Autumn Harvest", "mood": "warm",
     "colors": ["#D4A373", "#E6B87D", "#FAEDCD", "#CCD5AE", "#A68A64"]},
    {"id": "coral-reef", "name": "Coral Reef", "mood": "warm",
     "colors": ["#FF6B6B", "#EE9B9B", "#FFB4A2", "#E5989B", "#B5838D"]},

    # ── Cool ────────────────────────────────────
    {"id": "ocean-depths", "name": "Ocean Depths", "mood": "cool",
     "colors": ["#023E8A", "#0077B6", "#0096C7", "#00B4D8", "#48CAE4"]},
    {"id": "arctic-frost", "name": "Arctic Frost", "mood": "cool",
     "colors": ["#CAF0F8", "#ADE8F4", "#90E0EF", "#48CAE4", "#00B4D8"]},
    {"id": "lavender-dreams", "name": "Lavender Dreams", "mood": "cool",
     "colors": ["#E7C6FF", "#C8B6FF", "#B8C0FF", "#BBD0FF", "#D7E3FC"]},

    # ── Pastel ──────────────────────────────────
    {"id": "cotton-candy", "name": "Cotton Candy", "mood": "pastel",
     "colors": ["#FFB5E8", "#FF9CEE", "#B28DFF", "#97A2FF", "#AFF8DB"]},
    {"id": "spring-garden", "name": "Spring Garden", "mood": "pastel",
     "colors": ["#C1FBA4", "#B8F3B8", "#D0F4DE", "#FCEFB4", "#FFC9B5"]},
    {"id": "blush", "name": "Blush", "mood": "pastel",
     "colors": ["#FFCCD5", "#FFB3C6", "#FF8FAB", "#FB6F92", "#FF477E"]},

    # ── Vibrant ─────────────────────────────────
    {"id": "neon-nights", "name": "Neon Nights", "mood": "vibrant",
     "colors": ["#FF006E", "#8338EC", "#3A86FF", "#FFBE0B", "#FB5607"]},
    {"id": "electric", "name": "Electric", "mood": "vibrant",
     "colors": ["#7400B8", "#6930C3", "#5390D9", "#48BFE3", "#56CFE1"]},
    {"id": "pop-art", "name": "Pop Art", "mood": "vibrant",
     "colors": ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93"]},

    # ── Earth ───────────────────────────────────
    {"id": "forest-floor", "name": "Forest Floor", "mood": "earth",
     "colors": ["#606C38", "#283618", "#FEFAE0", "#DDA15E", "#BC6C25"]},
    {"id": "desert-sand", "name": "Desert Sand", "mood": "earth",
     "colors": ["#E6CCB2", "#DDB892", "#B08968", "#7F5539", "#9C6644"]},
    {"id": "terracotta", "name": "Terracotta", "mood": "earth",
     "colors": ["#CB997E", "#DDBEA9", "#FFE8D6", "#B7B7A4", "#A5A58D"]},

    # ── Monochrome ──────────────────────────────
    {"id": "midnight", "name": "Midnight", "mood": "monochrome",
     "colors": ["#1A1A2E", "#16213E", "#0F3460", "#533483", "#E94560"]},
    {"id": "silver-lining", "name": "Silver Lining", "mood": "monochrome",
     "colors": ["#F8F9FA", "#E9ECEF", "#DEE2E6", "#CED4DA", "#ADB5BD"]},
    {"id": "slate", "name": "Slate", "mood": "monochrome",
     "colors": ["#212529", "#343A40", "#495057", "#6C757D", "#ADB5BD"]},
]


def get_all_palettes() -> list[dict]:
    return PALETTES


def get_palette(palette_id: str) -> dict | None:
    for p in PALETTES:
        if p["id"] == palette_id:
            return p
    return None


def get_palettes_by_mood(mood: str) -> list[dict]:
    return [p for p in PALETTES if p["mood"] == mood]


def get_moods() -> list[str]:
    seen: list[str] = []
    for p in PALETTES:
        if p["mood"] not in seen:
            seen.append(p["mood"])
    return seen
