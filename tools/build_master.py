#!/usr/bin/env python3
"""Genere index.html (le master) depuis sections — la source unique des frontieres.

Le master n'est plus edite a la main : ses data-start / data-duration et les fenetres du visage
sont DERIVES des vraies coupes du derush. C'est ce qui empeche le bug "on voit la fin de la prise
precedente" (frontieres du master desynchronisees des coupes reelles).
"""
import pathlib
import re

import sections

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEC = sections.sections()
DUR = sections.DURATION
FACES = sections.face_windows()

# le CTA est ecrit a la main : on lui repique juste la duree de sa section
cta = ROOT / "compositions/s8-cta.html"
cta_dur = next(s["dur"] for s in SEC if s["id"] == "s8-cta")
cta.write_text(re.sub(r'data-duration="[\d.]+"', f'data-duration="{cta_dur}"', cta.read_text()))

faces = "\n".join(
    f'        <video id="face{chr(65+i)}" src="assets/video/base-proxy.mp4" muted playsinline '
    f'data-start="{st}" data-media-start="{st}" data-duration="{d}" data-track-index="10"></video>'
    for i, (st, d) in enumerate(FACES))

rows, track = [], {"split": 2, "full": 3}
for s in SEC:
    if s["id"] == "s0-hook":
        rows.append(
            '      <!-- HOOK — b-roll dupliq "Code Secret -> Claude", accéléré pour tomber pile sur la 1re prise -->\n'
            '      <div class="screen-top">\n'
            f'        <video id="hookbroll" src="assets/video/hook-broll-v1.mp4" muted playsinline '
            f'data-start="0" data-media-start="0" data-duration="{s["dur"]}" data-track-index="1"></video>\n'
            '      </div>')
        continue
    h = 920 if s["fmt"] == "split" else 1920
    ti = 4 if s["id"] == "s8-cta" else track[s["fmt"]]
    rows.append(
        f'      <div class="clip" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" '
        f'data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="{ti}" '
        f'data-width="1080" data-height="{h}" '
        f'style="position:absolute; left:0; top:0; width:1080px; height:{h}px; overflow:hidden;"></div>')

doc = f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <script src="assets/vendor/gsap.min.js"></script>
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #202022; }}
      @font-face {{ font-family: 'BowlbyOneSC'; src: url('assets/fonts/BowlbyOneSC-Regular.ttf') format('truetype'); font-display: block; }}

      /* Visage SPLIT-SCREEN : surface PLEIN CADRE clippée à la moitié basse (anti carré noir). */
      .face-bottom {{ position: absolute; inset: 0; overflow: hidden; background: transparent; clip-path: inset(920px 0 0 0); }}
      .face-bottom video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover;
        transform-origin: 0 0; transform: translate(-240px, 380px) scale(1.40); }}

      /* B-roll du hook (panneau HAUT) : vidéo pré-composée 1080x1920, le bas est clippé. */
      .screen-top {{ position: absolute; inset: 0; overflow: hidden; background: transparent; clip-path: inset(0 0 1000px 0); }}
      .screen-top video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <!--
      MASTER — NE PAS ÉDITER À LA MAIN : régénéré par tools/build_master.py.
      Reel "7 codes secrets à utiliser sur Claude" (@LeMondeDuMarketing) — 1080x1920, 30 fps, {DUR} s.

      Les data-start / data-duration viennent des VRAIES coupes du dérush
      (derush/2026-07-14_codes-claude/codes_claude_cuts.json, mesurées par tools/cut_boundaries.py),
      JAMAIS des timestamps Whisper : ceux-ci démarrent ~0.1-0.25 s trop tôt, la fenêtre du visage
      s'ouvrait avant le jump-cut et on voyait la fin de la prise précédente.

      Ordre DOM = layering : bgbase < visage split < sections < captions.
    -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">

      <!-- Fond de marque (seul aplat opaque autorisé, tout en bas de la pile) -->
      <div id="bgbase" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" style="position:absolute; inset:0; background:#202022;"></div>

      <!-- Voix off (toute la durée) -->
      <audio id="vo" src="assets/video/base-proxy.mp4" data-start="0" data-duration="{DUR}" data-track-index="13" data-volume="1"></audio>

      <!-- VISAGE (split-screen, bas) : uniquement pendant les fenêtres SPLIT -->
      <div class="face-bottom">
{faces}
      </div>

      <!-- ===== SECTIONS ===== -->
{chr(10).join(rows)}

      <!-- Sous-titres (par-dessus tout) -->
      <div data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="14" data-width="1080" data-height="1920" style="position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden;"></div>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
(ROOT / "index.html").write_text(doc)
print(f"index.html — {len(SEC)} sections, {len(FACES)} fenêtres visage, {DUR}s")
