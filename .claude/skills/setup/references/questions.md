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

## Bloc D — Visuel

| # | Question | Champ | Défaut | Validation |
|---|---|---|---|---|
| D1 | « Ta couleur de fond ? (donne-moi un code hex, ex. #202022) » | `visual.bg` | `#202022` | hex valide `#rgb`/`#rrggbb` ; **refuser `#000000`/`#000`** → proposer `#202022` |
| D2 | « Ta couleur d'accent ? (celle qui ressort, ex. jaune #ffee00) » | `visual.accent` | `#ffee00` | hex valide ; **contraste** : ratio accent/fond ET accent/blanc — si faible, avertir + proposer 2-3 alternatives |
| D3 | « La couleur des blocs/cartes (un poil plus clair que le fond) ? » | `visual.surface` | `#2b2b2d` | hex valide |
| D4 | « On garde Poppins, ou tu veux une autre police pour les titres ? » | `visual.fontDisplay` | `Poppins` | si autre → demander les fichiers `.woff2`/`.ttf` (→ `assets/fonts/`), jamais Google Fonts |
| D5 | « Et pour le texte courant ? » | `visual.fontBody` | `Poppins` | idem D4 |
| D6 | « Pour les sous-titres ? » | `visual.fontCaptions` | `Poppins` | idem D4 |
| D7 | « Tes sous-titres, sur 1 ou 2 lignes ? » | `visual.captionsLines` | `2` | `1` ou `2` |
| D8 | « Où tu les places par défaut ? (bas / centre-bas) » | `visual.captionsPosition` | valeur exemple | libellé simple |
| D9 | « Tu as un logo ou un avatar à intégrer ? (facultatif) » | (→ `assets/images/`) | aucun | fichier image si fourni |

---

## Bloc E — Dérush / audio

| # | Question | Champ | Défaut | Validation |
|---|---|---|---|---|
| E1 | « Tu filmes avec quoi ? (DJI, iPhone, webcam, autre) » | `derush.camera` | `iPhone` | si `DJI` → noter règle flux mjpeg + rappel SDR/mode Normal |
| E2 | « Comment on nettoie ta voix ? Adobe Podcast (2 clics à la main, meilleur son) ou 100% auto ffmpeg (un peu moins bon) ? » | `audio.enhanceMethod` | `adobe` | `adobe`/`ffmpeg` |
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
