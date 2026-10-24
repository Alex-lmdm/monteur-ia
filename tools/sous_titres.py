#!/usr/bin/env python3
"""STYLES DE SOUS-TITRES : un look du catalogue posé sur les sous-titres d'un Reel.

Le catalogue (templates/styles-sous-titres.json ; index lisible dans le skill motion-design,
references/styles-sous-titres.md) décrit chaque style : sa police, ses couleurs, comment les mots
arrivent (d'un bloc, mot à mot, un mot à la fois) et ce qui marque le mot dit (couleur, boîte,
taille). Un style est un look : il se pose sur n'importe quel montage, à la hauteur que le montage
donne aux sous-titres (tools/montage_captions.py), styles de montage du catalogue compris.

Usage (depuis le dossier du Reel ; --maison vaut pour toutes ses vidéos) :
    python3 tools/sous_titres.py --liste                     # les styles : numéro, nom, ce qu'on voit
    python3 tools/sous_titres.py --choisir 7                 # le style 7 pour CE Reel (reel.config.json)
    python3 tools/sous_titres.py --choisir 7 --maison        # pour toutes ses vidéos, et ce Reel s'il y en a un
    python3 tools/sous_titres.py --choisir                   # le style gardé pour toutes ses vidéos, sur ce Reel
    python3 tools/sous_titres.py --retouche allume=#3aa0ff   # une retouche du style choisi
    python3 tools/sous_titres.py --sans [--maison]           # plus de style : sous-titres d'un bloc
    python3 tools/sous_titres.py                             # applique le style à compositions/captions.html

--choisir, --retouche et --sans écrivent les réglages puis lancent la synchro. La maison (brand.config.json)
ne garde que visual.captionsStyle et visual.captionsLook : la police, la taille et la casse du style vont
dans le reel.config.json de chaque Reel (sinon elles changeraient aussi les vidéos YouTube et les
stories). Un Reel sans style posé alors que la maison en garde un le reçoit au premier passage de ce
script, qui s'arrête pour faire remesurer le découpage. Ensuite, dans le Reel :
`python3 tools/montage_captions.py --write` (la largeur se mesure dans la police du style), puis ce
script. Relançable : la sortie de montage_captions.py est gardée dans work/captions.origine.html, et
chaque passage repart d'elle. Sans style choisi, il remet cette sortie telle quelle.

Retouches (--retouche cle=valeur, gardées dans visual.captionsLook, elles passent avant le catalogue) :
    couleur  texte des mots           allume   le mot dit (couleur)     boite   la boîte du mot dit
    plaque   le bandeau (ou aucune)   contour  « 6px #000000 » ou aucun ombre   dure, douce, lueur, aucune
    fort     le mot fort (couleur)    mode     bloc, karaoke, mot-a-mot, un-mot
    entree   aucune, pop, rebond, glisse, fondu, flou, zoom, machine        lignes  1 ou 2
    taille   en px (30 à 160)         police   une police de templates/style-presets.json
Une couleur : un hex (#ffe600), ou accent / texte / fond (les couleurs du client).

Mot fort (styles qui en ont un) : entoure le mot d'astérisques dans le découpage (MANUAL de
montage_captions.py : « tes *vidéos* ») ; sans astérisque, le mot le plus long du sous-titre.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lieux import MAISON, REEL, REGLAGES_REEL, config  # noqa: E402

CATALOGUE = MAISON / "templates/styles-sous-titres.json"
MODES = ("bloc", "karaoke", "mot-a-mot", "un-mot")
ENTREES = ("aucune", "pop", "rebond", "glisse", "fondu", "flou", "zoom", "machine")
MARQUES = ("couleur", "boite", "grossit", "police")
# Réglages du `visual` qu'un style pose (police, taille, casse…) : les autres restent ceux du client.
CLES_STYLE = ("fontCaptions", "fontAccent", "captionsSkin", "captionsSize", "captionsCase", "captionsWeight",
              "captionsLineHeight", "captionsPadding", "captionsInk")
COULEURS_NOMMEES = {"accent": "var(--brand-accent)", "texte": "var(--brand-text)", "fond": "var(--brand-bg)"}
MARQUEUR = 'data-sous-titres="'


def catalogue() -> list[dict]:
    try:
        return json.loads(CATALOGUE.read_text(encoding="utf-8"))["styles"]
    except (OSError, ValueError, KeyError) as e:
        sys.exit(f"ERREUR : catalogue des styles de sous-titres illisible ({CATALOGUE}) : {e}")


def style_numero(n) -> dict:
    try:
        n = int(n)
    except (TypeError, ValueError):
        sys.exit(f"ERREUR : « {n} » n'est pas un numéro de style de sous-titres (--liste pour les voir).")
    for s in catalogue():
        if s["n"] == n:
            return s
    sys.exit(f"ERREUR : pas de style de sous-titres n°{n} (--liste pour les voir).")


# ---------------------------------------------------------------------------------------------
# Réglages : choisir, retoucher, retirer
# ---------------------------------------------------------------------------------------------
# Ce que la maison garde « pour toutes ses vidéos » : le numéro du style et ses retouches, rien
# d'autre. La police, la taille et la casse du style ne vont que dans le reel.config.json de chaque
# Reel : écrites dans le `visual` de la maison, elles changeraient aussi les vidéos YouTube et les
# stories, qui lisent les mêmes réglages (textes d'appui à 1,5 fois la taille des sous-titres).
def fichier_maison() -> pathlib.Path:
    f = MAISON / "brand.config.json"
    if not f.exists():
        shutil.copyfile(MAISON / "brand.config.example.json", f)
    return f


def fichier_reel() -> pathlib.Path:
    if REEL is None:
        sys.exit("ERREUR : hors d'un Reel, ajoute --maison (le style vaut alors pour toutes ses vidéos).")
    return REEL / REGLAGES_REEL


def lire_json(f: pathlib.Path) -> dict:
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except ValueError as e:
        sys.exit(f"ERREUR : {f} illisible ({e}).")


def visual_de(f: pathlib.Path) -> dict:
    return dict(lire_json(f).get("visual") or {})


def ecrire_visual(f: pathlib.Path, maj: dict, retire=()) -> None:
    """Pose `maj` dans le `visual` de `f` ; une clé retirée disparaît d'un reel.config.json et repasse
    à null dans brand.config.json (la forme du fichier d'exemple)."""
    cfg = lire_json(f)
    v = dict(cfg.get("visual") or {})
    for cle in retire:
        v.pop(cle, None) if f.name == REGLAGES_REEL else v.update({cle: None})
    v.update(maj)
    cfg["visual"] = v
    f.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def synchro() -> None:
    node = shutil.which("node")
    if node is None:
        print("  ⚠ node introuvable : lance `npm run sync` depuis le dossier Monteur IA.")
        return
    r = subprocess.run([node, "scripts/sync.mjs"], cwd=MAISON, capture_output=True, text=True, encoding="utf-8")
    for l in (r.stdout + r.stderr).splitlines():
        if "ignoré" in l or "ERREUR" in l:
            print(f"  ⚠ {l.strip()}")


def materialiser(n, look: dict) -> None:
    """Les réglages du style n°n (police, taille, casse…) dans le reel.config.json du Reel, avec ses
    retouches de taille et de police. Les réglages de sous-titres d'avant tombent ; la police d'accent
    du client reste, sauf si c'est celle d'un style de sous-titres d'avant."""
    s = style_numero(n)
    f = fichier_reel()
    base = {k: s["visual"][k] for k in CLES_STYLE if k in s["visual"]}
    if look.get("taille"):
        base["captionsSize"] = int(look["taille"])
    if look.get("police"):
        base["fontCaptions"] = look["police"]
    retire = [k for k in CLES_STYLE if k not in base and k != "fontAccent"]
    avant = visual_de(f)
    if "fontAccent" not in base and avant.get("captionsStyle") not in (None, "", "aucun"):
        ancien = next((x for x in catalogue() if str(x["n"]) == str(avant["captionsStyle"])), None)
        if ancien and ancien["visual"].get("fontAccent") == avant.get("fontAccent"):
            retire.append("fontAccent")
    ecrire_visual(f, {**base, "captionsStyle": s["n"]}, retire)


def polices_livrees() -> dict:
    try:
        return json.loads((MAISON / "templates/style-presets.json").read_text(encoding="utf-8")).get("fonts") or {}
    except (OSError, ValueError):
        return {}


def couleur_valide(val: str) -> str | None:
    v = str(val).strip()
    if v.lower() in COULEURS_NOMMEES or v.lower() in ("aucun", "aucune"):
        return v.lower()
    return v if re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", v) else None


def retouche_valide(cle: str, val: str):
    """La valeur d'une retouche, normalisée, ou None si elle ne veut rien dire."""
    if cle in ("couleur", "allume", "boite", "plaque", "fort"):
        return couleur_valide(val)
    if cle == "contour":
        v = val.strip().lower()
        if v in ("aucun", "aucune"):
            return "aucun"
        m = re.fullmatch(r"(\d+(?:\.\d+)?)px\s+(#[0-9a-fA-F]{3,8}|accent|texte|fond)", v)
        return f"{m.group(1)}px {m.group(2)}" if m else None
    if cle == "ombre":
        v = val.strip().lower()
        m = re.fullmatch(r"(dure|lueur)(?:\s+(#[0-9a-fA-F]{3,8}|accent|texte|fond))?", v)
        return v if v in ("douce", "aucune") or m else None
    if cle == "mode":
        return val if val in MODES else None
    if cle == "entree":
        return val if val in ENTREES else None
    if cle == "lignes":
        return int(val) if str(val) in ("1", "2") else None
    if cle == "taille":
        return int(val) if str(val).isdigit() and 30 <= int(val) <= 160 else None
    if cle == "police":
        return val if val in polices_livrees() else None
    return None


def choisir(n, maison: bool) -> None:
    if n is None:
        n = visual_de(fichier_maison()).get("captionsStyle")
        if n in (None, "", "aucun"):
            sys.exit("ERREUR : aucun style de sous-titres gardé pour toutes ses vidéos : donne un numéro (--choisir 7).")
    s = style_numero(n)
    look_maison = visual_de(fichier_maison()).get("captionsLook") or {}
    if maison:
        ecrire_visual(fichier_maison(), {"captionsStyle": s["n"]}, retire=["captionsLook"])
        look_maison = {}
    if REEL is not None:
        # Un choix pour ce Reel seul masque les retouches de la maison (faites pour un autre style).
        reel_look = {} if (maison or not look_maison) else {"captionsLook": {}}
        ecrire_visual(fichier_reel(), reel_look, retire=["captionsLook"])
        materialiser(s["n"], {} if not maison else look_maison)
    synchro()
    ou = "toutes ses vidéos (brand.config.json)" if maison else "ce Reel (reel.config.json)"
    print(f"Style de sous-titres n°{s['n']} « {s['nom']} » choisi pour {ou}.")
    if REEL is not None:
        print("Ensuite : python3 tools/montage_captions.py --write, puis python3 tools/sous_titres.py")


def retoucher(paires: list[str], maison: bool) -> None:
    f = fichier_maison() if maison else fichier_reel()
    look = dict(visual_de(f).get("captionsLook") or {})
    for p in paires:
        cle, _, val = p.partition("=")
        cle = cle.strip()
        norme = retouche_valide(cle, val.strip())
        if norme is None:
            sys.exit(f"ERREUR : retouche « {p} » non comprise (voir l'en-tête de tools/sous_titres.py).")
        look[cle] = norme
    ecrire_visual(f, {"captionsLook": look})
    # Taille ou police : elles vont dans les réglages du Reel, la largeur se remesure.
    if REEL is not None and {"taille", "police"} & {p.partition("=")[0].strip() for p in paires}:
        n = (config().get("visual") or {}).get("captionsStyle")
        if n not in (None, "", "aucun"):
            materialiser(n, (config().get("visual") or {}).get("captionsLook") or {})
            print("Taille ou police changée : relance python3 tools/montage_captions.py --write, puis ce script.")
    synchro()
    print(f"Retouche gardée dans {f.name} : " + ", ".join(f"{k}={v}" for k, v in look.items()))


def retirer(maison: bool) -> None:
    if maison:
        ecrire_visual(fichier_maison(), {}, retire=["captionsStyle", "captionsLook"])
    if REEL is not None:
        f = fichier_reel()
        avant = visual_de(f)
        # Les réglages posés par le style partent avec lui ; ceux qui viennent d'ailleurs (un style de
        # montage, une retouche) restent.
        s = next((x for x in catalogue() if str(x["n"]) == str(avant.get("captionsStyle"))), None)
        retire = ["captionsStyle", "captionsLook"] + [k for k in CLES_STYLE if s and avant.get(k) == s["visual"].get(k)]
        # La maison garde un style : ce Reel s'en écarte explicitement.
        reste = {"captionsStyle": "aucun"} if visual_de(fichier_maison()).get("captionsStyle") not in (None, "", "aucun") and not maison else {}
        ecrire_visual(f, reste, retire=[k for k in retire if k not in reste])
    synchro()
    print("Plus de style de sous-titres " + ("pour toutes ses vidéos" if maison else "pour ce Reel") + " : sous-titres d'un bloc.")


def lister() -> None:
    for s in catalogue():
        print(f"{s['n']:>2}  {s['nom']:<22} {s['voit']}")


# ---------------------------------------------------------------------------------------------
# Le look : catalogue + retouches
# ---------------------------------------------------------------------------------------------
def look_du_style(s: dict, retouches: dict) -> dict:
    look = json.loads(json.dumps(s["look"]))
    look.setdefault("allume", None)
    look.setdefault("fort", None)
    look.setdefault("plaque", None)
    for cle, val in (retouches or {}).items():
        if retouche_valide(cle, str(val)) is None:
            print(f"  ⚠ captionsLook.{cle} « {val} » ignoré.")
            continue
        if cle in ("couleur", "contour", "ombre", "mode", "entree", "lignes"):
            look[cle] = None if str(val) in ("aucun", "aucune") else val
        elif cle == "allume":
            look["allume"] = {**(look["allume"] or {"type": "couleur"}), "couleur": val, "tour": None}
        elif cle == "boite":
            look["allume"] = {**(look["allume"] or {}), "type": "boite", "fond": val, "tour": None}
        elif cle == "plaque":
            look["plaque"] = None if val == "aucune" else {**(look["plaque"] or {"arrondi": 12, "marge": "0.1em 0.35em"}), "fond": val}
        elif cle == "fort":
            look["fort"] = {**(look["fort"] or {"type": "couleur"}), "couleur": val, "tour": None}
    look["mode"] = look.get("mode") if look.get("mode") in MODES else "bloc"
    look["entree"] = look.get("entree") if look.get("entree") in ENTREES else "aucune"
    return look


def css_couleur(v) -> str:
    v = str(v)
    return COULEURS_NOMMEES.get(v.lower(), v)


def css_ombre(ombre, taille: float) -> str:
    if not ombre:
        return "none"
    mot, _, couleur = str(ombre).partition(" ")
    c = css_couleur(couleur) if couleur else "#000000"
    if mot == "dure":
        d = max(2, round(taille * 0.06))
        return f"{d}px {d}px 0 {c}"
    if mot == "lueur":
        return f"0 0 {round(taille * 0.18)}px {c}, 0 0 {round(taille * 0.42)}px {c}"
    if mot == "douce":
        return "0 3px 14px rgba(0, 0, 0, 0.55), 0 0 4px rgba(0, 0, 0, 0.45)"
    return "none"


def css_du_look(s: dict, look: dict, taille: float) -> str:
    """Les règles du style, scopées sous #captions .cap.st : elles passent devant le skin de tokens.css."""
    var = {"--st-couleur": css_couleur(look.get("couleur") or "#ffffff")}
    allume, fort, plaque = look.get("allume"), look.get("fort"), look.get("plaque")
    for i, c in enumerate((allume or {}).get("tour") or [(allume or {}).get("couleur") or "#ffe600"]):
        var[f"--st-allume-{i}"] = css_couleur(c)
    if allume and allume.get("fond"):
        var["--st-boite"] = css_couleur(allume["fond"])
    for i, c in enumerate((fort or {}).get("tour") or [(fort or {}).get("couleur") or "#ffe600"]):
        var[f"--st-fort-{i}"] = css_couleur(c)
    if fort and fort.get("fond"):
        var["--st-fort-boite"] = css_couleur(fort["fond"])
    if plaque:
        var["--st-plaque"] = css_couleur(plaque.get("fond") or "#000000")
    contour = look.get("contour")
    trait = ""
    if contour:
        ep, _, c = str(contour).partition(" ")
        trait = f"  -webkit-text-stroke: {ep} {css_couleur(c or '#000000')};\n  paint-order: stroke fill;\n"
    ombre = css_ombre(look.get("ombre"), taille)
    esp = look.get("espacement") or 0
    lignes = [
        f"/* Style de sous-titres n°{s['n']} « {s['nom']} » : écrit par tools/sous_titres.py depuis le catalogue et",
        "   les réglages (visual.captionsStyle, visual.captionsLook). Ne pas retoucher ici : relancer l'outil. */",
        "#captions { " + " ".join(f"{k}: {v};" for k, v in var.items()) + " }",
        "#captions .cap.st { background: none; padding: 0; border: 0; border-radius: 0; box-shadow: none;\n"
        f"  -webkit-text-stroke: 0; color: var(--st-couleur); text-shadow: {ombre}; letter-spacing: {esp}em; text-align: center; }}",
        "#captions .cap.st .in { display: inline-block; transform-origin: 50% 60%; }",
        "#captions .cap.st .w { position: relative; display: inline-block; transform-origin: 50% 60%; }",
        "#captions .cap.st .b, #captions .cap.st .h {\n" + (trait or "  -webkit-text-stroke: 0;\n") + "}",
    ]
    if plaque:
        bord = f"border-radius: {plaque.get('arrondi', 12)}px; padding: {plaque.get('marge', '0.1em 0.35em')};"
        if plaque.get("par") == "ligne":
            lignes.append("#captions .cap.st .t { background: var(--st-plaque); " + bord
                          + " -webkit-box-decoration-break: clone; box-decoration-break: clone; }")
        else:
            lignes.append("#captions .cap.st .in { background: var(--st-plaque); " + bord + " }")
    if allume:
        lignes.append("#captions .cap.st .w .h { position: absolute; left: 0; top: 0; opacity: 0; white-space: nowrap; }")
        for i in range(len((allume.get("tour") or [None]))):
            lignes.append(f"#captions .cap.st.a{i} .w .h {{ color: var(--st-allume-{i}); }}")
        if allume.get("type") == "boite":
            # Boîte centrée sur le mot, à la hauteur du texte (pas de l'interligne) : le mot ne bouge pas.
            lignes.append("#captions .cap.st .w .h { left: -0.14em; top: 50%; transform: translateY(-50%); line-height: 1.2;"
                          " padding: 0.07em 0.14em;"
                          f" border-radius: {allume.get('arrondi', 10)}px; background: var(--st-boite);"
                          f" color: {css_couleur(allume.get('couleur') or '#ffffff')};"
                          + (" -webkit-text-stroke: 0; text-shadow: none;" if not allume.get("contour") else "") + " }")
    if fort:
        for i in range(len((fort.get("tour") or [None]))):
            lignes.append(f"#captions .cap.st.f{i} .w.k .b {{ color: var(--st-fort-{i}); }}")
        t = fort.get("type")
        if t == "boite":
            lignes.append("#captions .cap.st .w.k .b { background: var(--st-fort-boite); padding: 0 0.12em; margin: 0 -0.06em;"
                          f" border-radius: {fort.get('arrondi', 8)}px; -webkit-text-stroke: 0; text-shadow: none; }}")
        elif t == "police":
            st = fort.get("style") or "normal"
            lignes.append("#captions .cap.st .w.k .b { font-family: var(--brand-font-accent); font-style: " + st
                          + f"; font-weight: {fort.get('graisse', 400)}; font-size: {fort.get('echelle', 1.3)}em;"
                          " text-transform: none; letter-spacing: 0; line-height: 1; }")
        elif t == "grossit":
            lignes.append(f"#captions .cap.st .w.k {{ transform: scale({fort.get('echelle', 1.18)}); margin: 0 0.1em; }}")
        if fort.get("lueur"):
            lignes.append("#captions .cap.st .w.k .b { text-shadow: 0 0 0.16em currentColor, 0 0 0.42em currentColor; }")
    if look["entree"] == "machine":
        lignes.append("#captions .cap.st .c { display: inline; }")
    return "\n".join("      " + l.replace("\n", "\n      ") for l in lignes) + "\n"


# ---------------------------------------------------------------------------------------------
# Les sous-titres du Reel
# ---------------------------------------------------------------------------------------------
LIGNE_CAP = re.compile(r'( *)<div class="cap clip" id="cap-(\d+)" style="top:(\d+)px" data-start="([\d.]+)" '
                       r'data-duration="([\d.]+)" data-track-index="(\d+)">(.*?)</div>')
FAIBLES = set("le la les un une des du de d l au aux à a en et ou mais donc car que qui dont ne pas se sa son ses "
              "ce cet cette ces mon ma mes ton ta tes nos vos leur leurs on il elle ils elles je tu nous vous y "
              "est sont c j l qu n s t m pour par sur avec dans sans plus tout tous très".split())


def normaliser(m: str) -> str:
    import unicodedata
    m = unicodedata.normalize("NFD", m.lower())
    return re.sub(r"[^a-z0-9%]", "", "".join(c for c in m if unicodedata.category(c) != "Mn"))


def temps_des_mots(toks, debut, fin, mots):
    """Le départ de chaque mot affiché : le mot transcrit correspondant dans la fenêtre du sous-titre
    (même méthode que l'outil karaoké du style 4) ; un mot introuvable se place entre ses voisins."""
    fen = [w for w in mots if debut - 0.35 <= w["start"] < fin + 0.05]
    temps, k = [], 0
    for t in toks:
        n, trouve = normaliser(t), None
        for q in range(k, len(fen)):
            if n and normaliser(fen[q]["w"]) == n:
                trouve, k = fen[q]["start"], q + 1
                break
        temps.append(trouve)
    if not temps:
        return temps
    temps[0] = debut
    for q in range(1, len(temps)):
        if temps[q] is None:
            suiv = next((temps[r] for r in range(q + 1, len(temps)) if temps[r] is not None), fin)
            temps[q] = temps[q - 1] + (suiv - temps[q - 1]) / 2
        temps[q] = min(max(temps[q], temps[q - 1] + 0.06), fin - 0.04)
    return temps


def mot_fort(toks) -> int | None:
    marques = [i for i, t in enumerate(toks) if t.startswith("*") and t.endswith("*") and len(t) > 2]
    if marques:
        return marques[0]
    pleins = [(len(normaliser(t)), i) for i, t in enumerate(toks) if normaliser(t) not in FAIBLES and len(normaliser(t)) >= 3]
    chiffres = [i for i, t in enumerate(toks) if any(c.isdigit() for c in t)]
    if chiffres:
        return chiffres[0]
    return max(pleins)[1] if pleins else None


LARGEUR_MAX = 940   # px : la largeur de l'image (1080) moins les marges de côté des zones sûres


def mesureur():
    """La largeur affichée d'un texte dans la police de sous-titres (casse et graisse comprises),
    comme tools/montage_captions.py la mesure ; None sans Pillow ni .ttf de mesure."""
    try:
        from PIL import ImageFont
        import brand_style
        st = brand_style.style()
        if st.captions_font_file is None:
            return None
        police = ImageFont.truetype(str(st.captions_font_file), st.captions_size)
        try:
            axes = police.get_variation_axes()
            valeurs = []
            for ax in axes:
                nom = ax.get("name")
                nom = (nom.decode("utf-8", "replace") if isinstance(nom, bytes) else str(nom or "")).lower()
                v = {"weight": st.captions_weight, "optical size": st.captions_size}.get(nom, ax["default"])
                valeurs.append(min(max(v, ax["minimum"]), ax["maximum"]))
            police.set_variation_by_axes(valeurs)
        except (OSError, AttributeError):
            pass
        haut = st.captions_case == "upper"
        return lambda texte: police.getlength(texte.upper() if haut else texte)
    except Exception:   # mesure de confort : sans elle, la taille du style reste telle quelle
        return None


def repartir_lignes(n: int, lignes: int, texte: str) -> list[int]:
    if lignes < 2 or n <= 2 or len(texte) <= 11:
        return [n]
    return [(n + 1) // 2, n // 2]


def apparition(sel: str, entree: str, t: float, dispo: float, n_car: int = 0) -> list[str]:
    """Les réglages GSAP de l'arrivée de `sel` à l'instant t, jamais plus longue que sa fenêtre."""
    def d(base):
        return round(min(base, max(0.05, dispo * 0.7)), 3)
    a = {
        "pop": ("{scale: 0.55, opacity: 0}", "{scale: 1, opacity: 1, duration: %s, ease: 'back.out(2.6)'}" % d(0.18)),
        "rebond": ("{y: 46, scale: 0.86, opacity: 0}", "{y: 0, scale: 1, opacity: 1, duration: %s, ease: 'back.out(3.2)'}" % d(0.3)),
        "glisse": ("{y: 34, opacity: 0}", "{y: 0, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.22)),
        "fondu": ("{opacity: 0}", "{opacity: 1, duration: %s, ease: 'power1.out'}" % d(0.2)),
        "flou": ("{opacity: 0, filter: 'blur(16px)'}", "{opacity: 1, filter: 'blur(0px)', duration: %s, ease: 'power2.out'}" % d(0.26)),
        "zoom": ("{scale: 1.4, opacity: 0}", "{scale: 1, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.2)),
        "aucune": ("{opacity: 0}", "{opacity: 1, duration: 0.001}"),
    }
    if entree == "machine" and n_car:
        pas = round(min(0.05, dispo * 0.75 / n_car), 4)
        return [f"tl.fromTo('{sel} .c', {{opacity: 0}}, {{opacity: 1, duration: 0.001, stagger: {pas}}}, {t:.3f});"]
    de, vers = a.get(entree, a["aucune"])
    return [f"tl.fromTo('{sel}', {de}, {vers}, {t:.3f});"]


def mots_html(toks, fort_i, avec_h, machine):
    out = []
    for q, t in enumerate(toks):
        nu = t[1:-1] if t.startswith("*") and t.endswith("*") and len(t) > 2 else t
        w = html.escape(nu)
        b = "".join(f'<span class="c">{html.escape(c)}</span>' for c in nu) if machine else w
        # La version allumée recouvre le mot (et sa boîte déborde un peu) : voulu, dit au contrôle.
        h = f'<span class="h" data-layout-allow-overlap data-layout-allow-overflow>{w}</span>' if avec_h else ""
        dessous = " data-layout-allow-occlusion" if avec_h else ""
        out.append(f'<span class="w w{q}{" k" if q == fort_i else ""}"><span class="b"{dessous}>{b}</span>{h}</span>')
    return out


def appliquer(s: dict, look: dict) -> None:
    import sections
    reel = REEL
    caps_f = reel / "compositions/captions.html"
    origine_f = reel / "work/captions.origine.html"
    actuel = caps_f.read_text(encoding="utf-8")
    if MARQUEUR in actuel:
        if not origine_f.exists():
            sys.exit("ERREUR : work/captions.origine.html manque. Relance python3 tools/montage_captions.py --write.")
        src = origine_f.read_text(encoding="utf-8")
    else:
        src = actuel
        origine_f.parent.mkdir(exist_ok=True)
        origine_f.write_text(src, encoding="utf-8")
    rows = list(LIGNE_CAP.finditer(src))
    if not rows:
        sys.exit("ERREUR : aucun sous-titre dans compositions/captions.html : lance d'abord "
                 "python3 tools/montage_captions.py --write.")

    tokens = (reel / "brand/tokens.css").read_text(encoding="utf-8")
    taille = float(re.search(r"--brand-cap-size:\s*([\d.]+)px", tokens).group(1))
    m_lh = re.search(r"\n\.cap \{[^}]*line-height:\s*([\d.]+)", tokens, re.S)
    interligne = float(m_lh.group(1)) if m_lh else 1.35
    fps = getattr(sections, "FPS", 30)
    mots_f = sections.CUTS_PATH.with_name(sections.CUTS_PATH.name.replace("_cuts.json", "_words.json"))
    mots = [w for w in json.loads(mots_f.read_text(encoding="utf-8")) if any(c.isalnum() for c in w["w"])] \
        if mots_f.exists() else []
    if not mots:
        print(f"  ⚠ {mots_f.name} absent : mots répartis à parts égales (lance tools/build_words.py pour les caler sur la voix).")

    mesure = mesureur()
    mode, entree = look["mode"], look["entree"]
    allume, fort = look.get("allume"), look.get("fort")
    machine = entree == "machine" and mode in ("bloc", "karaoke")
    n_allume = len((allume or {}).get("tour") or [None])
    n_fort = len((fort or {}).get("tour") or [None])
    lignes_voulues = int(look.get("lignes") or 1)

    sorties, tweens, j = [], [], 0
    for m in rows:
        indent, idx, top, st, du, piste, inner = m.groups()
        debut, fin = float(st), float(st) + float(du)
        texte = html.unescape(inner)
        toks = [t for t in (x.strip(".,;:!?«»\"") for x in texte.split()) if t]
        if not toks:
            continue
        temps = temps_des_mots(toks, debut, fin, mots) if mots else \
            [debut + (fin - debut) * q / len(toks) for q in range(len(toks))]
        fort_i = mot_fort(toks) if fort else None
        if mode == "un-mot":
            morceaux = []
            for q, (tok, tm) in enumerate(zip(toks, temps)):
                a = round(max(tm, debut) * fps)
                b = round((temps[q + 1] if q + 1 < len(toks) else fin) * fps)
                if b - a < 2 and q + 1 < len(toks):
                    continue
                morceaux.append(([tok], [a / fps], a, max(b, a + 2), q == fort_i))
        else:
            a, b = round(debut * fps), round(fin * fps)
            morceaux = [(toks, temps, a, b, None)]
        for mtoks, mtemps, a, b, est_fort in morceaux:
            cid = f"cap-{idx}" if len(morceaux) == 1 else f"cap-{idx}-{len(sorties)}"
            t0 = a / fps
            dispo = (b - a) / fps
            fi = (0 if est_fort else None) if mode == "un-mot" else fort_i
            reparti = repartir_lignes(len(mtoks), lignes_voulues, " ".join(mtoks))
            avec_h = bool(allume) and mode in ("karaoke", "mot-a-mot")
            spans = mots_html(mtoks, fi, avec_h, machine)
            parts, pos = [], 0
            for n in reparti:
                parts.append(" ".join(spans[pos:pos + n]))
                pos += n
            y = int(top) + (round(taille * interligne / 2) if len(reparti) == 2 else 0)
            classes = f"cap clip st a{j % n_allume} f{j % n_fort}"
            depart = "0" if a == 0 else f"{(a - 0.01) / fps:.5f}"
            # Un mot géant ou une ligne plus large que l'image (marges comprises) : la taille baisse pour ce sous-titre.
            reduit = ""
            if mesure:
                largeurs, pos = [], 0
                for n in reparti:
                    morceau = [x.strip("*") for x in mtoks[pos:pos + n]]
                    w = mesure(" ".join(morceau)) * (1 + (look.get("espacement") or 0) * 0.6)
                    if fi is not None and pos <= fi < pos + n and fort.get("type") in ("police", "grossit"):
                        w += mesure(mtoks[fi].strip("*")) * (float(fort.get("echelle", 1.3)) - 1)
                    largeurs.append(w + (taille * 0.8 if look.get("plaque") else 0))
                    pos += n
                if max(largeurs) > LARGEUR_MAX:
                    reduit = f" font-size:{taille * LARGEUR_MAX / max(largeurs):.1f}px;"
            sorties.append(
                f'{indent}<div class="{classes}" id="{cid}" style="top:{y}px;{reduit}" data-texte="{html.escape(" ".join(mtoks), quote=True)}" '
                f'data-start="{depart}" data-duration="{(b - a) / fps:.5f}" data-track-index="{piste}">'
                f'<span class="in"><span class="t">' + "<br>".join(parts) + "</span></span></div>")
            sel = f"#captions #{cid}"
            if mode in ("bloc", "karaoke", "un-mot"):
                if entree != "aucune":
                    tweens += apparition(f"{sel} .in", entree, t0, dispo, sum(len(t) for t in mtoks))
            else:  # mot-a-mot : chaque mot arrive quand il est dit et reste
                for q, t in enumerate(mtemps):
                    fen = (mtemps[q + 1] if q + 1 < len(mtemps) else b / fps) - t
                    tweens += apparition(f"{sel} .w{q}", entree if entree != "machine" else "fondu", max(t, t0), fen)
            if avec_h:
                garde = bool(allume.get("garde"))
                for q, t in enumerate(mtemps):
                    on = max(t, t0)
                    tweens.append(f"tl.fromTo('{sel} .w{q} .h', {{opacity: 0}}, {{opacity: 1, duration: 0.001, immediateRender: false}}, {on:.3f});")
                    if allume.get("type") == "grossit":
                        tweens.append(f"tl.to('{sel} .w{q}', {{scale: {allume.get('echelle', 1.07)}, duration: 0.08, ease: 'power2.out'}}, {on:.3f});")
                    if q + 1 < len(mtemps) and not garde:
                        off = mtemps[q + 1]
                        tweens.append(f"tl.set('{sel} .w{q} .h', {{opacity: 0}}, {off:.3f});")
                        if allume.get("type") == "grossit":
                            tweens.append(f"tl.to('{sel} .w{q}', {{scale: 1, duration: 0.08, ease: 'power2.out'}}, {off:.3f});")
            # Petit saut du mot fort quand il est dit : seulement d'un bloc (ailleurs, le mot a déjà son arrivée).
            if fi is not None and fort and fort.get("pop") and mode == "bloc" and fort.get("type") != "grossit":
                t_fort = max(mtemps[fi], t0 + 0.2)
                if t_fort < b / fps - 0.1:
                    saut = round(taille * 0.16)
                    tweens.append(f"tl.to('{sel} .w{fi}', {{keyframes: [{{y: -{saut}, scale: 1.05, duration: 0.1, ease: 'power2.out'}}, "
                                  f"{{y: 0, scale: 1, duration: 0.16, ease: 'power2.in'}}]}}, {t_fort:.3f});")
            j += 1

    out = src[:rows[0].start()] + "\n".join(sorties) + src[rows[-1].end():]
    out = out.replace('<div id="captions" ', f'<div id="captions" {MARQUEUR}{s["n"]}" ', 1)
    out = out.replace("    </style>", css_du_look(s, look, taille) + "    </style>", 1)
    tl = ("      window.__timelines = window.__timelines || {};\n"
          "      (function () {\n"
          "        var tl = gsap.timeline({ paused: true });\n"
          + "".join(f"        {t}\n" for t in tweens)
          + "        window.__timelines[\"captions\"] = tl;\n"
          "      })();\n")
    out, n = re.subn(r"      window\.__timelines = window\.__timelines \|\| \{\};\n.*?\n    </script>",
                     lambda _: tl + "    </script>", out, count=1, flags=re.S)
    if n != 1:
        sys.exit("ERREUR : timeline des sous-titres introuvable dans compositions/captions.html.")
    caps_f.write_text(out, encoding="utf-8")
    print(f"Sous-titres n°{s['n']} « {s['nom']} » ({mode}, entrée {entree}) : {len(sorties)} sous-titres, "
          f"{len(tweens)} réglages d'animation -> compositions/captions.html")


def restaurer() -> None:
    caps_f = REEL / "compositions/captions.html"
    origine_f = REEL / "work/captions.origine.html"
    if caps_f.exists() and MARQUEUR in caps_f.read_text(encoding="utf-8") and origine_f.exists():
        caps_f.write_text(origine_f.read_text(encoding="utf-8"), encoding="utf-8")
        print("Aucun style de sous-titres choisi : sous-titres remis d'un bloc (sortie de montage_captions.py).")
    else:
        print("Aucun style de sous-titres choisi (visual.captionsStyle) : rien à faire.")


def main() -> None:
    p = argparse.ArgumentParser(description="Styles de sous-titres du catalogue.")
    p.add_argument("--liste", action="store_true")
    p.add_argument("--choisir", nargs="?", const="", metavar="N")
    p.add_argument("--retouche", nargs="+", metavar="CLE=VALEUR")
    p.add_argument("--sans", action="store_true")
    p.add_argument("--maison", action="store_true")
    a = p.parse_args()
    if a.liste:
        return lister()
    if a.choisir is not None:
        return choisir(a.choisir or None, a.maison)
    if a.retouche:
        return retoucher(a.retouche, a.maison)
    if a.sans:
        return retirer(a.maison)
    if REEL is None:
        sys.exit("ERREUR : lance l'application du style depuis le dossier du Reel (reels/<nom>/tools/…).")
    v = config().get("visual") or {}
    if v.get("captionsStyle") in (None, "", "aucun"):
        return restaurer()
    if visual_de(fichier_reel()).get("captionsStyle") in (None, ""):
        # Style gardé pour toutes ses vidéos, pas encore posé sur ce Reel (nouveau Reel, ou réglages
        # d'un style de montage copiés par-dessus) : sa police et sa taille d'abord, puis le découpage.
        materialiser(v["captionsStyle"], v.get("captionsLook") or {})
        synchro()
        sys.exit(f"Style de sous-titres n°{v['captionsStyle']} (gardé pour toutes ses vidéos) posé sur ce Reel. "
                 "Relance python3 tools/montage_captions.py --write, puis ce script.")
    s = style_numero(v["captionsStyle"])
    appliquer(s, look_du_style(s, v.get("captionsLook") or {}))


if __name__ == "__main__":
    main()
