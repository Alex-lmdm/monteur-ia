#!/usr/bin/env python3
"""PUBLICATION d'une vidéo YouTube : chapitres horodatés et fiche publication.md.

Usage (depuis le dossier de la vidéo) :
    python3 tools/publication.py      # affiche les chapitres et les écrit dans publication.md

Les chapitres viennent des sections qui portent "chapitre" dans tools/sections.py : leurs instants
sont ceux du montage, donc justes à la seconde. Règles de YouTube : le premier à 00:00, au moins 3,
chacun d'au moins 10 s (sinon YouTube ne les affiche pas).

publication.md (créé s'il manque) : titre, description, chapitres, sous-titres, écran de fin.
Seul le bloc CHAPITRES est réécrit à chaque appel ; le reste est à l'IA et au client.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from lieux import MAISON  # noqa: E402,F401  (sortie UTF-8 sous Windows)

ROOT = pathlib.Path(__file__).resolve().parent.parent
FICHE = ROOT / "publication.md"
BLOC = re.compile(r"<!-- CHAPITRES:DEBUT -->.*?<!-- CHAPITRES:FIN -->", re.S)
MODELE = """# Publication YouTube

## Titre (3 propositions, moins de 60 caractères, la promesse de la miniature)

1.
2.
3.

## Description

(Deux premières lignes : la promesse et le lien principal, c'est ce qui s'affiche sans clic.)

{chapitres}

## Sous-titres

`exports/sous-titres.srt` : YouTube Studio > Sous-titres > Ajouter une langue > Importer un fichier.

## Écran de fin

Les 5 à 20 dernières secondes : une vidéo à regarder ensuite et le bouton S'abonner, posés dans
YouTube Studio > Écran de fin. Rien d'important à l'image sous ces éléments.
"""


def horodatage(t: float, long: bool) -> str:
    s = int(t)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}" if long else f"{s // 60:02d}:{s % 60:02d}"


def bloc() -> str:
    ch = sections.chapitres()
    if not ch:
        return ("<!-- CHAPITRES:DEBUT -->\n(aucun chapitre : ajoute \"chapitre\" aux sections qui ouvrent "
                "une partie, dans tools/sections.py)\n<!-- CHAPITRES:FIN -->")
    long = sections.DURATION >= 3600
    lignes = "\n".join(f"{horodatage(t, long)} {titre}" for t, titre in ch)
    return f"<!-- CHAPITRES:DEBUT -->\nChapitres :\n{lignes}\n<!-- CHAPITRES:FIN -->"


def main() -> None:
    texte = bloc()
    print(texte.replace("<!-- CHAPITRES:DEBUT -->\n", "").replace("\n<!-- CHAPITRES:FIN -->", ""))
    for alerte in sections.alertes():
        if "chapitre" in alerte:
            print(f"⚠️ {alerte}")
    if FICHE.exists():
        actuel = FICHE.read_text(encoding="utf-8")
        nouveau = BLOC.sub(lambda _m: texte, actuel) if BLOC.search(actuel) else actuel.rstrip() + "\n\n" + texte + "\n"
    else:
        nouveau = MODELE.format(chapitres=texte)
    FICHE.write_text(nouveau, encoding="utf-8")
    print(f"• chapitres écrits dans {FICHE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
