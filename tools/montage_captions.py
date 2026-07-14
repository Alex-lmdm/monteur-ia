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

# --- timing : interpole dans chaque phrase (proportionnel au nb de caracteres) ---
caps = []
for pi, ph in enumerate(PHRASES):
    chunks = MANUAL[pi]
    t0, t1 = ph['start'], ph['end']
    lens = [max(len(c), 1) for c in chunks]
    tot = sum(lens); acc = 0
    for c, L in zip(chunks, lens):
        caps.append({'start': round(t0 + (acc / tot) * (t1 - t0), 3), 'text': c.upper()})
        acc += L

# 1) SNAP sur les frontieres de section (aucun sous-titre ne bave sur la section suivante)
for B in BOUNDS:
    i = min(range(len(caps)), key=lambda k: abs(caps[k]['start'] - B))
    if abs(caps[i]['start'] - B) < 0.6:
        caps[i]['start'] = round(B, 3)
caps.sort(key=lambda c: c['start'])

# 2) fins recalculees (timing continu)
for j in range(len(caps)):
    end = caps[j + 1]['start'] if j + 1 < len(caps) else DUR
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
