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
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lieux import MAISON, avec_reglages_reel  # noqa: E402

# Réglages, presets et polices vivent dans la maison, même quand l'outil tourne dans un Reel.
ROOT = MAISON
PRESETS_PATH = ROOT / "templates/style-presets.json"


def _read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _load_config() -> dict:
    """Les réglages de la maison et, dans un Reel, son reel.config.json par-dessus (tools/lieux.py)."""
    for name in ("brand.config.json", "brand.config.example.json"):
        cfg = _read_json(ROOT / name)
        if cfg:
            return avec_reglages_reel(cfg)
    return avec_reglages_reel({})


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


def _mix(a: str, b: str, t: float) -> str:
    """Mélange linéaire de deux couleurs (t=0 -> a, t=1 -> b), arrondi comme Math.round de sync.mjs."""
    ra, rb = _hex_to_rgb(a), _hex_to_rgb(b)
    if not ra or not rb:
        return a
    return "#" + "".join(f"{min(255, max(0, int(x + (y - x) * t + 0.5))):02x}" for x, y in zip(ra, rb))


@dataclass(frozen=True)
class Style:
    preset_id: str
    chosen: bool
    perso: bool            # fond ou accent du client, autres que ceux du preset
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
    captions_size: int     # px, visual.captionsSize (défaut 50) = --brand-cap-size
    default_layout: str
    cta_style: str
    captions_font_file: pathlib.Path | None  # .ttf lisible par PIL, pour mesurer la largeur
    # Allure des sous-titres (visual.captions*, mêmes règles que scripts/sync.mjs, captionLook) :
    captions_case: str = "upper"         # "upper" (défaut) ou "asis" : le texte tel qu'écrit
    captions_weight: int = 900           # graisse affichée ("auto" = la plus forte de la police)
    captions_line_height: float = 1.35
    captions_padding: str | None = None  # None = la marge du skin
    captions_ink: str | None = None      # None = --brand-contrast (skin block)

    @property
    def bg_hex(self) -> str:
        """Le fond sans `#`, pour les filtres ffmpeg (`color=c=0x...`)."""
        return self.bg.lstrip("#")


def _caption_size(value) -> int:
    try:
        size = round(float(value))
    except (TypeError, ValueError):
        return 50
    return size if 30 <= size <= 100 else 50


def _caption_case(value) -> str:
    return "asis" if re.sub(r"[^a-z]", "", str(value or "").lower()) == "asis" else "upper"


def _caption_weight(value, faces) -> int:
    if str(value).lower() == "auto":
        poids = [int(f.get("weight") or 400) for f in faces if str(f.get("weight") or 400).isdigit()]
        return max(poids) if poids else 900
    try:
        w = round(float(value))
    except (TypeError, ValueError):
        return 900
    return w if 100 <= w <= 900 else 900


def _caption_line_height(value) -> float:
    try:
        lh = float(value)
    except (TypeError, ValueError):
        return 1.35
    return lh if 0.8 <= lh <= 3 else 1.35


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
            "ERREUR : aucun preset de style dans templates/style-presets.json : "
            "impossible de résoudre les couleurs."
        )

    # Une clé absente / nulle dans la config ne doit PAS écraser le preset.
    overrides = {k: v for k, v in (cfg.get("visual") or {}).items() if v not in (None, "")}
    visual = {**preset["visual"], **overrides}

    bg = visual["bg"]
    lisible = _pick_readable(bg, ["#ffffff", "#111111"])

    # Même règle que sync.mjs (resolveStyle) : le texte, la surface et le gris secondaire du preset
    # qui ne vont plus avec le fond du client sont recalculés ; une valeur qu'il a réglée est gardée.
    def garde(cle: str, va) -> bool:
        return cle in overrides or (visual.get(cle) not in (None, "") and va(visual[cle]))

    text = visual["text"] if garde("text", lambda c: _contrast(c, bg) >= 4.5) else lisible
    surface = visual["surface"] if garde("surface", lambda c: _contrast(c, bg) < 1.6) else _mix(bg, lisible, 0.07)
    muted = visual["muted"] if garde("muted", lambda c: _contrast(c, bg) >= 4.5) else _mix(text, bg, 0.42)
    accent = visual["accent"]
    perso = any(cle in overrides and str(overrides[cle]).lower() != str(preset["visual"].get(cle)).lower()
                for cle in ("bg", "accent"))

    fonts = presets_file.get("fonts") or {}
    measure = (fonts.get(visual["fontCaptions"]) or {}).get("measureFile")
    measure_path = ROOT / "assets/fonts" / measure if measure else None
    if measure_path is not None and not measure_path.exists():
        measure_path = None
    # La mesure suit la graisse affichée quand la police en déclare un .ttf/.otf (sinon measureFile).
    # Un faux gras du navigateur épaissit les traits sans élargir les lettres : même mesure.
    faces = (fonts.get(visual["fontCaptions"]) or {}).get("faces") or []
    weight = _caption_weight(visual.get("captionsWeight", 900), faces)
    for f in faces:
        fichier = ROOT / "assets/fonts" / str(f.get("file") or "")
        if str(f.get("weight") or 400) == str(weight) and fichier.suffix.lower() in (".ttf", ".otf") \
                and f.get("style", "normal") == "normal" and fichier.exists():
            measure_path = fichier
            break

    return Style(
        preset_id=preset["id"],
        chosen=(cfg.get("setup") or {}).get("styleChosen") is True
        or (bool(wanted) and not preset.get("isUnset")),
        perso=perso,
        bg=bg,
        surface=surface,
        text=text,
        muted=muted,
        accent=accent,
        contrast=_pick_readable(accent, [bg, text, "#ffffff", "#111111"]),
        stroke="#0b0b0b" if _luminance(text) > 0.5 else "#ffffff",
        font_body=visual["fontBody"],
        font_display=visual["fontDisplay"],
        font_captions=visual["fontCaptions"],
        captions_skin=visual.get("captionsSkin") or "plate",
        captions_lines=int(visual.get("captionsLines") or 1),
        captions_size=_caption_size(visual.get("captionsSize")),
        default_layout=(cfg.get("montage") or {}).get("defaultLayout")
        or (preset.get("montage") or {}).get("defaultLayout")
        or "split",
        cta_style=(cfg.get("cta") or {}).get("style")
        or (preset.get("cta") or {}).get("style")
        or "comment-field",
        captions_font_file=measure_path,
        captions_case=_caption_case(visual.get("captionsCase")),
        captions_weight=weight,
        captions_line_height=_caption_line_height(visual.get("captionsLineHeight", 1.35)),
        captions_padding=str(visual["captionsPadding"]) if visual.get("captionsPadding") not in (None, "") else None,
        captions_ink=str(visual["captionsInk"]) if visual.get("captionsInk") not in (None, "", "contrast") else None,
    )


if __name__ == "__main__":
    s = style()
    suite = "  (avec tes couleurs)" if s.perso else "" if s.chosen else "  (style de depart, pas encore personnalise : /setup visuel)"
    print(f"style      : {s.preset_id}{suite}")
    print(f"couleurs   : fond {s.bg} · accent {s.accent} · texte {s.text}")
    print(f"polices    : body {s.font_body} · sous-titres {s.font_captions} (skin {s.captions_skin})")
    print(f"cadrage    : {s.default_layout} · CTA {s.cta_style}")
    print(f"mesure PIL : {s.captions_font_file or 'AUCUNE (.ttf manquant)'}")
