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

# Cadence du rendu (data-fps du master, bouton Export de l'app). Les coupes sont mesurees au
# millieme dans le derush ; le rendu, lui, n'affiche que des images (n / FPS). Une borne posee entre
# deux images s'affichait sur la SUIVANTE : sous-titre en retard d'une image, ancienne section encore
# visible une image apres la coupe alors que le visage avait deja change. Toutes les bornes du montage
# (sections, sous-titres, duree) sont donc posees sur l'image la plus proche, comme les fenetres du
# visage (tools/build_master.py, fenetre()).
FPS = 30


def image(t):
    """L'instant `t` pose sur l'image du rendu la plus proche (n / FPS)."""
    return round(float(t) * FPS) / FPS


CUTS = json.loads(CUTS_PATH.read_text(encoding="utf-8"))
TAKES = CUTS["takes"]
DURATION = round(image(CUTS["duration"]), 5)   # duree du montage : un nombre entier d'images

# >>> A REMPLIR A CHAQUE NOUVEAU REEL : la table des sections.
#   (id, format, [index des prises couvertes], {options})
#     id     -> il DOIT exister un compositions/<id>.html du meme nom.
#     split  -> panneau motion 1080x920 en HAUT + visage en BAS.
#     full   -> motion 1080x1920 plein ecran, le visage est couvert.
#     face   -> VISAGE plein ecran, aucun motion (pas de compositions/<id>.html a creer).
#               Sert a casser le rythme : on enleve tout le decor et on revient sur toi.
#               Cadrage = brand.config.json -> montage.fullFaceTransform (calibre par /setup).
#     decor  -> la VIDEO FILMEE plein ecran, decor compris, et la sous-composition PAR-DESSUS
#               (fond transparent : cartes, titres, captures posees sur le decor, en haut). C'est
#               le format des Reels « cartes au-dessus de la tete » : jamais un ecran partage.
#               Cadrage = montage.decorTransform / decorOrigin (sans reglage : la video telle que
#               filmee ; visage trop haut -> scale(1.5) autour de « center top » le fait descendre).
#     detoure -> la PERSONNE DETOUREE (sans son decor) posee DEVANT la sous-composition : la
#               section peint le fond (page web, aplat, objets), la personne passe par-dessus.
#               tools/build_faces.py prepare visage-detoure.webm (detourage local, la premiere fois :
#               modele de 170 Mo a telecharger). Cadrage = montage.detoureTransform / detoureOrigin.
#
#   {"media": "fichier.mp4"} -> la section n'est PAS une sous-composition : c'est une <video>
#   posee directement dans le master (couche video NATIVE, compositee ensuite par ffmpeg).
#   ⛔ NE JAMAIS mettre un b-roll dans une sous-composition : le `data-start="0"` de la <video>
#   y est relatif a la compo, mais le runtime media le lit en ABSOLU -> la video s'affiche des
#   0 s, sur toute la timeline, et RECOUVRE les autres sections. Symptome : « je vois une video
#   figee au debut du reel, et mes autres sections sont noires ». En prime, passer un b-roll par
#   le render HyperFrames le rasterise (perte de nettete) alors que ffmpeg le garde intact.
#   Exemple :  ("s3-demo", "full", [3], {"media": "demo-broll-v1.mp4"}),
#
#   {"zoom": 1.25} -> (sections "decor", "face" et "split") la section se montre PLUS SERREE que le cadrage du
#   Reel, d'un coup a la coupe (1.25 = un quart plus serre). {"zoomOrigin": "center 30%"} = le point
#   qui reste fixe (les yeux, par defaut vers 30 % du haut). tools/build_faces.py prepare une video
#   nette par niveau de zoom. Exemple :  ("s4-point-fort", "decor", [4], {"zoom": 1.25}),
#   {"zoom": [1.25, 1], "zoomDuree": 0.8} -> zoom PROGRESSIF : de 1.25 au debut de la section a 1 en
#   0,8 s (1,3 fois d'ecart au plus ; sections "decor" et "face" seulement).
#   Les index pointent dans TAKES (0-based) et doivent couvrir TOUTES les prises, dans l'ordre,
#   sans trou ni chevauchement (les asserts plus bas le verifient).
#
# DEMO : une seule section split "exemple-section" qui couvre les 3 prises (0 -> 8 s) et
# correspond a compositions/exemple-section.html (index.html livre n'est qu'un apercu :
# build_master.py genere le vrai master depuis cette table).
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
Y_FACE = 1140    # visage plein ecran : un peu SOUS le centre, sinon le sous-titre tombe sur la
                 # bouche. (Plus le nombre est GRAND, plus le sous-titre est BAS.)
