#!/usr/bin/env python3
"""CLÔTURE d'un reel publié : fige l'état dans un tag git, sauvegarde les masters,
réinitialise le plan de travail (compositions, index, derush, renders, work).

Usage : python3 tools/close_reel.py <slug>            (ex. mon-premier-reel)

Ce que fait le script, dans l'ordre :
  1. refuse de tourner si le working tree n'est pas propre (commit d'abord) ;
  2. tag `reel/<slug>` sur HEAD (sauté s'il existe déjà) — l'archive, c'est git ;
  3. copie les masters (renders/ contenant « FINAL ») vers <Vidéos>/reels-publies/<slug>/ ;
  4. vide renders/ et work/, purge les médias de derush/ (garde les fichiers d'exemple),
     supprime compositions/*.html (garde exemple-section.html) et assets/video/*
     (garde le placeholder base.mp4) ;
  5. écrit un index.html squelette (le prochain reel le régénère via build_master.py) ;
  6. commit « chore: clôture reel <slug> ».

Pourquoi : le studio HyperFrames scanne TOUT le projet — un vieux reel laissé dans le
dossier pollue la sidebar de l'éditeur. Ne JAMAIS archiver un reel dans un sous-dossier
du repo : tout ce qui est versionné reste récupérable via
  git checkout reel/<slug> -- compositions/ index.html derush/
Les médias non versionnés (dérush, renders intermédiaires) sont perdus — c'est le but ;
seuls les masters « FINAL » sont copiés en lieu sûr avant.
"""
import os
import subprocess
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = "Videos" if os.name == "nt" else "Movies"
ARCHIVE_BASE = Path.home() / VIDEOS_DIR / "reels-publies"

# Fichiers du template à ne jamais purger (démo / placeholders versionnés)
KEEP_COMPOSITIONS = {"exemple-section.html"}
KEEP_DERUSH = {"README-exemple.md", "exemple_cuts.json", "build_derush.py"}
KEEP_VIDEO = {"base.mp4"}

SKELETON = """<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1080, height=1920">
    <script src="assets/vendor/gsap.min.js"></script>
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #202022; }
    </style>
  </head>
  <body>
    <!-- MASTER SQUELETTE (reel précédent clôturé) — régénéré par tools/build_master.py au prochain reel. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="10" data-fps="30" data-width="1080" data-height="1920">
      <div id="bgbase" class="clip" data-start="0" data-duration="10" data-track-index="0" style="position:absolute; inset:0; background:#202022;"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
"""


def run(*cmd: str) -> str:
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout


def purge(directory: Path, keep: set) -> None:
    if not directory.exists():
        return
    for p in directory.iterdir():
        if p.name in keep or p.name == ".gitkeep":
            continue
        p.unlink() if p.is_file() else shutil.rmtree(p)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    tag = f"reel/{slug}"

    if run("git", "status", "--porcelain").strip():
        sys.exit("❌ Working tree pas propre : committer l'état final du reel AVANT la clôture.")

    if tag in run("git", "tag", "--list", tag):
        print(f"• tag {tag} déjà posé — ok")
    else:
        run("git", "tag", "-a", tag, "-m", f"Reel {slug} : état final du montage au moment du post")
        print(f"• tag {tag} posé sur HEAD")

    # Masters en lieu sûr
    dest = ARCHIVE_BASE / slug
    renders = ROOT / "renders"
    finals = [p for p in renders.glob("*") if p.is_file() and "FINAL" in p.name]
    if finals:
        dest.mkdir(parents=True, exist_ok=True)
        for p in finals:
            shutil.copy2(p, dest / p.name)
            print(f"• master copié : {p.name} -> {dest}")
    else:
        print("• aucun master « FINAL » dans renders/ (rien à copier)")

    purge(renders, set())
    print("• renders/ vidé")
    purge(ROOT / "work", set())
    print("• work/ vidé")
    purge(ROOT / "derush", KEEP_DERUSH)
    print("• derush/ purgé (fichiers d'exemple conservés)")
    for p in (ROOT / "compositions").glob("*.html"):
        if p.name not in KEEP_COMPOSITIONS:
            p.unlink()
    print("• compositions/*.html supprimées (exemple-section.html conservée)")
    purge(ROOT / "assets" / "video", KEEP_VIDEO)
    print("• assets/video/ vidé (placeholder base.mp4 conservé)")

    (ROOT / "index.html").write_text(SKELETON, encoding="utf-8")
    print("• index.html remplacé par le squelette")

    run("git", "add", "-A")
    run("git", "commit", "-m", f"chore: clôture reel {slug} (plan de travail réinitialisé, archive = tag {tag})")
    print(f"✅ Reel {slug} clôturé. Récupération : git checkout {tag} -- <chemins>")


if __name__ == "__main__":
    main()
