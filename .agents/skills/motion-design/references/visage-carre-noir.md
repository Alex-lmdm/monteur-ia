# Panneau visage NOIR dans le studio — diagnostic (bug « carré noir », résolu 2026-06-08)

## ⚠️ RÈGLE — Aucun élément opaque empilé au-dessus du `<video>` visage

**Tout élément plein cadre (`position:absolute; inset:0`) placé APRÈS le `<video>` visage dans le DOM (ou avec un `z-index` supérieur) DOIT avoir `background: transparent`.**

Un fond opaque (`var(--brand-bg)`, `#000`, blanc…) plein cadre au-dessus du visage peint un rectangle qui le **masque dans le STUDIO uniquement**. À l'export ffmpeg il n'apparaît pas (la couche vidéo native est recomposée par-dessus, et le rendu par couches ignore le `background` des `body`). C'est ce décalage studio↔download qui trompe : « un élément par-dessus mon visage ». **Ça récidive à chaque nouvelle classe/sous-compo si la règle n'est pas appliquée** (occurrences typiques : `.face-full` opaque, `.screen-full` opaque, body de sous-compos, render sans sous-titres).

> Le SEUL aplat opaque autorisé est le **fond de marque tout en BAS de la pile** : `#bgbase { background:var(--brand-bg) }` à `data-track-index:0`, premier enfant du DOM → peint sous tout le reste. ⚠️ Le `track-index` ne contrôle PAS le layering visuel (c'est l'ordre DOM / `z-index`) ; `#bgbase` est sous le visage parce qu'il est le 1er enfant, pas parce que track 0.

**Liste de contrôle « rien d'opaque au-dessus du visage » (à chaque master) :**
- [ ] `.face-full`, `.face-bottom` (wrappers source du visage) → `background: transparent`
- [ ] `.screen-full`, tout `.screen-*` / `.illu-*` (wrappers vidéo screen-rec / illustration) → `background: transparent`. ⚠️ Piège classique : on crée une nouvelle classe wrapper avec `background:var(--brand-bg)` hérité, sans timing, placée après `.face-*` → masque le visage en continu.
- [ ] `html, body` / conteneur racine des sous-compos montées **plein cadre** (`data-composition-src`, host `1080×1920`, ex. `s2.html`, `captions.html`) → `background: transparent`. Le fond de marque vient de `#bgbase`, jamais du body des sous-compos.
- [ ] `#bgbase` (et lui seul) → `background:var(--brand-bg)`, `data-track-index:0`, **premier enfant du DOM**.
- [ ] Tout nouvel `position:absolute; inset:0` ajouté au master → **transparent par défaut**, sauf `#bgbase`.

**Deux pannes, même symptôme (panneau visage NOIR) — ne pas confondre :**
- **Mode A — la `<video>` ne PEINT pas** : surface partielle / déplacée / oversize+overflow → le compositeur du studio ne dessine pas la frame dès qu'une sous-compo est présente. Fix = surface **plein cadre** + `clip-path` sur le wrapper + cadrage via `transform` sur la vidéo.
- **Mode B — la `<video>` PEINT mais est MASQUÉE** par un overlay opaque plein cadre au-dessus. Fix = passer cet overlay en `background: transparent`.

La recette de diagnostic ci-dessous tranche entre A et B en 5 s.

## Diagnostic LIVE — trouver l'overlay opaque qui masque le visage

À coller dans la console du studio (ou via `javascript_tool` ciblant l'iframe de preview). Étape 1 = QUI est au-dessus du visage ; étape 2 = preuve que la `<video>` peint (donc Mode B = masquage, pas Mode A = non-peinture).

```js
// 1) PILE D'EMPILEMENT à la position du visage (panneau bas du split ~540,1400)
const ifr  = document.querySelector('iframe');           // iframe de preview du studio
const doc  = ifr ? ifr.contentDocument : document;
const face = doc.querySelector('.face-bottom video, .face-full video');
const r    = face.getBoundingClientRect();
const cx   = r.left + r.width  / 2;
const cy   = r.top  + r.height * 0.75;                    // 0.75 = plein dans le panneau visage
console.table(doc.elementsFromPoint(cx, cy).map(el => ({  // du plus HAUT au plus BAS
  tag: el.tagName,
  cls: typeof el.className === 'string' ? el.className : '',
  bg : getComputedStyle(el).backgroundColor,
  z  : getComputedStyle(el).zIndex,
})));
// Coupable = 1er élément listé AVANT la <video> dont bg n'est PAS "rgba(...,0)"/transparent
// (typiquement .screen-full peint avec le fond de marque). Fix : background:transparent dessus.

// 2) PREUVE que la <video> PEINT (Mode B : visage présent mais masqué)
const c = doc.createElement('canvas'); c.width = 160; c.height = 284;
const ctx = c.getContext('2d'); ctx.drawImage(face, 0, 0, c.width, c.height);
const d = ctx.getImageData(40, 120, 80, 80).data;
let s = 0; for (let i = 0; i < d.length; i += 4) s += (d[i]+d[i+1]+d[i+2]) / 3;
console.log('luminosite moy =', Math.round(s / (d.length / 4)), '/255');
// ~136/255 -> la video peint -> Mode B (overlay opaque) : corriger le bg trouve en (1)
// ~0/255   -> la video ne peint PAS -> Mode A (carre noir) : surface plein cadre + clip-path
```

⚠️⚠️ **LE bug à NE JAMAIS reproduire (Mode A — la `<video>` ne se peint pas)** : une `<video>` visage en **surface PARTIELLE** (positionnée en sous-zone `top:920`, déplacée, ou **surdimensionnée/recadrée par `overflow`**) **ne se peint PAS** dans le preview studio (panneau bas **NOIR**) dès qu'une sous-composition (`data-composition-src`) est présente. La `<video>` **DOIT être une surface PLEIN CADRE à l'origine (1080×1920 en 0,0)** ; on n'affiche que la moitié basse via **`clip-path` sur le WRAPPER** et on cadre le visage via **`transform` SUR LA VIDÉO**. (Fausses pistes écartées : `class="clip"`, oversize-vs-fill, `data-track-index`, version 0.6.60/72/81 — toutes reproduisent. Aggravant : `.face-full` à fond opaque masque le split → le mettre **transparent**.)

→ Pattern CSS correct à appliquer : `references/montage-talking-head.md` §3.
