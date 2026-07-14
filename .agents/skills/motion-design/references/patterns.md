# Patterns de section réutilisables

## Pattern CTA « commente un mot-clé » (RÉUTILISABLE tel quel)

Dès que le CTA d'une vidéo = « **commente `<MOT>` et je t'envoie X / le 🔗 en DM** », reprendre CE
design (en **split-screen 1080×920**, visage en bas) :
- **Avatar du créateur** en haut, ~206px : sa tête détourée sur un **rond accent
  `var(--brand-yellow)`** (`assets/images/avatar.png` — fourni en PNG transparent ; le redimensionner
  ~400px). Animation pop-in (`scale 0.5→1`).
- **Champ commentaire** style réseau social en dessous : pill `var(--brand-surface)` + bordure
  `#3a3a3d`, `border-radius:56px`, padding `28px 36px`. **Largeur modérée ~580px** (PAS trop large : le
  mot-clé est court), **police grosse ~54px en ACCENT**. De gauche à droite : **emoji 💬 petit**
  (`font-size:46px`), le **mot-clé qui se tape** (machine à écrire déterministe), une **flèche d'envoi
  accent** (SVG paper-plane) qui pulse.
- **PAS** de handle/@texte en dessous (l'avatar suffit comme signature).
- **Sous-titre du CTA — RÈGLE** : ne JAMAIS écrire le mot « **lien** » dans les sous-titres d'un CTA
  (risque de **shadowban**) → mettre l'emoji `cta.linkEmoji` (défaut 🔗, U+1F517) à la place. Ex. :
  sous-titre « **Si tu veux le 🔗** » (et non « Si tu veux le lien »). L'emoji rend bien en couleur même
  dans le bandeau caption.
- Détails de réglage : avatar **~182px**, **petit espace après le 💬** (`margin-right:10px` sur
  l'icône), et **léger zoom-avant de tout le groupe** (`.center` `scale 1→1.08`, transform-origin
  center) **une fois le mot-clé fini d'être tapé** (~0.05s après la fin de la machine à écrire).

(Réf. d'implémentation : une compo `compositions/s-cta.html`.)

## Pattern « image qui zoome » (Ken Burns)

Pour mettre en avant une donnée d'une capture (ex. zoom sur un chiffre-clé d'un screenshot) :
`.zoomer` (transform-origin 0 0) contenant l'`<img>` + un surligneur `.hl` (dans le même repère, donc
il suit le zoom), animés en GSAP `tl.to("#zoomer",{x,y,scale,...})` du plan large vers la donnée +
`tl.to("#hl",{width:...})` (marqueur accent `mix-blend-mode:multiply`). Une capture d'écran est
forcément un peu douce une fois agrandie (basse résolution) — limiter le scale final (~1.5).
