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

Polices des styles de sous-titres (`templates/styles-sous-titres.json`), même provenance
(dépôt github.com/google/fonts), chacune avec son texte de licence dans ce dossier :

| Police | Styles de sous-titres | Copyright | Licence |
|--------|-----------------------|-----------|---------|
| Bangers (ttf) | 5 Bande dessinée | © Vernon Adams | `OFL-Bangers.txt` |
| Bebas Neue (ttf) | 9 Rétro, 15 Bandeau noir | © Dharma Type | `OFL-BebasNeue.txt` |
| Bungee (ttf) | 7 Bloc 3D | © David Jonathan Ross | `OFL-Bungee.txt` |
| DynaPuff (ttf variable) | 4 Bulle rose | © The DynaPuff Project Authors | `OFL-DynaPuff.txt` |
| Gabarito (ttf variable) | 22 Montée douce | © The Gabarito Project Authors | `OFL-Gabarito.txt` |
| Londrina Solid Black (ttf) | 10 Feutre | © Marcelo Magalhães | `OFL-LondrinaSolid.txt` |
| Luckiest Guy (ttf) | 6 Cartoon violet | © Astigmatic | Apache 2.0, `LICENSE-LuckiestGuy.txt` |
| Poetsen One (ttf) | 21 Mot cyan | © Pablo Impallari | `OFL-PoetsenOne.txt` |
| Racing Sans One (ttf) | 8 Course | © Pablo Impallari | `OFL-RacingSansOne.txt` |
| Roboto Condensed (ttf variable) | 31, 37, 60, 63, 83 | © The Roboto Condensed Project Authors | `OFL-RobotoCondensed.txt` |
| Barlow Black (ttf) | 36 Impact orange | © The Barlow Project Authors | `OFL-Barlow.txt` |
| Funnel Sans (ttf variable) | 39 Mot sur vert | © The Funnel Project Authors | `OFL-FunnelSans.txt` |
| Outfit (ttf variable) | 76 Néon vacillant, 81 Minimal turquoise | © The Outfit Project Authors | `OFL-Outfit.txt` |
| Averia Libre Bold (ttf) | 35 Ludique | © Dan Sayers | `OFL-AveriaLibre.txt` |
| Monda (ttf variable) | 79 Professionnel | © The Monda Project Authors | `OFL-Monda.txt` |
| Playfair Display (ttf variable) | 77 Élégant noir | © The Playfair Project Authors | `OFL-PlayfairDisplay.txt` |
| IM Fell English (ttf) | 48 Ancien | © Igino Marini | `OFL-IMFellEnglish.txt` |
| DM Sans Italic (ttf variable) | 69 Italique bleu, 82 Or italique | © The DM Sans Project Authors | `OFL-DMSans.txt` |
| Gochi Hand (ttf) | 68 Manuscrit rouge | © Huerta Tipográfica | `OFL-GochiHand.txt` |
| Rubik (ttf variable) | 41 Pilule noire, 59 Ressort | © The Rubik Project Authors | `OFL-Rubik.txt` |
| Alef Bold (ttf) | 45 Lignes blanches | © Hagilda, Mushon Zer-Aviv | `OFL-Alef.txt` |

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
