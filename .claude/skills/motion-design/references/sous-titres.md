# Sous-titres (caption layer) — LMDM

> Lu quand des sous-titres sont à produire. Le découpage se décide **par unité grammaticale**,
> pas par largeur : lire ce fichier AVANT d'écrire le moindre chunk.

Police **Bowlby One SC** (Google Font, souvent déjà dans `~/Library/Fonts/BowlbyOneSC-Regular.ttf` ; sinon github google/fonts `ofl/bowlbyonesc`). Vendre en local `assets/fonts/`. Style : **texte noir**, **fond jaune `#ffee00` plein** (opacité 100%, **pas d'arrondi**), padding léger (`8px 20px`), **une seule ligne**, `font-size:50px` (UPPERCASE small-caps).

**Découpage — RÈGLES DÉTERMINISTES** (depuis `transcript.json`, mesurer la largeur avec `PIL.ImageFont.truetype` sur le vrai TTF pour garantir 1 ligne ; corriger « Cloud »→« Claude ») :
1. **Jamais de ponctuation de fin affichée** : retirer `. , ; : ! ?` du texte affiché (les `.` notamment ne servent à rien).
2. **Jamais à cheval sur 2 phrases** : un `. ! ?` ferme TOUJOURS le sous-titre courant ; la phrase suivante repart sur un nouveau sous-titre (même si ça fait 1-2 mots).
3. **Blocs insécables** gardés ensemble : `Claude Code`, nombres composés (`30 000`).
4. **Couper à une frontière logique** — bons points de coupe (priorité) : (a) après une **virgule** ; (b) **avant un connecteur** qui démarre une nouvelle bribe : conjonctions (`et mais ou donc car puis ensuite alors comme`), subordonnants/relatifs (`qui que qu' dont où quand si parce`), prépositions de tête (`à au aux dans sur avec pour par en vers chez sans sous entre`), pronoms sujets (`il elle on ils elles ça ce je tu nous vous`), `voire`, `certains`. Prendre le **1er bon point** une fois ≥2 mots → chunks plus courts et variés (2-4 mots). ⚠️ **Exception : « de »/« à » qui suivent un verbe** (périphrase : « vient **de** donner », « prêt **à** copier », « en train **de** ») **ne sont PAS des points de coupe** — ils appartiennent au groupe verbal, ne jamais démarrer un sous-titre dessus.
5. **Ne JAMAIS finir un sous-titre sur un mot faible** (il s'accroche au suivant) : articles/déterminants (`le la les un une des du de d' l' mon ma ses…`), prépositions (`à de en dans sur avec pour par sans…`), conjonctions (`et ou mais donc car que qui dont`), formes élidées (`qu' d' l' j' n'…`), **nombres** (`deux trois … dix cent mille` + chiffres → s'accrochent au nom : « deux minutes », « 30 000 développeurs »). Si la coupe forcée (taille/largeur) tombe sur un mot faible, reculer d'un mot.
6. **Taille** : **viser 2-3 tokens** par sous-titre (défaut idéal **validé par Alex** — plus granulaire que ce que l'algo tend à produire) ; **max 4** seulement si ça reste court ET cohérent ; largeur ≤ ~920px @50px → **jamais de débordement**.

**Découpage par UNITÉ GRAMMATICALE — le nerf de la guerre (validé Alex 2026-07-08).** Chaque
sous-titre = **UNE unité qui se tient**. `montage_captions.py` produit un **premier jet légal en
largeur mais SANS conscience grammaticale** (il empile 2-3 mots gloutonnement) → le découpage
**FINAL se décide par unité grammaticale**, à revoir **avant de livrer**. Règles (par ordre de force) :

1. **Nom + adjectif = insécable.** Ne JAMAIS orpheliner l'adjectif de son nom, ni le coller à la
   phrase suivante. « prompts secrets », « documentation officielle » restent ensemble.
2. **Groupe verbal = insécable**, y compris les **périphrases** : ne pas couper entre le
   (semi-)auxiliaire et son infinitif/participe. « vient de te donner », « est déjà écrit »,
   « prêt à copier-coller », « en train de », « commence à » = un seul bloc.
3. **Ne JAMAIS fusionner la fin d'une unité avec le début de la suivante** (ça sonne mal) :
   « secretsˇpour Claude Code », « écritˇprêt à » = interdits. En cas de conflit, re-couper **à la
   frontière** entre les deux unités.
4. **Trop large pour garder l'unité entière → ISOLER le mot seul**, jamais le coller à un voisin
   étranger. « tous ces prompts secrets » trop long → « tous ces prompts » / « secrets » /
   « pour Claude Code » (un adjectif ou un mot fort seul = OK, ça donne même du rythme).
5. **Un nom / sujet peut rester SEUL** pour l'emphase (« Anthropic », « ABSOLUMENT », « RESTAURER »).
6. **Adjectif/adverbe de CHUTE isolé = OK et FRÉQUENT** (rythme + emphase — corrigé Alex 2026-07-08).
   Alex **isole souvent le dernier mot qui porte l'accent** : « OFFICIELLE », « VRAIMENT », « SIMPLEMENT ».
   Donc « ils ont partagé ça » · « **dans leur documentation** » · « **officielle** » (et NON « dans leur »
   · « documentation officielle »). ⇒ La **règle 1** (nom+adjectif ensemble) est le **défaut**, mais
   elle **cède** quand l'adjectif final porte l'accent → on l'isole. En cas de doute, isoler le mot fort.
7. **En cas de doute : couper plus court.** Chunks courts/variés (souvent 2-3 mots) = lisent mieux,
   collent mieux à la voix, ne débordent jamais.
8. **Caler sur l'audio réel** + corriger les mots mal transcrits (« qu'il » pas « qui », « et c'est
   là » pas « essaie-la », « L'IA » pas « Léa », « ChatGPT » pas « ChatJPT »).

**Exemple de référence CANONIQUE — découpage COMPLET dicté mot-à-mot par Alex (2026-07-08, Reel
« prompts secrets »). C'est LE modèle à reproduire.** Extraits (viser la colonne CIBLE) :

| Voix off | ✅ Cible Alex (dictée) |
|---|---|
| Anthropic vient de te donner tous ses prompts secrets pour Claude Code, et c'est gratuit | `ANTHROPIC` · `VIENT DE TE DONNER` · `TOUS SES PROMPTS SECRETS` · `POUR CLAUDE CODE` · `ET C'EST GRATUIT` |
| Ils ont partagé ça dans leur documentation officielle | `ILS ONT PARTAGÉ ÇA` · `DANS LEUR DOCUMENTATION` · `OFFICIELLE` |
| En gros, tu copies la bonne phrase, tu la colles, et Claude sait exactement quoi faire | `EN GROS` · `TU COPIES` · `LA BONNE PHRASE` · `TU LA COLLES` · `ET CLAUDE` · `SAIT EXACTEMENT` · `QUOI FAIRE` |
| C'est de découvrir des demandes que t'aurais jamais pensé à faire | `C'EST DE DÉCOUVRIR` · `DES DEMANDES` · `QUE T'AURAIS` · `JAMAIS PENSÉ` · `À FAIRE` |
| Si tu veux le lien, commente CODE et je te l'envoie directement en DM | `SI TU VEUX LE 🔗` · `COMMENTE CODE` · `ET JE TE L'ENVOIE` · `DIRECTEMENT EN DM` |

> Le découpage COMPLET de ce Reel vit dans `montage_captions.py` (liste **`MANUAL`**, un chunk par
> sous-titre par clip). Le rythme : **fin (2-3 mots)**, connecteurs qui démarrent, mots forts / adjectifs
> de chute isolés, groupes grammaticaux intacts, jamais de largeur ≤ 820 px dépassée.

**⚠️ MÉTA-RÈGLE — le découpage final est l'OREILLE d'Alex.** Les règles 1-8 donnent un bon brouillon,
mais **toujours PROPOSER le découpage à Alex et implémenter SES chunks exacts** via la liste `MANUAL`
de `montage_captions.py` — plus fiable que n'importe quel algo. `montage_captions.py` ne fait que le
**timing + la largeur + le section-aware** ; le **groupement = dicté/validé par Alex**. Une fois qu'il
dicte, coller au mot près.

**⚠️ RÈGLE SYSTÉMATIQUE — SOUS-TITRES SECTION-AWARE (validée Alex 2026-07-08, cause d'un bug récurrent)** :
Un sous-titre est **LIÉ à une séquence visuelle**. Le générateur de sous-titres **DOIT connaître les
frontières des sections** (les `data-start` du master) et, **automatiquement** (pas en override manuel) :
1. **Aucun sous-titre ne DÉBORDE d'une section** : à chaque frontière de section, le sous-titre le plus
   proche **démarre PILE sur la frontière** (snap), et le précédent **finit PILE dessus**. Sinon le
   dernier sous-titre d'une section « bave » sur la section suivante (ex. « secrets pour Claude Code »
   qui traîne sur le plein-écran « et c'est gratuit »).
2. **La hauteur `y` vient de la SECTION**, pas d'une plage de temps bricolée : split → **920** (jointure),
   plein-écran VISAGE → **1140**, plein-écran MOTION/IMAGES → **1500**. Un sous-titre prend le `y` de la
   section qui contient son `start`.

Pourquoi le bug arrivait : le timing des sous-titres était interpolé **dans les clips** (dérush), en
ignorant les **sections** (montage). Or clips ≠ sections (une section = souvent un sous-ensemble d'un
clip, ex. le plein-écran « et c'est gratuit » est la fin du clip 1). Implémentation de réf :
`montage_captions.py` → liste `SECTIONS = [(start, y), …]`, snap des starts sur `BOUNDS`, `y_for(start)`
par section. **Garder `SECTIONS` synchro avec les `data-start` du master.**

Timing = continu (chaque caption jusqu'au start du suivant, sauf override). Répartir sur `data-track-index = idx%4` (sinon erreurs `overlapping_clips_same_track` quand end==next.start). Donner un `id="cap-N"` à chaque (sinon warning `studio_missing_editable_id` + non éditable dans le studio).

**Position (règle quasi immuable)** :
- **Split-screen** → sous-titre **pile à la jointure** (centre `y=920`).
- **Plein écran VISAGE** (le visage d'Alex en grand) → sous-titre **à ~59 %** (`y≈1140`, un peu sous le centre). (Validé par Alex ; rappel : « plus bas » = % plus GRAND.)
- **Plein écran MOTION / IMAGES** → **plus bas** (centre `y≈1500`), sous le visuel pour ne pas le couvrir.

**Implémentation** : compo dédiée `compositions/captions.html` (fond transparent, un `<div class="cap clip" id="cap-N">` par sous-titre, `position:absolute; left:50%; transform:translate(-50%,-50%); top:Ypx`). Branchée 2 fois :
- dans le master `index.html` comme overlay (track-index élevé) **+ `@font-face` Bowlby dans le head du master** → visible/éditable dans le studio ;
- rendue en overlay transparent `hyperframes render -c compositions/captions.html --format mov -o renders/captions.mov`, puis compositée en ffmpeg par-dessus `FINAL.mp4` : `ffmpeg -i FINAL.mp4 -i captions.mov -filter_complex "[0:v][1:v]overlay[v]" -map "[v]" -map 0:a ... renders/FINAL_CAP.mp4`.

**Mot « lien » dans un CTA** → interdit (shadowban) : utiliser l'emoji 🔗. Détail dans `references/patterns.md`.
