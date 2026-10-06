#!/usr/bin/env python3
"""GARDE-FOU de l'export — a lancer sur la video finale AVANT de livrer.

Usage (depuis le dossier du Reel) :
    python3 tools/check_export.py                    # export natif : exports/FINAL.mp4
    python3 tools/check_export.py ~/Downloads/x.mp4  # une video sortie par le bouton Export de l'app
    python3 tools/check_export.py --calque           # ancien export : le calque work/overlay.mov

Export natif (la video finale elle-meme) :
  F) format : 1080x1920, duree du montage, une piste son ;
  V) visage present et NON agrandi : la zone visage de chaque fenetre ressemble a la meme image des
     visages pre-cadres (tools/build_faces.py) ; s'ils manquent, le visage vient de base.mp4
     agrandie (moins net) -> signale ;
  T) les timelines tournent (meme principe que B ci-dessous, sur la video finale) ;
  S) le son est la : volume integre au-dessus de -35 LUFS.

Ancien export (--calque) : gardes A et B sur le calque, decrites ci-dessous.

╔══════════════════════════════════════════════════════════════════════════════╗
║ Ces deux gardes sont GENERIQUES (elles valent pour tout Reel). Le seuil de la  ║
║ garde B (zone echantillonnee) peut demander un petit ajustement selon ton      ║
║ motion : il est documente ci-dessous.                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

`npm run check` valide la STRUCTURE, pas le calque REELLEMENT rendu. Or le rendu peut diverger
silencieusement du studio :

  1. CSS des sous-comps GLOBAL : au render, toutes les sous-comps sont injectees dans UN SEUL
     document. Un `html, body { height: 920px }` d'un split ecraserait le 1920 des plein-ecrans ->
     calque rogne a 920px (sections coupees en deux, sous-titres coupes a la jointure).
  2. Scripts NON montes : si le master reference ses sous-comps par un chemin qui REMONTE
     (`../compositions/x.html`), le runtime monte le DOM + le CSS mais PAS les <script> ->
     AUCUNE timeline ne tourne, tout reste fige a l'etat CSS (rien ne s'anime).

Les deux passaient inapercus dans le studio (qui monte chaque sous-comp dans son propre iframe).
D'ou ce test sur le .mov, la seule verite.

  A) plein ecran -> le calque doit etre OPAQUE partout (sinon le visage transparait dessous)
     split       -> la moitie BASSE doit etre transparente (le visage passe dessous)
  B) au DEBUT d'une section plein ecran, les elements que GSAP pose a opacity:0 (leur etat de
     depart) NE doivent PAS etre visibles. S'ils apparaissent d'emblee => le JS n'a pas tourne
     (scripts non montes, bug 2 ci-dessus). On echantillonne une bande centrale peu apres le
     debut de section et on verifie qu'elle est quasi vide.
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

# Windows : une sortie lue par l'agent (redirigée) est en cp1252, et un « ✅ » y fait planter l'outil.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOV = ROOT / "work/overlay.mov"
FINAL = ROOT / "exports/FINAL.mp4"
VISAGES = {"split": ROOT / "assets/video/visage-split.mp4", "face": ROOT / "assets/video/visage-plein.mp4"}
# Zone du visage comparee, a l'ecart des sous-titres : sous la jointure en split, le haut en plein ecran.
ZONES = {"split": (0, 1100, 1080, 1920), "face": (0, 0, 1080, 1050)}


_MATRICES = {}


def matrice(src):
    """La matrice couleur de la vidéo : son étiquette, sinon bt709. Le navigateur du rendu lit une
    vidéo HD sans étiquette en bt709, ffmpeg en bt601 : sans ce choix, un visage tiré d'une source
    sans étiquette sort plus vert ici qu'à l'export, et la comparaison échoue à tort."""
    if src not in _MATRICES:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_space",
                              "-of", "default=nw=1:nk=1", str(src)], capture_output=True, encoding="utf-8", errors="replace").stdout
        tag = out.strip()
        _MATRICES[src] = tag if tag in ("bt709", "smpte170m", "bt470bg", "bt2020nc", "fcc", "smpte240m") else "bt709"
    return _MATRICES[src]


def grab(src, t, mode="RGBA"):
    m = {"smpte170m": "smpte170m", "bt470bg": "bt470bg", "bt2020nc": "bt2020", "fcc": "fcc", "smpte240m": "smpte240m"}.get(matrice(src), "bt709")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(src), "-frames:v", "1",
                          "-vf", f"scale=in_color_matrix={m}", "-c:v", "png", "-f", "image2pipe", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert(mode)


def frame(t):
    return grab(MOV, t)


def ssim(a, b):
    """SSIM de deux images PIL de meme taille (filtre ssim de ffmpeg)."""
    import re
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        pa, pb = pathlib.Path(d) / "a.png", pathlib.Path(d) / "b.png"
        a.save(pa)
        b.save(pb)
        err = subprocess.run(["ffmpeg", "-v", "info", "-i", str(pa), "-i", str(pb), "-lavfi", "ssim", "-f", "null", "-"],
                             capture_output=True, encoding="utf-8", errors="replace").stderr
    m = re.search(r"All:([\d.]+)", err)
    return float(m.group(1)) if m else 0.0


def verifier_final(mp4):
    import json
    import re
    ko = 0
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                                      "-of", "json", str(mp4)], capture_output=True, encoding="utf-8", errors="replace").stdout or "{}")
    video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    son = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    duree = float((info.get("format") or {}).get("duration") or 0)
    ok = video.get("width") == 1080 and video.get("height") == 1920 and abs(duree - sections.DURATION) < 0.15 and son
    ko += not ok
    print(f"F) format : {video.get('width')}x{video.get('height')}, {duree:.2f} s (montage {sections.DURATION} s), "
          f"son {'oui' if son else 'NON'}  {'OK' if ok else '!! KO'}")

    print("V) visage present, non agrandi, sur la meme image que la voix")
    decalages = []
    for s in sections.sections():
        if s["fmt"] not in VISAGES or s.get("media"):
            continue
        t = round(s["start"] + s["dur"] * 0.5, 2)
        zone = ZONES[s["fmt"]]
        if not VISAGES[s["fmt"]].exists():
            print(f"   {s['id']:<16} visage lu dans base.mp4 agrandie (moins net) : lance python3 tools/build_faces.py "
                  "puis python3 tools/build_master.py --write")
            continue
        image = grab(mp4, t, "RGB").crop(zone)
        # A une image pres : la ressemblance juge la presence et la nettete, l'ecart la synchro.
        scores = {k: ssim(image, grab(VISAGES[s["fmt"]], round(t + k / 30, 4), "RGB").crop(zone)) for k in (-1, 0, 1)}
        score = max(scores.values())
        decalages.append(max(scores, key=scores.get) if score - scores[0] > 0.01 else 0)
        ok = score >= 0.85
        ko += not ok
        print(f"   {s['id']:<16} ressemblance {score:.3f}  {'OK' if ok else '!! KO (visage absent, masque ou recadre)'}")
    # build_master.py cale chaque video sur les images du rendu (fenetre()) : un decalage d'une image
    # sur la plupart des sections veut dire un montage d'avant ce calage, ou un moteur qui a change.
    if decalages and sum(1 for k in decalages if k) * 3 >= len(decalages) * 2:
        ko += 1
        print("   !! visage decale d'une image sur la voix : relance python3 tools/build_faces.py puis python3 "
              "tools/build_master.py --write, puis exporte a nouveau ; si ca persiste, signale-le au support")

    print("T) les timelines des sections tournent")
    fulls = [s for s in sections.sections() if s["fmt"] == "full" and not s.get("media")]
    if not fulls:
        print("   (aucune section 'full' dans LAYOUT : garde sans objet pour ce Reel)")
    for s in fulls:
        band = grab(mp4, round(s["start"] + 0.20, 2), "L").crop((200, 900, 900, 1200))
        px = list(band.getdata())
        moy = sum(px) / len(px)
        ecart = (sum((p - moy) ** 2 for p in px) / len(px)) ** 0.5
        ok = ecart < 12
        ko += not ok
        print(f"   {s['id']:<16} bande centrale ecart-type {ecart:5.1f}  {'OK' if ok else '!! JS MUET (elements visibles des le debut)'}")

    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    lufs = float(m[-1]) if m else -99.0
    ok = lufs > -35
    ko += not ok
    print(f"S) son : {lufs:.1f} LUFS  {'OK' if ok else '!! KO (voix absente ou tres faible)'}")
    print("\n" + ("✅ EXPORT CONFORME" if ko == 0 else f"❌ {ko} point(s) à revoir avant de livrer"))
    sys.exit(1 if ko else 0)


args = [a for a in sys.argv[1:] if not a.startswith("--")]
if "--calque" not in sys.argv:
    cible = pathlib.Path(args[0]).expanduser() if args else FINAL
    if not cible.exists():
        print(f"Rien a verifier : {cible} n'existe pas.")
        print("Exporte d'abord la video : bouton Export de l'app, ou npm run render (exports/FINAL.mp4).")
        sys.exit(0)
    verifier_final(cible)

if not MOV.exists():
    print(f"Rien a verifier : {MOV.relative_to(ROOT)} n'existe pas.")
    print("Fais d'abord le rendu du calque : python3 tools/build_overlay.py --render")
    sys.exit(0)

ko = 0
print("A) opacite du calque")
for s in sections.sections():
    a = frame(round(s["start"] + s["dur"] * 0.6, 2)).split()[3]
    m = lambda b: round(sum(a.crop(b).getdata()) / ((b[2] - b[0]) * (b[3] - b[1])))
    top, bot = m((0, 0, 1080, 920)), m((0, 920, 1080, 1920))
    if s.get("media"):
        # Section MEDIA : le b-roll vit dans le master en couche video native et ne passe PAS
        # par le calque -> le calque DOIT y etre vide. L'inverse serait le bug.
        ok = top == 0 and bot == 0
    elif s["fmt"] == "full":
        ok = top == 255 and bot == 255
    else:
        ok = bot < 40
    ko += not ok
    print(f"   {s['id']:<16} haut={top:3} bas={bot:3}  {'OK' if ok else '!! KO (calque rogne / non opaque)'}")

print("\nB) les timelines des sections tournent (elements a opacity:0 caches au debut d'un plein ecran)")
# Les sections MEDIA n'ont aucune animation a verifier (leur 1er quart de seconde est deja
# l'image, souvent claire) -> sans cette exclusion le test criait « JS MUET » sur chaque b-roll.
fulls = [s for s in sections.sections() if s["fmt"] == "full" and not s.get("media")]
if not fulls:
    print("   (aucune section 'full' dans LAYOUT : garde B sans objet pour ce Reel)")
for s in fulls:
    # Bande centrale, 0.20 s apres le debut : a cet instant les entrees GSAP ne sont pas encore
    # jouees, donc l'element pose a opacity:0 doit laisser la zone quasi vide.
    # Seuil a ajuster si ton motion remplit deja cette zone a t+0.20 (fond plein, gros titre fixe).
    im = frame(round(s["start"] + 0.20, 2)).convert("L").crop((200, 900, 900, 1200))
    px = list(im.getdata())
    clair = sum(1 for p in px if p > 150) / len(px)
    ok = clair < 0.02
    ko += not ok
    print(f"   {s['id']:<16} {clair*100:5.1f}% de pixels clairs  {'OK' if ok else '!! JS MUET (scripts non montes)'}")

print("\n" + ("✅ EXPORT CONFORME" if ko == 0 else f"❌ {ko} point(s) à revoir avant de livrer"))
sys.exit(1 if ko else 0)
