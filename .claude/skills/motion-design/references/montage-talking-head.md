# Montage talking-head — format, master, visage, export

## 0. ⛔ Les frontières de section viennent des VRAIES COUPES (bug récurrent)

**Symptôme** : au passage plein-écran → split, on voit ~0,2 s de la **fin de la prise précédente**
(le créateur regarde ailleurs, il n'a pas encore attaqué sa phrase).

**Cause** : les `data-start` du master avaient été pris dans le **`timeline.json` Whisper**. Or
(a) Whisper démarre un segment **0,1–0,25 s trop tôt** (il englobe le souffle qui précède la voix),
et (b) le `concat` ffmpeg du dérush arrondit chaque prise à la frame → les bornes réelles du fichier
sont **~+0,07 s** (jusqu'à +0,12 s en fin de timeline) après les bornes théoriques. La fenêtre du
visage s'ouvrait donc **avant le jump-cut**.

**Règle** :
- Les `data-start` / `data-duration` des sections, les **fenêtres du visage** et les **bornes de
  phrase des sous-titres** viennent **TOUS** de **`derush/<cut>_cuts.json`** (les jump-cuts mesurés
  dans le fichier livré — cf skill `derush` §7bis). **Jamais** de Whisper, jamais d'une valeur tapée à
  la main.
- **Une seule source, lue par les 3 générateurs** (sous-comps, master, sous-titres) : sinon ils se
  désynchronisent. Réf : `tools/sections.py` + `tools/build_master.py` (le master est **généré**, plus
  édité à la main).
- En cas de doute sur une frontière, **arrondir vers le TARD** : quelques frames de motion en trop
  sont invisibles, quelques frames du visage d'avant se voient tout de suite.

## 0bis. ⛔ Le RENDER injecte toutes les sous-comps dans UN SEUL document

Le **studio** monte chaque sous-composition dans **son propre iframe** → tout y semble parfait. Le
**render**, lui, **injecte le DOM et le CSS de TOUTES les sous-comps dans un document unique**. Deux
conséquences invisibles en preview, qui peuvent ruiner un export complet :

**a) Le CSS des sous-comps est GLOBAL.**
- ❌ **Jamais de `html, body { height: 920px }`** dans une sous-comp : le 920 d'un split écrase le
  1920 des plein-écrans → **le calque entier est rogné à 920 px**. Mettre `html, body { width:100%;
  height:100% }` et porter la taille sur **la racine scopée**.
- ❌ **Jamais de sélecteur nu** (`#panel`, `.item`, `#win`) : il touche les autres sections. **Tout
  scoper** sous la racine : `#<composition-id> .panel { … }`, et les id internes deviennent des
  **classes** (un id doit rester unique dans le document unique).
- ❌ **Jamais de sélecteur GSAP nu** : `tl.from("#win", …)` attrape le `#win` d'**une autre** section.
  Toujours `tl.from("#<composition-id> .win", …)`.
- ❌ **Jamais de `const`/`let` au top-level** d'un script de sous-comp (portée globale partagée) →
  envelopper la timeline dans une **IIFE**.

**b) Les `<script>` des sous-comps ne sont montés QUE si le master les référence par un chemin qui
NE REMONTE PAS.** Avec `data-composition-src="../compositions/x.html"` (master hors racine), le
runtime monte le DOM + le CSS mais **PAS les scripts** : **aucune timeline ne tourne**, tout reste
figé à l'état CSS initial — et **le studio n'en montre rien**.
→ **Le calque d'export (master sans le visage) doit vivre À LA RACINE**, à côté d'`index.html`, et
référencer `compositions/…` à l'identique. Deux HTML racines = erreur de lint
`multiple_root_compositions` → on l'**écrit, on rend, puis on le supprime** (cf `tools/build_overlay.py --render`).

**Contrôle obligatoire avant de livrer** : `npm run check` ne voit RIEN de tout ça (il valide la
structure, pas le calque rendu). Lancer **`python3 tools/check_export.py`** sur `renders/overlay.mov` :
il vérifie (A) l'opacité du calque section par section et (B) que les timelines tournent vraiment
(un élément posé à `opacity:0` par GSAP doit être invisible au début de sa section).

## 1. La règle de format (le défaut vient de la config)

Le cadrage de départ vient de `brand.config.json` → `montage.defaultLayout`. Deux valeurs :

- **`"split"`** (valeur par défaut du config) : chaque section démarre en **split-screen** —
  motion design en HAUT (**1080×920**), **visage en BAS**. Le cadrage du visage = `montage.splitTransform`.
