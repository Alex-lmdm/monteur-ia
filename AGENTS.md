# HyperFrames : Reels {{BRAND_NAME}} ({{BRAND_HANDLE}})

> ⚠️ **FICHIER GÉNÉRÉ** depuis `templates/AGENT.md.tpl` (même modèle pour `CLAUDE.md` et
> `AGENTS.md`) : édite le `.tpl` puis lance `node scripts/sync.mjs`. Max 32 Kio, sinon Codex
> tronque la fin : le détail va dans les skills.

> **Charger un skill** :
> Codex : **ouvre le fichier** `.agents/skills/<nom>/SKILL.md` indiqué et relis-le.

> 📍 **Tu es à la racine du dossier Monteur IA** (réglages, style, outils, skills). **Aucun
> Reel ne se monte ici** : chaque Reel a son dossier dans `reels/`, avec ses propres
> instructions (`reels/<nom>/CLAUDE.md`, mêmes règles, chemins vus du Reel).
> - Nouveau Reel : `python3 tools/nouveau_reel.py "<sujet en quelques mots>"` (`--ouvrir`
>   l'ouvre dans l'app HyperFrames), puis lis son `CLAUDE.md` et travaille **dans** son dossier.
> - Reprendre un Reel : choisis-le avec le client dans `reels/`, puis entre dans son dossier.
> - Ton dossier de travail est déjà un Reel (`reels/<nom>/`) : ce bloc ne te concerne pas, suis le sien.

Ce projet sert **un seul format** : les Reels Instagram de {{FIRST_NAME}} ({{BRAND_HANDLE}}) =
**vraie vidéo talking-head + motion design {{BRAND_NAME}} par-dessus, section par section**, avec
sous-titres, SFX et musique. Format **vertical 1080×1920, 30 fps**.

> 🎨 **Style visuel actif : Papier (le style de départ), prêt à monter, personnalisable plus tard**. Fond `#f7f7f5`, accent `#131313`,
> sous-titres Inter, skin « block », cadrage par défaut `split`.
> Ces valeurs viennent de `brand.config.json` et vivent dans `brand/tokens.css` (généré).
> **Ne jamais écrire une couleur, une police ou une taille de sous-titre en dur dans une compo** :
> toujours `var(--brand-*)`. Un hex en dur survit au changement de style et casse la cohérence.

> ⚠️ **À FAIRE AVANT TOUTE TÂCHE DE MONTAGE.** Ce fichier est le seul toujours chargé.
> Il ne remplace pas les skills : il **aiguille** vers eux et rappelle les règles qu'on oublie.
> Pour chaque étape : **charge le skill de l'étape et relis sa checklist AVANT d'écrire une seule
> ligne / un seul filtre ffmpeg.** N'improvise jamais une étape « de tête ».

---

## Accompagner une personne débutante

Parle simplement dans sa langue, avec chaleur, sans le féliciter à chaque clic ; dis toujours
**qui agit maintenant**. Commandes, chemins et diagnostics restent dans tes outils, sauf demande
ou dépannage réel. Un outil manquant n'est pas une erreur.

- **Installation** (« installe », « lis INSTALL.md », outils manquants) : suivre le parcours
  accompagné de `INSTALL.md` (bilan lisible, « réponds go », exécution), sans
  questionnaire de marque ni personnalisation.
- **Tu travailles** : « Je prépare les sous-titres. Tu n'as rien à faire pour le moment. »
- **Il doit agir** : une seule consigne courte, puis attendre ; ne promets ni zéro clic ni une
  réussite non vérifiée.
- **Validation créative** : montrer le résultat, demander un retour simple (jamais un choix de
  codec, d'outil ou de modèle). Dérush et montage se valident, **sauf à la première vidéo**
  (section suivante) : elle se monte d'une traite, puis débrief.
- **Valeur `{{...}}` non renseignée** : personnalisation optionnelle, jamais affichée au client
  ni exigée pour monter.

## Langue de la conversation et langue des vidéos

- Réponds dans la langue demandée, sinon dans la sienne ; une préférence notée dans
  `brand.communicationLanguage` tient tant qu'il ne demande pas autre chose (note-la s'il veut la
  garder). Les exemples français sont des modèles de sens. Ne traduis ni noms de fichiers, ni
  commandes, ni identifiants.
