#!/usr/bin/env python3
"""SOURCE UNIQUE des sections d'une vidéo YouTube (1920x1080, 30 im/s).

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE VIDEO.                                          ║
║  - CUTS_PATH : le <video>_cuts.json de TON dérush (change ce chemin).          ║
║  - LAYOUT    : la table des sections de TA vidéo (une ligne = une section).    ║
║  - EMPHASES  : les phrases à appuyer d'un texte à l'écran.                     ║
║ Le reste (contrôles, fenêtres du visage, alertes) est générique.               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Les frontières viennent de <video>_cuts.json (les VRAIES coupes, mesurées dans le fichier livré
par tools/cut_boundaries.py), jamais d'une re-transcription Whisper (ses débuts de segment tombent
0,1 à 0,25 s trop tôt : on verrait la fin de la prise précédente).

Tout le montage lit ce module : le master (tools/build_master.py), les visages pré-cadrés
(tools/build_faces.py), les textes d'appui et les sous-titres (tools/build_emphases.py), les
chapitres (tools/publication.py) et les sons (tools/build_sfx.py). Une seule source : impossible
de les désynchroniser.

Usage : python3 tools/sections.py   (affiche la table, les fenêtres du visage et les alertes)
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lieux import config  # noqa: E402  (réglages du client, partagés par toutes ses vidéos)

ROOT = pathlib.Path(__file__).resolve().parent.parent

# >>> A CHANGER A CHAQUE VIDEO : le _cuts.json produit par tools/cut_boundaries.py.
#     Ici : la démo du gabarit (3 prises sur 9 s).
CUTS_PATH = ROOT / "derush/exemple_cuts.json"

CUTS = json.loads(CUTS_PATH.read_text(encoding="utf-8"))
TAKES = CUTS["takes"]
DURATION = CUTS["duration"]

# >>> A REMPLIR A CHAQUE VIDEO : la table des sections.
#   (id, format, [index des prises couvertes], {options})
#     face  -> le créateur plein cadre, rien par-dessus. Le cadre change à chaque coupe
#              (« large » puis « serre ») : c'est ce qui cache les jump cuts.
#     cote  -> le créateur glisse sur un côté, un panneau compositions/<id>.html (960x1080) entre
#              de l'autre. Pour expliquer, lister, montrer un schéma pendant qu'il parle.
#     over  -> le créateur plein cadre + compositions/<id>.html (1920x1080, fond TRANSPARENT)
#              par-dessus : bandeau nom, logo qui apparaît près de la tête, petit schéma.
#     full  -> motion plein écran compositions/<id>.html (1920x1080) : le visage est couvert.
#              {"media": "fichier.mp4"} -> B-roll plein écran (vidéo posée dans le master).
#
#   Options :
#     "cadre": "large" | "serre" | "tres-serre"  -> un seul cadre pour toute la section ;
#     "cadres": ["large", "serre"]               -> cadres alternés à chaque prise ; sans option, plan
#                                                   large (youtube.punchIn = "parcimonie", défaut) ou
#                                                   alterné (youtube.punchIn = "alterne") ;
#     "panneau": "droite" | "gauche"             -> côté du panneau d'une section cote (le créateur
#                                                   part de l'autre côté ; défaut youtube.panneau) ;
#     "chapitre": "Titre"                        -> cette section ouvre un chapitre YouTube
#                                                   (la 1re section en ouvre toujours un) ;
#     "media": "fichier.mp4"                     -> B-roll d'une section full (assets/video/).
#
#   Les index pointent dans TAKES (0-based) et couvrent TOUTES les prises, dans l'ordre, sans trou
#   ni chevauchement (les contrôles plus bas le vérifient).
#
# DÉMO : trois sections sur les 3 prises d'exemple, pour voir les trois cadrages de base.
LAYOUT = [
    ("s0-hook", "face", [0], {"chapitre": "Introduction", "cadre": "large"}),
    ("exemple-panneau", "cote", [1]),
    ("s2-retour", "face", [2], {"cadre": "serre"}),
]

# >>> A REMPLIR A CHAQUE VIDEO : les phrases à appuyer d'un texte à l'écran (pas de sous-titres
#     continus sur YouTube). "dit" = les mots tels que prononcés, retrouvés dans le
#     <video>_words.json (tools/build_words.py) ; "texte" = ce qui s'affiche (court, sans
#     ponctuation finale ; défaut : les mots dits). 1 à 3 par minute, sur les chiffres, les noms
#     propres et les idées-clés, jamais une phrase entière.
EMPHASES = [
    {"dit": "le rythme", "texte": "LE RYTHME"},
]

FORMATS = ("face", "cote", "over", "full")
CADRES = ("large", "serre", "tres-serre")
YT = config().get("youtube") or {}


def _cadres_par_defaut() -> list[str]:
    # Zoom avec parcimonie (défaut) : plan large, le serré se pose à la main sur ce qui compte.
    return ["large", "serre"] if YT.get("punchIn") == "alterne" else ["large"]


def _panneau_par_defaut() -> str:
    return "gauche" if YT.get("panneau") == "gauche" else "droite"


def sections() -> list[dict]:
    out, ids = [], set()
    for entry in LAYOUT:
        sid, fmt, idx = entry[0], entry[1], list(entry[2])
        opts = dict(entry[3]) if len(entry) > 3 else {}
        assert fmt in FORMATS, f"{sid} : format « {fmt} » inconnu ({', '.join(FORMATS)})"
        assert sid not in ids, f"{sid} : id déjà pris par une autre section"
        assert idx, f"{sid} : aucune prise"
        ids.add(sid)
        media = opts.get("media")
        assert not media or fmt == "full", f"{sid} : un B-roll (media) se pose en section full"
        if fmt == "cote":
            cadres = ["large"]
        elif fmt == "full":
            cadres = []
        elif opts.get("cadre"):
            cadres = [opts["cadre"]]
        else:
            cadres = list(opts.get("cadres") or _cadres_par_defaut())
        for c in cadres:
            assert c in CADRES, f"{sid} : cadre « {c} » inconnu ({', '.join(CADRES)})"
        panneau = opts.get("panneau") or _panneau_par_defaut()
        assert panneau in ("droite", "gauche"), f"{sid} : panneau « {panneau} » (droite ou gauche)"
        start, end = TAKES[idx[0]]["start"], TAKES[idx[-1]]["end"]
        out.append({"id": sid, "fmt": fmt, "takes": idx, "media": media,
                    "start": round(start, 3), "end": round(end, 3), "dur": round(end - start, 3),
                    "cadres": cadres, "panneau": panneau if fmt == "cote" else None,
                    "chapitre": opts.get("chapitre")})
    assert out[0]["start"] == 0.0, "la 1re section doit démarrer à 0"
    assert abs(out[-1]["end"] - DURATION) < 0.01, "la dernière section doit finir à la fin du cut"
    prises = [i for s in out for i in s["takes"]]
    assert prises == list(range(len(TAKES))), "les sections doivent couvrir toutes les prises, dans l'ordre"
    for a, b in zip(out, out[1:]):
        assert abs(a["end"] - b["start"]) < 1e-6, f"trou ou chevauchement entre {a['id']} et {b['id']}"
    return out


def cadre_par_prise() -> list[dict]:
    """Une ligne par prise : sa fenêtre et le cadre du visage (None = visage couvert).
    Autour d'une section cote, la prise voisine passe en « large » (si la section l'alterne) :
    le créateur glisse alors depuis le plein cadre, d'un seul geste, au lieu d'une coupe."""
    lignes = []
    secs = sections()
    for k, s in enumerate(secs):
        avant_cote = k + 1 < len(secs) and secs[k + 1]["fmt"] == "cote"
        apres_cote = k > 0 and secs[k - 1]["fmt"] == "cote"
        for n, i in enumerate(s["takes"]):
            cadre = s["cadres"][n % len(s["cadres"])] if s["cadres"] else None
            bord = (n == len(s["takes"]) - 1 and avant_cote) or (n == 0 and apres_cote)
            if bord and s["fmt"] != "cote" and "large" in s["cadres"]:
                cadre = "large"
            lignes.append({"take": i, "start": round(TAKES[i]["start"], 3), "end": round(TAKES[i]["end"], 3),
                           "cadre": cadre, "section": s["id"], "fmt": s["fmt"], "panneau": s["panneau"]})
    return lignes


def fenetres(cadre: str) -> list[tuple[float, float]]:
    """Fenêtres (début, durée) où le visage est montré dans ce cadre ; les contiguës fusionnées."""
    wins: list[list[float]] = []
    for p in cadre_par_prise():
        if p["cadre"] != cadre:
            continue
        if wins and abs(wins[-1][1] - p["start"]) < 1e-6:
            wins[-1][1] = p["end"]
        else:
            wins.append([p["start"], p["end"]])
    return [(round(a, 3), round(b - a, 3)) for a, b in wins]


def fenetres_cote() -> list[dict]:
    """Passages où le créateur est décalé (sections cote contiguës du même côté fusionnées),
    avec le cadre visible juste avant et juste après (« cote » si c'est un autre décalage, None si
    un plein écran) : le master anime le glissement seulement depuis et vers le visage large."""
    prises = cadre_par_prise()

    def visage(p: dict | None) -> str | None:
        if p is None:
            return None
        return "cote" if p["fmt"] == "cote" else p["cadre"]

    out: list[dict] = []
    for k, p in enumerate(prises):
        if p["fmt"] != "cote":
            continue
        suivant = prises[k + 1] if k + 1 < len(prises) else None
        if out and out[-1]["panneau"] == p["panneau"] and abs(out[-1]["end"] - p["start"]) < 1e-6:
            out[-1]["end"] = p["end"]
        else:
            out.append({"start": p["start"], "end": p["end"], "panneau": p["panneau"],
                        "avant": visage(prises[k - 1] if k > 0 else None)})
        meme = suivant is not None and suivant["fmt"] == "cote" and suivant["panneau"] == p["panneau"]
        if not meme:
            out[-1]["apres"] = visage(suivant)
    return out


def chapitres() -> list[tuple[float, str]]:
    """(début, titre) de chaque chapitre ; la 1re section en ouvre toujours un."""
    secs = sections()
    out = [(s["start"], s["chapitre"]) for s in secs if s["chapitre"]]
    if out and out[0][0] > 0:
        out.insert(0, (0.0, "Introduction"))
    return out


# --- alertes de rythme (règles du skill youtube, références/doctrine.md) ----------------------
PLAN_FIXE_MAX = 12.0     # s sur le même cadre sans aucun changement : on décroche
SANS_VISUEL_MAX = 45.0   # s sans panneau, incrustation, plein écran ni texte d'appui
VISAGE_ENTRE_GRAPHIQUES = 2.0   # s de visage au moins entre deux plans plein écran


def _mmss(t: float) -> str:
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def alertes() -> list[str]:
    out: list[str] = []
    secs = sections()
    # 1) plan fixe trop long (même cadre, même section)
    debut, cadre_prec = None, None
    for p in cadre_par_prise() + [{"start": DURATION, "end": DURATION, "cadre": "__fin__", "section": None}]:
        cle = (p["cadre"], p["section"]) if p["cadre"] else None
        if cle != cadre_prec:
            if cadre_prec and debut is not None and p["start"] - debut > PLAN_FIXE_MAX:
                out.append(f"plan fixe de {p['start'] - debut:.0f} s à {_mmss(debut)} : alterne le cadre, "
                           "pose un panneau ou un texte d'appui")
            debut, cadre_prec = p["start"], cle
    # 2) trop longtemps sans élément visuel
    temps = sorted([s["start"] for s in secs if s["fmt"] != "face"] + [s["end"] for s in secs if s["fmt"] != "face"])
    temps = [0.0] + temps + [DURATION]
    for a, b in zip(temps, temps[1:]):
        if b - a > SANS_VISUEL_MAX:
            out.append(f"{b - a:.0f} s sans panneau ni graphique à partir de {_mmss(a)} : un changement "
                       "visuel toutes les 15 à 30 s")
    # 3) graphiques plein écran
    plein = [s for s in secs if s["fmt"] == "full"]
    for a, b in zip(plein, plein[1:]):
        if 0 < b["start"] - a["end"] < VISAGE_ENTRE_GRAPHIQUES:
            out.append(f"moins de {VISAGE_ENTRE_GRAPHIQUES:.0f} s de visage entre {a['id']} et {b['id']} : "
                       "allonge le premier plan ou garde le visage plus longtemps")
    if secs[0]["fmt"] == "full":
        out.append("la vidéo s'ouvre sur un plan plein écran : le hook se dit face caméra")
    # 4) chapitres YouTube : 00:00, au moins 3, chacun d'au moins 10 s
    ch = chapitres()
    if ch:
        if len(ch) < 3:
            out.append(f"{len(ch)} chapitre(s) : YouTube n'affiche les chapitres qu'à partir de 3")
        bornes = [t for t, _ in ch] + [DURATION]
        for (t, titre), fin in zip(ch, bornes[1:]):
            if fin - t < 10:
                out.append(f"chapitre « {titre} » de {fin - t:.0f} s : YouTube exige 10 s au moins")
    return out


if __name__ == "__main__":
    for s in sections():
        extra = s["media"] or (f"panneau {s['panneau']}" if s["panneau"] else "/".join(s["cadres"]))
        chap = f"  [chapitre : {s['chapitre']}]" if s["chapitre"] else ""
        print(f'{s["id"]:<18} {s["fmt"]:<5} {_mmss(s["start"])} {s["start"]:8.3f} -> {s["end"]:8.3f}  '
              f'({s["dur"]:6.2f} s)  {extra}{chap}')
    for c in CADRES:
        w = fenetres(c)
        if w:
            print(f"\nvisage « {c} » : {len(w)} fenêtre(s)")
    for f in fenetres_cote():
        print(f"décalé {_mmss(f['start'])} -> {_mmss(f['end'])}  panneau {f['panneau']}  "
              f"(avant : {f['avant']}, après : {f['apres']})")
    al = alertes()
    print("\n" + ("\n".join(f"⚠️ {a}" for a in al) if al else "✅ rythme : aucune alerte"))