Y_FULL = 1500    # sous la fenetre plein ecran (motion / images)
Y_MEDIA = 1100   # b-roll plein ecran : juste SOUS le milieu. A 1500 le sous-titre tombe sur le
                 # bas de l'image (souvent la partie inutile : bureau, clavier, decor).
Y_DECOR = 760    # cartes sur le decor : juste SOUS les cartes du haut, au-dessus de la tete.
Y_DETOURE = 1250  # personne detouree devant les visuels : sur le buste, sous le visage.


def sections():
    out = []
    for entry in LAYOUT:
        sid, fmt, idx = entry[0], entry[1], entry[2]
        opts = entry[3] if len(entry) > 3 else {}
        media = opts.get("media")
        start = TAKES[idx[0]]["start"]
        end = TAKES[idx[-1]]["end"]
        if fmt == "split":
            y = Y_SPLIT
        elif fmt == "face":
            y = Y_FACE
        elif fmt == "decor":
            y = Y_DECOR
        elif fmt == "detoure":
            y = Y_DETOURE
        else:
            y = Y_MEDIA if media else Y_FULL
        out.append({"id": sid, "fmt": fmt, "takes": idx, "media": media,
                    "start": round(start, 3), "end": round(end, 3), "dur": None,
                    "y": y})
    assert out[0]["start"] == 0.0, "la 1re section doit demarrer a 0"
    assert abs(out[-1]["end"] - CUTS["duration"]) < 0.01, "la derniere section doit finir a la fin du cut"
    for a, b in zip(out, out[1:]):
        assert abs(a["end"] - b["start"]) < 1e-6, f"trou/chevauchement entre {a['id']} et {b['id']}"
    # Bornes sur les images du rendu (cf. FPS) : la meme coupe donne la meme image partout.
    for s in out:
        s["start"] = image(s["start"])
        s["end"] = DURATION if s is out[-1] else image(s["end"])
        s["dur"] = s["end"] - s["start"]
    return out


def _merge_windows(fmt):
    wins = []
    for s in sections():
        if s["fmt"] != fmt:
            continue
        if wins and abs(wins[-1][1] - s["start"]) < 1e-6:
            wins[-1] = (wins[-1][0], s["end"])
        else:
            wins.append((s["start"], s["end"]))
    return [(round(a, 3), round(b - a, 3)) for a, b in wins]


def face_windows():
    """Fenetres visage SPLIT (moitie basse) — les splits contigus sont fusionnes."""
    return _merge_windows("split")


def facefull_windows():
    """Fenetres visage PLEIN ECRAN (sections 'face') — contigues fusionnees."""
    return _merge_windows("face")


def decor_windows():
    """Fenetres video filmee plein ecran SOUS les cartes (sections 'decor'), contigues fusionnees."""
    return _merge_windows("decor")


def detoure_windows():
    """Fenetres personne detouree DEVANT les visuels (sections 'detoure'), contigues fusionnees."""
    return _merge_windows("detoure")


if __name__ == "__main__":
    for s in sections():
        print(f'{s["id"]:<16} {s["fmt"]:<5} {s["start"]:6.3f} -> {s["end"]:6.3f}  '
              f'({s["dur"]:5.3f}s)  y={s["y"]}')
    print("\nfenetres visage (split) :")
    for st, d in face_windows():
        print(f"  {st:6.3f}  +{d:.3f}")
    ff = facefull_windows()
    if ff:
        print("fenetres visage (plein ecran) :")
        for st, d in ff:
            print(f"  {st:6.3f}  +{d:.3f}")
    tt = detoure_windows()
    if tt:
        print("fenetres personne detouree (devant les visuels) :")
        for st, d in tt:
            print(f"  {st:6.3f}  +{d:.3f}")
    dd = decor_windows()
    if dd:
        print("fenetres decor (video plein ecran sous les cartes) :")
        for st, d in dd:
            print(f"  {st:6.3f}  +{d:.3f}")
