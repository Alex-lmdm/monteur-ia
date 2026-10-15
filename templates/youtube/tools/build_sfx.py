#!/usr/bin/env python3
"""SONS d'une vidéo YouTube : SFX et musique posés DANS le montage (export natif : bouton Export).

╔══════════════════════════════════════════════════════════════════════════════╗
║ CE FICHIER EST ADAPTE A CHAQUE VIDEO : remplis EVENTS (un évènement par SFX).  ║
║  - La MUSIQUE vient de brand.config.json -> youtube.musicFile (sinon           ║
║    audio.musicFile), au volume youtube.musicDb (-30 dB par défaut : plus bas   ║
║    que dans un Reel, la voix porte une vidéo longue). Optionnelle.             ║
║  - Les SFX sont ceux de assets/sfx/ du dossier Monteur IA (starter/, pack/…),  ║
║    nommés par chemin relatif (ex. "starter/whoosh.mp3"), ou "assets/<fichier>" ║
║    pour un son de la vidéo (trouvé dans l'app par find_sound_effect).          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage (depuis le dossier de la vidéo) :
    python3 tools/build_sfx.py              # pose SFX + musique dans index.html (bloc SONS)
    python3 tools/build_sfx.py --ecraser    # idem, même si les sons ont été retouchés à la main
    python3 tools/build_sfx.py --probe      # piste SFX + musique SEULE (work/sfx-only.wav, 48 kHz)

Le module partagé tools/sons.py pose chaque son en <audio> dans le bloc SONS du master, puis
amène tout le mixage (voix comprise) à -14 LUFS, le niveau que YouTube garde, crêtes sous -1 dBTP.

Règles YouTube (skill youtube, references/doctrine.md §6) : des sons RARES, sur les gestes qui
changent l'écran (le créateur qui glisse, un plein écran qui arrive, une révélation), jamais sur
chaque coupe. Un whoosh à chaque coupe, sur 15 minutes, fatigue en deux minutes.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from lieux import MAISON, config  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SFX_DIR = MAISON / "assets/sfx"
MUSIC_DIR = MAISON / "assets/music"
FONDU_COUPE = 0.06
SEC = sections.sections()
DUR = sections.DURATION
CFG = config()
YT = CFG.get("youtube") or {}


def die(msg):
    print("ERREUR :", msg)
    sys.exit(1)


available = sorted(p.relative_to(SFX_DIR).as_posix() for p in SFX_DIR.rglob("*")
                   if p.is_file() and p.suffix.lower() in (".mp3", ".wav", ".m4a", ".aif", ".aiff"))

# =============================================================================
# A REMPLIR PAR L'AGENT.
# MUSIQUE_VIDEO : musique de CETTE vidéo seulement ("assets/<fichier>" si trouvée dans l'app par
#   find_music). None = celle de la marque. MUSIQUE_VIDEO_DB : son volume (None = youtube.musicDb).
# EVENTS = (fichier_sfx, start_s, volume_dB, trim|None) :
#   start_s : l'instant du geste (début d'une section, d'un tween), lu dans sections.py ou la compo ;
#   volume_dB : rééquilibré par niveau PERÇU (references/sfx-musique.md du skill motion-design) ;
#   trim : None, une durée (on garde 0 -> trim), ou (t0, t1).
# Ci-dessous : un EXEMPLE, un son discret à l'entrée de chaque panneau et de chaque plein écran.
# =============================================================================
MUSIQUE_VIDEO = None
MUSIQUE_VIDEO_DB = None

events = []
for i, s in enumerate([s for s in SEC[1:] if s["fmt"] in ("cote", "full")]):
    if available:
        events.append((available[i % len(available)], s["start"], -22, 0.45))
events.sort(key=lambda e: e[1])


def sfx_path(f):
    p = pathlib.Path(f)
    if p.is_absolute():
        return p
    return ROOT / p if p.parts[0] == "assets" else SFX_DIR / p


music_file = MUSIQUE_VIDEO or YT.get("musicFile") or (CFG.get("audio") or {}).get("musicFile")
music_db = MUSIQUE_VIDEO_DB if MUSIQUE_VIDEO_DB is not None else YT.get("musicDb", -30)
MUSIC = None
if music_file:
    MUSIC = sfx_path(music_file) if pathlib.Path(music_file).parts[0] == "assets" else MUSIC_DIR / music_file
    if not MUSIC.exists():
        die(f"musique introuvable : {music_file} (youtube.musicFile ou audio.musicFile dans brand.config.json).")
else:
    print("Pas de musique (youtube.musicFile et audio.musicFile vides) : SFX seuls, sur la voix.")


def trim_bounds(trim):
    if not trim:
        return None
    return (float(trim[0]), float(trim[1])) if isinstance(trim, (tuple, list)) else (0.0, float(trim))


def poser():
    import sons
    evs = []
    for f, start, vol, trim in events:
        bornes = trim_bounds(trim)
        evs.append({"src": sfx_path(f), "start": start, "vol": vol, "trim": bornes,
                    "fondu_sortie": FONDU_COUPE if bornes else 0})
    try:
        rapport = sons.poser(ROOT, evs, musique=MUSIC, musique_db=music_db, total=DUR, sfx_dir=SFX_DIR,
                             ecraser="--ecraser" in sys.argv)
    except sons.Erreur as e:
        die(str(e))
    print(f"{len(events)} SFX + " + (f"musique ({music_file} @ {music_db} dB)" if MUSIC else "sans musique")
          + " posés dans index.html (bloc SONS, copies dans assets/sons/)")
    for f, s, v, t in events:
        print(f"  {sections._mmss(s)} {s:8.2f}  {v:>4} dB  {f}{'  (trim ' + str(t) + ')' if t else ''}")
    print(sons.resume_niveau(rapport))
    print("Export : bouton Export de l'app HyperFrames, ou npm run render (exports/FINAL.mp4).")


def probe():
    """Piste SFX + musique SEULE, en WAV 48 kHz : vérifier le placement sans écouter (pic de chaque
    son au moins 4 dB au-dessus de la musique). Jamais en 16 kHz : les aigus des sons disparaissent."""
    inputs, filters, mixin = [], [], []
    for i, (f, start, vol, trim) in enumerate(events):
        inputs += ["-i", str(sfx_path(f))]
        bornes = trim_bounds(trim)
        coupe = f"atrim={bornes[0]}:{bornes[1]},asetpts=PTS-STARTPTS," if bornes else ""
        filters.append(f"[{i}:a]{coupe}volume={vol}dB,aformat=channel_layouts=stereo:sample_rates=48000,"
                       f"adelay={int(start * 1000)}:all=1[e{i}]")
        mixin.append(f"[e{i}]")
    if MUSIC:
        inputs += ["-stream_loop", "-1", "-i", str(MUSIC)]
        filters.append(f"[{len(events)}:a]atrim=0:{DUR},volume={music_db}dB,"
                       "aformat=channel_layouts=stereo:sample_rates=48000[music]")
        mixin.append("[music]")
    if not mixin:
        die("aucun son à vérifier (EVENTS vide, pas de musique).")
    filters.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:dropout_transition=0[aout]")
    out = ROOT / "work/sfx-only.wav"
    out.parent.mkdir(exist_ok=True)
    r = subprocess.run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filters),
                        "-map", "[aout]", "-ar", "48000", "-ac", "1", str(out)],
                       capture_output=True, encoding="utf-8", errors="replace")
    print("probe exit:", r.returncode, "->", out.relative_to(ROOT))
    if r.returncode:
        print(r.stderr[-1200:])
    raise SystemExit(0 if r.returncode == 0 else 1)


if __name__ == "__main__":
    if not available and events:
        die(f"aucun SFX dans {SFX_DIR.relative_to(MAISON)} : dépose tes effets (cf assets/sfx/README.md).")
    probe() if "--probe" in sys.argv else poser()
