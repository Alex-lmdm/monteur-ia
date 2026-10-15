#!/usr/bin/env python3
"""NIVEAU FINAL : le cœur commun des tools/finaliser.py, celui d'un Reel et celui d'une vidéo YouTube.

Pas une commande : chaque projet lance son `python3 tools/finaliser.py`, qui donne ici sa cible
(-16 LUFS pour un Reel, -14 LUFS pour une vidéo YouTube), son débit AAC, sa vidéo de sortie et son
contrôle (le check_export.py du projet).

1. Niveau : un même gain pour tout le mixage (voix, sons, musique), qui garde l'équilibre du
   montage, puis un limiteur de crêtes vraies (suréchantillonné à 192 kHz, avec anticipation :
   sons.plafond_ffmpeg). Le gain se règle par essais, puis se vérifie sur la vidéo encodée (à 0,15 LU). L'image est copiée telle
   quelle, seul le son est réencodé (AAC 48 kHz, sans PNS : le bruit qu'il synthétise au décodage
   fait des crêtes que le limiteur n'a pas vues). La crête vraie se vérifie sur le fichier encodé :
   si l'AAC l'a remontée au-dessus de -1 dBTP, le plafond est abaissé d'autant et la vidéo refaite.
   Une voix absente (export sous -35 LUFS) n'est jamais remontée à l'aveugle.
   Pourquoi après l'export : le rendu de l'app HyperFrames ne garde pas un gain au-delà de la marge
   de crête du mixage (il baisse tout dès qu'une crête vraie dépasse -1 dBTP après l'encodage) ; le
   montage pose seulement le gain que cette marge permet (tools/sons.py).
2. Contrôle : le check_export.py du projet, sur la vidéo finalisée.
3. Livraison dans Téléchargements : la copie que l'app vient d'y poser est remplacée par la vidéo
   finalisée (même nom, une seule vidéo à livrer), si c'est encore la sienne ; sinon (npm run render,
   copie déplacée ou modifiée) copie en « <nom du projet>.mp4 », puis « V2 », « V3 »… Une vidéo
   identique déjà livrée n'est pas recopiée.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Callable, Iterable

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lieux import MAISON  # noqa: E402,F401  (sortie UTF-8 sous Windows : « ✅ » dans un terminal cp1252)
from sons import CRETE_MAX_DBTP, LIMITE_DB, niveau_sonore, plafond_ffmpeg  # noqa: E402

PLAFOND_DB = LIMITE_DB  # crêtes vraies visées ; le contrôle exige au plus -1 dBTP après l'encodage AAC
TOLERANCE_LUFS = 0.1   # écart accepté avant un nouvel essai du gain, avant l'encodage
ECART_FINAL = 0.15     # écart accepté sur la vidéo encodée (le contrôle des projets tolère 1 LU)
ESSAIS = 4             # réglages du gain, à plafond donné
ESSAIS_CRETE = 3       # encodages, si l'AAC remonte la crête vraie ou décale le niveau
SON_MIN_LUFS = -35.0   # en dessous, la voix manque : on ne la remonte pas à l'aveugle


def mesurer(src: pathlib.Path, filtre: str = "") -> tuple[float, float]:
    """(loudness intégrée en LUFS, crête vraie en dBTP) du son, après `filtre` s'il est donné."""
    lufs, crete = niveau_sonore(src, filtre)
    if lufs is None:
        sys.exit(f"ERREUR : son illisible dans {src.name} : pas de piste son ? Exporte à nouveau la vidéo.")
    return lufs, crete


def regler(src: pathlib.Path, niveau: float, cible: float, plafond: float) -> float:
    """Le gain qui amène l'export (mesuré à `niveau`) à `cible`, une fois limité à `plafond`."""
    gain = cible - niveau
    for _ in range(ESSAIS):
        obtenu, _crete = mesurer(src, plafond_ffmpeg(plafond, gain))
        if abs(obtenu - cible) <= TOLERANCE_LUFS:
            break
        gain += cible - obtenu   # le limiteur rogne un peu de loudness : on compense
    return gain


def ecrire(src: pathlib.Path, sortie: pathlib.Path, gain: float, plafond: float, debit: str) -> None:
    """La vidéo finalisée : image copiée, son réglé puis encodé en AAC sans PNS."""
    sortie.parent.mkdir(exist_ok=True)
    tmp = sortie.with_name(".finalisation-en-cours.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
                        "-af", plafond_ffmpeg(plafond, gain), "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", debit,
                        "-aac_pns", "0", "-movflags", "+faststart", str(tmp)],
                       capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        tmp.unlink(missing_ok=True)
        sys.exit(f"ERREUR : ffmpeg n'a pas pu finaliser le son :\n{r.stderr[-1200:]}")
    os.replace(tmp, sortie)


def finaliser_son(src: pathlib.Path, sortie: pathlib.Path, cible: float, debit: str) -> dict:
    """Écrit `sortie` au niveau final, vérifié sur la vidéo encodée. Si l'AAC a remonté la crête vraie
    au-dessus de CRETE_MAX_DBTP, le plafond est abaissé d'autant ; s'il a décalé le niveau de plus de
    ECART_FINAL, le gain vise d'autant plus loin. Un essai de plus suffit d'ordinaire."""
    niveau, crete = mesurer(src)
    if niveau < SON_MIN_LUFS:
        sys.exit(f"ERREUR : son de l'export trop faible ({niveau:.1f} LUFS) : voix absente ou coupée dans le "
                 "montage ? Vérifie-le, puis exporte à nouveau.")
    plafond, vise = PLAFOND_DB, cible
    for essai in range(ESSAIS_CRETE):
        gain = regler(src, niveau, vise, plafond)
        ecrire(src, sortie, gain, plafond, debit)
        apres, crete_apres = mesurer(sortie)
        crete_ok, niveau_ok = crete_apres <= CRETE_MAX_DBTP, abs(apres - cible) <= ECART_FINAL
        if (crete_ok and niveau_ok) or essai == ESSAIS_CRETE - 1:
            break
        if not crete_ok:
            plafond = round(plafond - (crete_apres - CRETE_MAX_DBTP) - 0.1, 2)
        if not niveau_ok:
            vise += cible - apres
    return {"niveau": niveau, "crete": crete, "gain": gain, "plafond": plafond, "apres": apres, "crete_apres": crete_apres}


