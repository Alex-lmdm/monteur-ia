#!/usr/bin/env python3
"""LIEUX : la maison (dossier Monteur IA) et le Reel, source unique des chemins des outils.

Un Reel = un projet : chaque Reel vit dans reels/<nom>/ avec la forme de l'ancien plan de
travail (index.html, compositions/, derush/, assets/video/, tools/, work/, exports/). Les outils
y sont copiés depuis la maison et lisent ICI ce qui reste partagé dans la maison : réglages
(brand.config.json), presets de style, polices, SFX et musique.

Usage :
    from lieux import MAISON, REEL, config
    MAISON / "brand.config.json"   # réglages du client
    reel() / "index.html"          # le montage du Reel (quitte proprement hors d'un Reel)
"""
from __future__ import annotations

import json
import pathlib
import sys

# Windows : une sortie lue par l'agent (redirigée) est en cp1252, et un « ✅ » y fait planter l'outil.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

OUTILS = pathlib.Path(__file__).resolve().parent


def maison_de(depart) -> pathlib.Path | None:
    """Le dossier Monteur IA qui contient `depart` : celui qui porte templates/AGENT.md.tpl."""
    p = pathlib.Path(depart).resolve()
    for d in (p, *p.parents):
        if (d / "templates" / "AGENT.md.tpl").is_file():
            return d
    return None


MAISON = maison_de(OUTILS)
if MAISON is None:
    # Cas typique : un Reel copié par le bouton Duplicate de l'app HyperFrames, hors du dossier Monteur IA.
    sys.exit(f"ERREUR : {OUTILS.parent} n'est pas rangé dans un dossier Monteur IA (copie faite par le "
             "bouton Duplicate de l'app HyperFrames ?) : réglages, sons et skills n'y sont pas. Recrée-le "
             "depuis le dossier Monteur IA : python3 tools/nouveau_reel.py \"<sujet>\" --depuis "
             f"\"{OUTILS.parent}\" --ouvrir")

# Le Reel dont ces outils font partie ; None quand ils tournent depuis la maison elle-même.
REEL = OUTILS.parent if OUTILS.parent != MAISON else None


def reel() -> pathlib.Path:
    """Le Reel courant, ou un arrêt clair si l'outil est lancé depuis la maison."""
    if REEL is None:
        sys.exit("ERREUR : cet outil travaille sur un Reel. Lance-le depuis le dossier du Reel "
                 "(reels/<nom>/tools/…), jamais depuis la racine du dossier Monteur IA.")
    return REEL


def config() -> dict:
    """brand.config.json (généré par /setup) sinon brand.config.example.json (réglages livrés)."""
    for name in ("brand.config.json", "brand.config.example.json"):
        p = MAISON / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}
