---
name: lmdm-motion-design
description: >-
  Motion design et montage vidéo @LeMondeDuMarketing (Reels, Stories, TikTok, YouTube) :
  design system LMDM + workflow HyperFrames. Use when: creating a composition, a clip or a
  motion graphic for the brand; monter une vidéo talking-head (split-screen, sections, export
  final ffmpeg); générer les sous-titres; poser les SFX et la musique. Entrée : un cut validé
  et la timeline.json produite par lmdm-derush.
---

# LMDM — Motion Design System

Identité visuelle Le Monde Du Marketing (@LeMondeDuMarketing) pour tout contenu vidéo / motion design. Format-agnostique : 1080×1920 (Reels/Stories), 1920×1080 (YouTube), 1080×1080 (clips intégrables), 4K.

**Références (chargées à la demande, selon la branche) :**

| Condition observable | Fichier |
|---|---|
| Vidéo talking-head à monter (split-screen, master, visage, export final) | `references/montage-talking-head.md` |
| Panneau visage NOIR dans le studio | `references/visage-carre-noir.md` |
| Vidéo source HDR (`color_transfer` = `arib-std-b67` ou `smpte2084`) | `references/transcodage-video.md` |
| Sous-titres à produire | `references/sous-titres.md` |
| SFX / musique (UNIQUEMENT après validation du montage par Alex) | `references/sfx-musique.md` |
| Section CTA « commente un mot-clé », ou image qui zoome (Ken Burns) | `references/patterns.md` |
| Projet Remotion (legacy) | `references/remotion.md` |

---

## 0. Principe fondateur — MOTION FIRST, ZÉRO REDONDANCE TEXTE

**La règle absolue du motion design LMDM :**

> **Pas de gros texte. Pas de hook textuel. Pas de mot cinématique. Pas de titre plein écran.**
> Le motion design est 100% visuel : schémas, icônes, animations, flows, dataviz, comparaisons.

**Pourquoi :** Alex parle déjà en voiceover, et des sous-titres sont ajoutés à l'étape de montage. Tout gros texte affiché devient triplement redondant (voix + sous-titres + overlay). Le motion design doit **ajouter** une couche d'info, pas redire.

**Question à se poser avant chaque section** :
> "Comment je rends cette idée **visuelle** au lieu de la dire en gros texte ?"

### Petits labels = OK / Gros textes = NON

| ✅ Autorisé                                                  | ❌ Interdit                                          |
|--------------------------------------------------------------|-----------------------------------------------------|
| Labels de colonnes en Poppins Black UPPERCASE (22-36 px)     | Hooks plein écran type "Y VOIR CLAIR" (150+ px)    |
| Tags catégoriels courts ("TVA 20%", "DÉDUCTIBLE")            | Phrases écrites qui reprennent la voix off          |
| Chiffres / valeurs dans un schéma                            | Mots cinématiques ("PUISSANT", "RÉVOLUTIONNAIRE")  |
| Numérotation / étapes ("1", "2", "3")                        | Tout titre centré en grosse police display          |
| Mots-clés intégrés à un visuel (label sur un bloc)           | Texte qui résume le contenu parlé                   |

### Conséquence pour les polices

- **Poppins partout.** C'est la seule famille à utiliser pour les labels du motion design.
- **Pas de police display en motion.** Poppins porte tout, hooks compris. Coluna est réservée aux formats statiques (`references/coluna-statique.md`) : en vidéo, elle n'a aucune utilité (pas de gros pavé de texte = pas besoin de display).
- **Mono** : seulement pour des prompts/terminaux/code affichés.

---

## 1. Identité de marque

- **Compte** : Le Monde Du Marketing
- **Handle** : @LeMondeDuMarketing
- **Auteur signataire** : Alex
- **Positionnement** : analyses, outils et patterns du marketing + IA, ton direct et factuel, voix de "pote qui te dit ce qui marche vraiment". Pas de corporate speak.
- **Assets perso** : `brand/assets/avatar.png`, `brand/assets/portrait.png` (à fournir par projet pour lower-thirds intro/outro)

---

## 2. Palette de couleurs

Référence canonique :

