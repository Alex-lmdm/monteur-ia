#!/usr/bin/env python3
"""PRISES : transcrit chaque prise d'un rush lu au prompteur et PROPOSE les prises à garder.

Usage (depuis le dossier du Reel ou de la vidéo YouTube) :
    python3 tools/prises.py "<rush>"                          # tableau des prises + proposition
    python3 tools/prises.py "<rush>" --script work/script.txt # + rapproché du texte (une phrase par ligne)
    python3 tools/prises.py "<rush>" --ecrire [--nom mon-cut] # écrit derush/build_derush.py (proposition)

Les étapes 1 à 4 du skill derush en une commande, en une à deux minutes pour un rush de 3 minutes :
  1. le son du rush en 16 kHz (work/prises_audio.wav), le flux 0:a:0 (caméras à double flux) ;
  2. les îlots de parole au réglage du dérush (derush.silenceDb / islandDuration), regroupés en
     prises : un blanc d'au moins 0,5 s sépare deux prises ;
  3. chaque prise transcrite SEULE par Whisper (fiable sur un morceau court ; le fichier entier
     fond les reprises dans une même phrase) ;
  4. le choix, règle du dérush : la DERNIÈRE prise propre de chaque phrase.
     - une prise est une reprise d'une prise proche qui suit (dans les 4 suivantes, moins de 30 s)
       si elle commence par les mêmes 3 mots ou si la suivante la contient presque entière, et
       que la suivante est au moins aussi complète ;
     - une prise qui recommence une prise gardée juste avant sans aller au bout (faux départ) part ;
     - un bruit transcrit (« Merci. » sur moins d'une seconde, aucun mot) part.
  Le début de chaque prise est recalé sur l'attaque de la voix (un clic isolé avant n'est pas
  gardé) ; la fin est celle de l'îlot, comme le veut la recette des marges.

Ce que l'outil ne décide pas, à relire dans le tableau : une improvisation à garder ou non, un
raccord (changer de cadre sur un mot), une prise dont un mot est raté au milieu (Whisper lisse les
bafouillages). La re-transcription du dérush reste obligatoire (skill derush, étape 6).

--ecrire crée derush/build_derush.py depuis le gabarit du skill derush (rush, sortie, marges du
dossier : celles des Reels, ou youtube.derush s'il est réglé pour une vidéo YouTube, et ISLANDS) ;
il refuse d'écraser un script existant sans --ecraser.
"""
from __future__ import annotations

import argparse
import array
import json
import math
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata
import wave
from difflib import SequenceMatcher

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lieux import MAISON, config, reel  # noqa: E402

ECART_PRISES = 0.5        # s : un blanc au moins aussi long sépare deux prises
FENETRE_PRISES, FENETRE_S = 4, 30.0   # une reprise se cherche dans les 4 prises suivantes, à moins de 30 s
# Ce que Whisper « entend » dans un bruit ou un silence (hallucinations connues).
BRUITS = ("merci", "sous titrage", "sous titres", "musique", "rires", "applaudissements", "merci d avoir regarde")
LETTRES_PAR_S = 40.0      # au-delà, ce n'est pas une voix (une hallucination sur un bruit court)
SR = 16000


