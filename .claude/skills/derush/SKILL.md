---
name: lmdm-derush
description: >-
  Dérush d'un rush brut face-cam d'Alex (LMDM) lu au prompteur : garde la meilleure prise de
  chaque phrase, coupe les blancs et les ratés, nettoie la voix. Use when the user hands a raw
  talking-head video and wants it rough-cut ("dérush", "monte la vidéo brute", "coupe les
  blancs") or its audio cleaned ("améliore l'audio", "le son grésille"). Entrée : un rush brut.
  Sortie : un MP4 1080x1920 serré + une timeline.json, consommée ensuite par lmdm-motion-design.
---

# LMDM — Dérush automatique d'une vidéo brute

Transforme une **vidéo brute face-cam** (Alex lit son script au prompteur, **phrase par phrase**,
avec de longs blancs et des prises **ratées / répétées**) en un **dérush serré** : on garde la
meilleure prise de chaque phrase, on supprime les blancs et les ratés, on nettoie l'audio.

> Prérequis de contexte : **le script final est connu** (vient de `lmdm-reel-script` ou fourni par
> Alex). C'est ce qui rend la sélection de prise fiable — on aligne l'audio sur un texte connu,
> on ne devine pas.

## Principe clé (à ne jamais oublier)

> **Un LLM ne donne JAMAIS de timestamp de coupe fiable.** Le *où couper* vient d'outils
> déterministes (Whisper word/segment + `ffmpeg silencedetect`). Le *quoi garder* vient du
> raisonnement (alignement transcript ↔ script). Les coupes se font **dans les silences**, jamais
> sur un mot.

## Outils / chemins (machine d'Alex)

- `ffmpeg`, `ffprobe`, `whisper-cli` → `/opt/homebrew/bin`
- Modèle Whisper (le meilleur) : `/Users/alexandrecastagna/.cache/hyperframes/whisper/models/ggml-large-v3.bin`
- Script de montage paramétrable : `references/build_derush_template.py`

---

## Pipeline (étape par étape)

Travailler dans `/tmp` puis copier les livrables dans `<projet>/derush/`.

### 1. Inspecter + extraire l'audio

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 "$SRC"
ffmpeg -y -i "$SRC" -ar 16000 -ac 1 -c:a pcm_s16le /tmp/d_audio.wav
```
Note : les vidéos DJI ont souvent un **2ᵉ flux vidéo mjpeg** (vignette) → au montage, mapper
explicitement `[0:v:0]` (le h264) et `[0:a:0]`.

### 2. Détecter les silences (points de coupe réels)

```bash
ffmpeg -i /tmp/d_audio.wav -af silencedetect=noise=-32dB:d=0.3 -f null - 2>&1 | grep silence_
```
→ donne la liste `silence_start` / `silence_end`. Les **îlots de parole** = le complément
(entre `silence_end[i]` et `silence_start[i+1]`). Chaque îlot = une prise candidate.

### 3. Transcrire (segment-level, FIABLE)

```bash
ffmpeg -y -i /tmp/d_audio.wav -af "loudnorm=I=-16:TP=-1.5" -ar 16000 -ac 1 /tmp/d_norm.wav
whisper-cli -m $MODEL -l fr -oj -of /tmp/d_seg /tmp/d_norm.wav
```
⚠️ **NE PAS utiliser `-ml 1 -sow` sur le fichier complet** → ça fait halluciner Whisper sur
cet audio (sortie « Sous-titrage… ST'… 501 »). La segmentation normale transcrit proprement.
`loudnorm` (pré-pass) ne change pas le timing, juste les niveaux → timestamps valides sur la
timeline d'origine.

Parser les segments (`offsets.from/to` en ms + `text`) :
```python
import json
for s in json.load(open('/tmp/d_seg.json'))['transcription']:
    o=s['offsets']; print(f"{o['from']/1000:6.2f}-{o['to']/1000:6.2f}  {s['text'].strip()}")
```

### 4. Sélection des prises (le raisonnement)

Lire la liste segments + silences et, en s'appuyant sur le **script connu** :
- Pour chaque phrase du script, repérer toutes les **prises candidates** (les répétitions).
- **Garder la meilleure** : par défaut la **dernière prise complète et fluide** ; jeter les ratés
  (phrase qui « traîne » avec `...`, mot tronqué, mauvais mot, faux départ).
- Mapper chaque prise gardée à son **îlot de parole** (bornes = silences réels) pour des coupes
  nettes. **Faire confiance aux bornes de silencedetect, pas aux timestamps Whisper** (qui dérivent
  de 1–2 s).
- Jeter aussi les artefacts de fin (« Applaudissements », « Sous-titrage » = hallucinations sur du
  silence/bruit).
- Garder les **ajouts pertinents** improvisés par Alex (ex. « et il m'a généré ces 3 illustrations »
  pour montrer des exemples à l'écran) — les signaler.
- Signaler les **trous éditoriaux** : une phrase du script jamais dite proprement (ex. « le plus
  fou… ») → proposer à Alex de la retourner ou de l'abandonner.

### 5. Construire le montage

Utiliser `references/build_derush_template.py` : y coller la liste `ISLANDS` (start, end, texte) des
prises gardées. Il génère le `filter_complex` (trim/atrim + `scale=1080:1920` + `concat`) et encode.
**Copier le script paramétré (avec ses `ISLANDS` finaux) dans `<projet>/derush/build_derush.py`** :
c'est la trace du montage et il est réutilisable au prochain rebuild.

Préférences calées avec Alex (rythme validé « parfait » le 2026-07-08, Reel « prompts secrets Anthropic ») :
- **Souffle inter-prise ≈ 0,10 s, régulier.** Recette qui tient sans clipper :
  - Bornes des prises = îlots **`silencedetect=noise=-40dB:d=0.18`** (serrés + réguliers). PAS les
    îlots -32 dB de l'étape 2 (qui rognent les fins de voix d'Alex qui baissent → mots tronqués),
    ni -45 dB (trop larges : ~0,07 s de marge muette de chaque côté → 0,24 s, ça traîne).
  - `PAD_START = 0.04`, `PAD_END = 0.02` (**asymétrique**). Retour d'Alex : « **le début est
    parfait, c'est la fin des cuts qui traîne** » → on resserre côté FIN, jamais côté début.
  - ⚠️ Attaques en **voyelle** (« Et », « et », « Mais », « En ») fragiles : un `PAD_START` négatif
    bouffe le début du mot (« Et tout » → « Tout »). Le garder **positif**.
  - Les 2-3 fins de voix les plus basses (ex. « …Claude Code », « …des prompts ») : étendre leur
    `end` juste assez pour ne pas clipper (l'étape 6 le confirme).
  - Cible mesurée : moy ≈ 0,10 s, max ≈ 0,14 s (mesurer les vrais écarts inter-cut en excluant les
    pauses internes aux phrases, qui sont naturelles et à garder).
- Sortie **1080×1920**, `libx264 -crf 20 -preset veryfast`, `aac 192k`, `-r 30000/1001`.
- Coupes **franches** (jump-cut) — elles seront lissées au montage (punch-in zoom / B-roll /
  illustrations + SFX par-dessus).

### 6. VÉRIFIER, écrire la timeline, faire valider à l'oreille (obligatoire)

Le transcript ne suffit pas : Whisper **lisse les bafouillages**, donc un mot doublé peut rester
**audible** alors que la re-transcription le voit propre. Cette étape n'est finie que quand les DEUX
critères sont remplis :

**(a) Re-transcription = le script, mot pour mot** (aucun mot coupé, aucune prise ratée) :
```bash
ffmpeg -y -i /tmp/d_out.mp4 -ar 16000 -ac 1 /tmp/d_check.wav
whisper-cli -m $MODEL -l fr -oj -of /tmp/d_check /tmp/d_check.wav   # puis re-parser
```
De cette re-transcription, **écrire `<projet>/derush/<cut>_timeline.json`** : les timestamps par
phrase sur la timeline du cut. C'est le contrat d'interface avec la suite (sous-titres + beats du
motion design) — le livrable n'existe pas sans ça.

**(b) Le bar final = l'oreille d'Alex.** Livrer explicitement le cut à Alex **pour validation à
l'écoute** : c'est le seul point non automatisable à 100 %. S'il signale un doublon, **zoomer** sur
la zone :
```bash
ffmpeg -y -ss <a> -to <b> -i /tmp/d_audio.wav -ar 16000 -ac 1 /tmp/z.wav
whisper-cli -m $MODEL -l fr -ml 1 -sow -wt 0.01 -oj -of /tmp/z /tmp/z.wav   # mot-à-mot, OK sur slice courte
ffmpeg -ss <a> -to <b> -i /tmp/d_audio.wav -af silencedetect=noise=-44dB:d=0.05 -f null -   # micro-pauses
```
On voit alors les deux occurrences (ex. « et ensuite tu peux lui demander » dit 2×) → ne garder que
la **2ᵉ** (complète), ajuster la borne de l'îlot, rebuild, re-vérifier (a) + (b), régénérer la
timeline.

### 7. Amélioration audio — Adobe Podcast Enhance (hybride)

L'audio brut grésille. Adobe Podcast Enhance donne le meilleur rendu (CapCut sonne mal d'après Alex).

```bash
ffmpeg -y -i <projet>/derush/<cut>.mp4 -vn -c:a libmp3lame -b:a 320k <projet>/derush/<cut>_voice.mp3
open -R <projet>/derush/<cut>_voice.mp3      # révèle le MP3 dans le Finder pour Alex
```
Puis via l'extension Chrome (`mcp__claude-in-chrome__*`) :
1. `navigate` → `https://podcast.adobe.com/fr/enhance` (Alex est déjà connecté à Adobe).
2. **Demander à Alex de glisser le MP3** sur la zone « Optimiser ».
   ⚠️ **L'agent NE PEUT PAS uploader lui-même** : `file_upload` est cassé (refuse les chemins
   disque), et cliquer « Choisir des fichiers » ouvre le **sélecteur natif macOS** que l'extension
   ne peut pas piloter (hors de la page). → l'upload reste manuel (1 glisser).
