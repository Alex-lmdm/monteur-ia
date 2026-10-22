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

Réglages propres à un Reel : reel.config.json, à la racine du Reel, passe avant brand.config.json
pour le cadrage du visage et la taille des sous-titres, et pour ce Reel seulement (un rush tourné
plus près de la caméra se cadre sans décaler les Reels suivants). Clés lues, rien d'autre :
    {"montage": {"splitTransform", "faceCrop", "fullFaceTransform", "fullFaceOrigin", "fullFaceCrop"},
     "visual": {"captionsSize"}}
Un transform posé sans son crop fait recalculer le crop depuis ce transform (tools/cadrage.py) : le
crop de la maison, calé sur un autre cadrage, n'est jamais repris. scripts/sync.mjs génère le
brand/tokens.css du Reel avec sa taille de sous-titres ; la mise à jour ne touche jamais reels/.
"""
from __future__ import annotations

import json
import pathlib
import re
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


REGLAGES_REEL = "reel.config.json"
CLES_REEL = {"montage": ("splitTransform", "faceCrop", "fullFaceTransform", "fullFaceOrigin", "fullFaceCrop",
                         "decorTransform", "decorOrigin", "decorCrop",
                         "detoureTransform", "detoureOrigin", "detoureCrop", "detourePlace")}
# `visual` : tout le style de CE Reel (couleurs, polices, sous-titres), les mêmes clés que le `visual`
# de brand.config.example.json, validées comme dans scripts/sync.mjs (visualDuReel) : une valeur que
# la synchro ignore est ignorée ici aussi, pour que les outils et le rendu voient le même style.
COULEURS_REEL = ("bg", "accent", "surface", "text", "muted")
POLICES_REEL = ("fontBody", "fontDisplay", "fontCaptions")


def _visual_valide(brut: dict) -> dict:
    def lire(nom):
        try:
            return json.loads((MAISON / nom).read_text(encoding="utf-8")) if MAISON else {}
        except (OSError, ValueError):
            return {}
    # Les couleurs du style, `muted` compris, même quand le fichier d'exemple ne les liste pas toutes.
    connues = set((lire("brand.config.example.json").get("visual") or {}).keys()) | set(COULEURS_REEL)
    presets = lire("templates/style-presets.json")
    out = {}
    for cle, val in brut.items():
        if val in (None, "") or cle not in connues:
            continue
        if cle == "captionsSize":
            try:
                ok = 30 <= float(val) <= 160
            except (TypeError, ValueError):
                ok = False
        elif cle in COULEURS_REEL:
            ok = isinstance(val, str) and re.fullmatch(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", val.strip()) is not None
        elif cle in POLICES_REEL:
            ok = val in (presets.get("fonts") or {})
        elif cle == "captionsSkin":
            ok = val in (presets.get("captionSkins") or {}) and val != "_comment"
        elif cle == "stylePreset":
            ok = any(p.get("id") == val for p in presets.get("presets") or [])
        else:
            ok = True
        if ok:
            out[cle] = val
    return out


def reglages_reel(dossier=None) -> dict:
    """Les réglages propres au Reel (reel.config.json) : le cadrage (CLES_REEL) et le style (`visual`) ; {} sans fichier."""
    dossier = REEL if dossier is None else pathlib.Path(dossier)
    fichier = dossier / REGLAGES_REEL if dossier is not None else None
    if fichier is None or not fichier.is_file():
        return {}
    try:
        brut = json.loads(fichier.read_text(encoding="utf-8"))
    except ValueError as e:
        sys.exit(f"ERREUR : {fichier} illisible ({e}). Corrige-le ou supprime-le : le Reel reprendra les réglages "
                 "de brand.config.json.")
    out = {}
    for bloc, cles in CLES_REEL.items():
        valeurs = {k: v for k, v in ((brut.get(bloc) or {}) if isinstance(brut, dict) else {}).items()
                   if k in cles and v not in (None, "")}
        if valeurs:
            out[bloc] = valeurs
    visual = _visual_valide((brut.get("visual") or {}) if isinstance(brut, dict) else {})
    if visual:
        out["visual"] = visual
    return out


def avec_reglages_reel(cfg: dict, dossier=None) -> dict:
    """Les réglages `cfg` de la maison, avec par-dessus ceux du Reel (reel.config.json) s'il en a."""
    propres = reglages_reel(dossier)
    if not propres:
        return cfg
    montage = dict(cfg.get("montage") or {})
    r = propres.get("montage", {})
    # Un transform du Reel sans son crop : le crop de la maison (calé sur un autre cadrage) tombe.
    if "splitTransform" in r and "faceCrop" not in r:
        montage.pop("faceCrop", None)
    if ("fullFaceTransform" in r or "fullFaceOrigin" in r) and "fullFaceCrop" not in r:
        montage.pop("fullFaceCrop", None)
    if ("decorTransform" in r or "decorOrigin" in r) and "decorCrop" not in r:
        montage.pop("decorCrop", None)
    if ("detoureTransform" in r or "detoureOrigin" in r) and "detoureCrop" not in r:
        montage.pop("detoureCrop", None)
    return {**cfg, "montage": {**montage, **r}, "visual": {**(cfg.get("visual") or {}), **propres.get("visual", {})}}


def config() -> dict:
    """brand.config.json (généré par /setup) sinon brand.config.example.json (réglages livrés), et,
    pour un outil lancé dans un Reel, ses réglages propres (reel.config.json) par-dessus."""
    cfg = {}
    for name in ("brand.config.json", "brand.config.example.json"):
        p = MAISON / name
        if p.exists():
            cfg = json.loads(p.read_text(encoding="utf-8"))
            break
    return avec_reglages_reel(cfg)
