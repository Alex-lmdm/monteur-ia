#!/usr/bin/env python3
"""GARDE-FOU de l'export — a lancer APRES chaque rendu de renders/overlay.mov, AVANT de livrer.

`npm run check` valide la structure, pas le calque REELLEMENT rendu. Or le rendu peut diverger
silencieusement du studio (bugs du 2026-07-14) :

  1. CSS des sous-comps GLOBAL : au render, toutes les sous-comps sont injectees dans UN SEUL
     document. Un `html, body { height: 920px }` d'un split ecrasait le 1920 des plein-ecrans ->
     calque rogne a 920px (sections coupees en deux, sous-titres coupes a la jointure).
  2. Scripts NON montes : si le master reference ses sous-comps par un chemin qui REMONTE
     (`../compositions/x.html`), le runtime monte le DOM + le CSS mais PAS les <script> ->
     AUCUNE timeline ne tourne, tout reste fige a l'etat CSS (rien ne s'anime).

Les deux passaient inapercus dans le studio (qui monte chaque sous-comp dans son propre iframe).
D'ou ce test sur le .mov, la seule verite.

  A) plein ecran -> le calque doit etre OPAQUE partout (sinon le visage transparait dessous)
     split       -> la moitie BASSE doit etre transparente (le visage passe dessous)
  B) au debut d'une section plein ecran, les lignes de reponse doivent etre CACHEES
     (elles sont posees a opacity:0 par GSAP : si elles s'affichent, le JS n'a pas tourne)
"""
import io
import pathlib
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOV = ROOT / "renders/overlay.mov"


def frame(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(MOV), "-frames:v", "1",
                          "-c:v", "png", "-f", "image2pipe", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGBA")


ko = 0
print("A) opacite du calque")
for s in sections.sections():
    a = frame(round(s["start"] + s["dur"] * 0.6, 2)).split()[3]
    m = lambda b: round(sum(a.crop(b).getdata()) / ((b[2] - b[0]) * (b[3] - b[1])))
    top, bot = m((0, 0, 1080, 920)), m((0, 920, 1080, 1920))
    ok = (top == 255 and bot == 255) if s["fmt"] == "full" else bot < 40
    ko += not ok
    print(f"   {s['id']:<14} haut={top:3} bas={bot:3}  {'OK' if ok else '!! KO (calque rogne / non opaque)'}")

print("\nB) les timelines des sections tournent (lignes cachees au debut d'un plein ecran)")
for s in sections.sections():
    if s["fmt"] != "full":
        continue
    im = frame(round(s["start"] + 0.20, 2)).convert("L").crop((200, 900, 900, 1200))
    px = list(im.getdata())
    clair = sum(1 for p in px if p > 150) / len(px)
    ok = clair < 0.02
    ko += not ok
    print(f"   {s['id']:<14} {clair*100:5.1f}% de pixels clairs  {'OK' if ok else '!! JS MUET (scripts non montes)'}")

print("\n" + ("✅ EXPORT CONFORME" if ko == 0 else f"❌ {ko} PROBLEME(S) — NE PAS LIVRER"))
sys.exit(1 if ko else 0)
