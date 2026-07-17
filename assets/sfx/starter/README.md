# assets/sfx/starter — pack de démarrage (livré avec le repo)

7 effets sonores **réels**, tous sous licence **CC0 (domaine public)** — donc **redistribuables** :
on peut les versionner dans le repo et les livrer avec le produit. Objectif : que « mets le sound
effect » fonctionne **dès le téléchargement, hors-ligne**, sans aucune configuration. Les fichiers ont
été rognés et normalisés (niveau homogène) ; le montage rééquilibre ensuite chaque son par niveau
perçu.

| Fichier          | À utiliser pour                                             |
| ---------------- | ----------------------------------------------------------- |
| `ui-click.mp3`   | clic souris / bouton / petit tic                            |
| `keyboard.mp3`   | un texte qui se tape (mot-clé du CTA, saisie…)              |
| `pop.mp3`        | apparition d'un élément, bulle, petit « plop »              |
| `whoosh.mp3`     | transition, swipe, changement de section                    |
| `riser.mp3`      | montée de tension juste avant un reveal                     |
| `impact.mp3`     | accent grave sur un mot fort / un chiffre qui tombe         |
| `beep.mp3`       | notification, validation, petit signal (ding)               |

## Provenance & licence

Sons issus de [Freesound](https://freesound.org), filtrés sur licence **CC0 1.0 Universal** (aucune
attribution requise ; l'attribution ci-dessous est de la simple traçabilité) :

| Fichier      | Source Freesound                        | Licence |
| ------------ | --------------------------------------- | ------- |
| `ui-click`   | https://freesound.org/s/634112/ (« dh mouse click »)        | CC0 |
| `keyboard`   | https://freesound.org/s/422712/ (« typing on keyboard »)    | CC0 |
| `pop`        | https://freesound.org/s/447910/ (« Plop! »)                 | CC0 |
| `whoosh`     | https://freesound.org/s/400372/ (« FastWhoosh »)            | CC0 |
| `riser`      | https://freesound.org/s/680514/ (« Synth+White Noise Riser ») | CC0 |
| `impact`     | https://freesound.org/s/369711/ (« Hit Impact »)            | CC0 |
| `beep`       | https://freesound.org/s/571513/ (« Soft-Notifications Bell Ding-Dong ») | CC0 |

## Pour élargir

Ce pack est un **socle minimal**. Pour des sons plus riches ou spécifiques :

- **Bibliothèque HeyGen** — `npx hyperframes auth`, puis recherche en langage naturel via l'API
  (cf `design-system/sfx-sound-search.md`). Bonus de la formation Monteur IA.
- **Tes propres MP3** — dépose-les à la racine de `assets/sfx/` (ils restent privés, non versionnés).
  ⚠️ N'y mets que des sons que tu as le droit d'utiliser ; s'ils doivent être **redistribués** avec le
  repo, il faut du CC0.