# --- texte --------------------------------------------------------------------------------------
def mots(texte: str) -> list[str]:
    t = unicodedata.normalize("NFKD", texte.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", t)


def lcs(a: list[str], b: list[str]) -> int:
    """Longueur de la plus longue sous-suite commune (mots dans l'ordre)."""
    prec = [0] * (len(b) + 1)
    for x in a:
        cour = [0]
        for j, y in enumerate(b):
            cour.append(prec[j] + 1 if x == y else max(prec[j + 1], cour[j]))
        prec = cour
    return prec[-1]


def est_bruit(p: dict) -> bool:
    m, duree = mots(p["texte"]), p["fin"] - p["debut"]
    if not m or duree < 0.25 or len("".join(m)) / duree > LETTRES_PAR_S:
        return True
    return duree < 1.5 and any(" ".join(m).startswith(b) for b in BRUITS)


def meme_phrase(a: list[str], b: list[str], strict: bool = False) -> bool:
    """b reprend la phrase de a : même début (3 mots), ou b contient presque tout a. Strict (deux
    phrases différentes du script) : seulement si b contient a presque mot pour mot."""
    contenu = lcs(a, b) / len(a) if a else 0.0
    if strict:
        return contenu >= 0.9
    return (len(a) >= 3 and a[:3] == b[:3]) or contenu >= 0.75


def choisir(prises: list[dict], script: list[str] | None = None) -> list[dict]:
    """Ajoute à chaque prise « statut » : garde, reprise (remplacée par une prise suivante), faux
    départ (recommence la prise gardée d'avant sans aller au bout) ou bruit. Fonction pure (tests)."""
    lignes = [mots(l) for l in (script or []) if mots(l)]

    def ligne(m: list[str]) -> tuple[int, float]:
        if not lignes:
            return -1, 0.0
        scores = [SequenceMatcher(None, m, l).ratio() for l in lignes]
        k = max(range(len(scores)), key=scores.__getitem__)
        return k, scores[k]

    for p in prises:
        p["mots"] = mots(p["texte"])
        p["statut"] = "bruit" if est_bruit(p) else "garde"
        p["ligne"], p["score"] = ligne(p["mots"])
    utiles = [p for p in prises if p["statut"] != "bruit"]

    def lignes_differentes(a: dict, b: dict) -> bool:
        # Deux phrases du script qui commencent pareil ne sont pas des reprises l'une de l'autre.
        return a["ligne"] >= 0 and b["ligne"] >= 0 and a["ligne"] != b["ligne"] and min(a["score"], b["score"]) >= 0.6

    for i, a in enumerate(utiles):
        for b in utiles[i + 1:i + 1 + FENETRE_PRISES]:
            if b["debut"] - a["fin"] > FENETRE_S:
                break
            if (meme_phrase(a["mots"], b["mots"], strict=lignes_differentes(a, b))
                    and len(b["mots"]) >= 0.8 * len(a["mots"])):
                a["statut"], a["par"] = "reprise", b["n"]
                break
    gardees = [p for p in utiles if p["statut"] == "garde"]
    for a, b in zip(gardees, gardees[1:]):
        if (b["debut"] - a["fin"] <= FENETRE_S and len(b["mots"]) < 0.8 * len(a["mots"])
                and a["mots"][:3] == b["mots"][:3] and lcs(b["mots"], a["mots"]) / max(len(b["mots"]), 1) >= 0.75
                and not lignes_differentes(a, b)):
            b["statut"], b["par"] = "faux depart", a["n"]
    return prises


def rapport(script: list[str], gardees: list[dict]) -> tuple[list[tuple[str, float]], list[dict]]:
    """Phrases du script mal couvertes par les prises gardées ((phrase, part dite) sous 60 % : une
    phrase peut être dite en une ou plusieurs prises de suite), et prises gardées qui ne viennent
    d'aucune phrase du script (improvisation : à garder ou non)."""
    lignes = [(l, mots(l)) for l in script if mots(l)]
    suites = [sum((p["mots"] for p in gardees[i:i + k]), []) for k in (1, 2, 3) for i in range(len(gardees))]
    manquent = []
    for l, m in lignes:
        part = max((lcs(m, s) / len(m) for s in suites), default=0.0)
        if part < 0.6:
            manquent.append((l, part))
    hors = [p for p in gardees if p["mots"] and not any(
        lcs(p["mots"], m) / min(len(p["mots"]), len(m)) >= 0.6 for _, m in lignes)]
    return manquent, hors


# --- son ----------------------------------------------------------------------------------------
def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")


def ilots(wav: pathlib.Path, seuil_db: float, duree_min: float, total: float) -> list[tuple[float, float]]:
    log = run(["ffmpeg", "-nostats", "-i", str(wav), "-af", f"silencedetect=noise={seuil_db}dB:d={duree_min}",
               "-f", "null", "-"]).stderr
    silences, debut = [], None
    for genre, t in re.findall(r"silence_(start|end): (-?[\d.]+)", log):
        if genre == "start":
            debut = max(float(t), 0.0)
        elif debut is not None:
            silences.append((debut, float(t)))
            debut = None
    if debut is not None:
        silences.append((debut, total))
    out, prec = [], 0.0
    for a, b in silences:
        if a - prec > 0.001:
            out.append((prec, a))
        prec = b
    if total - prec > 0.01:
        out.append((prec, total))
    return out


def niveaux(wav: pathlib.Path) -> array.array:
    """Niveau (dB) par tranche de 10 ms du son 16 kHz mono."""
    with wave.open(str(wav), "rb") as f:
        ech = array.array("h")
        ech.frombytes(f.readframes(f.getnframes()))
    pas = SR // 100
    out = array.array("f")
    for i in range(0, len(ech), pas):
        bloc = ech[i:i + pas]
        rms = math.sqrt(sum(x * x for x in bloc) / max(len(bloc), 1))
        out.append(20 * math.log10(max(rms, 1) / 32768))
    return out


def attaque(db: array.array, debut: float) -> float:
    """Début de la voix : la première tranche au-dessus de -48 dB suivie de 80 ms toutes au-dessus de
    -54 dB, entre 0,10 s avant et 0,40 s après le début de l'îlot (un clic isolé ne compte pas),
    moins 20 ms de sécurité pour une attaque douce (« Le », « Il »)."""
    a, b = max(int((debut - 0.10) * 100), 0), int((debut + 0.40) * 100)
    for k in range(a, min(b, len(db) - 8)):
        if db[k] > -48 and all(db[k + j] > -54 for j in range(8)):
            return round(max(k / 100 - 0.02, 0.0), 3)
    return round(debut, 3)


def transcrire(wav: pathlib.Path, a: float, b: float, whisper: str, modele: pathlib.Path, langue: str, tmp: pathlib.Path) -> str:
    morceau = tmp / "prise.wav"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(a - 0.15, 0):.3f}", "-to", f"{b + 0.15:.3f}", "-i", str(wav),
         "-af", "loudnorm=I=-16:TP=-1.5", "-ar", str(SR), "-ac", "1", str(morceau)])
    sortie = run([whisper, "-m", str(modele), "-l", langue, "-np", "-nt", str(morceau)]).stdout
    return " ".join(l.strip() for l in sortie.splitlines() if l.strip())


