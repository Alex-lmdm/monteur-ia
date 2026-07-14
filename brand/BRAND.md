# Design system de la marque — branché dans HyperFrames (README du dossier `brand/`)

Ce dossier est le **portage concret** du design system Le Monde Du Marketing pour le moteur
HyperFrames (HTML + CSS + GSAP).

> **Source de vérité = le skill `motion-design`.** Palette, typo, règles motion, patterns et
> anti-slop y sont décrits une seule fois — **on ne les recopie pas ici** (pour éviter la
> divergence). Ce README couvre uniquement **les fichiers de ce dossier et comment les brancher**.

## Fichiers

| Fichier | Contenu |
|---|---|
| `tokens.css` | Variables CSS (palette, typo, motion, safe areas) + classes utilitaires + patterns |
| `fonts.css` | Chargement Poppins **en `@font-face` local** (`assets/fonts/*.woff2`, sous-ensemble latin FR). Jamais de `@import` Google Fonts (appel réseau = rendu non déterministe). |
| `motion.js` | Easings + durées GSAP, helpers (`drawStroke`, `traceUnderline`, `enterFromLeft`). Expose `window.BRAND`. |
| `atoms.html` | Galerie de référence des atoms SVG (ouvrir dans le navigateur, puis copier). |

## Brancher le design system dans une composition

Dans le `<head>` :

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>
<link rel="stylesheet" href="../brand/fonts.css" />
<link rel="stylesheet" href="../brand/tokens.css" />
```

Avant ta timeline (en bas du `<body>`) :

```html
<script src="../brand/motion.js"></script>
```

> ⚠️ Dans le **master** `index.html`, charger `fonts.css` + `tokens.css` dans le `<head>` est
> **obligatoire** : sinon les `var(--brand-*)` et les polices des sous-compos ne se résolvent pas
> (couleurs noires au lieu de jaune, police par défaut). Cf `motion-design` §14.4.
>
> Pour les sections montées en direct dans le studio, **inliner `motion.js`** (pas `<script src>`
> externe) pour éviter la race au 1er play (`{{BRAND_NAME}} is not defined`). Cf §14.2.

- `CustomEase` est optionnel mais recommandé : il reproduit **exactement** les cubic-bezier du
  design system. Sans lui, `motion.js` retombe sur `power2.inOut` / `expo.out` (très proches).

## Fond transparent (overlay CapCut)

- `--format mp4` → fond `#202022` opaque (vidéo autonome).
- `--format mov` / `webm` / `png-sequence` → **fond transparent** automatique, pour superposer
  l'animation sur ta vidéo dans CapCut.

## Piège linter (faux positif connu)

Le linter HyperFrames affiche un warning `font_family_without_font_face` sur `var(--brand-font-body)`.
**Faux positif** : le linter ne résout pas les variables CSS et prend `var(...)` pour un nom de
police. Le `@font-face` « Poppins » existe bien et Chrome le résout correctement au rendu (vérifié :
Poppins Black + accents FR s'affichent dans le MP4).

## Voir la démo

`compositions/brand-showcase.html` recrée l'esprit d'une section {{BRAND_NAME}} (cartes qui entrent, checkmark
tracé, underline jaune, lower-third) avec ce seul design system. Lancer `npm run dev` et l'ouvrir.

---

*Le langage visuel complet (palette, typo, motion, patterns, anti-slop) est dans le skill
`motion-design`. Ce fichier ne documente que le branchement technique du dossier `brand/`.*
