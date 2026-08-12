#!/usr/bin/env python3
"""Résolution du STYLE visuel — source unique pour les outils Python.

Même logique que scripts/sync.mjs : un preset de `templates/style-presets.json` sert de
point de départ, et `brand.config.json` le surcharge. Aucune couleur ni police n'est
écrite en dur dans les outils : un hex en dur, c'est l'identité du template qui se
retrouve dans les vidéos de tout le monde.

Usage :
    from brand_style import style
    s = style()
    s.bg                 # "#0d1220"
    s.accent             # "#58a6ff"
    s.captions_skin      # "outline"
    s.captions_font_file # PosixPath(".../assets/fonts/Inter-900.ttf")  (mesure PIL)
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRESETS_PATH = ROOT / "templates/style-presets.json"


def _read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _load_config() -> dict:
    for name in ("brand.config.json", "brand.config.example.json"):
        cfg = _read_json(ROOT / name)
        if cfg:
            return cfg
    return {}


def _hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    v = str(value or "").strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        return None
    try:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return None


def _luminance(value: str) -> float:
    """Luminance relative WCAG (0 = noir, 1 = blanc)."""
    rgb = _hex_to_rgb(value)
    if not rgb:
        return 0.0
    chan = []
    for raw in rgb:
        s = raw / 255
        chan.append(s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _pick_readable(base: str, candidates: list[str]) -> str:
    return max((c for c in candidates if c), key=lambda c: _contrast(base, c))


@dataclass(frozen=True)
class Style:
    preset_id: str
    chosen: bool
    bg: str
    surface: str
    text: str
    muted: str
    accent: str
    contrast: str          # couleur lisible POSÉE SUR l'accent
    stroke: str            # contour de lisibilité
    font_body: str
    font_display: str
    font_captions: str
    captions_skin: str
    captions_lines: int
    default_layout: str
    cta_style: str
    captions_font_file: pathlib.Path | None  # .ttf lisible par PIL, pour mesurer la largeur

    @property
    def bg_hex(self) -> str:
        """Le fond sans `#`, pour les filtres ffmpeg (`color=c=0x...`)."""
        return self.bg.lstrip("#")


def style() -> Style:
    cfg = _load_config()
    presets_file = _read_json(PRESETS_PATH)
    presets = presets_file.get("presets") or []

    wanted = (cfg.get("visual") or {}).get("stylePreset")
    preset = next((p for p in presets if p["id"] == wanted), None)
    if preset is None:
        preset = next((p for p in presets if p.get("isUnset")), presets[0] if presets else None)
    if preset is None:
        raise SystemExit(
            "ERREUR : aucun preset de style dans templates/style-presets.json — "
            "impossible de résoudre les couleurs."
        )

    # Une clé absente / nulle dans la config ne doit PAS écraser le preset.
    overrides = {k: v for k, v in (cfg.get("visual") or {}).items() if v not in (None, "")}
    visual = {**preset["visual"], **overrides}

    bg = visual["bg"]
    text = visual.get("text") or _pick_readable(bg, ["#ffffff", "#111111"])
    accent = visual["accent"]

    fonts = presets_file.get("fonts") or {}
    measure = (fonts.get(visual["fontCaptions"]) or {}).get("measureFile")
    measure_path = ROOT / "assets/fonts" / measure if measure else None
    if measure_path is not None and not measure_path.exists():
        measure_path = None

    return Style(
        preset_id=preset["id"],
        chosen=bool(wanted) and not preset.get("isUnset"),
        bg=bg,
        surface=visual["surface"],
        text=text,
        muted=visual.get("muted") or text,
        accent=accent,
        contrast=_pick_readable(accent, [bg, text, "#ffffff", "#111111"]),
        stroke="#0b0b0b" if _luminance(text) > 0.5 else "#ffffff",
        font_body=visual["fontBody"],
        font_display=visual["fontDisplay"],
        font_captions=visual["fontCaptions"],
        captions_skin=visual.get("captionsSkin") or "plate",
        captions_lines=int(visual.get("captionsLines") or 1),
        default_layout=(cfg.get("montage") or {}).get("defaultLayout")
        or (preset.get("montage") or {}).get("defaultLayout")
        or "split",
        cta_style=(cfg.get("cta") or {}).get("style")
        or (preset.get("cta") or {}).get("style")
        or "comment-field",
        captions_font_file=measure_path,
    )


if __name__ == "__main__":
    s = style()
    print(f"style      : {s.preset_id}{'' if s.chosen else '  (AUCUN STYLE CHOISI — /setup visuel)'}")
    print(f"couleurs   : fond {s.bg} · accent {s.accent} · texte {s.text}")
    print(f"polices    : body {s.font_body} · sous-titres {s.font_captions} (skin {s.captions_skin})")
    print(f"cadrage    : {s.default_layout} · CTA {s.cta_style}")
    print(f"mesure PIL : {s.captions_font_file or 'AUCUNE (.ttf manquant)'}")
