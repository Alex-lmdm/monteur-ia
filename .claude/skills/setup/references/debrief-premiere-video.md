# Débrief de la première vidéo : apprendre le style du client

Quand : la première vidéo vient d'être montée d'une traite avec les réglages de base et livrée
(fichier agent, section 🟢, étape 4). Le client ne sait pas décrire son style à froid ; devant sa
propre vidéo, il sait dire ce qu'il aime. Ce débrief remplace le questionnaire : on corrige cette
vidéo avec ses retours, puis on retient tout pour les suivantes.

Mêmes règles que le reste du setup : zéro jargon, rien d'écrit sans OK explicite, écritures dans
`brand.config.json` puis `npm run sync`. Le débrief ne coche aucun bloc dans
`setup.completedBlocks` : les blocs complets restent disponibles via `/setup`.

---

## 1. Livrer et ouvrir le débrief (un seul message)

Adapter les exemples à ce qui a réellement été monté, garder la structure :

> « Ta vidéo est prête, elle est dans tes Téléchargements. C'est une version de base : je l'ai
> montée avec des réglages standard, sans rien savoir de tes goûts.
>
> Maintenant, apprends-moi ton style. Regarde-la et dis-moi tout ce que tu aurais fait autrement.
> Tout se règle :
> - **Les coupes** : plus serrées, plus aérées, un passage à couper ou à garder.
> - **Le son** : je peux rendre ta voix plus propre (deux gestes de ton côté), ajouter ta
>   musique, mettre plus ou moins de bruitages.
> - **L'image** : ton visage en bas et les animations en haut comme ici, ton visage en plein
>   écran, ou un mélange des deux.
> - **Les animations** : des schémas comme ici, de vraies images ou vidéos d'illustration,
>   des captures d'écran, des animations par-dessus ton visage, plus, moins, ou pas du tout.
> - **Les sous-titres** : police, couleur, taille, position, une ou deux lignes, style du bandeau.
> - **Les couleurs** : garder le noir et blanc, ou mettre les tiennes.
>
> Réponds comme tu veux, en vrac ou en vocal. « Rien à changer » est aussi une réponse.
> Je corrige cette vidéo avec tes retours, puis je retiens tout pour les prochaines. »

## 2. Écouter, traduire, clarifier

- Accepter les retours vagues et les traduire en changements concrets. Au plus **une question de
  précision par point ambigu**, toutes regroupées dans un seul message. « Je ne sais pas » sur un
  point = on garde le réglage de base, sans insister.
- Couleurs ou police données → appliquer les règles du bloc D (`questions.md`, D2 à D10 :
  hex valides, jamais `#000000`, polices livrées ou fichiers fournis). « Je veux de la couleur mais
  je ne sais pas laquelle » → présenter les 5 styles comme en D1.
- Ne jamais recopier une critique telle quelle : en tirer ce que le client **veut**.
- **Chiffrer les retours vagues** (« un peu plus gros », « moins de bruitages ») : appliquer une
  valeur concrète à la correction, la lui montrer, et c'est cette valeur validée qu'on retiendra.

| Il dit… | Ce que ça veut dire |
|---|---|
| « C'est trop haché » | coupes plus aérées : allonger un peu les fins de prise (jamais les débuts) |
| « Ça traîne » | coupes plus serrées, ou un passage à retirer : lui demander lequel s'il n'est pas évident |
| « Je préfère me voir en grand » | visage plein écran par défaut, animations en surimpression |
| « Les schémas, c'est pas mon truc » | B-roll ou captures d'écran à la place, ou moins d'animations |
| « Les sous-titres sont trop petits » | taille des sous-titres augmentée (50 px par défaut ; « un peu » ≈ 58–60 px) |
| « Moi en grand au début, après comme ça » | accroche en visage plein écran, le reste en split |
| « Le son est bizarre » | proposer le nettoyage de la voix (section 3) |

## 3. Corriger cette vidéo

C'est la review (étape 5) : appliquer les retours avec le skill `motion-design`, puis ré-exporter
toute la chaîne comme au montage (calque si le motion a changé, `tools/build_final.py`, puis
`tools/build_sfx.py`, qui repose les bruitages sur le nouvel export). Livrer la nouvelle version et
boucler jusqu'à ce qu'il soit content. Mêmes contrôles automatiques qu'au montage.

