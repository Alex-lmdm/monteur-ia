---
name: setup
description: >-
  L'Empreinte — l'onboarding de personnalisation du Monteur IA. Lance-le UNE fois après
  l'installation pour transférer TON goût (ta voix, tes couleurs, ton funnel, ton cadrage) à ton
  monteur. Use when the user says "setup", "configure mon système", "onboarding", "empreinte",
  "personnalise mon monteur", "je viens d'installer", ou au tout premier lancement du template.
  Aussi : `/setup <bloc>` (identite, voix, funnel, visuel, derush, technique) pour refaire un bloc.
---

# L'Empreinte — onboarding de personnalisation

> **Ce n'est pas configurer un logiciel. C'est transférer ton goût à une IA, une seule fois.**
> À la fin, ton monteur écrit dans TA voix, monte à TES couleurs, cadre TON visage et parle à TON
> audience. Tu ne referas jamais ce réglage (sauf si tu changes de style : `/setup <bloc>`).

Ce skill pilote un questionnaire chaleureux en **6 blocs (A → F)**, un bloc à la fois. Chaque
réponse va dans un seul fichier de vérité — `brand.config.json` à la racine du projet — puis on
**régénère** les fichiers du monteur depuis ce config (jamais l'inverse, jamais à la main).

L'utilisateur **n'est pas développeur.** Zéro jargon. Une question à la fois. Toujours un défaut
prêt (« appuie sur Entrée pour garder le réglage recommandé »).

---

## Principes de fonctionnement (à respecter à la lettre)

1. **6 blocs, dans l'ordre, un seul à la fois.** A Identité → B Voix → C Funnel/CTA → D Visuel →
   E Dérush/audio → F Technique + calibration. On ne déborde jamais sur le bloc suivant.
   `/setup <bloc>` refait un bloc isolé : `a`/`identite`, `b`/`voix`, `c`/`funnel`, `d`/`visuel`,
   `e`/`derush`, `f`/`technique`.

   🎨 **Le bloc D (Visuel) passe TOUJOURS en premier**, quel que soit l'ordre habituel. C'est le
   seul réglage qu'on ne peut pas deviner : le style de départ « Papier » (noir & blanc) rend bien,
   mais ne contient aucune couleur à lui. Si l'utilisateur arrive en disant « monte ma vidéo » sans
   setup, **propose le bloc D** (2 minutes, 3 questions) — et **s'il préfère voir d'abord, monte en
   Papier sans insister**, puis repropose une fois la vidéo livrée. Les 5 autres blocs restent
   optionnels et se font quand il veut.

2. **`brand.config.json` = source de vérité unique.** Au démarrage : lire `brand.config.json` à la
   racine. **S'il n'existe pas**, le créer en copiant `brand.config.example.json` (défauts
   recommandés, éprouvés en production : pads 0.04/0.02, silence -40 dB, musique -26,5 dB ; le
   cadrage split, lui, sera calibré au bloc F). Lire ensuite `setup.completedBlocks` pour savoir
   où on en est.

3. **Reprise annoncée.** Au début, dire clairement l'état : « Tu as déjà fait A et B. On reprend au
   bloc C (Funnel) ? » S'il n'y a rien de fait : « On commence par le bloc A (ton identité). » Ne
   jamais recommencer un bloc validé sans que l'utilisateur le demande.

4. **AUCUNE écriture avant validation explicite.** À la fin de chaque bloc, **récapituler ce qu'on
   va écrire** (les valeurs + les fichiers touchés), puis **attendre un OK clair**. Tant que
   l'utilisateur n'a pas validé, on ne touche à aucun fichier.

5. **Écritures déterministes, régénérées depuis les templates.** On ne patche jamais un fichier
   ligne par ligne. On remplit `brand.config.json`, puis on **régénère** les zones concernées depuis
   `templates/*.tpl` + le config.

   **Cas particulier du design system** : `brand/tokens.css` et `brand/fonts.css` sont
   **entièrement générés** par `node scripts/sync.mjs` (ils ne sont pas versionnés). On ne les
   édite JAMAIS à la main, ni par marqueurs : on écrit `visual.*` dans `brand.config.json` et on
   lance le sync. Toute couleur écrite à la main dans ces fichiers sera perdue au sync suivant.

   Pour les fichiers markdown, les zones générées sont encadrées par des marqueurs :
   ```
   <!-- BEGIN GENERATED: <clef> -->
   ...contenu régénéré...
   <!-- END GENERATED: <clef> -->
   ```
   (En CSS/JS : `/* BEGIN GENERATED: <clef> */ … /* END GENERATED: <clef> */`.)
   **Ne jamais écraser quoi que ce soit HORS de ces marqueurs** sans confirmation explicite. Si un
   fichier cible n'a pas encore ses marqueurs, les insérer proprement une première fois (en
   montrant l'emplacement à l'utilisateur).

