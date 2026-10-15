#!/usr/bin/env python3
"""FINALISER un Reel après l'export : niveau sonore à -16 LUFS, contrôle, vidéo à poster.

Usage (depuis le dossier du Reel), après le bouton Export de l'app ou `npm run render` :
    python3 tools/finaliser.py                 # le dernier export (app, exports/FINAL.mp4…)
    python3 tools/finaliser.py <fichier.mp4>   # un export précis
    python3 tools/finaliser.py --sans-copie    # sans rien écrire dans Téléchargements

1. Niveau : -16 LUFS intégrés, le niveau des Reels du fil, crêtes vraies sous -1 dBTP ; un même gain
   pour tout le mixage, puis un limiteur de crêtes vraies (le cœur commun : tools/niveau_final.py).
   Image copiée telle quelle, son en AAC 48 kHz 320 kb/s. Quelques secondes pour un Reel.
2. Contrôle : tools/check_export.py sur la vidéo finalisée (exports/FINAL-REEL.mp4).
3. Livraison dans Téléchargements : la copie que l'app vient d'y poser est remplacée par la vidéo
   finalisée (même nom, une seule vidéo à poster) ; sinon copie en « <nom du Reel>.mp4 », puis
   « V2 », « V3 »…
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import niveau_final  # noqa: E402
from lieux import reel as reel_courant  # noqa: E402
from ranger_reel import export_app  # noqa: E402
from sons import CIBLE_LUFS  # noqa: E402

ROOT = reel_courant()
SORTIE = ROOT / "exports/FINAL-REEL.mp4"
DEBIT = "320k"


def controle(sortie: pathlib.Path) -> int:
    import check_export   # lit le montage du Reel (sections) : seulement maintenant
    return check_export.verifier_final(sortie, finalise=True)


if __name__ == "__main__":
    niveau_final.main(ROOT, SORTIE, CIBLE_LUFS, DEBIT, controle,
                      [export_app(ROOT), ROOT / "exports/FINAL.mp4", ROOT / "exports/FINAL_SFX_MUSIC.mp4"],
                      "Prête à poster")