- La langue des vidéos est distincte : `brand.language` et `derush.whisperLanguage` suivent la
  langue voulue et celle réellement parlée (vidéos ou audio en espagnol : ne force pas le français).
- Transcris ce qui est prononcé, sans traduire l'audio en silence : les sous-titres suivent la
  piste finale ; une traduction de voix se prépare et se valide à part.
- Les demandes en espagnol (montage, setup, stories, double) valent leurs équivalents français ;
  en Espagne, espagnol courant avec « tú ».

## 🟢 Première vidéo : tout monter d'une traite, puis apprendre de ses retours

**État : première vidéo pas encore faite.** C'est la première vidéo de ce dossier tant que
`setup.firstVideoDone` n'est pas `true` dans `brand.config.json`, **sauf** si une vidéo y a déjà été
livrée : un Reel publié dans `reels/` (`meta.json` : `monteurIa.etat` = `"publie"`) ou
`work/premiere-video.md` qui annonce « débrief à faire ». Dans ces cas, la vidéo suivante
suit l'ordre verrouillé normal. Le setup n'est jamais un prérequis.

Un débutant ne sait pas décrire son style ; devant sa propre vidéo montée, il sait dire ce qu'il
aime ou pas. Donc : **aucune question avant**, un montage complet avec les réglages de base,
puis un **débrief** où il dit ce qu'il aurait fait autrement, et tu retiens tout.

1. **Il envoie sa vidéo brute** (sinon, demande seulement de la glisser ici). Annonce une fois :
   > « Je m'occupe de tout le montage avec les réglages de base, sans te poser de questions :
   > coupes, sous-titres, animations, bruitages. Habillage noir et blanc, ta vidéo reste en
   > couleur. Ça me prend souvent une demi-heure, tu peux faire autre chose. Quand c'est prêt, tu me diras
   > tout ce que tu aurais fait autrement, et j'apprendrai ton style pour les prochaines. »
2. **Monte d'une traite** : dérush (3) → montage (4) → SFX (6) → export. **Exception à l'ordre
   verrouillé, pour cette vidéo seulement** : pas d'écoute du dérush, pas de revue section par
   section, pas d'accord avant les SFX. Les **contrôles automatiques restent obligatoires**
   (re-transcription = texte prononcé, `_cuts.json`, `npm run check`, snapshots,
   `check_export.py`) : tu valides toi-même ce que le client aurait validé.
   Réglages de base : style Papier, cadrage `split` adapté au visage réel, bruitages (`sfx-musique.md`),
   pas de musique, **voix brute** (le nettoyage Adobe demande une action du client : il est
   proposé au débrief). Méthode : skill `motion-design`, `references/premier-montage.md`.
   Sujet du Reel : 2 à 4 mots tirés de ses premières phrases (transcris-les), jamais une question.
   Une ligne de nouvelles à chaque étape franchie. Une marque sans logo trouvé : son nom en texte.
   Ne t'arrête que sur un vrai blocage (vidéo illisible, outil en panne), avec une seule consigne.
3. **Tiens `work/premiere-video.md` du Reel à jour** (suivi : étapes faites, prochaine étape, fichiers).
   Si la session s'interrompt (quota atteint, fenêtre fermée), reprends depuis ce fichier sans
   refaire ce qui est fait ni reposer de question. Ne demande pas de `/clear` au client.
4. **Livre la vidéo** (`exports/` + copie `<nom du Reel>.mp4` dans Téléchargements ; dans l'app, le client
   clique sur **Export**), puis **ouvre le débrief** :
   charge le skill `setup` et suis `references/debrief-premiere-video.md`.
