# Police display statique de la marque (STATIQUE UNIQUEMENT)

**La police display est hors scope du motion.** En vidéo, les gros titres sont portés par le body en
graisse Black (`visual.fontBody`). Cette spéc concerne les formats **statiques** (carrousels, visuels,
miniatures) où le texte porte tout.

La police display de la marque = `brand.config.json` → `visual.fontDisplay`. Fichier custom exporté
dans chaque projet qui l'utilise : `brand/fonts/<display>.otf`.

> **Coluna** est un bon **exemple** de police display : condensée, bold, faite pour frapper en gros. Si
> ta marque n'a pas de display propre, une condensée de ce genre (ou la pile de secours ci-dessous)
> convient. Remplace « Coluna » par la valeur de `visual.fontDisplay`.

## Règles

- **TOUJOURS EN UPPERCASE**. La display existe en bold condensé pour frapper.
- Toujours pour hooks / titres / mots impactants. **Jamais pour du texte courant.**
- **Stroke noir pur `#000000`** : 3 px outside (Figma) ou 6 px centered (canvas).
- **Drop shadow légère** : `x=0, y=4, blur=0, color=rgba(0,0,0,0.55)`. Subtil mais décolle le texte des
  fonds chargés.
- Taille typique : **90 à 150 px en 1080×1350**. En vertical 1080×1920, pousser à **180-220 px** sur un
  mot court.
- **Line-height : ≈ 0.9** (très serré, ce qui donne le punch).
- **Casse** : UPPERCASE réservé à la display ; le corps reste en casse normale.

## Pile de polices (secours)

```
Display  → var(--brand-font-display) (défaut : Coluna, Impact, Haettenschweiler, Arial Narrow, sans-serif)
            Usage : gros titres / hooks / mots cinématiques (statique).
```

## Tokens (statique)

```json
{
  "fonts": {
    "display": "var(--brand-font-display)"
  },
  "typography": {
    "cover": {
      "family": "display",
      "weight": 700,
      "sizeMin": 90,
      "sizeMax": 150,
      "lineHeight": 0.9,
      "stroke": 6,
      "strokeColor": "#000000",
      "shadow": { "x": 0, "y": 4, "blur": 0, "color": "rgba(0,0,0,0.55)" }
    }
  }
}
```

## Hiérarchie (statique)

| Élément                      | Famille | Graisse | Taille (1080×1350) | Couleur         |
|------------------------------|---------|---------|--------------------|-----------------|
| Hook géant / mot cinématique | display | Bold    | 90–150 px          | Blanc + accent  |
