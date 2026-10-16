#!/usr/bin/env python3
"""REEL CLONEUR : prépare l'analyse d'un Reel qui a marché (Instagram, TikTok, YouTube Short ou fichier).

L'outil fait toute la partie mécanique ; l'IA fait ensuite la lecture et l'écriture (skill
`reel-cloneur`). Il range tout dans clones/<date>-<slug>/ du dossier Monteur IA :

    media.mp4        la vidéo (720p max)
    audio.wav        l'audio en 16 kHz mono (pour Whisper)
    transcript.json  la transcription horodatée (langue détectée : le Reel peut être en anglais)
    shots.json       les coupes, la durée des plans, le rythme, la liste des images extraites
    frames/          les images (une par coupe, une par seconde, deux par seconde sur les 5 premières s)
    planches/        planches-contact de 6 images (au-delà des 5 premières s), heure écrite sur chaque image
    meta.json        plateforme, auteur, date, légende, likes, commentaires, vues si connues
    style.json       avec --style : rythme dans le temps, couleurs qui reviennent, et rafales/ (images
                     rapprochées : comment les sous-titres apparaissent, à quoi ressemblent les transitions)

Usage :
    python3 tools/cloner_reel.py "<lien ou fichier vidéo>" [--style] [--largeur 768] [--langue en] [--refaire]
    python3 tools/cloner_reel.py installer     # crée .reel-cloneur-venv/ avec yt-dlp (une fois)
    python3 tools/cloner_reel.py verifier      # contrôle des outils (smoke test)
    python3 tools/cloner_reel.py comparer clones/<dossier>[/brouillon.md]   # le script reprend-il des phrases ?
    python3 tools/cloner_reel.py couleurs clones/<dossier>/frames/<image>.jpg [--zone bas]   # couleurs exactes

Règles : jamais de cookies ni de connexion au compte du client ; si un lien ne se télécharge pas,
l'outil le dit simplement et propose de glisser le fichier vidéo à la place. Relancer l'outil sur
le même lien reprend le même dossier sans refaire ce qui est déjà fait (--refaire pour tout refaire).

Python 3.9+ standard (macOS fournit 3.9). yt-dlp, lui, vit dans .reel-cloneur-venv/ avec un Python
3.10 ou plus : les versions récentes, les seules qui savent encore lire Instagram, l'exigent.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.parse

# Windows : une sortie lue par l'agent (redirigée) est en cp1252, et un « ✅ » y fait planter l'outil.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WIN = os.name == "nt"
PY = "python" if WIN else "python3"  # la commande à redonner au client dans les messages
OUTILS = pathlib.Path(__file__).resolve().parent


def maison_de(depart: pathlib.Path):
    """Le dossier Monteur IA qui contient `depart` : celui qui porte templates/AGENT.md.tpl."""
    for d in (depart, *depart.parents):
        if (d / "templates" / "AGENT.md.tpl").is_file():
            return d
    return None


MAISON = maison_de(OUTILS) or OUTILS.parent
CLONES = MAISON / "clones"
VENV = MAISON / ".reel-cloneur-venv"
YTDLP_PAQUET = "yt-dlp[default,curl-cffi]"
YTDLP_VERSION_MIN = "2026.07.01"     # en dessous, Instagram ne se télécharge plus sans connexion
MAJ_STAMP = VENV / ".derniere-mise-a-jour"
MAJ_INTERVALLE = 12 * 3600           # yt-dlp vérifié au plus toutes les 12 h (et toujours après un échec)

SCENE_SEUIL = 0.3
PLAFOND_IMAGES = 60
HOOK_S = 5.0                         # les 5 premières secondes visibles : lues image par image
PLANCHE_COLONNES, PLANCHE_LIGNES = 3, 2
TUILE_LARGEUR = 320                  # 3 × 320 px : planche d'environ 1 000 × 1 150 px, texte encore lisible
ECART_MIN = 0.35                     # deux images plus proches que ça : on n'en garde qu'une
FICHIER_VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".3gp")
# Une vidéo HD est codée en bt709 ; sans le préciser, ffmpeg la lit en bt601 et décale les couleurs
# des images extraites (le jaune #FFEE00 sortait #FCFD09). « auto » suit ce que déclare la vidéo.
COULEURS_JUSTES = "in_color_matrix=auto:out_color_matrix=bt601"


# ------------------------------------------------------------------ petits utilitaires
def dire(msg: str = "") -> None:
    print(msg, flush=True)


def arret(msg: str, code: int = 1) -> None:
    print(f"\n❌ {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def config() -> dict:
    for nom in ("brand.config.json", "brand.config.example.json"):
        p = MAISON / nom
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
    return {}


def binaire(cle: str, defaut: str):
    """Un exécutable : chemin de brand.config.json (env.<cle>) s'il existe, sinon celui du PATH."""
    v = (config().get("env") or {}).get(cle)
    if v and pathlib.Path(v).exists():
        return v
    if v and shutil.which(v):
        return shutil.which(v)
    trouve = shutil.which(defaut)
    if trouve:
        return trouve
    # Homebrew n'est pas toujours dans le PATH d'un agent lancé depuis une app.
    for prefixe in ("/opt/homebrew/bin", "/usr/local/bin"):
        p = pathlib.Path(prefixe) / defaut
        if p.exists():
            return str(p)
    return None


def ffprobe_de(ffmpeg: str) -> str:
    p = pathlib.Path(ffmpeg)
    cand = p.with_name(p.name.replace("ffmpeg", "ffprobe"))
    return str(cand) if cand.exists() else (shutil.which("ffprobe") or "ffprobe")


def lancer(cmd, timeout=None, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, **kw)


def slugifier(texte: str, longueur: int = 40) -> str:
    t = unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:longueur].strip("-") or "video"


def ecrire_json(chemin: pathlib.Path, donnees) -> None:
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lire_json(chemin: pathlib.Path):
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def mmss(t: float) -> str:
    t = max(0.0, float(t))
    return f"{int(t // 60)}:{t % 60:04.1f}"


# ------------------------------------------------------------------ yt-dlp (venv dédié)
def venv_bin(nom: str) -> pathlib.Path:
    return VENV / ("Scripts" if WIN else "bin") / (nom + (".exe" if WIN else ""))


