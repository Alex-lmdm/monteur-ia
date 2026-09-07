# Questionnaire de l'Empreinte — formulations exactes, bloc par bloc

Ce fichier est le **script du questionnaire**. Pour chaque question : la formulation exacte
(tutoiement, simple, zéro jargon), le **champ config cible**, le **défaut** (« Entrée = »), et les
**validations**. On pose **une question à la fois** quand c'est possible, on répète toujours le
défaut, et on n'écrit **rien** avant la validation de fin de bloc.

> Rappel : le défaut de chaque champ vient de `brand.config.example.json`. Quand ce fichier dit une
> valeur, c'est elle qu'on propose en « Entrée = … ».

---

## Bloc A — Identité

| # | Question (à dire tel quel) | Champ | Défaut | Validation |
|---|---|---|---|---|
| A1 | « C'est quoi le nom de ta marque ou de ton compte ? » | `brand.name` | — (obligatoire) | non vide |
| A2 | « Ton handle Instagram ? (ex. @toncompte) » | `brand.handle` | — | doit commencer par `@` → sinon on l'ajoute automatiquement ; pas d'espace |
| A3 | « Comment je t'appelle ? (ton prénom) » | `brand.firstName` | — | non vide |
| A4 | « Tu parles surtout de quoi ? Tes thématiques, en quelques mots. » | `brand.niche` | — | non vide (sert au mode interview du bloc B) |
| A5 | « Tes vidéos sont dans quelle langue ? » | `brand.language` | `français` (Entrée) | code/nom de langue simple |

---

## Bloc B — Voix

**Étape 1 — récolte du corpus (message unique) :**
> « Colle-moi entre 5 et 15 de tes propres scripts ou transcripts de Reels — juste le texte que tu
> dis face caméra. C'est ce qui apprend à ton monteur à écrire comme toi. Plus tu en mets, plus
> c'est fidèle. (Si tu n'en as pas sous la main, dis-le, on fera autrement.) »

- Cible : `.claude/skills/reel-script/references/scripts-exemples.md` (corpus) + zone
  `voice-profile` de `.claude/skills/reel-script/SKILL.md` (profil).
- Validation : au moins 1 script exploitable. Idéal ≥ 5. Si < 5, prévenir que le clone sera plus
  approximatif et proposer d'en ajouter.