| Rôle             | Hex       | Usage                                                              |
|------------------|-----------|--------------------------------------------------------------------|
| Background       | `#202022` | Fond principal. Quasi-noir, légère teinte grise. **JAMAIS noir pur.** |
| Surface          | `#2b2b2d` | Cartes / blocs surélevés sur le fond.                              |
| Surface light    | `#d8d8d8` | Surface claire (rare, pour contraste).                             |
| Blanc            | `#ffffff` | Texte principal sur fond sombre.                                   |
| Muted            | `#a6a6a0` | Texte secondaire / métadonnées (gris **chaud**, pas froid).         |
| **Jaune accent** | `#ffee00` | L'accent unique de la marque. Hooks, mots-clés, chiffres, CTA.    |
| Noir titre       | `#202022` | Identique au background (pas un vrai noir).                        |
| Stroke titre     | `#000000` | Contour noir pur 100% (**uniquement** pour le contour de gros titres). |

### Règles d'usage des couleurs

- **Le jaune n'est jamais décoratif.** Il ancre une info : un chiffre, une entité nommée, un mot-clé, un résultat surprenant, un CTA. Si tu colories une phrase entière en jaune, tu as raté la hiérarchie.
- **Maximum un accent jaune par "moment visuel"** (un plan, un slide, un titre).
- Le jaune est **plat, mat, brut** : aplat pur, jamais de gradient (jaune→orange, jaune→vert…).
- Le jaune s'applique **en texte brut sur fond sombre** : pas de pills jaunes translucides à bord, pas de cards à bord jaunes pour des labels.
- **Le fond est toujours `#202022`** ; le noir pur `#000` sert **uniquement** au stroke de titre (jamais en aplat).

### Couleurs autorisées

- Palette LMDM ci-dessus, **en aplats**, plus l'opacité 10% du ghost number (§6).
- Bleu / rouge / vert **uniquement en data visualisation explicite** : graphique, indicateur up/down.
- L'image reste **telle quelle** : pas de dégradé multi-couleurs, pas de filtre Instagram-style (lo-fi, vintage, warm tone), pas de translucide.

---

## 3. Typographies

### Polices

```
Headline → Poppins, Avenir Next, Arial, system-ui, sans-serif
/ Body      Usage : TOUS les textes. Hooks, sous-titres, paragraphes,
            lower-thirds, captions.

Mono     → Courier New, ui-monospace, monospace
            Usage : code, prompts, terminaux, valeurs techniques.
```

**Poppins est la seule police du motion.** Pas de police display en vidéo : un hook
géant, c'est Poppins Black, pas une autre famille. (Coluna reste la display des formats
STATIQUES : sa spéc est dans `references/coluna-statique.md`, ne l'utilise pas en motion.)

- Poppins : Google Fonts, dispo toutes graisses.

### Poppins — le corps

- **Body par défaut** : Poppins Regular (400). **Pas Light** (trop fin sur fond sombre).
- **Emphase forte** : Poppins Black (900), dans la même phrase. Outil principal pour donner des ancres à l'œil.
- **Emphase douce** : Poppins Regular Italic. Pour parenthèses, apartés, nuances.
- **Sous-titres / section titles** : Poppins Black, 10-20 px au-dessus du corps.
- **Slide number / numérotation** : Poppins SemiBold (600), 20 px, blanc.
- **Lower-third / handle vidéo** : SemiBold pour le nom, Regular pour le handle.

### Hiérarchie typographique de référence

| Élément                          | Famille | Graisse        | Taille (1080×1350)         | Couleur        |
|----------------------------------|---------|----------------|----------------------------|----------------|
| Hook géant / mot cinématique     | Poppins | Black 900      | 90–150 px (line-height 0.9)| Blanc + jaune  |
| Sous-titre / section title       | Poppins | Black 900      | 50 px (line-height 62)     | Blanc          |
| Body paragraphe                  | Poppins | Regular 400    | 40 px (line-height 55)     | Blanc          |
| Body emphase forte (1-3 mots)    | Poppins | Black 900      | 40 px                      | Blanc ou jaune |
| Body emphase douce               | Poppins | Regular italic | 40 px                      | Blanc          |
| Métadonnée / numérotation        | Poppins | SemiBold 600   | 20 px                      | Blanc          |
| Ghost number (déco)              | Poppins | Bold 700       | 180 px                     | Blanc 10% op.  |

