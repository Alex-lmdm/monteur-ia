#!/usr/bin/env python3
"""VISAGES PRÉ-CADRÉS d'une vidéo YouTube : les cadres « large », « serre » et « tres-serre »,
tirés du dérush en pleine résolution et posés à l'échelle 1 par le master (export net).

Usage (depuis le dossier de la vidéo) :
    python3 tools/build_faces.py --apercu   # work/cadrage-apercu.jpg : les 3 cadres dessinés sur le rush
    python3 tools/build_faces.py            # assets/video/visage-<cadre>.mp4, seulement les cadres utilisés
    python3 tools/build_master.py --write   # le master pose ces vidéos, sans les agrandir

Le cadrage vient de brand.config.json -> youtube.cadrage :
    {"visageX": 0.5, "yeuxY": 0.40}   position du visage dans le rush (0 = gauche/haut, 1 = droite/bas)
et des zooms youtube.zoomSerre (1.3) et youtube.zoomTresSerre (1.55). Les cadres serrés gardent
les yeux vers 40 % de la hauteur : la tête ne se coupe pas, le texte d'appui passe sur le torse.

Pourquoi des fichiers séparés plutôt qu'un zoom CSS : un zoom dans le navigateur agrandit une copie
1080p et floute le visage ; un cadre découpé dans un rush 4K garde tout son détail. Un rush 1080p
supporte un cadre serré jusqu'à ~1,3 (l'outil prévient au-delà) : pour des zooms nets, tourner en 4K.

Rush vertical (téléphone tenu droit) : le cadre large est découpé dans une bande 16:9 autour des
yeux, forcément agrandie et moins nette. Le dire au client : pour YouTube, on filme à l'horizontale.

Relancer après tout nouveau dérush ou tout changement de youtube.cadrage.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "assets/video/base.mp4"
W, H, FPS = 1920, 1080, 30
HDR = ("arib-std-b67", "smpte2084")
# Fichier de travail quasi sans perte : il n'est réencodé qu'une fois, à l'export.
ENCODE = ["-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", "-g", "30",
          "-keyint_min", "30", "-sc_threshold", "0", "-an", "-movflags", "+faststart"]
YT = config().get("youtube") or {}
CADRAGE = {"visageX": 0.5, "yeuxY": 0.40, **(YT.get("cadrage") or {})}
ZOOMS = {"large": 1.0, "serre": float(YT.get("zoomSerre") or 1.3), "tres-serre": float(YT.get("zoomTresSerre") or 1.55)}
YEUX_DANS_LE_CADRE = {"large": None, "serre": 0.40, "tres-serre": 0.42}
COULEURS = {"large": "white", "serre": "yellow", "tres-serre": "red"}


def probe(path: pathlib.Path) -> tuple[int, int, str, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,color_transfer:format=duration", "-of", "json", str(path)],
                         capture_output=True, encoding="utf-8", errors="replace").stdout
    data = json.loads(out or "{}")
    s = (data.get("streams") or [{}])[0]
    return (int(s.get("width") or 0), int(s.get("height") or 0), s.get("color_transfer") or "",
            float((data.get("format") or {}).get("duration") or 0))


def source() -> tuple[pathlib.Path, str | None]:
    """Le dérush pleine résolution (champ « source » du _cuts.json), sinon base.mp4 avec la raison."""
    src = ROOT / str(sections.CUTS.get("source") or "")
    if not src.is_file():
        return BASE, f"dérush pleine résolution introuvable ({src.relative_to(ROOT)})"
    w, h, transfer, duree = probe(src)
    if transfer in HDR:
        return BASE, "dérush en HDR : visage relu dans base.mp4, déjà converti (motion-design/references/transcodage-video.md)"
    if abs(duree - sections.DURATION) > 0.2:
        return BASE, f"le dérush ({duree:.2f} s) ne fait pas la durée des coupes ({sections.DURATION:.2f} s)"
    return src, None


def zone(cadre: str, w: int, h: int) -> tuple[int, int, int, int]:
    """(largeur, hauteur, x, y) du cadre dans le rush, en 16:9, bornée à l'image."""
    if w / h >= W / H:                       # rush horizontal : la bande 16:9 garde toute la hauteur
        lw, lh = round(h * W / H), h
    else:                                    # rush vertical ou 4:3 : bande 16:9 autour des yeux
        lw, lh = w, round(w * H / W)
    z = ZOOMS[cadre]
    cw, ch = round(lw / z), round(lh / z)
    cx, ey = CADRAGE["visageX"] * w, CADRAGE["yeuxY"] * h
    # Yeux vers 40 % de la hauteur du cadre ; le large d'un rush horizontal garde toute l'image.
    cible = YEUX_DANS_LE_CADRE[cadre] or 0.40
    x = cx - cw / 2
    y = 0 if ch == h else ey - cible * ch
    x, y = min(max(x, 0), w - cw), min(max(y, 0), h - ch)
    cw, ch = cw - cw % 2, ch - ch % 2
    return cw, ch, round(x) - round(x) % 2, round(y) - round(y) % 2


