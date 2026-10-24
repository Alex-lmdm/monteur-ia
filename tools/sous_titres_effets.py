#!/usr/bin/env python3
"""EFFETS DES STYLES DE SOUS-TITRES : l'habillage (CSS) et les animations (timeline GSAP) d'un look.

Module de tools/sous_titres.py, qui choisit le style, lit la voix et assemble compositions/captions.html.
Ici, rien ne lit ni n'écrit de fichier : un look (catalogue + retouches) entre, du CSS et des réglages
GSAP sortent. Tout est calé sur des instants absolus de la timeline `captions` (tl.set, tl.fromTo,
tl.to) : le rendu est déterministe, image par image, comme le reste du montage.

Les programmes d'animation, par leur nom dans le catalogue (templates/styles-sous-titres.json) :
- arrivée d'un sous-titre (`entree`, ou `bloc` quand les mots arrivent un à un ; une liste = une
  roue, un programme par sous-titre à tour de rôle) : voir ENTREES ;
- arrivée d'un mot (`entree` en mode mot-a-mot ou un-mot) : voir ENTREES et REVELES ;
- sortie (`sortie`) : resserre, fondu.
"""
from __future__ import annotations

import html
import math
import re

COULEURS_NOMMEES = {"accent": "var(--brand-accent)", "texte": "var(--brand-text)", "fond": "var(--brand-bg)"}
ENTREES = ("aucune", "pop", "rebond", "glisse", "fondu", "flou", "zoom", "machine",
           "pop-tenu", "jaillit", "zoom-lent", "glisse-zoom", "resserre", "ressort-lettres", "tangue",
           "tangue-mini", "tangue-zoom", "bascule-droite", "bascule-gauche", "pivote", "rebond-lent",
           "fondu-doux", "glisse-gauche", "clignote", "mots-tapes", "ecrase", "glitch",
           "slam-gauche", "slam-droite", "slam-haut", "vacille")
# Arrivées qui n'existent que pour un mot (mode mot-a-mot).
REVELES = ("glisse-vite", "flash", "balayage")
# Les emojis du découpage : pictogrammes, symboles et flèches en couleur, sélecteurs et liaisons compris.
EMOJI = re.compile("[\u00A9\u00AE\u203C\u2049\u2122\u2139\u2194-\u21AA\u2300-\u23FF\u24C2\u25A0-\u25FF"
                   "\u2600-\u27BF\u2934\u2935\u2B00-\u2BFF\u3030\u303D\u3297\u3299\U0001F000-\U0001FAFF\uFE0F\u200D]+")


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


def css_ombres(couches) -> str:
    """Une pile d'ombres du catalogue, [décalage x, décalage y, flou, couleur] en em (« propre » =
    la couleur du mot) : halos, reliefs en escalier, lueurs."""
    out = []
    for dx, dy, flou, c in couches:
        c = "currentColor" if c == "propre" else css_couleur(c)
        out.append(f"{dx:g}em {dy:g}em {flou:g}em {c}")
    return ", ".join(out) or "none"


