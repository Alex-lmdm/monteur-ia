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
data-volume, elle porte donc le niveau réel) ; voix, sons et musique sur le bus « mixage » (gain,
puis plafond à -1,5 dB).

Niveau : le rendu de l'app HyperFrames ne garde un gain que dans la marge de crête du mixage. Dès
qu'une crête vraie dépasse -1 dBTP après l'encodage, il baisse tout le son jusqu'au niveau que
cette marge permet (mesuré avec le moteur de l'app, 0.8.155 : +7 ou +8,1 dB posés sur le bus
donnent le même export que +4 dB, la marge du mixage ; la CLI 0.8.136, elle, applique le gain sous
son limiteur). À la pose, le mixage entier (voix comprise) est donc mesuré par ffmpeg, et le bus
reçoit le gain qui le rapproche de sa cible sans que sa crête vraie dépasse -1,5 dBTP : gain =
min(écart vers la cible, marge de crête), jamais négatif. Le rendu ne baisse alors plus rien, le
plafond du bus ne travaille presque pas, et une vidéo exportée puis postée telle quelle sort aussi
fort que le rendu de l'app le permet. Le tools/finaliser.py du projet pose ensuite le niveau final :
-16 LUFS pour un Reel (celui des Reels du fil), -14 LUFS pour une vidéo YouTube (meta.json : lieu
« youtube »). Les volumes de la voix (vers -24 LUFS, sortie d'Adobe Podcast), des sons et de la
musique ne changent pas entre eux : tout monte ensemble. Sans voix audible (vidéo d'exemple, Reel
muet), aucun gain.

Protection : le bloc porte une empreinte. Retouché à la main ou dans l'app, il n'est plus réécrit
sans `ecraser=True`.
"""
from __future__ import annotations

import functools
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

LIMITE_DB = -1.5        # plafond des crêtes : marge pour l'encodage AAC (crête vraie <= -1 dBTP)
CRETE_MAX_DBTP = -1.0   # crête vraie à ne pas dépasser dans la vidéo livrée, mesurée sur le fichier encodé
CIBLE_LUFS = -16.0      # niveau final d'un Reel, posé après l'export (tools/finaliser.py)
CIBLE_YOUTUBE_LUFS = -14.0   # celui d'une vidéo YouTube (son propre tools/finaliser.py)
GAIN_MAX_DB = 12.0      # borne des gains (HyperFrames : -60 à +12 dB)
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


def lire_lufs(sortie_ffmpeg: str) -> float | None:
    """La loudness intégrée du résumé d'ebur128 (dernière valeur « I: … LUFS »), sinon None."""
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", sortie_ffmpeg)
    return float(m[-1]) if m else None


def cible_lufs(projet: Path) -> float:
    """Le niveau final du projet, posé après l'export par son tools/finaliser.py : -16 LUFS pour un
    Reel, -14 LUFS pour une vidéo YouTube."""
    try:
        lieu = (json.loads((projet / "meta.json").read_text(encoding="utf-8")).get("monteurIa") or {}).get("lieu")
    except (OSError, ValueError):
        lieu = None
    return CIBLE_YOUTUBE_LUFS if lieu == "youtube" else CIBLE_LUFS


@functools.lru_cache(maxsize=None)
def ffmpeg_a_latence() -> bool:
    """L'option latency d'alimiter (FFmpeg 5 et après) recale le son sur l'image après l'anticipation."""
    aide = subprocess.run(["ffmpeg", "-hide_banner", "-h", "filter=alimiter"], capture_output=True,
                          encoding="utf-8", errors="replace").stdout
    return "latency" in aide


def plafond_ffmpeg(limite_db: float = LIMITE_DB, gain_db: float = 0.0) -> str:
    """Filtre ffmpeg : un gain constant, puis un plafond posé sur la crête VRAIE. alimiter ne voit que
    les échantillons ; entre deux, l'onde reconstruite dépasse (jusqu'à +0,6 dB mesuré sur un mixage
    dense poussé de +8 dB). Limiter à 192 kHz (le suréchantillonnage x4 de la mesure de crête vraie)
    puis revenir à 48 kHz garde la crête vraie au plafond, avant l'encodage."""
    gain = f"volume={gain_db:.2f}dB," if gain_db else ""
    return (f"aresample=192000,{gain}alimiter=limit={lin(limite_db)}:attack=5:release=50:level=false"
            + (":latency=true" if ffmpeg_a_latence() else "") + ",aresample=48000")


def niveau_sonore(fichier: Path, filtre: str = "") -> tuple[float | None, float]:
    """(loudness intégrée en LUFS, crête vraie en dBTP) de la piste son d'un fichier, après `filtre`
    s'il est donné ; (None, -99) sans piste son lisible. La crête vaut -99 pour un son muet."""
    err = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(fichier), "-map", "0:a:0", "-af",
                          (f"{filtre}," if filtre else "") + "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, encoding="utf-8", errors="replace").stderr
    pics = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", err)
    return lire_lufs(err), float(pics[-1]) if pics and pics[-1] != "-inf" else -99.0


def gain_final(niveau: float | None) -> float:
    """Le gain (dB) qui amène un mixage de ce niveau à CIBLE_LUFS ; 0 s'il est illisible ou muet.
    Gardé pour les tools/build_sfx.py des Reels créés avant le 15/10/2026 : leur export ffmpeg
    (--ffmpeg) pose encore ce gain lui-même."""
    if niveau is None or niveau < -60:
        return 0.0
    return round(max(-GAIN_MAX_DB, min(GAIN_MAX_DB, CIBLE_LUFS - niveau)), 1)


def gain_pose(niveau: float | None, crete: float | None, cible: float) -> float:
    """Le gain (dB) posé sur le bus : vers la cible, sans que la crête vraie du mixage dépasse
    LIMITE_DB (au-delà, le rendu baisserait tout le son) ; jamais négatif ; 0 sans mesure."""
    if niveau is None or crete is None or niveau < -60:
        return 0.0
    # Arrondi vers le bas : un dixième de trop suffirait à repasser la crête au-dessus du plafond.
    return max(0.0, math.floor(min(GAIN_MAX_DB, cible - niveau, LIMITE_DB - crete) * 10) / 10)


def _canaux(src: Path) -> int:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels",
                          "-of", "csv=p=0", str(src)], capture_output=True, encoding="utf-8", errors="replace").stdout
    try:
        return int(out.strip().split(",")[0])
    except ValueError:
        return 2


