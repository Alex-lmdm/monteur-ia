# SFX + musique de fond — DERNIÈRE ÉTAPE

⚠️ **Quand** : NE PAS poser les SFX au fil de l'eau. Sur un nouveau projet on monte d'abord TOUT
(sections, motion, sous-titres, couleur), **le créateur valide le montage final**, et **SEULEMENT
APRÈS** on ajoute les SFX.
Seule exception : la **première vidéo** d'un client (fichier agent, section 🟢), montée d'une
traite ; les SFX sont posés après tes propres contrôles, sans attendre de validation.

**Chercher un son qui n'est pas dans la bibliothèque** → méthode de recherche/sourcing :
`design-system/sfx-sound-search.md`.

**Quelle bibliothèque** (décision du 6 octobre 2026) :
1. **Pack SFX installé** : le pack d'abord (skill `pack-sfx`), l'app pour un son qu'il n'a pas.
2. **Dans l'app HyperFrames, sans Pack SFX** : la bibliothèque HeyGen d'abord (`find_sound_effect`,
   gratuite avec la connexion HeyGen). Requête en anglais qui décrit le geste (« fast whoosh
   transition », « mouse click », « cash register »). Elle n'a pas tout : rien de propre pour un
   déclencheur photo ou un feutre, et « ding » et « succès » renvoient la même notification. Pour
   ces moments, ou si rien ne colle, les sons de départ (`assets/sfx/starter/sounds.md`).
3. **Hors de l'app** (Claude Code, Codex, Windows) : les sons de départ, et le pack s'il est là.

**Sons et musique trouvés dans l'app** (`find_sound_effect`, `find_music` ; absents hors de l'app).
Le fichier arrive dans `assets/` du Reel avec sa durée, et pour un bruitage son `peakOffset`
(secondes entre le début du fichier et l'impact). Mesuré sur 39 sons : MP3 48 kHz stéréo, même
niveau technique que le pack, mais normalisés près du maximum (pic vers -1,5 dB), avec 20 à 50 ms
de silence avant le son et des queues longues (whooshes de 1,3 à 1,6 s) : rogne-les (`trim`, le
fondu de sortie est automatique) pour un son sec. Pour les poser :
- **jamais d'`<audio>` écrit à la main** : hors du bloc SONS, il disparaît à la prochaine
  régénération du master ;
- un bruitage → un event de `tools/build_sfx.py` : `("assets/<fichier>", instant_visé − peakOffset,
  volume_dB, trim)` (avec le Pack SFX : `{"file": "assets/<fichier>", "start": …, "vol": …}` dans
  `work/sfx_events.json`) ;
- une musique → `MUSIQUE_REEL = "assets/<fichier>"` (et `MUSIQUE_REEL_DB`) dans `tools/build_sfx.py`
  (avec le Pack SFX : `"music"` et `"musicDb"` dans `work/sfx_events.json`, forme objet). Elle ne
  vaut que pour ce Reel ; s'il veut la garder pour les suivants, copie-la dans `assets/music/` du
  dossier Monteur IA et règle `audio.musicFile` ;
- ces sons ne sont **pas calibrés** : mesure le volume (`volumedetect`, puis `--probe`) comme pour un
  MP3 du créateur ;
- le fichier reste dans `assets/` du Reel (le bloc SONS le référence sur place, sans copie).

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

**Pose dans le montage** (export natif) : `python3 tools/build_sfx.py` (liste d'events `(fichier,
start, volume_dB, trim|None)`, fichier = chemin relatif à `assets/sfx/`, ex. `starter/pop.mp3`, ou
`assets/<fichier>` pour un son du Reel). Chaque son de la bibliothèque est copié dans `assets/sons/` et écrit en `<audio>` dans le bloc SONS d'`index.html` : volume en dB
converti en `data-volume`, coupe adoucie et fondus en enveloppe `data-automation` (une enveloppe
**remplace** `data-volume`, elle porte donc le niveau réel), voix + sons + musique sur le bus
`mixage` plafonné à -0,26 dB. Dans l'app, chaque son devient un clip de la timeline. Le bloc retouché
à la main ou dans l'app n'est plus écrasé sans `--ecraser`. Mesuré sur un vrai Reel : même mixage
que l'ancien ffmpeg à 0,3 dB près.

**Ancien mixage ffmpeg** (secours : `python3 tools/build_sfx.py --ffmpeg`, par-dessus `exports/FINAL.mp4`) :
- par SFX : `[i:a]atrim=0:DUR(si rogné),volume=XdB,aformat=channel_layouts=stereo:sample_rates=48000,afade=t=out:st=DUR-0.06:d=0.06(si rogné),adelay=START_ms:all=1[ei]`
- mix : `[voice][e0][e1]…amix=inputs=N+1:normalize=0:dropout_transition=0,alimiter=limit=0.97[aout]`
- `-map 0:v -c:v copy -map [aout] -c:a aac -b:a 192k`. Sortie `exports/FINAL_SFX_MUSIC.mp4` (même nom sans musique : SFX seuls).
- Vérif placement sans écoute : `python3 tools/build_sfx.py --probe` (voir plus bas, la seule méthode fiable).

**Musique de fond par défaut** : `brand.config.json` → `audio.musicFile` (fichier dans
`assets/music/`, recopié de projet en projet), au volume `audio.musicDb`.
- **Ajoutée à la MÊME étape que les SFX** (dernière étape, après validation), sur **toute la durée** de
  la vidéo, avec **fade-in ~0.4s + fade-out ~1.2s**.
- **Volume = `audio.musicDb`** (défaut **-26.5 dB**, fond TRÈS discret — la voix toujours en premier ;
  à -26.5 elle finit ~15 dB sous la voix). Sauf si le créateur donne une autre musique/volume.
- **VOCABULAIRE** : quand le créateur dit « **mets le sound effect ET la musique** » → ça veut dire les
  SFX **+ cette musique de fond par défaut**, sauf indication contraire.
- Recette : ajouter au mix une entrée `[m:a]atrim=0:DUR,volume=<audio.musicDb>dB,aformat=channel_layouts=stereo:sample_rates=48000,afade=t=in:st=0:d=0.4,afade=t=out:st=DUR-1.2:d=1.2[music]`
  et l'inclure dans l'`amix` (déjà fait par `tools/build_sfx.py`). `alimiter=limit=0.97` en fin de chaîne évite toute
  saturation.

**Vérifier le placement SANS ÉCOUTER — la seule méthode fiable.**
`python3 tools/build_sfx.py --probe` écrit `work/sfx-only.wav` : la piste **SFX + musique
SEULE** (mêmes événements, sans la voix), en **48 kHz**. Comparer ensuite le pic de chaque
événement au pic de la musique de fond (viser **+4 dB** minimum). Deux méthodes qui mentent :
- ❌ **soustraire deux MP4** (avec / sans SFX) : deux encodages AAC indépendants laissent
  l'erreur de quantification de la voix (~-6 dB), très au-dessus des SFX → inexploitable ;
- ❌ **mesurer en 16 kHz** : coupe au-dessus de 8 kHz et **sous-estime massivement** risers et
  clics, qui vivent dans les aigus → on croit un SFX absent alors qu'il est bien là.

**Rééquilibrer par niveau PERÇU, pas par dB égal.** Un son dont l'énergie est **étalée** (riser :
une montée de ~0,75 s) sort beaucoup plus bas qu'un son percussif (shutter : 30 ms) au même
réglage. Mesuré : un riser posé au même dB que les shutters ressortait **5 dB SOUS la musique de
fond**, donc inaudible. Toujours vérifier au `--probe` après avoir posé les niveaux.
