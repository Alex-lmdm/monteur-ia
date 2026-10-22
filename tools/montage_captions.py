#!/usr/bin/env python3
"""Genere les SOUS-TITRES (captions.html) depuis sections.py — 1er jet, a re-couper a la main.

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE REEL : remplis MANUAL avec le decoupage de TON  ║
║ script (une ligne par phrase du derush, dans l'ordre des prises).              ║
║                                                                                ║
║ SORTIE :                                                                       ║
║   Par defaut -> work/captions.generated.html (brouillon, pour inspection).     ║
║   Avec --write -> ECRASE compositions/captions.html.                           ║
║ compositions/captions.html livre est un EXEMPLE pedagogique : on ne l'ecrase   ║
║ pas par defaut. Ce script donne le 1er jet ; RE-COUPE ensuite a la main        ║
║ (2-3 mots, unite grammaticale, pas de ponctuation finale, cf sous-titres.md).  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Decoupage par UNITE GRAMMATICALE : nom+adjectif et groupe verbal insecables, jamais a cheval
sur 2 phrases, jamais de ponctuation finale, mot fort de chute isole.

SECTION-AWARE : un sous-titre ne deborde jamais d'une section et prend la hauteur de sa section
(split -> y=920 a la jointure ; plein-ecran motion -> y=1500, sous la fenetre plein ecran).
"""
import html
import pathlib
import sys

import difflib
import json

from PIL import ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand_style
import sections
from lieux import config
from nombres import jetons, normaliser

# Windows : une sortie lue par l'agent (redirigée) est en cp1252, et un « ✅ » y fait planter l'outil.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent

# La police de sous-titres vient du style resolu (preset + brand.config.json), jamais en dur :
# c'est elle qui rend un compte reconnaissable en une seconde, elle doit appartenir a l'utilisateur.
STYLE = brand_style.style()
if STYLE.captions_font_file is None:
    raise SystemExit(
        f"ERREUR : aucun .ttf de mesure pour la police de sous-titres « {STYLE.font_captions} ».\n"
        "PIL ne lit pas le woff2 : sans .ttf, impossible de garantir une seule ligne.\n"
        "Depose le .ttf dans assets/fonts/, declare-le en `measureFile` dans "
        "templates/style-presets.json, puis relance."
    )
# = --brand-cap-size, a la graisse affichee ; le texte mesure est celui qui s'affiche (casse comprise).
FONT = ImageFont.truetype(str(STYLE.captions_font_file), STYLE.captions_size)
MAXW_HARD = 900

# Bornes de phrase = les VRAIES coupes (une prise = une phrase). Surtout PAS les timestamps
# Whisper : ils demarrent trop tot et les sous-titres partaient avant la coupe.
TAKES = sections.TAKES
# Bornes posees sur les images du rendu (sections.FPS) : un sous-titre au millieme s'affichait sur
# l'image SUIVANTE (une image de retard sur la voix, une fois sur trois). Recalees ici aussi, pour
# rester justes avec un tools/sections.py d'avant ce calage (Reel repris d'une ancienne version).
FPS = getattr(sections, "FPS", 30)


def image(t):
    """L'instant `t` pose sur l'image du rendu la plus proche (n / FPS)."""
    return round(float(t) * FPS) / FPS


SEC = [{**x, "start": image(x["start"]), "end": image(x["end"])} for x in sections.sections()]
DUR = round(image(sections.DURATION), 5)

# =============================================================================
# DECOUPAGE — une ligne par phrase de la timeline, dans l'ordre des prises.
# >>> A REMPLACER par le decoupage de TON script.
# DEMO : une ligne par prise de derush/exemple_cuts.json (3 prises).
# =============================================================================
MANUAL = [
    ["on garde", "tes mots"],                 # take 0
    ["on retire", "les silences"],           # take 1
    ["le rythme", "change tout"],            # take 2
]
# Un chunk peut imposer son mot de depart : ["LOGO", 3] part sur le mot de rang 3 de la phrase (le
# 4e, on compte depuis 0 comme dans <video>_words.json, signes seuls exclus). Utile quand la voix ne
# dit pas le mot affiche (« commenter LE logo » sous-titre « LOGO », depart sur « le »).

