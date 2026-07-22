#!/usr/bin/env python3
"""CLÔTURE d'un reel publié : fige l'état dans un tag git, sauvegarde les masters,
réinitialise le plan de travail (compositions, index, derush, renders, work).

Usage : python3 tools/close_reel.py <slug>            (ex. mon-premier-reel)

Aucun compte GitHub ni push requis : tout se passe en local.
  - git installé : le script initialise un repo local si besoin (git init), committe
    lui-même l'état final du reel, puis le tague `reel/<slug>` — l'archive, c'est git ;
  - git absent : l'archive se fait par COPIE du projet (compositions, index, cuts,
    timelines) vers <Vidéos>/reels-publies/<slug>/projet/.

Ensuite, dans les deux cas :
  3. copie les masters (renders/ contenant « FINAL ») vers <Vidéos>/reels-publies/<slug>/ ;
  4. vide renders/ et work/, purge les médias de derush/ (garde les fichiers d'exemple),
     supprime compositions/*.html (garde exemple-section.html) et assets/video/*
     (garde le placeholder base.mp4) ;
  5. écrit un index.html squelette (le prochain reel le régénère via build_master.py) ;
  6. commit « chore: clôture reel <slug> ».

Pourquoi : le studio HyperFrames scanne TOUT le projet — un vieux reel laissé dans le
dossier pollue la sidebar de l'éditeur. Ne JAMAIS archiver un reel dans un sous-dossier
du repo : tout reste récupérable via
  git checkout reel/<slug> -- compositions/ index.html derush/   (ou le dossier projet/ copié)
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




def commit(message: str) -> None:
    run("git", "add", "-A")
    if not run("git", "status", "--porcelain").strip():
        return
    try:
        run("git", "commit", "-m", message)
    except subprocess.CalledProcessError:
        # pas d'identité git configurée (client qui n'utilise pas git) : identité locale neutre
        run("git", "-c", "user.name=Monteur IA", "-c", "user.email=monteur-ia@local",
            "commit", "-m", message)


def archive_with_git(slug: str, tag: str) -> bool:
    """Archive l'état final via un repo git LOCAL (créé si besoin). False si git absent."""
    if shutil.which("git") is None:
        print("• git non installé — archive par copie de fichiers à la place")
        return False
    try:
        run("git", "rev-parse", "--is-inside-work-tree")
    except subprocess.CalledProcessError:
        run("git", "init", "-q")
        print("• repo git local initialisé (aucun compte GitHub requis)")
    commit(f"reel: {slug} (état final du montage au moment du post)")
    if tag in run("git", "tag", "--list", tag):
        print(f"• tag {tag} déjà posé — ok")
    else:
        run("git", "tag", "-a", tag, "-m", f"Reel {slug} : état final du montage au moment du post")
        print(f"• tag {tag} posé")
    return True


def archive_by_copy(slug: str) -> None:
    """Sans git : copie le projet du reel (fichiers légers) vers l'archive."""
    dest = ARCHIVE_BASE / slug / "projet"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "index.html", dest / "index.html")
    shutil.copytree(ROOT / "compositions", dest / "compositions", dirs_exist_ok=True)
    for p in (ROOT / "derush").glob("*.json"):
        shutil.copy2(p, dest / p.name)
    print(f"• projet du reel copié vers {dest}")

def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    tag = f"reel/{slug}"

    use_git = archive_with_git(slug, tag)
    if not use_git:
        archive_by_copy(slug)

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

    if use_git:
        commit(f"chore: clôture reel {slug} (plan de travail réinitialisé, archive = tag {tag})")
        print(f"✅ Reel {slug} clôturé. Récupération : git checkout {tag} -- <chemins>")
    else:
        print(f"✅ Reel {slug} clôturé. Archive : {ARCHIVE_BASE / slug}")


if __name__ == "__main__":
    main()
