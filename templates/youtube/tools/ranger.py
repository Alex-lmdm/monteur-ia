#!/usr/bin/env python3
"""RANGER UNE VIDÉO YOUTUBE : après publication, met la vidéo finale en lieu sûr et la marque publiée.

Usage (depuis le dossier de la vidéo) :
    python3 tools/ranger.py [--alleger]

- copie vers <Vidéos>/youtube-publiees/<nom>/ : les vidéos finales (« FINAL » dans exports/ ou
  renders/, et le dernier export réussi du bouton Export de l'app, copié en « <nom>.mp4 »), les
  sous-titres exports/sous-titres.srt et la fiche publication.md ;
- marque la vidéo publiée (meta.json : monteurIa.etat = "publie") : elle garde le style qu'elle
  avait au moment de la publication ;
- --alleger : efface en plus ce qui pèse et se refait (médias du dérush, fichiers de travail,
  rendus intermédiaires). Le montage et les vidéos finales restent.

Le dossier reste en place : il se rouvre d'un clic dans l'app HyperFrames.
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lieux import reel as projet_courant  # noqa: E402
from ranger_reel import VIDEOS_DIR, alleger, export_app, finales  # noqa: E402

ARCHIVE_BASE = Path.home() / VIDEOS_DIR / "youtube-publiees"


def main() -> None:
    parser = argparse.ArgumentParser(description="Range une vidéo YouTube publiée.")
    parser.add_argument("--alleger", action="store_true", help="Efface aussi les médias du dérush et les fichiers de travail.")
    args = parser.parse_args()
    video = projet_courant()

    app = export_app(video)
    copies = [(p, p.name) for p in finales(video)] + ([(app, f"{video.name}{app.suffix}")] if app else [])
    copies += [(p, p.name) for p in (video / "exports" / "sous-titres.srt", video / "publication.md") if p.is_file()]
    if copies:
        dest = ARCHIVE_BASE / video.name
        dest.mkdir(parents=True, exist_ok=True)
        for p, nom in copies:
            shutil.copy2(p, dest / nom)
            print(f"• copié : {nom} -> {dest}")
    else:
        print("• aucune vidéo finale (ni « FINAL » dans exports/, ni export de l'app) : rien à copier")

    meta_path = video / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"id": video.name, "name": video.name}
    suivi = meta.setdefault("monteurIa", {"lieu": "youtube"})
    suivi["etat"] = "publie"
    suivi["publieLe"] = datetime.date.today().isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("• vidéo marquée publiée")

    if args.alleger:
        alleger(video, app)
    print(f"✅ Vidéo « {video.name} » rangée. Son dossier reste dans youtube/ (et dans l'app HyperFrames).")


if __name__ == "__main__":
    main()