def entree_du(look: dict, j: int) -> str:
    """Le programme d'arrivée du sous-titre n°j : une liste fait une roue, un par sous-titre."""
    e = look.get("entree")
    if isinstance(e, list):
        return e[j % len(e)] if e else "aucune"
    return e or "aucune"


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
    ombre = css_ombres(look["ombres"]) if look.get("ombres") else css_ombre(look.get("ombre"), taille)
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
    if look.get("italique"):
        lignes.append("#captions .cap.st { font-style: italic; }")
    if look.get("minuscules"):
        lignes.append("#captions .cap.st { text-transform: lowercase; }")
    if look.get("degrade"):
        haut, bas = (css_couleur(c) for c in look["degrade"])
        lignes.append(f"#captions .cap.st .w:not(.k) .b {{ background: linear-gradient(180deg, {haut} 15%, {bas} 85%);"
                      " -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }")
    if plaque:
        bord = f"border-radius: {plaque.get('arrondi', 12)}px; padding: {plaque.get('marge', '0.1em 0.35em')};"
        if plaque.get("par") == "ligne":
            lignes.append("#captions .cap.st .t { background: var(--st-plaque); " + bord
                          + " -webkit-box-decoration-break: clone; box-decoration-break: clone; }")
            for i, l in enumerate(plaque.get("lignes") or []):
                regle = "display: inline-block;"
                if l.get("fond"):
                    regle += f" background: {css_couleur(l['fond'])};"
                if l.get("texte"):
                    regle += f" color: {css_couleur(l['texte'])};"
                if l.get("rotation"):
                    regle += f" rotate: {l['rotation']}deg;"
                if l.get("decalage"):
                    regle += f" margin-top: {l['decalage']}em;"
                lignes.append(f"#captions .cap.st .t.t{i} {{ {regle} }}")
        else:
            lignes.append("#captions .cap.st .in { background: var(--st-plaque); " + bord + " }")
    if allume:
        if allume.get("type") == "opacite":
            lignes.append(f"#captions .cap.st .w .b {{ opacity: {allume.get('depart', 0.3)}; }}")
        else:
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
    ligne = look.get("ligne")
    if look.get("mode") == "ligne" and ligne:
        lignes.append("#captions .cap.st .l { display: inline-block; transform-origin: 50% 60%;"
                      + (f" color: {css_couleur(ligne['inactive'])};" if ligne.get("inactive") else "")
                      + (f" font-weight: {ligne['graisse_inactive']};" if ligne.get("graisse_inactive") else "") + " }")
    if fort:
        # La couleur du mot fort tourne d'un sous-titre à l'autre, ou d'un mot fort à l'autre (`par_mot`).
        dessus = " -webkit-text-fill-color: currentColor; background: none;" if look.get("degrade") else ""
        for i in range(len((fort.get("tour") or [None]))):
            cible = f".w.k.k{i}" if fort.get("par_mot") else f".cap.st.f{i} .w.k"
            cible = cible if cible.startswith(".cap") else f".cap.st {cible}"
            lignes.append(f"#captions {cible} .b {{ color: var(--st-fort-{i});{dessus} }}")
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
        elif t == "graisse":
            lignes.append(f"#captions .cap.st .w.k .b {{ font-weight: {fort.get('graisse', 900)}; }}")
        elif t == "agrandi":
            lignes.append(f"#captions .cap.st .w.k .b {{ font-size: {fort.get('echelle', 1.4)}em; line-height: 1; }}")
        if fort.get("opacite"):
            lignes.append(f"#captions .cap.st .w.k .b {{ opacity: {fort['opacite']}; }}")
        if fort.get("lueur"):
            lignes.append("#captions .cap.st .w.k .b { text-shadow: 0 0 0.16em currentColor, 0 0 0.42em currentColor; }")
        if fort.get("ombres"):
            lignes.append(f"#captions .cap.st .w.k .b {{ text-shadow: {css_ombres(fort['ombres'])}; }}")
        if fort.get("particules"):
            lignes.append("#captions .cap.st .pt { position: absolute; left: 50%; top: 50%; width: 0.16em; height: 0.16em;"
                          " margin: -0.08em 0 0 -0.08em; border-radius: 50%; opacity: 0; }")
    if look.get("emoji"):
        e = look["emoji"]
        place = "bottom: 100%; margin-bottom: 0.1em;" if e.get("pos", "dessus") == "dessus" else "top: 100%; margin-top: 0.1em;"
        lignes.append("#captions .cap.st .in { position: relative; }")
        lignes.append(f"#captions .cap.st .emo {{ position: absolute; left: 0; right: 0; {place} font-size: {e.get('taille', 1.5)}em;"
                      " line-height: 1; -webkit-text-stroke: 0; text-shadow: none; }")
    if "flash" in (look.get("entree"), look.get("revele")):
        lignes.append("#captions .cap.st .fl { position: absolute; left: -0.1em; right: -0.1em; top: 0.08em; bottom: 0.04em;"
                      f" background: {css_couleur(look.get('flash', '#ffffff'))}; border-radius: 0.12em; opacity: 0; }}")
    if entree_du(look, 0) == "machine":
        lignes.append("#captions .cap.st .c { display: inline; }")
    return "\n".join("      " + l.replace("\n", "\n      ") for l in lignes) + "\n"


