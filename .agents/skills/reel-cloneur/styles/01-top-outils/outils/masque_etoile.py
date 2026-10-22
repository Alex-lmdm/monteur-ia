#!/usr/bin/env python3
"""MASQUE DE L'ÉTOILE (style n°01, pièce carte-outil) : la silhouette du client, pour que l'étoile
passe DERRIÈRE lui.

Usage (depuis le dossier du Reel) :
    python3 <kit>/outils/masque_etoile.py <debut> <fin> assets/images/masque-<id>.png [--video assets/video/base.mp4]

Prend 4 images de la vidéo entre <debut> et <fin> (la fenêtre de la carte, en secondes du montage),
détoure la personne sur chacune avec le modèle LOCAL de HyperFrames (`npx hyperframes
remove-background`, gratuit, rien n'est envoyé ni généré), réunit les 4 silhouettes, les élargit
d'environ 8 px, puis écrit un PNG 1080×1920 opaque partout SAUF sur la silhouette. La pièce
carte-outil s'en sert comme masque de l'étoile (DONNEES.masque). Sans masque, elle retombe sur
une ellipse autour de la tête (moins juste : on voit le mur entre les cheveux et l'étoile).
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageFilter

p = argparse.ArgumentParser()
p.add_argument("debut", type=float)
p.add_argument("fin", type=float)
p.add_argument("sortie")
p.add_argument("--video", default="assets/video/base.mp4")
a = p.parse_args()

union = None
with tempfile.TemporaryDirectory() as tmp:
    for k in range(4):
        t = a.debut + (a.fin - a.debut) * (k + 0.5) / 4
        img = pathlib.Path(tmp) / f"f{k}.png"
        out = pathlib.Path(tmp) / f"d{k}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1",
                        "-vf", "scale=1080:1920", str(img)], check=True)
        r = subprocess.run(["npx", "hyperframes", "remove-background", str(img), "-o", str(out)],
                           capture_output=True, text=True)
        if r.returncode or not out.exists():
            sys.exit(f"détourage impossible à {t:.2f} s :\n{r.stderr[-800:]}")
        alpha = Image.open(out).convert("RGBA").getchannel("A")
        union = alpha if union is None else ImageChops.lighter(union, alpha)

# Silhouette nette, élargie (~8 px) en basse résolution puis remise à la taille, bord adouci.
sil = union.point(lambda v: 255 if v > 110 else 0)
petit = sil.resize((270, 480), Image.BILINEAR).filter(ImageFilter.MaxFilter(5))
sil = petit.resize((1080, 1920), Image.BILINEAR).point(lambda v: 255 if v > 90 else 0).filter(ImageFilter.GaussianBlur(2))
masque = Image.new("RGBA", (1080, 1920), (0, 0, 0, 255))
masque.putalpha(ImageChops.invert(sil))
pathlib.Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
masque.save(a.sortie, optimize=True)
print(f"masque écrit : {a.sortie} (silhouette de {a.debut:.2f} à {a.fin:.2f} s)")
