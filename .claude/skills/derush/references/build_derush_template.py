#!/usr/bin/env python3
"""
Template de montage dérush LMDM.
Remplir SRC, OUT et la liste ISLANDS (prises gardees, bornes = silences reels).
Genere le filter_complex (trim/atrim + scale + concat) et encode.

Workflow :
  1. silencedetect -32dB d=0.3  -> bornes des ilots de parole
  2. whisper segments           -> texte de chaque ilot
  3. selection de prise (script connu) -> remplir ISLANDS ci-dessous
  4. python3 build_derush.py
  5. re-transcrire OUT pour verifier (aucun mot coupe / aucune prise ratee)
"""
import subprocess

SRC = "/CHEMIN/VERS/video_brute.MP4"
OUT = "/tmp/derush.mp4"

# (start_sec, end_sec, texte)  -- une prise gardee par ligne, dans l'ordre final.
# start/end = bornes de l'ilot de parole (silence_end -> silence_start).
ISLANDS = [
    # (4.99, 7.61, "Premiere phrase ..."),
    # (33.94, 37.22, "Deuxieme phrase ..."),
]

PAD_START = 0.04   # debut : garder l'elan d'attaque (ne jamais rogner -> negatif bouffe les voyelles)
PAD_END   = 0.02   # fin : resserree (retour Alex). Bornes sur ilots -40dB:d=0.18 -> ~0.10s inter-cut
SCALE     = "1080:1920"
FPS       = "30000/1001"

parts, concat_in, kept = [], "", 0.0
for i, (s, e, _txt) in enumerate(ISLANDS):
    a = max(s - PAD_START, 0.0); b = e + PAD_END; kept += (b - a)
    parts.append(f"[0:v:0]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,scale={SCALE}[v{i}];")
    parts.append(f"[0:a:0]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}];")
    concat_in += f"[v{i}][a{i}]"
filtg = "".join(parts) + f"{concat_in}concat=n={len(ISLANDS)}:v=1:a=1[v][a]"

cmd = ["ffmpeg", "-y", "-i", SRC, "-filter_complex", filtg,
       "-map", "[v]", "-map", "[a]", "-r", FPS,
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", OUT]

print(f"Prises : {len(ISLANDS)}  |  duree estimee : {kept:.1f}s")
r = subprocess.run(cmd, capture_output=True, text=True)
print("ffmpeg exit:", r.returncode)
if r.returncode:
    print(r.stderr[-1500:])