# --- réglages -----------------------------------------------------------------------------------
def modele_whisper(env: dict) -> pathlib.Path:
    if env.get("whisperModel"):
        return pathlib.Path(env["whisperModel"]).expanduser()
    for d in (".cache/monteur-ia/whisper", ".cache/hyperframes/whisper/models", "whisper-models", ".cache/whisper"):
        trouves = [f for f in (pathlib.Path.home() / d).glob("ggml-*.bin") if ".en." not in f.name]
        for prefere in ("large-v3-turbo", "large-v3", "large", "medium", "small", "base"):
            for f in trouves:
                if prefere in f.name:
                    return f
    return pathlib.Path.home() / ".cache/monteur-ia/whisper/ggml-large-v3-turbo.bin"


def marges(cfg: dict, projet: pathlib.Path) -> tuple[float, float]:
    """Celles des Reels (bloc derush) ; pour une vidéo YouTube, youtube.derush s'il est réglé."""
    d = cfg.get("derush") or {}
    pad = (float(d.get("padStart", 0.04)), float(d.get("padEnd", 0.02)))
    try:
        lieu = (json.loads((projet / "meta.json").read_text(encoding="utf-8")).get("monteurIa") or {}).get("lieu")
    except (OSError, ValueError):
        lieu = None
    yt = (cfg.get("youtube") or {}).get("derush") if lieu == "youtube" else None
    if yt:
        pad = (float(yt.get("padStart", pad[0])), float(yt.get("padEnd", pad[1])))
    return pad


def gabarit() -> pathlib.Path | None:
    for base in (".claude", ".agents"):
        f = MAISON / base / "skills/derush/references/build_derush_template.py"
        if f.is_file():
            return f
    return None


def ecrire(projet: pathlib.Path, rush: pathlib.Path, nom: str, gardees: list[dict], pad: tuple[float, float], ecraser: bool) -> None:
    cible = projet / "derush/build_derush.py"
    if cible.exists() and not ecraser:
        sys.exit(f"ERREUR : {cible.relative_to(projet)} existe déjà (le dérush en cours). Relance avec --ecraser "
                 "pour le remplacer par cette proposition.")
    src = gabarit()
    if src is None:
        sys.exit("ERREUR : gabarit du dérush introuvable (.claude/skills/derush/references/build_derush_template.py).")
    t = src.read_text(encoding="utf-8")
    lignes = "\n".join(f"    ({p['debut']:.3f}, {p['fin']:.3f}, {p['texte']!r})," for p in gardees)
    t = re.sub(r'^SRC = .*$', f'SRC = {str(rush)!r}   # rush brut (prises proposées par tools/prises.py)', t, count=1, flags=re.M)
    t = re.sub(r'^OUT = .*$', f'OUT = "derush/{nom}.mp4"', t, count=1, flags=re.M)
    t = re.sub(r"ISLANDS = \[.*?\n\]", "ISLANDS = [\n" + lignes + "\n]", t, count=1, flags=re.S)
    t = re.sub(r"^PAD_START = [\d.]+", f"PAD_START = {pad[0]}", t, count=1, flags=re.M)
    t = re.sub(r"^PAD_END   = [\d.]+", f"PAD_END   = {pad[1]}", t, count=1, flags=re.M)
    cible.parent.mkdir(exist_ok=True)
    cible.write_text(t, encoding="utf-8")
    print(f"\n• {cible.relative_to(projet)} écrit ({len(gardees)} prises, marges {pad[0]} / {pad[1]}). "
          "Relis-le (improvisations, raccords), puis : python3 derush/build_derush.py")


