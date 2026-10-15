#!/usr/bin/env python3
"""NOUVELLE VIDÉO YOUTUBE : crée le dossier d'une vidéo YouTube (16:9) dans youtube/, prête à monter.

Usage :
    python3 tools/nouvelle_video_youtube.py "<sujet>" [--date AAAA-MM-JJ] [--ouvrir]
    python3 tools/nouvelle_video_youtube.py "<sujet>" --video "<vidéo brute>" [--ouvrir]
    python3 tools/nouvelle_video_youtube.py "<sujet>" --brief "<la demande du client>" --ouvrir
    python3 tools/nouvelle_video_youtube.py "<sujet>" --depuis "<dossier d'une vidéo YouTube>"

Une vidéo YouTube = un projet HyperFrames autonome, comme un Reel, mais au format 1920x1080 et
avec ses propres règles (skill `youtube`). youtube/<nom>/ reçoit le gabarit templates/youtube/
(fichiers .demo sans leur suffixe, outils du 16:9) et les outils de la maison qui ne dépendent pas
du format ; `npm run sync` y ajoute le style, les polices, GSAP et les instructions.

Le nom du dossier est celui que l'app HyperFrames affiche : « <sujet> · <date> · <client> ».
Avec --video, la vidéo brute est notée dans work/brief.md (la copie faite par l'app dans l'accueil
part dans derush/ de la vidéo) ; avec --brief, la demande du client y est notée (script à écrire).

Ne touche ni aux Reels, ni aux autres vidéos, ni aux réglages du client. Marche depuis la maison,
l'accueil, un Reel ou une autre vidéo (l'outil retrouve la maison tout seul).
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lieux import MAISON  # noqa: E402
from nouveau_reel import SANS, copie_de_l_accueil, etiquette, noter_brief, propre  # noqa: E402

GABARIT = MAISON / "templates" / "youtube"
VIDEOS = MAISON / "youtube"
DEMO_SUFFIX = ".demo"
DOSSIERS = ["derush", "work", "exports", "assets/video"]
# Outils de la maison utiles en 16:9 tels quels. Les deux derniers sont adaptés à chaque vidéo
# (coupes, mots du dérush) ; les autres suivent la maison (scripts/sync.mjs, OUTILS_COMMUNS_YOUTUBE).
# Jamais un outil vertical des Reels : la vidéo a les siens, de même nom, dans templates/youtube/tools/.
OUTILS_MAISON = ["lieux.py", "brand_style.py", "sons.py", "niveau_final.py", "ecarts_derush.py", "ranger_reel.py",
                 "prises.py", "cut_boundaries.py", "build_words.py"]
# Outils d'une extension, copiés seulement s'ils sont installés (Pack SFX : sonoriser la vidéo), et à
# partir de la version 1.2.0 du pack, la première qui connaît les vidéos YouTube (même règle dans
# scripts/sync.mjs). Plus ancien, les sons se posent par tools/build_sfx.py de la vidéo.
OUTILS_EXTENSIONS = ["sfx.py", "sfx_mix.py"]
PACK_SFX_YOUTUBE = (1, 2, 0)


def version_pack_sfx() -> str | None:
    """La version du Pack SFX installée dans le dossier Monteur IA (manifeste de son installateur)."""
    try:
        return str(json.loads((MAISON / "assets/sfx/.pack-sfx-manifest.json").read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def pack_sfx_pour_youtube() -> bool:
    v = version_pack_sfx()
    try:
        return v is not None and tuple(int(x) for x in v.split(".")[:3]) >= PACK_SFX_YOUTUBE
    except ValueError:
        return False


def nom_de_la_video(sujet: str, date: str) -> str:
    return " · ".join(propre(p) for p in (sujet, date, etiquette()) if p and propre(p))


def dossier_libre(nom: str) -> Path:
    """youtube/<nom>, ou youtube/<nom> (2), (3)… : une vidéo existante n'est jamais écrasée."""
    candidat, n = VIDEOS / nom, 2
    while candidat.exists():
        candidat, n = VIDEOS / f"{nom} ({n})", n + 1
    return candidat


