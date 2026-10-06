#!/usr/bin/env python3
"""ETAPE 6 — SFX + musique, poses DANS le montage (export natif : bouton Export de l'app).

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE REEL.                                           ║
║  - La MUSIQUE vient de brand.config.json -> audio.musicFile + audio.musicDb.   ║
║    Optionnelle : sans musique (premiere video), seuls les SFX sont poses.     ║
║  - Les SFX sont les fichiers de assets/sfx/ (dossier Monteur IA) ET de ses     ║
║    sous-dossiers (starter/, pack/...) : on les nomme par chemin relatif, ex.   ║
║    starter/pop.mp3. Un son du Reel (trouve dans l'app par find_sound_effect,   ║
║    ou depose dans le Reel) se nomme "assets/<fichier>".                        ║
║  - Musique propre a CE Reel (find_music) : MUSIQUE_REEL, plus bas.             ║
║  - Le MAPPING/PLACEMENT (quel SFX, a quel instant, a quel volume) est PILOTE   ║
║    PAR L'AGENT : remplis la liste EVENTS ci-dessous, un evenement par SFX.     ║
║ La demo place un SFX de transition sur chaque frontiere de section — c'est un  ║
║ EXEMPLE de structure, remplace-le par le placement de TON Reel.                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage (depuis le dossier du Reel) :
    python3 tools/build_sfx.py              # pose SFX + musique dans index.html (bloc SONS)
    python3 tools/build_sfx.py --ecraser    # idem, meme si les sons ont ete retouches a la main
    python3 tools/build_sfx.py --probe      # piste SFX+musique SEULE en WAV, pour verifier sans ecouter
    python3 tools/build_sfx.py --ffmpeg     # ancien export : remixe exports/FINAL.mp4 (secours)

Pose native : chaque son est copie dans assets/sons/ (un son deja dans assets/ du Reel reste ou
il est) puis ecrit en <audio> dans le bloc SONS du master, avec les memes reglages que l'ancien mixage ffmpeg : volume en dB, coupe adoucie (60 ms),
musique avec fondus (0.4 s / 1.2 s) et un plafond (limiteur) sur tout le mix, voix comprise. Dans
l'app HyperFrames, chaque son devient un clip de la timeline (deplacable, volume reglable) et le
bouton Export sort la video complete. Retouches faites a la main ou dans l'app : elles sont
protegees, l'outil refuse de les ecraser sans --ecraser (empreinte du bloc).

Regles generales (skill motion-design / references/sfx-musique.md) :
  - Musique en fond, toute la duree, -26.5 dB par defaut (fade in 0.4 / out 1.2).
  - Volumes SFX REEQUILIBRES par niveau PERCU (pas un dB uniforme : la frappe clavier et les
    clics sont inaudibles au meme dB qu'un riser).
  - Les temps s'appuient sur sections (les VRAIES coupes) + les timelines GSAP des sections.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections
from lieux import MAISON  # réglages, SFX et musique partagés par tous les Reels

ROOT = pathlib.Path(__file__).resolve().parent.parent
SFX_DIR = MAISON / "assets/sfx"
MUSIC_DIR = MAISON / "assets/music"
SRC = ROOT / "exports/FINAL.mp4"          # ancien export (--ffmpeg) : video sans SFX
OUT = ROOT / "exports/FINAL_SFX_MUSIC.mp4"
FONDU_COUPE, FONDU_ENTREE, FONDU_SORTIE = 0.06, 0.4, 1.2

SEC = sections.sections()
DUR = sections.DURATION


def die(msg):
    print("ERREUR :", msg)
    sys.exit(1)


def load_config():
    for name in ("brand.config.json", "brand.config.example.json"):
        p = MAISON / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    die("aucun brand.config.json ni brand.config.example.json trouve : lance /setup.")


CFG = load_config()

# --- SFX disponibles ---------------------------------------------------------------------------
# Racine ET sous-dossiers : la bibliotheque de demarrage vit dans starter/. Chemins relatifs a
# assets/sfx/ (ex. "starter/whoosh.mp3"), c'est ce qu'on ecrit dans EVENTS.
available = sorted(p.relative_to(SFX_DIR).as_posix() for p in SFX_DIR.rglob("*")
                   if p.is_file() and p.suffix.lower() in (".mp3", ".wav", ".m4a", ".aif", ".aiff"))
if not available:
    die(f"aucun SFX dans {SFX_DIR.relative_to(MAISON)} : depose tes effets (cf assets/sfx/README.md).")

# =============================================================================
# A REMPLIR PAR L'AGENT.
# MUSIQUE_REEL : musique de CE Reel seulement (ex. trouvee dans l'app par find_music, arrivee dans
#   assets/ du Reel : "assets/<fichier>"). None = la musique de la marque (brand.config.json ->
#   audio.musicFile). MUSIQUE_REEL_DB : son volume (None = audio.musicDb).
# EVENTS = (fichier_sfx, start_s, volume_dB, trim|None) :
#   fichier_sfx : chemin relatif a assets/sfx/ du dossier Monteur IA (ex. "starter/pop.mp3"),
#                 "assets/<fichier>" pour un son du Reel (find_sound_effect), ou chemin absolu.
#   start_s : debut du son. Son trouve dans l'app : instant vise MOINS son peakOffset.
#   volume_dB : un son de l'app n'est pas calibre, mesure-le (references/sfx-musique.md).
#   trim : None, une duree (on garde 0 -> trim), ou un tuple (t0, t1) (on garde t0 -> t1).
# Ci-dessous : un EXEMPLE generique — un SFX de transition sur chaque debut de section
# (sauf la premiere). On alterne les SFX disponibles pour ne jamais jouer 2x le meme d'affilee.
# =============================================================================
MUSIQUE_REEL = None
MUSIQUE_REEL_DB = None

events = []
transitions = [s["start"] for s in SEC[1:]]
for i, t in enumerate(transitions):
    events.append((available[i % len(available)], round(t, 3), -20, 0.45))

events.sort(key=lambda e: e[1])


def sfx_path(f):
    p = pathlib.Path(f)
    if p.is_absolute():
        return p
    return ROOT / p if p.parts[0] == "assets" else SFX_DIR / p


# --- musique : celle du Reel (MUSIQUE_REEL), sinon celle de la marque (brand.config.json) ---------
audio = CFG.get("audio") or {}
music_file = MUSIQUE_REEL or audio.get("musicFile")
music_db = MUSIQUE_REEL_DB if MUSIQUE_REEL_DB is not None else audio.get("musicDb", -26.5)
MUSIC = None
if MUSIQUE_REEL:
    MUSIC = sfx_path(MUSIQUE_REEL) if pathlib.Path(MUSIQUE_REEL).parts[0] == "assets" else MUSIC_DIR / MUSIQUE_REEL
    if not MUSIC.exists():
        die(f"musique du Reel introuvable : {MUSIQUE_REEL} (MUSIQUE_REEL dans tools/build_sfx.py).")
elif music_file:
    MUSIC = MUSIC_DIR / music_file
    if not MUSIC.exists():
        die(f"musique introuvable : {MUSIC.relative_to(MAISON)} (verifie audio.musicFile dans brand.config.json).")
else:
    print("Pas de musique (audio.musicFile vide) : SFX seuls, sur la voix.")


def trim_bounds(trim):
    if not trim:
        return None
    return (float(trim[0]), float(trim[1])) if isinstance(trim, (tuple, list)) else (0.0, float(trim))


# =============================================================================
# POSE NATIVE (defaut) : bloc SONS dans index.html, par le module partage tools/sons.py
# =============================================================================
def poser():
    import sons
    evs = []
    for f, start, vol, trim in events:
        bornes = trim_bounds(trim)
        evs.append({"src": sfx_path(f), "start": start, "vol": vol, "trim": bornes,
                    "fondu_sortie": FONDU_COUPE if bornes else 0})
    try:
        sons.poser(ROOT, evs, musique=MUSIC, musique_db=music_db, total=DUR, sfx_dir=SFX_DIR,
                   ecraser="--ecraser" in sys.argv)
    except sons.Erreur as e:
        die(str(e))
    print(f"{len(events)} SFX + " + (f"musique ({music_file} @ {music_db} dB)" if MUSIC else "sans musique")
          + " poses dans index.html (bloc SONS, copies dans assets/sons/)")
    for f, s, v, t in events:
        print(f"  {s:6.2f}  {v:>4} dB  {f}{'  (trim ' + str(t) + ')' if t else ''}")
    print("Export : bouton Export de l'app HyperFrames, ou npm run render (exports/FINAL.mp4).")


# =============================================================================
# ANCIEN MIXAGE ffmpeg (--ffmpeg, et --probe pour verifier sans ecouter)
# =============================================================================
def filtres_sfx_musique(premier_index):
    inputs, filters, mixin = [], [], []
    for i, (f, start, vol, trim) in enumerate(events, start=premier_index):
        inputs += ["-i", str(sfx_path(f))]
        ch = f"[{i}:a]"
        bornes = trim_bounds(trim)
        if bornes:
            t0, t1 = bornes
            keep = t1 - t0
            ch_f = (f"atrim={t0}:{t1},asetpts=PTS-STARTPTS,volume={vol}dB,"
                    f"aformat=channel_layouts=stereo:sample_rates=48000,"
                    f"afade=t=out:st={max(keep - FONDU_COUPE, 0):.3f}:d={FONDU_COUPE},adelay={int(start * 1000)}:all=1")
        else:
            ch_f = (f"volume={vol}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                    f"adelay={int(start * 1000)}:all=1")
        filters.append(f"{ch}{ch_f}[e{i}]")
        mixin.append(f"[e{i}]")
    if MUSIC:
        mi = premier_index + len(events)
        inputs += ["-i", str(MUSIC)]
        filters.append(f"[{mi}:a]atrim=0:{DUR},volume={music_db}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                       f"afade=t=in:st=0:d={FONDU_ENTREE},afade=t=out:st={DUR - FONDU_SORTIE:.3f}:d={FONDU_SORTIE}[music]")
        mixin.append("[music]")
    return inputs, filters, mixin


def ffmpeg_ou_probe():
    # --probe : ecrit la piste SFX+musique SEULE (sans la voix) en WAV 48 kHz, pour VERIFIER LE
    # PLACEMENT SANS ECOUTER. Comparer ensuite le pic de chaque evenement au pic de la musique de
    # fond (viser +4 dB minimum) ; sans musique, le comparer au niveau de la voix (chaque SFX
    # audible mais sous la voix). Deux methodes qui MENTENT, a ne pas utiliser :
    #   - soustraire le MP4 final et le MP4 sans SFX : deux encodages AAC independants laissent
    #     l'erreur de quantification de la voix (~-6 dB), tres au-dessus des SFX -> inexploitable ;
    #   - mesurer en 16 kHz : coupe au-dessus de 8 kHz et sous-estime massivement risers et clics
    #     (qui vivent dans les aigus) -> on croit un SFX absent alors qu'il est bien la.
    if "--probe" in sys.argv:
        inputs, filters, mixin = filtres_sfx_musique(0)
        filters.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:dropout_transition=0[aout]")
        probe_out = ROOT / "work/sfx-only.wav"
        probe_out.parent.mkdir(exist_ok=True)
        r = subprocess.run(["ffmpeg", "-y", "-v", "error"] + inputs +
                           ["-filter_complex", ";".join(filters), "-map", "[aout]",
                            "-ar", "48000", "-ac", "1", str(probe_out)],
                           capture_output=True, encoding="utf-8", errors="replace")
        print("probe exit:", r.returncode, "->", probe_out.relative_to(ROOT))
        if r.returncode:
            print(r.stderr[-1200:])
        raise SystemExit(0 if r.returncode == 0 else 1)

    if not SRC.exists():
        die(f"{SRC.relative_to(ROOT)} manquant : rends d'abord la video finale (python3 tools/build_final.py).")
    inputs, filters, mixin = filtres_sfx_musique(1)
    filters.append(f"[0:a]{''.join(mixin)}amix=inputs={len(mixin) + 1}:normalize=0:dropout_transition=0,"
                   f"alimiter=limit=0.97[aout]")
    cmd = (["ffmpeg", "-y", "-v", "error", "-i", str(SRC)] + inputs +
           ["-filter_complex", ";".join(filters), "-map", "0:v", "-c:v", "copy",
            "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    print("ffmpeg exit:", r.returncode)
    if r.returncode:
        print(r.stderr[-1200:])
        raise SystemExit(1)
    print(f"{len(events)} SFX + " + (f"musique ({music_file} @ {music_db} dB)" if MUSIC else "sans musique")
          + f" -> {OUT.relative_to(ROOT)}")


if "--ffmpeg" in sys.argv or "--probe" in sys.argv:
    ffmpeg_ou_probe()
else:
    poser()