def main() -> None:
    ap = argparse.ArgumentParser(description="Propose les prises à garder d'un rush lu au prompteur.")
    ap.add_argument("rush")
    ap.add_argument("--script", help="texte lu, une phrase par ligne (repère les phrases jamais dites)")
    ap.add_argument("--ecrire", action="store_true", help="écrit derush/build_derush.py avec la proposition")
    ap.add_argument("--ecraser", action="store_true", help="avec --ecrire : remplace un build_derush.py existant")
    ap.add_argument("--nom", default="derush", help="nom du cut (derush/<nom>.mp4)")
    args = ap.parse_args()
    projet = reel()
    rush = pathlib.Path(args.rush).expanduser().resolve()
    if not rush.is_file():
        sys.exit(f"ERREUR : rush introuvable : {args.rush}")
    cfg = config()
    env, der = cfg.get("env") or {}, cfg.get("derush") or {}
    langue = der.get("whisperLanguage") or (cfg.get("brand") or {}).get("language") or "fr"
    whisper = str(pathlib.Path(env["whisperCli"]).expanduser()) if env.get("whisperCli") else "whisper-cli"
    modele = modele_whisper(env)
    if not modele.exists():
        sys.exit(f"ERREUR : modèle Whisper introuvable ({modele}).")
    script = None
    if args.script:
        script = [l for l in pathlib.Path(args.script).read_text(encoding="utf-8").splitlines() if l.strip()]

    (projet / "work").mkdir(exist_ok=True)
    wav = projet / "work/prises_audio.wav"
    r = run(["ffmpeg", "-v", "error", "-y", "-i", str(rush), "-map", "0:a:0", "-ar", str(SR), "-ac", "1",
             "-c:a", "pcm_s16le", str(wav)])
    if r.returncode:
        sys.exit(f"ERREUR : son du rush illisible : {r.stderr[-400:]}")
    db = niveaux(wav)
    total = len(db) / 100
    iles = ilots(wav, float(der.get("silenceDb", -40)), float(der.get("islandDuration", 0.18)), total)

    groupes: list[list[tuple[float, float]]] = []
    for a, b in iles:
        if groupes and a - groupes[-1][-1][1] < ECART_PRISES:
            groupes[-1].append((a, b))
        else:
            groupes.append([(a, b)])
    prises = []
    print(f"{len(groupes)} prises dans {rush.name} ({total:.0f} s), transcription une par une…", flush=True)
    with tempfile.TemporaryDirectory() as d:
        for n, g in enumerate(groupes):
            debut, fin = attaque(db, g[0][0]), round(g[-1][1], 3)
            prises.append({"n": n, "debut": debut, "fin": fin,
                           "texte": transcrire(wav, debut, fin, whisper, modele, langue, pathlib.Path(d))})
    choisir(prises, script)

    print(f"\n{'#':>3}  {'début':>7}  {'fin':>7}  {'durée':>5}  statut        texte")
    for p in prises:
        statut = p["statut"] + (f" → #{p['par']}" if p.get("par") is not None else "")
        print(f"{p['n']:>3}  {p['debut']:7.2f}  {p['fin']:7.2f}  {p['fin'] - p['debut']:5.2f}  {statut:<13} {p['texte'][:90]}")
    gardees = [p for p in prises if p["statut"] == "garde"]
    if script:
        manquent, hors = rapport(script, gardees)
        for l, part in manquent:
            print(f"  ⚠️ {'dite en partie' if part >= 0.3 else 'jamais dite'} : « {l.strip()} »")
        for p in hors:
            print(f"  ⚠️ hors script (improvisation ? à garder ou non) : #{p['n']} « {p['texte'][:70]} »")
    print("\nISLANDS proposés (dernière prise propre de chaque phrase) :\nISLANDS = [")
    for p in gardees:
        print(f"    ({p['debut']:.3f}, {p['fin']:.3f}, {p['texte']!r}),")
    print("]")
    (projet / "work/prises.json").write_text(json.dumps(
        [{k: p[k] for k in ("n", "debut", "fin", "texte", "statut") if k in p} | ({"par": p["par"]} if "par" in p else {})
         for p in prises], ensure_ascii=False, indent=1), encoding="utf-8")
    if args.ecrire:
        ecrire(projet, rush, args.nom, gardees, marges(cfg, projet), args.ecraser)


if __name__ == "__main__":
    main()
