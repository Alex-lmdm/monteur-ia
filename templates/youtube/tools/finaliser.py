#!/usr/bin/env python3
"""FINALISER une vidéo YouTube après l'export : niveau sonore à -14 LUFS, contrôle, vidéo à téléverser.

Usage (depuis le dossier de la vidéo), après le bouton Export de l'app ou `npm run render` :
    python3 tools/finaliser.py                 # le dernier export (app ou exports/FINAL.mp4)
    python3 tools/finaliser.py <fichier.mp4>   # un export précis
    python3 tools/finaliser.py --sans-copie    # sans rien écrire dans Téléchargements

1. Niveau : -14 LUFS intégrés (le niveau que YouTube garde), crêtes vraies sous -1 dBTP ; un même
   gain pour tout le mixage, qui garde l'équilibre voix, sons et musique, puis un limiteur de
   crêtes vraies : le même cœur que les Reels (tools/niveau_final.py). Image copiée telle quelle,
   son en AAC 48 kHz 384 kb/s (la recommandation de YouTube). Quelques secondes, même sur 20 min.
2. Contrôle : tools/check_export.py sur la vidéo finalisée (exports/FINAL-YOUTUBE.mp4).
3. Livraison dans Téléchargements : la copie que l'app vient d'y poser est remplacée par la vidéo
   finalisée (même nom, une seule vidéo à téléverser) ; sinon copie en « <nom de la vidéo>.mp4 »,
   puis « V2 », « V3 »…
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import niveau_final  # noqa: E402
from lieux import reel as projet_courant  # noqa: E402
from ranger_reel import export_app  # noqa: E402
from sons import CIBLE_YOUTUBE_LUFS  # noqa: E402

ROOT = projet_courant()
SORTIE = ROOT / "exports/FINAL-YOUTUBE.mp4"
DEBIT = "384k"


def controle(sortie: pathlib.Path) -> int:
    import check_export   # lit le montage de la vidéo (sections) : seulement maintenant
    return check_export.verifier(sortie, finalise=True)


if __name__ == "__main__":
    niveau_final.main(ROOT, SORTIE, CIBLE_YOUTUBE_LUFS, DEBIT, controle,
                      [export_app(ROOT), ROOT / "exports/FINAL.mp4", ROOT / "exports/FINAL_SFX_MUSIC.mp4"],
                      "Prête à téléverser")