# --mots N (1 a 3) : le decoupage vient de la voix au lieu de MANUAL, N mots par sous-titre, tels
# que la transcription les ecrit (ponctuation comprise). C'est le « mot a mot » des styles qui
# l'imposent (style clone, style du catalogue) ; sans l'option, MANUAL reste la regle.
MOTS = None
if "--mots" in sys.argv:
    try:
        MOTS = int(sys.argv[sys.argv.index("--mots") + 1])
    except (IndexError, ValueError):
        MOTS = 0
    if not 1 <= MOTS <= 3:
        raise SystemExit("ERREUR : --mots attend 1, 2 ou 3 (le nombre de mots par sous-titre).")
# --sans s0-hook,s5 : aucun sous-titre dans ces sections (une accroche ou une carte qui porte deja le
# texte, quand le style le veut). Sans l'option, toutes les sections en ont.
SANS = set()
if "--sans" in sys.argv:
    try:
        SANS = {x.strip() for x in sys.argv[sys.argv.index("--sans") + 1].split(",") if x.strip()}
    except IndexError:
        raise SystemExit("ERREUR : --sans attend les sections sans sous-titres, ex. --sans s0-hook,s5-cta.")

# Option (brand.config.json -> montage.sousTitresDepuisCoupe, defaut false) : le 1er sous-titre de
# chaque phrase part sur la coupe, pas sur son 1er mot reconnu (il s'affiche des la 1re image du plan).
DEPUIS_COUPE = (config().get("montage") or {}).get("sousTitresDepuisCoupe") is True

# Une phrase par prise (cas simple). Si plusieurs prises forment UNE phrase (ex. un CTA en
# 3 bouts), fusionne-les ici : PHRASES.append({'start': TAKES[i]['start'], 'end': TAKES[j]['end']}).
PHRASES = [{'start': t['start'], 'end': t['end']} for t in TAKES]

# SECTIONS = derivees de sections (meme source que le master) -> jamais desynchronisees
SECTIONS = [(x['start'], x['y']) for x in SEC]
BOUNDS = [s[0] for s in SECTIONS]   # 0 compris : la 1re image du Reel porte deja un sous-titre

# --- timing : sur les VRAIS MOTS si <video>_words.json existe, sinon approximation ---
# Le prorata de caracteres DERIVE : les premiers chunks durent trop et tous les suivants
# arrivent en retard. Lance `python3 tools/build_words.py` une fois : les sous-titres
# demarrent alors PILE sur le mot qu'ils affichent.
WORDS_PATH = sections.CUTS_PATH.with_name(
    sections.CUTS_PATH.name.replace('_cuts.json', '_words.json'))
WORDS = json.loads(WORDS_PATH.read_text(encoding='utf-8')) if WORDS_PATH.exists() else None
if WORDS is None:
    print(f"  ⚠ {WORDS_PATH.name} absent -> timing APPROXIMATIF (proportionnel au texte).")
    print("    Lance `python3 tools/build_words.py` pour caler les sous-titres sur la voix.")

if MOTS:
    if WORDS is None:
        raise SystemExit(f"ERREUR : --mots decoupe la voix : lance d'abord `python3 tools/build_words.py` ({WORDS_PATH.name}).")
    MANUAL = []
    for ph in PHRASES:
        dits, avant = [], ""
        for w in WORDS:
            m = w['w'].strip()
            if not m or not (ph['start'] - 1e-6 <= w['start'] < ph['end']):
                continue
            if any(c.isalnum() for c in m):
                dits.append(avant + m)
                avant = ""
            elif m in ("«", "(", "[", "“", "‘") or not dits:     # un signe qui ouvre : avec le mot suivant
                avant += m + (" " if m == "«" else "")
            else:                                               # un signe seul : avec son mot
                dits[-1] += (" " if m in ("?", "!", ":", ";", "»") else "") + m
        MANUAL.append([" ".join(dits[i:i + MOTS]) for i in range(0, len(dits), MOTS)])