def mesurer(pistes, total: float) -> tuple[float | None, float | None]:
    """(loudness intégrée en LUFS, crête vraie en dBTP) des pistes sommées comme sur le bus, avant
    gain ; (None, None) si ffmpeg échoue. Une piste : {"src": Path, "start": s, "duree": s | None,
    "media_start": s, "volume": linéaire, "fondu_entree": s, "fondu_sortie": s}. Les enveloppes sont
    approchées par des fondus linéaires. Une source mono est jouée à plein niveau sur les deux
    canaux, comme le fait le rendu HyperFrames (vérifié avec 0.8.136 ; ffmpeg, lui, la répartirait
    à -3 dB)."""
    if not pistes:
        return None, None
    entrees, filtres = [], []
    for i, p in enumerate(pistes):
        entrees += ["-i", str(p["src"])]
        stereo = "pan=stereo|c0=c0|c1=c0" if _canaux(p["src"]) == 1 else "aformat=channel_layouts=stereo"
        f = f"[{i}:a]atrim=start={p['media_start']:.3f}"
        if p.get("duree"):
            f += f":duration={p['duree']:.3f}"
        f += f",asetpts=PTS-STARTPTS,aformat=sample_rates=48000,{stereo},volume={p['volume']}"
        if p.get("fondu_entree"):
            f += f",afade=t=in:st=0:d={p['fondu_entree']:.3f}"
        if p.get("fondu_sortie") and p.get("duree"):
            f += f",afade=t=out:st={max(p['duree'] - p['fondu_sortie'], 0):.3f}:d={p['fondu_sortie']:.3f}"
        filtres.append(f + f",adelay={int(round(p['start'] * 1000))}:all=1[p{i}]")
    filtres.append("".join(f"[p{i}]" for i in range(len(pistes)))
                   + f"amix=inputs={len(pistes)}:normalize=0:dropout_transition=0,atrim=0:{total:.3f},ebur128=peak=true[m]")
    r = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", *entrees, "-filter_complex", ";".join(filtres),
                        "-map", "[m]", "-f", "null", "-"], capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        return None, None
    pics = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", r.stderr)
    return lire_lufs(r.stderr), float(pics[-1]) if pics and pics[-1] != "-inf" else -99.0


