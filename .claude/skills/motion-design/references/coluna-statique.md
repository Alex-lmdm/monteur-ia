# Coluna — la police display (STATIQUE UNIQUEMENT)

**Coluna est hors scope du motion.** En vidéo, les gros titres sont portés par
**Poppins Black**. Cette spéc est conservée ici pour les formats **statiques**
(carrousels, visuels, miniatures) où le texte porte tout.

Fichier custom : `brand/fonts/Coluna.otf` (à exporter dans chaque projet qui l'utilise).

## Règles

- **TOUJOURS EN UPPERCASE**. Coluna existe en bold condensé pour frapper.
- Toujours pour hooks / titres / mots impactants. **Jamais pour du texte courant.**
- **Stroke noir pur `#000000`** : 3 px outside (Figma) ou 6 px centered (canvas).
- **Drop shadow légère** : `x=0, y=4, blur=0, color=rgba(0,0,0,0.55)`. Subtil mais décolle
  le texte des fonds chargés.
- Taille typique : **90 à 150 px en 1080×1350**. En vertical 1080×1920, pousser à
  **180-220 px** sur un mot court.
- **Line-height : ≈ 0.9** (très serré, ce qui donne le punch).
- **Casse** : UPPERCASE réservé à Coluna ; le corps reste en casse normale.

## Pile de polices

```
Display  → Coluna, Impact, Haettenschweiler, Arial Narrow, sans-serif
            Usage : gros titres / hooks / mots cinématiques (statique).
```

## Tokens (statique)

```json
{
  "fonts": {
    "display": "Coluna, Impact, Haettenschweiler, Arial Narrow, sans-serif"
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

| Élément                      | Famille | Graisse | Taille (1080×1350) | Couleur       |
|------------------------------|---------|---------|--------------------|---------------|
| Hook géant / mot cinématique | Coluna  | Bold    | 90–150 px          | Blanc + jaune |
