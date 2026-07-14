# Effets sonores (SFX) — recherche via l'API audio HeyGen

Comment trouver et ajouter des effets sonores au montage. AJ (créateur de HyperFrames)
a exposé un catalogue SFX via l'API externe HeyGen, recherchable en langage naturel.

## Règle de priorité

1. **Toujours réutiliser d'abord les SFX déjà présents dans `assets/sfx/`** (la bibliothèque du
   créateur, recopiée de projet en projet). Ce sont les sons « maison », à privilégier pour tout ce
   qui est courant.
2. **N'appeler l'API HeyGen que pour un besoin spécial** : un mouvement, une animation, un clic,
   une transition à l'écran qui n'a pas de son adéquat en local.

## SFX déjà disponibles en local (réutiliser en priorité)

| Fichier (`assets/sfx/`)                         | À utiliser pour                                  |
| ----------------------------------------------- | ------------------------------------------------ |
| `mouse single click 2.MP3`                      | clic souris                                      |
| `Ballpoint pen click.MP3`                       | clic de stylo / petit tic                        |
| `PC typing keyboard kacha.MP3`                  | frappe clavier / on tape une commande            |
| `felt pen.MP3`                                  | trait de feutre (soulignement, dessin, surlignage) |
| `Riser.MP3`                                     | montée de tension avant un reveal / transition   |
| `camera shutter sound.MP3`                      | déclencheur photo / capture / screenshot         |
| `Click (camera shutter sound single shot).MP3` | screenshot « net », one-shot                     |
| `camera shutter sound analog.MP3`              | variante shutter, plus analogique                |
| `camera shutter sound kashashka.MP3`           | variante shutter, plus marquée                   |

## L'endpoint

```
GET https://api.heygen.com/v3/audio/sounds
```

Auth : header `x-api-key: <clé HeyGen>` (ou `Authorization: Bearer <token>`).
→ Obtenir la clé via `hyperframes auth` (connexion compte HeyGen) ou le dashboard HeyGen.
**Aucune clé n'est encore configurée localement** (à fournir avant utilisation).

Paramètres :

| Param       | Requis | Détail                                                                       |
| ----------- | ------ | ---------------------------------------------------------------------------- |
| `query`     | ✅     | Description en langage naturel, **en anglais** (catalogue indexé en anglais) |
| `type`      | —      | `music` (défaut !) ou `sound_effects` → **TOUJOURS mettre `sound_effects`** pour des SFX |
| `limit`     | —      | 1–50, défaut 10                                                              |
| `min_score` | —      | 0–1, défaut 0.7 (baisser à ~0.5–0.6 si trop peu de résultats)               |
| `token`     | —      | curseur de pagination (`next_token` de la réponse précédente)               |

Réponse : `data[]` avec `id`, `name`, `description`, `audio_url` (pré-signée, **temporaire**),
`duration`, `score`, `type`. Plus `has_more` / `next_token`.

## Recette

Recherche (en anglais, type sound_effects) :

```bash
curl -s -H "x-api-key: $HEYGEN_API_KEY" \
  "https://api.heygen.com/v3/audio/sounds?type=sound_effects&query=whoosh%20for%20a%20scene%20change&limit=5&min_score=0.6" \
  | python3 -m json.tool
```

Télécharger le son choisi **immédiatement** (l'URL expire) dans `assets/sfx/` :

```bash
curl -L -o "assets/sfx/whoosh scene change.mp3" "<audio_url>"
```

## Workflow SFX au montage

1. Repérer les moments qui méritent un son : clic, apparition, swipe, pop, transition, riser,
   « cha-ching », erreur/succès, frappe clavier, screenshot…
2. Pour chaque moment : chercher d'abord dans `assets/sfx/`. Si rien d'adéquat → requête API
   (en anglais), prendre le meilleur `score`, télécharger dans `assets/sfx/` avec un nom descriptif.
3. Câbler dans la composition : un `<audio>` dédié, en `clip`, `data-start` aligné **exactement**
   sur l'événement visuel. Suivre le skill `hyperframes` pour le timing/registration.
4. Volume des SFX en dessous de la voix ; ne pas les empiler.

## Pièges

- ⚠️ `type` par défaut = `music` → ne **jamais** oublier `type=sound_effects` pour des SFX.
- ⚠️ `audio_url` est pré-signée et expire → télécharger tout de suite, ne pas mettre l'URL en cache.
- Requêtes en **anglais** = bien meilleurs résultats.
