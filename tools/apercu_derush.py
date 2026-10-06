#!/usr/bin/env python3
"""APERCU DU DERUSH : pose la video coupee dans le montage du Reel, plein ecran, sans motion.

Usage (depuis le dossier du Reel) :
    python3 tools/apercu_derush.py derush/<cut>.mp4              # apres le derush (etape 3)
    python3 tools/apercu_derush.py derush/<cut>_enhanced.mp4     # apres le nettoyage Adobe
    python3 tools/apercu_derush.py derush/<cut>.mp4 --ecraser    # meme sur un montage deja construit

Pourquoi : le client valide le derush a l'oreille. Dans l'app HyperFrames, il le regarde la ou il
regardera tout le montage, dans le lecteur et sur la timeline, pas dans le Finder. Hors de l'app,
l'apercu sert aussi (npm run dev), en plus du fichier revele.

Ce que fait l'outil : une copie legere du cut en 1080x1920 (work/apercu-derush.mp4, lue sans ramer
par le lecteur de l'app), puis un index.html qui la montre plein ecran, voix comprise. Le modele de
demonstration ou un ancien apercu est remplace ; un montage deja construit (sections) ne l'est pas
sans --ecraser, et l'index d'avant est garde dans work/index-avant-apercu.html.
L'etape 4 (montage) remplace cet apercu : python3 tools/build_master.py --write.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
APERCU = ROOT / "work" / "apercu-derush.mp4"
MARQUE = "APERCU DU DERUSH"


def die(msg: str) -> None:
    print("ERREUR :", msg)
    sys.exit(1)


def duree(path: pathlib.Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, encoding="utf-8", errors="replace").stdout.strip()
    try:
        return round(float(out), 3)
    except ValueError:
        die(f"duree illisible : {path}")


def page(src: str, dur: float) -> str:
    return f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <script src="assets/vendor/gsap.min.js"></script>
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--brand-bg); }}
      #derush {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <!-- {MARQUE} (tools/apercu_derush.py) : la video coupee, plein ecran, sans motion, pour la
         valider a l'oreille. Le montage (etape 4) remplace ce fichier : python3 tools/build_master.py --write. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-fps="30" data-width="1080" data-height="1920">
      <video id="derush" class="clip" src="{src}" muted playsinline data-start="0" data-media-start="0" data-duration="{dur}" data-track-index="1"></video>
      <audio id="vo" src="{src}" data-start="0" data-duration="{dur}" data-track-index="2" data-volume="1"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        die("donne la video coupee : python3 tools/apercu_derush.py derush/<cut>.mp4")
    cut = (pathlib.Path.cwd() / args[0]).resolve()
    if not cut.is_file():
        die(f"video introuvable : {args[0]}")
    try:
        cut.relative_to(ROOT.resolve())
    except ValueError:
        die(f"{cut} n'est pas dans ce Reel : le derush s'ecrit dans derush/ du Reel.")
    actuel = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    if 'class="face-bottom"' in actuel and MARQUE not in actuel and "--ecraser" not in sys.argv:
        die("index.html est deja un montage construit (sections) : l'apercu le remplacerait. Relance avec "
            "--ecraser seulement si le montage doit repartir du derush (python3 tools/build_master.py --write le refera).")
    APERCU.parent.mkdir(exist_ok=True)
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(cut), "-map", "0:v:0", "-map", "0:a:0?",
                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(APERCU)],
                       capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        die(f"ffmpeg a echoue : {r.stderr[-600:]}")
    if actuel and MARQUE not in actuel:
        shutil.copyfile(INDEX, ROOT / "work" / "index-avant-apercu.html")
    INDEX.write_text(page(APERCU.relative_to(ROOT).as_posix(), duree(APERCU)), encoding="utf-8")
    print(f"Apercu du derush pose dans index.html : {cut.relative_to(ROOT.resolve()).as_posix()}, {duree(APERCU)} s.")
    print("Dans l'app HyperFrames : le client le regarde dans le lecteur. Etape 4 : python3 tools/build_master.py --write.")


if __name__ == "__main__":
    main()
