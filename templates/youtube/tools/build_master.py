#!/usr/bin/env python3
"""Génère le MASTER d'une vidéo YouTube (1920x1080, 30 im/s) depuis tools/sections.py.

Ce script ne se modifie pas : il DÉRIVE tout de la table LAYOUT de sections.py.
  - une <video> plein cadre par cadre utilisé (visage-large, visage-serre, visage-tres-serre),
    toutes calées sur la timeline du dérush ; le master montre la bonne à chaque coupe ;
  - le glissement du créateur sur le côté pendant les sections « cote » (un seul geste avec
    l'entrée du panneau) ;
  - une sous-composition par section (panneau, incrustation, plein écran), un B-roll posé ici ;
  - les textes d'appui compositions/emphases.html (tools/build_emphases.py), par-dessus tout.

SORTIE :
  Par défaut -> work/index.generated.html (brouillon, pour inspection).
  Avec --write -> ÉCRASE index.html (les sons déjà posés par tools/build_sfx.py sont gardés).

Pièges du montage par couches (communs avec les Reels) : skill motion-design,
references/montage-talking-head.md §0bis et §0ter.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEC = sections.sections()
DUR = sections.DURATION
FPS = 30
W, H = 1920, 1080
DECALAGE = 480          # px : le créateur glisse d'un quart d'écran, le panneau prend la moitié libre
GLISSE_ENTREE, GLISSE_SORTIE = 0.6, 0.5
PISTES = {"large": 10, "serre": 11, "tres-serre": 12}
YT = config().get("youtube") or {}
CADRAGE = {"visageX": 0.5, "yeuxY": 0.40, **(YT.get("cadrage") or {})}
ZOOMS = {"large": 1.0, "serre": float(YT.get("zoomSerre") or 1.3), "tres-serre": float(YT.get("zoomTresSerre") or 1.55)}


def instant(t: float) -> str:
    """Un changement à l'instant t (une coupe du dérush), calé sur l'image du rendu qui le montre :
    écrit un centième d'image sous la frontière, il tombe sur la même image que la voix."""
    k = round(float(t) * FPS)
    return "0" if k == 0 else f"{(k - 0.01) / FPS:.5f}"


def fenetre_media(st: float, d: float) -> tuple[str, str]:
    """data-start et data-duration d'un B-roll (vidéo lue depuis son début), calés sur les images."""
    debut, fin = round(st * FPS), round((st + d) * FPS)
    return instant(st), f"{(fin - debut) / FPS:.5f}"


# --- visages : une <video> plein cadre par cadre utilisé -------------------------------------
cadres = [c for c in sections.CADRES if sections.fenetres(c)]
visages, css_visages = [], []
for c in cadres:
    natif = (ROOT / f"assets/video/visage-{c}.mp4").exists()
    src = f"assets/video/visage-{c}.mp4" if natif else "assets/video/base.mp4"
    if natif:
        transfo = "transform: none;"
    else:   # aperçu avant tools/build_faces.py : zoom CSS sur base.mp4 (moins net, jamais exporté ainsi)
        transfo = (f"transform: scale({ZOOMS[c]}); transform-origin: {CADRAGE['visageX'] * 100:.0f}% "
                   f"{CADRAGE['yeuxY'] * 100:.0f}%;")
    visages.append(
        f'      <div id="visage-{c}" class="visage">\n'
        f'        <video id="video-{c}" src="{src}" muted playsinline data-layout-allow-overflow '
        f'data-start="0" data-media-start="0" data-duration="{DUR}" data-track-index="{PISTES[c]}"></video>\n'
        f'      </div>')
    css_visages.append(f"      #visage-{c} video {{ {transfo} }}")

