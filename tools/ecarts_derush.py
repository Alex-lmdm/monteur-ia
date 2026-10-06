#!/usr/bin/env python3
"""ECARTS DU DERUSH : mesure le blanc reel a chaque coupe du derush et signale ceux qui trainent.

Usage (depuis le dossier du Reel) :
    python3 tools/ecarts_derush.py                         # lit derush/build_derush.py
    python3 tools/ecarts_derush.py derush/build_derush.py

Lit ISLANDS, PAD_START, PAD_END et OUT dans le script du derush (sans le lancer), retrouve chaque
coupe dans la video livree et mesure le blanc autour : silences a -40 dB, un souffle ou un clic de
moins de 0,25 s suivi (ou precede) d'un blanc d'au moins 0,10 s compte dans le blanc (c'est lui
qu'on entend trainer) ; un debut de mot suivi d'une micro-pause n'en est pas un.
Cible : environ 0,10 s, jamais plus de 0,20 s.

Code de sortie 1 si une coupe traine. Cause la plus frequente : une prise qui commence par un
souffle isole puis un blanc (ou qui finit par un blanc puis un souffle). Recaler l'ilot : son debut
sur l'attaque de la parole, sa fin sur la derniere syllabe ; relancer build_derush.py ; re-mesurer.
"""
from __future__ import annotations

import ast
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEUIL_DB = -40
MAX_BLANC = 0.20        # s : au-dela, la coupe s'entend
SOUFFLE_MAX = 0.25      # s : un son plus court pris entre deux blancs (souffle, clic) compte dans le blanc
VRAI_BLANC = 0.10       # s : ... a condition que le blanc d'en face dure au moins ca
FENETRE = (0.30, 0.80)  # s avant / apres la coupe theorique


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
    t, trainent = 0.0, []
    print(f"{len(v['ISLANDS'])} prises, {len(v['ISLANDS']) - 1} coupes ({video.name}) :")
    for i, (debut, fin, texte) in enumerate(v["ISLANDS"]):
        if i:
            blanc = blanc_a_la_coupe(t, sil)
            mark = "  <- traine" if blanc > MAX_BLANC else ""
            print(f"  coupe {i:2d} a {t:6.2f} s : blanc {blanc:4.2f} s  avant « {str(texte)[:48]} »{mark}")
            if mark:
                trainent.append(i)
        t += (fin + v["PAD_END"]) - max(debut - v["PAD_START"], 0.0)
    if trainent:
        print(f"{len(trainent)} coupe(s) trainent (> {MAX_BLANC:.2f} s) : recale l'ilot de la prise qui suit "
              "(debut sur l'attaque de la parole, sans le souffle isole), relance build_derush.py, re-mesure.")
        sys.exit(1)
    print(f"Toutes les coupes sont serrees (<= {MAX_BLANC:.2f} s).")


if __name__ == "__main__":
    main()
