# HyperFrames — Reels {{BRAND_NAME}} ({{BRAND_HANDLE}})

> ⚠️ **FICHIER GÉNÉRÉ** depuis `templates/AGENT.md.tpl` — ne pas éditer directement ;
> éditer le `.tpl` puis lancer `npm run sync`. (`CLAUDE.md` est lu par Claude Code, `AGENTS.md`
> par Codex : les deux sont produits par le même template et restent identiques, sauf la façon de
> charger un skill ci-dessous.)

> **Charger un skill** :
> Codex — **ouvre le fichier** `.agents/skills/<nom>/SKILL.md` indiqué et relis-le.

Ce projet sert **un seul format** : les Reels Instagram de {{FIRST_NAME}} ({{BRAND_HANDLE}}) =
**vraie vidéo talking-head + motion design {{BRAND_NAME}} par-dessus, section par section**, avec
sous-titres, SFX et musique. Format **vertical 1080×1920, 30 fps**.

> 🎨 **Style visuel actif : Papier (le style de départ) — prêt à monter, personnalisable plus tard** — fond `#f7f7f5`, accent `#131313`,
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

L'utilisateur vient pour monter sa vidéo. Parle simplement dans sa langue, avec chaleur, sans le
féliciter à chaque clic. Explique ce que tu fais et indique clairement **qui agit maintenant**.
Les commandes, chemins et diagnostics détaillés restent dans tes outils, sauf demande explicite
ou besoin réel de dépannage. Ne confonds pas une liste d'outils manquants avec des erreurs.

- **Installation** (« installe », « lis INSTALL.md », outils manquants) : lire `INSTALL.md` et
  suivre son parcours accompagné. Bilan lisible, action unique « réponds go », puis exécution.
  Ne lancer ni questionnaire de marque ni personnalisation pendant l'installation.
- **Tu travailles** : « Je prépare les sous-titres. Tu n'as rien à faire pour le moment. »
- **Il doit agir** : une seule consigne courte, puis attendre. Les permissions réelles de
  l'application restent nécessaires ; ne promettre ni zéro clic ni une réussite non vérifiée.
- **Validation créative** : présenter le résultat et demander un retour simple, pas un choix
  de codec, d'outil ou de modèle. Les validations du dérush et du montage restent obligatoires,
  **sauf pour la première vidéo** (section suivante) : elle se monte d'une traite, puis débrief.
- **Valeur `{{...}}` non renseignée** : c'est une personnalisation optionnelle. Ne jamais
  afficher ces marqueurs au client ni l'obliger à renseigner son identité pour monter.

## Langue de la conversation et langue des vidéos

- Réponds dans la langue demandée par l'utilisateur ; sinon, utilise la langue dans laquelle
  il te parle. Si une préférence est déjà enregistrée dans `brand.communicationLanguage`,
  conserve-la tant qu'il ne demande pas autre chose. Les exemples français des instructions
  sont des modèles de sens, pas une obligation de répondre en français.
- S'il demande de garder cette préférence, note-la dans `brand.communicationLanguage`.
  Ne traduis ni les noms de fichiers, ni les commandes, ni les identifiants techniques.
- La langue du contenu est distincte : `brand.language` et `derush.whisperLanguage` suivent
  la langue souhaitée pour les vidéos et la langue réellement parlée dans l'audio.
  Lors du premier montage, ne force pas le défaut français si le client annonce des vidéos
  en espagnol ou si l'audio est espagnol. Configure la transcription en conséquence.
- Transcris ce qui est prononcé, sans traduire silencieusement l'audio. Les sous-titres doivent
  correspondre à la piste finale. Une traduction de voix se prépare et se valide séparément.
- Comprends les demandes de montage, setup, stories ou double formulées en espagnol comme
  leurs équivalents français. En Espagne, utilise un espagnol courant avec « tú ».

## 🟢 Première vidéo : tout monter d'une traite, puis apprendre de ses retours

