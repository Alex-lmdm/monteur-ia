# Publication d'une vidéo YouTube

Après l'export finalisé (`✅ Prête à téléverser`), jamais avant. Tout se rassemble dans
`publication.md` du dossier de la vidéo, que le client copie dans YouTube Studio.

```bash
python3 tools/publication.py   # chapitres horodatés (depuis sections.py) écrits dans publication.md
```

## 1. Titre (3 propositions)

- Moins de 60 caractères (au-delà, YouTube le coupe sur mobile), la promesse en premier.
- Il dit ce que le hook tient dans les 30 premières secondes : pas de promesse que la vidéo ne tient
  pas (le spectateur part, YouTube le voit).
- Trois angles : le résultat (« Monter une vidéo YouTube en 10 minutes avec Claude »), la curiosité
  (« L'outil que les monteurs ne veulent pas que tu connaisses »), le chiffre (« 3 réglages qui ont
  doublé mes vues »). Pas de majuscules partout, pas de tiret long, pas d'emoji obligatoire.
- Le texte de la **miniature** se propose avec (2 à 4 mots, différents du titre) : la miniature
  elle-même n'est pas faite ici.

## 2. Description

- **Les deux premières lignes** : ce qui s'affiche sans cliquer. La promesse reformulée, puis la
  ressource principale (« Le lien de l'outil : … »). Les liens réels se demandent au client, jamais
  inventés.
- Un court paragraphe sur le contenu, avec les mots que les gens tapent (sans en empiler).
- Le bloc **Chapitres** écrit par `tools/publication.py` (00:00 en premier, au moins 3, chacun
  d'au moins 10 s : sinon YouTube ne les affiche pas). Titres de chapitres courts et parlants.
- Les liens secondaires (réseaux, autres vidéos), puis rien d'autre : pas de pavé de hashtags
  (3 au plus, à la fin, s'il y tient).

## 3. Sous-titres

`exports/sous-titres.srt` (écrit par `tools/build_emphases.py`) : YouTube Studio > la vidéo >
Sous-titres > Ajouter une langue > Importer un fichier > « avec synchronisation ». Le spectateur les
active s'il veut ; ils améliorent le référencement. Les relire avant : un nom propre mal transcrit
(« Monteria » pour « Monteur IA ») se corrige dans `derush/<cut>_words.json` (le champ `w`, sans
toucher aux temps), puis `python3 tools/build_emphases.py --srt`. Pas dans le `.srt` lui-même :
`build_emphases.py` le réécrit à chaque passage.

## 4. Écran de fin

Dans YouTube Studio > Écran de fin : une vidéo à regarder ensuite et le bouton S'abonner, sur les
5 à 20 dernières secondes. La vidéo a été montée pour : rien d'important à l'image sous ces
éléments à la fin.

## 5. Après la mise en ligne

Le client dit « c'est en ligne » : `python3 tools/ranger.py` (vidéo finale, SRT et fiche copiés
dans `Vidéos/youtube-publiees/<nom>/`, vidéo marquée publiée ; `--alleger` libère aussi la place
des rushes). Le dossier reste dans l'app, rouvrable pour une version 2.