3. Attendre « Traitement… » → écran de réglages (Voix/Musique/Bruit de fond), version « Optimisée »
   active. Cliquer **« Télécharger »** (bas-droite) → le fichier arrive dans `~/Downloads`
   (nommé `<cut>_voice-optimisé-v2.mp3`).
4. Remux (vidéo intacte + audio amélioré, sync préservé car même durée) :
```bash
cp ~/Downloads/"<cut>_voice-optimisé-v2.mp3" <projet>/derush/<cut>_voice_enhanced.mp3
ffmpeg -y -i <projet>/derush/<cut>.mp4 -i <projet>/derush/<cut>_voice_enhanced.mp3 \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest \
  <projet>/derush/<cut>_enhanced.mp4
```
Toujours vérifier que les durées vidéo/audio matchent (`ffprobe ... format=duration`) avant remux.

**Alternative 100 % locale (zéro geste)**, si un jour Alex veut tout automatiser sans Adobe :
enhancer IA local type `resemble-enhance` (qualité à comparer), ou simple débruitage `ffmpeg`
(`afftdn` / `arnndn` RNNoise) pour juste tuer le grésillement. Adobe reste le défaut tant qu'il est
préféré.

### 7bis. MESURER LES VRAIS POINTS DE COUPE → `<cut>_cuts.json` (OBLIGATOIRE)