6. **Après chaque bloc validé :** (a) mettre à jour `setup.completedBlocks` dans `brand.config.json`
   (ajouter la lettre du bloc), puis (b) lancer `node scripts/sync.mjs` — c'est lui qui régénère
   `CLAUDE.md` + `AGENTS.md` et met à jour le miroir des skills à partir du config. Confirmer à
   l'utilisateur : « Bloc X enregistré, ton monteur est à jour. »

7. **Ton chaleureux, humain, concret.** On explique le POURQUOI en une phrase simple quand un
   réglage a un enjeu (« le fond n'est jamais noir pur, sinon ça bave à l'écran »), jamais en
   paragraphe technique. On félicite les petites étapes. On propose toujours de sauter (« pas
   obligatoire, on peut y revenir »).

> **Périmètre.** Ce skill écrit dans : `brand.config.json`, `.claude/skills/reel-script/SKILL.md`
> (+ `references/scripts-exemples.md`), `design-system/manychat-dm.md`,
> `design-system/instagram-caption.md`, `templates/style-presets.json` (table `fonts`, quand
> l'utilisateur fournit SA police), `assets/…`.
> Il **lit** `templates/`, `scripts/sync.mjs`, `brand.config.example.json`,
> `.claude/skills/motion-design/references/montage-talking-head.md`.
> ⛔ Il **n'écrit jamais** `brand/tokens.css` ni `brand/fonts.css` : ces deux fichiers sont générés
> par `node scripts/sync.mjs`. Il n'installe RIEN (ffmpeg, whisper, polices → `INSTALL.md`).

Le **questionnaire complet** (formulation exacte de chaque question, champ config cible, défaut,
validations) est dans **`references/questions.md`** — le lire avant d'animer un bloc.

---

## Démarrage (à chaque appel `/setup`)

1. Lire `brand.config.json` (ou le créer depuis `brand.config.example.json`).
2. Regarder `setup.completedBlocks` et **`setup.styleChosen`**.
3. **Si un bloc précis est demandé** (`/setup voix`) → aller droit à ce bloc.
4. **Si `setup.styleChosen` est `false` → proposer le bloc D EN PREMIER**, quel que soit l'ordre
   habituel. Annoncer franchement : « on commence par tes couleurs et tes sous-titres, 2 minutes —
   après tu peux monter, et on fera le reste quand tu veux ». S'il préfère voir d'abord une vidéo
   sortir, **c'est OK** : le style de départ « Papier » tient la route, on repropose après.
5. **Sinon** → annoncer l'état et proposer le prochain bloc non fait. Un petit mot d'accueil au tout
   premier lancement : présenter l'Empreinte en 2 phrases (ton monteur apprend ta voix, tes couleurs, ton cadrage : tu la déposes une fois, chaque vidéo la porte), dire
   que ça prend ~15 min et qu'on peut s'arrêter entre deux blocs (tout est sauvegardé).

---

## Bloc A — Identité `brand.*`

**Écrit :** `brand.name`, `brand.handle`, `brand.firstName`, `brand.niche`, `brand.language`.

Questions (détail + validations dans `references/questions.md`) :
- Le nom de ta marque / de ton compte.
- Ton handle Instagram (valider qu'il commence par `@`, sinon l'ajouter).
- Comment ton monteur doit t'appeler (ton prénom).
- Tes thématiques récurrentes (ta niche, en quelques mots).
- La langue de tes vidéos (défaut : français).

**Restitution + validation**, puis écrire `brand.*`, marquer `A` fait, `node scripts/sync.mjs`.

---

## Bloc B — Voix (le cœur de l'Empreinte)

**Écrit :** le **Profil de voix** injecté entre les marqueurs `voice-profile` de
`.claude/skills/reel-script/SKILL.md`, + le corpus copié dans
`.claude/skills/reel-script/references/scripts-exemples.md`.

> **Dire à l'utilisateur d'entrée de jeu :** son monteur écrit **déjà** ses scripts avec la méthode
> complète (le skill `reel-script` marche sans ce bloc). Ce bloc est un **bonus de personnalisation** :
> il apprend à écrire **comme lui** (ses accroches, ses tics, ses superlatifs). C'est facultatif et
> ça peut se faire plus tard — jamais un prérequis pour monter une vidéo. C'est aussi le bloc qui
> tire le plus le produit vers le haut quand on le fait.

Méthode d'analyse détaillée (quoi chercher, comment classer, pièges) →
**`references/voice-extraction.md`** — le lire avant d'analyser.

1. **Récolter le corpus.** Demander de coller **5 à 15 scripts ou transcripts** de ses propres Reels
   (le texte parlé ; s'il donne des liens, lui demander de coller le texte — on n'accède pas au
   réseau). Plus il y en a, meilleur est le clone.
   - **Pas de corpus ?** Basculer en **mode interview de secours** (5 questions sur son ton, ses
     tics, son public — cf `references/questions.md` bloc B mode interview), construire un profil
     générique de sa niche et le **marquer explicitement « à affiner avec de vrais scripts »**.

2. **Analyser** (méthode `references/voice-extraction.md`) : patterns de hook, longueur de phrase,
   tutoiement/vouvoiement, expressions & tics récurrents, transitions favorites, structure des CTA,
   niveau de langage. Règles d'or : **ne jamais inventer un tic à partir d'un seul exemple**
   (min. 2-3 occurrences), et **distinguer la voix du sujet** (un mot revient parce qu'il parle
   souvent d'IA ≠ c'est un tic de style).

3. **RESTITUER** à l'utilisateur : « Voici les N patterns que je retiens de ta voix » — une liste
   claire, courte, lisible (hooks, rythme, tutoiement, tics, CTA). Il valide ou corrige chaque
   point. On n'écrit qu'après son OK.

4. **Écrire** : remplir `templates/voice-profile.md.tpl` avec les patterns validés → injecter le
   résultat entre `<!-- BEGIN GENERATED: voice-profile -->` / `<!-- END GENERATED: voice-profile -->`
   dans `.claude/skills/reel-script/SKILL.md` ; copier le corpus brut (annoté par structure/CTA si
   possible) dans `.claude/skills/reel-script/references/scripts-exemples.md`. Marquer `B` fait,
   `node scripts/sync.mjs`.

---

## Bloc C — Funnel / CTA `cta.*`

**Écrit :** `cta.*` + les zones générées de `design-system/manychat-dm.md` et
`design-system/instagram-caption.md`.

> **Dire à l'utilisateur :** la génération de sa **légende Instagram** et de son **DM ManyChat** est
> **déjà active** (la méthode complète est embarquée, elle tourne à chaque publication sans réglage).
> Ce bloc ne l'active pas — il **mémorise son offre et son mot-clé** pour que le monteur ne les lui
> redemande plus à chaque post. Facultatif, personnalisation confort.

Questions :
- Tes types de CTA (mot-clé → DM · lien en bio · follow · partage). Plusieurs possibles → liste dans
  `cta.types`.
- Ton outil de DM (`cta.dmTool` : ManyChat / autre / aucun). Si aucun → pas de DM à générer plus tard.
- Ton mot-clé par défaut (`cta.defaultKeyword`) et si tu as une offre type / lead magnet.
- **Règle non négociable, à écrire :** on **n'écrit JAMAIS le mot « lien »** (risque de shadowban) →
  on utilise l'emoji `cta.linkEmoji` (défaut `🔗`).

**Restitution + validation**, remplir `cta.*`, réécrire le contenu entre les marqueurs `<!-- BEGIN GENERATED: cta -->` /
`<!-- END GENERATED: cta -->` des deux fichiers `design-system/` (si un fichier n'a pas
encore ces marqueurs, les insérer après l'intro, en montrant l'emplacement à l'utilisateur), marquer `C`, `node scripts/sync.mjs`.

---

## Bloc D — Visuel `visual.*`  🎨 LE PREMIER BLOC, TOUJOURS

**Écrit :** `visual.*`, `setup.styleChosen`, puis `node scripts/sync.mjs` régénère
`brand/tokens.css` + `brand/fonts.css`.

> **Pourquoi celui-là passe en premier.** Le fond, l'accent et la police de sous-titres sont ce qui
> rend un compte reconnaissable en une seconde. Dis-le simplement : « c'est le seul réglage que je
> ne peux pas deviner à ta place ».

> **Et s'il ne sait pas encore ?** C'est fréquent, et c'est légitime. Le style de départ
> « Papier » (noir & blanc, sans couleur) est propre et utilisable tel quel : **propose de monter
> d'abord, de voir le rendu, et de choisir après**. Ne force jamais un choix esthétique à quelqu'un
> qui n'a pas encore vu une seule de ses vidéos sortir — il choisira mal, et changera de toute
> façon. Redis-lui que **rien n'est définitif** : `/setup visuel` se relance à tout moment, tout le
> système suit, aucune vidéo déjà montée n'est cassée.

**Format : 3 questions, 2 minutes.** Pas d'inventaire de nuancier, pas de cours de design.
Le questionnaire détaillé (formulations exactes, validations) est dans `references/questions.md`.

### D1 — Le style de départ (la seule question vraiment importante)

Lire `templates/style-presets.json` et **présenter les presets par leur `label` + `description`**,
sans jargon, en disant clairement que c'est un **point de départ modifiable**, pas un moule.

> « J'ai 5 styles prêts. Tu en prends un, et on ajuste ce que tu veux après. Ou tu me donnes tes
> propres couleurs si tu les as déjà. Et si tu ne sais pas encore, on garde le noir & blanc, tu
> montes une vidéo, et tu choisis en voyant le résultat. »

- **Toujours offrir la 3e porte** (« je ne sais pas encore ») : laisser `visual.stylePreset` à
  `null`, ne PAS mettre `styleChosen` à `true`, monter en Papier, et reproposer après la vidéo.
  Un choix forcé avant d'avoir vu un rendu est un choix qui sera refait.
- Ne PAS présenter `neutral` comme un style parmi les autres : c'est le point de départ, il est
  déjà actif.
- **S'il a déjà une identité** (site, logo, chaîne existante) → prendre SES couleurs directement,
  c'est toujours mieux qu'un preset. Écrire `visual.bg` / `visual.accent` / `visual.surface`.
- Écrire `visual.stylePreset` = l'`id` choisi. Les valeurs du preset s'appliquent, et **toute clé
  renseignée dans `visual.*` gagne sur le preset** (c'est le mécanisme d'ajustement).

### D2 — Les couleurs (seulement si ajustement)

Si le preset lui va tel quel, **passer**. Sinon :
- **Fond** (`visual.bg`) : **jamais noir pur `#000000`** (ça bave à l'écran) → proposer un quasi-noir
  teinté de sa couleur.
- **Accent** (`visual.accent`) : `npm run sync` vérifie automatiquement les ratios de contraste et
  avertit si l'accent ou le texte passe mal sur le fond. **Relayer l'avertissement**, proposer 2-3
  alternatives plus contrastées, et laisser trancher : c'est son goût, pas le tien.
- `visual.surface`, `visual.text` : dérivés du preset, on n'en parle que s'il le demande.

### D3 — Les sous-titres (le marqueur d'identité le plus visible)

Deux réglages, deux phrases :
- **La police** (`visual.fontCaptions`) : Inter, Anton ou Archivo Black sont livrées. **Si tu as la
  tienne, c'est mieux** — c'est ce qui te distingue le plus vite. Fichiers `.woff2`/`.ttf` dans
  `assets/fonts/`, déclarés dans la table `fonts` de `templates/style-presets.json`.
  ⚠️ Une police de sous-titres a besoin d'un **`.ttf` de mesure** (`measureFile`) : PIL ne lit pas
  le woff2, et sans lui `tools/montage_captions.py` ne peut plus garantir une seule ligne.
  **JAMAIS de Google Fonts en ligne** (rendu non déterministe / hors-ligne cassé).
- **Le skin** (`visual.captionsSkin`) : les 5 apparences sont décrites dans `captionSkins` de
  `templates/style-presets.json` — `block` (fond plein), `outline` (contour), `plate` (plaque
  arrondie), `shadow` (ombre portée), `underline` (souligné). Les nommer en une ligne chacun,
  laisser choisir.
- `visual.captionsLines` (1 ou 2) et `visual.captionsPosition` : garder les défauts sauf demande.

### D4 — Style du CTA et cadrage (optionnel, proposer sans insister)

- `cta.style` : les options sont dans `ctaStyles` de `templates/style-presets.json`. Le preset en a
  déjà posé un.
- `montage.defaultLayout` : `split` ou `faceplein`. **Détail complet au bloc F3** (avec la
  calibration du cadrage) — ici on ne fait que confirmer celui du preset.
- **Logo / avatar** (optionnel) : si fourni → le déposer dans `assets/images/`.

### Écriture

**Restitution + validation**, puis écrire `visual.*` (+ `cta.style` si touché), mettre
`setup.styleChosen = true`, marquer `D` dans `completedBlocks`, et lancer **`node scripts/sync.mjs`**
— c'est lui, et lui seul, qui écrit `brand/tokens.css` et `brand/fonts.css`.

**Contrôle final obligatoire** : relire la sortie du sync. S'il avertit sur un contraste faible ou
une police manquante, **le dire à l'utilisateur** avant de conclure. Ne jamais annoncer « c'est
prêt » sur un sync qui a averti.

---

## Bloc E — Dérush / audio `audio.*` + `derush.*`

**Écrit :** `audio.*` et `derush.*`.

Questions :
- **Caméra** (`derush.camera` : DJI / iPhone / webcam / autre). Si **DJI** → noter la règle du 2ᵉ
  flux mjpeg (vignette) qu'il faudra mapper au dérush, et rappeler de filmer en **SDR / mode Normal**
  (pas HDR/HLG, sinon tonemap obligatoire au transcodage).
- **Nettoyage audio** : pas de question. La voix est **toujours** nettoyée avec Adobe Podcast
  Enhance (gratuit, compte Adobe), le process vit dans le skill `derush` §7. Le dire en une phrase
  (« au dérush, tu glisseras un fichier sur Adobe Enhance, je fais le reste »), sans proposer
  d'alternative.
- **Musique de fond** : l'utilisateur fournit son MP3 → le déposer dans `assets/music/`, écrire
  `audio.musicFile`. Volume par défaut `audio.musicDb` = **-26,5 dB**.
- **Rythme des coupes** (`derush.padStart`, `padEnd`, `silenceDb`, `islandDuration`) : garder les
  **défauts recommandés** (0.04 / 0.02 / -40 dB / ~0.18) sauf demande explicite. Ne pas re-régler
  au jugé.
- **Langue Whisper** (`derush.whisperLanguage`) : par défaut = `brand.language`.

**Restitution + validation**, écrire `audio.*` + `derush.*`, marquer `E`, `node scripts/sync.mjs`.

---

## Bloc F — Technique + calibration `env.*` + `montage.*`

**Écrit :** `env.*` et `montage.*`. C'est le seul bloc qui inspecte la machine et produit un
snapshot visuel.

1. **Détecter l'environnement** (remplir `env.*`, ne rien installer) :
   - OS (`env.os`) : via node `process.platform` (`darwin`/`win32`/`linux`) ou `uname`/`ver`.
   - `ffmpeg` (`env.ffmpegPath`) : `which ffmpeg` (macOS/Linux) / `where ffmpeg` (Windows).
   - Whisper (`env.whisperCli`, `env.whisperModel`) : détecter la CLI whisper dispo.
   - **Si ffmpeg ou whisper manquent** → NE PAS installer ici : renvoyer vers `INSTALL.md` et
     marquer le champ à compléter, on pourra relancer `/setup technique` plus tard.
2. **Agents** (`env.agents`) : demander lesquels il utilise — `claude-code`, `codex`, ou les deux.

3. **CADRAGE PAR DÉFAUT** (`montage.defaultLayout`) — **une vraie question, en langage simple.**
   Poser le décor d'abord, sans jargon : « Quand ton monteur assemble une vidéo, il lui faut un point
   de départ visuel — à quoi ressemble une section “normale” chez toi. **C'est juste le DÉFAUT** :
   après, à chaque vidéo, tu lui diras section par section (“là je veux juste ma tête en grand”, “là
   cette image en plein écran”…). Mais au départ, il part sur quoi ? » Deux choix :

   - **1) Écran coupé en deux (split-screen)** — Ta tête occupe la **moitié basse** de l'écran, et la
     **moitié haute** affiche les animations, les images, le motion design. On te voit tout le temps,
     avec le visuel juste au-dessus de toi. → `montage.defaultLayout = "split"` (c'est la valeur
     retenue si l'utilisateur ne tranche pas — présente-la neutre, sans la « recommander »).
   - **2) Ta tête en plein écran, animations par-dessus** — on te voit **en grand sur tout l'écran**
     en continu, et les animations/illustrations viennent **se poser par-dessus toi** (fond
     transparent, près de ta tête), sans couper l'écran en deux. → `montage.defaultLayout = "faceplein"`.

   **Toujours rappeler** : quel que soit le choix, il garde la main à 100 % — n'importe quelle section
   pourra devenir sa tête seule en grand, ou un visuel/une vidéo qui prend tout l'écran. Ce réglage ne
   fait que fixer **le point de départ** que l'IA applique sans qu'il ait à le redemander.

4. **CALIBRATION CROP** — procédure complète dans **`references/calibration-crop.md`** (la suivre
   pas à pas). En résumé : rush test 10-20 s → poser `assets/video/base.mp4` (transcoder en SDR si
   HDR, cf `motion-design`) → **calibrer le cadrage du mode par défaut choisi en F3** :
   - Si `defaultLayout = "split"` → itérer le `montage.splitTransform` (visage dans la moitié basse),
     puis dériver `montage.faceCrop` (formule de conversion, cf `references/calibration-crop.md`).
   - Si `defaultLayout = "faceplein"` → itérer le `montage.fullFaceTransform` (visage cadré plein
     écran, tête assez haute pour laisser la place aux overlays et aux sous-titres), puis dériver
     `montage.fullFaceCrop`.
   `npx hyperframes snapshot` → montrer à l'utilisateur et **itérer** (« ton visage est-il bien cadré ?
   trop zoomé ? ») en ajustant `translate`/`scale`. L'autre cadrage (celui qui n'est pas le défaut)
   peut rester à l'exemple par défaut : on le calibrera à la première section qui l'utilise.

**Restitution + validation**, écrire `env.*` + `montage.*`, marquer `F`, `node scripts/sync.mjs`.

---

## Fin de setup (les 6 blocs faits)

1. Régénérer tout une dernière fois : `node scripts/sync.mjs`.
2. Contrôle santé : `npx hyperframes doctor` (signaler ce qui reste à faire, ex. ffmpeg manquant).
3. Afficher un **récapitulatif de TOUT ce qui a été personnalisé** : identité, voix (N patterns),
   funnel/CTA, couleurs + polices, dérush/audio, cadrage calibré. Format court et lisible.
4. Conclure chaleureusement :
   > « Ton Empreinte est prête. Pour ton premier Reel : donne-moi ton idée de script, ou
   > lance-toi direct avec ta première vidéo brute. »

Rappel du pipeline pour la suite (sans déborder) : Script → Tournage → Dérush → Montage → Review →
SFX/Musique → Publication. On enchaîne un projet vidéo, plus jamais le setup.