assert len(MANUAL) == len(PHRASES), f"MANUAL={len(MANUAL)} != phrases={len(PHRASES)}"


def _align(words, chunks):
    """start de chaque chunk = start de son 1er mot. difflib plutot qu'un compteur : robuste
    quand Whisper decoupe autrement que le decoupage manuel. Les deux sources sont normalisees par
    tools/nombres.py (minuscules, sans accents ni ponctuation) et un nombre s'y ecrit d'une seule
    facon : « 3 » / « trois », « 1 400 » / « 1400 » / « mille quatre cents », « 100 % » / « 100% »."""
    wtoks = jetons([w['w'] for w in words])
    cwords, owner = [], []
    for k, c in enumerate(chunks):
        for n, _ in jetons(c.split()):
            if n:
                cwords.append(n)
                owner.append(k)
    first = {}
    for i, j, size in difflib.SequenceMatcher(a=[n for n, _ in wtoks], b=cwords, autojunk=False).get_matching_blocks():
        for d in range(size):
            k = owner[j + d]
            if k not in first:
                first[k] = words[wtoks[i + d][1]]['start']
    return first


def _chunk(c):
    """(texte, rang du mot de depart impose ou None) : "texte" ou ["texte", rang]."""
    if isinstance(c, (list, tuple)):
        rang = c[1] if len(c) > 1 and isinstance(c[1], int) and not isinstance(c[1], bool) else None
        return str(c[0]), rang
    return c, None


caps = []
for pi, ph in enumerate(PHRASES):
    lus = [_chunk(c) for c in MANUAL[pi]]
    chunks, imposes = [t for t, _ in lus], [r for _, r in lus]
    t0, t1 = ph['start'], ph['end']

    starts = None
    if WORDS:
        wins = [w for w in WORDS if t0 - 1e-6 <= w['start'] < t1]
        first = _align(wins, chunks)
        mots = [w for w in wins if normaliser(w['w'])]
        for k, rang in enumerate(imposes):
            if rang is None:
                continue
            if 0 <= rang < len(mots):
                first[k] = mots[rang]['start']
            else:
                print(f"  ⚠ « {chunks[k]} » : pas de mot de rang {rang} dans la phrase {pi} ({len(mots)} mots), depart calcule.")
        if first:
            starts = []
            for k in range(len(chunks)):
                if k in first:
                    starts.append(max(t0, first[k]))
                else:                       # mot introuvable : on interpole entre les voisins cales
                    prev = starts[-1] if starts else t0
                    nxt = next((first[j] for j in range(k + 1, len(chunks)) if j in first), t1)
                    starts.append(prev + (nxt - prev) / 2)
            for k in range(1, len(starts)):  # croissance stricte
                starts[k] = max(starts[k], starts[k - 1] + 0.08)
            starts = [min(t, t1 - 0.05) for t in starts]
            if DEPUIS_COUPE and imposes[0] is None:
                starts[0] = t0

    if starts is None:                       # fallback : proportionnel au nb de caracteres
        if any(r is not None for r in imposes):
            print(f"  ⚠ phrase {pi} : depart sur un mot impose sans {WORDS_PATH.name}, timing approximatif.")
        lens = [max(len(c), 1) for c in chunks]
        tot = sum(lens); acc = 0
        starts = []
        for L in lens:
            starts.append(t0 + (acc / tot) * (t1 - t0))
            acc += L

    for c, t in zip(chunks, starts):
        if SANS and any(x["id"] in SANS and x["start"] - 1e-6 <= image(t) < x["end"] for x in SEC):
            continue
        # Casse : celle de visual.captionsCase (capitales par defaut, comme le CSS de .cap).
        caps.append({'start': image(t), 'text': c.upper() if STYLE.captions_case == "upper" else c})

if not caps:
    raise SystemExit("ERREUR : aucun sous-titre a ecrire (decoupage vide, ou toutes les sections dans --sans).")

