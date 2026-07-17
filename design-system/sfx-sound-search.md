# Effets sonores (SFX) — recherche via l'API audio HeyGen

Comment trouver et ajouter des effets sonores au montage. AJ (créateur de HyperFrames)
a exposé un catalogue SFX via l'API externe HeyGen, recherchable en langage naturel.

## Règle de priorité

1. **Toujours réutiliser d'abord les SFX déjà présents dans `assets/sfx/`** — le **pack de démarrage
   livré** (`assets/sfx/starter/`, ci-dessous) et tout MP3 que le créateur a déposé lui-même à la
   racine du dossier. À privilégier pour tout ce qui est courant.
2. **N'appeler l'API HeyGen que pour un besoin spécial** : un mouvement, une animation, une
   transition à l'écran qui n'a pas de son adéquat en local. Nécessite `npx hyperframes auth` (voir
   plus bas) — si l'auth n'est pas faite, rester sur le pack de démarrage ou demander au créateur de
   déposer son propre MP3.

## Bibliothèque de démarrage livrée (`assets/sfx/starter/`) — réutiliser en priorité

**22 sons réels sous licence CC0** (Freesound + Kenney), versionnés dans le repo donc redistribuables,
disponibles **hors-ligne, sans configuration**.

> **L'index, avec une description « à utiliser quand… » par son, est dans
> [`assets/sfx/starter/sounds.md`](../assets/sfx/starter/sounds.md).** À l'étape SFX, **lire cet index
> et choisir le fichier dont la description colle le mieux au moment à l'écran** (clic → un son de
> clic, transition → un whoosh, reveal → un riser, etc.). On ne pose pas tous les sons : on choisit le
> bon, au bon endroit.

Catégories couvertes : clics (souris, double, UI, select, tick, switch), feedback (confirmation,
error), apparition (pop, drop), whoosh (fast/standard/long), riser (clair/dark), impact (accent/boom),
notification (ding, notification), keyboard, cha-ching.

> Pour un besoin **absent** de la bibliothèque (son très spécifique), passer par l'API HeyGen
> ci-dessous, ou déposer ses propres MP3. Toujours **regarder d'abord dans `sounds.md`**.

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