# Visibilité : à chaque coupe, seul le cadre de la prise est visible (aucun pendant un plein écran).
# L'état de départ s'écrit dans le CSS : un tl.set() à 0 n'est pas rendu tant que la tête de lecture
# est pile sur 0, et la 1re image montrait le cadre du dessus (très serré) au lieu de celui du hook.
etapes, visible = [], None
for p in sections.cadre_par_prise():
    if p["cadre"] == visible:
        continue
    t = instant(p["start"])
    for c in cadres:
        if t == "0":
            if c != p["cadre"]:
                css_visages.append(f"      #visage-{c} {{ opacity: 0; visibility: hidden; }}")
            continue
        etapes.append(f'      tl.set("#visage-{c}", {{ autoAlpha: {1 if c == p["cadre"] else 0} }}, {t});')
    visible = p["cadre"]

# Glissement sur le côté (sections cote) : il part du visage large plein cadre dès que la prise
# d'avant montre le visage, quel que soit son cadre (une prise serrée passe en large sur la coupe,
# puis glisse : le panneau entre toujours d'un seul geste). Instantané après un plein écran ou un
# autre décalage. Le retour est animé vers le visage large, coupé sec vers un autre cadre.
for f in sections.fenetres_cote():
    dx = -DECALAGE if f["panneau"] == "droite" else DECALAGE
    t0, t1 = instant(f["start"]), instant(f["end"])
    if f["avant"] in sections.CADRES:
        etapes.append(f'      tl.fromTo("#visage-large", {{ x: 0 }}, {{ x: {dx}, duration: {GLISSE_ENTREE}, '
                      f'ease: "power2.inOut", immediateRender: false }}, {t0});')
    else:
        etapes.append(f'      tl.set("#visage-large", {{ x: {dx} }}, {t0});')
    if f["apres"] == "large" and f["end"] < DUR - 0.01:
        etapes.append(f'      tl.fromTo("#visage-large", {{ x: {dx} }}, {{ x: 0, duration: {GLISSE_SORTIE}, '
                      f'ease: "power2.inOut", immediateRender: false }}, {t1});')
    else:
        etapes.append(f'      tl.set("#visage-large", {{ x: 0 }}, {t1});')

# --- sections -------------------------------------------------------------------------------
manquantes = [s["id"] for s in SEC if s["fmt"] != "face" and not s["media"]
              and not (ROOT / f"compositions/{s['id']}.html").exists()]
if manquantes:
    sys.exit("ERREUR : compositions manquantes : " + ", ".join(f"compositions/{m}.html" for m in manquantes)
             + "\nCrée-les (panneau 960x1080 pour cote, 1920x1080 pour over et full), puis relance.")

