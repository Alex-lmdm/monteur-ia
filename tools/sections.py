#!/usr/bin/env python3
"""SOURCE UNIQUE des frontieres de section — Reel "7 codes secrets Claude".

Les frontieres viennent de <cut>_cuts.json (les VRAIS jump-cuts, mesures dans le fichier livre),
JAMAIS d'une re-transcription Whisper (ses debuts de segment tombent ~0.1-0.25 s trop tot ->
la fenetre du visage s'ouvre avant la coupe et on voit la fin de la prise precedente).

Tout le montage lit ce module : les sous-compositions (durees), le master (data-start) et les
sous-titres (snap + hauteur). Une seule source => impossible de les desynchroniser.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CUTS = json.loads((ROOT / "derush/2026-07-14_codes-claude/codes_claude_cuts.json").read_text())
TAKES = CUTS["takes"]
DURATION = CUTS["duration"]

# (id, format, [index des prises couvertes])
#   split -> panneau motion 1080x920 en haut + visage en bas
#   full  -> motion 1080x1920, le visage est couvert
LAYOUT = [
    ("s0-hook",       "split", [0]),
    ("s1a-grill",     "split", [1]),   ("s1b-grill",     "full", [2]),
    ("s2a-devil",     "split", [3]),   ("s2b-devil",     "full", [4]),
    ("s3a-brief",     "split", [5]),   ("s3b-brief",     "full", [6]),
    ("s4a-roast",     "split", [7]),   ("s4b-roast",     "full", [8]),
    ("s5a-steal",     "split", [9]),   ("s5b-steal",     "full", [10]),
    ("s6a-ghost",     "split", [11]),  ("s6b-ghost",     "full", [12]),
    ("s7a-premortem", "split", [13]),  ("s7b-premortem", "full", [14, 15]),
    ("s8-cta",        "split", [16, 17, 18]),
]

# y du sous-titre selon le format de la section
Y_SPLIT = 920    # pile a la jointure
Y_FULL = 1500    # sous la fenetre Claude


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
        print(f'{s["id"]:<14} {s["fmt"]:<5} {s["start"]:6.3f} -> {s["end"]:6.3f}  ({s["dur"]:5.3f}s)  y={s["y"]}')
    print("\nfenetres visage (split) :")
    for st, d in face_windows():
        print(f"  {st:6.3f}  +{d:.3f}")