- **`"faceplein"`** : chaque section démarre **visage en plein écran** (**1080×1920**, `.face-full`,
  cadrage = `montage.fullFaceTransform`), et le motion/les visuels se posent **PAR-DESSUS** le visage
  en **surimpression `background: transparent`** (jamais un panneau opaque qui coupe l'écran). On voit
  le créateur en continu ; les animations flottent près de sa tête.

**Dans les deux cas, le créateur dirige section par section** — il peut passer n'importe quelle
section en : visage plein écran seul, visuel/motion plein écran seul (recouvre le visage), ou split.
Formats techniques de section : `1080×920` (split) ou `1080×1920` (full). On commence TOUT sur le
`defaultLayout` choisi, puis on ajuste au fil des retours.

> Ancien nom : `montage.splitByDefault` (booléen) a été remplacé par `montage.defaultLayout`. Si tu
> lis un vieux config avec `splitByDefault: true`, traite-le comme `defaultLayout: "split"`.

## 2. Master natif `index.html` (les pièges)

- 1080×1920, `data-duration` = durée vidéo. **Charger `brand/fonts.css` + `brand/tokens.css` dans le
  `<head>` du master** — SINON les `var(--brand-*)` et les polices des sous-comps **ne se résolvent
  pas** dans la composition par couches (→ couleurs noires au lieu de l'accent, police par défaut).
  Diag : une couleur en dur `#ffee00` marche mais `var(--brand-yellow)` non.
- `<audio src="assets/video/base.mp4" data-volume="1" data-start="0" data-duration="DUREE" data-track-index="9">` = voix off (toute la durée).
- Sections via `data-composition-src` avec **style explicite `width/height/overflow`** (sinon la
  sous-compo se rend en plein écran et recouvre tout). Split → host `1080×920` `top:0` ; full → host
  `1080×1920` `top:0`.
- La **vidéo du visage** = surface plein cadre + `clip-path`/`transform` (pattern OBLIGATOIRE
  ci-dessous, contre le bug du carré noir → `references/visage-carre-noir.md`). **SANS `class="clip"`**
  ; `data-start`/`data-duration` couvrent SEULEMENT la/les fenêtre(s) split (sinon elle déborde sur
  les sections full). `.face-bottom` ET `.face-full` en `background: transparent`.
- **⚠️ ORDRE DOM = LAYERING (pas le track-index)** : le `.face-full` (plein-écran VISAGE) doit être
  **APRÈS toutes les sections** dans le DOM, sinon une section (même hors de sa fenêtre) peut
  **peindre par-dessus** le plein-écran → on voit la section au lieu du visage. Ordre correct :
  **`sections` < `.face-full` < `captions`**. Et **mettre `class="clip"` sur chaque host de section
  `data-composition-src`** (visibilité gérée par le framework ; sans ça un host peut « rester peint »).
- **Piège animation vs placement studio** : quand on repositionne un élément dans le studio, ça ajoute
  la propriété CSS **`translate`** (individuelle) sur l'élément. Si l'animation GSAP d'entrée joue
  aussi sur la **position** (`y`/`x`), les deux se combinent → petit **glissement/décalage** à
  l'apparition. Solution : pour les entrées, animer **uniquement `opacity` + `scale`** (qui composent
  proprement avec `translate`), PAS `x/y`. L'élément apparaît alors pile où il a été placé.

## 3. Placement du visage en split-screen — PATTERN OBLIGATOIRE

> Si le panneau visage apparaît NOIR dans le studio → `references/visage-carre-noir.md` (diagnostic
> Mode A / Mode B).

**Le cadrage du visage (transform CSS du split ET crop ffmpeg de l'export) se lit dans
`brand.config.json` → `montage.splitTransform` et `montage.faceCrop`** (calibrés par `/setup` selon
la caméra et la distance de tournage). Les valeurs ci-dessous sont un **exemple par défaut** (caméra
type DJI Osmo Pocket 3, cadrage habituel) — reprendre la STRUCTURE, remplacer les nombres par ceux de
la config.

**Pattern par défaut — reprendre TEL QUEL (nombres = `montage.splitTransform`) :**
```css
/* Wrapper plein cadre, clippé à la moitié basse (clip en espace écran, wrapper non transformé) */
.face-bottom { position:absolute; inset:0; overflow:hidden; background:transparent; clip-path: inset(920px 0 0 0); }
/* Vidéo = SURFACE PLEIN CADRE ; cadrage du visage via transform = montage.splitTransform */
.face-bottom video { position:absolute; inset:0; width:1080px; height:1920px; object-fit:cover;
  transform-origin:0 0; transform: translate(-216px, 410px) scale(1.40); }
/* Plein-écran VISAGE : fond TRANSPARENT obligatoire + léger zoom sur la tête.
   transform = paint-only, la box reste plein cadre. */
.face-full { position:absolute; inset:0; overflow:hidden; background:transparent; }
.face-full video { position:absolute; inset:0; width:1080px; height:1920px; object-fit:cover;
  transform: scale(2); transform-origin: center 35%; }
```
**Plein écran VISAGE** (quand une section entière = juste le visage en grand, ex. « pattern break ») :
utiliser `.face-full` (surface plein cadre, fond transparent) avec un **zoom serré sur la tête**
(exemple `transform: scale(2); transform-origin: center 35%` — le visage est ainsi HAUT, les
sous-titres passent dessous ; **`transform-origin` % plus GRAND = visage plus HAUT**, ajuster selon la
vidéo) — et **sous-titres à ~59 % (`y≈1140`, sous le centre)** (cf `references/sous-titres.md`). Le
`<video>` plein cadre n'a PAS le bug du split (il est déjà plein cadre).

Les `<video>` visage : **SANS `class="clip"`** (le framework gère leur visibilité via les data-attrs ;
ne jamais animer width/height/top/left d'une `<video>`), `src="assets/video/base-proxy.mp4"` (jamais un
fichier séparé → ne se compose pas), `data-start`/`data-duration`/`data-media-start`/`data-track-index`
(track au-dessus des sections).

**Ajustement du cadrage = UNIQUEMENT via `transform`** : `scale` = zoom · **2e valeur de `translate`**
= hauteur (plus petit = plus haut) · 1re valeur = horizontal. ⚠️ **NE PAS dragger/resizer la vidéo dans
le studio** (repositionne la surface → re-déclenche le carré noir). Une fois calé, reporter les valeurs
dans `montage.splitTransform`.

**Correspondance transform ↔ crop (indispensable à `/setup` et à l'export)** : le crop de `base.mp4`
qui CORRESPOND au transform de l'exemple = **`crop=771:714:154:364,scale=1080:1000`** (overlay à `0:920`
sur les fenêtres split). **Formule générale** : pour `transform: translate(Tx, Ty) scale(S)`, la zone
source visible est `src_x = (0 .. 1080 - Tx) / S`, `src_y = (920 - Ty .. 1920 - Ty) / S` →
`crop=w:h:x:y` puis `scale=1080:1000`. C'est ce crop qui est stocké dans `montage.faceCrop`. Si le
transform change, recalculer le crop avec cette formule.

## 4. Export final = ffmpeg, PAS le render HyperFrames (qualité visage)

**Le render HyperFrames RASTERISE/ramollit la couche vidéo** (visage flou : la même frame depuis
`base.mp4` est nette, depuis le render HyperFrames elle est floue). Donc :
- **Studio HyperFrames** = preview/édition live uniquement (visage doux dans l'aperçu = normal).
- **Export final** = **compositer en ffmpeg** (couche vidéo native, zéro rasterisation) → visage net.
  Modèle (split S1 + sections plein écran S2–S8 en overlay, audio de la base) :
```bash
ffmpeg -y -i assets/video/base.mp4 -i sections/s1.mp4 -i sections/s2.mp4 ... \
 -filter_complex "[0:v]split=2[bg][c];[c]crop=771:714:154:364,scale=1080:1000[face];\
 [bg][1:v]overlay=0:0:enable='between(t,0,T1)'[v1];[v1][face]overlay=0:920:enable='between(t,0,T1)'[v2];\
 [2:v]setpts=PTS+T1/TB[d2];[v2][d2]overlay=0:0:enable='between(t,T1,T2)'[v3]; ...(s3..s8)... [vout]" \
 -map "[vout]" -map 0:a -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/FINAL.mp4
```
Le `crop` du visage doit correspondre EXACTEMENT au `transform` CSS du split (= `montage.faceCrop`,
dérivé de `montage.splitTransform` par la formule du §3). Un crop désaligné = un cadrage faux à
l'export. `-crf 16` (le bitrate moyen paraît bas car le motion design plein écran compresse énormément
; le visage reçoit beaucoup de bits).
