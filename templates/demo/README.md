# Gabarit d'un nouveau Reel

`tools/nouveau_reel.py` crée chaque Reel dans `reels/<nom>/` à partir de ce dossier : chaque
fichier `X.demo` devient `X` (même chemin, sans le suffixe), puis les outils de `tools/` sont
copiés à côté et `npm run sync` ajoute le style, les polices, GSAP et les instructions.

Le Reel neuf est donc le plan de travail de départ : démo de 8 s, placeholder `base.mp4`, coupes
d'exemple (`derush/exemple_cuts.json`, lu par `tools/sections.py`), sans aucun réglage du client.

Le suffixe `.demo` empêche le studio HyperFrames de lister ces fichiers comme des compositions ou
des médias, et la racine du dossier Monteur IA de passer pour un projet.

**Maintenance (template uniquement).** Un fichier modifié ici change tous les Reels créés
ensuite, jamais les Reels existants. `node --test scripts/sync.test.mjs` vérifie qu'un Reel créé
depuis ce gabarit est un projet HyperFrames complet.
