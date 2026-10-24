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
from sous_titres_effets import (EMOJI, ENTREES, REVELES, apparition, css_couleur, css_du_look,  # noqa: E402
                               entree_du, mots_html, particules, repartir_lignes, sortie)

CATALOGUE = MAISON / "templates/styles-sous-titres.json"
MODES = ("bloc", "karaoke", "mot-a-mot", "un-mot", "ligne")
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
    """Le style que le client demande : son numéro dans la galerie (ou son slug)."""
    for s in catalogue():
        if str(n).strip() in (str(s["n"]), s["slug"]):
            return s
    sys.exit(f"ERREUR : pas de style de sous-titres « {n} » (--liste pour les voir).")


def style_reglage(v) -> dict | None:
    """Le style gardé dans des réglages (visual.captionsStyle) : son slug ; un numéro écrit avant la
    renumérotation du 24/10/2026 (galerie rangée par famille) se relit par `avant`, puis par `n`."""
    if v in (None, "", "aucun"):
        return None
    styles = catalogue()
    s = next((x for x in styles if x["slug"] == str(v)), None)
    if s is None and str(v).isdigit():
        s = next((x for x in styles if x.get("avant") == int(v)), None) or next((x for x in styles if x["n"] == int(v)), None)
    if s is None:
        sys.exit(f"ERREUR : style de sous-titres « {v} » inconnu dans les réglages (--liste pour les voir).")
    return s


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


def materialiser(s: dict, look: dict) -> None:
    """Les réglages du style n°n (police, taille, casse…) dans le reel.config.json du Reel, avec ses
    retouches de taille et de police. Les réglages de sous-titres d'avant tombent ; la police d'accent
    du client reste, sauf si c'est celle d'un style de sous-titres d'avant."""
    f = fichier_reel()
    base = {k: s["visual"][k] for k in CLES_STYLE if k in s["visual"]}
    if look.get("taille"):
        base["captionsSize"] = int(look["taille"])
    if look.get("police"):
        base["fontCaptions"] = look["police"]
    retire = [k for k in CLES_STYLE if k not in base and k != "fontAccent"]
    avant = visual_de(f)
    if "fontAccent" not in base and avant.get("captionsStyle") not in (None, "", "aucun"):
        ancien = style_reglage(avant["captionsStyle"])
        if ancien and ancien["visual"].get("fontAccent") == avant.get("fontAccent"):
            retire.append("fontAccent")
    ecrire_visual(f, {**base, "captionsStyle": s["slug"]}, retire)


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
        return val if val in ENTREES + REVELES else None
    if cle == "lignes":
        return int(val) if str(val) in ("1", "2") else None
    if cle == "taille":
        return int(val) if str(val).isdigit() and 30 <= int(val) <= 160 else None
    if cle == "police":
        return val if val in polices_livrees() else None
    return None


def choisir(n, maison: bool) -> None:
    if n is None:
        s = style_reglage(visual_de(fichier_maison()).get("captionsStyle"))
        if s is None:
            sys.exit("ERREUR : aucun style de sous-titres gardé pour toutes ses vidéos : donne un numéro (--choisir 7).")
    else:
        s = style_numero(n)
    look_maison = visual_de(fichier_maison()).get("captionsLook") or {}
    if maison:
        ecrire_visual(fichier_maison(), {"captionsStyle": s["slug"]}, retire=["captionsLook"])
        look_maison = {}
    if REEL is not None:
        # Un choix pour ce Reel seul masque les retouches de la maison (faites pour un autre style).
        reel_look = {} if (maison or not look_maison) else {"captionsLook": {}}
        ecrire_visual(fichier_reel(), reel_look, retire=["captionsLook"])
        materialiser(s, {} if not maison else look_maison)
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
        s = style_reglage((config().get("visual") or {}).get("captionsStyle"))
        if s is not None:
            materialiser(s, (config().get("visual") or {}).get("captionsLook") or {})
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
        s = style_reglage(avant.get("captionsStyle")) if avant.get("captionsStyle") != "aucun" else None
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
            if cle == "ombre":
                look.pop("ombres", None)
        elif cle == "allume":
            look["allume"] = {**(look["allume"] or {"type": "couleur"}), "couleur": val, "tour": None}
        elif cle == "boite":
            look["allume"] = {**(look["allume"] or {}), "type": "boite", "fond": val, "tour": None}
        elif cle == "plaque":
            look["plaque"] = None if val == "aucune" else {**(look["plaque"] or {"arrondi": 12, "marge": "0.1em 0.35em"}), "fond": val}
        elif cle == "fort":
            look["fort"] = {**(look["fort"] or {"type": "couleur"}), "couleur": val, "tour": None}
    look["mode"] = look.get("mode") if look.get("mode") in MODES else "bloc"
    e = look.get("entree")
    valides = ENTREES + REVELES
    if isinstance(e, list):
        look["entree"] = [x for x in e if x in valides] or "aucune"
    else:
        look["entree"] = e if e in valides else "aucune"
    return look


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