def pistes_du_master(reel: Path, page: str) -> list[dict]:
    """Les pistes du master qui passent par le bus « mixage » hors du bloc SONS : la voix."""
    pistes = []
    for balise in re.findall(r"<audio\b[^>]*>", BLOC_RE.sub("", page)):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', balise))
        src = reel / html.unescape(a["src"]) if a.get("src") else None
        if a.get("data-audio-group") != "mixage" or not src or not src.is_file():
            continue
        try:
            pistes.append({"src": src, "start": float(a.get("data-start") or 0),
                           "duree": float(a["data-duration"]) if a.get("data-duration") else None,
                           "media_start": float(a.get("data-media-start") or 0),
                           "volume": float(a.get("data-volume") or 1)})
        except ValueError:
            continue
    return pistes


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
           sfx_dir: Path | None = None, voix=(), rapport: dict | None = None) -> list[str]:
    """Les éléments du bloc SONS (copie ou prépare chaque son dans assets/sons/ du Reel).
    voix : les pistes du master hors bloc (pistes_du_master), mesurées avec les sons pour régler le
    gain du bus ; sans voix audible, pas de gain. rapport : rempli avec la mesure et le gain posé."""
    dossier = reel / "assets" / "sons"
    dossier.mkdir(parents=True, exist_ok=True)
    out, pistes = [], list(voix)
    if musique:
        v = lin(musique_db)
        entree, sortie = min(FONDU_MUSIQUE[0], total / 4), min(FONDU_MUSIQUE[1], total / 3)
        pts = [{"t": 0, "v": 0}, {"t": round(entree, 3), "v": v},
               {"t": round(total - sortie, 3), "v": v}, {"t": round(total, 3), "v": 0}]
        chemin = _preparer_musique(musique, dossier, total, reel)
        out.append(f'<audio id="musique" src="{_src(chemin)}" '
                   f'data-start="0" data-duration="{round(total, 3)}" data-media-start="0" data-volume="{v}" '
                   f'data-track-index="19" data-audio-group="mixage" data-automation="{_enveloppe(pts)}"></audio>')
        pistes.append({"src": reel / chemin, "start": 0.0, "duree": total, "media_start": 0.0, "volume": v,
                       "fondu_entree": entree, "fondu_sortie": sortie})
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
        pistes.append({"src": reel / chemin, "start": start, "duree": garde, "media_start": debut, "volume": v,
                       "fondu_entree": fe, "fondu_sortie": fs})
    # Gain seulement si une voix s'entend : sans elle (Reel muet, vidéo d'exemple), la musique seule
    # n'est pas poussée.
    voix_audible = bool(voix) and ((mesurer(list(voix), total)[0] or -99.0) > -50)
    niveau, crete = mesurer(pistes, total) if voix_audible else (None, None)
    cible = cible_lufs(reel)
    gain = gain_pose(niveau, crete, cible)
    if rapport is not None:
        rapport.update(niveau=niveau, crete=crete, gain=gain, cible=cible)
    chaine = {"version": 1, "nodes": [
        {"type": "gain", "id": "n0", "label": "Niveau", "params": {"gain": gain}},
        {"type": "limiter", "id": "n1", "label": "Plafond", "params": {"limit": LIMITE_DB}}]}
    return [f'<hf-audio-group id="mixage" data-label="Mixage" data-fx-chain="{_attr_json(chaine)}"></hf-audio-group>',
            *out]


def poser(reel: Path, evenements, musique: Path | None = None, musique_db: float = -26.5,
          total: float | None = None, sfx_dir: Path | None = None, ecraser: bool = False) -> dict:
    """Écrit le bloc SONS dans reel/index.html. Lève Erreur si le bloc a été retouché (sauf ecraser).
    Rend le rapport lu par resume_niveau : mesure du mixage, gain posé sur le bus, cible finale."""
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
    rapport = {"apres_export": True}
    contenu = "\n".join(indent + l for l in lignes(reel, evenements, musique, musique_db, total, sfx_dir,
                                                    voix=pistes_du_master(reel, page), rapport=rapport))
    bloc = (f"{indent}<!-- SONS:DEBUT genere par tools/sons.py, empreinte {empreinte(contenu)} -->\n"
            f"{contenu}\n{indent}<!-- SONS:FIN -->")
    page = (page[:existant.start()] + bloc + page[existant.end():]) if existant \
        else page.replace(f"{indent}{PLACE}", bloc, 1)
    index.write_text(page, encoding="utf-8")
    return rapport


def resume_niveau(rapport: dict) -> str:
    """Une ligne pour le récapitulatif de la pose, ou de l'export ffmpeg d'un Reel créé avant le
    15/10/2026 (qui pose encore un gain)."""
    if rapport.get("apres_export"):
        cible = rapport.get("cible") or CIBLE_LUFS
        fin = f"Après l'export, python3 tools/finaliser.py amène la vidéo à {cible:.0f} LUFS (et la contrôle)."
        if rapport.get("niveau") is None:
            return f"Niveau : pas de voix audible, aucun gain dans le montage. {fin}"
        return (f"Niveau : mixage mesuré à {rapport['niveau']:.1f} LUFS, crête {rapport['crete']:.1f} dBTP ; gain "
                f"{rapport['gain']:+.1f} dB sur le bus, borné par la marge de crête (au-delà, le rendu baisserait "
                f"tout). {fin}")
    if rapport.get("niveau") is None:
        return "Niveau final : non mesuré (pas de voix audible, ou mesure impossible), aucun gain posé."
    return (f"Niveau final : mixage mesuré à {rapport['niveau']:.1f} LUFS, gain {rapport['gain']:+.1f} dB "
            f"(visé {rapport['cible']:.0f} LUFS, crêtes plafonnées à {LIMITE_DB} dB).")


if __name__ == "__main__":
    sys.exit("Module partagé : utilise tools/build_sfx.py (ou l'outil de ton extension).")
