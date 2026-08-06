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
║ (2-3 mots, unite grammaticale, pas de ponctuation finale, cf skill §14.8).     ║
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
import re
import unicodedata

from PIL import ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections

ROOT = pathlib.Path(__file__).resolve().parent.parent
TTF = str(ROOT / "assets/fonts/BowlbyOneSC-Regular.ttf")
FONT = ImageFont.truetype(TTF, 50)
MAXW_HARD = 900

# Bornes de phrase = les VRAIES coupes (une prise = une phrase). Surtout PAS les timestamps
# Whisper : ils demarrent trop tot et les sous-titres partaient avant la coupe.
SEC = sections.sections()
TAKES = sections.TAKES
DUR = sections.DURATION

# =============================================================================
# DECOUPAGE — une ligne par phrase de la timeline, dans l'ordre des prises.
# >>> A REMPLACER par le decoupage de TON script.
# DEMO : une ligne par prise de derush/exemple_cuts.json (3 prises).
# =============================================================================
MANUAL = [
    ["voici une", "section témoin"],          # take 0
    ["duplique ce fichier", "pour la tienne"],  # take 1
    ["garde les invariants", "un à sept"],     # take 2
]

# Une phrase par prise (cas simple). Si plusieurs prises forment UNE phrase (ex. un CTA en
# 3 bouts), fusionne-les ici : PHRASES.append({'start': TAKES[i]['start'], 'end': TAKES[j]['end']}).
PHRASES = [{'start': t['start'], 'end': t['end']} for t in TAKES]
assert len(MANUAL) == len(PHRASES), f"MANUAL={len(MANUAL)} != phrases={len(PHRASES)}"

# SECTIONS = derivees de sections (meme source que le master) -> jamais desynchronisees
SECTIONS = [(x['start'], x['y']) for x in SEC]
BOUNDS = [s[0] for s in SECTIONS[1:]]

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


def _norm(w):
    """minuscules, sans accents ni ponctuation : les deux sources doivent matcher malgre les
    variantes de Whisper (« 4 » / « quatre », « 100 % » / « 100% »)."""
    w = unicodedata.normalize('NFD', w.lower())
    w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9%]', '', w)


def _align(words, chunks):
    """start de chaque chunk = start de son 1er mot. difflib plutot qu'un compteur : robuste
    quand Whisper decoupe autrement que le decoupage manuel."""
    wnorm = [_norm(w['w']) for w in words]
    cwords, owner = [], []
    for k, c in enumerate(chunks):
        for piece in c.split():
            n = _norm(piece)
            if n:
                cwords.append(n)
                owner.append(k)
    first = {}
    for i, j, size in difflib.SequenceMatcher(a=wnorm, b=cwords, autojunk=False).get_matching_blocks():
        for d in range(size):
            k = owner[j + d]
            if k not in first:
                first[k] = words[i + d]['start']
    return first


caps = []
for pi, ph in enumerate(PHRASES):
    chunks = MANUAL[pi]
    t0, t1 = ph['start'], ph['end']

    starts = None
    if WORDS:
        wins = [w for w in WORDS if t0 - 1e-6 <= w['start'] < t1]
        first = _align(wins, chunks)
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

    if starts is None:                       # fallback : proportionnel au nb de caracteres
        lens = [max(len(c), 1) for c in chunks]
        tot = sum(lens); acc = 0
        starts = []
        for L in lens:
            starts.append(t0 + (acc / tot) * (t1 - t0))
            acc += L

    for c, t in zip(chunks, starts):
        caps.append({'start': round(t, 3), 'text': c.upper()})

# 1) SNAP sur les frontieres de section : le sous-titre le plus proche demarre PILE dessus
for B in BOUNDS:
    i = min(range(len(caps)), key=lambda k: abs(caps[k]['start'] - B))
    if abs(caps[i]['start'] - B) < 0.6:
        caps[i]['start'] = round(B, 3)
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
    caps[j]['end'] = round(end, 3)
    caps[j]['dur'] = round(end - caps[j]['start'], 3)

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
    f'data-start="{c["start"]}" data-duration="{c["dur"]}" data-track-index="{j % 4}">'
    f'{html.escape(c["text"])}</div>'
    for j, c in enumerate(caps))

doc = f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <!-- SOUS-TITRES — genere par tools/montage_captions.py depuis derush/<video>_cuts.json.
         Regles : 2-3 mots par sous-titre, AUCUNE ponctuation finale, jamais a cheval sur 2 phrases. -->
    <script src="../assets/vendor/gsap.min.js"></script>
    <link rel="stylesheet" href="../brand/tokens.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      /* Pas de height en dur sur body : plein cadre 1920, scope sous #captions. */
      html, body {{ width: 100%; height: 100%; overflow: hidden; background: transparent; }}
      #captions {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; }}
      @font-face {{
        font-family: 'BowlbyOneSC';
        src: url('../assets/fonts/BowlbyOneSC-Regular.ttf') format('truetype');
        font-display: block;
      }}
      #captions .cap {{
        position: absolute; left: 50%; transform: translate(-50%, -50%);
        font-family: var(--brand-font-captions, 'BowlbyOneSC', sans-serif);
        font-size: 50px; line-height: 1; color: var(--brand-bg);
        background: var(--brand-yellow); padding: 8px 20px; white-space: nowrap;
      }}
    </style>
  </head>
  <body>
    <div id="captions" data-composition-id="captions" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">
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