def creer(sujet: str, date: str, depuis: Path | None = None) -> Path:
    if not (GABARIT / f"index.html{DEMO_SUFFIX}").exists():
        sys.exit("ERREUR : gabarit de vidéo YouTube introuvable (templates/youtube/). Rien n'a été créé.")
    video = dossier_libre(nom_de_la_video(sujet, date))
    if depuis:
        shutil.copytree(depuis, video, ignore=lambda _d, noms: [n for n in noms if n in SANS])
    else:
        video.mkdir(parents=True)
        for src in sorted(GABARIT.rglob(f"*{DEMO_SUFFIX}")):
            cible = video / src.relative_to(GABARIT).as_posix()[:-len(DEMO_SUFFIX)]
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, cible)
        (video / "tools").mkdir(exist_ok=True)
        for outil in sorted((GABARIT / "tools").glob("*.py")):
            shutil.copy2(outil, video / "tools" / outil.name)
        for nom in OUTILS_MAISON:
            shutil.copy2(MAISON / "tools" / nom, video / "tools" / nom)
        for nom in OUTILS_EXTENSIONS if pack_sfx_pour_youtube() else []:
            if (MAISON / "tools" / nom).is_file():
                shutil.copy2(MAISON / "tools" / nom, video / "tools" / nom)
    for d in DOSSIERS:
        (video / d).mkdir(parents=True, exist_ok=True)
    shutil.copy2(MAISON / "hyperframes.json", video / "hyperframes.json")
    maintenant = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    meta = {"id": video.name, "name": video.name, "createdAt": maintenant,
            "monteurIa": {"lieu": "youtube", "etat": "en-cours", "sujet": sujet, "date": date, "format": "16:9"}}
    (video / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paquet = {"name": "video-youtube-monteur-ia", "private": True, "type": "module",
              "scripts": {"dev": "hyperframes preview", "check": "hyperframes check",
                          "render": "hyperframes render -o exports/FINAL.mp4"}}
    (video / "package.json").write_text(json.dumps(paquet, indent=2) + "\n", encoding="utf-8")
    return video


def poser_la_video(dossier: Path, brute: Path) -> str:
    """Range la vidéo brute (copie de l'accueil -> derush/) et la note dans work/brief.md."""
    deplacee = copie_de_l_accueil(brute)
    if deplacee:
        cible, n = dossier / "derush" / brute.name, 2
        while cible.exists():
            cible, n = dossier / "derush" / f"{brute.stem} ({n}){brute.suffix}", n + 1
        shutil.move(str(brute), str(cible))
        brute = cible
    brief = dossier / "work" / "brief.md"
    debut = brief.read_text(encoding="utf-8") if brief.exists() else "# Brief\n\n"
    brief.write_text(debut + f"Vidéo brute : {brute.resolve()}\n", encoding="utf-8")
    return (f"vidéo rangée dans la vidéo YouTube : {brute.relative_to(dossier)} (la copie faite par l'app)"
            if deplacee else f"vidéo notée dans work/brief.md : {brute.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crée le dossier d'une nouvelle vidéo YouTube.")
    parser.add_argument("sujet", help="Le sujet de la vidéo, en quelques mots.")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="AAAA-MM-JJ (défaut : aujourd'hui)")
    parser.add_argument("--ouvrir", action="store_true", help="Ouvre la vidéo dans l'app HyperFrames (Mac).")
    parser.add_argument("--depuis", type=Path, help="Dossier d'une vidéo YouTube existante : la nouvelle en est une copie.")
    parser.add_argument("--video", type=Path, help="La vidéo brute (ex. celle glissée dans l'accueil).")
    parser.add_argument("--brief", help="La demande du client (script à écrire, idées, liens), notée dans work/brief.md.")
    args = parser.parse_args()
    if not propre(args.sujet):
        sys.exit("ERREUR : donne un sujet à la vidéo, en quelques mots.")
    try:
        datetime.date.fromisoformat(args.date)
    except ValueError:
        sys.exit("ERREUR : la date s'écrit AAAA-MM-JJ.")
    depuis = args.depuis.expanduser().resolve() if args.depuis else None
    if depuis and (depuis / "meta.json").is_file():
        lieu = (json.loads((depuis / "meta.json").read_text(encoding="utf-8")).get("monteurIa") or {}).get("lieu")
        if lieu != "youtube":
            sys.exit(f"ERREUR : {depuis.name} n'est pas une vidéo YouTube (c'est un projet « {lieu} »). Rien n'a été créé.")
    elif depuis:
        sys.exit(f"ERREUR : {depuis} n'est pas le dossier d'une vidéo YouTube. Rien n'a été créé.")
    brute = args.video.expanduser().absolute() if args.video else None
    if brute and not brute.is_file():
        sys.exit(f"ERREUR : vidéo introuvable : {brute}. Rien n'a été créé.")

    video = creer(args.sujet, args.date, depuis)
    print(f"• vidéo YouTube créée : {video.relative_to(MAISON)}" + (f" (copie de « {depuis.name} »)" if depuis else ""))
    if args.brief and args.brief.strip():
        noter_brief(video, args.brief)
        print("• demande du client notée dans work/brief.md (lue en début de conversation)")
    if brute:
        print("• " + poser_la_video(video, brute))
    sync = subprocess.run(["node", "scripts/sync.mjs"], cwd=MAISON, capture_output=True, encoding="utf-8", errors="replace")
    if sync.returncode != 0:
        print(sync.stdout[-2000:] + sync.stderr[-2000:])
        sys.exit("ERREUR : `npm run sync` a échoué ; le dossier de la vidéo existe mais sans instructions.")
    print("• style, polices et instructions ajoutés (npm run sync)")
    if (MAISON / "tools" / "sfx_mix.py").is_file() and not pack_sfx_pour_youtube():
        print(f"• Pack SFX {version_pack_sfx() or '(version inconnue)'} : il ne sonorise pas encore les vidéos YouTube "
              "(il faut la 1.2.0 ou plus). À dire au client : le retélécharger depuis sa formation (module « Mises "
              "à jour », bouton jaune), puis mettre Monteur IA à jour. D'ici là, les sons se posent avec "
              "tools/build_sfx.py de la vidéo (les sons du pack aussi, par leur chemin pack/…).")
    if args.ouvrir:
        app = subprocess.run(["node", "scripts/app-hyperframes.mjs", "ouvrir", str(video)],
                             cwd=MAISON, capture_output=True, encoding="utf-8", errors="replace")
        print("• " + (app.stdout.strip() or app.stderr.strip()))
    print(f"✅ Prête : {video}")


if __name__ == "__main__":
    main()
