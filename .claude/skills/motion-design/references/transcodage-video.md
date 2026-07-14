# Transcodage vidéo (HDR→SDR + keyframes + couleur)

**ÉTAPE 0 — TOUJOURS vérifier l'espace couleur AVANT de transcoder** :
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer,color_primaries,width,height,bit_rate -of default=noprint_wrappers=1 SRC
```
- **`color_transfer=bt709` → SDR**. AUCUN tonemap, AUCun orange. On utilise la vidéo **directement** (juste `scale` vers 1080×1920 si besoin + keyframes `-g 30`). C'est le cas idéal.
- **`color_transfer=arib-std-b67` (HLG) ou `smpte2084` (PQ) → HDR** → tonemap obligatoire (recette ci-dessous), sinon couleurs délavées OU teinte orange.

Depuis ~juin 2026 Alex filme sur **DJI Osmo Pocket 3 en mode couleur « Normal » → bt709 SDR direct** (plus de HDR, plus d'orange). Vérifier quand même à chaque vidéo.

**Qualité MAX (zéro dégradation)** : le DJI brut est en **2,7K (1728×3072) / 22 Mbps**. CapCut, à l'export, **réduit en 1080p** par défaut → perte de netteté surtout sur le **visage recadré** (split-screen). ⇒ **Demander à Alex d'exporter de CapCut en résolution MAX (2K/4K) + débit élevé.** Plus de pixels source = visage net après recadrage. De mon côté : base.mp4 en **crf 14**, export final en **crf 16**.

---

## Cas HDR (anciennes vidéos iPhone HLG, ou si jamais l'Osmo repasse en HLG)

Les vidéos étaient **HDR HLG BT.2020 10-bit** (`color_transfer=arib-std-b67`). Sans VRAIE conversion : couleurs **délavées/blanchâtres** + warning « sparse keyframes » (freeze au seek).

**Important** : exporter en H.264 depuis CapCut **ne tonemappe PAS** — CapCut garde les données HLG (vérifié : frame identique avant/après, toujours `arib-std-b67`). Donc **c'est NOUS qui devons tonemapper**.

Le ffmpeg Homebrew (8.1.x) **n'a pas `zscale`** (zimg pas dans la formule) → impossible de linéariser le HLG → `tonemap` seul assombrit/déraille. **Solution** : récupérer un **build statique macOS avec `zscale`** (evermeet.cx) :
```bash
curl -sL "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip" -o /tmp/ff.zip && unzip -o /tmp/ff.zip -d /tmp/ffx && chmod +x /tmp/ffx/ffmpeg
```
Puis vrai tonemapping HLG→SDR BT.709 + keyframes denses (`-g 30` obligatoire) :
```bash
/tmp/ffx/ffmpeg -i SRC -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
  -c:v libx264 -crf 23 -g 30 -keyint_min 30 -sc_threshold 0 -c:a aac -b:a 192k -movflags +faststart assets/video/base.mp4
```
Résultat : couleurs naturelles/riches, pas lavé, pas sombre. **Toujours vérifier** : `ffprobe ... color_transfer` doit être `bt709`. Au render, si HDR re-détecté : `hyperframes render --sdr`.

**Teint orangé (correction validée par Alex)** : le tonemap HLG laisse un teint **trop chaud/orange** sur la peau. Ajouter à la fin du `-vf` : `,colortemperature=temperature=7200:mix=0.35,eq=saturation=0.92` (refroidit légèrement la balance + désature un peu → teint naturel, mur bien blanc).

**Qualité visage (split-screen)** : le visage est un recadrage zoomé (`crop ... scale`) d'une sous-partie du 1080p → chaque ré-encodage ramollit. Pour garder un visage net : base.mp4 en **crf 14** (quasi-sans-perte) ET export final en **crf 16** (pas 18+). Limite inhérente : Alex filmé d'assez loin → conseiller un cadrage plus serré au tournage pour les prochaines vidéos.
