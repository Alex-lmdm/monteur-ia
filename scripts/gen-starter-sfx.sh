#!/usr/bin/env bash
# gen-starter-sfx.sh — (re)génère le pack de SFX de démarrage livré dans assets/sfx/starter/.
# Sons 100 % synthétiques (ffmpeg) → originaux, libres de droits, versionnables.
# Usage : bash scripts/gen-starter-sfx.sh
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)/assets/sfx/starter"
mkdir -p "$DIR"
cd "$DIR"

C=(-ac 2 -ar 44100 -c:a libmp3lame -b:a 192k)
FF=(ffmpeg -hide_banner -loglevel error -y)

# clic UI très court (bruit rose filtré, ~35 ms)
"${FF[@]}" -f lavfi -i "anoisesrc=d=0.035:c=pink:a=0.9" \
  -af "highpass=f=2200,afade=t=out:st=0.008:d=0.025,volume=1.2" "${C[@]}" "ui-click.mp3"

# pop : sinus avec chute de hauteur + décroissance rapide
"${FF[@]}" -f lavfi -i "aevalsrc='0.7*sin(2*PI*(1000*t - 4000*t*t))*exp(-t*22)':d=0.16:s=44100" \
  -af "afade=t=out:st=0.13:d=0.03" "${C[@]}" "pop.mp3"

# whoosh : bruit rose qui enfle puis retombe (~0.5 s)
"${FF[@]}" -f lavfi -i "anoisesrc=d=0.5:c=pink:a=0.9" \
  -af "highpass=f=300,lowpass=f=6000,afade=t=in:st=0:d=0.25,afade=t=out:st=0.25:d=0.25,volume=1.3" "${C[@]}" "whoosh.mp3"

# riser : montée de tension avant un reveal (~1 s)
"${FF[@]}" -f lavfi -i "anoisesrc=d=1.0:c=white:a=0.6" \
  -af "highpass=f=600,afade=t=in:st=0:d=0.95,volume=1.6" "${C[@]}" "riser.mp3"

# beep : notification courte
"${FF[@]}" -f lavfi -i "sine=frequency=880:duration=0.13" \
  -af "afade=t=in:st=0:d=0.01,afade=t=out:st=0.09:d=0.04,volume=0.8" "${C[@]}" "beep.mp3"

# impact : petit thud grave (accent sur un mot / apparition)
"${FF[@]}" -f lavfi -i "aevalsrc='0.9*sin(2*PI*120*t)*exp(-t*17)':d=0.26:s=44100" \
  -af "afade=t=out:st=0.22:d=0.04" "${C[@]}" "impact.mp3"

echo "✓ Pack SFX de démarrage régénéré dans $DIR"
ls -1 "$DIR"/*.mp3
