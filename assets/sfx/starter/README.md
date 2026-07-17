# assets/sfx/starter — pack de démarrage (livré avec le repo)

Ces sons sont **générés synthétiquement** (ffmpeg, ondes + bruit filtré). Ils sont donc **100 %
originaux et libres de droits** : on peut les versionner dans le repo, contrairement aux SFX de
bibliothèques commerciales. Objectif : que « mets le sound effect » fonctionne **dès le
téléchargement, hors-ligne**, sans aucune configuration.

| Fichier          | À utiliser pour                                             |
| ---------------- | ----------------------------------------------------------- |
| `ui-click.mp3`   | clic souris / bouton / petit tic                            |
| `pop.mp3`        | apparition d'un élément, bulle, petit « boup »              |
| `whoosh.mp3`     | transition, swipe, changement de section                    |
| `riser.mp3`      | montée de tension juste avant un reveal                     |
| `impact.mp3`     | accent grave sur un mot fort / un chiffre qui tombe         |
| `beep.mp3`       | notification, validation, petit signal                      |

C'est un **socle minimal**, pas une bibliothèque complète. Pour élargir (sons plus riches, variantes,
besoins spécifiques), deux voies :

- **Bibliothèque HeyGen** — `npx hyperframes auth`, puis recherche en langage naturel via l'API
  (cf `design-system/sfx-sound-search.md`). Bonus de la formation Monteur IA.
- **Tes propres MP3** — dépose-les à la racine de `assets/sfx/` (ils restent privés, non versionnés).

Régénérer ce pack si besoin : `scripts/gen-starter-sfx.sh`.
