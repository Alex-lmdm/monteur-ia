# Transcodage vidéo (HDR→SDR + keyframes + couleur)

**ÉTAPE 0 — TOUJOURS vérifier l'espace couleur AVANT de transcoder** :
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer,color_primaries,width,height,bit_rate -of default=noprint_wrappers=1 SRC
```
- **`color_transfer=bt709` → SDR**. AUCUN tonemap, AUCUN orange. On utilise la vidéo **directement**
  (juste `scale` vers 1080×1920 si besoin + keyframes `-g 30`). C'est le cas idéal.
- **`color_transfer=arib-std-b67` (HLG) ou `smpte2084` (PQ) → HDR** → tonemap obligatoire (recette
  ci-dessous), sinon couleurs délavées OU teinte orange.

La caméra habituelle du créateur est notée dans `brand.config.json` → `derush.camera`. Beaucoup de
caméras récentes (ex. **DJI Osmo Pocket 3 en mode couleur « Normal »**) sortent en **bt709 SDR
direct** (plus de HDR, plus d'orange). **Vérifier quand même à chaque vidéo.**

**Qualité MAX (zéro dégradation)** : un capteur type DJI filme en **2,7K / 22 Mbps**. CapCut, à
l'export, **réduit en 1080p** par défaut → perte de netteté surtout sur le **visage recadré**
(split-screen). ⇒ **Demander au créateur d'exporter de CapCut en résolution MAX (2K/4K) + débit
élevé.** Plus de pixels source = visage net après recadrage. De ton côté : le **dérush reste en
pleine résolution** (skill `derush` §5), `base.mp4` (1080×1920, crf 14) n'en est que la réduction
pour le studio, et l'export final (crf 16) relit le visage dans le dérush.

---

## Cas HDR (vidéos HLG — anciennes captures iPhone, ou caméra repassée en HLG)

Les vidéos HDR HLG BT.2020 10-bit (`color_transfer=arib-std-b67`) sans VRAIE conversion : couleurs
**délavées/blanchâtres** + warning « sparse keyframes » (freeze au seek).

**Important** : exporter en H.264 depuis CapCut **ne tonemappe PAS** — CapCut garde les données HLG
(frame identique avant/après, toujours `arib-std-b67`). Donc **c'est NOUS qui devons tonemapper**.

Si le ffmpeg installé **n'a pas `zscale`** (zimg pas dans la formule) → impossible de linéariser le
HLG → `tonemap` seul assombrit/déraille. **Solution** : récupérer un **build statique avec `zscale`** :
- macOS : `curl -sL "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip" -o work/ff.zip && unzip -o work/ff.zip -d work/ffx && chmod +x work/ffx/ffmpeg`
- Windows : télécharger un build « full » (gyan.dev / BtbN) qui inclut `--enable-libzimg`.

Puis vrai tonemapping HLG→SDR BT.709 + keyframes denses (`-g 30` obligatoire), en une ligne :
```bash
ffmpeg -i SRC -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" -c:v libx264 -crf 23 -g 30 -keyint_min 30 -sc_threshold 0 -c:a aac -b:a 192k -movflags +faststart assets/video/base.mp4
```
Résultat : couleurs naturelles/riches, pas lavé, pas sombre. **Toujours vérifier** :
`ffprobe ... color_transfer` doit être `bt709`. Au render, si HDR re-détecté : `hyperframes render --sdr`.

**Teint orangé (correction fréquente)** : le tonemap HLG laisse un teint **trop chaud/orange** sur la
peau. Ajouter à la fin du `-vf` : `,colortemperature=temperature=7200:mix=0.35,eq=saturation=0.92`
(refroidit légèrement la balance + désature un peu → teint naturel, mur bien blanc).

**Qualité visage (split-screen)** : le visage est un recadrage zoomé (`crop ... scale`) d'une petite
zone de l'image (~771×714 px de `base.mp4` pour remplir 1080×1000). Mesuré sur un rush DJI
1728×3072, en % du détail du visage dans le rush :
- visage lu dans `base.mp4` (dérush réduit en 1080 dès le départ, ancien pipeline) : **33 %** — la
  réduction en 1080 seule en coûtait déjà plus de la moitié ;
- visage relu dans le dérush pleine résolution (pipeline actuel) : **~80 %**.
D'où la règle : **aucune réduction avant l'export**. `tools/build_final.py` relit le visage dans le
dérush (`<cut>_cuts.json` → `source`) avec un crop mis à l'échelle ; il retombe sur `base.mp4` (et le
dit) si ce dérush manque, est en HDR, ou ne montre pas les mêmes images que `base.mp4`. Export final
en **crf 16** (pas 18+).
**Cas HDR** : le dérush garde les couleurs HLG, seul `base.mp4` est tonemappé → l'export retombe sur
`base.mp4` (visage moins net). Le remède durable reste de filmer en SDR (mode couleur « Normal »).
Limite inhérente : si le créateur est filmé d'assez loin → conseiller un cadrage plus serré au
tournage.
