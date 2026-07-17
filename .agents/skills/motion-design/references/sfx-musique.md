# SFX + musique de fond — DERNIÈRE ÉTAPE

⚠️ **Quand** : NE PAS poser les SFX au fil de l'eau. Sur un nouveau projet on monte d'abord TOUT
(sections, motion, sous-titres, couleur), **le créateur valide le montage final**, et **SEULEMENT
APRÈS** on ajoute les SFX.

**Chercher un son qui n'est pas dans la bibliothèque** → méthode de recherche/sourcing :
`design-system/sfx-sound-search.md`.

**Bibliothèque** : `assets/sfx/` — contient le **pack de démarrage livré** (`assets/sfx/starter/`, 7
sons CC0 : `ui-click`, `keyboard`, `pop`, `whoosh`, `riser`, `impact`, `beep`) plus tout MP3 que le
créateur a ajouté (ses propres sons, ou récupérés via l'API HeyGen — cf
`design-system/sfx-sound-search.md`). **Se référer aux fichiers réellement présents.** Les sons plus
riches cités ci-dessous (camera shutter, felt pen…) ne sont là **que si** l'auth HeyGen a été faite ou
que le créateur les a déposés — sinon, se rabattre sur le pack de démarrage.

**Règles de placement (par TYPE de moment — conserver cette logique)** :
1. **Riser** (`riser`) : sur le HOOK (S1), placé pour **finir PILE à la fin du hook**
   (`start = fin_hook − durée_riser`).
2. **Transition de section** : `whoosh` par défaut (ou, si disponibles, des **camera shutters** en
   **ALTERNANT** — jamais 2× le même de suite). **Pas systématique** : si la transition est
   **fluide/continue** (une image qui se prolonge d'une section à l'autre), **AUCUN son**.
3. **Apparition d'un élément** (nœuds, cartes, valeurs, checks…) : `pop` ou `ui-click`. Sélectif, pas
   chaque micro-élément.
4. **Accent sur un mot fort / un chiffre qui tombe** : `impact` (grave, ponctuel).
5. **Notification / validation / petit signal** : `beep`.
6. **Surlignage** : `felt pen` **si disponible** (bruit de marqueur), un par surlignage, **rogné à la
   durée du surlignage** (~0.45-0.55s) avec `afade` out. Sinon, rien.
7. **Texte qui se tape** (ex. mot-clé du CTA) : `keyboard` (du pack), durée adaptée (quelques lettres →
   rogner court ; longue phrase → laisser courir ou doubler).

**Volume — RÉÉQUILIBRER par niveau perçu** (les fichiers n'ont PAS la même intensité à dB égal ;
mesurer avec `ffmpeg -i F -af volumedetect -f null /dev/null`). Niveaux de référence (exemples, à
ajuster au son réel) :
- **forts/punchy** (riser, whoosh, impact, camera shutters) = **-20 dB**
- **felt pen** = **-11 dB** · **PC typing** = **-12 dB** · **clics/pop d'apparition, beep** =
  **-14/-15 dB**
- (À -20 uniforme, les sons doux — felt pen, typing, clics — sont inaudibles ; les remonter.)

**Recette ffmpeg** (mix par-dessus `renders/FINAL_CAP.mp4`, **vidéo copiée** donc rapide) — script de
réf `work/sfx.py` (liste d'events `(fichier, start, volume_dB, trim|None)`) :
- par SFX : `[i:a]atrim=0:DUR(si rogné),volume=XdB,aformat=channel_layouts=stereo:sample_rates=48000,afade=t=out:st=DUR-0.06:d=0.06(si rogné),adelay=START_ms:all=1[ei]`
- mix : `[voice][e0][e1]…amix=inputs=N+1:normalize=0:dropout_transition=0,alimiter=limit=0.97[aout]`
- `-map 0:v -c:v copy -map [aout] -c:a aac -b:a 192k`. Sortie `renders/FINAL_SFX.mp4`.
- Vérif placement sans écoute : `showwavespic` (comparer voix seule vs voix+SFX, les pics SFX doivent
  apparaître aux bons temps).

**Musique de fond par défaut** : `brand.config.json` → `audio.musicFile` (fichier dans
`assets/music/`, recopié de projet en projet), au volume `audio.musicDb`.
- **Ajoutée à la MÊME étape que les SFX** (dernière étape, après validation), sur **toute la durée** de
  la vidéo, avec **fade-in ~0.4s + fade-out ~1.2s**.
- **Volume = `audio.musicDb`** (défaut **-26.5 dB**, fond TRÈS discret — la voix toujours en premier ;
  à -26.5 elle finit ~15 dB sous la voix). Sauf si le créateur donne une autre musique/volume.
- **VOCABULAIRE** : quand le créateur dit « **mets le sound effect ET la musique** » → ça veut dire les
  SFX **+ cette musique de fond par défaut**, sauf indication contraire.
- Recette : ajouter au mix une entrée `[m:a]atrim=0:DUR,volume=<audio.musicDb>dB,aformat=channel_layouts=stereo:sample_rates=48000,afade=t=in:st=0:d=0.4,afade=t=out:st=DUR-1.2:d=1.2[music]`
  et l'inclure dans l'`amix` (cf `work/mix.py`). `alimiter=limit=0.97` en fin de chaîne évite toute
  saturation.
