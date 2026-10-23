#!/usr/bin/env python3
"""SOUS-TITRES DU STYLE N°01 (Top outils) : un mot géant à la fois, au-dessus de la tête.

Usage (depuis le dossier du Reel, après tools/build_words.py et tools/sections.py réglés) :
    python3 <kit>/outils/sous_titres_style01.py manual [--corrige "réel=Reel,note=Notion"]
        -> écrit MANUAL dans tools/montage_captions.py : un mot par sous-titre, ponctuation
           retirée, un nombre collé au mot qui suit (« 3 outils ») ou au nom qui le précède
           (« Outil 2 »), un mot que Whisper fait partir juste avant une frontière (moins de
           0,12 s) remis dans la prise suivante. Relis la liste affichée (noms propres, mots mal entendus) : --corrige remplace un mot par un autre.
    python3 tools/montage_captions.py --sans <accroche>,<cartes> --write
    python3 <kit>/outils/sous_titres_style01.py finir --sans <accroche>,<cartes>
        -> retouche compositions/captions.html :
           1. un sous-titre que montage_captions.py a posé sur le début d'une section --sans (son
              « snap » à moins de 0,6 s d'une frontière) revient sur son mot et finit à la frontière ;
           2. les mots passent à 1,5 fois la taille réglée (150 px pour 100 : le mot géant de
              l'original ; visual.captionsSize ne monte pas au-delà de 100), chasse serrée
              (-0,025 em) ; un mot trop long pour 920 px est réduit pour tenir, comme l'original.
Relancer « finir » après chaque `montage_captions.py --write` (qui réécrit captions.html).
"""
import html
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "tools"))
import sections  # noqa: E402

FPS = getattr(sections, "FPS", 30)
FACTEUR, LARGEUR_MAX = 1.5, 920
WORDS = json.loads(sections.CUTS_PATH.with_name(sections.CUTS_PATH.name.replace("_cuts.json", "_words.json")).read_text(encoding="utf-8"))


def norme(m):
    m = unicodedata.normalize("NFKD", m.lower())
    return "".join(c for c in m if c.isalnum())


def nettoie(m):
    return re.sub(r'^[«"“(\[]+|[»"”)\].,;:!?…]+$', "", m.strip()).strip()


def manual(corrige):
    takes = sections.TAKES
    mots = []
    for w in WORDS:
        m = nettoie(w["w"])
        if not any(c.isalnum() for c in m):
            continue
        # Prise : celle qui contient le mot, sauf s'il part moins de 0,12 s avant la fin de sa prise.
        k = next((i for i, t in enumerate(takes) if t["start"] - 1e-6 <= w["start"] < t["end"]), len(takes) - 1)
        if k + 1 < len(takes) and takes[k]["end"] - w["start"] < 0.12:
            k += 1
        mots.append((k, corrige.get(m, m)))
    out = [[] for _ in takes]
    i = 0
    while i < len(mots):
        k, m = mots[i]
        nombre = re.fullmatch(r"[0-9][0-9.,]*", m)
        if nombre and out[k] and out[k][-1][:1].isupper():      # une version : « Outil 2 », « Pro 3.5 »
            out[k][-1] += " " + m; i += 1
        elif nombre and i + 1 < len(mots) and mots[i + 1][0] == k:   # une quantité : « 3 outils »
            out[k].append(m + " " + mots[i + 1][1]); i += 2
        else:
            out[k].append(m); i += 1
    bloc = "MANUAL = [\n" + "".join("    " + json.dumps(c, ensure_ascii=False) + f",   # prise {k}\n" for k, c in enumerate(out)) + "]\n"
    p = ROOT / "tools/montage_captions.py"
    s = p.read_text(encoding="utf-8")
    s2, n = re.subn(r"(?ms)^MANUAL = \[\n.*?^\]\n", lambda _: bloc, s, count=1)
    if not n:
        sys.exit("MANUAL introuvable dans tools/montage_captions.py")
    p.write_text(s2, encoding="utf-8")
    print(bloc + "-> écrit dans tools/montage_captions.py (relis les noms propres)")


def finir(sans):
    from PIL import ImageFont
    import brand_style
    style = brand_style.style()
    taille = style.captions_size
    police = ImageFont.truetype(str(style.captions_font_file), round(taille * FACTEUR))
    secs = [s for s in sections.sections()]
    p = ROOT / "compositions/captions.html"
    s = p.read_text(encoding="utf-8")
    motif = re.compile(r'<div class="cap clip" id="(cap-\d+)" style="([^"]*)" data-start="([0-9.]+)" data-duration="([0-9.]+)"([^>]*)>(.*?)</div>')
    caps = [list(m.groups()) for m in motif.finditer(s)]
    image = lambda t: round(float(t) * FPS)
    # 1. sous-titre posé sur une section --sans : retour sur son mot.
    for j, c in enumerate(caps):
        debut = image(float(c[2]) + 0.01 / FPS)
        sec = next((x for x in secs if x["id"] in sans and abs(image(x["start"]) - debut) <= 0), None)
        if not sec:
            continue
        texte = norme(html.unescape(c[5]).split(" ")[0])
        avant = [w for w in WORDS if norme(w["w"]) == texte and w["start"] < sec["start"]]
        if not avant or j == 0:
            continue
        a, b = image(avant[-1]["start"]), image(sec["start"])
        prec = caps[j - 1]
        pa = image(float(prec[2]) + 0.01 / FPS)
        a = max(a, pa + 2)
        if a >= b:
            continue
        prec[3] = f"{(a - pa) / FPS:.5f}"
        c[2], c[3] = f"{(a - 0.01) / FPS:.5f}", f"{(b - a) / FPS:.5f}"
        print(f"  {html.unescape(c[5])!r} remis sur son mot ({a / FPS:.2f} s), fini à {sec['id']}")
    # 2. taille : 1,5 fois, réduite pour un mot trop long.
    for c in caps:
        styl = re.sub(r";?\s*(font-size|letter-spacing):[^;]*", "", c[1])
        largeur = police.getbbox(html.unescape(c[5]))[2]
        f = FACTEUR if largeur <= LARGEUR_MAX else round(FACTEUR * LARGEUR_MAX / largeur, 3)
        c[1] = f"{styl}; font-size:calc(var(--brand-cap-size) * {f}); letter-spacing:-0.025em"
    def remplace(m):
        c = next(x for x in caps if x[0] == m.group(1))
        return f'<div class="cap clip" id="{c[0]}" style="{c[1]}" data-start="{c[2]}" data-duration="{c[3]}"{c[4]}>{c[5]}</div>'
    s = motif.sub(remplace, s)
    p.write_text(s, encoding="utf-8")
    print(f"{len(caps)} sous-titres à {FACTEUR} fois {taille} px (mots longs réduits pour tenir dans {LARGEUR_MAX} px)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["manual"]:
        corr = {}
        if "--corrige" in args:
            for paire in args[args.index("--corrige") + 1].split(","):
                if "=" in paire:
                    a, b = paire.split("=", 1); corr[a.strip()] = b.strip()
        manual(corr)
    elif args[:1] == ["finir"]:
        sans = set(args[args.index("--sans") + 1].split(",")) if "--sans" in args else set()
        finir(sans)
    else:
        sys.exit(__doc__)