> ⛔ **Bug systémique, corrigé le 2026-07-14 (Reel « codes secrets Claude »), déjà vu sur les
> montages précédents.** Symptôme : au passage plein-écran → split, on voit ~0,2 s de la **fin de
> la prise précédente** (Alex regarde ailleurs, il n'a pas encore « attaqué » sa phrase).

**Les frontières de section ne se prennent JAMAIS dans le `timeline.json` Whisper.** Deux erreurs
s'additionnent :
1. **Whisper démarre un segment trop tôt** (~0,1–0,25 s) : il englobe le souffle/silence qui précède
   la parole. La fenêtre du visage s'ouvre donc **avant le jump-cut**.
2. **Dérive d'encodage** : le `concat` ffmpeg arrondit chaque prise à la frame → les bornes RÉELLES
   du fichier livré sont **~+0,07 s** après les bornes théoriques (cumul des `ISLANDS`), et l'écart
   **grandit le long de la timeline** (+0,12 s à la fin sur 19 prises).

**La vérité, c'est le fichier livré.** Un jump-cut est un changement de plan → on le mesure à la
frame près :
```bash
ffmpeg -v error -i <cut>_enhanced.mp4 \
  -filter:v "select='gt(scene,0.015)',metadata=print:file=-" -an -f null - 2>/dev/null | grep pts_time
```
Puis **recaler chaque détection sur la borne théorique la plus proche** (cumul des `ISLANDS`,
tolérance 0,35 s) : ça garantit N-1 coupes, zéro faux positif, zéro oubli. Écrire le résultat dans
**`<cut>_cuts.json`** (une entrée par prise : `start`, `end`, `text`).
Implémentation de référence : `tools/cut_boundaries.py` du projet vidéo.

✅ *Critère* : `len(cuts) == len(ISLANDS)`, bornes croissantes, dernière borne == durée du fichier.

### 8. Livrables (dans `<projet>/derush/`)

- `<cut>_enhanced.mp4` — le dérush final, audio nettoyé, 1080×1920 (étape 7).
- **`<cut>_cuts.json` — les VRAIS points de coupe (étape 7bis). C'est LA source de vérité des
  frontières de section du montage ET des bornes de phrase des sous-titres.**
- `<cut>_timeline.json` — re-transcription du cut (étape 6). Sert à **vérifier le texte**, PAS à
  timer les sections (ses timestamps dérivent — cf 7bis).
- `build_derush.py` — le script de cette vidéo (étape 5 : trace + réutilisable).

---

## Enchaînements

Amont : `lmdm-reel-script` (le script lu au prompteur).
Aval : sous-titres + `lmdm-motion-design` (visuel) + SFX (voir
`/Users/alexandrecastagna/code/video-hyperframes/design-system/sfx-sound-search.md`),
qui consomment la `timeline.json` produite ici.