def repartir_lignes(n: int, lignes: int, texte: str, coupe: int = 11, coupure: str | None = None) -> list[int]:
    """Les mots par ligne : une ligne, ou deux dès que le texte dépasse `coupe` caractères, la 1re
    plus longue ; `coupure` « dernier » met le seul dernier mot à la ligne (dès 4 mots)."""
    if coupure == "dernier":
        return [n - 1, 1] if lignes >= 2 and n >= 4 else [n]
    if lignes < 2 or n <= 2 or len(texte) <= coupe:
        return [n]
    return [(n + 1) // 2, n // 2]


def apparition(sel: str, entree: str, t: float, dispo: float, n_car: int = 0, look: dict | None = None,
               j: int = 0, n_mots: int = 0) -> list[str]:
    """Les réglages GSAP de l'arrivée de `sel` à l'instant t, jamais plus longue que sa fenêtre."""
    def d(base):
        return round(min(base, max(0.05, dispo * 0.7)), 3)
    p = (look or {}).get("params") or {}
    a = {
        "pop": ("{scale: 0.55, opacity: 0}", "{scale: 1, opacity: 1, duration: %s, ease: 'back.out(2.6)'}" % d(0.18)),
        "rebond": ("{y: 46, scale: 0.86, opacity: 0}", "{y: 0, scale: 1, opacity: 1, duration: %s, ease: 'back.out(3.2)'}" % d(0.3)),
        "glisse": ("{y: 34, opacity: 0}", "{y: 0, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.22)),
        "fondu": ("{opacity: 0}", "{opacity: 1, duration: %s, ease: 'power1.out'}" % d(0.2)),
        "flou": ("{opacity: 0, filter: 'blur(16px)'}", "{opacity: 1, filter: 'blur(0px)', duration: %s, ease: 'power2.out'}" % d(0.26)),
        "zoom": ("{scale: 1.4, opacity: 0}", "{scale: 1, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.2)),
        "aucune": ("{opacity: 0}", "{opacity: 1, duration: 0.001}"),
        # Programmes mesurés sur les styles de sous-titres du marché (réglages en `params` du catalogue).
        "pop-tenu": ("{scale: 1}", "{scale: %s, duration: %s, ease: 'power2.out'}" % (p.get("echelle", 1.1), d(0.12))),
        "zoom-lent": ("{scale: %s}" % p.get("de", 1), "{scale: %s, duration: %s, ease: 'none'}" % (p.get("a", 1.12), round(max(dispo, 0.05), 3))),
        "glisse-zoom": ("{y: %s, scale: %s, opacity: 0}" % (p.get("dy", 8), p.get("zoom", 1.04)),
                        "{y: 0, scale: 1, opacity: 1, duration: %s, ease: 'power2.out'}" % d(0.2)),
        "resserre": ("{letterSpacing: '%sem', opacity: 0}" % p.get("de_em", -0.07),
                     "{letterSpacing: '%sem', opacity: 1, duration: %s, ease: 'power2.out'}" % (p.get("a_em", 0), d(0.26))),
        "bascule-droite": ("{x: 80, rotation: 3, opacity: 0}", "{x: 0, rotation: 0, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.22)),
        "bascule-gauche": ("{x: -80, rotation: -3, opacity: 0}", "{x: 0, rotation: 0, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.22)),
        "pivote": ("{scale: 0.7, rotation: 8, opacity: 0}", "{scale: 1, rotation: 0, opacity: 1, duration: %s, ease: 'back.out(2)'}" % d(0.22)),
        "rebond-lent": ("{scale: %s}" % p.get("de", 0.8), "{scale: 1, duration: %s, ease: 'elastic.out(1, 0.45)'}" % d(0.72)),
        "fondu-doux": ("{opacity: %s}" % p.get("de", 0.3), "{opacity: 1, duration: %s, ease: 'power1.out'}" % d(0.17)),
        "glisse-gauche": ("{x: 70, opacity: 0}", "{x: 0, opacity: 1, duration: %s, ease: 'power3.out'}" % d(0.2)),
        "ecrase": ("{scaleX: 1.6, scaleY: 0.8, opacity: 0}", "{scaleX: 1, scaleY: 1, opacity: 1, duration: %s, ease: 'back.out(2.2)'}" % d(0.14)),
        "slam-gauche": ("{x: -320, scale: 1.4, opacity: 0}", "{x: 0, scale: 1, opacity: 1, duration: %s, ease: 'power4.out'}" % d(0.16)),
        "slam-droite": ("{x: 320, scale: 1.4, opacity: 0}", "{x: 0, scale: 1, opacity: 1, duration: %s, ease: 'power4.out'}" % d(0.16)),
        "slam-haut": ("{y: -260, scale: 1.4, opacity: 0}", "{y: 0, scale: 1, opacity: 1, duration: %s, ease: 'power4.out'}" % d(0.16)),
        "glisse-vite": ("{y: 30, opacity: 0}", "{y: 0, opacity: 1, duration: %s, ease: 'power2.out'}" % d(0.1)),
        "balayage": ("{clipPath: 'inset(-20% 100% -20% 0%)'}", f"{{clipPath: 'inset(-20% 0% -20% 0%)', duration: {d(0.18)}, ease: 'power2.out'}}"),
    }
    # Arrivées en plusieurs temps : posées d'un coup, puis enchaînées (keyframes).
    etapes = {
        "jaillit": ("{scale: %s, opacity: 0}" % p.get("de", 0.9),
                    [f"{{scale: {p.get('pic', 1.1)}, opacity: 1, duration: {d(0.1)}, ease: 'power2.out'}}",
                     f"{{scale: 1, duration: {d(0.12)}, ease: 'power2.inOut'}}"]),
        "ressort-lettres": ("{letterSpacing: '-0.23em', opacity: 0}",
                            [f"{{letterSpacing: '0.04em', opacity: 1, duration: {d(0.14)}, ease: 'power2.out'}}",
                             f"{{letterSpacing: '0em', duration: {d(0.12)}, ease: 'power2.inOut'}}"]),
        "tangue": ("{rotation: -7, y: %s, opacity: 0}" % p.get("ampleur", 10),
                   [f"{{rotation: 4, y: -4, opacity: 1, duration: {d(0.12)}, ease: 'power2.out'}}",
                    f"{{rotation: -2, y: 1, duration: {d(0.12)}, ease: 'sine.inOut'}}",
                    f"{{rotation: 0, y: 0, duration: {d(0.14)}, ease: 'sine.out'}}"]),
        "tangue-mini": ("{rotation: -3}",
                        [f"{{rotation: 1.5, duration: {d(0.12)}, ease: 'sine.out'}}",
                         f"{{rotation: 0, duration: {d(0.14)}, ease: 'sine.inOut'}}"]),
        "tangue-zoom": ("{rotation: -5, scale: %s, opacity: 0}" % p.get("de", 0.9),
                        [f"{{rotation: 3, scale: 1.04, opacity: 1, duration: {d(0.12)}, ease: 'power2.out'}}",
                         f"{{rotation: 0, scale: 1, duration: {d(0.16)}, ease: 'sine.inOut'}}"]),
        "clignote": ("{opacity: 0}",
                     [f"{{opacity: 1, duration: {d(0.06)}}}", f"{{opacity: 0.15, duration: {d(0.06)}}}",
                      f"{{opacity: 1, duration: {d(0.08)}}}"]),
        "vacille": ("{opacity: 0}",
                    [f"{{opacity: 0.9, duration: {d(0.04)}}}", f"{{opacity: 0.2, duration: {d(0.05)}}}",
                     f"{{opacity: 1, duration: {d(0.04)}}}", f"{{opacity: 0.5, duration: {d(0.05)}}}",
                     f"{{opacity: 1, duration: {d(0.08)}}}"]),
        "glitch": ("{x: -10, skewX: 10, opacity: 0, textShadow: '-0.07em 0 #ff1f5a, 0.07em 0 #18e4ff'}",
                   [f"{{x: 7, skewX: -7, opacity: 1, duration: {d(0.05)}, ease: 'steps(1)'}}",
                    f"{{x: -4, skewX: 4, duration: {d(0.05)}, ease: 'steps(1)'}}",
                    f"{{x: 2, skewX: 0, textShadow: '-0.03em 0 #ff1f5a, 0.03em 0 #18e4ff', duration: {d(0.05)}, ease: 'steps(1)'}}",
                    f"{{x: 0, duration: {d(0.08)}, clearProps: 'textShadow'}}"]),
    }
    if entree == "machine" and n_car:
        pas = round(min(0.05, dispo * 0.75 / n_car), 4)
        return [f"tl.fromTo('{sel} .c', {{opacity: 0}}, {{opacity: 1, duration: 0.001, stagger: {pas}}}, {t:.3f});"]
    if entree == "mots-tapes" and n_mots:
        pas = round(min(p.get("pas", 0.08), dispo * 0.7 / n_mots), 4)
        return [f"tl.fromTo('{sel} .w', {{opacity: 0}}, {{opacity: 1, duration: 0.001, stagger: {pas}}}, {t:.3f});"]
    if entree == "flash":
        return [f"tl.fromTo('{sel} .fl', {{opacity: 0}}, {{opacity: 1, duration: 0.001}}, {t:.3f});",
                f"tl.set('{sel} .fl', {{opacity: 0}}, {t + 1 / 30:.3f});",
                f"tl.fromTo('{sel} .b', {{opacity: 0}}, {{opacity: 1, duration: {d(0.12)}, ease: 'power1.out'}}, {t:.3f});"]
    if entree in etapes:
        de, suite = etapes[entree]
        return [f"tl.set('{sel}', {de}, {t:.3f});", f"tl.to('{sel}', {{keyframes: [{', '.join(suite)}]}}, {t:.3f});"]
    de, vers = a.get(entree, a["aucune"])
    return [f"tl.fromTo('{sel}', {de}, {vers}, {t:.3f});"]


def sortie(sel: str, programme: str | None, fin: float, look: dict) -> list[str]:
    """La sortie d'un sous-titre, juste avant sa fin (sinon il disparaît net à la coupe suivante)."""
    p = look.get("params") or {}
    t = round(fin - 0.12, 3)
    if programme == "resserre":
        return [f"tl.to('{sel}', {{letterSpacing: '{p.get('de_em', -0.07)}em', opacity: 0, duration: 0.11, ease: 'power2.in'}}, {t:.3f});"]
    if programme == "fondu":
        return [f"tl.to('{sel}', {{opacity: 0, duration: 0.11, ease: 'power1.in'}}, {t:.3f});"]
    return []


def particules(sel: str, t: float, fort: dict, taille: float) -> list[str]:
    """Une gerbe de points qui part du mot fort quand il est dit, dans les couleurs du style."""
    cfg = fort.get("particules") or {}
    n = int(cfg.get("nombre", 10))
    out = []
    for i in range(n):
        ang = 2 * math.pi * i / n + 0.35 * (i % 2)
        r = taille * (1.1 + 0.45 * ((i * 7) % 3))
        out.append(f"tl.fromTo('{sel} .pt{i}', {{x: 0, y: 0, scale: 1, opacity: 1}}, {{x: {r * math.cos(ang):.1f}, "
                   f"y: {r * math.sin(ang):.1f}, scale: 0.3, opacity: 0, duration: 0.55, ease: 'power2.out'}}, {t:.3f});")
    return out


def mots_html(toks, forts, avec_h, machine, flash=False, particules_cfg=None, cycle_fort=False):
    """Un <span class="w"> par mot : sa base (.b), sa version allumée (.h) pour le karaoké, ses
    lettres (.c) pour la machine à écrire, son éclair (.fl), ses points (.pt) pour le mot fort."""
    if not isinstance(forts, (set, list, tuple)):
        forts = set() if forts is None else {forts}
    out, rang = [], 0
    for q, t in enumerate(toks):
        nu = t[1:-1] if t.startswith("*") and t.endswith("*") and len(t) > 2 else t
        w = html.escape(nu)
        b = "".join(f'<span class="c">{html.escape(c)}</span>' for c in nu) if machine else w
        # La version allumée recouvre le mot (et sa boîte déborde un peu) : voulu, dit au contrôle.
        h = f'<span class="h" data-layout-allow-overlap data-layout-allow-overflow>{w}</span>' if avec_h else ""
        dessous = " data-layout-allow-occlusion" if avec_h else ""
        fl = '<span class="fl" data-layout-allow-overlap></span>' if flash else ""
        k = ""
        pts = ""
        if q in forts:
            k = " k" + (f" k{rang}" if cycle_fort else "")
            rang += 1
            if particules_cfg:
                couleurs = particules_cfg.get("couleurs") or ["#ffffff"]
                pts = "".join(f'<span class="pt pt{i}" style="background:{couleurs[i % len(couleurs)]}" data-layout-allow-overlap></span>'
                              for i in range(int(particules_cfg.get("nombre", 10))))
        out.append(f'<span class="w w{q}{k}">{fl}<span class="b"{dessous}>{b}</span>{h}{pts}</span>')
    return out
