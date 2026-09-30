#!/usr/bin/env python3
"""CLÔTURE d'un reel publié : fige l'état dans un tag git, sauvegarde les masters, puis remet
le plan de travail dans l'état exact d'un ZIP neuf.

Usage : python3 tools/close_reel.py <slug>            (ex. mon-premier-reel)

Aucun compte GitHub ni push requis : tout se passe en local.
  - git installé : le script initialise un repo local si besoin (git init), committe
    lui-même l'état final du reel, puis le tague `reel/<slug>` — l'archive, c'est git ;
  - git absent : l'archive se fait par COPIE du projet (compositions, index, cuts, script de
    dérush, outils du reel) vers <Vidéos>/reels-publies/<slug>/projet/.

Ensuite, dans les deux cas :
  3. copie les masters (renders/ contenant « FINAL ») vers <Vidéos>/reels-publies/<slug>/ ;
  4. vide renders/, work/, derush/, compositions/ et assets/video/, et supprime ce que les
     outils laissent à la racine (snapshots/, probe/, overlay.html, transcript.json, caches
     du studio). Seule exception : si le débrief de la première vidéo n'a pas eu lieu, une
     note « débrief à faire » reste dans work/premiere-video.md ;
  5. remet les fichiers livrés depuis templates/demo/ : master d'aperçu, sous-titres et
     section d'exemple, cuts de démo, placeholder base.mp4, outils du reel (sections.py,
     build_words.py, montage_captions.py, cut_boundaries.py, build_sfx.py, build_master.py) ;
  6. commit « chore: clôture reel <slug> ».

Ne touche jamais aux réglages du client : brand.config.json, brand/, assets/ hors
assets/video/ (images, logos, musique, SFX), reels-publies/.

Pourquoi remettre les outils : le pipeline les adapte à chaque reel (CUTS_PATH, LAYOUT, MANUAL,
EVENTS…). Laissés tels quels, le reel suivant repartirait des réglages de l'ancien, et
derush/build_derush.py laissé en place ferait relire ses prises à cut_boundaries.py.

Ne JAMAIS archiver un reel dans un sous-dossier du repo (le studio HyperFrames scanne tout le
projet et polluerait la sidebar de l'éditeur) : tout reste récupérable via
  git checkout reel/<slug> -- compositions/ index.html derush/ tools/   (ou le dossier projet/ copié)
Les médias non versionnés (dérush, renders intermédiaires) sont perdus — c'est le but ;
seuls les masters « FINAL » sont copiés en lieu sûr avant.
"""
import json
import os
import subprocess
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = "Videos" if os.name == "nt" else "Movies"
ARCHIVE_BASE = Path.home() / VIDEOS_DIR / "reels-publies"

# Version livrée de chaque fichier du plan de travail : templates/demo/<chemin>.demo
DEMO = ROOT / "templates" / "demo"
DEMO_SUFFIX = ".demo"

# Dossiers propres à un reel : vidés entièrement (seul .gitkeep reste), puis la démo est remise.
WORK_DIRS = ["renders", "work", "derush", "compositions", "assets/video"]
# Ce que les outils laissent à la racine et qu'un ZIP neuf ne contient pas.
ROOT_LEFTOVERS = ["snapshots", "probe", ".thumbnails", ".waveform-cache", "overlay.html",
                  "transcript.json"]

# Suivi de la première vidéo. Si son débrief n'a pas eu lieu (repoussé par le client), une note
# propre remplace le suivi purgé avec work/ : le débrief est reproposé une fois au reel suivant.
FIRST_VIDEO_NOTE = ROOT / "work" / "premiere-video.md"
DEBRIEF_NOTE = """# Première vidéo : débrief à faire

La première vidéo a été publiée (reel {slug}) sans que le débrief ait eu lieu.
Le reproposer une fois en début de conversation : skill `setup`,
`references/debrief-premiere-video.md`. La vidéo est publiée et son projet archivé : le débrief
sert seulement à retenir ses préférences pour les prochaines, sans remonter celle-ci.
Supprimer ce fichier ensuite, qu'il accepte ou non.
"""


def debrief_pending() -> bool:
    """Suivi de première vidéo présent et débrief pas enregistré (setup.firstVideoDone)."""
    if not FIRST_VIDEO_NOTE.exists():
        return False
    try:
        config = json.loads((ROOT / "brand.config.json").read_text(encoding="utf-8"))
        return (config.get("setup") or {}).get("firstVideoDone") is not True
    except (OSError, ValueError, AttributeError):
        return True


def run(*cmd: str) -> str:
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout


def remove(p: Path) -> None:
    if p.is_dir() and not p.is_symlink():
        shutil.rmtree(p)
    elif p.exists() or p.is_symlink():
        p.unlink()


def purge(directory: Path) -> None:
    if not directory.exists():
        return
    for p in directory.iterdir():
        if p.name != ".gitkeep":
            remove(p)


def demo_files() -> list:
    """(copie de référence, destination dans le projet) pour chaque fichier livré."""
    return [(src, ROOT / src.relative_to(DEMO).as_posix()[:-len(DEMO_SUFFIX)])
            for src in sorted(DEMO.rglob(f"*{DEMO_SUFFIX}"))]


def check_demo() -> None:
    """Refuse de commencer si la copie de référence manque : sinon on purgerait sans rien remettre."""
    targets = {dest.relative_to(ROOT).as_posix() for _, dest in demo_files()}
    missing = {"index.html", "assets/video/base.mp4", "tools/sections.py"} - targets
    if missing:
        sys.exit(f"ERREUR : copie de référence incomplète dans {DEMO.relative_to(ROOT)}/ "
                 f"(manque : {', '.join(sorted(missing))}). Rien n'a été modifié. "
                 "Récupère le dossier templates/demo/ depuis la dernière version du template.")


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
    for pattern in ("*.json", "*.py"):
        for p in (ROOT / "derush").glob(pattern):
            shutil.copy2(p, dest / p.name)
    # Les outils adaptés au reel (sections, sous-titres, SFX…) : de quoi le reconstruire.
    (dest / "tools").mkdir(exist_ok=True)
    for _, target in demo_files():
        if target.parent.name == "tools" and target.exists():
            shutil.copy2(target, dest / "tools" / target.name)
    print(f"• projet du reel copié vers {dest}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    tag = f"reel/{slug}"
    check_demo()

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

    keep_debrief = debrief_pending()
    for d in WORK_DIRS:
        purge(ROOT / d)
    print(f"• {', '.join(d + '/' for d in WORK_DIRS)} vidés")
    if keep_debrief:
        FIRST_VIDEO_NOTE.write_text(DEBRIEF_NOTE.format(slug=slug), encoding="utf-8")
        print("• note « débrief à faire » conservée dans work/premiere-video.md")
    for name in ROOT_LEFTOVERS:
        remove(ROOT / name)
    print("• restes à la racine supprimés (snapshots/, probe/, overlay.html…)")

    for src, target in demo_files():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    print("• fichiers de démo remis : master d'aperçu, placeholder base.mp4, outils du reel")

    if use_git:
        commit(f"chore: clôture reel {slug} (plan de travail remis à neuf, archive = tag {tag})")
        print(f"✅ Reel {slug} clôturé. Récupération : git checkout {tag} -- <chemins>")
    else:
        print(f"✅ Reel {slug} clôturé. Archive : {ARCHIVE_BASE / slug}")


if __name__ == "__main__":
    main()
