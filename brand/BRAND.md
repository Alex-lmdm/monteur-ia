# Ton design system — dossier `brand/`

Ce dossier est le **portage concret de TON identité visuelle** pour le moteur HyperFrames
(HTML + CSS + GSAP). Il n'appartient à aucune marque en particulier : tout ce qui est une
couleur, une police ou un skin de sous-titres y est **généré depuis ta config**.

> **Source de vérité des VALEURS = `brand.config.json`** (+ le preset de style choisi dans
> `templates/style-presets.json`). **Source de vérité de la MÉTHODE = le skill `motion-design`.**
> On ne recopie ni l'une ni l'autre ici : ce README ne documente que les fichiers du dossier.

## Fichiers

| Fichier | Contenu | Généré ? |
|---|---|---|
| `tokens.css` | Variables CSS (palette, typo, motion, safe areas), classes utilitaires, skins de sous-titres | **Oui** — `npm run sync` |
| `fonts.css` | `@font-face` locaux des polices de ton style (`assets/fonts/`) | **Oui** — `npm run sync` |
| `motion.js` | Easings + durées GSAP, helpers (`drawStroke`, `traceUnderline`, `enterFromLeft`). Expose `window.BRAND`. | Non |
| `atoms.html` | Galerie de référence des atoms SVG (ouvrir dans le navigateur, puis copier). | Non |

⚠️ **`tokens.css` et `fonts.css` ne sont pas versionnés et ne doivent pas être édités à la main** :
ils sont réécrits à chaque `npm run sync`. Pour changer une couleur ou une police, lance
`/setup visuel`, ou édite `brand.config.json` puis `npm run sync`.

## Ce qui est à toi, ce qui ne l'est pas

| Réglable (c'est ton identité) | Fixe (c'est la méthode) |
|---|---|
| Fond, surface, accent, couleur de texte | Safe areas Instagram (contrainte de la plateforme) |
| Polices body / display / sous-titres | Easings et durées d'apparition |
| Skin de sous-titres (5 au choix) | Découpage grammatical des sous-titres |
| Cadrage par défaut (split / visage plein) | Règle motion-first, zéro redondance texte |
| Style de la section CTA | Checklist anti-slop |

Les patterns du catalogue (ghost number, underline d'accent, cutout circulaire) sont des
**options**, pas une signature obligatoire. Les reprendre tous, à chaque vidéo, dans le même
ordre, c'est ce qui rend deux comptes indistinguables.

## Brancher le design system dans une composition

Dans le `<head>` :

```html
<script src="../assets/vendor/gsap.min.js"></script>
<script src="../assets/vendor/CustomEase.min.js"></script>
<link rel="stylesheet" href="../brand/fonts.css" />
<link rel="stylesheet" href="../brand/tokens.css" />
```

Avant ta timeline (en bas du `<body>`) :

```html
<script src="../brand/motion.js"></script>
```

> ⚠️ Dans le **master** `index.html`, charger `fonts.css` + `tokens.css` dans le `<head>` est
> **obligatoire** : sinon les `var(--brand-*)` et les polices des sous-compos ne se résolvent pas
> (couleurs noires au lieu de l'accent, police système). Cf `motion-design` §14.4.
>
> Pour les sections montées en direct dans le studio, **inliner `motion.js`** (pas `<script src>`
> externe) pour éviter la race au 1er play (`BRAND is not defined`). Cf §14.2.

- `CustomEase` est optionnel mais recommandé : il reproduit **exactement** les cubic-bezier du
  design system. Sans lui, `motion.js` retombe sur `power2.inOut` / `expo.out` (très proches).

## Ne jamais écrire une couleur en dur

Un `#f0f0f0` posé dans une compo survit à tout changement de style : la vidéo suivante sortira
avec la couleur d'un autre. **Toujours `var(--brand-*)`.** Les tokens disponibles :

`--brand-bg` · `--brand-surface` · `--brand-surface-contrast` · `--brand-text` · `--brand-muted` ·
`--brand-accent` · `--brand-contrast` (à poser SUR l'accent) · `--brand-stroke` (contour de
lisibilité) · `--brand-negative` (dataviz uniquement).

`--brand-white` et `--brand-yellow` existent encore comme **alias** de `--brand-text` et
`--brand-accent`, pour du code plus ancien. Ne pas les employer dans du code neuf : leur nom ment
dès que le style n'est ni sombre ni jaune.

## Fond transparent (overlay CapCut)

- `--format mp4` → fond `var(--brand-bg)` opaque (vidéo autonome).
- `--format mov` / `webm` / `png-sequence` → **fond transparent** automatique, pour superposer
  l'animation sur ta vidéo dans CapCut.

## Piège linter (faux positif connu)

Le linter HyperFrames affiche un warning `font_family_without_font_face` sur `var(--brand-font-body)`.
**Faux positif** : le linter ne résout pas les variables CSS et prend `var(...)` pour un nom de
police. Le `@font-face` existe bien dans `fonts.css` et Chrome le résout correctement au rendu.

## Voir la démo

`compositions/brand-showcase.html` recrée une section avec ce seul design system (cartes qui
entrent, checkmark tracé, underline d'accent, lower-third). Lancer `npm run dev` et l'ouvrir.

---

*Le langage visuel complet (règles motion, patterns, anti-slop) est dans le skill `motion-design`.
Ce fichier ne documente que le branchement technique du dossier `brand/`.*
