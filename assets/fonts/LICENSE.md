# Licences des polices incluses

Les polices de ce dossier sont distribuées sous la **SIL Open Font License 1.1** (OFL),
qui autorise l'usage, la modification et la redistribution, y compris dans un projet
commercial, tant que les polices ne sont pas vendues seules.

| Police | Rôle par défaut | Copyright | Licence |
|--------|-----------------|-----------|---------|
| Inter (woff2) | Texte et labels du motion | © The Inter Project Authors | [OFL 1.1](https://openfontlicense.org/open-font-license-official-text/) |
| Anton (woff2) | Sous-titres / display | © The Anton Project Authors | [OFL 1.1](https://openfontlicense.org/open-font-license-official-text/) |
| Archivo Black (woff2) | Sous-titres / display | © Omnibus-Type | [OFL 1.1](https://openfontlicense.org/open-font-license-official-text/) |

Polices des styles du catalogue (skill `reel-cloneur`, dossier `styles/`), chacune avec son texte
de licence `OFL-<police>.txt` dans ce dossier (SIL OFL 1.1, dépôt github.com/google/fonts) :

| Police | Style du catalogue | Copyright | Licence |
|--------|--------------------|-----------|---------|
| DM Serif Display Italic (ttf) | 01 Top outils | © Colophon Foundry, Adobe | `OFL-DMSerifDisplay.txt` |
| Source Serif 4 Italic (ttf variable) | 03 Liste de conseils | © The Source Serif 4 Project Authors | `OFL-SourceSerif4.txt` |
| Open Sans ExtraBold Italic (ttf) | 06 Démo sur ordinateur | © The Open Sans Project Authors | `OFL-OpenSans.txt` |
| Mr Dafoe (ttf) | 07 Annonce choc | © Alejandro Paul | `OFL-MrDafoe.txt` |
| Poppins Bold (ttf) | 08 Réponse à un abonné, 10 Avis produit | © The Poppins Project Authors | `OFL-Poppins.txt` |
| Fraunces (ttf variable) | 08 Réponse à un abonné | © The Fraunces Project Authors | `OFL-Fraunces.txt` |
| Abril Fatface (ttf) | 09 Collage illustré | © TypeTogether | `OFL-AbrilFatface.txt` |
| Courier Prime (ttf) | 09 Collage illustré | © The Courier Prime Project Authors | `OFL-CourierPrime.txt` |
| Montserrat (ttf variable) | 11 Mon histoire | © The Montserrat.Git Project Authors | `OFL-Montserrat.txt` |
| Newsreader (ttf variable) | 11 Mon histoire | © The Newsreader Project Authors | `OFL-Newsreader.txt` |

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
