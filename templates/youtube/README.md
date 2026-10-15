# Gabarit d'une vidéo YouTube (mode YouTube de Monteur IA)

`tools/nouvelle_video_youtube.py` crée chaque vidéo dans `youtube/<nom>/` à partir de ce dossier :

- chaque fichier `X.demo` devient `X` (même chemin, sans le suffixe) : aperçu 1920×1080, panneau
  d'exemple, coupes et mots d'exemple ;
- `tools/` (ici) : les outils propres au 16:9 (sections, visages, master, textes d'appui, contrôle
  de l'export, publication). Ceux dont l'en-tête dit « A CHAQUE VIDEO » appartiennent ensuite à la
  vidéo ; les autres suivent la version de la maison à chaque `npm run sync` ;
- s'y ajoutent les outils du dossier Monteur IA qui ne dépendent pas du format (lieux, style, sons,
  écarts du dérush) et ceux du dérush que la vidéo adapte (coupes, mots) : liste
  `OUTILS_MAISON` de `tools/nouvelle_video_youtube.py` (et `OUTILS_COMMUNS_YOUTUBE` de `scripts/sync.mjs`).

Les règles de montage YouTube vivent dans le skill `youtube` (`.claude/skills/youtube/`), pas ici.

**Maintenance (template uniquement).** Un fichier `.demo` modifié ici change les vidéos créées
ensuite, jamais les vidéos existantes. Un outil générique modifié ici atteint toutes les vidéos au
prochain `npm run sync`. `node --test scripts/sync.test.mjs` vérifie qu'une vidéo créée depuis ce
gabarit est un projet HyperFrames complet, et que les Reels n'en sont pas touchés.
