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

⚠️ index.html livre dans le template est un APERCU (zone d'attente a la place du visage, aucun
   media requis). Le vrai master se genere ICI : brouillon d'abord, puis --write quand ta table
   LAYOUT reflete vraiment ton Reel (ou pour le calage du cadrage, cf. setup/calibration-crop.md).
   Les pieges du master sont documentes dans motion-design/references/montage-talking-head.md §2.

POURQUOI generer plutot qu'editer a la main : les data-start / data-duration et les fenetres du
visage sont DERIVES des vraies coupes du derush. C'est ce qui empeche le bug "on voit la fin de
la prise precedente" (frontieres du master desynchronisees des coupes reelles).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections
from lieux import MAISON  # réglages du client, partagés par tous les Reels

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEC = sections.sections()
DUR = sections.DURATION
FACES = sections.face_windows()          # visage en split (moitie basse)
FACEFULL = sections.facefull_windows()   # visage PLEIN ECRAN (sections "face")

# Transform par defaut du visage en split (calibre par /setup -> montage.splitTransform).
DEFAULT_SPLIT_TRANSFORM = "translate(-216px, 410px) scale(1.40)"  # = repli crop de build_final.py
# Transform du visage PLEIN ECRAN (calibre par /setup -> montage.fullFaceTransform).
# Zoom modere sur la tete : le visage remonte, les sous-titres passent dessous.
DEFAULT_FULLFACE_TRANSFORM = "scale(1.4)"
DEFAULT_FULLFACE_ORIGIN = "center 34%"


def load_config():
    """brand.config.json (genere par /setup) sinon brand.config.example.json (defauts livres)."""
    for name in ("brand.config.json", "brand.config.example.json"):
        p = MAISON / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


CFG = load_config()
SPLIT_TRANSFORM = (CFG.get("montage") or {}).get("splitTransform") or DEFAULT_SPLIT_TRANSFORM
FULLFACE_TRANSFORM = (CFG.get("montage") or {}).get("fullFaceTransform") or DEFAULT_FULLFACE_TRANSFORM
FULLFACE_ORIGIN = (CFG.get("montage") or {}).get("fullFaceOrigin") or DEFAULT_FULLFACE_ORIGIN
# Le fond n'est JAMAIS ecrit en dur ici : le master charge brand/tokens.css, donc
# `var(--brand-bg)` suffit et suit le style de chacun. C'est aussi le motif que
# tools/build_overlay.py cherche pour fabriquer le calque alpha.
BG = "var(--brand-bg)"

# --- export natif : visages pre-cadres en pleine resolution (tools/build_faces.py) -----------
# Presents -> le master les pose a l'echelle 1 (aucun agrandissement : le rendu HyperFrames, donc le
# bouton Export de l'app, garde le visage net). Absents -> repli sur base.mp4 agrandie par transform.
NATIF_SPLIT = (ROOT / "assets/video/visage-split.mp4").exists()
NATIF_PLEIN = (ROOT / "assets/video/visage-plein.mp4").exists()
SRC_SPLIT = "assets/video/visage-split.mp4" if NATIF_SPLIT else "assets/video/base.mp4"
SRC_PLEIN = "assets/video/visage-plein.mp4" if NATIF_PLEIN else "assets/video/base.mp4"
CSS_SPLIT = "transform: none;" if NATIF_SPLIT else f"transform-origin: 0 0; transform: {SPLIT_TRANSFORM};"
CSS_PLEIN = "transform: none;" if NATIF_PLEIN else f"transform: {FULLFACE_TRANSFORM}; transform-origin: {FULLFACE_ORIGIN};"

# --- calage des videos sur les images du rendu (30 im/s) --------------------------------------
FPS = 30   # cadence du rendu : data-fps du master, bouton Export de l'app


def fenetre(st: float, d: float, media: bool = True) -> tuple[str, str, str]:
    """data-start, data-media-start et data-duration d'une <video> posee sur [st, st + d[, calees
    sur les images du rendu. Mesure sur HyperFrames 0.8 (videos numerotees) : le rendu compte le
    depart d'une video a l'image SUIVANTE et son entree dans le fichier a l'image PRECEDENTE. Un
    depart entre deux images (les coupes du derush) affichait donc l'image d'avant : le visage
    arrivait 33 a 59 ms apres la voix. Depart ecrit un centieme d'image SOUS la frontiere, entree
    un centieme AU-DESSUS : les deux tombent sur la meme image (avec cet arrondi, comme au plus
    pres). media=False : video qui commence au debut de son fichier (b-roll)."""
    debut, fin = round(float(st) * FPS), round((float(st) + float(d)) * FPS)
    depart = "0" if debut == 0 else f"{(debut - 0.01) / FPS:.5f}"
    entree = ("0" if debut == 0 else f"{(debut + 0.01) / FPS:.5f}") if media else "0"
    return depart, entree, f"{(fin - debut) / FPS:.5f}"


# --- calques visage : une <video> par fenetre split -------------------------------------------
def calque(ident: str, src: str, st: float, d: float, piste: int) -> str:
    depart, entree, duree = fenetre(st, d)
    return (f'        <video id="{ident}" src="{src}" muted playsinline data-layout-allow-overflow '
            f'data-start="{depart}" data-media-start="{entree}" data-duration="{duree}" data-track-index="{piste}"></video>')


faces = "\n".join(calque(f"face{chr(65 + i)}", SRC_SPLIT, st, d, 10) for i, (st, d) in enumerate(FACES))

