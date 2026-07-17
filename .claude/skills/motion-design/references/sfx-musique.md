# SFX + musique de fond — DERNIÈRE ÉTAPE

⚠️ **Quand** : NE PAS poser les SFX au fil de l'eau. Sur un nouveau projet on monte d'abord TOUT
(sections, motion, sous-titres, couleur), **le créateur valide le montage final**, et **SEULEMENT
APRÈS** on ajoute les SFX.

**Chercher un son qui n'est pas dans la bibliothèque** → méthode de recherche/sourcing :
`design-system/sfx-sound-search.md`.

**Bibliothèque** : `assets/sfx/` — contient la **bibliothèque de démarrage livrée**
(`assets/sfx/starter/`, 22 sons CC0) plus tout MP3 que le créateur a ajouté (ses propres sons, ou
récupérés via l'API HeyGen). **➡️ Lire `assets/sfx/starter/sounds.md`** : chaque son y a une description
« à utiliser quand… » — c'est l'index dans lequel on **choisit** le bon son pour chaque moment. **Se
référer aux fichiers réellement présents.**

**Règles de placement (par TYPE de moment — choisir le fichier via `sounds.md`)** :
1. **Riser** (catégorie *riser* : `riser` clair / `riser-dark` grave) : sur le HOOK (S1), placé pour
   **finir PILE à la fin du hook** (`start = fin_hook − durée_riser`).
2. **Transition de section** (catégorie *whoosh* : `whoosh-fast` / `whoosh` / `whoosh-long` selon
   l'ampleur du changement) — **ALTERNER** les variantes, jamais 2× la même de suite. **Pas
   systématique** : si la transition est **fluide/continue** (une image qui se prolonge d'une section à
   l'autre), **AUCUN son**.
3. **Apparition d'un élément** (nœuds, cartes, valeurs, checks…) : *pop* (`pop`, `drop`) ou un *clic*
   (`click-ui`, `select`, `tick`). Sélectif, pas chaque micro-élément.
4. **Clic / interaction montrée à l'écran** (curseur, bouton, bascule) : `click-mouse`, `click-double`,
   `switch`… selon ce qu'on voit.
5. **Accent sur un mot fort / un chiffre qui tombe** : `impact` (sec) ou `impact-boom` (gros, plein écran).
6. **Validation / erreur** : `confirmation` (succès, coche) · `error` (mauvais choix, à éviter).
7. **Notification / signal** : `ding` (chaleureux) ou `notification` (cristallin).
8. **Texte qui se tape** (ex. mot-clé du CTA) : `keyboard`, durée adaptée (quelques lettres → rogner
   court ; longue phrase → laisser courir).
9. **Argent** (vente, gain, prix) : `cha-ching`.
10. **Surlignage** : `felt pen` **si disponible** dans la biblio (bruit de marqueur), rogné à la durée
    du surlignage (~0.45-0.55s) avec `afade` out. Sinon, rien.

**Volume — RÉÉQUILIBRER par niveau perçu** (les fichiers n'ont PAS la même intensité à dB égal ;
mesurer avec `ffmpeg -i F -af volumedetect -f null /dev/null`). Niveaux de référence (exemples, à
ajuster au son réel) :
- **forts/punchy** (riser, whoosh, impact/impact-boom, cha-ching) = **-20 dB**
- **keyboard** = **-12 dB** · **clics/pop/drop d'apparition, ding, notification, confirmation, error** =
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
