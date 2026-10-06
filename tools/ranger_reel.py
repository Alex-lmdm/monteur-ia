#!/usr/bin/env python3
"""RANGER UN REEL : après publication, met les vidéos finales en lieu sûr et marque le Reel publié.

Usage (depuis le dossier du Reel) :
    python3 tools/ranger_reel.py [--alleger]

- copie les vidéos finales vers <Vidéos>/reels-publies/<nom du Reel>/ : les fichiers dont le nom
  contient « FINAL » (exports/, renders/) et le dernier export réussi du bouton Export de l'app
  HyperFrames (renders/<id>.mp4, décrit par renders/<id>.meta.json), copié en « <nom du Reel>.mp4 » ;
- marque le Reel publié (meta.json : monteurIa.etat = "publie") : il garde le style qu'il avait
  au moment du post et prouve que la première vidéo est derrière nous ;
- si le débrief de la première vidéo n'a pas eu lieu, pose la note « débrief à faire » dans le
  dossier Monteur IA (work/premiere-video.md) : elle est reproposée au Reel suivant ;
- --alleger : efface en plus ce qui pèse et se refait (médias du dérush, fichiers de travail,
  rendus intermédiaires, snapshots). Le montage, ses vidéos et les vidéos finales restent.

Le dossier du Reel reste en place : il se rouvre d'un clic dans l'app HyperFrames.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lieux import MAISON, config, reel as reel_courant  # noqa: E402

VIDEOS_DIR = "Videos" if os.name == "nt" else "Movies"
ARCHIVE_BASE = Path.home() / VIDEOS_DIR / "reels-publies"
MEDIAS = {".mp4", ".mov", ".m4a", ".mp3", ".wav", ".aac", ".mkv", ".webm"}

DEBRIEF_NOTE = """# Première vidéo : débrief à faire

La première vidéo a été publiée (Reel « {nom} ») sans que le débrief ait eu lieu.
Le reproposer une fois en début de conversation : skill `setup`,
`references/debrief-premiere-video.md`. La vidéo est publiée : le débrief sert seulement à
retenir ses préférences pour les prochaines, sans remonter celle-ci.
Supprimer ce fichier ensuite, qu'il accepte ou non.
"""


def finales(reel: Path) -> list[Path]:
    return sorted(p for d in ("exports", "renders") if (reel / d).is_dir()
                  for p in (reel / d).iterdir() if p.is_file() and "FINAL" in p.name)


def export_app(reel: Path) -> Path | None:
    """Dernier export réussi du bouton Export de l'app : l'app rend dans renders/<id>.<ext>, en copie
    une dans Téléchargements et note le résultat dans renders/<id>.meta.json (status « complete »).
    Aucun nom ne contient « FINAL » : sans ceci, « c'est posté » ne rangerait rien après un Export."""
    renders = reel / "renders"
    if not renders.is_dir():
        return None
    fiches = sorted(renders.glob("*.meta.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for fiche in fiches:
        try:
            meta = json.loads(fiche.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(meta, dict) or meta.get("status") != "complete":
            continue
        base = fiche.name[: -len(".meta.json")]
        for ext in (".mp4", ".mov", ".webm"):
            if (renders / f"{base}{ext}").is_file():
                return renders / f"{base}{ext}"
        copie = Path(str(meta.get("exportedTo") or ""))
        if copie.name and copie.is_file():
            return copie
    return None


def debrief_a_faire(reel: Path) -> bool:
    """Suivi de première vidéo présent dans ce Reel et débrief pas enregistré."""
    if not (reel / "work" / "premiere-video.md").exists():
        return False
    return (config().get("setup") or {}).get("firstVideoDone") is not True


def vider(dossier: Path, garder=lambda p: False) -> int:
    n = 0
    if not dossier.is_dir():
        return n
    for p in dossier.iterdir():
        if p.name == ".gitkeep" or garder(p):
            continue
        shutil.rmtree(p) if p.is_dir() and not p.is_symlink() else p.unlink()
        n += 1
    return n


def alleger(reel: Path, app: Path | None = None) -> None:
    rushes = sum(1 for p in (reel / "derush").rglob("*") if p.is_file() and p.suffix.lower() in MEDIAS)
    for p in [p for p in (reel / "derush").rglob("*") if p.is_file() and p.suffix.lower() in MEDIAS]:
        p.unlink()
    travail = vider(reel / "work")
    # L'export de l'app est une vidéo finale : il reste, avec sa fiche (l'app s'en sert).
    garde_app = {app.name, f"{app.stem}.meta.json"} if app and app.parent == reel / "renders" else set()
    rendus = sum(vider(reel / d, garder=lambda p: "FINAL" in p.name or p.name in garde_app) for d in ("renders", "exports"))
    for d in ("snapshots", "probe"):
        if (reel / d).is_dir():
            shutil.rmtree(reel / d)
    print(f"• allégé : {rushes} média(s) du dérush, {travail} fichier(s) de travail, "
          f"{rendus} rendu(s) intermédiaire(s) supprimés ; montage et vidéos finales gardés")


def main() -> None:
    parser = argparse.ArgumentParser(description="Range un Reel publié.")
    parser.add_argument("--alleger", action="store_true",
                        help="Efface aussi les médias du dérush et les fichiers de travail.")
    args = parser.parse_args()
    reel = reel_courant()

    finals = finales(reel)
    app = export_app(reel)
    copies = [(p, p.name) for p in finals] + ([(app, f"{reel.name}{app.suffix}")] if app else [])
    if copies:
        dest = ARCHIVE_BASE / reel.name
        dest.mkdir(parents=True, exist_ok=True)
        for p, nom in copies:
            shutil.copy2(p, dest / nom)
            print(f"• vidéo finale copiée : {nom} -> {dest}")
    else:
        print("• aucune vidéo finale (ni « FINAL » dans exports/, ni export de l'app) : rien à copier")

    if debrief_a_faire(reel):
        note = MAISON / "work" / "premiere-video.md"
        note.parent.mkdir(exist_ok=True)
        note.write_text(DEBRIEF_NOTE.format(nom=reel.name), encoding="utf-8")
        print("• note « débrief à faire » posée dans work/premiere-video.md du dossier Monteur IA")

    meta_path = reel / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"id": reel.name, "name": reel.name}
    suivi = meta.setdefault("monteurIa", {"lieu": "reel"})
    suivi["etat"] = "publie"
    suivi["publieLe"] = datetime.date.today().isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("• Reel marqué publié")

    if args.alleger:
        alleger(reel, app)
    print(f"✅ Reel « {reel.name} » rangé. Son dossier reste dans reels/ (et dans l'app HyperFrames, si tu l'utilises).")


if __name__ == "__main__":
    main()
