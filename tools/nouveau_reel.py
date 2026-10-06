#!/usr/bin/env python3
"""NOUVEAU REEL : crée le dossier d'un Reel dans reels/, prêt à monter, et l'ouvre dans l'app.

Usage :
    python3 tools/nouveau_reel.py "<sujet>" [--date AAAA-MM-JJ] [--ouvrir]
    python3 tools/nouveau_reel.py "<sujet>" --depuis "<dossier d'un Reel>"   # variante d'un Reel
    python3 tools/nouveau_reel.py "<sujet>" --video "<vidéo brute>" [--ouvrir]  # avec sa vidéo

Un Reel = un projet HyperFrames autonome. reels/<nom>/ reçoit le plan de travail de départ
(templates/demo/, sans le suffixe .demo) et une copie des outils de la maison ; `npm run sync`
y ajoute ensuite le style (brand/), les polices, GSAP et les instructions (CLAUDE.md, AGENTS.md).
Le nom du dossier est celui que l'app HyperFrames affiche : « <sujet> · <date> · <client> ». Le sujet
vient en premier : la liste des projets de l'app coupe les noms vers 25 caractères.

Avec --depuis, le nouveau Reel part d'une copie d'un Reel existant (montage, médias, outils
adaptés), sans ses exports ni ce que l'app y a mis. C'est la façon de dupliquer un Reel : le
bouton Duplicate de l'app copie le dossier hors du dossier Monteur IA, où ses outils, ses
réglages et ses sons partagés ne sont plus.

Avec --video, la vidéo brute est notée dans work/brief.md du Reel. Glissée dans l'accueil de l'app,
elle y a été recopiée (sans limite de taille) : cette copie part dans derush/ du Reel, pour ne pas
s'empiler dans l'accueil ; « ranger --alleger » la libère avec les autres rushes. Une vidéo prise
ailleurs (le fichier du client) n'est jamais déplacée.

Ne touche ni aux autres Reels ni aux réglages du client. Marche depuis la maison, l'accueil ou un
autre Reel (l'outil retrouve la maison tout seul).
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lieux import MAISON, config  # noqa: E402

DEMO = MAISON / "templates" / "demo"
DEMO_SUFFIX = ".demo"
REELS = MAISON / "reels"
# Dossiers vides attendus par le pipeline (exports/ remplace renders/, réservé par l'app).
DOSSIERS = ["derush", "work", "exports", "assets/video"]
# Noms de dossier Monteur IA laissés par défaut : ils ne disent rien du client.
NOMS_PAR_DEFAUT = {"monteur-ia", "monteur-ia-main", "monteur ia", "monteur-ia-template"}
# Variante d'un Reel : ni ce que l'app ou les rendus y ont mis, ni ses instructions (régénérées).
SANS = {".thumbnails", ".hyperframes", ".waveform-cache", ".transcode-cache", "renders", "exports", "node_modules",
        "__pycache__", "meta.json", "project.json", "CLAUDE.md", "AGENTS.md", ".DS_Store"}
# Caractères refusés par l'app (« : », « / », « \ ») ou par Windows.
INTERDITS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def propre(texte: str, longueur: int = 60) -> str:
    texte = re.sub(r"\s+", " ", INTERDITS.sub("-", str(texte))).strip(" .-")
    return texte[:longueur].rstrip(" .-")


def etiquette() -> str | None:
    """Le client ou la marque, pour reconnaître ses Reels dans l'app : `brand.name`, sinon le nom du
    dossier Monteur IA s'il a été renommé (ex. « Monteur IA - Client A »)."""
    nom = str((config().get("brand") or {}).get("name") or "").strip()
    if nom:
        return nom
    return None if MAISON.name.strip().lower() in NOMS_PAR_DEFAUT else MAISON.name


def nom_du_reel(sujet: str, date: str) -> str:
    return " · ".join(propre(p) for p in (sujet, date, etiquette()) if p and propre(p))


def dossier_libre(nom: str) -> Path:
    """reels/<nom>, ou reels/<nom> (2), (3)… : un Reel existant n'est jamais écrasé."""
    candidat, n = REELS / nom, 2
    while candidat.exists():
        candidat, n = REELS / f"{nom} ({n})", n + 1
    return candidat


def outils_de_la_maison() -> list[Path]:
    return sorted(p for p in (MAISON / "tools").iterdir()
                  if p.is_file() and p.suffix in (".py", ".sh"))


