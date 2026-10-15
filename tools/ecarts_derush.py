#!/usr/bin/env python3
"""ECARTS DU DERUSH : mesure le blanc reel a chaque coupe du derush et signale ceux qui trainent.

Usage (depuis le dossier du Reel) :
    python3 tools/ecarts_derush.py                         # lit derush/build_derush.py
    python3 tools/ecarts_derush.py derush/build_derush.py

Lit ISLANDS, PAD_START, PAD_END et OUT dans le script du derush (sans le lancer), retrouve chaque
coupe dans la video livree et mesure le blanc autour : silences a -40 dB, un souffle ou un clic de
moins de 0,25 s suivi (ou precede) d'un blanc d'au moins 0,10 s compte dans le blanc (c'est lui
qu'on entend trainer) ; un debut de mot suivi d'une micro-pause n'en est pas un.
Cible : environ 0,10 s, jamais plus de 0,20 s. Vidéo YouTube (meta.json : lieu « youtube ») dont le
derush garde la respiration (youtube.derush, marges de 0,2 s et plus) : 0,3 a 0,5 s ; signalees :
plus de 0,60 s (un blanc) ou moins de 0,15 s (on entend un begaiement). Un raccord (deux prises qui se touchent : une phrase partagée pour
changer de cadre sur un mot) n'est pas une coupe : il n'est pas mesuré.

Code de sortie 1 si une coupe traine. Cause la plus frequente : une prise qui commence par un
souffle isole puis un blanc (ou qui finit par un blanc puis un souffle). Recaler l'ilot : son debut
sur l'attaque de la parole, sa fin sur la derniere syllabe ; relancer build_derush.py ; re-mesurer.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEUIL_DB = -40


def est_youtube() -> bool:
    try:
        return (json.loads((ROOT / "meta.json").read_text(encoding="utf-8")).get("monteurIa") or {}).get("lieu") == "youtube"
    except (OSError, ValueError):
        return False


YOUTUBE = est_youtube()
MAX_BLANC = 0.60 if YOUTUBE else 0.20   # s : au-dela, la coupe s'entend
MIN_BLANC = 0.15 if YOUTUBE else 0.0    # s : en dessous (YouTube), la phrase suivante arrive trop tot
SOUFFLE_MAX = 0.25      # s : un son plus court pris entre deux blancs (souffle, clic) compte dans le blanc
VRAI_BLANC = 0.10       # s : ... a condition que le blanc d'en face dure au moins ca
FENETRE = (0.30, 0.80)  # s avant / apres la coupe theorique
RACCORD = 0.005         # s : deux prises qui se touchent apres les marges = un raccord, pas une coupe


def seuils(pad_start: float, pad_end: float) -> tuple[float, float]:
    """(min, max) du blanc a chaque coupe. La respiration YouTube ne vaut que si le derush la garde
    (marges de 0,2 s et plus) ; une video YouTube montee au rythme des Reels (marges serrees,
    youtube.derush = derush) est mesuree comme un Reel."""
    if YOUTUBE and pad_start + pad_end >= 0.2:
        return MIN_BLANC, MAX_BLANC
    return 0.0, 0.20


def lire_script(chemin: pathlib.Path) -> dict:
    valeurs = {}
    for noeud in ast.parse(chemin.read_text(encoding="utf-8")).body:
        if isinstance(noeud, ast.Assign) and len(noeud.targets) == 1 and isinstance(noeud.targets[0], ast.Name):
            nom = noeud.targets[0].id
            if nom in ("ISLANDS", "PAD_START", "PAD_END", "OUT"):
                valeurs[nom] = ast.literal_eval(noeud.value)
    manque = {"ISLANDS", "PAD_START", "PAD_END", "OUT"} - valeurs.keys()
    if manque:
        sys.exit(f"ERREUR : {chemin} ne definit pas {', '.join(sorted(manque))}.")
    return valeurs


def silences(video: pathlib.Path) -> list[tuple[float, float]]:
    log = subprocess.run(["ffmpeg", "-nostats", "-i", str(video), "-map", "0:a:0", "-af",
                          f"silencedetect=noise={SEUIL_DB}dB:d=0.03", "-f", "null", "-"],
                         capture_output=True, encoding="utf-8", errors="replace").stderr
    debuts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    fins = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(debuts, fins))


def blanc_a_la_coupe(t: float, sil: list[tuple[float, float]]) -> float:
    """Le blanc entendu autour de la coupe t. Part du silence de la coupe, puis l'etend par-dessus un son
    court (souffle, clic) seulement s'il est suivi, ou precede, d'un vrai blanc : un debut de mot suivi
    d'une micro-pause (« Ça | fait ») n'est pas un souffle."""
    proches = [(a, b) for a, b in sil if b > t - FENETRE[0] and a < t + FENETRE[1]]
    if not proches:
        return 0.0
    i = min(range(len(proches)), key=lambda k: 0 if proches[k][0] <= t <= proches[k][1]
            else min(abs(proches[k][0] - t), abs(proches[k][1] - t)))
    a, b = proches[i]
    if not (a <= t <= b or min(abs(a - t), abs(b - t)) < 0.35):
        return 0.0
    for c, d in proches[i + 1:]:            # apres la coupe : souffle puis blanc en tete de prise
        if c - b < SOUFFLE_MAX and d - c >= VRAI_BLANC:
            b = d
        else:
            break
    for c, d in reversed(proches[:i]):      # avant la coupe : blanc puis souffle en queue de prise
        if a - d < SOUFFLE_MAX and d - c >= VRAI_BLANC:
            a = c
        else:
            break
    return round(b - a, 3)


def main() -> None:
    script = (pathlib.Path.cwd() / (sys.argv[1] if len(sys.argv) > 1 else "derush/build_derush.py")).resolve()
    if not script.exists():
        sys.exit(f"ERREUR : script du derush introuvable : {script}")
    v = lire_script(script)
    video = (ROOT / v["OUT"]) if not pathlib.Path(v["OUT"]).is_absolute() else pathlib.Path(v["OUT"])
    if not video.exists():
        sys.exit(f"ERREUR : video du derush introuvable : {v['OUT']} (lance d'abord build_derush.py).")
    sil = silences(video)
    t, trainent, serrees = 0.0, [], []
    bas, haut = seuils(v["PAD_START"], v["PAD_END"])
    iles = v["ISLANDS"]
    # Raccord : la prise reprend le rush là où la précédente s'arrête (une phrase partagée pour changer
    # de cadre sur un mot). build_derush.py les monte d'un seul tenant : il n'y a pas de coupe à mesurer.
    raccords = {i for i in range(1, len(iles)) if abs((iles[i - 1][1] + v["PAD_END"])
                                                      - max(iles[i][0] - v["PAD_START"], 0.0)) <= RACCORD}
    print(f"{len(iles)} prises, {len(iles) - 1 - len(raccords)} coupes"
          + (f" + {len(raccords)} raccord(s)" if raccords else "") + f" ({video.name}) :")
    for i, (debut, fin, texte) in enumerate(iles):
        if i in raccords:
            print(f"  raccord {i:2d} a {t:6.2f} s : changement de cadre sans coupe, avant « {str(texte)[:40]} »")
        elif i:
            blanc = blanc_a_la_coupe(t, sil)
            mark = "  <- traine" if blanc > haut else "  <- trop serree" if blanc < bas else ""
            print(f"  coupe {i:2d} a {t:6.2f} s : blanc {blanc:4.2f} s  avant « {str(texte)[:48]} »{mark}")
            if "traine" in mark:
                trainent.append(i)
            elif mark:
                serrees.append(i)
        t += (fin + v["PAD_END"]) - max(debut - v["PAD_START"], 0.0)
    if serrees:
        print(f"{len(serrees)} coupe(s) trop serrees (< {bas:.2f} s) : allonge la fin de la prise d'avant "
              "(son ilot ou PAD_END), relance build_derush.py, re-mesure.")
    if trainent:
        print(f"{len(trainent)} coupe(s) trainent (> {haut:.2f} s) : recale l'ilot de la prise qui suit "
              "(debut sur l'attaque de la parole, sans le souffle isole), relance build_derush.py, re-mesure.")
    if trainent or serrees:
        sys.exit(1)
    print(f"Toutes les coupes sont dans la cible ({bas:.2f} a {haut:.2f} s)." if bas
          else f"Toutes les coupes sont serrees (<= {haut:.2f} s).")


if __name__ == "__main__":
    main()