**État : première vidéo pas encore faite.** C'est la première vidéo tant que
`setup.firstVideoDone` n'est pas `true` dans `brand.config.json`, **sauf** si une vidéo a déjà
été livrée : archive des reels clôturés non vide (`~/Movies/reels-publies/` sur Mac,
`~/Videos/reels-publies/` sur Windows, hors du projet) ou `work/premiere-video.md` qui annonce
« débrief à faire ». Dans ces deux cas, la vidéo suivante suit l'ordre verrouillé normal.
Le setup n'est jamais un prérequis.

Un débutant ne sait pas décrire son style ; devant sa propre vidéo montée, il sait dire ce qu'il
aime ou pas. Donc : **aucune question avant**, un montage complet avec les réglages de base,
puis un **débrief** où il dit ce qu'il aurait fait autrement, et tu retiens tout.

1. **Il envoie sa vidéo brute** (sinon, demande seulement de la glisser ici). Annonce une fois :
   > « Je m'occupe de tout le montage avec les réglages de base, sans te poser de questions :
   > coupes, sous-titres, animations, bruitages. Habillage noir et blanc, ta vidéo reste en
   > couleur. Ça me prend un moment, tu peux faire autre chose. Quand c'est prêt, tu me diras
   > tout ce que tu aurais fait autrement, et j'apprendrai ton style pour les prochaines. »
2. **Monte d'une traite** : dérush (3) → montage (4) → export → SFX (6). **Exception à l'ordre
   verrouillé, pour cette vidéo seulement** : pas d'écoute du dérush, pas de revue section par
   section, pas d'accord avant les SFX. Les **contrôles automatiques restent obligatoires**
   (re-transcription = texte prononcé, `_cuts.json`, `npm run check`, snapshots,
   `check_export.py`) : tu valides toi-même ce que le client aurait validé.
   Réglages de base : style Papier, cadrage `split` adapté au visage réel, SFX d'`assets/sfx/`,
   pas de musique, **voix brute** (le nettoyage Adobe demande une action du client : il est
   proposé au débrief). Méthode : skill `motion-design`, `references/premier-montage.md`.
   Ne t'arrête que sur un vrai blocage (vidéo illisible, outil en panne), avec une seule consigne.
3. **Tiens `work/premiere-video.md` à jour** : étapes faites, prochaine étape, fichiers produits.
   Si la session s'interrompt (quota atteint, fenêtre fermée), reprends depuis ce fichier sans
   refaire ce qui est fait ni reposer de question. Ne demande pas de `/clear` au client.
4. **Livre la vidéo** (`renders/` + copie dans Téléchargements), puis **ouvre le débrief** :
   charge le skill `setup` et suis `references/debrief-premiere-video.md`.