**Nettoyage de la voix demandé** : suivre le skill `derush`, étape 7 (Adobe Podcast Enhance) sur
`derush/<cut>.mp4`, puis remplacer seulement l'audio, la vidéo et les coupes ne bougent pas.
Vérifier que les durées concordent (écart < 0,1 s), puis :
```bash
ffmpeg -y -i derush/<cut>.mp4 -i derush/<cut>_voice_enhanced.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest derush/<cut>_enhanced.mp4
ffmpeg -y -i assets/video/base.mp4 -i derush/<cut>_voice_enhanced.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest work/base_voix.mp4
```
Remplacer `assets/video/base.mp4` par `work/base_voix.mp4`, puis relancer `tools/build_final.py` et
`tools/build_sfx.py` (le calque ne change pas).

## 4. Résumer ce qu'on retient, attendre l'OK, enregistrer

> « Voilà ce que je retiens pour tes prochaines vidéos :
> - [chaque préférence en français courant]
>
> On garde tout ça ? »

Rien n'est écrit avant un OK clair. Ensuite :

| Retour | Où l'enregistrer |
|---|---|
| Couleurs, polices, sous-titres (skin, lignes, position) | `visual.*` selon le bloc D, puis `setup.styleChosen = true` |
| « Je garde le noir et blanc » | `visual.stylePreset = "neutral"`, `setup.styleChosen = true` |
| Visage plein écran ou split par défaut | `montage.defaultLayout` (`"faceplein"` ou `"split"`) |
| Un mélange (ex. accroche en plein écran, le reste en split) | `montage.defaultLayout` = le cadrage majoritaire, et le mélange en préférence |
| Cadrage du visage recalé pendant la correction | `montage.splitTransform` ou `montage.fullFaceTransform` / `fullFaceOrigin` (réglage technique : l'écrire dès qu'il est validé à l'image) |
| Taille des sous-titres | `visual.captionsSize` (en px, la valeur validée à la correction) |
| Sa musique | fichier dans `assets/music/`, `audio.musicFile` (et `audio.musicDb` s'il la veut plus ou moins forte) |
| Rythme des coupes | les valeurs `derush.padStart` / `padEnd` réellement appliquées et validées à la correction |
| Voix nettoyée | rien : dès la deuxième vidéo, le nettoyage fait partie du dérush |
| Animations (type, quantité, position), B-roll, bruitages, tout le reste | `montage.preferences` |
| « Le reste c'est bon », ou un point dont il ne parle pas (musique, voix, coupes…) | rien : les réglages de base restent. Sans musique, `tools/build_sfx.py` mixe les bruitages seuls. |

**Écrire une préférence** (`montage.preferences`, une chaîne par préférence) :
- une ligne, concrète, applicable sans connaître cette conversation :
  « Pas d'animation par-dessus le visage », « B-roll réel plutôt qu'un schéma quand il cite un
  objet ou un lieu », « Bruitages discrets, seulement sur les apparitions importantes » ;
- ce que le client veut, pas ce qu'il a critiqué, avec la valeur validée quand il y en a une
  (« Bruitages sobres : 4 à 6 par vidéo, sur les moments forts ») ;
- pas de doublon ni de contradiction : une nouvelle préférence remplace l'ancienne sur le même
  sujet. Au-delà d'une douzaine, fusionner.

Puis passer `setup.firstVideoDone` à `true` et lancer `npm run sync` : les préférences
sont recopiées dans `CLAUDE.md` / `AGENTS.md`, relus à chaque conversation. Confirmer :
« C'est enregistré. Ta prochaine vidéo sera montée comme ça directement, et tu pourras toujours
me dire de changer quelque chose. »

**« Rien à changer »** : même résumé (« je garde ce style tel quel »), puis après OK
`visual.stylePreset = "neutral"` si aucun style n'était choisi, `setup.styleChosen = true`,
`setup.firstVideoDone = true`, sync.

**Il veut débriefer plus tard** : ne rien enregistrer et laisser `firstVideoDone` à `false` ;
noter « débrief à faire » dans `work/premiere-video.md` et le reproposer une fois à la
conversation suivante.

## 5. Ensuite

Proposer la légende (étape 7 du pipeline). Mentionner une seule fois, sans insister, que l'IA peut
aussi écrire ses scripts avec sa façon de parler : « dis-moi "on fait ma voix" quand tu veux »
(bloc B).
