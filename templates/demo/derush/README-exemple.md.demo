# Contrat `*_cuts.json` (exemple : `exemple_cuts.json`)

- **Ce fichier = la SEULE source des frontières de section.** `data-start` / `data-duration` du master
  (`index.html`) et des sous-comps sont dérivés des `takes[].start` / `.end`, jamais des timestamps Whisper.
- Whisper démarre ~0,1-0,25 s trop tôt : la fenêtre du visage s'ouvrait avant le jump-cut et on voyait
  la fin de la prise précédente. Les `start`/`end` ici sont **mesurés sur la vidéo dérushée livrée**
  (détection scene-change, `tools/cut_boundaries.py`).
- Format : `source`, `duration`, `method`, puis `takes[]` avec `i`, `start`, `end`, `text`.
- Généré à l'étape dérush ; le master est ensuite (re)construit par `tools/build_master.py` à partir d'ici.
- `exemple_cuts.json` est un factice pédagogique (~8 s, 3 prises) : remplace-le par le vrai dérush de ta vidéo.