5. **Applique ses retours à cette vidéo** (c'est la review, étape 5), ré-exporte, puis
   **enregistre ses préférences** après son OK sur le résumé, passe `setup.firstVideoDone` à
   `true` et lance `npm run sync`. Ensuite seulement : proposer la légende (étape 7).

**Dès la deuxième vidéo**, l'ordre verrouillé et toutes ses validations s'appliquent, avec les
préférences apprises (section suivante) appliquées d'office.

- Le questionnaire `/setup` reste disponible à tout moment (« personnalise mon style ») ; ne le
  lance pas de toi-même. Le débrief, lui, fait partie de la première vidéo.
- **Débrief repoussé** : si `work/premiere-video.md` annonce « débrief à faire » (la note survit
  à la clôture du reel), le reproposer une fois en début de conversation, suivre ce que dit la
  note, puis la supprimer, qu'il accepte ou non.
- Ne pas marquer `setup.styleChosen = true` sans choix explicite (garder le noir et blanc en est
  un). Ne jamais écraser une identité déjà renseignée. L'habillage ne filtre jamais le visage.
- Ne jamais inventer une identité « en attendant » : tokens `var(--brand-*)`, polices livrées,
  réglages éprouvés. `compositions/exemple-section.html` montre le niveau visuel attendu ; son
  sujet et ses timings sont un exemple, pas un scénario.

## 🧠 Préférences de montage apprises

À appliquer d'office à chaque vidéo. Elles priment sur les réglages par défaut, jamais sur une
demande explicite du moment. Si le client change d'avis, mets à jour `montage.preferences`
(après son OK sur la nouvelle formulation) puis `npm run sync`.

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
| 2 | **Tournage** | ({{FIRST_NAME}} tourne la vidéo, puis) « voici la vidéo brute » | — | La vidéo brute est fournie. (Rappel : export **résolution MAX**, pas 1080p.) |
| 3 | **Dérush** | « fais les cuts », « coupe les blancs / les ratés », « clean l'audio » | `derush` | Re-transcription du cut = le script, **aucun mot coupé/doublé**, souffle inter-cut ≈ 0,1 s. **Voix nettoyée avec Adobe Podcast Enhance** (toujours, aucune autre méthode : l'utilisateur glisse un MP3, tu fais le reste). |
| 4 | **Montage / motion** | « passe au montage », « mets les split-screens / le motion / les sous-titres » | `motion-design` (+ `references/montage-talking-head.md`) | Chaque section montée : split-screen là où il faut, motion-first, visage net (pas de carré noir), sous-titres calés, safe-zones OK. |
| 5 | **Review** | « là je veux plutôt ça », « mets cette vidéo/image ici », « ça en plein écran », « les sous-titres vont pas » | (rester dans `motion-design`) | {{FIRST_NAME}} a **tout validé section par section** après ses retours. **C'est la barrière avant les SFX.** |
| 6 | **SFX + musique** | « mets le sound effect et la musique » | `motion-design` → `references/sfx-musique.md` | **Uniquement APRÈS validation étape 5.** SFX d'`assets/sfx/` placés + musique posée. |
| 7 | **Publication** | « la légende », « le message DM » | `design-system/instagram-caption.md` + `manychat-dm.md` | **Toute fin.** Légende IG + (si CTA) DM prêts. Le mot « lien » **jamais écrit** → emoji 🔗. |

> **Export MP4** : ce n'est pas une étape à part, c'est l'acte technique qui produit la vidéo pour la
> review (étape 5) puis la version finale (après 6). Toujours **en ffmpeg**, jamais `npm run render`
> (voir checklist). Fichiers dans `renders/` + copie dans `~/Downloads`.

> 🧹 **Étape 8 — Clôture (après publication).** Une fois le reel posté, on remet le plan de
> travail à zéro : `python3 tools/close_reel.py <slug>`. Le script archive l'état final
> (**aucun compte GitHub ni push requis, tout est local** : avec git il committe et tague
> `reel/<slug>` tout seul, en initialisant un repo local au besoin ; sans git il copie le
> projet du reel vers le dossier Vidéos), copie les masters `renders/*FINAL*` vers
> `~/Movies/reels-publies/<slug>/` (Windows : `~/Videos/…`, hors du projet), vide `renders/`, `work/`, `derush/`, `compositions/`,
> `assets/video/` et les restes à la racine (`snapshots/`, `probe/`, `overlay.html`), en gardant
> une note « débrief à faire » si le débrief de la première vidéo n'a pas eu lieu, puis
> remet les fichiers livrés depuis `templates/demo/` (master d'aperçu, placeholder `base.mp4`,
> outils du reel remis en mode démo) : le projet redevient celui d'un ZIP neuf, réglages du
> client intacts (`brand.config.json`, ses assets). **Ne JAMAIS archiver un vieux reel dans un dossier du
> projet** (le studio scanne tout le projet → il polluerait la sidebar de l'éditeur) : la
> récupération se fait via `git checkout reel/<slug> -- <chemins>` (ou le dossier copié).

Étapes annexes au besoin : **logos** → skill `thesvg` · **SFX à trouver** → `design-system/sfx-sound-search.md` · **texte long / anti-slop** → `design-system/writing-anti-slop.md`.

---

## ⚡ Fluidité — faire vite, sans re-travail

> Constat d'audit : le **compute réel** (ffmpeg/whisper/render) pèse à peine **~2-3 %** du temps.
> Le temps part dans les **itérations** (assets refaits 4-6×) et le **volume de sortie**
> (réécritures HTML entières, longs messages), jamais dans la machine. Réflexes anti-lenteur :

1. **Une session par grosse étape.** Ne pas enchaîner script → dérush → montage → SFX → publication
   dans un seul contexte (contexte saturé → auto-compaction en plein montage). `/clear`
   entre les étapes lourdes. Première vidéo : pas de `/clear` demandé au client, la continuité
   passe par `work/premiere-video.md`.
2. **Cadrer AVANT de produire l'asset** (dérush, b-roll, écran plein) : demander la cible
   précise **une seule fois** au lieu de deviner par itérations. Dérush → appliquer d'emblée les
   valeurs du bloc `derush` de `brand.config.json` (`padStart`, `padEnd`, `silenceDb`,
   `islandDuration`), pas de re-tune au jugé.
3. **Valider le CONCEPT motion sur 1 snapshot** d'une section-témoin **avant** de décliner toutes les
   sections → évite les refontes « c'est moche ».
4. **Un seul contrôle visuel : `hyperframes snapshot`** (déterministe, zéro cache navigateur). Le
   navigateur sert **uniquement au visionnage de la vidéo finale**. **Versionner les assets dès le
   départ** (`hook-broll-v2.mp4`…) pour ne jamais se battre avec le cache studio.
5. **Serveur preview vivant toute la session** (`npm run dev` en `run_in_background`, lancé une fois)
   — ne pas le tuer/relancer.
6. **Éditer, pas réécrire** : `Edit` ciblé plutôt que `Write` d'un HTML entier (chaque réécriture
   coûte 9-23 s). Réponses de review courtes. Peu de délibération sur le rote (lint, transcode, remux).
