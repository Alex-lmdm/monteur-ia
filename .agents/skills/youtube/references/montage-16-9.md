# Construire le montage d'une vidéo YouTube (1920×1080)

Depuis le dossier de la vidéo (`youtube/<nom>/`). Le dérush est fait : `derush/<cut>_enhanced.mp4`
(pleine résolution), `<cut>_cuts.json`, `<cut>_words.json`, `assets/video/base.mp4` (1920×1080).

## 1. Le plan de montage (`work/plan-montage.md`)

Avant toute composition, écris le plan, à partir du texte et de `references/doctrine.md` :

```
## Chapitres
00:00 Introduction · 01:12 <titre> · …
## Sections
s0-hook      over  prises 0-4    hook face caméra, logo de la marque citée, plan large
s1-outils    cote  prises 5-11   panneau : les 3 outils, une ligne par outil quand il est dit
s2-demo      full  prise 12      capture de l'outil, zoom sur le bouton
…
## Textes d'appui
00:41 « 100 % GRATUIT » · 02:05 « 3 OUTILS » · …
## B-roll / captures à fournir
- capture du site X (je la fais) · vidéo de démo Y (à demander au client)
```

Montre-le au client en clair (pas le fichier) : les parties, ce qui s'affichera, ce qu'il doit
fournir (une capture, une vidéo). Il valide ou corrige ; première vidéo : pas d'arrêt.
Puis reporte-le dans `tools/sections.py` (`CUTS_PATH`, `LAYOUT`, `EMPHASES`) et lance
`python3 tools/sections.py` : il vérifie la couverture des prises et affiche les **alertes de
rythme** (plan fixe trop long, trop longtemps sans visuel, chapitres trop courts). Les corriger.

## 2. Les visages pré-cadrés

1. `python3 tools/build_faces.py --apercu` puis **regarde** `work/cadrage-apercu.jpg` : blanc =
   large, jaune = serré, rouge = très serré.
2. Ajuste `brand.config.json` → `youtube.cadrage` : `visageX` (centre du visage, 0 = gauche,
   1 = droite) et `yeuxY` (hauteur des yeux, 0 = haut). Les cadres serrés gardent les yeux vers
   40 % de leur hauteur. Réglage technique : pas d'accord à demander, il vaut pour ses prochaines
   vidéos tant qu'il filme au même endroit.
3. `python3 tools/build_faces.py` : `assets/video/visage-large.mp4`, `visage-serre.mp4`,
   `visage-tres-serre.mp4` (seulement ceux utilisés), en 1920×1080 à 30 im/s, découpés dans le dérush
   pleine résolution. Un cadre agrandi de plus de ×1,35 (rush 1080p) est signalé moins net.

## 3. Les compositions

Une composition par section `cote`, `over` ou `full` sans `media`, au nom de son id :
`compositions/<id>.html`. Pars de `compositions/exemple-panneau.html` (le niveau attendu) et des
blocs du registre (`npx hyperframes catalog`, skill `hyperframes-registry`), aux couleurs de la
marque. Les invariants de l'exemple valent pour toutes :

1. Racine `#<id>` avec `data-composition-id="<id>"`, `data-duration` = durée de SA section,
   `data-width` / `data-height` : **960×1080** (cote), **1920×1080** (over, full).
2. Tout le CSS **scopé** sous `#<id>`, jamais de règle sur `html`/`body`, éléments internes en classes.
3. Timeline GSAP `paused`, dans une **IIFE**, sur `window.__timelines["<id>"]`, un seul sélecteur
   par tween, `fromTo` explicites, entrées en `opacity` + `scale` (jamais `x`/`y`, ni `left`/`top`).
4. Couleurs et polices en `var(--brand-*)` ; zones en `var(--brand-yt-*)`.
5. `over` : racine **sans fond** (transparente), rien sur le visage ni la bouche.
6. `cote` : fond `var(--brand-bg)` permis (le panneau ne couvre que la moitié libre). Entrée du
   panneau = même geste que le glissement : le conteneur interne `.pan` (fond compris) glisse en
   `x` de 960 à 0 en 0,6 s `power2.inOut` à 0 (panneau à gauche : de -960 à 0).
   Sortie : le contenu s'efface dans les 0,25 dernières secondes (le fond reste) ; le créateur
   revient au centre par-dessus après la coupe, sans texte qui disparaît d'un coup.
7. `full` : opaque, fond de marque ; un média qui ne remplit pas l'écran → fond flou.
8. **Export rapide** : aucun `clip-path`, masque, mode de fusion ni 3D **animés** (un texte qui
   s'écrit : un cache qui se retire en `scaleX`). Une seule image animée ainsi suffit à faire
   passer tout l'export sur un seul processeur : deux à trois fois plus long (mesuré).

Tailles en 16:9 (lisible sur un téléphone à l'horizontale comme sur une télé) : titre 56 à 72 px
Black, lignes 36 à 44 px, détail 26 à 30 px minimum. Un B-roll (`{"media": "x.mp4"}`) n'est jamais
dans une composition : il est posé par le master (vidéo 16:9 pré-cadrée dans `assets/video/`).

Contrôle d'une composition seule : un dossier `probe/` (copie de la compo en `index.html`, liens
symboliques `assets` et `brand`), `npx hyperframes snapshot probe --at …`, puis supprimer `probe/`.

## 4. Textes d'appui, master, contrôles

```bash
python3 tools/build_emphases.py --write   # compositions/emphases.html + exports/sous-titres.srt
python3 tools/build_master.py --write     # index.html : visages, glissements, sections, textes
npm run check                             # 0 erreur avant de montrer
npx hyperframes snapshot --at 12,47.5,95  # instants choisis : une entrée de panneau, un plein écran, un texte
```

- **Regarde** chaque snapshot : visage net et entier, panneau lisible, rien sur la bouche, rien
  dans les 150 px du bas, texte d'appui sur le torse.
- Une section qui change de prises ou de format : modifier `sections.py`, puis relancer
  `build_emphases.py --write` et `build_master.py --write` (les sons posés sont gardés).
- Le master contient une `<video>` plein cadre par cadre, calée sur la timeline du dérush ; il
  montre la bonne à chaque coupe. Ne jamais l'éditer à la main : tout part de `sections.py`.

## 5. Export et finalisation

- Dans l'app : « Clique sur **Export** en haut à droite, puis dis-moi quand c'est fini. » Hors de
  l'app : `npm run render` (exports/FINAL.mp4). Temps : environ la durée de la vidéo.
- Puis **toujours** `python3 tools/finaliser.py` : niveau -14 LUFS sur le mixage final (un même gain
  pour tout, crêtes vraies limitées, image copiée, pas réencodée), contrôle `tools/check_export.py`
  (format, visage net et calé sur la voix, écart son/image, niveau), puis la vidéo dans
  Téléchargements, à la place de la copie de l'app (sinon « <nom>.mp4 ») : **c'est ce fichier** qui
  se téléverse sur YouTube.
- Un point KO : le corriger dans le montage et réexporter ; ne jamais livrer un export KO.