# 1) SNAP sur les frontieres de section : le sous-titre le plus proche demarre PILE dessus
for B in BOUNDS:
    i = min(range(len(caps)), key=lambda k: abs(caps[k]['start'] - B))
    if abs(caps[i]['start'] - B) < 0.6:
        caps[i]['start'] = B
caps.sort(key=lambda c: c['start'])

# 2) fins recalculees (timing continu), BORNEES A LA FIN DE LA SECTION.
#    Sans cette borne, le dernier sous-titre d'une section reste affiche sur la suivante :
#    il « bave » une demi-seconde sur le plan d'apres (bug classique, tres visible au montage).
SECTION_ENDS = [x['end'] for x in SEC]


def _section_end(t):
    for x in SEC:
        if x['start'] - 1e-6 <= t < x['end']:
            return x['end']
    return DUR


for j in range(len(caps)):
    nxt = caps[j + 1]['start'] if j + 1 < len(caps) else DUR
    end = min(nxt, _section_end(caps[j]['start']))
    caps[j]['end'] = end
    caps[j]['dur'] = end - caps[j]['start']


def _attrs(debut, duree):
    """data-start / data-duration d'un sous-titre : depart un centieme d'image SOUS sa frontiere
    (le rendu l'affiche des cette image, jamais la suivante), duree en images entieres (meme regle
    que fenetre() de tools/build_master.py, pour les sections et le visage)."""
    a, b = round(debut * FPS), round((debut + duree) * FPS)
    return ("0" if a == 0 else f"{(a - 0.01) / FPS:.5f}"), f"{(b - a) / FPS:.5f}"


# 3) Y = section qui contient le start
def y_for(start):
    y = SECTIONS[0][1]
    for st, yy in SECTIONS:
        if start >= st - 1e-6:
            y = yy
    return y


over = [(c['text'], FONT.getbbox(c['text'])[2]) for c in caps if FONT.getbbox(c['text'])[2] > MAXW_HARD]
if over:
    print("⚠ sous-titres trop larges :", over)

rows = "\n".join(
    f'      <div class="cap clip" id="cap-{j}" style="top:{y_for(c["start"])}px" '
    f'data-start="{_attrs(c["start"], c["dur"])[0]}" data-duration="{_attrs(c["start"], c["dur"])[1]}" '
    f'data-track-index="{j % 4}">{html.escape(c["text"])}</div>'
    for j, c in enumerate(caps))

doc = f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <!-- SOUS-TITRES : genere par tools/montage_captions.py depuis derush/<video>_cuts.json.
         Decoupage : MANUAL (2-3 mots, sans ponctuation finale), ou --mots N (la voix telle que
         transcrite) ; jamais a cheval sur 2 phrases. -->
    <script src="assets/vendor/gsap.min.js"></script>
    <!-- L'apparence de .cap (police, couleurs, skin « {STYLE.captions_skin} ») vient ENTIEREMENT
         de brand/tokens.css, genere depuis TON style. Ne rien redefinir ici : une regle en dur
         dans ce fichier survivrait a un changement de style et casserait la coherence. -->
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      /* Pas de height en dur sur body : plein cadre 1920, scope sous #captions. */
      html, body {{ width: 100%; height: 100%; overflow: hidden; background: transparent; }}
      #captions {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div id="captions" data-composition-id="captions" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
{rows}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["captions"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''

if "--write" in sys.argv:
    out = ROOT / "compositions/captions.html"
else:
    (ROOT / "work").mkdir(exist_ok=True)
    out = ROOT / "work/captions.generated.html"

out.write_text(doc, encoding="utf-8")
maxw = max(FONT.getbbox(c["text"])[2] for c in caps)
print(f'{len(caps)} sous-titres -> {out.relative_to(ROOT)}  (largeur max {maxw}px)')
if "--write" not in sys.argv:
    print("(brouillon ; re-coupe puis relance avec --write pour ecraser compositions/captions.html)")
for c in caps:
    print(f'  {c["start"]:6.2f}->{c["end"]:6.2f} [y={y_for(c["start"])}]  {c["text"]}')
