# Calibration du cadrage — split-screen (transform) ↔ crop ffmpeg

But du bloc F : régler **une fois** comment le visage de l'utilisateur est cadré dans la moitié
basse du split-screen, le valider **à l'œil sur un vrai snapshot**, puis en déduire le **crop
ffmpeg** exact pour que l'export final soit cadré à l'identique (la preview HyperFrames ramollit le
visage → l'export final se fait en ffmpeg, donc le crop doit correspondre pixel pour pixel au
`transform` CSS).

Sortie : `montage.splitTransform` (le CSS validé) + `montage.faceCrop` (le filtre ffmpeg dérivé).

> Format de référence : **1080×1920, 30 fps**. Split par défaut : motion en haut, **visage en bas**
> (fenêtre écran `y = 920 → 1920`, soit **1000 px** de haut). Overlay ffmpeg à `0:920`.

---

## 1. Poser le rush test en `base.mp4`

1. Demander un **rush test de 10-20 s** (l'utilisateur, face caméra, son cadrage habituel).
2. **Vérifier le `color_transfer`** avant de transcoder :
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 <rush>
   ```
   - `bt709` → SDR, rien à faire (transcoder direct).
   - `arib-std-b67` ou `smpte2084` → **HDR**, tonemap obligatoire (cf
     `.claude/skills/motion-design/references/transcodage-video.md`).
   - Caméra **DJI** : la vidéo a un **2ᵉ flux mjpeg** (vignette) → mapper `[0:v:0]` explicitement.
3. Transcoder en `assets/video/base.mp4`, 1080×1920 (crf 14, visage net). Rappeler à l'utilisateur
   de filmer en **SDR / mode Normal** à l'avenir s'il est en HDR.

---

## 2. Appliquer le transform par défaut et générer un snapshot

Le `transform` du visage en split (défaut validé, cadrage type) :
```css
.face-bottom video {
  position:absolute; inset:0; width:1080px; height:1920px; object-fit:cover;
  transform-origin:0 0; transform: translate(-216px, 410px) scale(1.40);
}
```
Poser cette valeur dans `montage.splitTransform`, puis générer un contrôle visuel **déterministe** :
```bash
npx hyperframes snapshot   # (+ --selector / --shot selon l'outil) — jamais le navigateur ici
```
Montrer l'image à l'utilisateur.

---

## 3. Itérer sur 3 leviers, à l'œil

On ajuste **uniquement le `transform`** (jamais dragger/resizer la vidéo dans le studio → ça
repositionne la surface et déclenche le bug du « carré noir »). Trois leviers seulement :

| Levier | Propriété | Effet |
|---|---|---|
| Zoom | `scale` | plus grand = visage plus gros |
| Hauteur | **2ᵉ** valeur de `translate` (`ty`) | plus **petit** = visage plus **haut** |
| Horizontal | **1ʳᵉ** valeur de `translate` (`tx`) | recentre gauche/droite |

Questions de calage à poser (une itération = un ajustement + un nouveau snapshot) :
- « Ton visage est bien centré dans la moitié basse ? »
- « Il est trop zoomé / pas assez ? »
- « Les yeux tombent à peu près au tiers haut du cadre du bas ? »

Répéter snapshot → ajustement jusqu'à ce que **l'utilisateur valide**. La valeur validée = le
`montage.splitTransform` définitif.

---

## 4. Convertir le transform en crop ffmpeg (formule exacte)

Reprise de `.claude/skills/motion-design/references/montage-talking-head.md`.

Le `transform: translate(tx, ty) scale(s)` (origin `0 0`) sur une surface 1080×1920 mappe une source
vers l'écran par `écran = translate + s · source`, donc `source = (écran − translate) / s`. La
fenêtre visible du visage en split est l'écran `x ∈ [0,1080]`, `y ∈ [920,1920]`. On en déduit la
zone source à cropper :

```
crop_w = round(1080 / s)
crop_h = round((1920 - 920) / s) = round(1000 / s)
crop_x = round((0   - tx) / s) = round(-tx / s)
crop_y = round((920 - ty) / s)
```
puis on rescale la zone cropée à la taille de la fenêtre split (1080×1000) et on l'overlay à `0:920` :
```
crop=crop_w:crop_h:crop_x:crop_y,scale=1080:1000     # overlay=0:920
```

**Vérification avec le défaut** `translate(-216px, 410px) scale(1.40)` :
- `crop_w = 1080/1.40 = 771,4 → 771`
- `crop_h = 1000/1.40 = 714,3 → 714`
- `crop_x = 216/1.40 = 154,3 → 154`
- `crop_y = (920-410)/1.40 = 510/1.40 = 364,3 → 364`
- → `crop=771:714:154:364,scale=1080:1000` ✔ (valeur de référence du skill motion-design).

Écrire ce résultat dans `montage.faceCrop`. **Si `splitTransform` change un jour, recalculer** avec
la formule ci-dessus — un crop désaligné = un cadrage faux à l'export.

---

## 5. Écrire et valider

Récapituler à l'utilisateur :
- `montage.splitTransform` = le CSS validé au snapshot.
- `montage.faceCrop` = le crop ffmpeg dérivé (préciser l'overlay `0:920`).
- `montage.splitByDefault` = `true` (tout commence en split ; les passages plein écran se décident
  section par section au montage).

Après OK → écrire dans `brand.config.json`, marquer le bloc `F`, `node scripts/sync.mjs`.

> Note qualité : l'export final se fait **en ffmpeg** (crf 16, visage net), **jamais** `npm run
> render` (le render HyperFrames ramollit la couche vidéo). Le crop calibré ici est précisément ce
> qui garde l'export aligné sur la preview.