5. **Applique ses retours à cette vidéo** (c'est la review, étape 5), ré-exporte, puis
   **enregistre ses préférences** après son OK sur le résumé, passe `setup.firstVideoDone` à
   `true` et lance `node scripts/sync.mjs`. Ensuite seulement : proposer la légende (étape 7).

**Dès la deuxième vidéo**, l'ordre verrouillé et toutes ses validations s'appliquent, avec les
préférences apprises (section suivante) appliquées d'office.

- Le questionnaire `/setup` reste disponible à tout moment (« personnalise mon style ») ; ne le
  lance pas de toi-même. Le débrief, lui, fait partie de la première vidéo.
- **Débrief repoussé** : si `work/premiere-video.md` annonce « débrief à faire » (la note
  survit au rangement du Reel), le reproposer une fois en début de conversation, suivre ce que dit la
  note, puis la supprimer, qu'il accepte ou non.
- Ne pas marquer `setup.styleChosen = true` sans choix explicite (garder le noir et blanc en est
  un). Ne jamais écraser une identité déjà renseignée. L'habillage ne filtre jamais le visage.
- Ne jamais inventer une identité « en attendant » : tokens `var(--brand-*)`, polices livrées,
  réglages éprouvés. `compositions/exemple-section.html` montre le niveau visuel attendu ; son
  sujet et ses timings sont un exemple, pas un scénario.

## 🧠 Préférences de montage apprises

À appliquer d'office à chaque vidéo. Elles priment sur les réglages par défaut, jamais sur une
demande explicite du moment. Si le client change d'avis, mets à jour `montage.preferences`
(après son OK sur la nouvelle formulation) puis `node scripts/sync.mjs`.

_Aucune pour l'instant : elles s'apprennent au débrief de la première vidéo._

---

## ⛔ Ordre séquentiel VERROUILLÉ (la règle qui casse le plus souvent)

On monte une vidéo **étape par étape, dans l'ordre ci-dessous**. **Ne JAMAIS proposer ni produire
une étape en avance.** Erreurs déjà commises à ne pas refaire :

- ❌ Proposer la **légende / le DM** pendant le script, le dérush ou le montage.
  → La publication (légende + DM) est **l'étape 7, la TOUTE DERNIÈRE**, seulement **après** montage
  validé **et** SFX/musique posés.
- ❌ Poser les **SFX / la musique** avant que {{FIRST_NAME}} ait **validé tout le montage** (étape 6 après 5).

**Seule exception : la première vidéo** (section 🟢 plus haut), montée d'une traite puis débriefée.

**Réflexe de début de session montage** : situer où on en est dans le pipeline, annoncer **la
prochaine étape (une seule)**, et ne pas déborder dessus.

---

## 🧭 Le pipeline en 7 étapes (aiguilleur)

Le détail de chaque étape vit dans son skill (source de vérité). Ici : quoi charger, quand, et la
barrière « terminé quand » à passer **avant de montrer le résultat à {{FIRST_NAME}} / passer à l'étape suivante**.

| # | Étape | {{FIRST_NAME}} dit… | Skill à charger AVANT d'agir | Terminé quand |
|---|-------|-----------|------------------------------|----------------|
| 1 | **Script** | « on brainstorm un script », « écris ma version », « voici mon script » | `reel-script` | Hook + corps + CTA, voix de {{FIRST_NAME}}, ~30-45 s, **validé**. Si CTA « commente [MOT] » → juste **noter le mot-clé** (le DM se rédige à l'étape 7, pas maintenant). |
| 2 | **Tournage** | ({{FIRST_NAME}} tourne la vidéo, puis) « voici la vidéo brute » | aucun | La vidéo brute est fournie. (Rappel : export **résolution MAX**, pas 1080p.) |
| 3 | **Dérush** | « fais les cuts », « coupe les blancs / les ratés », « clean l'audio » | `derush` | Re-transcription du cut = le script, **aucun mot coupé/doublé**, souffle inter-cut ≈ 0,1 s. **Voix nettoyée avec Adobe Podcast Enhance** (toujours, aucune autre méthode : l'utilisateur glisse un MP3, tu fais le reste). |
| 4 | **Montage / motion** | « passe au montage », « mets les split-screens / le motion / les sous-titres » | `motion-design` (+ `references/montage-talking-head.md`) | Chaque section montée : split-screen là où il faut, motion-first, visage net (pas de carré noir), sous-titres calés, safe-zones OK. |
| 5 | **Review** | « là je veux plutôt ça », « mets cette vidéo/image ici », « ça en plein écran », « les sous-titres vont pas » | (rester dans `motion-design`) | {{FIRST_NAME}} a **tout validé section par section** après ses retours. **C'est la barrière avant les SFX.** |
| 6 | **SFX + musique** | « mets le sound effect et la musique » | `motion-design` → `references/sfx-musique.md` | **Uniquement APRÈS validation étape 5.** SFX placés + musique posée. |
| 7 | **Publication** | « la légende », « le message DM » | `design-system/instagram-caption.md` + `manychat-dm.md` | **Toute fin.** Légende IG + (si CTA) DM prêts, dans la conversation et dans `publication.md` du Reel. Le mot « lien » **jamais écrit** → emoji 🔗. |

> **Export MP4** : pas une étape à part, l'acte technique qui produit la vidéo de review (étape 5)
> puis la finale (après 6). **Export natif** : le montage contient tout (visage pré-cadré, sons) ;
> dans l'app HyperFrames c'est le bouton **Export** (vidéo dans Téléchargements), ailleurs
> `npm run render` (`exports/FINAL.mp4`), que tu copies dans `~/Downloads` : `<nom du Reel>.mp4`,
> puis ` V2`, ` V3`… Détail : checklist Export. Les invitations de la CLI (avis, app, mise à jour) : ignore.

> 🖥️ **Dans l'app HyperFrames**, l'aperçu et l'export sont les siens : ne lance ni `npm run dev`
> ni rendu, dis « Clique sur **Export** en haut à droite ». Ses consignes limitent les retouches à
> `index.html`, `compositions/` et `assets/` ; pour le pipeline de ce fichier (dérush, outils,
> `work/`, `exports/`), ce fichier prime. Jamais `.thumbnails/`, `.hyperframes/`, `.claude/`, `renders/`.

> 🧹 **Étape 8 : ranger (après publication).** Reel posté → `python3 tools/ranger_reel.py` :
> vidéos finales copiées dans `~/Movies/reels-publies/<nom>/` (Windows : `~/Videos/…`), Reel
> marqué publié, dossier gardé (il se rouvre d'un clic dans l'app). `--alleger` efface en plus
> les rushes et les fichiers de travail. Détail : skill `motion-design` §12.3.

Étapes annexes : **vrai logo de toute marque nommée** (jamais une icône inventée) → skill `thesvg` · **SFX à trouver** → `design-system/sfx-sound-search.md` · **texte long / anti-slop** → `design-system/writing-anti-slop.md`.

---

## ⚡ Fluidité : faire vite, sans re-travail

Le temps part dans les **itérations**, presque jamais dans la machine (détail : skill
`motion-design` §12.2). Réflexes :

1. **Une session par grosse étape** (`/clear` entre les étapes lourdes ; première vidéo : jamais,
   la suite passe par `work/premiere-video.md`).
2. **Cadrer AVANT de produire l'asset** (dérush, b-roll, écran plein) : la cible demandée une fois ;
   dérush avec le bloc `derush` de `brand.config.json`, pas de re-tune au jugé.
3. **Valider le concept motion sur 1 snapshot** d'une section-témoin avant de décliner les autres.
4. **Contrôle visuel = `hyperframes snapshot`** ; le navigateur, pour la vidéo finale seulement.
   Assets versionnés dès le départ (`hook-broll-v2.mp4`…).
5. **Serveur preview lancé une fois** (`npm run dev` en arrière-plan) ; dans l'app, jamais.
6. **Éditer, pas réécrire** : `Edit` ciblé plutôt qu'un HTML entier. Réponses de review courtes.

---

## 🚫 Checklist anti-oubli (les règles atomiques qui sautent tout le temps)

À relire à chaque projet. Chaque règle a sa source complète dans le skill indiqué.

**Dérush (`derush`)**
- [ ] **Souffle inter-cut ≈ 0,1 s**, régulier : **resserrer les FINS de cut, JAMAIS les débuts** (attaques de voyelle fragiles). Coupes franches. *Valeurs exactes → `derush` §5 + bloc `derush` de `brand.config.json`.*
- [ ] Couper **dans les silences** (`silencedetect`), **jamais** sur un timestamp Whisper/LLM (ils dérivent).
- [ ] **Jamais `-v error` avec `silencedetect` / `volumedetect`** : ils loguent en *info*, `-v error` ne renvoie rien et on croit qu'il n'y a aucun silence.
- [ ] **Ne pas recopier les prises à la main** : `tools/cut_boundaries.py` lit les `ISLANDS` de `derush/build_derush.py` s'il existe (une seule source, impossible à désynchroniser).
- [ ] Selon la caméra (`derush.camera` = `{{CAMERA}}`) : certaines vidéos (ex. DJI) ont un 2ᵉ flux mjpeg (vignette) → mapper `[0:v:0]` explicitement.
- [ ] **Re-transcrire le cut final** pour vérifier : lecture = script, zéro mot coupé/doublé.
- [ ] **Dérush en pleine résolution** (pas de `scale`, crf 14) : l'export recadre le visage dedans. Le réduire en 1080 dès le dérush divise par ~2,5 le détail du visage.
- [ ] **Mesurer les VRAIS points de coupe** (`<cut>_cuts.json`, détection scene-change sur le fichier livré) : `derush` §7bis.

**Transcodage (`motion-design/references/transcodage-video.md`)**
- [ ] Vérifier `color_transfer` **AVANT** de transcoder : `bt709` = SDR direct (rien à faire) / `arib-std-b67` = HDR → tonemap obligatoire.
- [ ] `base.mp4` = le dérush **réduit en 1080×1920**, crf 14 (son + repli) ; le visage de l'export vient du dérush pleine résolution, pré-cadré par `tools/build_faces.py`.

**Montage / motion (`motion-design` + `references/montage-talking-head.md`)**
- [ ] **Frontières de section = `<cut>_cuts.json`**, JAMAIS les timestamps Whisper (ils démarrent 0,1-0,25 s trop tôt → on voit la fin de la prise précédente au passage plein-écran → split). Master, sous-comps et sous-titres lisent **la même source**.
- [ ] **MOTION FIRST, zéro redondance texte** : pas de gros texte qui redit la voix off / les sous-titres.
- [ ] Chaque section démarre sur le **cadrage par défaut** (`montage.defaultLayout` : `"split"` = visage en bas / motion en haut · `"faceplein"` = visage plein écran, motion par-dessus) ; {{FIRST_NAME}} décide ensuite section par section des passages en plein écran.
- [ ] **Bug « carré noir »** : tout élément plein cadre au-dessus du `<video>` visage = `background: transparent`. Visage = surface **plein cadre** + `clip-path` (jamais surface partielle).
- [ ] **Motion riche = partir d'un template du registry** (`hyperframes add <block>`, découverte via `hyperframes catalog`, skill `hyperframes-registry`) puis le personnaliser aux couleurs de la marque, plutôt que tout dessiner à la main : mieux fini, plus vite.
- [ ] **Ajout de sections = risque de collision `data-track-index`** : garder les tracks visage / voix off / sous-titres **bien au-dessus** des tracks de sections (elles gardent leurs index bas). Deux éléments qui se chevauchent sur le même track = l'un des deux disparaît au render.
- [ ] Entrées d'éléments : **`opacity` + `scale`** (un `x/y` d'entrée se décale avec le `translate` du studio) ; un déplacement (curseur, pastille) : `x/y`, jamais `left`/`top` (refusé par `npm run check`).
- [ ] **Safe-zone haute** : rien d'important dans les ~150 px du haut (Instagram cache le haut).
- [ ] **Safe-zone latérale** : rien d'important à moins de **~100 px** des bords gauche/droit, **en split ET en plein écran** (Instagram recadre les côtés). Le **ghost number** se pose en haut à droite du bloc qu'il numérote (quitte à passer derrière), **jamais collé au bord**.
- [ ] Charger `brand/fonts.css` + `brand/tokens.css` dans le `<head>` du **master** (sinon `var(--brand-*)` et polices cassées).
- [ ] **Pièges silencieux du RENDER** (invisibles au studio et à `npm run check` ; liste complète : `montage-talking-head.md` §0bis et §0ter) : toutes les sous-comps vivent dans **UN SEUL document** (CSS et sélecteurs GSAP scopés sous `#<composition-id>`, jamais `html, body { height: 920px }`) ; sous-comps référencées **depuis la racine** ; **B-roll dans le master**, jamais dans une sous-comp ; libs tierces dans le `<head>` du master ; **un seul sélecteur par tween** ; canvas/WebGL en `preserveDrawingBuffer: true`.
- [ ] **`python3 tools/check_export.py` sur chaque export** (vidéo de l'app : `python3 tools/check_export.py <fichier>`) : lui voit ces bugs. **Console du navigateur AVANT de deviner**.

**Sous-titres (`motion-design/references/sous-titres.md`)**
- [ ] **2-3 mots** par sous-titre, **pas de ponctuation finale**, **jamais à cheval sur 2 phrases**, jamais finir sur un mot faible.
- [ ] **Découper par unité grammaticale** : nom+adjectif et groupe verbal insécables ; **ne jamais orpheliner un adjectif ni fusionner deux unités** ; trop large → isoler le mot seul. `tools/montage_captions.py` = 1er jet, **re-couper avant de livrer** (`sous-titres.md` a le tableau d'exemples).
- [ ] Position : jointure (`y=920`) en split · `y≈1140` en plein visage (section `face`) · `y≈1100` en plein écran **B-ROLL** · `y≈1500` en plein motion.
- [ ] **Timing = les VRAIS MOTS** : lancer `python3 tools/build_words.py` une fois, sinon le timing est proportionnel au texte et **dérive** (jusqu'à +0,35 s de retard sur la voix).
- [ ] **Snap aux DEUX bords de section** : le 1er sous-titre démarre à `section.start`, le dernier finit à `section.end` (sinon il bave sur la section suivante).
- [ ] **Sous-titres section-aware** : si une même prise est scindée en deux sections, le générateur raisonne **par section** (frontières du master), jamais par prise ; sinon les sous-titres de la 2ᵉ section gardent la position/le timing de la 1ʳᵉ.
- [ ] CTA : **ne JAMAIS écrire « lien »** → emoji 🔗 (risque de shadowban).

**Export (`motion-design/references/montage-talking-head.md` §4)**
- [ ] **Export natif** : après tout dérush ou changement de cadrage, `python3 tools/build_faces.py` puis `python3 tools/build_master.py --write`. Le visage est pré-cadré en pleine résolution et posé sans agrandissement : net au rendu HyperFrames. Ne recalcule jamais un cadrage à la main (`tools/cadrage.py` sert l'aperçu et l'export).
- [ ] Dans l'app : bouton **Export** (MP4 1080p, 30 im/s). Ailleurs : `npm run render`. Secours si l'export natif déraille : `python3 tools/build_overlay.py --render`, `python3 tools/build_final.py`, puis `python3 tools/build_sfx.py --ffmpeg`.

**SFX + musique (`motion-design/references/sfx-musique.md`) : étape 6, après validation**
- [ ] **Seulement après validation complète du montage (étape 5).** Jamais au fil de l'eau.
- [ ] « mets le sound effect et la musique » = les SFX (dans l'app sans Pack SFX : bibliothèque HeyGen d'abord) + la musique `(aucune, à fournir)` à **-26.5 dB**, sauf indication contraire.
- [ ] Les sons se posent **dans le montage** : `python3 tools/build_sfx.py` (bloc SONS d'`index.html`, un clip par son dans l'app). Retouchés à la main ou dans l'app, ils ne sont plus écrasés : modifie le bloc, ou `--ecraser` pour repartir d'EVENTS. **Sons de l'app** (`find_sound_effect`, `find_music`) : jamais d'`<audio>` à la main, perdu au prochain master ; ils passent par cette liste (`sfx-musique.md`).
- [ ] Volumes SFX **rééquilibrés par niveau perçu** (pas un dB uniforme).
- [ ] **Un son étalé (riser) sort bien plus bas qu'un son percussif (shutter) au même dB** : vérifié, un riser posé au niveau des shutters passait **sous** la musique de fond.
- [ ] Contrôle sans écoute = **`python3 tools/build_sfx.py --probe`** (piste SFX seule, **48 kHz**). Ni soustraction de deux MP4 (erreur d'encodage AAC), ni mesure en 16 kHz (tue les aigus).

**Publication (`design-system/`) : étape 7, la dernière**
- [ ] Légende IG (`instagram-caption.md`) : si CTA « commente [MOT] », le CTA est la **1ʳᵉ ligne**. Aucun hashtag.
- [ ] DM (`manychat-dm.md`) **uniquement si** CTA mot-clé. `🔗` obligatoire, jamais « lien ». Demander l'URL réelle, ne jamais l'inventer.

**Self-checks (obligatoires)**
- [ ] `npm run check` après **chaque** modif `.html` : corriger toutes les erreurs avant de présenter le résultat, revoir ses avertissements avant render.
- [ ] Contrôle du **mouvement** après **chaque** modif d'animation : `npx hyperframes snapshot --at 0.3,1.2,2.5`, puis **regarder** les images (skill `motion-design`, « Motion self-check »).

---

## Skills framework : couche TECHNIQUE (⚠️ ne remplace JAMAIS le pipeline de ce fichier)

> ⛔ **RÈGLE DE PRIORITÉ.** Pour TOUT montage de reel, le **pipeline en 7 étapes de ce fichier
> est la seule route** : `reel-script` → `derush` → `motion-design`. Les skills HyperFrames sont
> une **référence technique** (« comment fait-on X »), **jamais un workflow de montage** : ni le
> router `hyperframes`, ni `talking-head-recut`, `general-video`, `motion-graphics`… sauf
> demande **explicite** d'un autre type de projet.

`hyperframes-core` (composition, `data-*`) · `hyperframes-animation`, `hyperframes-keyframes`
(animation seek-safe) · `hyperframes-audio` · `hyperframes-cli` · `hyperframes-registry`
(`hyperframes add`) · `media-use` · `motion-doctrine`, `seam-craft`, `cut-the-curve` · `animejs`,
`css-animations`, `lottie`, `three`, `waapi`, `tailwind`. Jamais `npx hyperframes skills update` : il installe
ses skills dans la config personnelle du client, ceux du dossier sont déjà à la bonne version.

## Commands

```bash
npm run dev          # serveur de preview (long-running : le garder vivant en background)
npm run check        # hyperframes check : lint, exécution, mise en page, mouvement, contraste
npm run render       # export final natif -> exports/FINAL.mp4 (dans l'app : bouton Export)
node scripts/sync.mjs   # régénère style, CLAUDE.md / AGENTS.md (maison, accueil, Reels) + skills
node scripts/app-hyperframes.mjs brancher   # une fois par ordinateur : l'app lit ces consignes
```

> **`npm run dev` bloque jusqu'à l'arrêt** : toujours le lancer en arrière-plan (Claude Code :
> `run_in_background: true`). En premier plan, il expire, le serveur meurt et la preview casse.

**Windows** : `python` (sinon `py`) là où les consignes et les skills écrivent `python3`. **Doc** : `npx hyperframes
docs <topic>` (hors ligne) ; complète via `https://hyperframes.heygen.com/llms.txt`, sans deviner d'URL.

## Structure du projet

- **Un Reel** (`reels/<nom>/`, un projet de l'app) : `index.html` (composition maître) ·
  `compositions/` (sous-compositions) · `derush/` (dérushs + coupes) · `assets/` (vidéos du Reel,
  polices, GSAP) · `brand/` (copie du style) · `tools/` (copie des outils ; ceux marqués
  « A CHAQUE REEL » appartiennent à ce Reel) · `work/` (fichiers de travail) · `meta.json`
- **Le dossier Monteur IA** : `brand.config.json` (réglages, source de vérité) ·
  `brand/` (style généré) · `assets/` (polices, logos, SFX, musique partagés) · `tools/` (outils
  source, copiés dans chaque Reel) · `templates/` (`AGENT.md.tpl`, `demo/` = gabarit d'un Reel) ·
  `design-system/` (légende, DM, SFX, anti-slop) · `scripts/` (`sync.mjs`, `app-hyperframes.mjs`)
  · l'accueil (vignette de l'app) · `reels/`

## Règles framework HyperFrames (rappel technique)

1. Tout élément timé porte `data-start`, `data-duration` et `data-track-index`.
2. Les éléments timés visibles **DOIVENT** avoir `class="clip"` (contrôle de visibilité). Exception connue : le `<video>` visage n'a PAS `class="clip"` (voir `motion-design/references/visage-carre-noir.md`).
2bis. **Toute balise `<video>` porte un `id`** : sans `id`, le runtime ne pilote pas sa lecture et la vidéo est **gelée** au render (bug silencieux : la preview studio peut sembler correcte).
2ter. **Le framework impose son cadrage (`object-fit`) sur les `<video>`** : pour un cadrage déterministe du visage, **pré-cropper le segment en ffmpeg** en amont ; pour un **zoom animé**, animer un `<div>` conteneur autour de la vidéo, jamais la `<video>` elle-même.
3. Les timelines GSAP sont **paused** et enregistrées sur `window.__timelines["composition-id"]`.
4. Les vidéos sont `muted` avec un `<audio>` séparé pour la piste son.
5. Les sous-compositions utilisent `data-composition-src="compositions/file.html"`.
6. Logique **déterministe** uniquement : pas de `Date.now()`, pas de `Math.random()`, pas de fetch réseau.
