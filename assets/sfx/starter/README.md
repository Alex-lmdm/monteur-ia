# assets/sfx/starter — bibliothèque de démarrage (livrée avec le repo)

**22 effets sonores réels, tous sous licence CC0 (domaine public)** — donc redistribuables : versionnés
dans le repo, « mets le sound effect » fonctionne **dès le téléchargement, hors-ligne**, sans aucune
configuration. Sons rognés et normalisés à un niveau homogène ; le montage rééquilibre ensuite chaque
son par niveau perçu.

👉 **L'index complet, avec une description « à utiliser quand… » par son, est dans
[`sounds.md`](./sounds.md)** — c'est ce que l'IA lit à l'étape SFX pour choisir le bon son au bon
moment. Provenance (Freesound + Kenney) et licences y sont aussi listées.

Catégories : **clics** (souris, double, UI, select, tick, switch) · **feedback** (confirmation, error)
· **apparition** (pop, pop-mouth, drop) · **whoosh** (fast, standard, long) · **riser** (clair, dark) ·
**impact** (accent, boom) · **notification** (ding, notification) · **divers** (keyboard, cha-ching).

## Pour élargir

- **Bibliothèque HeyGen** — `npx hyperframes auth`, puis recherche en langage naturel via l'API
  (cf `design-system/sfx-sound-search.md`). Bonus de la formation Monteur IA.
- **Tes propres MP3** — dépose-les à la racine de `assets/sfx/` (privés, non versionnés).
  ⚠️ Pour redistribuer un son avec le repo, il faut du **CC0**.
