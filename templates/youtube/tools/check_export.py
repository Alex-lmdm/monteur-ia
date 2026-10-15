#!/usr/bin/env python3
"""GARDE-FOU de l'export d'une vidéo YouTube : à lancer sur la vidéo finale AVANT de livrer.

Usage (depuis le dossier de la vidéo) :
    python3 tools/check_export.py                    # export natif : exports/FINAL.mp4
    python3 tools/check_export.py ~/Downloads/x.mp4  # une vidéo sortie par le bouton Export de l'app

  F) format : 1920x1080 (ou 3840x2160), durée du montage, une piste son aussi longue que l'image
     (un écart veut dire une dérive son/image le long de la vidéo) ;
  V) visage présent, net et calé sur la voix : sur un échantillon de prises, la zone du visage
     ressemble à la même image du visage pré-cadré (tools/build_faces.py), à une image près ;
     un visage gelé (vidéo sans id, média trop court) ou absent échoue ici ;
  S) son : présent ; une fois finalisé (tools/finaliser.py), -14 LUFS (le niveau que YouTube garde)
     et crête vraie sous -1 dBTP.

`npm run check` valide la STRUCTURE, pas la vidéo réellement rendue : les pièges du rendu par
couches (skill motion-design, references/montage-talking-head.md §0bis) ne se voient qu'ici.
"""
from __future__ import annotations

import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import warnings

warnings.filterwarnings("ignore")
from PIL import Image  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from lieux import MAISON  # noqa: E402,F401  (sortie UTF-8 sous Windows)

ROOT = pathlib.Path(__file__).resolve().parent.parent
FINAL = ROOT / "exports/FINAL.mp4"
W, H, FPS = 1920, 1080, 30
DECALAGE = 480
CIBLE_LUFS, TOLERANCE_LUFS = -14.0, 1.5
ECHANTILLON = 12          # prises contrôlées, réparties sur toute la vidéo


def grab(src: pathlib.Path, t: float, largeur: int = W) -> Image.Image:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
                          "-vf", f"scale={largeur}:-2:in_color_matrix=bt709", "-c:v", "png", "-f", "image2pipe", "-"],
                         capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB")


def ssim(a: Image.Image, b: Image.Image) -> float:
    with tempfile.TemporaryDirectory() as d:
        pa, pb = pathlib.Path(d) / "a.png", pathlib.Path(d) / "b.png"
        a.save(pa)
        b.save(pb)
        err = subprocess.run(["ffmpeg", "-v", "info", "-i", str(pa), "-i", str(pb), "-lavfi", "ssim", "-f", "null", "-"],
                             capture_output=True, encoding="utf-8", errors="replace").stderr
    m = re.search(r"All:([\d.]+)", err)
    return float(m.group(1)) if m else 0.0


def zones(p: dict) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    """(zone dans l'export, même zone dans le visage pré-cadré), au-dessus des textes d'appui."""
    if p["fmt"] == "cote":
        export = (0, 60, 960, 700) if p["panneau"] == "droite" else (960, 60, 1920, 700)
        return export, (DECALAGE, 60, DECALAGE + 960, 700)
    return (480, 60, 1440, 700), (480, 60, 1440, 700)


def verifier(mp4: pathlib.Path, finalise: bool = False) -> int:
    ko = 0
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                      "stream=codec_type,width,height,duration:format=duration", "-of", "json", str(mp4)],
                                     capture_output=True, encoding="utf-8", errors="replace").stdout or "{}")
    flux = info.get("streams", [])
    video = next((s for s in flux if s.get("codec_type") == "video"), {})
    audio = next((s for s in flux if s.get("codec_type") == "audio"), None)
    duree = float((info.get("format") or {}).get("duration") or 0)
    taille = (video.get("width"), video.get("height"))
    ecart = abs(float(video.get("duration") or duree) - float((audio or {}).get("duration") or duree))
    ok = taille in ((1920, 1080), (3840, 2160)) and abs(duree - sections.DURATION) < 0.15 and audio and ecart < 0.1
    ko += not ok
    print(f"F) format : {taille[0]}x{taille[1]}, {duree:.2f} s (montage {sections.DURATION} s), son "
          f"{'oui' if audio else 'NON'}, écart son/image {ecart:.2f} s  {'OK' if ok else '!! KO'}")

    print("V) visage présent, net, sur la même image que la voix")
    prises = [p for p in sections.cadre_par_prise() if p["cadre"] and p["end"] - p["start"] >= 1.2]
    pas = max(1, len(prises) // ECHANTILLON)
    decalages = []
    for p in prises[::pas][:ECHANTILLON]:
        visage = ROOT / f"assets/video/visage-{p['cadre']}.mp4"
        if not visage.exists():
            print(f"   {sections._mmss(p['start'])} visage « {p['cadre']} » lu dans base.mp4 zoomée (moins net) : "
                  "python3 tools/build_faces.py puis python3 tools/build_master.py --write")
            continue
        t = round(p["start"] + max(0.7, (p["end"] - p["start"]) * 0.5), 3)
        t = min(t, p["end"] - 0.1)
        za, zb = zones(p)
        image = grab(mp4, t).crop(za)
        scores = {k: ssim(image, grab(visage, round(t + k / FPS, 4)).crop(zb)) for k in (-1, 0, 1)}
        score = max(scores.values())
        decalages.append(max(scores, key=scores.get) if score - scores[0] > 0.01 else 0)
        ok = score >= 0.80
        ko += not ok
        print(f"   {sections._mmss(p['start'])} prise {p['take']:<4} {p['cadre']:<10} {p['fmt']:<5} "
              f"ressemblance {score:.3f}  {'OK' if ok else '!! KO (visage absent, gelé, masqué ou mal cadré)'}")
    if decalages and sum(1 for k in decalages if k) * 3 >= len(decalages) * 2:
        ko += 1
        print("   !! visage décalé d'une image sur la voix : relance tools/build_faces.py puis "
              "tools/build_master.py --write, puis exporte à nouveau")

    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    lufs = float(m[-1]) if m else -99.0
    pics = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", err)
    crete = float(pics[-1]) if pics and pics[-1] != "-inf" else -99.0
    ok = lufs > -35 and (not finalise or (abs(lufs - CIBLE_LUFS) <= TOLERANCE_LUFS and crete <= -1.0))
    ko += not ok
    print(f"S) son : {lufs:.1f} LUFS (visé {CIBLE_LUFS:.0f}), crête {crete:.1f} dBTP  "
          f"{'OK' if ok else '!! KO (voix absente, ou niveau final hors cible)'}")
    if not finalise and lufs > -35 and abs(lufs - CIBLE_LUFS) > TOLERANCE_LUFS:
        print("   export brut : le niveau final se pose avec python3 tools/finaliser.py (fichier à téléverser)")
    return ko


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cible = pathlib.Path(args[0]).expanduser() if args else FINAL
    if not cible.exists():
        print(f"Rien à vérifier : {cible} n'existe pas.")
        print("Exporte d'abord la vidéo : bouton Export de l'app, ou npm run render (exports/FINAL.mp4).")
        sys.exit(0)
    ko = verifier(cible)
    print("\n" + ("✅ EXPORT CONFORME" if ko == 0 else f"❌ {ko} point(s) à revoir avant de livrer"))
    sys.exit(1 if ko else 0)


if __name__ == "__main__":
    main()
