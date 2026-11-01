# Dérush à la main (repli si `tools/prises.py` échoue)

Étapes 1 à 3 du skill `derush`, faites par `tools/prises.py` en temps normal.

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
⚠️ **JAMAIS `-v error` avec `silencedetect`** : ce filtre logue au niveau *info*, donc `-v error`
renvoie **zéro ligne** et on conclut à tort « aucun silence détecté ». Même piège avec
`volumedetect`. (`ffprobe -v error` reste correct : c'est `ffmpeg` + filtre de mesure qui pose problème.)
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