def mots_forts(toks, fort: dict | None) -> list[int]:
    """Les mots forts d'un sous-titre : un seul par défaut (le marqué, sinon le chiffre ou le plus
    long) ; `nombre` en demande plus (« tous » : chaque mot plein), les marqués d'abord."""
    if not fort:
        return []
    nombre = fort.get("nombre", 1)
    if nombre == 1:
        i = mot_fort(toks)
        return [] if i is None else [i]
    marques = [i for i, t in enumerate(toks) if t.startswith("*") and t.endswith("*") and len(t) > 2]
    pleins = [i for i, t in enumerate(toks) if normaliser(t) not in FAIBLES and len(normaliser(t)) >= 3]
    if nombre == "tous":
        return sorted(set(marques) | set(pleins))
    choisis = marques or sorted(pleins, key=lambda i: -len(normaliser(toks[i])))
    return sorted(choisis[:int(nombre)])


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
    mode = look["mode"]
    allume, fort, plaque, ligne = look.get("allume"), look.get("fort"), look.get("plaque"), look.get("ligne")
    n_allume = len((allume or {}).get("tour") or [None])
    n_fort = len((fort or {}).get("tour") or [None])
    lignes_voulues = int(look.get("lignes") or 1)
    coupe = int(look.get("coupe") or 11)
    lignes_par_t = bool(plaque and plaque.get("par") == "ligne" and plaque.get("lignes"))
    lignes_l = mode == "ligne" or bool(look.get("lignes_couleurs"))
    inclinaisons = look.get("inclinaisons") or []
    karaoke_h = bool(allume) and allume.get("type") != "opacite"

    sorties, tweens, j = [], [], 0
    for m in rows:
        indent, idx, top, st, du, piste, inner = m.groups()
        debut, fin = float(st), float(st) + float(du)
        texte = html.unescape(inner)
        emojis = "".join(EMOJI.findall(texte)) if look.get("emoji") else ""
        if look.get("emoji"):
            texte = EMOJI.sub(" ", texte)
        toks = [t for t in (x.strip(".,;:!?«»\"") for x in texte.split()) if t]
        if not toks:
            continue
        temps = temps_des_mots(toks, debut, fin, mots) if mots else \
            [debut + (fin - debut) * q / len(toks) for q in range(len(toks))]
        forts = mots_forts(toks, fort)
        if mode == "un-mot":
            morceaux = []
            for q, (tok, tm) in enumerate(zip(toks, temps)):
                a = round(max(tm, debut) * fps)
                b = round((temps[q + 1] if q + 1 < len(toks) else fin) * fps)
                if b - a < 2 and q + 1 < len(toks):
                    continue
                morceaux.append(([tok], [a / fps], a, max(b, a + 2), q in forts, emojis if q + 1 == len(toks) else ""))
        else:
            a, b = round(debut * fps), round(fin * fps)
            morceaux = [(toks, temps, a, b, None, emojis)]
        for mtoks, mtemps, a, b, est_fort, memo in morceaux:
            cid = f"cap-{idx}" if len(morceaux) == 1 else f"cap-{idx}-{len(sorties)}"
            t0 = a / fps
            dispo = (b - a) / fps
            fis = ([0] if est_fort else []) if mode == "un-mot" else forts
            fi = fis[0] if fis else None
            entree = entree_du(look, j)
            reparti = repartir_lignes(len(mtoks), lignes_voulues, " ".join(mtoks), coupe, look.get("coupure"))
            avec_h = karaoke_h and mode in ("karaoke", "mot-a-mot")
            spans = mots_html(mtoks, fis if len(fis) != 1 else fi, avec_h, entree == "machine" and mode in ("bloc", "karaoke"),
                              flash=entree == "flash", particules_cfg=(fort or {}).get("particules"),
                              cycle_fort=bool((fort or {}).get("par_mot")))
            parts, pos = [], 0
            for i, n in enumerate(reparti):
                part = " ".join(spans[pos:pos + n])
                if lignes_l:
                    couleur = ""
                    fixes = look.get("lignes_couleurs") or []
                    if fixes and fixes[j % len(fixes)][0] == i:
                        couleur = f' style="color:{css_couleur(fixes[j % len(fixes)][1])}"'
                    part = f'<span class="l l{i}"{couleur}>{part}</span>'
                if lignes_par_t:
                    part = f'<span class="t t{i}">{part}</span>'
                parts.append(part)
                pos += n
            y = int(top) + (round(taille * interligne / 2) if len(reparti) == 2 else 0)
            classes = f"cap clip st a{j % n_allume} f{j % n_fort}"
            depart = "0" if a == 0 else f"{(a - 0.01) / fps:.5f}"
            # Un mot géant ou une ligne plus large que l'image (marges comprises) : la taille baisse pour ce sous-titre.
            echelle = float(look.get("un_mot_echelle") or 1) if len(mtoks) == 1 and mode != "un-mot" else 1
            reduit = f" font-size:{taille * echelle:.1f}px;" if echelle != 1 else ""
            if mesure:
                largeurs, pos = [], 0
                for n in reparti:
                    morceau = [x.strip("*") for x in mtoks[pos:pos + n]]
                    w = mesure(" ".join(morceau)) * (1 + (look.get("espacement") or 0) * 0.6)
                    for f in fis:
                        if pos <= f < pos + n and fort.get("type") in ("police", "grossit", "agrandi"):
                            w += mesure(mtoks[f].strip("*")) * (float(fort.get("echelle", 1.3)) - 1)
                    largeurs.append(w * echelle + (taille * 0.8 if plaque else 0))
                    pos += n
                if max(largeurs) > LARGEUR_MAX:
                    reduit = f" font-size:{taille * echelle * LARGEUR_MAX / max(largeurs):.1f}px;"
            penche = f' style="rotate:{inclinaisons[j % len(inclinaisons)]}deg"' if inclinaisons and inclinaisons[j % len(inclinaisons)] else ""
            corps = "<br>".join(parts) if lignes_par_t else '<span class="t">' + "<br>".join(parts) + "</span>"
            emo = f'<span class="emo" data-layout-allow-overflow>{html.escape(memo)}</span>' if memo else ""
            sorties.append(
                f'{indent}<div class="{classes}" id="{cid}" style="top:{y}px;{reduit}" data-texte="{html.escape(" ".join(mtoks), quote=True)}" '
                f'data-start="{depart}" data-duration="{(b - a) / fps:.5f}" data-track-index="{piste}">'
                f'<span class="in"{penche}>' + corps + emo + "</span></div>")
            sel = f"#captions #{cid}"
            n_car = sum(len(t) for t in mtoks)
            if mode in ("bloc", "karaoke", "un-mot", "ligne"):
                if entree != "aucune":
                    tweens += apparition(f"{sel} .in", entree, t0, dispo, n_car, look, j, len(mtoks))
            else:  # mot-a-mot : chaque mot arrive quand il est dit et reste
                if look.get("bloc"):
                    tweens += apparition(f"{sel} .in", look["bloc"], t0, dispo, n_car, look, j, len(mtoks))
                for q, t in enumerate(mtemps):
                    fen = (mtemps[q + 1] if q + 1 < len(mtemps) else b / fps) - t
                    tweens += apparition(f"{sel} .w{q}", entree if entree != "machine" else "fondu", max(t, t0), fen, look=look)
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
            if allume and allume.get("type") == "opacite" and mode in ("karaoke", "mot-a-mot"):
                for q, t in enumerate(mtemps):
                    tweens.append(f"tl.to('{sel} .w{q} .b', {{opacity: 1, duration: {allume.get('duree', 0.1)}, ease: 'power1.out'}}, {max(t, t0):.3f});")
            # Petit saut du mot fort quand il est dit : seulement d'un bloc (ailleurs, le mot a déjà son arrivée).
            if fi is not None and fort and fort.get("pop") and mode == "bloc" and fort.get("type") != "grossit":
                t_fort = max(mtemps[fi], t0 + 0.2)
                if t_fort < b / fps - 0.1:
                    saut = round(taille * 0.16)
                    tweens.append(f"tl.to('{sel} .w{fi}', {{keyframes: [{{y: -{saut}, scale: 1.05, duration: 0.1, ease: 'power2.out'}}, "
                                  f"{{y: 0, scale: 1, duration: 0.16, ease: 'power2.in'}}]}}, {t_fort:.3f});")
            if fort and fort.get("particules"):
                for f in fis:
                    tweens += particules(f"{sel} .w{f}", max(mtemps[f], t0) + 0.02, fort, taille)
            if mode == "ligne" and ligne:
                tweens += lignes_actives(sel, reparti, mtemps, t0, b / fps, ligne, j, look.get("couleur") or "#ffffff")
            if memo:
                tweens.append(f"tl.fromTo('{sel} .emo', {{scale: 0, opacity: 0}}, {{scale: 1, opacity: 1, duration: {min(0.2, dispo * 0.6):.3f}, "
                              f"ease: 'back.out(2.5)'}}, {t0 + min(0.06, dispo * 0.2):.3f});")
            if look.get("sortie") and dispo > 0.4:
                tweens += sortie(f"{sel} .in", look["sortie"], b / fps, look)
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
    nom_entree = "/".join(look["entree"]) if isinstance(look["entree"], list) else look["entree"]
    print(f"Sous-titres n°{s['n']} « {s['nom']} » ({mode}, entrée {nom_entree}) : {len(sorties)} sous-titres, "
          f"{len(tweens)} réglages d'animation -> compositions/captions.html")


