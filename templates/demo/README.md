# Copie de référence du plan de travail livré

Chaque fichier `X.demo` ici est la version **livrée** du fichier `X` du projet (même chemin,
suffixe `.demo` en plus). `tools/close_reel.py` les recopie à leur place après avoir purgé le
reel publié : le projet revient exactement à l'état d'un ZIP neuf (démo de 8 s, placeholder
`base.mp4`, outils pointés sur `derush/exemple_cuts.json`), sans toucher aux réglages du client.

Le suffixe `.demo` empêche le studio HyperFrames de lister ces fichiers comme des compositions
ou des médias du projet.

**Maintenance (template uniquement).** Si tu modifies dans le template un fichier qui a sa copie
ici, recopie-le : `cp tools/sections.py templates/demo/tools/sections.py.demo`.
`node --test scripts/sync.test.mjs` échoue tant qu'une copie diffère de l'original, et quand
un fichier du plan de travail (outil marqué « A CHAQUE REEL », `compositions/`, `derush/`,
`assets/video/`) n'a pas de copie.
