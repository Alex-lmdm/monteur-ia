#!/usr/bin/env python3
"""TEXTES D'APPUI d'une vidéo YouTube (compositions/emphases.html) + sous-titres SRT à téléverser.

Sur YouTube, pas de sous-titres mot à mot en continu : quelques textes courts qui appuient un
chiffre, un nom ou une idée-clé, posés PILE sur les mots prononcés. La liste vit dans
tools/sections.py (EMPHASES) ; les instants viennent du <video>_words.json (tools/build_words.py).

Usage (depuis le dossier de la vidéo) :
    python3 tools/build_emphases.py           # brouillon work/emphases.generated.html + la liste
    python3 tools/build_emphases.py --write   # écrit compositions/emphases.html
    python3 tools/build_emphases.py --srt     # écrit seulement exports/sous-titres.srt

Le SRT (toute la voix, phrase par phrase) se téléverse sur YouTube (Sous-titres > Importer un
fichier) : sous-titres activables par le spectateur, mieux référencés, jamais incrustés.

Option brand.config.json -> youtube.sousTitres = "partout" : en plus des textes d'appui, des
sous-titres continus incrustés (4 à 7 mots, casse normale, bas de l'écran). À réserver à une
chaîne qui le veut vraiment : YouTube propose déjà les siens.

Position : selon le cadre de la prise (large, serré, décalé) ; jamais sur un plein écran (le
texte va alors dans le graphique lui-même).
"""
from __future__ import annotations

import html
import itertools
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from lieux import config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 1920, 1080, 30
DUR = sections.DURATION
WORDS = sections.CUTS_PATH.with_name(sections.CUTS_PATH.name.replace("_cuts.json", "_words.json"))
YT = config().get("youtube") or {}
PARTOUT = YT.get("sousTitres") == "partout"
TENUE_MIN, TENUE_APRES = 1.2, 0.6      # s : un texte reste lisible, et un peu après le dernier mot
Y = {"large": 800, "serre": 840, "tres-serre": 870}   # au-dessus de la barre de lecture, sur le torse
Y_SOUS_TITRES = 900


def normal(mot: str) -> str:
    mot = unicodedata.normalize("NFKD", mot.lower())
    mot = "".join(c for c in mot if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9%€$]+", "", mot)


def mots() -> list[dict]:
    if not WORDS.exists():
        sys.exit(f"ERREUR : {WORDS.relative_to(ROOT)} introuvable : lance d'abord python3 tools/build_words.py.")
    out = []
    for w in json.loads(WORDS.read_text(encoding="utf-8")):
        for morceau in str(w["w"]).split():
            if normal(morceau):
                out.append({"w": morceau, "n": normal(morceau), "start": float(w["start"]), "end": float(w["end"]),
                            "take": w.get("take")})
    return out


def coupe_entre(w: dict, suivant: dict) -> bool:
    """Une vraie coupe du dérush sépare ces deux mots (pas un raccord) : un sous-titre ne l'enjambe
    jamais, même quand Whisper n'a pas mis de point (sinon « … YouTube Il a coupé les »)."""
    a, b = w.get("take"), suivant.get("take")
    return (a is not None and b is not None and a != b and b < len(sections.TAKES)
            and not sections.TAKES[b].get("raccord"))


def trouver(liste: list[dict], dit: str, depuis: int) -> tuple[int, int] | None:
    cible = [normal(m) for m in dit.split() if normal(m)]
    for i in range(depuis, len(liste) - len(cible) + 1):
        if [liste[i + k]["n"] for k in range(len(cible))] == cible:
            return i, i + len(cible) - 1
    return None


def prise_a(t: float) -> dict:
    for p in sections.cadre_par_prise():
        if p["start"] - 1e-6 <= t < p["end"]:
            return p
    return sections.cadre_par_prise()[-1]


