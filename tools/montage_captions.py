#!/usr/bin/env python3
"""Genere compositions/captions.html — Reel "7 codes secrets Claude".

Decoupage MANUEL (une phrase du derush = une ligne de MANUAL, un chunk = un sous-titre),
par UNITE GRAMMATICALE : nom+adjectif et groupe verbal insecables, jamais a cheval sur
2 phrases, jamais de ponctuation finale, mot fort de chute isole.

SECTION-AWARE : un sous-titre ne deborde jamais d'une section et prend la hauteur de sa
section (split -> 920 a la jointure ; plein-ecran motion -> 1500, sous la fenetre Claude).
"""
import html
import sys
sys.path.insert(0, 'tools')
from PIL import ImageFont
import sections

TTF  = 'assets/fonts/BowlbyOneSC-Regular.ttf'
OUT  = 'compositions/captions.html'
FONT = ImageFont.truetype(TTF, 50)
MAXW_HARD = 900

# Bornes de phrase = les VRAIES coupes (une prise = une phrase). Surtout PAS les timestamps
# Whisper : ils demarrent trop tot et les sous-titres partaient avant la coupe.
SEC   = sections.sections()
TAKES = sections.TAKES
DUR   = sections.DURATION

# =============================================================================
# DECOUPAGE — une ligne par phrase de la timeline, dans l'ordre.
# =============================================================================
MANUAL = [
    ["7 codes secrets", "à utiliser", "sur Claude"],                                         # 0  hook
    ["numéro 1", "/grill"],                                                                # 1
    ["tu le mets", "à la fin", "de ta demande", "et Claude", "t'interroge d'abord",
     "sur tout ce", "qui lui manque", "avant d'écrire", "une seule ligne"],                      # 2
    ["numéro 2", "/devil"],                                                              # 3
    ["Claude arrête", "de te flatter", "et attaque", "ton idée", "avec les meilleurs",
     "arguments", "contre toi"],                                                                 # 4
    ["numéro 3", "/brief"],                                                             # 5
    ["une réponse", "en 3 lignes", "maximum", "fini les pavés"],                             # 6
    ["numéro 4", "/roast"],                                                            # 7
    ["par défaut", "Claude trouve", "tout génial", "là il te dit", "vraiment",
     "ce qu'il trouve", "mauvais"],                                                              # 8
    ["numéro 5", "/steal"],                                                              # 9
    ["tu colles", "une pub", "ou un email", "qui a cartonné", "et il te ressort",
     "les mécaniques", "exactes", "pour les réutiliser", "chez toi"],                            # 10
    ["numéro 6", "/ghost"],                                                               # 11
    ["il traque tout", "ce qui sonne IA", "dans ton texte", "les tirets longs",
     "les formules", "toutes faites", "et il réécrit"],                                          # 12
    ["et numéro 7", "/premortem"],                                                       # 13
    ["Claude imagine", "que ton projet", "a échoué", "dans 6 mois", "et il te liste",
     "toutes les raisons", "possibles"],                                                         # 14
    ["tu vois", "les problèmes", "avant de les vivre"],                                          # 15
    ["et si t'en veux", "9 autres", "commente CODES", "et je t'envoie",
     "la liste complète", "directement en DM"],                                                  # 16  CTA
]
# 19 prises -> 17 phrases : les 3 dernieres prises (CTA) forment une seule phrase
PHRASES = [{'start': t['start'], 'end': t['end']} for t in TAKES[:16]]
PHRASES.append({'start': TAKES[16]['start'], 'end': TAKES[18]['end']})
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
    <script src="../assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 100%; height: 100%; overflow: hidden; background: transparent; }}
      #captions {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; }}
      @font-face {{
        font-family: 'BowlbyOneSC';
        src: url('../assets/fonts/BowlbyOneSC-Regular.ttf') format('truetype');
        font-display: block;
      }}
      #captions .cap {{
        position: absolute; left: 50%; transform: translate(-50%, -50%);
        font-family: 'BowlbyOneSC', sans-serif;
        font-size: 50px; line-height: 1; color: #000;
        background: #ffee00; padding: 8px 20px; white-space: nowrap;
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
open(OUT, 'w').write(doc)
print(f'{len(caps)} sous-titres -> {OUT}  (largeur max {max(FONT.getbbox(c["text"])[2] for c in caps)}px)')
for c in caps:
    print(f'  {c["start"]:6.2f}->{c["end"]:6.2f} [y={y_for(c["start"])}]  {c["text"]}')