def encode(src: pathlib.Path, zones: dict[str, tuple[int, int, int, int]]) -> None:
    """Tous les cadres en UN passage : le dérush (souvent 4K) n'est décodé qu'une fois, puis découpé
    en parallèle ; trois passages séparés le décodaient trois fois (le plus long de l'étape)."""
    noms = list(zones)
    graphe = f"[0:v:0]split={len(noms)}" + "".join(f"[s{i}]" for i in range(len(noms))) + ";" + ";".join(
        f"[s{i}]crop={z[0]}:{z[1]}:{z[2]}:{z[3]},scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS}[v{i}]"
        for i, z in enumerate(zones.values()))
    # 30 im/s exactement, la cadence du rendu : une source à 29,97 y serait lue avec une image de
    # retard qui varie (l'image affichée est la dernière dont l'horodatage précède l'instant rendu).
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-filter_complex", graphe]
    for i, cadre in enumerate(noms):
        cmd += ["-map", f"[v{i}]", *ENCODE, str(ROOT / f"assets/video/visage-{cadre}.mp4")]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-1500:])
        sys.exit(f"ERREUR : ffmpeg n'a pas pu produire les visages ({', '.join(noms)}).")


def apercu(src: pathlib.Path, w: int, h: int) -> None:
    """Une image du rush avec les trois cadres dessinés : à regarder avant de régler youtube.cadrage."""
    t = (sections.TAKES[0]["start"] + sections.TAKES[0]["end"]) / 2
    boites = ",".join(f"drawbox=x={x}:y={y}:w={cw}:h={ch}:color={COULEURS[c]}@0.9:t={max(4, w // 400)}"
                      for c in ZOOMS for cw, ch, x, y in [zone(c, w, h)])
    out = ROOT / "work/cadrage-apercu.jpg"
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(src), "-frames:v", "1",
                    "-vf", f"{boites},scale=1280:-2", str(out)], check=True)
    print(f"• {out.relative_to(ROOT)} : blanc = large, jaune = serre, rouge = très serré")
    print(f"  cadrage actuel : visageX {CADRAGE['visageX']}, yeuxY {CADRAGE['yeuxY']} (brand.config.json -> youtube.cadrage)")


def main() -> None:
    if not BASE.exists():
        sys.exit("ERREUR : assets/video/base.mp4 introuvable (fais d'abord le dérush, puis base.mp4).")
    src, repli = source()
    w, h, _, _ = probe(src)
    print(f"visage lu dans : {src.relative_to(ROOT)} ({w}x{h})")
    if repli:
        print(f"  ⚠️ visage moins net : {repli}")
    if h > w:
        print("  ⚠️ rush vertical : le cadre large est une bande 16:9 agrandie. Pour YouTube, on filme à l'horizontale.")
    if "--apercu" in sys.argv:
        apercu(src, w, h)
        return
    zones = {}
    for cadre in sections.CADRES:
        if sections.fenetres(cadre):
            zones[cadre] = zone(cadre, w, h)
        else:
            (ROOT / f"assets/video/visage-{cadre}.mp4").unlink(missing_ok=True)
    encode(src, zones)
    for cadre, z in zones.items():
        agrandi = W / z[0]
        note = f"  ⚠️ agrandi x{agrandi:.2f} : moins net, tourne en 4K pour ce cadre" if agrandi > 1.35 else ""
        print(f"• assets/video/visage-{cadre}.mp4 : zone {z[0]}x{z[1]} en ({z[2]}, {z[3]}) du rush{note}")
    print("Ensuite : python3 tools/build_master.py --write (le master pose ces vidéos sans les agrandir).")


if __name__ == "__main__":
    main()