def place(t: float) -> tuple[int, int] | None:
    """(x, y) du centre du texte à l'instant t, ou None sur un plein écran."""
    p = prise_a(t)
    if p["cadre"] is None:
        return None
    if p["fmt"] == "cote":
        return (W // 4 if p["panneau"] == "droite" else 3 * W // 4), Y["large"]
    return W // 2, Y[p["cadre"]]


def bornes_section(t: float) -> float:
    for s in sections.sections():
        if s["start"] - 1e-6 <= t < s["end"]:
            return s["end"]
    return DUR


def emphases(liste: list[dict]) -> tuple[list[dict], list[str]]:
    out, erreurs, curseur = [], [], 0
    for e in sections.EMPHASES:
        trouve = trouver(liste, e["dit"], curseur) or trouver(liste, e["dit"], 0)
        if not trouve:
            erreurs.append(f"« {e['dit']} » introuvable dans {WORDS.name} (écris les mots tels que prononcés)")
            continue
        a, b = trouve
        curseur = b + 1
        start = liste[a]["start"]
        fin = min(max(liste[b]["end"] + TENUE_APRES, start + TENUE_MIN), bornes_section(start))
        xy = place(start)
        if xy is None:
            erreurs.append(f"« {e['dit']} » tombe sur un plein écran : mets le texte dans le graphique")
            continue
        out.append({"texte": e.get("texte") or e["dit"], "start": start, "end": fin, "x": xy[0], "y": xy[1]})
    out.sort(key=lambda e: e["start"])
    for x, y in zip(out, out[1:]):      # jamais deux textes d'appui à l'écran en même temps
        x["end"] = min(x["end"], y["start"] - 0.05)
    return out, erreurs


def _texte(morceau: list[dict]) -> str:
    return " ".join(x["w"] for x in morceau)


# Coupe d'un bloc trop long : jamais après un mot faible (article, préposition, conjonction), de
# préférence avant un mot qui ouvre une proposition. Français et espagnol ; ailleurs, l'équilibre seul.
FAIBLES = {"le", "la", "les", "l", "un", "une", "des", "de", "du", "d", "a", "au", "aux", "et", "ou", "que",
           "qui", "pour", "sur", "dans", "en", "par", "avec", "ce", "cette", "ces", "mon", "ma", "mes", "ton",
           "ta", "tes", "son", "sa", "ses", "comme", "mais", "donc", "el", "los", "las", "una", "del", "y",
           "para", "con", "como", "pero", "por", "mi", "tu", "su"}
OUVRANTS = {"que", "qui", "pour", "comme", "et", "mais", "donc", "quand", "parce", "car", "ou", "y", "para",
            "como", "pero", "porque", "cuando"}


def equilibrer(bloc: list[dict], max_mots: int, max_car: int) -> list[list[dict]]:
    """Un bloc trop long se partage en morceaux de longueur égale, jamais un mot seul ni un mot
    faible en bout (« Il a coupé les | blancs et les ratés » devient « Il a coupé les blancs |
    et les ratés »)."""
    n = 1
    while len(bloc) > n * max_mots or len(_texte(bloc)) > n * max_car:
        n += 1
    if n == 1 or len(bloc) < 2 * n:
        return [bloc]

    def cout(points: tuple[int, ...]) -> float:
        bornes = (0, *points, len(bloc))
        morceaux = [bloc[a:b] for a, b in zip(bornes, bornes[1:])]
        trop = sum(len(m) > max_mots or len(_texte(m)) > max_car for m in morceaux)
        seuls = sum(len(m) == 1 for m in morceaux)
        faibles = sum(m[-1]["n"] in FAIBLES for m in morceaux[:-1])
        ouvrants = sum(m[0]["n"] in OUVRANTS for m in morceaux[1:])
        return 1000 * trop + 100 * seuls + 50 * faibles - 30 * ouvrants + max(len(_texte(m)) for m in morceaux)

    # n morceaux au moins ; un de plus s'il évite un mot faible en bout ou un morceau trop long.
    candidats = [c for k in (n, n + 1) if len(bloc) >= 2 * k
                 for c in itertools.combinations(range(1, len(bloc)), k - 1)]
    meilleur = min(candidats, key=lambda c: cout(c) + 40 * (len(c) + 1 - n))
    bornes = (0, *meilleur, len(bloc))
    return [bloc[a:b] for a, b in zip(bornes, bornes[1:])]


def phrases(liste: list[dict], max_mots: int = 8, max_car: int = 42) -> list[dict]:
    """Découpe la voix en phrases courtes : fin de phrase, pause de plus de 0,35 s ou coupe du
    dérush ; une phrase trop longue se partage en morceaux équilibrés."""
    blocs, cur = [], []
    for i, w in enumerate(liste):
        cur.append(w)
        suivant = liste[i + 1] if i + 1 < len(liste) else None
        if (suivant is None or re.search(r"[.!?…:;,]$", w["w"]) or suivant["start"] - w["end"] > 0.35
                or coupe_entre(w, suivant)):
            blocs.append(cur)
            cur = []
    out = []
    for bloc in blocs:
        for m in equilibrer(bloc, max_mots, max_car):
            out.append({"texte": re.sub(r"[.,;:…]+$", "", _texte(m)), "start": m[0]["start"], "end": m[-1]["end"]})
    for x, y in zip(out, out[1:]):
        x["end"] = min(max(x["end"], x["start"] + 1.0), y["start"])
    return out


def srt(liste: list[dict]) -> str:
    def tc(t: float) -> str:
        ms = round(t * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i}\n{tc(p['start'])} --> {tc(p['end'])}\n{p['texte']}\n"
                     for i, p in enumerate(phrases(liste), 1))