**Étape 1 bis — mode interview de secours (si pas de corpus).** 5 questions :
| # | Question | Sert à |
|---|---|---|
| B-i1 | « Tu tutoies ou tu vouvoies ton audience ? » | tutoiement/vouvoiement |
| B-i2 | « Ton hook d'intro, tu l'attaques comment en général ? (une punchline ? une question ? une news ?) » | pattern de hook |
| B-i3 | « Il y a des mots ou des expressions que tu répètes tout le temps ? » | tics récurrents |
| B-i4 | « Tes phrases, plutôt courtes et punchy, ou posées et explicatives ? » | rythme / longueur |
| B-i5 | « À la fin, tu demandes quoi ? (commenter un mot, aller en bio, s'abonner…) » | structure CTA |
→ profil générique de la niche `brand.niche`, **marqué « à affiner avec de vrais scripts »**.

**Étape 3 — restitution :** lister les N patterns retenus, demander « je valide ? corrige ce qui
sonne faux. » On n'écrit qu'après OK.

---

## Bloc C — Funnel / CTA

| # | Question | Champ | Défaut | Validation |
|---|---|---|---|---|
| C1 | « Tu finis tes Reels comment ? (plusieurs possibles : commenter un mot-clé → DM, lien en bio, t'abonner, partager) » | `cta.types` (liste) | `["keyword"]` | ≥ 1 type connu |
| C2 | « Tu envoies tes DM avec quel outil ? » | `cta.dmTool` | `ManyChat` | `ManyChat`/`autre`/`aucun` — si `aucun`, pas de DM généré ensuite |
| C3 | « Ton mot-clé par défaut quand tu dis "commente X" ? » | `cta.defaultKeyword` | — | un seul mot court ; demandé seulement si `keyword` dans les types |
| C4 | « Tu as une ressource/offre type à envoyer ? (lead magnet, guide, lien…) » | (contexte, sert aux DM) | — | optionnel |
| — | Règle imposée, pas une question : le mot « lien » ne s'écrit **jamais** → emoji. | `cta.linkEmoji` | `🔗` | emoji unique |

---

## Bloc D — Visuel  🎨 TOUJOURS EN PREMIER

> **Aucun défaut proposé pour D1.** C'est volontaire : un défaut accepté par réflexe, c'est
> exactement le problème qu'on veut éviter. D2 à D12 ont, eux, les valeurs du preset choisi en
> D1 — on les saute si le preset convient tel quel.
>
> **« Je ne sais pas encore » est une réponse valable à D1** : laisser `visual.stylePreset` à
> `null` et `styleChosen` à `false`, monter en style « Papier » (noir & blanc, propre), et
> reproposer le bloc D une fois la première vidéo livrée. Quelqu'un qui n'a jamais vu une de ses
> vidéos sortir choisit mal — autant le laisser voir d'abord.

| # | Question | Champ | Défaut | Validation |
|---|---|---|---|---|
| D1 | « J'ai 5 styles prêts, tu en choisis un et on ajuste après. Ou tu me donnes tes couleurs si tu les as déjà. Et si tu ne sais pas encore, on garde le noir & blanc et tu choisis en voyant ta 1re vidéo. » puis lister `label` + `description` des presets | `visual.stylePreset` | **aucun** | l'`id` doit exister ; **ne pas présenter `neutral` comme une option** (il est déjà actif) ; s'il a déjà une identité (site, logo, chaîne), prendre SES couleurs plutôt qu'un preset ; « je ne sais pas » → laisser `null`, monter en Papier, reproposer après |
| D2 | « Tu veux ajuster la couleur de fond ? » | `visual.bg` | celle du preset | hex valide `#rgb`/`#rrggbb` ; **refuser `#000000`/`#000`** → proposer un quasi-noir teinté de sa couleur |
| D3 | « Et la couleur d'accent, celle qui ressort ? » | `visual.accent` | celle du preset | hex valide ; `npm run sync` calcule les ratios de contraste et avertit — **relayer l'avertissement**, proposer 2-3 alternatives, laisser trancher |
| D4 | « La couleur des blocs/cartes (un peu plus contrastée que le fond) ? » | `visual.surface` | celle du preset | hex valide |
| D5 | « Police des titres ? » | `visual.fontDisplay` | celle du preset | Inter / Anton / ArchivoBlack livrées ; si autre → fichiers dans `assets/fonts/` + déclaration dans la table `fonts` de `templates/style-presets.json`. **Jamais Google Fonts en ligne** |
| D6 | « Et pour le texte courant ? » | `visual.fontBody` | celle du preset | idem D5 |
| D7 | « Pour les sous-titres ? C'est ce qui te rend reconnaissable le plus vite — si tu as ta police, c'est le moment. » | `visual.fontCaptions` | celle du preset | idem D5, **plus** : un `.ttf` de mesure (`measureFile`) est obligatoire, PIL ne lit pas le woff2 |
| D8 | « Tes sous-titres, ils ressemblent à quoi ? » puis lister les 5 skins de `captionSkins` en une ligne chacun | `visual.captionsSkin` | celui du preset | `block`/`outline`/`plate`/`shadow`/`underline` |
| D9 | « Sur 1 ou 2 lignes ? » | `visual.captionsLines` | `1` | `1` ou `2` |
| D10 | « Où tu les places par défaut ? (jointure du split / centre-bas) » | `visual.captionsPosition` | celui du preset | libellé simple |
| D11 | « Le style de ta section CTA ? (facultatif) » puis lister `ctaStyles` | `cta.style` | celui du preset | id existant |
| D12 | « Tu as un logo ou un avatar à intégrer ? (facultatif) » | (→ `assets/images/`) | aucun | fichier image si fourni |

**Après écriture** : `setup.styleChosen = true`, puis `node scripts/sync.mjs`. Relire sa sortie :
tout avertissement (contraste faible, police absente de la table, `.ttf` de mesure manquant) doit
être dit à l'utilisateur avant de conclure.

---

## Bloc E — Dérush / audio

| # | Question | Champ | Défaut | Validation |
|---|---|---|---|---|
| E1 | « Tu filmes avec quoi ? (DJI, iPhone, webcam, autre) » | `derush.camera` | `iPhone` | si `DJI` → noter règle flux mjpeg + rappel SDR/mode Normal |
| E2 | (pas de question) Annoncer : « ta voix sera nettoyée avec Adobe Podcast Enhance au dérush, tu glisses un fichier, je fais le reste » | aucun | Adobe Enhance, toujours | ne proposer aucune alternative |
| E3 | « Tu as une musique de fond ? Colle/dépose ton MP3, je le range. » | `audio.musicFile` (→ `assets/music/`) | aucun | MP3 si fourni |
| E4 | « Le volume de la musique, on garde le réglage recommandé ? » | `audio.musicDb` | `-26.5` | nombre (dB) |
| E5 | « Le rythme des coupes, on garde les réglages recommandés ? (conseillé) » | `derush.padStart`/`padEnd`/`silenceDb`/`islandDuration` | `0.04`/`0.02`/`-40`/`0.18` | ne changer que sur demande explicite |
| E6 | « Whisper transcrit dans quelle langue ? » | `derush.whisperLanguage` | = `brand.language` | code langue |

---

## Bloc F — Technique + calibration

| # | Question / action | Champ | Défaut | Validation |
|---|---|---|---|---|
| F1 | (auto) détecter l'OS | `env.os` | détecté | `darwin`/`win32`/`linux` |
| F2 | (auto) `which/where ffmpeg` | `env.ffmpegPath` | détecté | si absent → `INSTALL.md`, champ à compléter |
| F3 | (auto) détecter la CLI whisper + modèle | `env.whisperCli`, `env.whisperModel` | détecté / exemple | si absent → `INSTALL.md` |
| F4 | « Tu montes avec Claude Code, Codex, ou les deux ? » | `env.agents` (liste) | `["claude-code"]` | ≥ 1 |
| F5 | « Ton cadrage par défaut : **écran coupé en deux** (toi en bas, motion en haut) ou **toi en plein écran** avec les animations par-dessus ? C'est juste le point de départ, tu diriges section par section ensuite. » | `montage.defaultLayout` | `"split"` | `"split"` \| `"faceplein"` |
| F6 | « Envoie-moi un rush test de 10-20 s (toi face caméra, cadrage habituel). » | → `assets/video/base.mp4` | — | vidéo fournie ; transcoder SDR si HDR |
| F7 | Calibration itérative du cadrage **du mode choisi en F5** (voir `calibration-crop.md`) | `montage.splitTransform` (si `split`) ou `montage.fullFaceTransform` (si `faceplein`) | ex. `translate(-216px,410px) scale(1.40)` | validé au snapshot par l'utilisateur |
| F8 | (auto, dérivé de F7) crop ffmpeg du visage | `montage.faceCrop` (si `split`) ou `montage.fullFaceCrop` (si `faceplein`) | ex. `crop=771:714:154:364,scale=1080:1000` | recalculé si le transform change |

---

## Règles de validation transverses

- **Hex** : `^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$`. Normaliser en minuscules 6 chiffres.
- **Handle** : ajouter `@` s'il manque ; retirer une URL éventuelle (`instagram.com/…` → `@…`).
- **Contraste** : viser un ratio WCAG ≥ 3:1 pour l'accent sur le fond et sur le blanc ; en dessous,
  avertir clairement (« ce jaune sur ce fond risque d'être dur à lire ») et proposer des variantes.
- **dB** : nombre (négatif attendu pour la musique).
- **Fichiers médias** : ne jamais inventer un chemin — attendre que l'utilisateur fournisse le
  fichier, puis le ranger dans le bon dossier `assets/…` et écrire le chemin réel.
- **Champ inconnu / sauté** : garder le défaut du `brand.config.example.json`, ne pas bloquer.