7. **hyperframes en local** (`npm i -D hyperframes`) plutôt que `npx --yes hyperframes@version`
   (re-résolution réseau à chaque appel).

---

## 🚫 Checklist anti-oubli (les règles atomiques qui sautent tout le temps)

À relire à chaque projet. Chaque règle a sa source complète dans le skill indiqué.

**Dérush (`derush`)**
- [ ] **Souffle inter-cut ≈ 0,1 s**, régulier : **resserrer les FINS de cut, JAMAIS les débuts** (attaques de voyelle fragiles). Coupes franches. *Valeurs exactes → `derush` §5 + bloc `derush` de `brand.config.json`.*
- [ ] Couper **dans les silences** (`silencedetect`), **jamais** sur un timestamp Whisper/LLM (ils dérivent).
- [ ] **Jamais `-v error` avec `silencedetect` / `volumedetect`** : ces filtres loguent en *info*, `-v error` renvoie zéro ligne et on croit qu'il n'y a aucun silence.
- [ ] **Ne pas recopier les prises à la main** : `tools/cut_boundaries.py` lit les `ISLANDS` de `derush/build_derush.py` s'il existe — une seule source, impossible de les désynchroniser.
- [ ] Selon la caméra (`derush.camera` = `{{CAMERA}}`) : certaines vidéos (ex. DJI) ont un 2ᵉ flux mjpeg (vignette) → mapper `[0:v:0]` explicitement.
- [ ] **Re-transcrire le cut final** pour vérifier : lecture = script, zéro mot coupé/doublé.
- [ ] **Dérush en pleine résolution** (template : pas de `scale`, crf 14) : l'export recadre le visage dedans. Le réduire en 1080 dès le dérush divise par ~2,5 le détail du visage.
- [ ] **Mesurer les VRAIS points de coupe** (`<cut>_cuts.json`, détection scene-change sur le fichier livré) — cf `derush` §7bis.

**Transcodage (`motion-design/references/transcodage-video.md`)**
- [ ] Vérifier `color_transfer` **AVANT** de transcoder : `bt709` = SDR direct (rien à faire) / `arib-std-b67` = HDR → tonemap obligatoire.
- [ ] `base.mp4` = le dérush **réduit en 1080×1920**, crf 14 (studio + son) ; export final en **crf 16**, visage relu dans le dérush pleine résolution par `build_final.py`.

