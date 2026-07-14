---
name: derush
description: >-
  Dérush d'un rush brut face-cam lu au prompteur : garde la meilleure prise de chaque phrase, coupe
  les blancs et les ratés, nettoie la voix. Use when the user hands a raw talking-head video and
  wants it rough-cut ("dérush", "monte la vidéo brute", "coupe les blancs") or its audio cleaned
  ("améliore l'audio", "le son grésille"). Entrée : un rush brut. Sortie : un MP4 1080x1920 serré
  + une timeline.json, consommée ensuite par le skill motion-design.
---
<!-- Copie générée — éditer .claude/skills/derush/ puis npm run sync -->

# Dérush automatique d'une vidéo brute

Transforme une **vidéo brute face-cam** (le créateur lit son script au prompteur, **phrase par
phrase**, avec de longs blancs et des prises **ratées / répétées**) en un **dérush serré** : on garde
la meilleure prise de chaque phrase, on supprime les blancs et les ratés, on nettoie l'audio.

> Prérequis de contexte : **le script final est connu** (vient du skill `reel-script` ou fourni par le
> créateur). C'est ce qui rend la sélection de prise fiable — on aligne l'audio sur un texte connu, on
> ne devine pas.

## Principe clé (à ne jamais oublier)

> **Un LLM ne donne JAMAIS de timestamp de coupe fiable.** Le *où couper* vient d'outils
> déterministes (Whisper word/segment + `ffmpeg silencedetect`). Le *quoi garder* vient du
> raisonnement (alignement transcript ↔ script). Les coupes se font **dans les silences**, jamais
> sur un mot.

## Outils / chemins → `brand.config.json` → `env`

Tous les binaires et le modèle Whisper se lisent dans `brand.config.json` → `env`
(`env.ffmpegPath`, `env.whisperCli`, `env.whisperModel`, `env.os`). Ne jamais coder un chemin en dur.

- **`ffmpeg` / `ffprobe`** : `env.ffmpegPath`
  - macOS : le dossier `bin` de Homebrew (le trouver avec `which ffmpeg`) — Windows : `C:\ffmpeg\bin`
    (ou dossier ajouté au PATH)
- **`whisper-cli`** : `env.whisperCli`
  - macOS : dans le `bin` de Homebrew (`which whisper-cli`) — Windows : `C:\tools\whisper\whisper-cli.exe`
- **Modèle Whisper** : `env.whisperModel`
  - **Défaut recommandé : `ggml-large-v3-turbo`** (plus léger, rapide, quasi aussi précis).
    Alternative haute qualité : `ggml-large-v3` (plus lourd).
  - macOS : `~/.cache/hyperframes/whisper/models/ggml-large-v3-turbo.bin`
  - Windows : `%USERPROFILE%\.cache\hyperframes\whisper\models\ggml-large-v3-turbo.bin`
- **Langue de transcription** : `brand.config.json` → `derush.whisperLanguage` (noté `<LANG>` ci-dessous).
- Script de montage paramétrable : `references/build_derush_template.py`.

> Les exemples ci-dessous utilisent des chemins courts (`ffmpeg`, `whisper-cli`, `$MODEL`). Sur ta
> machine, préfixer par `env.ffmpegPath` / `env.whisperCli` si les binaires ne sont pas dans le PATH.

---

## Pipeline (étape par étape)

Travailler dans le dossier de travail du projet **`work/`** (cross-platform) puis copier les livrables
dans `<projet>/derush/`.

