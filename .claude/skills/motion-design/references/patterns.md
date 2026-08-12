# Patterns de section réutilisables

> ⚠️ **Ce sont des recettes, pas une signature.** Les reprendre toutes, à chaque vidéo, dans le même
> ordre, c'est ce qui rend deux comptes indistinguables. Avant d'en poser un : « est-ce que cette
> section a vraiment besoin de ça, ou est-ce que je le mets parce qu'il est écrit ici ? »
>
> Toutes les couleurs et polices ci-dessous passent par `var(--brand-*)`. **Aucun hex en dur.**

## Pattern CTA « commente un mot-clé »

Dès que le CTA d'une vidéo = « commente `<MOT>` et je t'envoie X / le 🔗 en DM ».
**Le style vient de `cta.style`** (`brand.config.json`, posé au bloc D du setup) — ne choisis pas à
la place du créateur, lis sa config. Les variantes sont décrites dans `ctaStyles` de
`templates/style-presets.json` :

### `comment-field` — champ de commentaire

Split-screen 1080×920, visage en bas.
- **Avatar du créateur** en haut, ~206 px : sa tête détourée sur un rond `var(--brand-accent)`
  (`assets/images/avatar.png`, PNG transparent, redimensionné ~400 px). Pop-in `scale 0.5→1`.
  Pas d'avatar fourni ? Le mot-clé seul suffit, ne pas inventer de substitut.
- **Champ commentaire** en dessous : pill `var(--brand-surface)` + bordure discrète,
  `border-radius:56px`, padding `28px 36px`. **Largeur modérée ~580 px** (le mot-clé est court),
  police ~54 px en `var(--brand-accent)`. De gauche à droite : emoji 💬 (~46 px, `margin-right:10px`),
  le **mot-clé qui se tape** (machine à écrire déterministe), une **flèche d'envoi** en accent (SVG
  paper-plane) qui pulse.
- **Léger zoom-avant du groupe** (`scale 1→1.08`, transform-origin center) ~0,05 s après la fin de
  la frappe.
- Pas de handle en dessous : l'avatar suffit comme signature.

### `keyword-stamp` — le mot-clé tamponné

Plein écran ou split. Le mot-clé **seul**, très gros (`--brand-font-display`, 140-200 px), qui
arrive en un impact : `scale 1.6→1` + `opacity 0→1` sur 250 ms, easing `BRAND.ease.outExpo`, puis
un léger recul (`scale 1→0.98`). Un mot en `var(--brand-accent)`, rien d'autre à l'écran.
Le plus rapide à lire, le moins bavard.

### `chat-bubble` — bulle de conversation

Deux bulles façon messagerie, en bas de zone : la première (sortante, `var(--brand-accent)` avec
texte `var(--brand-contrast)`) contient le mot-clé et entre par la droite ; la seconde (entrante,
`var(--brand-surface)`) arrive 400 ms après avec la réponse promise. Indicateur « en train
d'écrire » (3 points qui pulsent) entre les deux si la section dure > 3 s.

### `none` — pas de section CTA animée

Le mot-clé passe uniquement en sous-titre et dans la légende. Légitime : une section CTA animée sur
une vidéo courte peut coûter plus qu'elle ne rapporte.

### Règle commune à toutes les variantes

**Ne JAMAIS écrire le mot « lien » dans les sous-titres d'un CTA** (risque de shadowban) → mettre
l'emoji `cta.linkEmoji` (défaut 🔗) à la place. Ex. : « Si tu veux le 🔗 » et non « Si tu veux le
lien ». L'emoji rend bien en couleur, même dans le bandeau de sous-titres.

(Réf. d'implémentation : une compo `compositions/s-cta.html`.)

## Pattern « image qui zoome » (Ken Burns)

Pour mettre en avant une donnée d'une capture (ex. zoom sur un chiffre-clé d'un screenshot) :
`.zoomer` (transform-origin 0 0) contenant l'`<img>` + un surligneur `.hl` (dans le même repère, donc
il suit le zoom), animés en GSAP `tl.to("#zoomer",{x,y,scale,...})` du plan large vers la donnée +
`tl.to("#hl",{width:...})` (marqueur `var(--brand-accent)`, `mix-blend-mode:multiply`). Une capture
d'écran est forcément un peu douce une fois agrandie (basse résolution) — limiter le scale final
(~1.5).
