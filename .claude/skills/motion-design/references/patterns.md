# Patterns de section réutilisables

## Pattern CTA « commente un mot-clé » (RÉUTILISABLE tel quel)

Dès que le CTA d'une vidéo = « **commente `<MOT>` et je t'envoie X / le lien en DM** », reprendre CE design (en **split-screen 1080×920**, visage en bas) :
- **Avatar d'Alex** en haut, ~206px : sa tête détourée sur un **rond jaune `#ffee00`** (`assets/images/avatar.png` — Alex le fournit en PNG transparent ; le redimensionner ~400px). Animation pop-in (`scale 0.5→1`).
- **Champ commentaire** style réseau social en dessous : pill `--lmdm-surface` + bordure `#3a3a3d`, `border-radius:56px`, padding `28px 36px`. **Largeur modérée ~580px** (PAS trop large : le mot-clé est court, juste un peu de vide à droite), **police grosse ~54px en JAUNE**. De gauche à droite : **emoji 💬 petit** (`font-size:46px`), le **mot-clé qui se tape** (machine à écrire déterministe), une **flèche d'envoi jaune** (SVG paper-plane) qui pulse.
- **PAS** de handle/@texte en dessous (l'avatar suffit comme signature).
- **Sous-titre du CTA — RÈGLE** : ne JAMAIS écrire le mot « **lien** » dans les sous-titres d'un CTA (risque de **shadowban**) → mettre l'**emoji 🔗** (U+1F517, les deux maillons) à la place. Ex. : sous-titre « **Si tu veux le 🔗** » (et non « Si tu veux le lien »). L'emoji rend bien en couleur même dans le bandeau Bowlby noir-sur-jaune.
- Détails de réglage validés par Alex : avatar **~182px**, **petit espace après le 💬** (`margin-right:10px` sur l'icône), et **léger zoom-avant de tout le groupe** (`.center` `scale 1→1.08`, transform-origin center) **une fois le mot-clé fini d'être tapé** (~0.05s après la fin de la machine à écrire).

(Réf. d'implémentation : `compositions/s8-cta.html` du projet « Claude Code gratuit ».)

## Pattern « image qui zoome » (Ken Burns)

Pour mettre en avant une donnée d'une capture (ex. S3 = repo GitHub, zoom sur « 32.4k stars ») : `.zoomer` (transform-origin 0 0) contenant l'`<img>` + un surligneur `.hl` (dans le même repère, donc il suit le zoom), animés en GSAP `tl.to("#zoomer",{x,y,scale,...})` du plan large vers la donnée + `tl.to("#hl",{width:...})` (marqueur jaune `mix-blend-mode:multiply`). Une capture d'écran est forcément un peu douce une fois agrandie (basse résolution) — limiter le scale final (~1.5).