**Montage / motion (`motion-design` + `references/montage-talking-head.md`)**
- [ ] **Frontières de section = `<cut>_cuts.json`**, JAMAIS les timestamps Whisper (ils démarrent 0,1-0,25 s trop tôt → on voit la fin de la prise précédente au passage plein-écran → split). Master, sous-comps et sous-titres lisent **la même source**.
- [ ] **MOTION FIRST, zéro redondance texte** : pas de gros texte qui redit la voix off / les sous-titres.
- [ ] Chaque section démarre sur le **cadrage par défaut** (`montage.defaultLayout` : `"split"` = visage en bas / motion en haut · `"faceplein"` = visage plein écran, motion en surimpression transparente) ; {{FIRST_NAME}} dit ensuite section par section ce qui passe en plein écran visage ou plein écran visuel.
- [ ] **Bug « carré noir »** : tout élément plein cadre au-dessus du `<video>` visage = `background: transparent`. Visage = surface **plein cadre** + `clip-path` (jamais surface partielle).
- [ ] **Motion riche = partir d'un template du registry** (`hyperframes add <block>`, découverte via `hyperframes catalog` — skill `hyperframes-registry`) puis le personnaliser aux couleurs de la marque, plutôt que tout dessiner à la main : mieux fini, plus vite.
- [ ] **Ajout de sections = risque de collision `data-track-index`** : garder les tracks visage / voix off / sous-titres **bien au-dessus** des tracks de sections (elles gardent leurs index bas). Deux éléments qui se chevauchent sur le même track = l'un des deux disparaît au render.
- [ ] Entrées d'éléments : animer **`opacity` + `scale` uniquement**, jamais `x/y` (sinon décalage avec le `translate` du studio).
- [ ] **Safe-zone haute** : rien d'important dans les ~150 px du haut (Instagram cache le haut).
- [ ] **Safe-zone latérale** : rien d'important à moins de **~100 px** des bords gauche/droit — **en split ET en plein écran** (Instagram recadre les côtés). Le **ghost number** se pose en haut à droite du bloc qu'il numérote (quitte à passer derrière), **jamais collé au bord**.
- [ ] Charger `brand/fonts.css` + `brand/tokens.css` dans le `<head>` du **master** (sinon `var(--brand-*)` et polices cassées).
- [ ] **Au RENDER, toutes les sous-comps vivent dans UN SEUL document** (le studio, lui, les isole en iframes → il ne montre RIEN de ces bugs) :
  - jamais de `html, body { height: 920px }` dans une sous-comp (ça rogne tout le calque à 920 px) ;
  - **scoper** CSS et sélecteurs GSAP sous `#<composition-id>` (un `#win` nu attrape celui d'une autre section) ; ids internes → **classes** ; timeline dans une **IIFE**.
  - le **calque d'export doit être à la RACINE** (`compositions/…`, jamais `../compositions/…`) : sinon les `<script>` des sous-comps ne sont pas montés et **aucune animation ne tourne**.
- [ ] **`python3 tools/check_export.py` après chaque rendu du calque** : `npm run check` ne voit pas ces bugs, lui si.
- [ ] **Un B-ROLL vit dans le MASTER, jamais dans une sous-comp** (`{"media": "…"}` dans `tools/sections.py`) : le `data-start="0"` d'une `<video>` de sous-comp est lu en **absolu** → elle s'affiche dès 0 s et recouvre les autres sections.
- [ ] **Les `<script src>` d'une sous-comp ne sont PAS chargés en composition par couches** → toute lib tierce (three.js, plugins) va dans le `<head>` du **master**.
- [ ] **`tl.seek()` supprime les callbacks GSAP** → un `onUpdate` qui redessine un canvas ne tourne pas en preview studio ; doubler d'un `gsap.ticker.add()` (sûr si le dessin est analytique).
- [ ] **UN SEUL sélecteur par tween** : `tl.to([sel1, sel2], …)` est **silencieusement ignoré** dans une sous-comp (console : `GSAP target … not found`).
- [ ] Canvas / WebGL → **`preserveDrawingBuffer: true`** (sinon snapshot et render tout **noirs**) et `setPixelRatio` fixe.
- [ ] **Console du navigateur AVANT de deviner** : ces bugs sont invisibles au lint et n'apparaissent souvent qu'en preview.

**Sous-titres (`motion-design/references/sous-titres.md`)**
- [ ] **2-3 mots** par sous-titre, **pas de ponctuation finale**, **jamais à cheval sur 2 phrases**, jamais finir sur un mot faible.
- [ ] **Découper par unité grammaticale** : nom+adjectif et groupe verbal insécables ; **ne jamais orpheliner un adjectif ni fusionner deux unités** ; trop large → isoler le mot seul. `tools/montage_captions.py` = 1er jet, **re-couper avant de livrer** (`sous-titres.md` a le tableau d'exemples).
- [ ] Position : jointure (`y=920`) en split · `y≈1140` en plein visage · `y≈1500` en plein motion.
- [ ] **Timing = les VRAIS MOTS** : lancer `python3 tools/build_words.py` une fois, sinon le timing est proportionnel au texte et **dérive** (jusqu'à +0,35 s de retard sur la voix).
- [ ] **Snap aux DEUX bords de section** : le 1er sous-titre démarre à `section.start`, le dernier finit à `section.end` (sinon il bave sur la section suivante).
- [ ] Plein écran **B-ROLL** → `y≈1100` · section **`face`** (visage plein écran) → `y≈1140`.
- [ ] **Sous-titres section-aware** : si une même prise est scindée en deux sections, le générateur raisonne **par section** (frontières du master), jamais par prise — sinon les sous-titres de la 2ᵉ section gardent la position/le timing de la 1ʳᵉ.
- [ ] CTA : **ne JAMAIS écrire « lien »** → emoji 🔗 (risque de shadowban).

**Export (`motion-design/references/montage-talking-head.md` §4)**
- [ ] Export = **ffmpeg**, **PAS `npm run render`** (le render HyperFrames ramollit le visage).
- [ ] L'export final se lance avec **`python3 tools/build_final.py`** : il dérive le crop du visage de `brand.config.json` (ou le calcule depuis le `transform`, `transform-origin` compris). Ne pas réécrire la commande ffmpeg à la main — un crop faux passe inaperçu jusqu'à l'export.

**SFX + musique (`motion-design/references/sfx-musique.md`) — étape 6, après validation**
- [ ] **Seulement après validation complète du montage (étape 5).** Jamais au fil de l'eau.
- [ ] « mets le sound effect et la musique » = les SFX d'`assets/sfx/` + la musique `(aucune — à fournir)` à **-26.5 dB**, sauf indication contraire.
- [ ] Volumes SFX **rééquilibrés par niveau perçu** (pas un dB uniforme).
- [ ] **Un son étalé (riser) sort bien plus bas qu'un son percussif (shutter) au même dB** : vérifié, un riser posé au niveau des shutters passait **sous** la musique de fond.
- [ ] Contrôle sans écoute = **`python3 tools/build_sfx.py --probe`** (piste SFX seule, **48 kHz**). Ni soustraction de deux MP4 (erreur d'encodage AAC), ni mesure en 16 kHz (tue les aigus).

**Publication (`design-system/`) — étape 7, la dernière**
- [ ] Légende IG (`instagram-caption.md`) : si CTA « commente [MOT] », le CTA est la **1ʳᵉ ligne**. Aucun hashtag.
- [ ] DM (`manychat-dm.md`) **uniquement si** CTA mot-clé. `🔗` obligatoire, jamais « lien ». Demander l'URL réelle, ne jamais l'inventer.

**Self-checks (obligatoires)**
- [ ] `npm run check` après **chaque** modif `.html`.
- [ ] Contrôle du **mouvement** après **chaque** modif d'animation (voir « Motion self-check » plus bas).

---

## Skills framework — couche TECHNIQUE (⚠️ ne remplace JAMAIS le pipeline de ce fichier)

> ⛔ **RÈGLE DE PRIORITÉ.** Pour TOUT montage de reel, le **pipeline en 7 étapes de ce fichier
> est la seule route** : `reel-script` → `derush` → `motion-design`. Les skills officiels
> HyperFrames ci-dessous sont une **RÉFÉRENCE TECHNIQUE à consulter** (« comment fait-on X dans
> le framework »), **PAS un workflow de montage**. Ne JAMAIS router le montage d'un reel via le
> skill `hyperframes` (son router) ni via un workflow générique du framework
> (`talking-head-recut`, `product-launch-video`, `faceless-explainer`, `slideshow`,
> `motion-graphics`, `general-video`…). Ces workflows ne servent QUE si {{FIRST_NAME}} demande
> **explicitement** un autre type de projet, hors du workflow reel habituel.

Ces skills encodent les patterns HyperFrames (`window.__timelines`, sémantique des `data-*`,
media géré par le runtime, CSS shader-compatible) absents des docs web génériques. **Consulter
le bon skill technique évite de tâtonner** (ex. une `<video>` a besoin d'un `id` sinon elle gèle
au render ; le framework impose son cadrage sur les `<video>` → pré-cropper en ffmpeg pour un
cadrage déterministe).

| Skill                      | Command                   | Quand l'utiliser                                                                 |
| -------------------------- | ------------------------- | -------------------------------------------------------------------------------- |
| **hyperframes**            | `/hyperframes`            | Router officiel (⛔ hors route pour les reels — voir règle de priorité)           |
| **hyperframes-core**       | `/hyperframes-core`       | Contrat de composition : `data-*`, `class="clip"`, tracks, sous-compositions      |
| **hyperframes-animation**  | `/hyperframes-animation`  | Animation (ex-`gsap`) : règles de motion, blueprints, GSAP/Lottie/CSS/WAAPI       |
| **hyperframes-keyframes**  | `/hyperframes-keyframes`  | Keyframes seek-safe, FLIP, paths, masks, diagnostics `hyperframes keyframes`      |
| **hyperframes-creative**   | `/hyperframes-creative`   | Direction créative : palettes, typo, beats, patterns de composition               |
| **hyperframes-cli**        | `/hyperframes-cli`        | Boucle dev CLI : init, lint, check, preview, render, doctor                       |
| **hyperframes-registry**   | `/hyperframes-registry`   | Installer des blocks/composants via `hyperframes add`                             |
| **media-use**              | `/media-use`              | Médias (ex-`hyperframes-media`) : SFX, musique, images, TTS, transcription        |
| **motion-doctrine / seam-craft / cut-the-curve** | `/<nom>`    | Doctrine motion : qualité du mouvement, transitions, courbes                      |
| **website-to-hyperframes** | `/website-to-hyperframes` | Capturer une URL et la transformer en vidéo                                       |
| **animejs / css-animations / lottie / three / waapi / tailwind** | `/<nom>` | Selon la techno d'animation utilisée                        |

> **Mise à jour des skills framework** : `npx hyperframes skills update` (ils s'installent en
> global dans `~/.claude/skills/` et `~/.agents/skills/`, et s'auto-mettent à jour — le repo
> embarque une copie qui marche dès le clone, mais cette commande donne toujours la dernière
> version). Skills absents ? Même commande, puis redémarrer la session.

## Commands

```bash
npm run dev          # serveur de preview (long-running — le garder vivant en background)
npm run check        # lint + validate + inspect
npm run render       # rend en MP4 (⚠️ PAS l'export final — voir checklist Export : ffmpeg)
npm run sync         # régénère CLAUDE.md / AGENTS.md + miroir des skills métier vers .agents/
npx hyperframes lint --verbose  # inclut les findings info
npx hyperframes lint --json     # sortie machine pour CI
npx hyperframes docs <topic>    # docs de référence dans le terminal
```

> **`npm run dev` est un serveur long-running, pas une commande one-shot.** Il bloque jusqu'à
> l'arrêt. Dans Claude Code, **toujours le lancer avec `run_in_background: true`**. Jamais en
> foreground — il timeout et le serveur meurt, ce qui casse la preview navigateur.

## Documentation

**Référence rapide** (pas de réseau) : `npx hyperframes docs <topic>`
Topics : `data-attributes`, `gsap`, `compositions`, `rendering`, `examples`, `troubleshooting`

**Doc complète** : découvrir les pages via l'index machine — ne PAS deviner les URLs :
`https://hyperframes.heygen.com/llms.txt`

## Structure du projet

- `index.html` — composition maître (root timeline)
- `compositions/` — sous-compositions référencées via `data-composition-src`
- `brand/` — design system branché dans les compositions (`tokens.css`, `fonts.css`, `motion.js`, `atoms.html`)
- `brand.config.json` — réglages personnalisés (généré par `/setup`) · source de vérité des valeurs
- `templates/` — templates dépersonnalisés (`AGENT.md.tpl`, `tokens.css.tpl`, `voice-profile.md.tpl`) ; `templates/demo/` = copie des fichiers livrés, remise en place par `tools/close_reel.py` (ne pas éditer pendant un montage)
- `scripts/` — outils du template (`sync.mjs` : régénère `CLAUDE.md`/`AGENTS.md` + miroir skills)
- `tools/` — utilitaires Python du pipeline (`montage_captions.py`, `check_export.py`, `cut_boundaries.py`…)
- `design-system/` — docs publication + recherche (légende IG, DM, SFX, anti-slop)
- `derush/` — dérushs + timelines JSON par vidéo
- `assets/` — médias (video, audio, images, logos, fonts, sfx, music)
- `work/` — fichiers de travail temporaires (non versionnés)
- `renders/` — exports MP4 (garder le plus complet)
- `meta.json` — métadonnées projet · `transcript.json` — transcript Whisper mot-à-mot (si généré)

## Linting — TOUJOURS LANCER APRÈS MODIFICATION

Après avoir créé ou édité une composition `.html`, **toujours** lancer avant de considérer la
tâche terminée :

```bash
npm run check
```

Corriger toutes les erreurs avant de présenter le résultat. Revoir les warnings d'inspect avant render.

## Motion self-check — APRÈS TOUTE MODIF D'ANIMATION

`npm run check` valide la structure, pas le **mouvement**. Après avoir écrit/modifié des
animations (GSAP/CSS/Anime), vérifier aussi le mouvement.

**Toujours disponible** : des images à des instants choisis (début, pendant l'entrée, fin de
chaque animation), puis les regarder réellement :

```bash
npx hyperframes snapshot --at 0.3,1.2,2.5
```

**Si ta version de la CLI a la commande `keyframes`** (`npx hyperframes --help` la liste ; ce n'est
pas le cas de la version épinglée dans ce projet), elle ajoute un diagnostic détaillé :

```bash
npx hyperframes keyframes compositions/<scene>.html          # tweens + timing + valeurs
npx hyperframes keyframes compositions/<scene>.html --shot out.png [--selector "#el"] [--layout strip]
```

- Vérifier que chaque tween tombe sur le bon temps du voiceover.
- Un sélecteur `__unresolved__` (keyframes) ou un élément resté figé d'une image à l'autre
  (snapshots) = bug silencieux à corriger. La console du navigateur signale aussi
  `GSAP target … not found`.
- Pour toute motion non triviale (arc, stagger, pulse), regarder la trajectoire sur plusieurs
  images **avant** le render final.

## Règles framework HyperFrames (rappel technique)

1. Tout élément timé porte `data-start`, `data-duration` et `data-track-index`.
2. Les éléments timés visibles **DOIVENT** avoir `class="clip"` (contrôle de visibilité). Exception connue : le `<video>` visage n'a PAS `class="clip"` (voir `motion-design/references/visage-carre-noir.md`).
2bis. **Toute balise `<video>` porte un `id`** — sans `id`, le runtime ne pilote pas sa lecture et la vidéo est **gelée** au render (bug silencieux : la preview studio peut sembler correcte).
2ter. **Le framework impose son cadrage (`object-fit`) sur les `<video>`** : pour un cadrage déterministe du visage, **pré-cropper le segment en ffmpeg** en amont ; pour un **zoom animé**, animer un `<div>` conteneur autour de la vidéo, jamais la `<video>` elle-même.
3. Les timelines GSAP sont **paused** et enregistrées sur `window.__timelines` :
   ```js
   window.__timelines = window.__timelines || {};
   window.__timelines["composition-id"] = gsap.timeline({ paused: true });
   ```
4. Les vidéos sont `muted` avec un `<audio>` séparé pour la piste son.
5. Les sous-compositions utilisent `data-composition-src="compositions/file.html"`.
6. Logique **déterministe** uniquement — pas de `Date.now()`, pas de `Math.random()`, pas de fetch réseau.