def empreinte(p: pathlib.Path) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def copie_de_l_app(projet: pathlib.Path, src: pathlib.Path) -> pathlib.Path | None:
    """La copie que l'app a posée dans Téléchargements pour cet export : renders/<id>.meta.json décrit
    le rendu renders/<id>.<ext> et sa copie (exportedTo). `src` peut être l'un ou l'autre."""
    renders = projet / "renders"
    for fiche in renders.glob("*.meta.json") if renders.is_dir() else ():
        try:
            meta = json.loads(fiche.read_text(encoding="utf-8"))
            copie = pathlib.Path(str(meta.get("exportedTo") or "")).expanduser()
        except (OSError, ValueError, AttributeError):
            continue
        base = fiche.name[: -len(".meta.json")]
        rendus = {(renders / f"{base}{ext}").resolve() for ext in (".mp4", ".mov", ".webm")}
        if copie.name and copie.is_file() and (src in rendus or copie.resolve() == src):
            return copie.resolve()
    return None


def _remplacer(sortie: pathlib.Path, cible: pathlib.Path) -> bool:
    """Remplace `cible` par la vidéo finalisée, d'un coup ; False si c'est impossible (Windows : la
    vidéo est ouverte dans un lecteur)."""
    tmp = cible.with_name(f".{cible.name}.finalisation")
    try:
        shutil.copyfile(sortie, tmp)
        os.replace(tmp, cible)
        return True
    except OSError:
        tmp.unlink(missing_ok=True)
        return False


def livrer(projet: pathlib.Path, sortie: pathlib.Path, src: pathlib.Path,
           empreintes_avant: set[str]) -> tuple[pathlib.Path, str]:
    """Pose la vidéo finalisée dans Téléchargements -> (fichier, ce qui a été fait)."""
    neuve = empreinte(sortie)
    copie = copie_de_l_app(projet, src)
    # La copie de l'app n'est remplacée que si elle est encore celle de l'app (ou notre finalisation
    # précédente) : un fichier que le client a changé depuis reste intact.
    if copie and empreinte(copie) in empreintes_avant | {neuve} and _remplacer(sortie, copie):
        return copie, "remplace la copie posée par l'app (même nom)"
    dossier = pathlib.Path.home() / "Downloads"
    dossier.mkdir(exist_ok=True)
    cible, n = dossier / f"{projet.name}.mp4", 2
    while cible.exists():
        if empreinte(cible) == neuve:
            return cible, "déjà livrée, identique"
        cible, n = dossier / f"{projet.name} V{n}.mp4", n + 1
    shutil.copy2(sortie, cible)
    return cible, "copiée"


def main(projet: pathlib.Path, sortie: pathlib.Path, cible: float, debit: str,
         controle: Callable[[pathlib.Path], int], exports: Iterable[pathlib.Path | None], pret: str) -> None:
    """La commande `python3 tools/finaliser.py [fichier] [--sans-copie]` d'un projet. `exports` : les
    vidéos exportées candidates (la plus récente est prise sans fichier précisé) ; `controle` : le
    contrôle du projet sur la vidéo finalisée, qui rend le nombre de points KO ; `pret` : le mot de la
    fin (« Prête à poster », « Prête à téléverser »)."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        src = pathlib.Path(args[0]).expanduser()
    else:
        candidats = [p for p in exports if p and p.is_file()]
        src = max(candidats, key=lambda p: p.stat().st_mtime) if candidats else None
    if not src or not src.is_file():
        sys.exit("Rien à finaliser : exporte d'abord la vidéo (bouton Export de l'app, ou npm run render).")
    src = src.resolve()
    if src == sortie.resolve():
        sys.exit("Ce fichier est déjà la version finalisée : exporte à nouveau pour repartir du montage.")
    # Empreintes de l'export de l'app et de la finalisation précédente, avant de la réécrire.
    empreintes_avant = {empreinte(p) for p in (src, sortie) if p.is_file()}
    r = finaliser_son(src, sortie, cible, debit)
    abaisse = f", plafond abaissé à {r['plafond']} dB après l'encodage" if r["plafond"] != PLAFOND_DB else ""
    print(f"• son : {r['niveau']:.1f} LUFS (crête {r['crete']:.1f} dBTP) -> {r['apres']:.1f} LUFS "
          f"(crête {r['crete_apres']:.1f} dBTP), gain {r['gain']:+.1f} dB{abaisse} ; {src.name} -> "
          f"{sortie.relative_to(projet)}\n")
    ko = controle(sortie)
    if ko:
        print(f"\n❌ {ko} point(s) à revoir : rien n'est copié dans Téléchargements.")
        sys.exit(1)
    if "--sans-copie" in sys.argv:
        print(f"\n✅ {pret} : {sortie}")
        return
    cible_livree, fait = livrer(projet, sortie, src, empreintes_avant)
    print(f"\n✅ {pret} : {cible_livree} ({fait})")


if __name__ == "__main__":
    sys.exit("Module partagé : lance python3 tools/finaliser.py depuis le dossier du Reel ou de la vidéo YouTube.")
