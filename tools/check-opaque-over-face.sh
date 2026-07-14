#!/usr/bin/env bash
# Garde anti-regression "visage noir au studio" (cf skill motion-design §14.5).
# Signale tout wrapper video PLEIN CADRE (.face*/.screen*/.illu*) a fond OPAQUE :
# un tel element empile au-dessus du <video> visage le masque dans le studio.
set -u
cd "$(dirname "$0")/.."
hits=$(grep -nE '\.(screen|illu|face)[A-Za-z-]*[^{]*\{[^}]*background[^;}]*:[^;}]*(#[0-9a-fA-F]{3,8}|rgb\()' index.html compositions/*.html 2>/dev/null \
  | grep -viE 'transparent|rgba\([^)]*,\s*0\s*\)')
if [ -n "$hits" ]; then
  echo "❌ Wrapper video plein cadre a fond OPAQUE (masque le visage dans le studio) :"
  echo "$hits"
  echo "→ Mettre background:transparent (seul #bgbase track 0 peut etre opaque). Cf skill §14.5."
  exit 1
fi
echo "✅ Aucun wrapper video opaque au-dessus du visage."
