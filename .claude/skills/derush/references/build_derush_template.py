#!/usr/bin/env python3
"""
Template de montage derush.
Remplir SRC, OUT et la liste ISLANDS (prises gardees, bornes = silences reels).
Genere le filter_complex (trim/atrim + concat) et encode, SANS reduire la resolution du rush.
Valeurs par defaut (PAD_START/PAD_END/silenceDb/islandDuration) = brand.config.json -> derush.

Workflow :
  1. silencedetect (derush.silenceDb / derush.islandDuration)  -> bornes des ilots de parole
  2. whisper segments (derush.whisperLanguage)                 -> texte de chaque ilot
  3. selection de prise (script connu) -> remplir ISLANDS ci-dessous
  4. python3 build_derush.py
  5. re-transcrire OUT pour verifier (aucun mot coupe / aucune prise ratee)
"""
import subprocess

SRC = "CHEMIN/VERS/video_brute.MP4"   # relatif a la racine du projet, ou absolu
OUT = "work/derush.mp4"               # dossier de travail du projet (cross-platform)

# (start_sec, end_sec, texte)  -- une prise gardee par ligne, dans l'ordre final.
# start/end = bornes de l'ilot de parole (silence_end -> silence_start).
ISLANDS = [
    # (4.99, 7.61, "Premiere phrase ..."),
    # (33.94, 37.22, "Deuxieme phrase ..."),
]

PAD_START = 0.04   # brand.config.json -> derush.padStart. Debut : garder l'elan d'attaque (negatif bouffe les voyelles)
PAD_END   = 0.02   # brand.config.json -> derush.padEnd. Fin : resserree. Bornes sur ilots -40dB:d=0.18 -> ~0.10s inter-cut
PAD_FIN   = 0.30   # la DERNIERE prise : aucune coupe apres elle, la voix retombe en entier (sinon le dernier mot est coupe)
FPS       = "30000/1001"
# PLEINE RESOLUTION, quasi sans perte : a l'export, le visage est recadre DANS ce fichier puis
# agrandi (tools/build_final.py). Reduire ici en 1080x1920 (ancien reglage, crf 20 veryfast)
# ne laissait qu'un tiers du detail du visage ; garde tel quel, il en conserve ~80 %.
# Le passage en 1080x1920 pour le studio se fait plus tard (base.mp4, motion-design etape 3).
CRF       = 14
# veryfast : fichier intermediaire, deux fois moins de calcul que le reglage par defaut (mesure sur
# un rush DJI 4K : 510 s de processeur au lieu de 944), image identique a l'oeil (PSNR 50 dB).
PRESET    = "veryfast"
# RACCORD : deux prises qui se touchent apres les marges (fin + PAD_END == debut suivant - PAD_START)
# sont UNE seule prise du rush partagee en deux, pour changer de cadre sur un mot au montage
# (« comme la », « offert »). Elles sont montees d'un seul tenant : aucune coupe, ni dans l'image
# ni dans le son. Le partage ne vit que dans <cut>_cuts.json (tools/cut_boundaries.py).
RACCORD   = 0.005

segs = []
for k, (s, e, _txt) in enumerate(ISLANDS):
    a = max(s - PAD_START, 0.0); b = e + (PAD_FIN if k == len(ISLANDS) - 1 else PAD_END)
    if segs and a < segs[-1][1] - RACCORD:
        raise SystemExit(f"prises qui se chevauchent vers {a:.2f} s : le son serait double. "
                         "Pour un raccord, fin + PAD_END doit egaler debut suivant - PAD_START.")
    if segs and a <= segs[-1][1] + RACCORD:
        segs[-1][1] = b
    else:
        segs.append([a, b])

parts, concat_in, kept = [], "", 0.0
for i, (a, b) in enumerate(segs):
    kept += (b - a)
    parts.append(f"[0:v:0]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}];")
    parts.append(f"[0:a:0]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}];")
    concat_in += f"[v{i}][a{i}]"
filtg = "".join(parts) + f"{concat_in}concat=n={len(segs)}:v=1:a=1[v][a]"

cmd = ["ffmpeg", "-y", "-i", SRC, "-filter_complex", filtg,
       "-map", "[v]", "-map", "[a]", "-r", FPS,
       "-c:v", "libx264", "-preset", PRESET, "-crf", str(CRF), "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", OUT]

raccords = len(ISLANDS) - len(segs)
print(f"Prises : {len(ISLANDS)}" + (f" (dont {raccords} raccord(s) sans coupe)" if raccords else "")
      + f"  |  duree estimee : {kept:.1f}s")
r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
print("ffmpeg exit:", r.returncode)
if r.returncode:
    print(r.stderr[-1500:])