def ecrire_srt(liste: list[dict]) -> None:
    out = ROOT / "exports/sous-titres.srt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(srt(liste), encoding="utf-8")
    print(f"• {out.relative_to(ROOT)} : sous-titres à téléverser sur YouTube")


def clip(i: int, classe: str, texte: str, start: float, end: float, x: int, y: int) -> str:
    return (f'      <div class="{classe} clip" id="{classe}-{i}" style="left:{x}px; top:{y}px" '
            f'data-start="{start:.3f}" data-duration="{max(end - start, 0.2):.3f}" data-track-index="{i % 4}">'
            f'{html.escape(texte)}</div>')


def main() -> None:
    liste = mots()
    ecrire_srt(liste)
    if "--srt" in sys.argv:
        return
    emph, erreurs = emphases(liste)
    rows = [clip(i, "appui", e["texte"], e["start"], e["end"], e["x"], e["y"]) for i, e in enumerate(emph)]
    if PARTOUT:
        for j, p in enumerate(phrases(liste)):
            xy = place(p["start"]) or (W // 2, Y_SOUS_TITRES)
            rows.append(clip(j, "sous-titre", p["texte"], p["start"], p["end"], xy[0], Y_SOUS_TITRES))
    # Entrée en opacité + échelle seulement (le centrage xPercent/yPercent ne bouge pas).
    tweens = [f'      tl.fromTo("#appui-{i}", {{ xPercent: -50, yPercent: -50, opacity: 0, scale: 0.92 }}, '
              f'{{ xPercent: -50, yPercent: -50, opacity: 1, scale: 1, duration: 0.18, ease: "power2.out" }}, '
              f'{e["start"]:.3f});' for i, e in enumerate(emph)]
    doc = f'''<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width={W}, height={H}">
    <!-- TEXTES D'APPUI : générés par tools/build_emphases.py depuis tools/sections.py (EMPHASES)
         et les mots horodatés du dérush. Ne pas éditer ici : modifier EMPHASES puis --write. -->
    <script src="assets/vendor/gsap.min.js"></script>
    <link rel="stylesheet" href="brand/fonts.css">
    <link rel="stylesheet" href="brand/tokens.css">
    <style>
      html, body {{ width: 100%; height: 100%; overflow: hidden; background: transparent; }}
      #emphases {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden; }}
      /* L'allure vient du skin de sous-titres de la marque (.cap, brand/tokens.css), en plus grand. */
      #emphases .appui, #emphases .sous-titre {{ position: absolute; transform: translate(-50%, -50%);
        white-space: nowrap; }}
      #emphases .appui {{ font-size: var(--brand-yt-emphase-size); }}
      #emphases .sous-titre {{ font-size: var(--brand-yt-caption-size); text-transform: none; font-weight: 700; }}
    </style>
  </head>
  <body>
    <div id="emphases" data-composition-id="emphases" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
{chr(10).join(rows)}
    </div>
    <script>
      (function () {{
      window.__timelines = window.__timelines || {{}};
      var tl = gsap.timeline({{ paused: true }});
{chr(10).join(tweens)}
      window.__timelines["emphases"] = tl;
      }})();
    </script>
  </body>
</html>
'''
    # La classe .cap porte le skin de la marque : on l'ajoute aux deux sortes de textes.
    doc = doc.replace('class="appui clip"', 'class="cap appui clip"').replace(
        'class="sous-titre clip"', 'class="cap sous-titre clip"')
    if "--write" in sys.argv:
        out = ROOT / "compositions/emphases.html"
    else:
        (ROOT / "work").mkdir(exist_ok=True)
        out = ROOT / "work/emphases.generated.html"
    out.write_text(doc, encoding="utf-8")
    print(f"{out.relative_to(ROOT)} : {len(emph)} texte(s) d'appui" + (" + sous-titres continus" if PARTOUT else ""))
    for e in emph:
        print(f"  {sections._mmss(e['start'])} {e['start']:8.2f} -> {e['end']:8.2f}  ({e['x']}, {e['y']})  {e['texte']}")
    for err in erreurs:
        print(f"  ⚠️ {err}")
    if "--write" not in sys.argv:
        print("(brouillon ; relance avec --write pour écrire compositions/emphases.html, puis build_master.py --write)")


if __name__ == "__main__":
    main()