**Adaptation aux formats vidéo** :
- 1080×1920 (Reels/Stories) → **multiplier les tailles par ≈1.4**
- 1080×1080 (square clips intégrables) → tailles de référence
- 4K → ×2

### Règles d'emphase dans le corps (le détail clé)

1. Tu écris en **Poppins Regular**.
2. Dans chaque phrase, tu mets **1 à 3 mots en Poppins Black** pour donner des ancres à l'œil. **Pas 5, pas une phrase entière.**
3. **L'italique** sert aux apartés, nuances, citations courtes. Sparingly.
4. **Le jaune** sert à **un seul élément par bloc** : le chiffre, le nom propre, le mot-clé.

Trois niveaux : Regular (base), Black (ancres), Italic (nuance). + jaune `#ffee00` sur le mot qui porte le hook.

### Familles et traitements autorisés

- **Tout est sans serif** : Poppins, partout. Pas de serif (Times, Georgia, Playfair), pas de "fun" / handwritten / script, pas de police display.
- **Casse** : casse normale. L'UPPERCASE reste un effet ponctuel (un mot), pas un mode de titrage.
- **Décorations** : aucune. Le soulignement existe dans un seul cas, l'underline jaune sous un mot (§6) ; pas de barré / strike-through décoratif.
- **Tracking par défaut** (pas de letter-spacing élargi pour faire "stylé").

---

## 4. Règles motion (le cœur du skill)

### Fond
- **Toujours `#202022`**. Pas de fond blanc, sauf inversion intentionnelle pour un plan choc (et préférer un blanc cassé même là).
- Pour des **clips à intégrer dans un montage existant** : fond transparent OK si l'animation est conçue pour s'intégrer dans une vidéo qui a déjà son fond.

### Transitions
- **Cut sec** (par défaut), **slide rapide** (200-300 ms), **fade très court**. Ces trois-là, et rien d'autre.

### Apparition de texte
- **Par mot ou par bloc**, jamais lettre par lettre.
- Exception : effet "machine à écrire" pour un prompt mono (terminal).

### Easing et durées — source unique = le JSON de tokens (§8)

Les valeurs canoniques vivent dans `motion.easing` (`inOut`, `outExpo`) et `motion.duration` (`appearMs`, `holdHookMs`, `holdWordMs`, `slideTransitionMs`) du §8, exprimées en **ms**.
Conversions : **secondes (HyperFrames) = ms ÷ 1000** · **frames @30 fps = ms × 30 ÷ 1000** (donc frames ÷ 30 = secondes, secondes × 1000 = ms).

Plages et règles d'usage (ne figurent pas dans le JSON) :
- **Apparition d'un élément** : 250-400 ms.
- **Hold time pour un hook** : ≥ 1,2 s après apparition.
- **Hold time pour le body** : ≈ 0,4 s par mot affiché.
- **Mots en jaune** : peuvent apparaître **après** les mots blancs (delay 100-200 ms) pour effet d'accent — le jaune arrive en dernier, comme une révélation.
- **Frame budget (à 30 fps)** : 250 ms = **7-8 frames** · 400 ms = **12 frames** · 1,2 s = **36 frames** · calcul précis `duration_ms * fps / 1000`.
- Springs Remotion : `references/remotion.md`.

---

## 5. Lower-third / identité / safe areas

### Lower-third (identité bas-gauche)
- **Avatar** circulaire `brand/assets/avatar.png`, ≈ 76×85 px (×1.4 en 1080×1920).
- **Texte sur 2 lignes** à droite de l'avatar :
  - Ligne 1 : `Alex` — Poppins SemiBold, blanc
  - Ligne 2 : `@LeMondeDuMarketing` — Poppins Regular, blanc ou muted `#a6a6a0`
- **Position** : bottom-left, à 68 px du bord gauche (au-delà du minimum de 54 px, cf. safe areas ci-dessous).

### Watermark / signature
- Logo ou handle dans un coin, opacité 70-90%.

### Safe areas — 1080×1920 (Reels/Stories/TikTok) — validées Alex 2026-06-25