def creer(sujet: str, date: str, depuis: Path | None = None) -> Path:
    if not (DEMO / f"index.html{DEMO_SUFFIX}").exists():
        sys.exit(f"ERREUR : gabarit de Reel introuvable ({DEMO.relative_to(MAISON)}/). Rien n'a été créé.")
    reel = dossier_libre(nom_du_reel(sujet, date))
    if depuis:
        # Variante : tout le travail du Reel d'origine, ses outils adaptés compris.
        shutil.copytree(depuis, reel, ignore=lambda _dossier, noms: [n for n in noms if n in SANS])
    else:
        reel.mkdir(parents=True)
        # Plan de travail de départ : démo de 8 s, placeholder base.mp4, coupes d'exemple.
        for src in sorted(DEMO.rglob(f"*{DEMO_SUFFIX}")):
            cible = reel / src.relative_to(DEMO).as_posix()[:-len(DEMO_SUFFIX)]
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, cible)
        # Outils : les génériques sont rafraîchis par `npm run sync` ; ceux dont l'en-tête les dit
        # adaptés à chaque Reel (sections, sous-titres, SFX…) appartiennent ensuite à ce Reel seul.
        (reel / "tools").mkdir(exist_ok=True)
        for outil in outils_de_la_maison():
            shutil.copy2(outil, reel / "tools" / outil.name)
    for d in DOSSIERS:
        (reel / d).mkdir(parents=True, exist_ok=True)
    shutil.copy2(MAISON / "hyperframes.json", reel / "hyperframes.json")
    maintenant = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    meta = {"id": reel.name, "name": reel.name, "createdAt": maintenant,
            "monteurIa": {"lieu": "reel", "etat": "en-cours", "sujet": sujet, "date": date}}
    (reel / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paquet = {"name": "reel-monteur-ia", "private": True, "type": "module",
              "scripts": {"dev": "hyperframes preview", "check": "hyperframes check", "render": "hyperframes render -o exports/FINAL.mp4"}}
    (reel / "package.json").write_text(json.dumps(paquet, indent=2) + "\n", encoding="utf-8")
    return reel


def copie_de_l_accueil(video: Path) -> bool:
    """Vrai si la vidéo est la copie que l'app a faite en la recevant dans l'accueil (assets/ d'un
    projet « accueil » de cette maison) : c'est la seule qu'on se permet de déplacer."""
    try:
        rel = video.resolve().relative_to(MAISON.resolve())
    except ValueError:
        return False
    if len(rel.parts) < 3 or rel.parts[1] != "assets":
        return False
    try:
        meta = json.loads((MAISON / rel.parts[0] / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (meta.get("monteurIa") or {}).get("lieu") == "accueil"


def poser_la_video(reel: Path, video: Path) -> str:
    """Range la vidéo brute (copie de l'accueil -> derush/ du Reel) et la note dans work/brief.md."""
    deplacee = copie_de_l_accueil(video)
    if deplacee:
        cible, n = reel / "derush" / video.name, 2
        while cible.exists():
            cible, n = reel / "derush" / f"{video.stem} ({n}){video.suffix}", n + 1
        shutil.move(str(video), str(cible))
        video = cible
    brief = reel / "work" / "brief.md"
    ligne = f"Vidéo brute : {video.resolve()}\n"
    brief.write_text((brief.read_text(encoding="utf-8") if brief.exists() else "# Brief\n\n") + ligne, encoding="utf-8")
    return (f"vidéo rangée dans le Reel : {video.relative_to(reel)} (la copie faite par l'app dans l'accueil)"
            if deplacee else f"vidéo notée dans work/brief.md : {video.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crée le dossier d'un nouveau Reel.")
    parser.add_argument("sujet", help="Le sujet du Reel, en quelques mots (ex. « Méliès »).")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="AAAA-MM-JJ (défaut : aujourd'hui)")
    parser.add_argument("--ouvrir", action="store_true", help="Ouvre le Reel dans l'app HyperFrames (Mac).")
    parser.add_argument("--depuis", type=Path, help="Dossier d'un Reel existant : le nouveau en est une copie.")
    parser.add_argument("--video", type=Path, help="La vidéo brute du Reel (ex. celle glissée dans l'accueil).")
    args = parser.parse_args()
    if not propre(args.sujet):
        sys.exit("ERREUR : donne un sujet au Reel, en quelques mots.")
    try:
        datetime.date.fromisoformat(args.date)
    except ValueError:
        sys.exit("ERREUR : la date s'écrit AAAA-MM-JJ.")

    depuis = args.depuis.expanduser().resolve() if args.depuis else None
    if depuis and not (depuis / "index.html").is_file():
        sys.exit(f"ERREUR : {depuis} n'est pas le dossier d'un Reel (il n'a pas d'index.html). Rien n'a été créé.")
    if depuis and depuis == MAISON:
        sys.exit("ERREUR : --depuis attend le dossier d'un Reel, pas le dossier Monteur IA. Rien n'a été créé.")
    video = args.video.expanduser().absolute() if args.video else None
    if video and not video.is_file():
        sys.exit(f"ERREUR : vidéo introuvable : {video}. Rien n'a été créé.")
    reel = creer(args.sujet, args.date, depuis)
    print(f"• Reel créé : {reel.relative_to(MAISON)}" + (f" (copie de « {depuis.name} »)" if depuis else ""))
    if video:
        print("• " + poser_la_video(reel, video))
    sync = subprocess.run(["node", "scripts/sync.mjs"], cwd=MAISON, capture_output=True, encoding="utf-8", errors="replace")
    if sync.returncode != 0:
        print(sync.stdout[-2000:] + sync.stderr[-2000:])
        sys.exit("ERREUR : `npm run sync` a échoué ; le dossier du Reel existe mais sans instructions.")
    print("• style, polices et instructions ajoutés (npm run sync)")
    if args.ouvrir:
        app = subprocess.run(["node", "scripts/app-hyperframes.mjs", "ouvrir", str(reel)],
                             cwd=MAISON, capture_output=True, encoding="utf-8", errors="replace")
        print("• " + (app.stdout.strip() or app.stderr.strip()))
    print(f"✅ Prêt : {reel}")


if __name__ == "__main__":
    main()
