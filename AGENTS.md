# HyperFrames — Reels Le Monde Du Marketing (exemple) (@toncompte)

> ⚠️ **FICHIER GÉNÉRÉ** depuis `templates/AGENT.md.tpl` — ne pas éditer directement ;
> éditer le `.tpl` puis lancer `npm run sync`. (`CLAUDE.md` est lu par Claude Code, `AGENTS.md`
> par Codex : les deux sont produits par le même template et restent identiques, sauf la façon de
> charger un skill ci-dessous.)

> **Charger un skill** :
> Codex — **ouvre le fichier** `.agents/skills/<nom>/SKILL.md` indiqué et relis-le.

Ce projet sert **un seul format** : les Reels Instagram de Prénom (@toncompte) =
**vraie vidéo talking-head + motion design Le Monde Du Marketing (exemple) par-dessus, section par section**, avec
sous-titres, SFX et musique. Format **vertical 1080×1920, 30 fps**.

> ⚠️ **À FAIRE AVANT TOUTE TÂCHE DE MONTAGE.** Ce fichier est le seul toujours chargé.
> Il ne remplace pas les skills : il **aiguille** vers eux et rappelle les règles qu'on oublie.
> Pour chaque étape : **charge le skill de l'étape et relis sa checklist AVANT d'écrire une seule
> ligne / un seul filtre ffmpeg.** N'improvise jamais une étape « de tête ».

---

## 🟢 Étape 0 — Setup (avant tout montage)

Avant de démarrer le pipeline, vérifie que l'installation est personnalisée :

- Si **`brand.config.json` n'existe pas**, ou si **`setup.completedBlocks` est incomplet** (il manque
  des blocs par rapport au schéma), **propose `/setup`** avant toute tâche de montage. Tant que le
  setup n'est pas fait, les valeurs personnelles (marque, couleurs, musique, caméra…) ne sont pas
  fiables et le rendu sera générique.
- Les valeurs personnalisées (dérush, audio, visuel, CTA…) vivent dans **`brand.config.json`** :
  c'est la source de vérité des réglages. Ce fichier renvoie systématiquement vers ses valeurs.

---

## ⛔ Ordre séquentiel VERROUILLÉ (la règle qui casse le plus souvent)

On monte une vidéo **étape par étape, dans l'ordre ci-dessous**. **Ne JAMAIS proposer ni produire
une étape en avance.** Erreurs déjà commises à ne pas refaire :

- ❌ Proposer la **légende / le DM** pendant le script, le dérush ou le montage.
  → La publication (légende + DM) est **l'étape 7, la TOUTE DERNIÈRE**, seulement **après** montage
  validé **et** SFX/musique posés.
- ❌ Poser les **SFX / la musique** avant que Prénom ait **validé tout le montage** (étape 6 après 5).

**Réflexe de début de session montage** : situer où on en est dans le pipeline, annoncer **la
prochaine étape (une seule)**, et ne pas déborder dessus.

---

## 🧭 Le pipeline en 7 étapes (aiguilleur)

Le détail de chaque étape vit dans son skill (source de vérité). Ici : quoi charger, quand, et la
barrière « terminé quand » à passer **avant de montrer le résultat à Prénom / passer à l'étape suivante**.