Une seule table de vérité. Elle vaut pour le **contenu motion important** (texte, labels,
schémas, éléments-clés), pas pour les médias : **vidéos, images et illustrations PEUVENT
déborder** hors cadre (c'est souvent souhaitable). Ne JAMAIS rétrécir un média pour tenir
dans la safe area.

| Bord | Marge | Pourquoi |
|---|---|---|
| **Haut** | **150 px minimum** (idéalement 220 px) | Le plus critique : Instagram superpose le nom d'utilisateur + la photo de profil, ils CACHENT le contenu du haut. |
| **Bas** | **380 px** | Caption, likes, commentaires. Le visage du talking-head y est OK. |
| **Côtés** | **100 px** (54 px = plancher absolu) | **Instagram redimensionne/recadre les côtés selon l'appareil** → un élément posé à 54 px du bord se fait rogner. Corrigé par Alex 2026-07-14 : « il faudrait un petit peu plus d'espace sur les côtés ». |

En **split-screen**, le contenu motion du panneau HAUT doit démarrer à **y ≥ 150 px** (ne pas
coller le haut du panneau).

**Les côtés valent AUSSI en plein écran** : une carte / fenêtre / mockup plein écran se cadre à
**~105 px des bords**, pas 54.

⚠️ **Ghost number : JAMAIS collé au bord droit.** Le poser **en haut à droite du bloc** qu'il
numérote (il peut passer **derrière** la carte et être partiellement recouvert — c'est le rendu
voulu), à l'intérieur de la marge de 100 px. Collé au bord, il est le premier élément rogné par
Instagram.

✅ *Réflexe à chaque section (split ou plein écran)* : « un élément important est-il dans la
bande haute (< 150 px), en bas (> 1540 px) ou à moins de **100 px** d'un bord latéral ? » → si
oui, le décaler vers le centre.

### Safe areas — 1080×1080 (clips square intégrables)
- **Top/Bottom** : 68 px
- **Left/Right** : 68 px
- Zone safe : padding 68 px tout autour, soit zone utile 944×944.

### 5.6 Remplissage fond flou (média qui ne remplit pas la zone) — RÈGLE validée Alex 2026-07-08

Dès qu'un **média affiché** (image OU vidéo), en **plein écran ou split-screen**, **ne remplit pas
toute la zone** (il tient soit en largeur soit en hauteur → vide en haut/bas ou sur les côtés) :

- ❌ **NE PAS cropper** pour forcer le remplissage (perte de contenu — rejeté par Alex).
- ❌ Pas de barres noires.
- ✅ **Dupliquer le média en arrière-plan, beaucoup plus grand, flouté + légèrement assombri**, pour
  combler tout le vide → petit effet « fond flou » (façon Reels/YouTube). Le média net reste entier,
  centré, à sa taille pleine largeur (ou pleine hauteur).

Recette ffmpeg : `[m]split[bg][fg]; [bg]scale=<plus grand que la zone>,crop=<zone>,gblur=sigma=26,eq=brightness=-0.06[bgb]; [fg]scale=<pleine largeur/hauteur>[fgs]; [bgb][fgs]overlay=(W-w)/2:(H-h)/2`.
En CSS (compo HyperFrames) : un `<img>`/`<video>` de fond en `filter:blur(28px) brightness(0.9)`,
`transform:scale(1.25)`, `object-fit:cover` sous le média net.
Réflexe à chaque média d'une compo : « est-ce que ça remplit toute la zone ? » — si non → fond flou.

---

## 6. Patterns motion transposables

### Le "ghost number"
- Grand chiffre décoratif, **Poppins Bold 180 px**, **blanc à 10% d'opacité**, en haut à droite.
- **Usage strict** : un ghost = une entrée d'énumération (raison 1, outil 2, étape 3).
- Pas de ghost sur cover, intro, transition, synthèse, CTA.
- En vidéo : repère visuel d'un chapitre/section, respecter "une entrée numérotée = un ghost".

### Le "yellow underline"
- Texte en blanc, Poppins Black ~44 px.
- Soulignement jaune `#ffee00` épais (≈ 6 px) sous un mot-clé.
- **En motion** : animer un trait jaune qui se trace **de gauche à droite** sur 300-400 ms.

### Le "circular cutout"
- Cercle blanc bordé contenant un logo, un visage, ou une preuve.
- Posé sur une image principale comme focus visuel news-style.
- En vidéo : overlay d'invité, citation d'auteur, mini-screenshot.

### Le "speech bubble emoji"
- Sur les CTA, un emoji 💬 à 100 px ajoute du volume.
- En motion : marqueur visuel d'interactivité (commenter, DM).

> Patterns de **section entière** (CTA « commente un mot-clé », image qui zoome / Ken Burns) : `references/patterns.md`.

---

## 7. Anti-slop pour les textes à l'écran

Les overlays texte tombent souvent dans le slop IA. À éviter :

### Mots à blacklister dans tout overlay
crucial · fondamental · indéniablement · incontournable · primordial · révolutionnaire · fascinant · remarquable · formidable · considérablement · significativement · effectivement · notamment · ainsi (début de phrase) · en effet · certes · davantage · pléthore · paradigme · synergie · holistique · robuste · levier (abstrait) · optimiser (sauf technique) · catalyseur.

### Expressions à bannir
- "Dans le monde de..." / "Dans un monde où..." / "À l'ère de..."
- "Il est important de noter que..."
- "Ce n'est pas X. C'est Y." (formule IA surutilisée — montre le contraste autrement)
- "La vraie question, c'est..."
- "Saviez-vous que..." / "Vous êtes-vous déjà demandé..."
- Hooks vagues type "C'est fou ce que l'IA peut faire" (→ un chiffre, un nom propre, un contraste concret).
- Règles de 3 forcées ("Plus rapide, plus simple, plus efficace").
- Slogans corporate ("Libérez votre potentiel", "Transformez votre business").
- Voiceover qui résume le visuel ("Comme vous pouvez le voir...").

### Règles d'écriture pour overlays
1. **Spécifique uniquement.** Chiffres précis, noms d'outils. Pas de couverture.
2. **Zéro hedging.** Bannir : "pourrait", "potentiellement", "éventuellement", "peut-être".
3. **Accents français propres partout.** Pas de "methode", "deja", "idee".
4. **Pas de tirets longs (—)** dans les overlays. Virgules ou phrases courtes.
5. **Tutoiement** par défaut.

---

## 8. Tokens techniques (à exporter dans chaque projet)

```json
{
  "colors": {
    "background": "#202022",
    "backgroundDeep": "#202022",
    "surface": "#2b2b2d",
    "surfaceLight": "#d8d8d8",
    "white": "#ffffff",
    "muted": "#a6a6a0",
    "yellow": "#ffee00",
    "black": "#202022",
    "titleStroke": "#000000"
  },
  "fonts": {
    "headline": "Poppins, Avenir Next, Arial, system-ui, sans-serif",
    "body": "Poppins, Avenir Next, Arial, system-ui, sans-serif",
    "mono": "Courier New, ui-monospace, monospace"
  },
  "typography": {
    "cover": {
      "family": "headline",
      "weight": 900,
      "sizeMin": 90,
      "sizeMax": 150,
      "lineHeight": 0.9
    },
    "body":       { "family": "body", "weight": 400, "size": 40, "lineHeight": 55 },
    "bodyStrong": { "family": "body", "weight": 900 },
    "bodyItalic": { "family": "body", "weight": 400, "style": "italic" },
    "subtitle":   { "family": "body", "weight": 900, "size": 50, "lineHeight": 62 }
  },
  "motion": {
    "easing": {
      "inOut":  "cubic-bezier(0.65, 0, 0.35, 1)",
      "outExpo":"cubic-bezier(0.16, 1, 0.3, 1)"
    },
    "duration": {
      "appearMs": 300,
      "holdHookMs": 1200,
      "holdWordMs": 400,
      "slideTransitionMs": 250
    }
  },
  "profile": {
    "name": "Alex",
    "handle": "@LeMondeDuMarketing"
  }
}
```

---

## 9. Formats vidéo de référence

| Format               | Dimensions  | Usage                              |
|----------------------|-------------|------------------------------------|
| Reel / Story / TikTok | 1080×1920  | Vertical, plein écran mobile       |
| Square (clips intégrables) | 1080×1080 | Inserts dans un montage existant |
| YouTube / horizontal | 1920×1080  | Vidéos longues, podcasts vidéo     |
| Carrousel (référence statique) | 1080×1350 | Hors scope ce skill          |

---

## 10. Checklist anti-slop avant export motion

- [ ] Le premier plan accroche en moins de **1,5 s** (chiffre, nom propre, contraste, ou question concrète).
- [ ] Aucun mot/expression de la blacklist (§7) dans les overlays.
- [ ] Accents français propres partout (é è à ù ç ê î ï ô û).
- [ ] Pas de tirets longs (—) dans les overlays texte.
- [ ] Le jaune `#ffee00` est utilisé sur **1 mot/chiffre maximum par plan**.
- [ ] Aucune police display : tout est en Poppins, hooks compris (Poppins Black).
- [ ] Le corps est en Poppins Regular avec 1-3 mots en Poppins Black pour les ancres.
- [ ] Le fond est `#202022`, pas du noir pur (ou transparent pour clip intégrable).
- [ ] Aucun emoji décoratif sans utilité (pas de ✨ 🚀 💯 génériques). Si emoji : Apple/iOS style, 1-2 par moment max.
- [ ] L'identité (handle, avatar) est visible **au moins une fois** dans la vidéo finale.
- [ ] Easing utilisé est conforme (§4 / §8).

---

## 11. Usage avec HyperFrames (référence rapide)

HyperFrames = HTML + CSS + GSAP, raisonnement en **secondes** (pas en frames). Le design system se branche via 4 fichiers dans `lmdm/` (cf projet `~/Documents/Vidéo hyperframes/`) :

- `lmdm/tokens.css` — variables CSS (`--lmdm-bg`, `--lmdm-yellow`, easings, durées, safe areas) + classes utilitaires (`.lmdm-stage`, `.lmdm-surface`, `.lmdm-label`, `.lmdm-ghost`, `.lmdm-underline`, `.lmdm-cutout`).
- `lmdm/fonts.css` — Poppins en **`@font-face` local** (`assets/fonts/*.woff2`, sous-ensemble latin pour les accents FR). **Jamais** de `@import` Google Fonts : appel réseau qui casse le rendu déterministe.
- `lmdm/motion.js` — `window.LMDM.ease` (`inOut`/`outExpo` via CustomEase, fallback `power2.inOut`/`expo.out`), `window.LMDM.dur` (secondes), helpers `drawStroke` / `traceUnderline` / `enterFromLeft`.
- `lmdm/atoms.html` — galerie de référence des atoms SVG.

Brancher dans une composition :

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>
<link rel="stylesheet" href="../lmdm/fonts.css" />
<link rel="stylesheet" href="../lmdm/tokens.css" />
<!-- ... <script src="../lmdm/motion.js"></script> avant la timeline -->
```

Easings : `LMDM.ease.outExpo` pour les entrées, `LMDM.ease.inOut` pour le standard. Durées : `LMDM.dur.appear` (0.3s), `LMDM.dur.slide` (0.25s), etc. — valeurs canoniques dans le JSON §8 (ms ÷ 1000 = secondes).

Règles HyperFrames à respecter : tout élément timé porte `class="clip"` + `data-start`/`data-duration`/`data-track-index` ; une seule `gsap.timeline({paused:true})` enregistrée sur `window.__timelines["<composition-id>"]` ; logique déterministe (pas de `Date.now()`/`Math.random()`/fetch). Toujours `npm run check` après modification.

**Fond transparent (overlay CapCut)** : `--format mov`/`webm`/`png-sequence` rendent automatiquement avec transparence ; `--format mp4` garde le fond `#202022`.

---

## 12. PIPELINE « talking-head → motion overlay » (montage natif HyperFrames)

**Déclencheur** : Alex fournit une vidéo de lui qui parle (plein cadre vertical 1080×1920, format Reel). Objectif : ajouter du motion design LMDM par-dessus, **section par section**, et produire la vidéo finale montée — **prévisualisable en live dans le studio** (compo `index`).

Les 7 étapes, dans l'ordre. Chaque étape n'est finie que quand son **critère** est vérifié.

**Étape 1 — Sonder la source.**
`ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer,color_primaries,width,height,bit_rate -of default=noprint_wrappers=1 SRC` : dims, durée, audio, **espace couleur**.
✅ *Critère* : les 5 valeurs (largeur, hauteur, durée, présence audio, `color_transfer`) sont connues et notées.

**Étape 2 — Transcrire et découper en sections.**
`whisper-cli --model large-v3 --language fr` (les `.en` ne marchent pas en FR). Découper en sections par **sujet**, calées sur les timestamps. (« Cloud » entendu = **Claude**.)
✅ *Critère* : chaque section a un `start`/`end` en secondes issu des timestamps, la liste couvre 100 % de la durée sans trou ni chevauchement, et le format de chaque section est décidé (split par défaut, full si Alex le demande — `references/montage-talking-head.md`).

**Étape 3 — Transcoder la vidéo → `assets/video/base.mp4`.**
Cas courant **SDR** (`color_transfer=bt709`, DJI Osmo Pocket 3 en mode « Normal ») : **aucun tonemap** — `scale` vers 1080×1920 si besoin, keyframes denses `-g 30 -keyint_min 30 -sc_threshold 0`, `-crf 14`.
▶ **Vidéo source HDR (`color_transfer` = `arib-std-b67` ou `smpte2084`) → lis `references/transcodage-video.md` AVANT de lancer ffmpeg** (tonemap zscale obligatoire, sinon couleurs délavées ou teint orange).
✅ *Critère* : `ffprobe` de la sortie renvoie `color_transfer=bt709` ET le seek dans le studio ne freeze pas (keyframes denses).

**Étape 4 — Construire chaque section (compo HyperFrames LMDM).**
**Motion-first** (§0), `motion.js` **inliné** (pas `<script src>` externe : sinon race au 1er play → `LMDM is not defined`). GSAP + CustomEase **vendus en local** (`assets/vendor/`).
▶ Section CTA « commente un mot-clé » ou image qui zoome → `references/patterns.md`.
✅ *Critère* : **CHAQUE section du découpage (étape 2) a sa compo**, elle passe la **checklist §10** ligne à ligne, elle respecte les safe areas (§5), et `npm run check` est vert.

**Étape 5 — Logos (§12.1) et médias.**
✅ *Critère* : tout logo/média est **vendu en local** (`assets/logos/`, `assets/images/`), zéro appel CDN au rendu, et tout média qui ne remplit pas sa zone a son **fond flou** (§5.6).

**Étape 6 — Master natif `index.html`.**
▶ **Vidéo talking-head à assembler (visage + sections + audio) → `references/montage-talking-head.md`** (ordre DOM, hosts de section, `clip-path` du visage).
▶ **Panneau visage NOIR dans le studio → `references/visage-carre-noir.md`** (Mode A / Mode B, diagnostic console en 5 s).
✅ *Critère* : dans le studio, sur toute la durée, on voit le visage (jamais un carré noir), chaque section apparaît dans sa fenêtre et **uniquement** dans sa fenêtre, la voix off court de 0 à la fin, et les `var(--lmdm-*)` se résolvent (jaune = jaune, pas noir).

**Étape 7 — Preview live + révision section par section.**
Ouvrir la compo `index`, montrer à Alex, corriger.
✅ *Critère* : **Alex a vu la preview et validé section par section.** C'est CE feu vert qui débloque les sous-titres finaux, l'export et les SFX — rien avant.

**Après validation, dans cet ordre :**
1. ▶ **Sous-titres à produire → lis `references/sous-titres.md` AVANT d'écrire le moindre chunk** (le découpage se décide par **unité grammaticale**, pas par largeur ; les chunks finaux sont **dictés par Alex**).
2. ▶ **Export final → `references/montage-talking-head.md` §4** : l'export se fait **en ffmpeg**, PAS avec le render HyperFrames (qui rasterise et ramollit le visage).
3. ▶ **SFX / musique → UNIQUEMENT après validation du montage par Alex : `references/sfx-musique.md`.** (« mets le sound effect ET la musique » = SFX + musique de fond par défaut.)

### 12.1 Logos → skill theSVG

`npx skills add glincker/thesvg`. CDN : `https://cdn.jsdelivr.net/gh/glincker/thesvg@main/public/icons/{slug}/{variant}.svg` ; registre des slugs : `.../src/data/icons.json`. **Toujours les couleurs d'origine** (Alex y tient — pas de recolorage mono). **Vendre en local** (`assets/logos/`), jamais de CDN au rendu (déterminisme). Sur fond sombre, marques monochromes (GitHub, OpenRouter) → variant `dark` (= logo blanc). GLM → slug `zhipu` (couleur), `chatglm/color` ressort en currentColor.
