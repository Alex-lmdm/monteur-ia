# Licences des polices incluses

Les polices de ce dossier sont distribuées sous la **SIL Open Font License 1.1** (OFL),
qui autorise l'usage, la modification et la redistribution, y compris dans un projet
commercial, tant que les polices ne sont pas vendues seules.

| Police | Rôle par défaut | Copyright | Licence |
|--------|-----------------|-----------|---------|
| Inter (woff2) | Texte et labels du motion | © The Inter Project Authors | [OFL 1.1](https://openfontlicense.org/open-font-license-official-text/) |
| Anton (woff2) | Sous-titres / display | © The Anton Project Authors | [OFL 1.1](https://openfontlicense.org/open-font-license-official-text/) |
| Archivo Black (woff2) | Sous-titres / display | © Omnibus-Type | [OFL 1.1](https://openfontlicense.org/open-font-license-official-text/) |

Texte intégral de la licence : https://openfontlicense.org/open-font-license-official-text/

## Mettre TA police

Ces trois polices sont des **points de départ neutres**, pas une identité. Une police de
sous-titres est ce qui rend un compte reconnaissable en une seconde : prends la tienne.

1. Dépose tes fichiers (`.woff2` de préférence, `.ttf` accepté) dans ce dossier.
2. Déclare-les dans la table `fonts` de `templates/style-presets.json`.
3. Renseigne `visual.fontCaptions` / `fontBody` / `fontDisplay` dans `brand.config.json`.
4. `npm run sync` régénère `brand/fonts.css` et `brand/tokens.css`.

Ou plus simplement : `/setup visuel`, qui fait les 4 étapes pour toi.

⚠️ Vérifie que tu as le droit d'embarquer la police dans ton projet : les polices achetées
ont souvent une licence web séparée de la licence bureau.
