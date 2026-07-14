#!/usr/bin/env python3
"""SOURCE UNIQUE des frontieres de section du Reel.

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE REEL.                                           ║
║  - CUTS_PATH : pointe vers le <video>_cuts.json de TON derush (change ce path).║
║  - LAYOUT    : la table des sections de TON Reel (une ligne = une section).    ║
║ Le reste (asserts, face_windows) est generique : ne le touche pas.             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Les frontieres viennent de <video>_cuts.json (les VRAIS jump-cuts, mesures dans le fichier
livre par tools/cut_boundaries.py), JAMAIS d'une re-transcription Whisper (ses debuts de
segment tombent ~0.1-0.25 s trop tot -> la fenetre du visage s'ouvre avant la coupe et on voit
la fin de la prise precedente).

Tout le montage lit ce module : les sous-compositions (durees), le master (data-start) et les
sous-titres (snap + hauteur). Une seule source => impossible de les desynchroniser.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# >>> A CHANGER A CHAQUE NOUVEAU REEL : le _cuts.json produit par tools/cut_boundaries.py.
#     Ici : la demo du template (3 prises sur 8 s, cf derush/README-exemple.md).
CUTS_PATH = ROOT / "derush/exemple_cuts.json"

CUTS = json.loads(CUTS_PATH.read_text(encoding="utf-8"))
TAKES = CUTS["takes"]
DURATION = CUTS["duration"]

# >>> A REMPLIR A CHAQUE NOUVEAU REEL : la table des sections.
#   (id, format, [index des prises couvertes])
#     id     -> il DOIT exister un compositions/<id>.html du meme nom.
#     split  -> panneau motion 1080x920 en HAUT + visage en BAS.
#     full   -> motion 1080x1920 plein ecran, le visage est couvert.
#   Les index pointent dans TAKES (0-based) et doivent couvrir TOUTES les prises, dans l'ordre,
#   sans trou ni chevauchement (les asserts plus bas le verifient).
#
# DEMO : une seule section split "exemple-section" qui couvre les 3 prises (0 -> 8 s) et
# correspond a compositions/exemple-section.html + a index.html livre.
# Pour un vrai Reel tu auras plutot une alternance split/full, par exemple :
#     ("s0-hook",   "split", [0]),
#     ("s1a-intro", "split", [1]),  ("s1b-intro", "full", [2]),
#     ...
LAYOUT = [
    ("exemple-section", "split", [0, 1, 2]),
]

# y du sous-titre selon le format de la section.
# NB : brand.config.json -> visual.captionsPosition decrit l'INTENTION ("split-jointure"),
# pas une valeur en px. On garde donc ces constantes ; ajuste-les si ta marque cadre autrement.
Y_SPLIT = 920    # pile a la jointure split (au ras du haut du visage)
Y_FULL = 1500    # sous la fenetre plein ecran


def sections():
    out = []
    for sid, fmt, idx in LAYOUT:
        start = TAKES[idx[0]]["start"]
        end = TAKES[idx[-1]]["end"]
        out.append({"id": sid, "fmt": fmt, "takes": idx,
                    "start": round(start, 3), "end": round(end, 3),
                    "dur": round(end - start, 3),
                    "y": Y_SPLIT if fmt == "split" else Y_FULL})
    assert out[0]["start"] == 0.0, "la 1re section doit demarrer a 0"
    assert abs(out[-1]["end"] - DURATION) < 0.01, "la derniere section doit finir a la fin du cut"
    for a, b in zip(out, out[1:]):
        assert abs(a["end"] - b["start"]) < 1e-6, f"trou/chevauchement entre {a['id']} et {b['id']}"
    return out


def face_windows():
    """Fenetres ou le visage est visible (split) — les splits contigus sont fusionnes."""
    wins = []
    for s in sections():
        if s["fmt"] != "split":
            continue
        if wins and abs(wins[-1][1] - s["start"]) < 1e-6:
            wins[-1] = (wins[-1][0], s["end"])
        else:
            wins.append((s["start"], s["end"]))
    return [(round(a, 3), round(b - a, 3)) for a, b in wins]


if __name__ == "__main__":
    for s in sections():
        print(f'{s["id"]:<16} {s["fmt"]:<5} {s["start"]:6.3f} -> {s["end"]:6.3f}  '
              f'({s["dur"]:5.3f}s)  y={s["y"]}')
    print("\nfenetres visage (split) :")
    for st, d in face_windows():
        print(f"  {st:6.3f}  +{d:.3f}")