def lignes_actives(sel: str, reparti: list[int], mtemps: list[float], t0: float, fin: float, ligne: dict, j: int,
                   base: str) -> list[str]:
    """Karaoké par ligne : la ligne en cours de lecture prend sa couleur (à tour de rôle d'un
    sous-titre à l'autre), sa graisse et grossit un peu ; elle reprend son allure à la suivante."""
    tour = ligne.get("tour") or [ligne.get("active") or "#ffffff"]
    active = css_couleur(tour[j % len(tour)])
    repos = css_couleur(ligne.get("inactive") or base)
    duree = float(ligne.get("transition", 0))
    out, pos, debuts = [], 0, []
    for n in reparti:
        debuts.append(max(mtemps[pos], t0))
        pos += n
    debuts[0] = t0
    for i, on in enumerate(debuts):
        off = debuts[i + 1] if i + 1 < len(debuts) else None
        vers = f"color: '{active}', scale: {ligne.get('echelle', 1)}"
        repli = f"color: '{repos}', scale: 1"
        if ligne.get("graisse_active"):
            vers += f", fontWeight: {ligne['graisse_active']}"
            repli += f", fontWeight: {ligne.get('graisse_inactive', 400)}"
        if duree:
            out.append(f"tl.to('{sel} .l{i}', {{{vers}, duration: {duree}}}, {on:.3f});")
            if off is not None and off < fin - 0.01:
                out.append(f"tl.to('{sel} .l{i}', {{{repli}, duration: {duree}}}, {off:.3f});")
        else:
            out.append(f"tl.set('{sel} .l{i}', {{{vers}}}, {on:.3f});")
            if off is not None and off < fin - 0.01:
                out.append(f"tl.set('{sel} .l{i}', {{{repli}}}, {off:.3f});")
    return out


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
    s = style_reglage(v.get("captionsStyle"))
    if s is None:
        return restaurer()
    if visual_de(fichier_reel()).get("captionsStyle") in (None, ""):
        # Style gardé pour toutes ses vidéos, pas encore posé sur ce Reel (nouveau Reel, ou réglages
        # d'un style de montage copiés par-dessus) : sa police et sa taille d'abord, puis le découpage.
        materialiser(s, v.get("captionsLook") or {})
        synchro()
        sys.exit(f"Style de sous-titres n°{s['n']} « {s['nom']} » (gardé pour toutes ses vidéos) posé sur ce Reel. "
                 "Relance python3 tools/montage_captions.py --write, puis ce script.")
    appliquer(s, look_du_style(s, v.get("captionsLook") or {}))


if __name__ == "__main__":
    main()
