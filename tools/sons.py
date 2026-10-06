#!/usr/bin/env python3
"""SONS DANS LE MONTAGE : pose les SFX et la musique d'un Reel dans son index.html (bloc SONS).

Module partagé par tools/build_sfx.py et par les extensions (Pack SFX) : c'est ce qui permet au
bouton Export de l'app HyperFrames (ou à `npm run render`) de sortir la vidéo complète, et à
l'app d'afficher chaque son comme un clip de la timeline.

    import sons
    sons.poser(reel, evenements, musique=..., musique_db=-26.5, duree=..., ecraser=False)

Un évènement est un dict : {"src": Path, "start": s, "vol": dB, "trim": (t0, t1) | None,
"fondu_entree": s, "fondu_sortie": s, "af": filtre ffmpeg | None}. Ce que HyperFrames ne sait pas
faire lui-même (variante « af » : accélérer, inverser…, musique trop courte à boucler) est
préparé en fichier par ffmpeg dans assets/sons/, puis posé tel quel. Un son déjà rangé dans
assets/ du Reel (trouvé dans l'app par find_sound_effect ou find_music) y reste : pas de copie.

Réglages repris de l'ancien mixage ffmpeg, mesurés à 0,3 dB près sur un vrai Reel :
volume en dB -> data-volume ; fondus en enveloppe data-automation (une enveloppe REMPLACE
data-volume, elle porte donc le niveau réel) ; voix, sons et musique sur le bus « mixage »
plafonné à -0,26 dB (= alimiter limit=0.97).

Protection : le bloc porte une empreinte. Retouché à la main ou dans l'app, il n'est plus réécrit
sans `ecraser=True`.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

LIMITE_DB = -0.26
FONDU_MUSIQUE = (0.4, 1.2)
BLOC_RE = re.compile(r"( *)<!-- SONS:DEBUT[^>]*empreinte (\w+) -->\n(.*?)\n *<!-- SONS:FIN -->", re.S)
PLACE = "<!-- SONS -->"   # emplacement posé par tools/build_master.py


class Erreur(Exception):
    pass


def empreinte(contenu: str) -> str:
    return hashlib.sha1(contenu.encode("utf-8")).hexdigest()[:10]


def duree(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], capture_output=True, encoding="utf-8", errors="replace").stdout.strip()
    try:
        return float(out)
    except ValueError:
        raise Erreur(f"durée illisible : {path}")


def lin(db: float) -> float:
    return round(10 ** (db / 20), 4)


def _attr_json(obj) -> str:
    return html.escape(json.dumps(obj, separators=(",", ":")), quote=True)


def _enveloppe(points) -> str:
    return _attr_json({"version": 1, "lanes": [{"target": "volume", "points": points}]})


def _nom(src: Path, sfx_dir: Path | None, prefixe: str = "") -> str:
    try:
        base = "-".join(src.relative_to(sfx_dir).parts) if sfx_dir else src.name
    except ValueError:
        base = src.name
    return f"{prefixe}{base}"


def _dans_le_reel(reel: Path, src: Path) -> str | None:
    """Le chemin d'un son déjà rangé dans assets/ du Reel (relatif au Reel), sinon None."""
    try:
        rel = src.resolve().relative_to((reel / "assets").resolve())
    except ValueError:
        return None
    return f"assets/{rel.as_posix()}"


def _src(chemin: str) -> str:
    return html.escape(chemin, quote=True)


def _copie(src: Path, dest: Path) -> None:
    if not dest.exists() or dest.stat().st_size != src.stat().st_size:
        shutil.copy2(src, dest)


def _ffmpeg(args) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", *args], capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise Erreur(f"ffmpeg a échoué : {r.stderr[-600:]}")


def _preparer_variante(e, dossier: Path, sfx_dir: Path | None) -> tuple[str, float]:
    """Une variante « af » : le segment rogné, transformé par ffmpeg, en WAV. -> (nom, durée)."""
    t0, t1 = e.get("trim") or (0.0, None)
    signature = hashlib.sha1(f"{e['src']}|{t0}|{t1}|{e['af']}".encode()).hexdigest()[:8]
    nom = f"{Path(_nom(e['src'], sfx_dir)).stem}-variante-{signature}.wav"
    dest = dossier / nom
    if not dest.exists():
        coupe = ["-ss", f"{t0:.3f}"] + (["-to", f"{t1:.3f}"] if t1 else [])
        _ffmpeg([*coupe, "-i", str(e["src"]), "-af", str(e["af"]), "-ar", "48000", "-ac", "2", str(dest)])
    return nom, duree(dest)


def _preparer_musique(musique: Path, dossier: Path, total: float, reel: Path) -> str:
    """La musique (chemin pour src), bouclée en WAV si elle est plus courte que la vidéo ; sinon
    copiée telle quelle, ou laissée en place si elle est déjà dans assets/ du Reel."""
    if duree(musique) >= total:
        sur_place = _dans_le_reel(reel, musique)
        if sur_place:
            return sur_place
        nom = f"musique-{musique.name}"
        _copie(musique, dossier / nom)
        return f"assets/sons/{nom}"
    nom = f"musique-{musique.stem}-boucle-{int(total * 1000)}.wav"
    if not (dossier / nom).exists():
        _ffmpeg(["-stream_loop", "-1", "-i", str(musique), "-t", f"{total:.3f}", "-ar", "48000", str(dossier / nom)])
    return f"assets/sons/{nom}"