rows = []
for s in SEC:
    if s["fmt"] == "face":
        continue
    if s["media"]:
        depart, duree = fenetre_media(s["start"], s["dur"])
        rows.append(f'      <video id="{s["id"]}" class="media-full" src="assets/video/{s["media"]}" muted playsinline '
                    f'data-start="{depart}" data-media-start="0" data-duration="{duree}" data-track-index="3"></video>')
        continue
    if s["fmt"] == "cote":
        x, w, piste = (W // 2 if s["panneau"] == "droite" else 0), W // 2, 2
    else:
        x, w, piste = 0, W, (4 if s["fmt"] == "over" else 3)
    rows.append(f'      <div id="section-{s["id"]}" class="clip" data-composition-id="{s["id"]}" '
                f'data-composition-src="compositions/{s["id"]}.html" data-start="{s["start"]}" '
                f'data-duration="{s["dur"]}" data-track-index="{piste}" data-width="{w}" data-height="{H}" '
                f'style="position:absolute; left:{x}px; top:0; width:{w}px; height:{H}px; overflow:hidden;"></div>')

emphases = ""
if (ROOT / "compositions/emphases.html").exists():
    emphases = (f'      <div id="textes-appui" class="clip" data-composition-id="emphases" '
                f'data-composition-src="compositions/emphases.html" data-track-kind="captions" data-start="0" '
                f'data-duration="{DUR}" data-track-index="14" data-width="{W}" data-height="{H}" '
                f'style="position:absolute; left:0; top:0; width:{W}px; height:{H}px; overflow:hidden;"></div>')

nl = "\n"
doc = f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width={W}, height={H}">
    <script src="assets/vendor/gsap.min.js"></script>
    <!-- PIÈGE : brand/fonts.css + brand/tokens.css DANS LE <head> DU MASTER, sinon au rendu par
         couches les var(--brand-*) et les polices des sous-compositions ne se résolvent pas. -->
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: var(--brand-bg); }}
      /* Visage : surface PLEIN CADRE, fond transparent (anti carré noir). Le glissement anime le
         conteneur, jamais la <video> (le framework impose son cadrage sur les <video>). */
      .visage {{ position: absolute; inset: 0; overflow: hidden; background: transparent; }}
      .visage video {{ position: absolute; inset: 0; width: {W}px; height: {H}px; object-fit: cover; }}
{nl.join(css_visages)}
      /* B-roll : pré-cadré en 16:9 par ffmpeg (fond flou compris s'il ne remplit pas l'écran). */
      .media-full {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <!--
      MASTER : GÉNÉRÉ par tools/build_master.py (ne pas éditer à la main : modifier tools/sections.py).
      {W}x{H}, {FPS} im/s, {DUR} s. {len(SEC)} section(s), cadres : {", ".join(cadres) or "aucun"}.
      Frontières = les VRAIES coupes ({sections.CUTS_PATH.relative_to(ROOT)}), jamais Whisper.
      Ordre DOM = superposition : fond < visages < panneaux < incrustations < plein écran < textes d'appui.
    -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">

      <!-- Fond de marque (seul aplat opaque plein cadre autorisé, tout en bas de la pile). -->
      <div id="bgbase" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" style="position:absolute; inset:0; background:var(--brand-bg);"></div>

      <!-- Voix : piste audio séparée (les <video> sont muted). Source = la base dérushée. -->
      <audio id="vo" src="assets/video/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="13" data-volume="1" data-audio-group="mixage"></audio>

      <!-- SFX et musique : posés ici par tools/build_sfx.py, gardés quand le master est régénéré. -->
      <!-- SONS -->

      <!-- VISAGES (un cadre par vidéo ; le master montre celui de chaque prise). -->
{nl.join(visages)}

      <!-- ===== SECTIONS ===== -->
{nl.join(rows)}

      <!-- Textes d'appui (par-dessus tout). Chemin depuis la RACINE (jamais ../). -->
{emphases}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      (function () {{
      var tl = gsap.timeline({{ paused: true }});
{nl.join(etapes)}
      window.__timelines["main"] = tl;
      }})();
    </script>
  </body>
</html>
'''

if "--write" in sys.argv:
    out = ROOT / "index.html"
    # Les sons déjà posés (tools/build_sfx.py, ou retouchés dans l'app) survivent à la régénération.
    if out.exists():
        sons = re.search(r" *<!-- SONS:DEBUT.*?<!-- SONS:FIN -->", out.read_text(encoding="utf-8"), re.S)
        if sons:
            doc = doc.replace("      <!-- SONS -->", sons.group(0), 1)
else:
    (ROOT / "work").mkdir(exist_ok=True)
    out = ROOT / "work/index.generated.html"

out.write_text(doc, encoding="utf-8")
print(f"{out.relative_to(ROOT)} : {len(SEC)} section(s), cadres {', '.join(cadres) or 'aucun'}, {DUR} s")
if any(not (ROOT / f"assets/video/visage-{c}.mp4").exists() for c in cadres):
    print("  ⚠️ aperçu : visages zoomés dans base.mp4. Avant l'export : python3 tools/build_faces.py, puis --write.")
if "--write" not in sys.argv:
    print("(brouillon ; compare-le à index.html, puis relance avec --write pour écraser index.html)")