| # | Étape | Prénom dit… | Skill à charger AVANT d'agir | Terminé quand |
|---|-------|-----------|------------------------------|----------------|
| 1 | **Script** | « on brainstorm un script », « écris ma version », « voici mon script » | `reel-script` | Hook + corps + CTA, voix de Prénom, ~30-45 s, **validé**. Si CTA « commente [MOT] » → juste **noter le mot-clé** (le DM se rédige à l'étape 7, pas maintenant). |
| 2 | **Tournage** | (Prénom tourne lui-même, puis) « voici la vidéo brute » | — | La vidéo brute est fournie. (Rappel : export **résolution MAX**, pas 1080p.) |
| 3 | **Dérush** | « fais les cuts », « coupe les blancs / les ratés », « clean l'audio » | `derush` | Re-transcription du cut = le script, **aucun mot coupé/doublé**, souffle inter-cut ≈ 0,1 s. **Audio nettoyé** (méthode `audio.enhanceMethod` de `brand.config.json`). |
| 4 | **Montage / motion** | « passe au montage », « mets les split-screens / le motion / les sous-titres » | `motion-design` (§14) | Chaque section montée : split-screen là où il faut, motion-first, visage net (pas de carré noir), sous-titres calés, safe-zones OK. |
| 5 | **Review** | « là je veux plutôt ça », « mets cette vidéo/image ici », « ça en plein écran », « les sous-titres vont pas » | (rester dans `motion-design`) | Prénom a **tout validé section par section** après ses retours. **C'est la barrière avant les SFX.** |
| 6 | **SFX + musique** | « mets le sound effect et la musique » | `motion-design` §14.10 | **Uniquement APRÈS validation étape 5.** SFX d'`assets/sfx/` placés + musique posée. |
| 7 | **Publication** | « la légende », « le message DM » | `design-system/instagram-caption.md` + `manychat-dm.md` | **Toute fin.** Légende IG + (si CTA) DM prêts. Le mot « lien » **jamais écrit** → emoji 🔗. |

> **Export MP4** : ce n'est pas une étape à part, c'est l'acte technique qui produit la vidéo pour la
> review (étape 5) puis la version finale (après 6). Toujours **en ffmpeg**, jamais `npm run render`
> (voir checklist). Fichiers dans `renders/` + copie dans `~/Downloads`.

Étapes annexes au besoin : **logos** → skill `thesvg` · **SFX à trouver** → `design-system/sfx-sound-search.md` · **texte long / anti-slop** → `design-system/writing-anti-slop.md`.

---

## ⚡ Fluidité — faire vite, sans re-travail

> Constat d'audit : le **compute réel** (ffmpeg/whisper/render) pèse à peine **~2-3 %** du temps.
> Le temps part dans les **itérations** (assets refaits 4-6×) et le **volume de sortie**
> (réécritures HTML entières, longs messages), jamais dans la machine. Réflexes anti-lenteur :

1. **Une session par grosse étape.** Ne pas enchaîner script → dérush → montage → SFX → publication
   dans un seul contexte (contexte saturé → auto-compaction en plein montage). `/clear`
   entre les étapes lourdes.
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
- [ ] Selon la caméra (`derush.camera` = `dji`) : certaines vidéos (ex. DJI) ont un 2ᵉ flux mjpeg (vignette) → mapper `[0:v:0]` explicitement.
- [ ] **Re-transcrire le cut final** pour vérifier : lecture = script, zéro mot coupé/doublé.
- [ ] **Mesurer les VRAIS points de coupe** (`<cut>_cuts.json`, détection scene-change sur le fichier livré) — cf `derush` §7bis.

**Transcodage (`motion-design` §14.3)**
- [ ] Vérifier `color_transfer` **AVANT** de transcoder : `bt709` = SDR direct (rien à faire) / `arib-std-b67` = HDR → tonemap obligatoire.
- [ ] `base.mp4` en **crf 14**, export final en **crf 16** (visage net).

**Montage / motion (`motion-design` §14)**
- [ ] **Frontières de section = `<cut>_cuts.json`**, JAMAIS les timestamps Whisper (ils démarrent 0,1-0,25 s trop tôt → on voit la fin de la prise précédente au passage plein-écran → split). Master, sous-comps et sous-titres lisent **la même source**.
- [ ] **MOTION FIRST, zéro redondance texte** : pas de gros texte qui redit la voix off / les sous-titres.
- [ ] Tout commence en **split-screen** par défaut (`montage.splitByDefault`) ; Prénom dit ensuite quelles sections passent en plein écran.
- [ ] **Bug « carré noir »** : tout élément plein cadre au-dessus du `<video>` visage = `background: transparent`. Visage = surface **plein cadre** + `clip-path` (jamais surface partielle).
- [ ] Entrées d'éléments : animer **`opacity` + `scale` uniquement**, jamais `x/y` (sinon décalage avec le `translate` du studio).
- [ ] **Safe-zone haute** : rien d'important dans les ~150 px du haut (Instagram cache le haut).
- [ ] **Safe-zone latérale** : rien d'important à moins de **~100 px** des bords gauche/droit — **en split ET en plein écran** (Instagram recadre les côtés). Le **ghost number** se pose en haut à droite du bloc qu'il numérote (quitte à passer derrière), **jamais collé au bord**.
- [ ] Charger `brand/fonts.css` + `brand/tokens.css` dans le `<head>` du **master** (sinon `var(--brand-*)` et polices cassées).
- [ ] **Au RENDER, toutes les sous-comps vivent dans UN SEUL document** (le studio, lui, les isole en iframes → il ne montre RIEN de ces bugs) :
  - jamais de `html, body { height: 920px }` dans une sous-comp (ça rogne tout le calque à 920 px) ;
  - **scoper** CSS et sélecteurs GSAP sous `#<composition-id>` (un `#win` nu attrape celui d'une autre section) ; ids internes → **classes** ; timeline dans une **IIFE**.
  - le **calque d'export doit être à la RACINE** (`compositions/…`, jamais `../compositions/…`) : sinon les `<script>` des sous-comps ne sont pas montés et **aucune animation ne tourne**.
- [ ] **`python3 tools/check_export.py` après chaque rendu du calque** : `npm run check` ne voit pas ces bugs, lui si.

**Sous-titres (`motion-design` §14.8)**
- [ ] **2-3 mots** par sous-titre, **pas de ponctuation finale**, **jamais à cheval sur 2 phrases**, jamais finir sur un mot faible.
- [ ] **Découper par unité grammaticale** : nom+adjectif et groupe verbal insécables ; **ne jamais orpheliner un adjectif ni fusionner deux unités** ; trop large → isoler le mot seul. `tools/montage_captions.py` = 1er jet, **re-couper avant de livrer** (§14.8 a le tableau d'exemples).
- [ ] Position : jointure (`y=920`) en split · `y≈1140` en plein visage · `y≈1500` en plein motion.
- [ ] CTA : **ne JAMAIS écrire « lien »** → emoji 🔗 (risque de shadowban).

**Export (`motion-design` §14.7)**
- [ ] Export = **ffmpeg**, **PAS `npm run render`** (le render HyperFrames ramollit le visage).

**SFX + musique (`motion-design` §14.10) — étape 6, après validation**
- [ ] **Seulement après validation complète du montage (étape 5).** Jamais au fil de l'eau.
- [ ] « mets le sound effect et la musique » = les SFX d'`assets/sfx/` + la musique `(aucune — à fournir)` à **-26.5 dB**, sauf indication contraire.
- [ ] Volumes SFX **rééquilibrés par niveau perçu** (pas un dB uniforme).

**Publication (`design-system/`) — étape 7, la dernière**
- [ ] Légende IG (`instagram-caption.md`) : si CTA « commente [MOT] », le CTA est la **1ʳᵉ ligne**. Aucun hashtag.
- [ ] DM (`manychat-dm.md`) **uniquement si** CTA mot-clé. `🔗` obligatoire, jamais « lien ». Demander l'URL réelle, ne jamais l'inventer.

**Self-checks (obligatoires)**
- [ ] `npm run check` après **chaque** modif `.html`.
- [ ] `npx hyperframes keyframes` (+ onion-shot `--shot`) après **chaque** modif d'animation.

---

## Skills framework — À CHARGER AVANT DE CODER UNE COMPOSITION

En plus des skills métier ci-dessus, ces skills encodent les patterns HyperFrames
(`window.__timelines`, sémantique des `data-*`, CSS shader-compatible) absents des docs web
génériques. **Sauter le skill = composition cassée.**

| Skill                      | Command                   | Quand l'utiliser                                                                 |
| -------------------------- | ------------------------- | -------------------------------------------------------------------------------- |
| **hyperframes**            | `/hyperframes`            | Créer/éditer des compositions HTML, captions, TTS, animation audio-réactive      |
| **hyperframes-cli**        | `/hyperframes-cli`        | Boucle dev CLI : init, lint, inspect, preview, render, doctor                     |
| **hyperframes-media**      | `/hyperframes-media`      | Préprocessing des assets : tts (Kokoro), transcribe (Whisper), remove-background  |
| **hyperframes-registry**   | `/hyperframes-registry`   | Installer des blocks/composants via `hyperframes add`                             |
| **website-to-hyperframes** | `/website-to-hyperframes` | Capturer une URL et la transformer en vidéo                                       |
| **gsap**                   | `/gsap`                   | Animations GSAP — tweens, timelines, easing, perf                                |
| **animejs / css-animations / lottie / three / waapi / tailwind** | `/<nom>` | Selon la techno d'animation utilisée                        |

> **Skills absents ?** Lancer `npx hyperframes skills` puis redémarrer la
> session, ou installer : `npx skills add heygen-com/hyperframes`.

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
- `templates/` — templates dépersonnalisés (`AGENT.md.tpl`, `tokens.css.tpl`, `voice-profile.md.tpl`)
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
animations (GSAP/CSS/Anime), lancer aussi le diagnostic keyframes :

```bash
npx hyperframes keyframes compositions/<scene>.html          # tweens + timing + valeurs
npx hyperframes keyframes compositions/<scene>.html --shot out.png [--selector "#el"] [--layout strip]
```

- Vérifier que chaque tween tombe sur le bon temps du voiceover.
- Un sélecteur `__unresolved__` = bug silencieux à corriger.
- Pour toute motion non triviale (x/y, arc, stagger, pulse), générer l'onion-shot (`--shot`) et
  regarder la trajectoire **avant** le render final.

## Règles framework HyperFrames (rappel technique)

1. Tout élément timé porte `data-start`, `data-duration` et `data-track-index`.
2. Les éléments timés visibles **DOIVENT** avoir `class="clip"` (contrôle de visibilité). Exception connue : le `<video>` visage n'a PAS `class="clip"` (voir `motion-design` §14.5).
3. Les timelines GSAP sont **paused** et enregistrées sur `window.__timelines` :
   ```js
   window.__timelines = window.__timelines || {};
   window.__timelines["composition-id"] = gsap.timeline({ paused: true });
   ```
4. Les vidéos sont `muted` avec un `<audio>` séparé pour la piste son.
5. Les sous-compositions utilisent `data-composition-src="compositions/file.html"`.
6. Logique **déterministe** uniquement — pas de `Date.now()`, pas de `Math.random()`, pas de fetch réseau.
