#!/usr/bin/env python3
"""Genere overlay.html — le CALQUE D'EXPORT — A LA RACINE DU PROJET, puis le rend en .mov alpha.

= le master SANS le visage, SANS le fond, SANS l'audio. Le visage et le b-roll restent en couche
video NATIVE, compositee par ffmpeg (le render HyperFrames les rasteriserait et les ramollirait).

⛔ POURQUOI A LA RACINE, ET PAS DANS build/ (bug du 2026-07-14) :
   Quand un master reference ses sous-comps par un chemin qui REMONTE (`../compositions/x.html`),
   le runtime monte bien leur DOM et leur CSS... mais PAS leurs <script>. Resultat : AUCUNE timeline
   de section ne tourne, tout reste fige a l'etat CSS initial (texte tape invisible, lignes de
   reponse affichees d'un coup, pave de /brief jamais efface). Et ca ne se voit PAS dans le studio,
   qui monte chaque sous-comp dans son propre iframe.
   => Le calque doit vivre A COTE de index.html et referencer `compositions/...` a l'identique.
   Comme deux HTML racines avec data-composition-id = erreur de lint (multiple_root_compositions),
   on l'ecrit, on rend, puis on le SUPPRIME (--render fait les trois).

Usage :
  python3 tools/build_overlay.py            # ecrit overlay.html a la racine (pour inspection)
  python3 tools/build_overlay.py --render    # ecrit + rend renders/overlay.mov + supprime
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "overlay.html"
MOV = ROOT / "renders/overlay.mov"

src = (ROOT / "index.html").read_text()
out = src

# fond transparent (le #202022 est repose par ffmpeg, sous la couche visage)
out = out.replace("background: #202022; }", "background: transparent; }", 1)
# retirer fond de marque / voix off / toutes les <video> (visage + b-roll)
out = re.sub(r"\n      <!-- Fond de marque.*?</div>\n", "\n", out, flags=re.S)
out = re.sub(r"\n      <!-- Voix off.*?</audio>\n", "\n", out, flags=re.S)
out = re.sub(r"\n *<video\b[^>]*>\s*</video>", "", out)
# retirer les wrappers devenus vides ET leur CSS : un div plein cadre avec `clip-path` reste un
# clippeur dans le compositeur, meme vide.
out = re.sub(r'\n *<div class="(face-bottom|screen-top)">\s*</div>', "", out)
out = re.sub(r"\n */\* (Visage SPLIT-SCREEN|B-roll du hook).*?\n(?=\n|    </style>)", "\n", out, flags=re.S)
# composition distincte du master
out = out.replace('data-composition-id="main"', 'data-composition-id="overlay"')
out = out.replace('window.__timelines["main"]', 'window.__timelines["overlay"]')
out = out.replace("      MASTER — NE PAS ÉDITER À LA MAIN : régénéré par tools/build_master.py.",
                  "      CALQUE D'EXPORT — NE PAS ÉDITER À LA MAIN : régénéré par tools/build_overlay.py.\n"
                  "      Fichier TEMPORAIRE (supprimé après le rendu) : deux compositions racines = erreur de lint.")

assert "<video" not in out and "<audio" not in out, "visage/audio non retire"
assert "clip-path" not in out, "un clip-path plein cadre traine encore dans le calque"
assert 'data-composition-src="compositions/' in out, "les sous-comps doivent etre en chemin RACINE"

OVERLAY.write_text(out)
print(f"overlay.html (racine) — {out.count('data-composition-src')} sections + captions")

if "--render" in sys.argv:
    try:
        r = subprocess.run(["npx", "--yes", "hyperframes@0.6.72", "render", "-c", "overlay.html",
                            "--format", "mov", "-q", "high", "-o", str(MOV)],
                           cwd=ROOT, capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-400:])
    finally:
        OVERLAY.unlink(missing_ok=True)   # jamais laisser 2 compositions racines dans le projet
        print("overlay.html supprime (le projet garde une seule composition racine)")
