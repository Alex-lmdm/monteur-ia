---
name: setup
description: >-
  Le Clone Monteur — l'onboarding de personnalisation du Monteur IA. Lance-le UNE fois après
  l'installation pour transférer TON goût (ta voix, tes couleurs, ton funnel, ton cadrage) à ton
  monteur. Use when the user says "setup", "configure mon système", "onboarding", "clone monteur",
  "personnalise mon monteur", "je viens d'installer", ou au tout premier lancement du template.
  Aussi : `/setup <bloc>` (identite, voix, funnel, visuel, derush, technique) pour refaire un bloc.
---
<!-- Copie générée — éditer .claude/skills/setup/ puis npm run sync -->

# Le Clone Monteur — onboarding de personnalisation

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
   `templates/*.tpl` + le config. Les zones générées sont encadrées par des marqueurs :
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
> `design-system/instagram-caption.md`, `brand/tokens.css`, `brand/fonts.css`, `assets/…`.
> Il **lit** `templates/`, `scripts/sync.mjs`, `brand.config.example.json`,
> `.claude/skills/motion-design/references/montage-talking-head.md`. Il n'installe RIEN (ffmpeg,
> whisper, polices → renvoyer vers `INSTALL.md`).

Le **questionnaire complet** (formulation exacte de chaque question, champ config cible, défaut,
validations) est dans **`references/questions.md`** — le lire avant d'animer un bloc.

---

## Démarrage (à chaque appel `/setup`)

1. Lire `brand.config.json` (ou le créer depuis `brand.config.example.json`).
2. Regarder `setup.completedBlocks`.
3. **Si un bloc précis est demandé** (`/setup voix`) → aller droit à ce bloc.
4. **Sinon** → annoncer l'état et proposer le prochain bloc non fait. Un petit mot d'accueil au tout
   premier lancement : présenter le Clone Monteur en 2 phrases (principe du transfert de goût), dire
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

## Bloc B — Voix (le cœur du Clone Monteur)

**Écrit :** le **Profil de voix** injecté entre les marqueurs `voice-profile` de
`.claude/skills/reel-script/SKILL.md`, + le corpus copié dans
`.claude/skills/reel-script/references/scripts-exemples.md`.

C'est LE bloc qui vaut le produit : on apprend à écrire comme l'utilisateur.
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

Questions :
- Tes types de CTA (mot-clé → DM · lien en bio · follow · partage). Plusieurs possibles → liste dans
  `cta.types`.
- Ton outil de DM (`cta.dmTool` : ManyChat / autre / aucun). Si aucun → pas de DM à générer plus tard.
- Ton mot-clé par défaut (`cta.defaultKeyword`) et si tu as une offre type / lead magnet.
- **Règle non négociable, à écrire :** on **n'écrit JAMAIS le mot « lien »** (risque de shadowban) →
  on utilise l'emoji `cta.linkEmoji` (défaut `🔗`).

**Restitution + validation**, remplir `cta.*`, régénérer les zones `GENERATED: cta` des deux
fichiers `design-system/`, marquer `C`, `node scripts/sync.mjs`.

---

## Bloc D — Visuel `visual.*`

**Écrit :** `visual.*` + régénère `brand/tokens.css` (depuis `templates/tokens.css.tpl`) et, si
besoin, `brand/fonts.css`.

Questions + garde-fous :
- **Couleur de fond** (`visual.bg`) : hex valide. **Garde-fou : jamais noir pur `#000000`** (ça bave
  à l'écran) → si l'utilisateur donne `#000`, proposer `#202022` ou un quasi-noir.
- **Couleur d'accent** (`visual.accent`) : hex valide. **Garde-fou contraste** — vérifier le ratio
  accent/fond ET accent/blanc ; si un ratio est faible (peu lisible), **avertir** et proposer 2-3
  alternatives plus contrastées. Ne pas écrire une couleur illisible sans l'avoir signalé.
- **Surface** (`visual.surface`) : bloc surélevé, légèrement plus clair que le fond (défaut proposé).
- **Polices** (`visual.fontDisplay`, `fontBody`, `fontCaptions`) : garder **Poppins** (recommandé,
  déjà en local) ou fournir une autre police. Si autre police → expliquer simplement : « donne-moi
  les fichiers `.woff2`/`.ttf`, je les mets dans `assets/fonts/` et je les déclare dans
  `brand/fonts.css` ». **JAMAIS de Google Fonts en ligne** (rendu non déterministe / hors-ligne
  cassé). Tant que les fichiers ne sont pas fournis, garder Poppins.
- **Sous-titres** (`visual.captionsLines` 1 ou 2 lignes, `visual.captionsPosition`) : style et
  position par défaut.
- **Logo / avatar** (optionnel) : si fourni → le déposer dans `assets/images/`.

**Restitution + validation**, écrire `visual.*`, régénérer `brand/tokens.css` (+ `fonts.css` si
police custom), marquer `D`, `node scripts/sync.mjs`.

---

## Bloc E — Dérush / audio `audio.*` + `derush.*`

**Écrit :** `audio.*` et `derush.*`.

Questions :
- **Caméra** (`derush.camera` : DJI / iPhone / webcam / autre). Si **DJI** → noter la règle du 2ᵉ
  flux mjpeg (vignette) qu'il faudra mapper au dérush, et rappeler de filmer en **SDR / mode Normal**
  (pas HDR/HLG, sinon tonemap obligatoire au transcodage).
- **Nettoyage audio** (`audio.enhanceMethod`) : **`adobe`** (recommandé — Adobe Podcast Enhance, 2
  clics à la main, meilleure qualité ; renvoyer au skill `derush` pour le process) ou **`ffmpeg`**
  (100 % automatique, un peu moins bon). Expliquer le compromis en une phrase.
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
3. **CALIBRATION CROP** — procédure complète dans **`references/calibration-crop.md`** (la suivre
   pas à pas). En résumé : rush test 10-20 s → poser `assets/video/base.mp4` (transcoder en SDR si
   HDR, cf `motion-design`) → appliquer le `montage.splitTransform` par défaut → `npx hyperframes
   snapshot` → montrer à l'utilisateur et **itérer** (« ton visage est-il centré dans la moitié
   basse ? trop zoomé ? ») en ajustant `translate`/`scale` → une fois validé, **calculer le
   `montage.faceCrop` ffmpeg** avec la formule de conversion (reprise depuis
   `.claude/skills/motion-design/references/montage-talking-head.md`, redonnée dans
   `references/calibration-crop.md`) → écrire `montage.splitTransform` + `montage.faceCrop`.
   Écrire aussi `montage.splitByDefault` (défaut `true` : tout commence en split-screen).

**Restitution + validation**, écrire `env.*` + `montage.*`, marquer `F`, `node scripts/sync.mjs`.

---

## Fin de setup (les 6 blocs faits)

1. Régénérer tout une dernière fois : `node scripts/sync.mjs`.
2. Contrôle santé : `npx hyperframes doctor` (signaler ce qui reste à faire, ex. ffmpeg manquant).
3. Afficher un **récapitulatif de TOUT ce qui a été personnalisé** : identité, voix (N patterns),
   funnel/CTA, couleurs + polices, dérush/audio, cadrage calibré. Format court et lisible.
4. Conclure chaleureusement :
   > « Ton Clone Monteur est prêt. Pour ton premier Reel : donne-moi ton idée de script, ou
   > lance-toi direct avec ta première vidéo brute. »

Rappel du pipeline pour la suite (sans déborder) : Script → Tournage → Dérush → Montage → Review →
SFX/Musique → Publication. On enchaîne un projet vidéo, plus jamais le setup.