# --- calque visage PLEIN ECRAN : une <video> par section "face" ------------------------------
faces_full = "\n".join(calque(f"facefull{i}", SRC_PLEIN, st, d, 11) for i, (st, d) in enumerate(FACEFULL))

# --- sections : une sous-comp par ligne de LAYOUT --------------------------------------------
# ⛔ Une section MEDIA (b-roll) est une <video> POSEE ICI, pas une sous-comp : dans une sous-comp
# le `data-start="0"` de la video est relatif a la compo mais le runtime media le lit en ABSOLU
# -> le b-roll s'affiche des 0 s et recouvre les autres sections. Comme le <video> visage, elle
# n'a PAS class="clip" : sa fenetre vient de data-start/data-duration.
rows, track = [], {"split": 2, "full": 3}
for s in SEC:
    if s["fmt"] == "face":
        continue          # section "face" = juste le visage plein ecran, aucune sous-comp a monter
    h = 920 if s["fmt"] == "split" else 1920
    ti = track[s["fmt"]]
    if s.get("media"):
        depart, entree, duree = fenetre(s["start"], s["dur"], media=False)
        rows.append(
            f'      <video id="{s["id"]}" class="media-{"split" if h == 920 else "full"}" '
            f'src="assets/video/{s["media"]}" muted playsinline '
            f'data-start="{depart}" data-media-start="{entree}" data-duration="{duree}" '
            f'data-track-index="{ti}"></video>')
        continue
    rows.append(
        f'      <div id="section-{s["id"]}" class="clip" data-composition-id="{s["id"]}" '
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
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: {BG}; }}

      /* Visage SPLIT-SCREEN : surface PLEIN CADRE clippee a la moitie basse (anti carre noir).
         Fond transparent obligatoire. Export natif : visage-split.mp4 deja cadre (transform: none) ;
         sinon base.mp4 cadree par montage.splitTransform (calibre par /setup). */
      .face-bottom {{ position: absolute; inset: 0; overflow: hidden; background: transparent; clip-path: inset(920px 0 0 0); }}
      .face-bottom video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover;
        {CSS_SPLIT} }}
      /* Visage PLEIN ECRAN (sections "face") : surface plein cadre, fond TRANSPARENT
         obligatoire (sinon carre noir). Export natif : visage-plein.mp4 deja cadre ; sinon zoom
         sur la tete depuis montage.fullFaceTransform. */
      .face-full {{ position: absolute; inset: 0; overflow: hidden; background: transparent; }}
      .face-full video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover;
        {CSS_PLEIN} }}
      /* B-roll : pre-cadre a la zone par ffmpeg (fond flou compris) -> aucun recadrage ici. */
      .media-full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .media-split {{ position: absolute; left: 0; top: 0; width: 1080px; height: 920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <!--
      MASTER : GENERE par tools/build_master.py (ne pas editer a la main).
      1080x1920, 30 fps, {DUR} s. {len(SEC)} section(s), {len(FACES)} fenetre(s) visage.

      Les data-start / data-duration viennent des VRAIES coupes du derush
      (via tools/sections.py -> {sections.CUTS_PATH.relative_to(ROOT)}, mesurees par
      tools/cut_boundaries.py), JAMAIS des timestamps Whisper (qui demarrent ~0.1-0.25 s trop tot
      -> on verrait la fin de la prise precedente au passage plein-ecran).

      Ordre DOM = layering : bgbase < visage split < sections < captions.
    -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">

      <!-- Fond de marque (seul aplat opaque autorise, tout en bas de la pile). -->
      <div id="bgbase" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" style="position:absolute; inset:0; background:{BG};"></div>

      <!-- Voix off : piste audio separee (les <video> sont muted). Source = la base derushee. -->
      <audio id="vo" src="assets/video/base.mp4" data-start="0" data-duration="{DUR}" data-track-index="13" data-volume="1" data-audio-group="mixage"></audio>

      <!-- SFX et musique (etape 6) : poses ici par tools/build_sfx.py, gardes quand le master est regenere. -->
      <!-- SONS -->

      <!-- VISAGE (split-screen, bas) : uniquement pendant les fenetres SPLIT. -->
      <div class="face-bottom">
{faces}
      </div>

      <!-- ===== SECTIONS ===== -->
{chr(10).join(rows)}

      <!-- VISAGE plein ecran : APRES les sections. L'ordre DOM fait le layering : place avant,
           une section pourrait peindre par-dessus le visage meme hors de sa fenetre. -->
      <div class="face-full">
{faces_full}
      </div>

      <!-- Sous-titres (par-dessus tout). Chemin depuis la RACINE (jamais ../). -->
      <div id="sous-titres" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-track-kind="captions" data-start="0" data-duration="{DUR}" data-track-index="14" data-width="1080" data-height="1920" style="position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden;"></div>
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
    # Les sons deja poses (tools/build_sfx.py, ou retouches dans l'app) survivent a la regeneration.
    if out.exists():
        import re
        sons = re.search(r" *<!-- SONS:DEBUT.*?<!-- SONS:FIN -->", out.read_text(encoding="utf-8"), re.S)
        if sons:
            doc = doc.replace("      <!-- SONS -->", sons.group(0), 1)
else:
    (ROOT / "work").mkdir(exist_ok=True)
    out = ROOT / "work/index.generated.html"

out.write_text(doc, encoding="utf-8")
print(f"{out.relative_to(ROOT)} : {len(SEC)} section(s), {len(FACES)} fenetre(s) visage, {DUR}s")
if "--write" not in sys.argv:
    print("(brouillon ; compare-le a index.html, puis relance avec --write pour ecraser index.html)")