def version_python(exe: str):
    try:
        r = lancer([exe, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"], timeout=20)
        if r.returncode == 0:
            maj, mineur = r.stdout.strip().split(".")
            return int(maj), int(mineur)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return None


def python_recent():
    """Un Python 3.10+ pour le venv. macOS fournit 3.9 : on cherche celui de Homebrew ou d'python.org."""
    candidats = [sys.executable]
    noms = ["python3.13", "python3.12", "python3.11", "python3.14", "python3.10", "python3", "python"]
    for nom in noms:
        p = shutil.which(nom)
        if p:
            candidats.append(p)
    for prefixe in ("/opt/homebrew/bin", "/usr/local/bin", "/Library/Frameworks/Python.framework/Versions/Current/bin"):
        for nom in noms:
            p = pathlib.Path(prefixe) / nom
            if p.exists():
                candidats.append(str(p))
    if WIN and shutil.which("py"):
        for v in ("3.13", "3.12", "3.11", "3.10"):
            r = lancer(["py", f"-{v}", "-c", "import sys; print(sys.executable)"], timeout=20)
            if r.returncode == 0 and r.stdout.strip():
                candidats.append(r.stdout.strip())
    vus = set()
    for c in candidats:
        if c in vus:
            continue
        vus.add(c)
        v = version_python(c)
        if v and v >= (3, 10):
            return c
    return None


def version_ytdlp(exe) -> str:
    try:
        r = lancer([exe, "--version"], timeout=60)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def assez_recent(version: str) -> bool:
    def cle(v):
        return tuple(int(x) for x in re.findall(r"\d+", v)[:3])
    return bool(version) and cle(version) >= cle(YTDLP_VERSION_MIN)


def ytdlp_exe():
    """yt-dlp du venv dédié ; à défaut, un yt-dlp du système assez récent."""
    p = venv_bin("yt-dlp")
    if p.exists():
        return str(p)
    systeme = binaire("ytDlp", "yt-dlp")
    if systeme and assez_recent(version_ytdlp(systeme)):
        return systeme
    return None


def mettre_a_jour_ytdlp(forcer: bool = False) -> None:
    """Instagram et TikTok changent souvent : yt-dlp se tient à jour tout seul (sans bloquer si hors ligne)."""
    py = venv_bin("python")
    if not py.exists():
        return
    if not forcer and MAJ_STAMP.exists() and time.time() - MAJ_STAMP.stat().st_mtime < MAJ_INTERVALLE:
        return
    try:
        # Hors ligne, pip réessaie longtemps par défaut : on coupe court (10 s, un seul nouvel essai).
        r = lancer([py, "-m", "pip", "install", "--upgrade", "--quiet", "--disable-pip-version-check",
                    "--timeout", "10", "--retries", "1", YTDLP_PAQUET], timeout=120)
        if r.returncode == 0:
            MAJ_STAMP.write_text(datetime.datetime.now().isoformat())
    except (OSError, subprocess.SubprocessError):
        pass


def installer() -> None:
    dire("Reel Cloneur : installation du téléchargeur de vidéos (yt-dlp)…")
    py = venv_bin("python")
    if py.exists() and not (version_python(str(py)) or (0, 0)) >= (3, 10):
        dire("• ancien environnement (Python trop ancien) : je le recrée")
        shutil.rmtree(VENV, ignore_errors=True)
    if not py.exists():
        base = python_recent()
        if not base:
            conseil = ("brew install python@3.12" if sys.platform == "darwin"
                       else "winget install -e --id Python.Python.3.12" if WIN
                       else "sudo apt install python3.12-venv")
            arret("Il faut un Python 3.10 ou plus récent pour le téléchargeur (celui de ton ordinateur est "
                  f"plus ancien). Installe-le avec : {conseil}\npuis relance : {PY} tools/cloner_reel.py "
                  "installer", 3)
        dire(f"• Python utilisé : {base}")
        r = lancer([base, "-m", "venv", str(VENV)], timeout=300)
        if r.returncode != 0:
            arret("Impossible de créer l'environnement .reel-cloneur-venv/ :\n" + (r.stderr or r.stdout)[-800:]
                  + ("\nSur Linux : sudo apt install python3-venv" if sys.platform.startswith("linux") else ""))
    r = lancer([py, "-m", "pip", "install", "--upgrade", "--quiet", "--disable-pip-version-check",
                YTDLP_PAQUET], timeout=600)
    if r.returncode != 0:
        arret("L'installation de yt-dlp a échoué (connexion internet ?) :\n" + (r.stderr or r.stdout)[-800:])
    MAJ_STAMP.write_text(datetime.datetime.now().isoformat())
    v = version_ytdlp(venv_bin("yt-dlp"))
    curl = lancer([py, "-c", "import curl_cffi"], timeout=60).returncode == 0
    dire(f"✅ yt-dlp {v} installé dans .reel-cloneur-venv/ (curl_cffi : {'oui' if curl else 'NON'})")
    if not assez_recent(v):
        arret(f"yt-dlp {v} est trop ancien (il faut {YTDLP_VERSION_MIN} ou plus).")


# ------------------------------------------------------------------ vérification (smoke test)
def verifier() -> int:
    lignes = []

    def ligne(ok, quoi, detail):
        lignes.append((ok, quoi, detail))

    ffmpeg = binaire("ffmpegPath", "ffmpeg")
    ligne(bool(ffmpeg), "ffmpeg", ffmpeg or "introuvable")
    if ffmpeg:
        fp = ffprobe_de(ffmpeg)
        ligne(bool(shutil.which(fp) or pathlib.Path(fp).exists()), "ffprobe", fp)
    w = binaire("whisperCli", "whisper-cli")
    ligne(bool(w), "whisper-cli", w or "introuvable")
    m = modele_whisper()
    ligne(bool(m), "modèle Whisper", m or "introuvable (env.whisperModel de brand.config.json)")
    y = ytdlp_exe()
    v = version_ytdlp(y) if y else ""
    ligne(bool(y) and assez_recent(v), "yt-dlp", f"{v} ({y})" if y else f"absent : {PY} tools/cloner_reel.py installer")
    if venv_bin("python").exists():
        curl = lancer([venv_bin("python"), "-c", "import curl_cffi"], timeout=60).returncode == 0
        ligne(curl, "curl_cffi", "ok" if curl else "absent : relance l'installation")
    node = binaire("nodePath", "node")
    ligne(bool(node), "node (YouTube)", node or "introuvable")
    ok_global = all(ok for ok, _, _ in lignes)
    if ok_global and ffmpeg and w and m:
        # Mini-chaîne réelle : 2 s de vidéo de test → audio → Whisper → détection de coupes.
        test = CLONES / "_test"
        test.mkdir(parents=True, exist_ok=True)
        try:
            r1 = lancer([ffmpeg, "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x568:rate=30:d=2",
                         "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-shortest", "-pix_fmt", "yuv420p",
                         test / "media.mp4"], timeout=120)
            r2 = lancer([ffmpeg, "-y", "-v", "error", "-i", test / "media.mp4", "-ac", "1", "-ar", "16000",
                         test / "audio.wav"], timeout=120)
            r3 = lancer([w, "-m", m, "-f", test / "audio.wav", "-l", "auto", "-np", "-oj", "-of",
                         test / "w"], timeout=300)
            ok = r1.returncode == 0 and r2.returncode == 0 and r3.returncode == 0 and (test / "w.json").exists()
            ligne(ok, "chaîne vidéo → audio → texte", "ok" if ok else (r1.stderr + r2.stderr + r3.stderr)[-300:])
        finally:
            shutil.rmtree(test, ignore_errors=True)
    dire("Reel Cloneur : vérification des outils")
    for ok, quoi, detail in lignes:
        dire(f"  {'✅' if ok else '❌'} {quoi} : {detail}")
    ok_global = all(ok for ok, _, _ in lignes)
    dire("ok" if ok_global else "\nAu moins un outil manque (voir ❌ ci-dessus).")
    return 0 if ok_global else 1


# ------------------------------------------------------------------ source : lien ou fichier
MOTIFS_ID = [
    ("instagram", re.compile(r"instagram\.com/(?:[\w.]+/)?(?:reel|reels|p|tv)/([\w-]+)")),
    ("tiktok", re.compile(r"tiktok\.com/.*?/(?:video|photo)/(\d+)")),
    ("youtube", re.compile(r"youtube\.com/shorts/([\w-]{11})")),
    ("youtube", re.compile(r"[?&]v=([\w-]{11})")),
    ("youtube", re.compile(r"youtu\.be/([\w-]{11})")),
]


def id_du_lien(url: str):
    for plateforme, motif in MOTIFS_ID:
        m = motif.search(url)
        if m:
            return plateforme, m.group(1)
    return None, None


def clone_existant(plateforme, ident, source):
    if not CLONES.exists():
        return None
    for meta_p in sorted(CLONES.glob("*/meta.json")):
        meta = lire_json(meta_p) or {}
        if ident and meta.get("plateforme") == plateforme and meta.get("id") == ident:
            return meta_p.parent
        if source and meta.get("source") == source:
            return meta_p.parent
    return None


def erreur_telechargement(texte: str) -> str:
    t = texte.lower()
    if "private" in t or "privé" in t:
        return "Cette vidéo est privée : elle ne se télécharge pas sans connexion au compte."
    if "login" in t or "cookies" in t or "sign in" in t or "rate-limit" in t or "rate limit" in t:
        return ("La plateforme refuse de donner cette vidéo sans connexion : vidéo privée ou supprimée, lien "
                "incomplet, ou trop de téléchargements en ce moment.")
    if "unsupported url" in t:
        return "Ce lien n'est pas reconnu comme une vidéo (vérifie que c'est bien le lien du Reel, du TikTok ou du Short)."
    if "not available" in t or "unavailable" in t or "404" in t or "removed" in t:
        return "Cette vidéo n'est pas disponible (supprimée, réservée à certains pays ou à certains comptes)."
    if "unable to download" in t or "timed out" in t or "connection" in t or "resolve" in t:
        return "La connexion internet a coupé pendant le téléchargement."
    return "Le téléchargement n'a pas marché."


def telecharger(url: str, ffmpeg: str):
    """Télécharge le lien dans clones/_telechargement/ ; renvoie (dossier temporaire, info yt-dlp)."""
    y = ytdlp_exe()
    if not y:
        arret(f"Le téléchargeur n'est pas installé. Lance d'abord : {PY} tools/cloner_reel.py installer")
    mettre_a_jour_ytdlp()
    tmp = CLONES / "_telechargement"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    cmd = [y, "--no-playlist", "--no-cookies", "--no-progress", "--retries", "3", "--socket-timeout", "30",
           "-S", "res:720,ext:mp4:m4a", "--merge-output-format", "mp4", "--remux-video", "mp4",
           "--ffmpeg-location", ffmpeg, "--write-info-json", "-o", str(tmp / "media.%(ext)s")]
    node = binaire("nodePath", "node")
    if node:
        cmd += ["--js-runtimes", f"node:{node}"]     # YouTube exige un moteur JavaScript ; Node est déjà là
    cmd.append(url)
    erreurs = ""
    for essai in (1, 2):
        try:
            r = lancer(cmd, timeout=600)
        except subprocess.TimeoutExpired:
            r = None
        video = tmp / "media.mp4"
        if r is not None and r.returncode == 0 and video.exists():
            info = lire_json(tmp / "media.info.json") or {}
            return tmp, info
        erreurs = (r.stderr + r.stdout) if r is not None else "timed out"
        if essai == 1:
            dire("• premier essai raté : je mets à jour le téléchargeur et je réessaie…")
            mettre_a_jour_ytdlp(forcer=True)
    shutil.rmtree(tmp, ignore_errors=True)
    # Le détail reste court : la fin du message de yt-dlp conseille des cookies, ce qu'on ne fait jamais.
    detail = next((l for l in reversed(erreurs.splitlines()) if "ERROR" in l), "")
    detail = re.split(r"\. (?=[A-Z])|; please", detail)[0][:220]
    arret(f"{erreur_telechargement(erreurs)}\n\n"
          "👉 Solution : enregistre la vidéo sur ton ordinateur ou ton téléphone (bouton « Enregistrer » de "
          "l'appli quand il existe, sinon un enregistrement d'écran pendant que le Reel passe), puis glisse le "
          "fichier vidéo dans la conversation et redis « clone ce Reel ».\n"
          f"(Détail technique : {detail or 'aucun'})", 2)


def nom_plateforme(info: dict, url: str) -> str:
    cle = (info.get("extractor_key") or info.get("extractor") or "").lower()
    for p in ("instagram", "tiktok", "youtube"):
        if p in cle or p in url:
            return p
    return cle or "web"


def meta_depuis_info(info: dict, url: str) -> dict:
    plateforme = nom_plateforme(info, url)
    date = info.get("upload_date")
    if not date and info.get("timestamp"):
        date = datetime.datetime.fromtimestamp(info["timestamp"], datetime.timezone.utc).strftime("%Y%m%d")
    # Le pseudo public (@…) : Instagram le met dans « channel », TikTok dans « uploader » (uploader_id y
    # est un numéro), YouTube dans « uploader_id » (« @pseudo »).
    compte = {"instagram": info.get("channel"), "tiktok": info.get("uploader")}.get(plateforme)
    compte = compte or info.get("uploader_id") or info.get("channel_id") or info.get("uploader")
    if plateforme == "youtube":
        compte = (info.get("uploader_id") or info.get("channel") or "").lstrip("@") or compte
    # La plateforme déclare parfois un son (« son original »…) ; qu'on l'entende ou non n'est pas
    # détectable ici : l'IA ne voit que les images.
    musique = "non détectable"
    if info.get("track") or info.get("artist"):
        musique = "déclarée par la plateforme : " + " · ".join(x for x in (info.get("track"), info.get("artist")) if x)
    return {
        "source": url,
        "plateforme": plateforme,
        "id": info.get("id"),
        "lien": info.get("webpage_url") or url,
        "auteur": info.get("uploader") or info.get("channel"),
        "compte": compte,
        "titre": None if (info.get("title") or "").startswith("Video by ") else info.get("title"),
        "date": f"{date[:4]}-{date[4:6]}-{date[6:8]}" if date else None,
        "legende": info.get("description"),
        "likes": info.get("like_count"),
        "commentaires": info.get("comment_count"),
        "vues": info.get("view_count"),
        "partages": info.get("repost_count"),
        "musique": musique,
        "hashtags": info.get("tags") or [],
    }


# ------------------------------------------------------------------ média
def sonde(ffmpeg: str, video: pathlib.Path) -> dict:
    r = lancer([ffprobe_de(ffmpeg), "-v", "error", "-show_entries",
                "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", video], timeout=60)
    d = json.loads(r.stdout or "{}") if r.returncode == 0 else {}
    flux = d.get("streams") or []
    v = next((s for s in flux if s.get("codec_type") == "video"), {})
    fps = None
    try:
        n, q = (v.get("r_frame_rate") or "0/1").split("/")
        fps = round(int(n) / int(q), 2) if int(q) else None
    except ValueError:
        pass
    return {"duree": round(float((d.get("format") or {}).get("duration") or 0), 2),
            "largeur": v.get("width"), "hauteur": v.get("height"), "fps": fps,
            "audio": any(s.get("codec_type") == "audio" for s in flux)}


def preparer_fichier(chemin: pathlib.Path, dossier: pathlib.Path, ffmpeg: str) -> None:
    cible = dossier / "media.mp4"
    if chemin.suffix.lower() == ".mp4":
        shutil.copy2(chemin, cible)
        return
    r = lancer([ffmpeg, "-y", "-v", "error", "-i", chemin, "-c", "copy", "-movflags", "+faststart", cible], timeout=600)
    if r.returncode != 0:
        r = lancer([ffmpeg, "-y", "-v", "error", "-i", chemin, "-vf", "scale='min(720,iw)':-2", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "23", "-c:a", "aac", cible], timeout=1800)
        if r.returncode != 0:
            arret(f"Je n'arrive pas à lire ce fichier vidéo ({chemin.name}). Essaie un autre format (.mp4 ou .mov).")


def extraire_audio(ffmpeg: str, dossier: pathlib.Path) -> None:
    r = lancer([ffmpeg, "-y", "-v", "error", "-i", dossier / "media.mp4", "-vn", "-ac", "1", "-ar", "16000",
                "-c:a", "pcm_s16le", dossier / "audio.wav"], timeout=600)
    if r.returncode != 0:
        arret("Extraction de l'audio impossible :\n" + r.stderr[-500:])


def modele_whisper():
    m = (config().get("env") or {}).get("whisperModel")
    if m and pathlib.Path(m).expanduser().exists():
        return str(pathlib.Path(m).expanduser())
    for d in (MAISON / "models", MAISON / "assets" / "models", pathlib.Path.home() / "whisper-models",
              pathlib.Path.home() / ".cache" / "whisper"):
        if d.exists():
            for nom in ("ggml-large-v3-turbo.bin", "ggml-medium.bin", "ggml-small.bin", "ggml-base.bin"):
                if (d / nom).exists():
                    return str(d / nom)
            autres = sorted(d.glob("ggml-*.bin"))
            if autres:
                return str(autres[0])
    return None


def langue_marque() -> str:
    c = config()
    return ((c.get("derush") or {}).get("whisperLanguage") or (c.get("brand") or {}).get("language") or "fr")


def secondes(horodatage: str) -> float:
    h, m, s = horodatage.replace(",", ".").split(":")
    return round(int(h) * 3600 + int(m) * 60 + float(s), 2)


def en_phrases(morceaux, duree: float):
    """Regroupe les morceaux Whisper (60 caractères) en phrases, d'après la ponctuation.
    Une phrase sans ponctuation est coupée à 12 s ; aucune borne ne dépasse la durée de la vidéo."""
    phrases, courante = [], None
    for m in morceaux:
        if courante is None:
            courante = {"debut": m["debut"], "fin": m["fin"], "qui": "", "texte": m["texte"]}
        else:
            courante["fin"] = m["fin"]
            courante["texte"] += " " + m["texte"]
        if re.search(r"[.!?…]['\"»”)]*$", courante["texte"]) or courante["fin"] - courante["debut"] >= 12:
            phrases.append(courante)
            courante = None
    if courante:
        phrases.append(courante)
    for ph in phrases:
        ph["fin"] = round(min(ph["fin"], duree), 2)
        ph["debut"] = round(min(ph["debut"], ph["fin"]), 2)
    return phrases


def transcrire(dossier: pathlib.Path, langue_forcee, duree: float):
    w = binaire("whisperCli", "whisper-cli")
    m = modele_whisper()
    if not w or not m:
        arret("Whisper (la transcription) est introuvable : vérifie env.whisperCli et env.whisperModel dans "
              "brand.config.json (c'est l'installation de Monteur IA qui les remplit).")
    audio = dossier / "audio.wav"
    langue, proba = langue_forcee, None
    if not langue:
        # Le Reel copié n'est pas forcément dans la langue du client : on détecte d'abord.
        r = lancer([w, "-m", m, "-f", audio, "-l", "auto", "-dl"], timeout=300)
        trouve = re.search(r"auto-detected language:\s*([a-z]{2,3})\s*\(p\s*=\s*([\d.]+)", r.stderr + r.stdout)
        if trouve and float(trouve.group(2)) >= 0.5:
            langue, proba = trouve.group(1), round(float(trouve.group(2)), 3)
        else:
            langue = langue_marque()
    sortie = dossier / "_whisper"
    # Phrases de 60 caractères au plus : assez fin pour horodater le script beat par beat.
    r = lancer([w, "-m", m, "-f", audio, "-l", langue, "-np", "-ml", "60", "-sow", "-oj", "-of", sortie],
               timeout=1800)
    brut = lire_json(sortie.with_suffix(".json"))
    sortie.with_suffix(".json").unlink(missing_ok=True)
    if r.returncode != 0 or brut is None:
        arret("La transcription a échoué :\n" + (r.stderr or "")[-500:])
    morceaux = []
    for s in brut.get("transcription") or []:
        texte = (s.get("text") or "").strip()
        if not texte or re.fullmatch(r"[\[(].*[\])]|♪+", texte):
            continue
        debut_m = secondes(s["timestamps"]["from"])
        if debut_m >= duree:
            continue
        morceaux.append({"debut": debut_m, "fin": min(secondes(s["timestamps"]["to"]), round(duree, 2)),
                         "texte": texte})
    phrases = en_phrases(morceaux, duree)
    transcript = {
        "langue": langue,
        "langueDetectee": proba is not None,
        "probabilite": proba,
        "modele": pathlib.Path(m).name,
        "phrases": phrases,
        "texte": " ".join(p["texte"] for p in phrases),
        "morceaux": morceaux,
        "_note": "Transcription automatique : peut contenir des fautes sur les noms propres. Le texte "
                 "à l'écran (frames/) fait foi quand il dit autre chose. « qui » est vide : à remplir par "
                 "l'IA (d'après les sous-titres, le cadre ou la voix) quand plusieurs personnes parlent.",
    }
    ecrire_json(dossier / "transcript.json", transcript)
    return transcript


# ------------------------------------------------------------------ coupes et images
def debut_visible(ffmpeg: str, video: pathlib.Path) -> float:
    """Le premier instant où l'image n'est plus noire (beaucoup de Shorts démarrent sur une image noire)."""
    r = lancer([ffmpeg, "-hide_banner", "-nostats", "-t", "3", "-i", video, "-an", "-vf",
                "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"], timeout=300)
    temps = [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    lum = [float(y) for y in re.findall(r"YAVG=([\d.]+)", r.stderr)]
    for t, y in zip(temps, lum):
        if y > 24:                      # noir vidéo ≈ 16 ; au-dessus de 24, il y a quelque chose à voir
            return round(t, 2)
    return 0.0


def detecter_coupes(ffmpeg: str, video: pathlib.Path, duree: float):
    """Changements d'image francs, mesurés deux fois : sur l'image entière, et sur sa zone centrale.

    La zone centrale rattrape les vidéos encadrées (format podcast : bande vidéo au milieu, fond noir et
    titre fixe autour) où le cadre immobile écrase le score de l'image entière sous le seuil."""
    trouves = []
    for zone in ("", f"crop=iw*0.8:ih*0.5:iw*0.1:ih*0.25,"):
        r = lancer([ffmpeg, "-hide_banner", "-nostats", "-i", video, "-an", "-filter:v",
                    f"{zone}select='gt(scene,{SCENE_SEUIL})',showinfo", "-f", "null", "-"], timeout=1800)
        trouves += [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    visible = debut_visible(ffmpeg, video)
    if visible > 0:
        trouves.append(visible)
    coupes = []
    for t in sorted(trouves):
        if 0.0 < t < duree - 0.1 and (not coupes or t - coupes[-1] >= 0.25):
            coupes.append(round(t, 2))
    return coupes, visible


def choisir_images(duree: float, coupes, visible: float = 0.0):
    """Une image juste après chaque coupe, 2/s sur les 5 premières s visibles, 1/s ensuite, la dernière ; 60 au plus.
    Une ouverture noire n'a pas d'image à elle : la première image est la première qui montre quelque chose."""
    fin = max(0.0, duree - 0.1)
    cand = [(min(c + 0.12, fin), "coupe") for c in coupes]
    t = round(visible + 0.12, 2) if visible > 0 else 0.0
    fin_hook = visible + HOOK_S
    while t < min(fin_hook, duree):
        cand.append((t, "debut"))
        t += 0.5
    t = fin_hook
    while t < duree - 0.2:
        cand.append((t, "seconde"))
        t += 1.0
    cand.append((fin, "fin"))
    priorite = {"debut": 0, "coupe": 1, "fin": 2, "seconde": 3}
    gardees = []
    for t, raison in sorted(cand, key=lambda x: (priorite[x[1]], x[0])):
        if all(abs(t - g[0]) >= ECART_MIN for g in gardees):
            gardees.append((round(t, 2), raison))
    if len(gardees) > PLAFOND_IMAGES:
        fixes = [g for g in gardees if g[1] != "seconde"]
        libres = [g for g in gardees if g[1] == "seconde"]
        if len(fixes) > PLAFOND_IMAGES - 5:          # beaucoup de coupes : on espace les images de coupe
            debut = [g for g in fixes if g[1] == "debut"]
            reste = [g for g in fixes if g[1] != "debut"]
            pas = len(reste) / max(1, PLAFOND_IMAGES - len(debut))
            reste = [reste[int(i * pas)] for i in range(min(len(reste), PLAFOND_IMAGES - len(debut)))]
            gardees = debut + reste
        else:
            place = PLAFOND_IMAGES - len(fixes)
            pas = len(libres) / max(1, place)
            gardees = fixes + [libres[int(i * pas)] for i in range(min(place, len(libres)))]
    return sorted(gardees)


def extraire_images(ffmpeg: str, dossier: pathlib.Path, choix, largeur: int):
    frames = dossier / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir()
    liste = []
    for i, (t, raison) in enumerate(choix):
        nom = f"f{i:02d}_{t:06.2f}s.jpg"
        r = lancer([ffmpeg, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", dossier / "media.mp4", "-frames:v", "1",
                    "-vf", f"scale={largeur}:-2:{COULEURS_JUSTES}", "-q:v", "3", frames / nom], timeout=120)
        if r.returncode == 0 and (frames / nom).exists():
            liste.append({"fichier": f"frames/{nom}", "t": t, "raison": raison})
    return liste


# Police 5 × 7 pour écrire l'heure sur chaque image d'une planche. Le ffmpeg de Homebrew n'a pas
# `drawtext` (pas de freetype) : on dessine l'étiquette nous-mêmes, en image PPM, et ffmpeg la colle.
POLICE = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    ":": "00000 01100 01100 00000 01100 01100 00000", ".": "00000 00000 00000 00000 00000 01100 01100",
}


def etiquette(texte: str, chemin: pathlib.Path, fond=(255, 255, 255), echelle: int = 3) -> None:
    """Écrit `texte` (chiffres, « : », « . ») en noir sur `fond`, cadre noir, dans une image PPM."""
    marge, bord = 2 * echelle, 2
    l = marge * 2 + len(texte) * 6 * echelle - echelle
    h = marge * 2 + 7 * echelle
    px = [[fond] * l for _ in range(h)]
    for i, c in enumerate(texte):
        for y, rang in enumerate(POLICE[c].split()):
            for x, bit in enumerate(rang):
                if bit == "1":
                    for dy in range(echelle):
                        for dx in range(echelle):
                            px[marge + y * echelle + dy][marge + (i * 6 + x) * echelle + dx] = (0, 0, 0)
    for y in range(h):
        for x in range(l):
            if x < bord or y < bord or x >= l - bord or y >= h - bord:
                px[y][x] = (0, 0, 0)
    chemin.write_bytes(f"P6 {l} {h} 255\n".encode() + bytes(v for rang in px for p in rang for v in p))


def assembler_planche(ffmpeg: str, sources, sortie: pathlib.Path, colonnes: int, tuile: int, media: dict) -> bool:
    """Colle des images en une planche (`colonnes` par rang, dans l'ordre de lecture), chacune avec son
    heure en haut à gauche ; `sources` = [(fichier, t, jaune)], jaune = étiquette jaune. Vrai si la
    planche est écrite."""
    lv, hv = media.get("largeur") or 9, media.get("hauteur") or 16
    th = max(2, int(round(tuile * hv / lv / 2)) * 2)
    cw, ch = tuile + 8, th + 8                             # une case = l'image + 4 px de blanc autour
    entrees, filtres, sorties = [], [], []
    n = len(sources)
    for i, (fichier, t, jaune) in enumerate(sources):
        lab = sortie.parent / f"_etiquette{i}.ppm"
        etiquette(mmss(t), lab, (255, 214, 0) if jaune else (255, 255, 255))
        entrees += ["-i", fichier, "-i", lab]
        filtres.append(f"[{2 * i}:v]scale={tuile}:{th},setsar=1[s{i}];[s{i}][{2 * i + 1}:v]overlay=6:6,"
                       f"pad={cw}:{ch}:4:4:white[t{i}]")
        sorties.append(f"[t{i}]")
    if n == 1:
        filtres.append("[t0]null[out]")
    else:
        places = "|".join(f"{(i % colonnes) * cw}_{(i // colonnes) * ch}" for i in range(n))
        filtres.append(f"{''.join(sorties)}xstack=inputs={n}:layout={places}:fill=white[out]")
    r = lancer([ffmpeg, "-y", "-v", "error", *entrees, "-filter_complex", ";".join(filtres), "-map", "[out]",
                "-frames:v", "1", "-q:v", "3", sortie], timeout=120)
    for lab in sortie.parent.glob("_etiquette*.ppm"):
        lab.unlink()
    return r.returncode == 0 and sortie.exists()


def faire_planches(ffmpeg: str, dossier: pathlib.Path, images, fin_hook: float, media: dict):
    """Les images au-delà des 5 premières secondes, par planches de 6 (3 × 2), dans l'ordre de lecture.

    Chaque image porte son heure en haut à gauche (étiquette jaune : image prise juste après une coupe).
    L'IA lit une planche au lieu de six images : même contenu, trois fois moins d'allers-retours."""
    dossier_p = dossier / "planches"
    shutil.rmtree(dossier_p, ignore_errors=True)
    reste = [im for im in images if im["t"] >= fin_hook]
    if not reste:
        return []
    dossier_p.mkdir()
    par_planche = PLANCHE_COLONNES * PLANCHE_LIGNES
    nb = -(-len(reste) // par_planche)                     # planches équilibrées : 32 images → 6,6,5,5,5,5
    bornes = [round(i * len(reste) / nb) for i in range(nb + 1)]
    planches = []
    for k in range(nb):
        groupe = reste[bornes[k]:bornes[k + 1]]
        nom = f"p{k + 1:02d}_{groupe[0]['t']:06.2f}-{groupe[-1]['t']:06.2f}s.jpg"
        sources = [(dossier / im["fichier"], im["t"], im["raison"] == "coupe") for im in groupe]
        if not assembler_planche(ffmpeg, sources, dossier_p / nom, PLANCHE_COLONNES, TUILE_LARGEUR, media):
            shutil.rmtree(dossier_p, ignore_errors=True)
            return None                                    # pas de planche : l'IA lira les images une à une
        planches.append({"fichier": f"planches/{nom}", "de": groupe[0]["t"], "a": groupe[-1]["t"],
                         "images": [im["fichier"] for im in groupe]})
    return planches


def analyser_plans(dossier: pathlib.Path, ffmpeg: str, largeur: int, media: dict) -> dict:
    duree = media["duree"]
    coupes, visible = detecter_coupes(ffmpeg, dossier / "media.mp4", duree)
    bornes = [0.0] + coupes + [duree]
    plans = [{"n": i + 1, "debut": bornes[i], "fin": bornes[i + 1], "duree": round(bornes[i + 1] - bornes[i], 2)}
             for i in range(len(bornes) - 1)]
    moyenne = round(duree / len(plans), 2) if plans else duree
    images = extraire_images(ffmpeg, dossier, choisir_images(duree, coupes, visible), largeur)
    fin_hook = round(visible + HOOK_S, 2)
    planches = faire_planches(ffmpeg, dossier, images, fin_hook, media)
    if planches is None:                                   # ffmpeg n'a pas su assembler : tout en images seules
        lecture = {"uneParUne": [im["fichier"] for im in images], "planches": []}
    else:
        lecture = {"uneParUne": [im["fichier"] for im in images if im["t"] < fin_hook], "planches": planches}
    rythme = ("très rapide" if moyenne < 1.5 else "rapide" if moyenne < 3 else "posé" if moyenne < 6
              else "plan quasi unique")
    shots = {
        "duree": duree,
        "seuilScene": SCENE_SEUIL,
        "coupes": coupes,
        "nbCoupes": len(coupes),
        "coupes0a3s": sum(1 for c in coupes if c <= 3),
        "coupes0a10s": sum(1 for c in coupes if c <= 10),
        "dureeMoyennePlan": moyenne,
        "ouvertureNoireJusqua": visible or None,
        "planLePlusLong": max((p["duree"] for p in plans), default=duree),
        "rythme": rythme,
        "plans": plans,
        "largeurImages": largeur,
        "images": images,
        "lecture": lecture,
        "_note": "Coupes franches détectées par changement d'image (seuil 0.3, sur l'image entière et sur sa "
                 "zone centrale) : un zoom brusque ou un texte plein écran compte comme une coupe, un fondu lent "
                 "ou une animation dans un plan n'en est pas une. Vérifie sur les images. Lecture : les images des 5 "
                 "premières secondes une par une (lecture.uneParUne), le reste en planches de 6 (lecture.planches, "
                 "de gauche à droite puis de haut en bas, heure en haut à gauche, étiquette jaune = juste après "
                 "une coupe). Texte illisible sur une planche : ouvre l'image seule dans frames/.",
    }
    ecrire_json(dossier / "shots.json", shots)
    return shots


# ------------------------------------------------------------------ style de montage (--style)
# Ce que l'IA ne voit pas bien sur des images fixes : comment un sous-titre apparaît, à quoi ressemble
# une transition, la couleur exacte. L'outil le prépare ; l'IA décrit et décide. Le son ne se mesure
# pas ici : un niveau ne distingue pas un bruitage d'une syllabe ni une musique basse du bruit de la
# pièce (essais du 16/10/2026) ; le skill demande au client ce qu'il entend.
RAFALE_SOUS_TITRES_PAS = 0.15        # 8 images en 1,2 s : on voit les mots arriver (ou se surligner)
RAFALE_COUPE_PAS = 0.12              # 6 images autour d'une coupe : coupe sèche, glissé, zoom, flash…
RAFALE_TUILE = 360                   # rafales plus grandes que les planches : la police doit se reconnaître


def pixels(ffmpeg: str, image: pathlib.Path, largeur: int = 48, zone=None):
    """Les pixels RVB d'une image réduite (largeur 48 px), éventuellement d'une bande de l'image
    (`zone` = (haut, bas) en fractions de la hauteur)."""
    vf = f"scale={largeur}:-2"
    if zone:
        vf = f"crop=iw:ih*{zone[1] - zone[0]:.3f}:0:ih*{zone[0]:.3f}," + vf
    r = subprocess.run([str(ffmpeg), "-v", "error", "-i", str(image), "-vf", vf, "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True, timeout=60)
    if r.returncode != 0:
        return []
    b = r.stdout
    return [(b[i], b[i + 1], b[i + 2]) for i in range(0, len(b) - 2, 3)]


def classer_couleurs(px):
    """Couleurs par familles (vives, blanc, noir), avec leur part et leur teinte la plus fréquente (pas la
    moyenne : les bords flous d'une lettre la tireraient vers le gris)."""
    import colorsys
    familles = {}
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if v < 0.13:
            cle = "noir"
        elif s < 0.12 and v > 0.88:
            cle = "blanc"
        elif s >= 0.6 and v >= 0.55:
            # Familles de 30° centrées : rouge autour de 0°, orange de 15 à 45°, jaune de 45 à 75°…
            cle = "vive-" + ("rouge", "orange", "jaune", "jaune-vert", "vert", "vert", "cyan", "bleu", "bleu",
                             "violet", "magenta", "rose")[int((h * 360 + 15) % 360 // 30)]
        else:
            continue
        f = familles.setdefault(cle, {})
        case = f.setdefault((r // 16, g // 16, b // 16), [0, 0, 0, 0])
        case[0] += 1
        case[1] += r
        case[2] += g
        case[3] += b
    total = max(1, len(px))
    sortie = {}
    for cle, cases in familles.items():
        n, rs, gs, bs = max(cases.values(), key=lambda c: c[0])
        sortie[cle] = {"part": round(sum(c[0] for c in cases.values()) / total, 4),
                       "hex": f"#{rs // n:02X}{gs // n:02X}{bs // n:02X}", "poids": n}
    return sortie


def analyser_couleurs(ffmpeg: str, dossier: pathlib.Path, images) -> dict:
    """Les couleurs vives qui reviennent d'image en image (texte surligné, accent de marque), et l'allure
    générale de l'image (claire ou sombre, vive ou sobre)."""
    import colorsys
    cumul, presence, lum, sat, n_px = {}, {}, 0.0, 0.0, 0
    for im in images:
        px = pixels(ffmpeg, dossier / im["fichier"], 120)
        if not px:
            continue
        for r, g, b in px:
            _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            lum += v
            sat += s
        n_px += len(px)
        for cle, val in classer_couleurs(px).items():
            c = cumul.setdefault(cle, [0.0, {}])
            c[0] += val["part"]
            c[1][val["hex"]] = c[1].get(val["hex"], 0) + val["poids"]
            if val["part"] >= 0.005:
                presence[cle] = presence.get(cle, 0) + 1
    nb = max(1, len(images))
    vives = sorted(([k[5:], round(v[0] / nb, 4), presence.get(k, 0), v[1]] for k, v in cumul.items()
                    if k.startswith("vive-") and presence.get(k, 0) >= max(2, nb // 6)),
                   key=lambda x: -x[2])[:4]

    def hex_moyen(teintes):
        return max(teintes.items(), key=lambda x: x[1])[0]

    lum_m = round(lum / max(1, n_px), 2)
    sat_m = round(sat / max(1, n_px), 2)
    allure = ("image sombre" if lum_m < 0.35 else "image claire" if lum_m > 0.62 else "image moyenne") + ", " + (
        "presque noir et blanc" if sat_m < 0.08 else "couleurs sobres" if sat_m < 0.22 else "couleurs vives")
    return {
        "vivesRecurrentes": [{"famille": f, "hex": hex_moyen(h), "partMoyenne": p, "images": n}
                             for f, p, n, h in vives],
        "blanc": round(cumul.get("blanc", [0])[0] / nb, 3),
        "noir": round(cumul.get("noir", [0])[0] / nb, 3),
        "luminositeMoyenne": lum_m,
        "saturationMoyenne": sat_m,
        "allure": allure,
        "_note": "Couleurs vives présentes sur plusieurs images (souvent : le mot surligné, l'accent des "
                 "animations ; parfois le décor). Vérifie sur les images à quoi chacune correspond. Couleur "
                 "exacte d'un élément : « couleurs <image> --zone bas|milieu|haut ».",
    }


def rafales(ffmpeg: str, dossier: pathlib.Path, transcript: dict, shots: dict, media: dict) -> list:
    """Planches d'images rapprochées : pendant une phrase (comment le sous-titre apparaît) et autour de
    trois coupes (à quoi ressemble la transition)."""
    sortie = dossier / "rafales"
    shutil.rmtree(sortie, ignore_errors=True)
    sortie.mkdir()
    tmp = sortie / "_images"
    tmp.mkdir()
    duree = media["duree"]
    debut_utile = (shots.get("ouvertureNoireJusqua") or 0) + HOOK_S
    plans = []
    # 1. Sous-titres : un morceau de phrase d'au moins 5 mots et 1,6 s, au plus près du milieu de la vidéo.
    morceaux = [m for m in transcript.get("morceaux") or []
                if len(m["texte"].split()) >= 5 and m["fin"] - m["debut"] >= 1.6 and m["debut"] >= debut_utile * 0.6]
    if not morceaux:
        morceaux = [m for m in transcript.get("morceaux") or [] if m["fin"] - m["debut"] >= 1.2]
    if morceaux:
        m = min(morceaux, key=lambda x: abs((x["debut"] + x["fin"]) / 2 - duree / 2))
        temps = [round(m["debut"] + 0.05 + i * RAFALE_SOUS_TITRES_PAS, 2) for i in range(8)]
        plans.append(("sous-titres", [t for t in temps if t < duree - 0.05], None, 4, m["texte"]))
    # 2. Transitions : la première coupe après l'ouverture, une au milieu, une aux trois quarts.
    coupes = shots.get("coupes") or []
    choisies = []
    for cible in (0.0, duree / 2, duree * 0.75):
        c = min(coupes, key=lambda x: abs(x - cible), default=None)
        if c is not None and c not in choisies:
            choisies.append(c)
    for c in choisies:
        temps = [round(c + d * RAFALE_COUPE_PAS, 2) for d in (-2, -1, 0, 1, 2, 3)]
        temps[2] = round(c + 0.03, 2)
        plans.append(("coupe", [t for t in temps if 0 <= t < duree - 0.05], c, 3, None))
    resultat = []
    for k, (genre, temps, coupe, colonnes, texte) in enumerate(plans):
        sources = []
        for i, t in enumerate(temps):
            f = tmp / f"r{k}_{i}.jpg"
            r = lancer([ffmpeg, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", dossier / "media.mp4", "-frames:v",
                        "1", "-vf", f"scale=768:-2:{COULEURS_JUSTES}", "-q:v", "3", f], timeout=120)
            if r.returncode == 0 and f.exists():
                sources.append((f, t, coupe is not None and t >= coupe))
        if len(sources) < 3:
            continue
        nom = (f"{k + 1}-sous-titres_{temps[0]:06.2f}s.jpg" if genre == "sous-titres"
               else f"{k + 1}-coupe_{coupe:06.2f}s.jpg")
        if assembler_planche(ffmpeg, sources, sortie / nom, colonnes, RAFALE_TUILE, media):
            entree = {"genre": genre, "fichier": f"rafales/{nom}", "de": sources[0][1], "a": sources[-1][1]}
            if genre == "sous-titres":
                entree["paroles"] = texte
                entree["pas"] = RAFALE_SOUS_TITRES_PAS
            else:
                entree["coupe"] = coupe
                entree["pas"] = RAFALE_COUPE_PAS
            resultat.append(entree)
    shutil.rmtree(tmp, ignore_errors=True)
    return resultat


def mediane(valeurs):
    v = sorted(valeurs)
    if not v:
        return None
    m = len(v) // 2
    return v[m] if len(v) % 2 else (v[m - 1] + v[m]) / 2


def analyser_rythme(shots: dict) -> dict:
    """Le rythme dans le temps : où ça coupe vite, où ça respire."""
    duree, coupes = shots["duree"], shots.get("coupes") or []
    plans = [p["duree"] for p in shots.get("plans") or []]
    tranches = []
    t = 0.0
    while t < duree - 0.5:
        fin = min(duree, t + 5)
        tranches.append({"de": round(t, 1), "a": round(fin, 1), "coupes": sum(1 for c in coupes if t <= c < fin)})
        t = fin
    debut = tranches[0]["coupes"] if tranches else 0
    suite = [tr["coupes"] for tr in tranches[1:]]
    moy_suite = sum(suite) / len(suite) if suite else 0
    if not coupes:
        lecture = "un seul plan, aucune coupe franche : le rythme vient des animations ou du zoom (voir les images)"
    else:
        lecture = (f"{len(coupes)} coupes ; un plan dure le plus souvent {mediane(plans):.1f} s "
                   f"(de {min(plans):.1f} à {max(plans):.1f} s)")
        if debut >= moy_suite + 2:
            lecture += f" ; accroche plus nerveuse : {debut} coupes sur les 5 premières secondes"
    return {"planMedian": round(mediane(plans) or duree, 2), "planLePlusCourt": round(min(plans or [duree]), 2),
            "planLePlusLong": round(max(plans or [duree]), 2), "coupesParTranche5s": tranches, "lecture": lecture}


def analyser_style(dossier: pathlib.Path, ffmpeg: str, media: dict, transcript: dict, shots: dict) -> dict:
    """style.json : rythme dans le temps, couleurs qui reviennent, rafales d'images."""
    style = {
        "rythme": analyser_rythme(shots),
        "couleurs": analyser_couleurs(ffmpeg, dossier, shots.get("images") or []),
        "rafales": rafales(ffmpeg, dossier, transcript, shots, media),
        "largeurImages": shots.get("largeurImages"),
        "_note": "Mesures pour la fiche de style (skill reel-cloneur, mode style). Les rafales sont des "
                 "planches d'images rapprochées (heure en haut à gauche, étiquette jaune = après la coupe) : "
                 "« sous-titres » montre comment le texte arrive pendant une phrase, « coupe » à quoi "
                 "ressemble la transition. Tout se vérifie sur les images. Le son n'est pas mesuré : demande-le au client.",
    }
    ecrire_json(dossier / "style.json", style)
    return style


def couleurs_image(image: str, zone) -> int:
    ffmpeg = binaire("ffmpegPath", "ffmpeg")
    chemin = pathlib.Path(image).expanduser()
    if not ffmpeg or not chemin.exists():
        arret(f"Image ou ffmpeg introuvable : {image}")
    bandes = {"haut": (0.0, 0.35), "milieu": (0.3, 0.7), "bas": (0.6, 1.0), None: None}
    px = pixels(ffmpeg, chemin, 96, bandes[zone])
    if not px:
        arret("Je n'arrive pas à lire cette image.")
    comptes = {}
    for r, g, b in px:
        cle = (r // 16 * 16 + 8, g // 16 * 16 + 8, b // 16 * 16 + 8)
        comptes[cle] = comptes.get(cle, 0) + 1
    dire(f"Couleurs les plus présentes ({chemin.name}{', zone ' + zone if zone else ''}) :")
    familles = classer_couleurs(px)
    for (r, g, b), n in sorted(comptes.items(), key=lambda x: -x[1])[:8]:
        dire(f"  #{min(r, 255):02X}{min(g, 255):02X}{min(b, 255):02X}  {100 * n / len(px):5.1f} %")
    vives = {k[5:]: v for k, v in familles.items() if k.startswith("vive-") and v["part"] >= 0.003}
    if vives:
        dire("Couleurs vives : " + ", ".join(f"{k} {v['hex']} ({100 * v['part']:.1f} %)"
                                             for k, v in sorted(vives.items(), key=lambda x: -x[1]["part"])))
    return 0


# ------------------------------------------------------------------ test anti-copie
def mots(texte: str):
    t = unicodedata.normalize("NFKD", (texte or "").lower()).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", t)


def comparer(cible_txt: str, taille: int = 6) -> int:
    """Cherche dans un script (brouillon ou script.md) toute suite de `taille` mots reprise du Reel d'origine.

    Sources : les paroles (transcript.json), la légende, et le script mot pour mot écrit dans analyse.md,
    traductions comprises : traduire une phrase de l'auteur, c'est encore la copier."""
    cible = pathlib.Path(cible_txt).expanduser()
    script_p = cible if cible.is_file() else cible / "script.md"
    dossier = script_p.parent
    if not script_p.exists():
        arret(f"Je ne trouve pas le script à vérifier : {script_p}")
    transcript = lire_json(dossier / "transcript.json") or {}
    meta = lire_json(dossier / "meta.json") or {}
    sources = {"paroles": transcript.get("texte") or "", "légende": meta.get("legende") or ""}
    analyse = dossier / "analyse.md"
    if analyse.exists():
        texte = analyse.read_text(encoding="utf-8")
        bloc = re.search(r"\n## 1\.(.*?)(?=\n## 2\.|\Z)", texte, re.S)    # le script mot pour mot (+ traduction)
        if bloc:
            # Seulement la colonne « Ce qui est dit » (phrase et traduction), pas les descriptions d'images.
            lignes = [l.split("|") for l in bloc.group(1).splitlines()
                      if l.strip().startswith("|") and not set(l.strip()) <= set("|-: ")]
            if lignes:
                entete = [c.strip().lower() for c in lignes[0]]
                col = next((i for i, c in enumerate(entete) if "dit" in c), 2)
                dits = [l[col] for l in lignes[1:] if len(l) > col]
                sources["script d'origine et sa traduction (analyse.md)"] = "\n".join(dits)
    # Seul le texte prompteur compte : ce qui précède « À vérifier avant de tourner », « À reproduire
    # au montage » ou « Pour Monteur IA » (les faits sur l'outil et le bloc technique reprennent des
    # mots de la vidéo par nature, ce n'est pas une copie).
    texte_script = script_p.read_text(encoding="utf-8")
    coupe = re.search(r"\n## (À vérifier|À reproduire|Pour Monteur IA)", texte_script)
    if coupe:
        texte_script = texte_script[:coupe.start()]
    script = mots(texte_script)
    trouvees = []
    for nom, texte in sources.items():
        m = mots(texte)
        grammes = {tuple(m[i:i + taille]) for i in range(len(m) - taille + 1)}
        i = 0
        while i <= len(script) - taille:
            if tuple(script[i:i + taille]) in grammes:
                j = i + taille
                while j < len(script) and tuple(script[j - taille + 1:j + 1]) in grammes:
                    j += 1
                trouvees.append((nom, " ".join(script[i:j])))
                i = j
            else:
                i += 1
    if not trouvees:
        dire(f"ok : aucune suite de {taille} mots ou plus reprise du Reel d'origine dans le texte prompteur (paroles, traduction, légende).")
        dire("(Le texte à l'écran n'est que dans les images : relis-le toi-même.)")
        return 0
    dire(f"⚠️ {len(trouvees)} passage(s) proches du Reel d'origine dans le texte prompteur (à reformuler, sauf si le client veut les garder ou si c'est un fait sur l'outil) :")
    for nom, extrait in trouvees:
        dire(f"  - [{nom}] « {extrait} »")
    return 1


# ------------------------------------------------------------------ le clonage
def cloner(source: str, largeur, langue, refaire: bool, style: bool = False) -> None:
    debut = time.time()
    telecharge = False
    # Le style se lit dans les détails (police, contour, surlignage) : images plus grandes par défaut.
    largeur = largeur or (768 if style else 512)
    ffmpeg = binaire("ffmpegPath", "ffmpeg")
    if not ffmpeg:
        arret("ffmpeg est introuvable : c'est un outil de Monteur IA, relance son installation.")
    CLONES.mkdir(exist_ok=True)
    aujourdhui = datetime.date.today().isoformat()
    brut = source.strip().strip("'\"")
    if brut.startswith("file://"):
        brut = urllib.parse.unquote(brut[7:])
    chemin = pathlib.Path(brut).expanduser()
    if not chemin.exists() and "\\ " in brut:
        chemin = pathlib.Path(brut.replace("\\ ", " ")).expanduser()   # glissé depuis le Finder : « Mon\ Reel.mov »
    est_fichier = not re.match(r"https?://", source.strip()) and chemin.exists()
    if not est_fichier and not re.match(r"https?://", source.strip()):
        if chemin.suffix.lower() in FICHIER_VIDEO:
            arret(f"Je ne trouve pas ce fichier : {chemin}")
        source = "https://" + source.strip()

    if est_fichier:
        chemin = chemin.resolve()
        dossier = clone_existant(None, None, str(chemin))
        if dossier is None or refaire:
            dossier = dossier or CLONES / f"{aujourdhui}-fichier-{slugifier(chemin.stem)}"
            dossier.mkdir(parents=True, exist_ok=True)
            dire(f"• fichier : {chemin.name}")
            preparer_fichier(chemin, dossier, ffmpeg)
            telecharge = True
            meta = {"source": str(chemin), "plateforme": "fichier", "id": None, "lien": None,
                    "auteur": None, "compte": None, "titre": chemin.stem, "date": None, "legende": None,
                    "likes": None, "commentaires": None, "vues": None, "partages": None, "musique": "non détectable",
                    "hashtags": []}
            ecrire_json(dossier / "meta.json", meta)
        else:
            dire(f"• déjà cloné : je reprends {dossier.name}")
    else:
        url = source.strip()
        plateforme, ident = id_du_lien(url)
        dossier = clone_existant(plateforme, ident, url)
        if dossier is not None and (dossier / "media.mp4").exists() and not refaire:
            dire(f"• déjà téléchargé : je reprends {dossier.name}")
        else:
            dire(f"• téléchargement : {url}")
            t0 = time.time()
            tmp, info = telecharger(url, ffmpeg)
            telecharge = True
            meta = meta_depuis_info(info, url)
            if dossier is None:
                nom = "-".join(x for x in (aujourdhui, meta["plateforme"], slugifier(meta["compte"] or "", 30),
                                           slugifier(meta["id"] or "", 20)) if x)
                dossier = CLONES / nom
            dossier.mkdir(parents=True, exist_ok=True)
            shutil.move(str(tmp / "media.mp4"), str(dossier / "media.mp4"))
            shutil.rmtree(tmp, ignore_errors=True)
            ecrire_json(dossier / "meta.json", meta)
            dire(f"  ok ({time.time() - t0:.1f} s)")
            for vieux in ("audio.wav", "transcript.json", "shots.json"):
                (dossier / vieux).unlink(missing_ok=True)

    meta = lire_json(dossier / "meta.json") or {}
    media = sonde(ffmpeg, dossier / "media.mp4")
    if not media["duree"]:
        arret("Cette vidéo semble vide ou abîmée (durée nulle).")

    refait = False
    t0 = time.time()
    if media["audio"]:
        if refaire or not (dossier / "audio.wav").exists():
            extraire_audio(ffmpeg, dossier)
        transcript = lire_json(dossier / "transcript.json")
        if refaire or langue or transcript is None or "phrases" not in transcript:
            dire("• transcription…")
            refait = True
            transcript = transcrire(dossier, langue, media["duree"])
            dire(f"  ok ({time.time() - t0:.1f} s, langue : {transcript['langue']})")
    else:
        transcript = {"langue": None, "phrases": [], "morceaux": [], "texte": "",
                      "_note": "Vidéo sans piste audio : tout passe par l'image et le texte à l'écran."}
        ecrire_json(dossier / "transcript.json", transcript)

    t0 = time.time()
    shots = lire_json(dossier / "shots.json")
    if (refaire or shots is None or shots.get("largeurImages") != largeur or not (dossier / "frames").exists()
            or "ouvertureNoireJusqua" not in shots or "lecture" not in shots):
        dire("• coupes et images…")
        refait = True
        shots = analyser_plans(dossier, ffmpeg, largeur, media)
        dire(f"  ok ({time.time() - t0:.1f} s)")

    style_d = None
    if style:
        t0 = time.time()
        style_d = lire_json(dossier / "style.json")
        if (refait or style_d is None or style_d.get("largeurImages") != largeur
                or not (dossier / "rafales").exists()):
            dire("• style de montage (rythme, couleurs, rafales d'images)…")
            refait = True
            style_d = analyser_style(dossier, ffmpeg, media, transcript, shots)
            dire(f"  ok ({time.time() - t0:.1f} s)")

    meta.update({"duree": media["duree"], "largeur": media["largeur"], "hauteur": media["hauteur"],
                 "fps": media["fps"], "dossier": str(dossier)})
    meta.setdefault("clonéLe", datetime.datetime.now().isoformat(timespec="seconds"))
    ecrire_json(dossier / "meta.json", meta)

    # ---- résumé court (l'IA lit ensuite les fichiers eux-mêmes)
    def n(v):
        return f"{v:,}".replace(",", " ") if isinstance(v, int) else "inconnu"
    dire("")
    dire(f"✅ Reel prêt à analyser : {dossier}")
    dire(f"   {meta.get('plateforme')} · {meta.get('compte') or meta.get('auteur') or '?'} · publié le "
         f"{meta.get('date') or '?'} · {media['duree']:.1f} s")
    dire(f"   vues {n(meta.get('vues'))} · likes {n(meta.get('likes'))} · commentaires {n(meta.get('commentaires'))}")
    dire(f"   {len(transcript.get('phrases') or [])} phrases transcrites (langue : {transcript.get('langue')})")
    dire(f"   {shots['nbCoupes']} coupes (dont {shots['coupes0a3s']} sur 0-3 s, {shots['coupes0a10s']} sur 0-10 s), "
         f"plan moyen {shots['dureeMoyennePlan']} s, rythme {shots['rythme']} (coupes franches seulement : "
         "les animations et zooms se voient sur les images)")
    lec = shots["lecture"]
    if lec["planches"]:
        dire(f"   à lire : {len(lec['uneParUne'])} images une par une (les 5 premières secondes, dans frames/), puis "
             f"{len(lec['planches'])} planche{'s' if len(lec['planches']) > 1 else ''} de 6 images au plus (le reste, "
             "dans planches/)")
    else:
        dire(f"   à lire : {len(lec['uneParUne'])} images dans frames/ ({largeur} px)")
    if style_d:
        dire(f"   style : {style_d['rythme']['lecture']}")
        vives = ", ".join(f"{c['famille']} {c['hex']}" for c in style_d["couleurs"]["vivesRecurrentes"])
        dire(f"   couleurs : {style_d['couleurs']['allure']}" + (f" ; vives qui reviennent : {vives}" if vives else ""))
        dire(f"   rafales à lire (dans rafales/) : {len(style_d['rafales'])}")
    premiere = transcript["phrases"][0]["texte"] if transcript.get("phrases") else None
    if premiere:
        dire(f"   première phrase : « {premiere[:140]} »")
    if refait or telecharge:
        dire(f"   préparé en {time.time() - debut:.0f} s")
    else:
        dire("   dossier déjà prêt, rien à refaire")
    dire("")
    if style_d:
        dire("Étape suivante (pour l'IA) : lis style.json, les images du début une par une, chaque planche et chaque "
             "rafale ; ensuite, suis le mode style du skill reel-cloneur.")
    else:
        dire("Étape suivante (pour l'IA) : lis transcript.json, les images du début une par une, puis chaque planche ; "
             "ensuite, suis le skill reel-cloneur.")


def main() -> None:
    p = argparse.ArgumentParser(description="Reel Cloneur : prépare l'analyse d'un Reel (lien ou fichier).")
    p.add_argument("source", help="lien du Reel / TikTok / Short, chemin d'un fichier vidéo, ou « installer » / "
                   "« verifier » / « comparer » / « couleurs »")
    p.add_argument("dossier", nargs="?", help="avec « comparer » : le dossier clones/<…> à vérifier ; "
                   "avec « couleurs » : l'image")
    p.add_argument("--style", action="store_true",
                   help="prépare aussi le style de montage (rythme, couleurs, rafales d'images) : style.json")
    p.add_argument("--zone", choices=["haut", "milieu", "bas"], help="avec « couleurs » : une bande de l'image")
    p.add_argument("--largeur", type=int, default=None, choices=[512, 768],
                   help="largeur des images (512 par défaut, 768 avec --style)")
    p.add_argument("--langue", help="force la langue parlée (fr, en, es…) ; sinon détectée")
    p.add_argument("--refaire", action="store_true", help="refait tout, même ce qui est déjà prêt")
    a = p.parse_args()
    if a.source == "installer":
        installer()
    elif a.source in ("verifier", "vérifier"):
        sys.exit(verifier())
    elif a.source == "comparer":
        if not a.dossier:
            arret(f"Usage : {PY} tools/cloner_reel.py comparer clones/<dossier>")
        sys.exit(comparer(a.dossier))
    elif a.source == "couleurs":
        if not a.dossier:
            arret(f"Usage : {PY} tools/cloner_reel.py couleurs clones/<dossier>/frames/<image>.jpg [--zone bas]")
        sys.exit(couleurs_image(a.dossier, a.zone))
    else:
        cloner(a.source, a.largeur, a.langue, a.refaire, a.style)


if __name__ == "__main__":
    main()
