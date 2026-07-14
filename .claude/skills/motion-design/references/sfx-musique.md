# SFX + musique de fond — DERNIÈRE ÉTAPE

⚠️ **Quand** : NE PAS poser les SFX au fil de l'eau. Sur un nouveau projet on monte d'abord TOUT (sections, motion, sous-titres, couleur), **Alex valide le montage final**, et **SEULEMENT APRÈS** on ajoute les SFX. (Demande explicite d'Alex.)

**Chercher un son qui n'est pas dans la bibliothèque** → méthode de recherche/sourcing :
`/Users/alexandrecastagna/code/video-hyperframes/design-system/sfx-sound-search.md`

**Bibliothèque** : `assets/sfx/` — 9 fichiers d'Alex (à recopier de projet en projet) :
`Riser.MP3` · `Ballpoint pen click.MP3` · `mouse single click 2.MP3` · `camera shutter sound.MP3` · `camera shutter sound analog.MP3` · `camera shutter sound kashashka.MP3` · `Click (camera shutter sound single shot).MP3` · `felt pen.MP3` · `PC typing keyboard kacha.MP3`.

**Règles de placement (validées par Alex)** :
1. **Riser** : sur le HOOK (S1), placé pour **finir PILE à la fin du hook** (`start = fin_hook − durée_riser`, ~0.757s).
2. **Ballpoint click** : enchaîne juste après le riser → marque la **transition S1→S2** (à la fin du hook).
3. **Camera shutters** (4 variantes) = **transitions de section**. **ALTERNER** (jamais 2× le même de suite). **Pas systématique** : si la transition est **fluide/continue** (une image qui se prolonge d'une section à l'autre), **AUCUN son**.
4. **Clics** (`mouse single click`, `Ballpoint`) = **apparitions** d'éléments (nœuds, cartes, valeurs, checks…). Sélectif, pas chaque micro-élément.
5. **Felt pen** = **surlignages** (bruit de marqueur). Un par surlignage, **rogné à la durée du surlignage** (~0.45-0.55s) avec `afade` out.
6. **PC typing** = un texte qui se **tape** (ex. mot-clé du CTA). **Adapter la durée** : quelques lettres → court ; longue phrase → doubler le SFX.

**Volume — RÉÉQUILIBRER par niveau perçu** (les fichiers n'ont PAS la même intensité à dB égal ; mesurer avec `ffmpeg -i F -af volumedetect -f null /dev/null`). Niveaux validés par Alex :
- **forts/punchy** (Riser, camera shutters, single-shot click) = **-20 dB**
- **felt pen** = **-11 dB** · **PC typing** = **-12 dB** · **clics souris/ballpoint d'apparition** = **-14/-15 dB**
- (À -20 uniforme, felt pen / typing / clics sont inaudibles — felt pen a le pic le plus faible, max ≈ -15.7 dB.)

**Recette ffmpeg** (mix par-dessus `renders/FINAL_CAP.mp4`, **vidéo copiée** donc rapide) — script de réf `/tmp/sfx.py` (liste d'events `(fichier, start, volume_dB, trim|None)`) :
- par SFX : `[i:a]atrim=0:DUR(si rogné),volume=XdB,aformat=channel_layouts=stereo:sample_rates=48000,afade=t=out:st=DUR-0.06:d=0.06(si rogné),adelay=START_ms:all=1[ei]`
- mix : `[voice][e0][e1]…amix=inputs=N+1:normalize=0:dropout_transition=0,alimiter=limit=0.97[aout]`
- `-map 0:v -c:v copy -map [aout] -c:a aac -b:a 192k`. Sortie `renders/FINAL_SFX.mp4`.
- Vérif placement sans écoute : `showwavespic` (comparer voix seule vs voix+SFX, les pics SFX doivent apparaître aux bons temps).

**Musique de fond par défaut** : Alex met ~90% du temps la même musique → `assets/music/Banana Cake.mp3` (à recopier de projet en projet ; source d'origine `~/Documents/🎬 Assets Réseaux Sociaux/`).
- **Ajoutée à la MÊME étape que les SFX** (dernière étape, après validation), sur **toute la durée** de la vidéo, avec **fade-in ~0.4s + fade-out ~1.2s**.
- **Volume = -26.5 dB** (fond TRÈS discret — la voix d'Alex toujours en premier ; à -26.5 elle finit ~15 dB sous la voix). Sauf si Alex donne une autre musique/volume.
- **VOCABULAIRE** : quand Alex dit « **mets le sound effect ET la musique** » → ça veut dire les SFX **+ cette musique de fond par défaut**, sauf indication contraire.
- Recette : ajouter au mix une entrée `[m:a]atrim=0:DUR,volume=-26.5dB,aformat=channel_layouts=stereo:sample_rates=48000,afade=t=in:st=0:d=0.4,afade=t=out:st=DUR-1.2:d=1.2[music]` et l'inclure dans l'`amix` (cf `/tmp/mix.py` du projet). `alimiter=limit=0.97` en fin de chaîne évite toute saturation.
