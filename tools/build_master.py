#!/usr/bin/env python3
"""Genere le MASTER (calques visage + sections + sous-titres) depuis sections.py.

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE REEL — mais tu edites surtout tools/sections.py.║
║ Ce script se contente de DERIVER le master de la table LAYOUT de sections.py : ║
║  - un calque <video> visage (assets/video/base.mp4) sur chaque fenetre SPLIT ; ║
║  - une sous-comp compositions/<id>.html par section (data-start/duration      ║
║    cales sur les VRAIES coupes du derush) ;                                    ║
║  - la piste sous-titres compositions/captions.html.                           ║
║ Le split-transform du visage vient de brand.config.json -> montage.splitTransform.║
╚══════════════════════════════════════════════════════════════════════════════╝

SORTIE :
  Par defaut -> work/index.generated.html (un BROUILLON, pour inspection/diff).
  Avec --write -> ECRASE index.html a la racine.

⚠️ index.html livre dans le template est ecrit A LA MAIN (pedagogique, avec les [pieges]).
   On ne l'ecrase donc PAS par defaut : compare d'abord le brouillon genere a index.html,
   puis --write seulement quand ta table LAYOUT reflete vraiment ton Reel.

POURQUOI generer plutot qu'editer a la main : les data-start / data-duration et les fenetres du
visage sont DERIVES des vraies coupes du derush. C'est ce qui empeche le bug "on voit la fin de
la prise precedente" (frontieres du master desynchronisees des coupes reelles).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEC = sections.sections()
DUR = sections.DURATION
FACES = sections.face_windows()

# Transform par defaut du visage en split (calibre par /setup -> montage.splitTransform).
DEFAULT_SPLIT_TRANSFORM = "translate(-240px, 380px) scale(1.40)"


def load_config():
    """brand.config.json (genere par /setup) sinon brand.config.example.json (defauts livres)."""
    for name in ("brand.config.json", "brand.config.example.json"):
        p = ROOT / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


CFG = load_config()
SPLIT_TRANSFORM = (CFG.get("montage") or {}).get("splitTransform") or DEFAULT_SPLIT_TRANSFORM

# --- calques visage : une <video> par fenetre split, source = ta base derushee ---------------
faces = "\n".join(
    f'        <video id="face{chr(65 + i)}" src="assets/video/base.mp4" muted playsinline '
    f'data-layout-allow-overflow '
    f'data-start="{st}" data-media-start="{st}" data-duration="{d}" data-track-index="10"></video>'
    for i, (st, d) in enumerate(FACES))

# --- sections : une sous-comp par ligne de LAYOUT --------------------------------------------
rows, track = [], {"split": 2, "full": 3}
for s in SEC:
    h = 920 if s["fmt"] == "split" else 1920
    ti = track[s["fmt"]]
    rows.append(
        f'      <div class="clip" data-composition-id="{s["id"]}" '
        f'data-composition-src="compositions/{s["id"]}.html" '
        f'data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="{ti}" '
        f'data-width="1080" data-height="{h}" '
        f'style="position:absolute; left:0; top:0; width:1080px; height:{h}px; overflow:hidden;"></div>')

doc = f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <script src="assets/vendor/gsap.min.js"></script>
    <!-- PIEGE : charger brand/fonts.css + brand/tokens.css DANS LE <head> DU MASTER, sinon au
         render par couches les var(--brand-*) et les polices des sous-comps ne se resolvent pas. -->
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #202022; }}

      /* Visage SPLIT-SCREEN : surface PLEIN CADRE clippee a la moitie basse (anti carre noir).
         Fond transparent obligatoire ; cadrage UNIQUEMENT via transform (jamais resize studio).
         Le transform vient de brand.config.json -> montage.splitTransform (calibre par /setup). */
      .face-bottom {{ position: absolute; inset: 0; overflow: hidden; background: transparent; clip-path: inset(920px 0 0 0); }}
      .face-bottom video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover;
        transform-origin: 0 0; transform: {SPLIT_TRANSFORM}; }}
    </style>
  </head>
  <body>
    <!--
      MASTER — GENERE par tools/build_master.py (ne pas editer a la main).
      1080x1920, 30 fps, {DUR} s. {len(SEC)} section(s), {len(FACES)} fenetre(s) visage.

      Les data-start / data-duration viennent des VRAIES coupes du derush
      (via tools/sections.py -> {sections.CUTS_PATH.relative_to(ROOT)}, mesurees par
      tools/cut_boundaries.py), JAMAIS des timestamps Whisper (qui demarrent ~0.1-0.25 s trop tot
      -> on verrait la fin de la prise precedente au passage plein-ecran).

      Ordre DOM = layering : bgbase < visage split < sections < captions.
    -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">

      <!-- Fond de marque (seul aplat opaque autorise, tout en bas de la pile). -->
      <div id="bgbase" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" style="position:absolute; inset:0; background:#202022;"></div>

      <!-- Voix off : piste audio separee (les <video> sont muted). Source = la base derushee. -->
      <audio id="vo" src="assets/video/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="13" data-volume="1"></audio>

      <!-- VISAGE (split-screen, bas) : uniquement pendant les fenetres SPLIT. -->
      <div class="face-bottom">
{faces}
      </div>

      <!-- ===== SECTIONS ===== -->
{chr(10).join(rows)}

      <!-- Sous-titres (par-dessus tout). Chemin depuis la RACINE (jamais ../). -->
      <div class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="14" data-width="1080" data-height="1920" style="position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden;"></div>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''

if "--write" in sys.argv:
    out = ROOT / "index.html"
else:
    (ROOT / "work").mkdir(exist_ok=True)
    out = ROOT / "work/index.generated.html"

out.write_text(doc, encoding="utf-8")
print(f"{out.relative_to(ROOT)} — {len(SEC)} section(s), {len(FACES)} fenetre(s) visage, {DUR}s")
if "--write" not in sys.argv:
    print("(brouillon ; compare-le a index.html, puis relance avec --write pour ecraser index.html)")