### 1. Inspecter + extraire l'audio

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 "$SRC"
ffmpeg -y -i "$SRC" -ar 16000 -ac 1 -c:a pcm_s16le work/d_audio.wav
```
Note (conditionnelle sur `brand.config.json` → `derush.camera`) : certaines caméras (ex. **DJI**)
exposent un **2ᵉ flux vidéo mjpeg** (vignette) → au montage, mapper explicitement `[0:v:0]` (le h264)
et `[0:a:0]`. Si `derush.camera` n'est pas une caméra à double flux, ignorer.

### 2. Détecter les silences (points de coupe réels)

```bash
ffmpeg -i work/d_audio.wav -af silencedetect=noise=-32dB:d=0.3 -f null - 2>&1 | grep silence_
```
→ donne la liste `silence_start` / `silence_end`. Les **îlots de parole** = le complément
(entre `silence_end[i]` et `silence_start[i+1]`). Chaque îlot = une prise candidate.

### 3. Transcrire (segment-level, FIABLE)

```bash
ffmpeg -y -i work/d_audio.wav -af "loudnorm=I=-16:TP=-1.5" -ar 16000 -ac 1 work/d_norm.wav
whisper-cli -m $MODEL -l <LANG> -oj -of work/d_seg work/d_norm.wav
```
⚠️ **NE PAS utiliser `-ml 1 -sow` sur le fichier complet** → ça fait halluciner Whisper sur cet audio
(sortie de bruit / phrases parasites). La segmentation normale transcrit proprement. `loudnorm`
(pré-pass) ne change pas le timing, juste les niveaux → timestamps valides sur la timeline d'origine.

Parser les segments (`offsets.from/to` en ms + `text`) :
```python
import json
for s in json.load(open('work/d_seg.json'))['transcription']:
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
- Jeter aussi les artefacts de fin (hallucinations Whisper sur du silence/bruit).
- Garder les **ajouts pertinents** improvisés par le créateur (ex. « et regarde ces exemples » pour
  montrer des visuels à l'écran) — les signaler.
- Signaler les **trous éditoriaux** : une phrase du script jamais dite proprement → proposer au
  créateur de la retourner ou de l'abandonner.

### 5. Construire le montage

Utiliser `references/build_derush_template.py` : y coller la liste `ISLANDS` (start, end, texte) des
prises gardées. Il génère le `filter_complex` (trim/atrim + `scale=1080:1920` + `concat`) et encode.
**Copier le script paramétré (avec ses `ISLANDS` finaux) dans `<projet>/derush/build_derush.py`** :
c'est la trace du montage et il est réutilisable au prochain rebuild.

Préférences de pacing — **valeurs par défaut recommandées, lues depuis `brand.config.json` →
`derush`** (`padStart`, `padEnd`, `silenceDb`, `islandDuration`). Ne pas re-tuner au jugé :
- **Souffle inter-prise ≈ 0,10 s, régulier.** Recette qui tient sans clipper :
  - Bornes des prises = îlots **`silencedetect=noise=<derush.silenceDb>:d=<derush.islandDuration>`**
    (défaut **-40 dB / d=0.18** : serrés + réguliers). PAS les îlots -32 dB de l'étape 2 (qui rognent
    les fins de voix qui baissent → mots tronqués), ni -45 dB (trop larges : ~0,07 s de marge muette
    de chaque côté → ça traîne).
  - `PAD_START = <derush.padStart>` (défaut **0.04**), `PAD_END = <derush.padEnd>` (défaut **0.02**),
    **asymétrique**. Retour terrain : « le début est parfait, c'est la fin des cuts qui traîne » → on
    resserre côté FIN, jamais côté début.
  - ⚠️ Attaques en **voyelle** (« Et », « Mais », « En »…) fragiles : un `PAD_START` négatif bouffe le
    début du mot. Le garder **positif**.
  - Les 2-3 fins de voix les plus basses : étendre leur `end` juste assez pour ne pas clipper
    (l'étape 6 le confirme).
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
ffmpeg -y -i work/d_out.mp4 -ar 16000 -ac 1 work/d_check.wav
whisper-cli -m $MODEL -l <LANG> -oj -of work/d_check work/d_check.wav   # puis re-parser
```
De cette re-transcription, **écrire `<projet>/derush/<cut>_timeline.json`** : les timestamps par
phrase sur la timeline du cut. C'est le contrat d'interface avec la suite (sous-titres + beats du
motion design) — le livrable n'existe pas sans ça.

**(b) Le bar final = l'oreille du créateur.** Livrer explicitement le cut **pour validation à
l'écoute** : c'est le seul point non automatisable à 100 %. S'il signale un doublon, **zoomer** sur
la zone :
```bash
ffmpeg -y -ss <a> -to <b> -i work/d_audio.wav -ar 16000 -ac 1 work/z.wav
whisper-cli -m $MODEL -l <LANG> -ml 1 -sow -wt 0.01 -oj -of work/z work/z.wav   # mot-à-mot, OK sur slice courte
ffmpeg -ss <a> -to <b> -i work/d_audio.wav -af silencedetect=noise=-44dB:d=0.05 -f null -   # micro-pauses
```
On voit alors les deux occurrences → ne garder que la **dernière** (complète), ajuster la borne de
l'îlot, rebuild, re-vérifier (a) + (b), régénérer la timeline.

### 7. Amélioration audio → `brand.config.json` → `audio.enhanceMethod`

L'audio brut grésille. Deux variantes documentées ; le choix vient de `audio.enhanceMethod`.

D'abord, extraire la voix du cut :
```bash
ffmpeg -y -i <projet>/derush/<cut>.mp4 -vn -c:a libmp3lame -b:a 320k <projet>/derush/<cut>_voice.mp3
```

#### Variante `adobe` — Adobe Podcast Enhance (manuel, meilleure qualité)

Rendu haut de gamme, mais passe par le navigateur (upload manuel).

1. Révéler le MP3 pour le créateur :
   - macOS : `open -R <projet>/derush/<cut>_voice.mp3`
   - Windows : `explorer /select,"<projet>\derush\<cut>_voice.mp3"`
2. Via le navigateur (extension Chrome / `mcp__claude-in-chrome__*`) : ouvrir
   `https://podcast.adobe.com/enhance` (le créateur doit être connecté à Adobe).
3. **Demander au créateur de glisser le MP3** sur la zone « Optimiser ».
   ⚠️ **L'agent NE PEUT PAS uploader lui-même** : le sélecteur de fichiers ouvre la fenêtre native de
   l'OS, hors de la page → l'upload reste manuel (1 glisser).
4. Attendre le traitement → cliquer **« Télécharger »** → le fichier arrive dans le dossier de
   téléchargements (`~/Downloads` / `%USERPROFILE%\Downloads`).
5. Remux (vidéo intacte + audio amélioré, sync préservé car même durée) :
```bash
cp ~/Downloads/"<cut>_voice-optimisé.mp3" <projet>/derush/<cut>_voice_enhanced.mp3
ffmpeg -y -i <projet>/derush/<cut>.mp4 -i <projet>/derush/<cut>_voice_enhanced.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest <projet>/derush/<cut>_enhanced.mp4
```
> Le remux ci-dessus est écrit en **une seule ligne** exprès (collable tel quel, y compris sous
> PowerShell). Toujours vérifier que les durées vidéo/audio matchent (`ffprobe ... format=duration`)
> avant remux.

#### Variante `ffmpeg` — débruitage 100 % local (automatisable, zéro geste)

Pas d'upload, entièrement scriptable. Chaîne raisonnable : passe-haut (coupe les basses parasites) +
débruitage adaptatif + réduction de bruit non-local + normalisation loudness. Une seule ligne :
```bash
ffmpeg -y -i <projet>/derush/<cut>.mp4 -c:v copy -af "highpass=f=90,afftdn=nf=-25,anlmdn=s=4:p=0.002:r=0.006,loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 256k <projet>/derush/<cut>_enhanced.mp4
```
- `highpass=f=90` : enlève le ronflement/rumble sous 90 Hz.
- `afftdn=nf=-25` : débruitage spectral (monter `nf` vers -20 si le souffle persiste, descendre vers
  -30 si la voix devient métallique).
- `anlmdn` : réduction de bruit non-locale (léger, préserve les transitoires de la voix).
- `loudnorm=I=-16` : niveau cible standard réseaux sociaux.
- Alternative RNNoise si un modèle est dispo : remplacer `afftdn,anlmdn` par
  `arnndn=m=<chemin_modele>.rnnn`.

Adobe reste la meilleure qualité perçue ; le mode `ffmpeg` est le défaut quand on veut un pipeline
sans intervention.

### 7bis. MESURER LES VRAIS POINTS DE COUPE → `<cut>_cuts.json` (OBLIGATOIRE)

> ⛔ **Bug systémique.** Symptôme : au passage plein-écran → split, on voit ~0,2 s de la **fin de la
> prise précédente** (le créateur regarde ailleurs, il n'a pas encore « attaqué » sa phrase).

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
ffmpeg -v error -i <cut>_enhanced.mp4 -filter:v "select='gt(scene,0.015)',metadata=print:file=-" -an -f null - 2>/dev/null | grep pts_time
```
Puis **recaler chaque détection sur la borne théorique la plus proche** (cumul des `ISLANDS`,
tolérance 0,35 s) : ça garantit N-1 coupes, zéro faux positif, zéro oubli. Écrire le résultat dans
**`<cut>_cuts.json`** (une entrée par prise : `start`, `end`, `text`).
Implémentation de référence : `tools/cut_boundaries.py`.

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

Amont : `reel-script` (le script lu au prompteur).
Aval : sous-titres + `motion-design` (visuel) + SFX (voir `design-system/sfx-sound-search.md`), qui
consomment la `timeline.json` / `cuts.json` produites ici. Une seule source de frontières lue par les
3 générateurs (sous-comps, master, sous-titres) : `tools/sections.py` + `tools/build_master.py`.