def lignes(reel: Path, evenements, musique: Path | None, musique_db: float, total: float,
           sfx_dir: Path | None = None) -> list[str]:
    """Les éléments du bloc SONS (copie ou prépare chaque son dans assets/sons/ du Reel)."""
    dossier = reel / "assets" / "sons"
    dossier.mkdir(parents=True, exist_ok=True)
    out = [f'<hf-audio-group id="mixage" data-label="Mixage" data-fx-chain="'
           f'{_attr_json({"version": 1, "nodes": [{"type": "limiter", "id": "n1", "label": "Plafond", "params": {"limit": LIMITE_DB}}]})}'
           f'"></hf-audio-group>']
    if musique:
        v = lin(musique_db)
        entree, sortie = min(FONDU_MUSIQUE[0], total / 4), min(FONDU_MUSIQUE[1], total / 3)
        pts = [{"t": 0, "v": 0}, {"t": round(entree, 3), "v": v},
               {"t": round(total - sortie, 3), "v": v}, {"t": round(total, 3), "v": 0}]
        out.append(f'<audio id="musique" src="{_src(_preparer_musique(musique, dossier, total, reel))}" '
                   f'data-start="0" data-duration="{round(total, 3)}" data-media-start="0" data-volume="{v}" '
                   f'data-track-index="19" data-audio-group="mixage" data-automation="{_enveloppe(pts)}"></audio>')
    fins = []   # une piste par son qui se chevauche : deux clips sur la même piste, l'un disparaît
    for n, e in enumerate(sorted(evenements, key=lambda x: x["start"]), start=1):
        src = Path(e["src"])
        if not src.exists():
            raise Erreur(f"son introuvable : {src}")
        if e.get("af"):
            nom, garde = _preparer_variante(e, dossier, sfx_dir)
            chemin, debut = f"assets/sons/{nom}", 0.0
        else:
            chemin = _dans_le_reel(reel, src)
            if not chemin:
                nom = _nom(src, sfx_dir)
                _copie(src, dossier / nom)
                chemin = f"assets/sons/{nom}"
            complet = duree(src)
            t0, t1 = e.get("trim") or (0.0, complet)
            debut, garde = t0, min(t1, complet) - t0
        garde = round(garde, 3)
        start = round(max(float(e["start"]), 0.0), 3)
        piste = next((i for i, fin in enumerate(fins) if fin <= start), None)
        if piste is None:
            piste = len(fins)
            fins.append(start + garde)
        else:
            fins[piste] = start + garde
        v = lin(float(e["vol"]))
        ligne = (f'<audio id="sfx-{n:02d}" src="{_src(chemin)}" data-start="{start:.3f}" '
                 f'data-duration="{garde:.3f}" data-media-start="{debut:.3f}" data-volume="{v}" '
                 f'data-track-index="{20 + piste}" data-audio-group="mixage"')
        fe, fs = float(e.get("fondu_entree") or 0), float(e.get("fondu_sortie") or 0)
        if fe or fs:
            pts = [{"t": 0, "v": 0 if fe else v}]
            if fe:
                pts.append({"t": round(min(fe, garde), 3), "v": v})
            if fs:
                pts.append({"t": round(max(garde - fs, 0), 3), "v": v})
                pts.append({"t": garde, "v": 0})
            ligne += f' data-automation="{_enveloppe(pts)}"'
        out.append(ligne + "></audio>")
    return out


def poser(reel: Path, evenements, musique: Path | None = None, musique_db: float = -26.5,
          total: float | None = None, sfx_dir: Path | None = None, ecraser: bool = False) -> None:
    """Écrit le bloc SONS dans reel/index.html. Lève Erreur si le bloc a été retouché (sauf ecraser)."""
    index = reel / "index.html"
    if not index.exists():
        raise Erreur("index.html manquant : génère d'abord le master (python3 tools/build_master.py --write).")
    page = index.read_text(encoding="utf-8")
    existant = BLOC_RE.search(page)
    if existant:
        indent = existant.group(1)
        if empreinte(existant.group(3)) != existant.group(2) and not ecraser:
            raise Erreur("les sons ont ete retouches a la main ou dans l'app depuis leur pose : modifie-les "
                         "directement dans index.html, ou relance avec --ecraser pour repartir de la liste.")
    elif PLACE in page:
        indent = re.search(rf"( *){re.escape(PLACE)}", page).group(1)
    else:
        raise Erreur("emplacement des sons introuvable dans index.html : régénère le master "
                     "(python3 tools/build_master.py --write).")
    if total is None:
        m = re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"', page)
        if not m:
            raise Erreur("durée du montage introuvable dans index.html.")
        total = float(m.group(1))
    contenu = "\n".join(indent + l for l in lignes(reel, evenements, musique, musique_db, total, sfx_dir))
    bloc = (f"{indent}<!-- SONS:DEBUT genere par tools/sons.py, empreinte {empreinte(contenu)} -->\n"
            f"{contenu}\n{indent}<!-- SONS:FIN -->")
    page = (page[:existant.start()] + bloc + page[existant.end():]) if existant \
        else page.replace(f"{indent}{PLACE}", bloc, 1)
    index.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    sys.exit("Module partagé : utilise tools/build_sfx.py (ou l'outil de ton extension).")
