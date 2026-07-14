# Légende Instagram (caption)

À chaque carrousel écrit, **tu génères aussi la légende Instagram** qui ira
sous le post. Elle est stockée dans le champ racine `caption` du
`carousel.json`. Pas de PR, pas de question, c'est systématique — la légende
fait partie du livrable au même titre que les slides.

## Le prompt source

C'est la version d'Alex, à appliquer telle quelle. Les blocs entre crochets
sont les seuls inputs qui changent d'un carrousel à l'autre.

```text
Role: Rédacteur expert en descriptions Instagram engageantes, spécialisé en
stratégie de visibilité organique

Instructions:
- Analyse le contenu fourni par l'utilisateur. Il s'agit soit du script complet
  d'un carousel Instagram, soit du script d'un réel.
- Rédige une description d'environ 10 lignes pour accompagner ce contenu sur
  Instagram.
- Commence par une accroche captivante, qui intrigue et donne envie de lire
  jusqu'à la fin.
- Ne répète pas ce qui est déjà dit dans le contenu du post. Apporte plutôt
  des informations complémentaires, des réflexions, une autre perspective ou
  des détails qui enrichissent la publication.
- N'ajoute aucun hashtag.
- Donne du rythme à la lecture en alternant des phrases courtes et des phrases
  un peu plus longues. Évite les phrases trop longues ou trop complexes.
- Chaque ligne doit donner envie de lire la suivante.
- Utilise un ton naturel, humain, et en accord avec le style défini par
  l'utilisateur.
- Intègre les mots clés fournis dans la description de façon fluide et
  naturelle pour améliorer le référencement.
- Si un appel à l'action est précisé, termine la description en l'intégrant de
  façon cohérente avec le reste du texte.

Contraintes:
- Longueur : environ 10 lignes
- Aucun hashtag
- Ne pas paraphraser le contenu du post, mais plutôt l'enrichir
- Ton naturel et fluide
- Rythme dynamique (variété dans la longueur des phrases)
- Formate chaque nouvelle phrase avec une nouvelle ligne pour que le texte
  soit plus lisible.
- Inclue des emojis.
- La première phrase de la légende doit accrocher les lecteurs (éveiller leur
  curiosité), et ne commence pas la phrase par « Êtes-vous curieux ? »
- Intégration fluide des mots clés
- Style, émotion, et appel à l'action personnalisables

Inputs:
- Contenu du post : [script du carousel / réel]
- Mots-clés à ajouter : [liste]
- Émotion principale ou objectif du post : [inspirer, choquer, informer, vendre, rassurer…]
- Appel à l'action souhaité (facultatif) : [commenter, enregistrer, partager, visiter un lien…]
- Style souhaité (facultatif) : [professionnel, familier, storytelling, provocateur, éducatif…]
```

## Comment je l'applique

1. **Contenu du post** : je condense le carrousel dans ma tête — le hook de
   couverture, le slide 2, les insights clés, le dernier slide. C'est ma
   matière première, mais **je ne la paraphrase pas**. Je l'utilise pour
   savoir ce qui a déjà été dit (et donc ce que je dois éviter de répéter).
2. **Mots-clés** : je dérive 4–6 mots-clés du `brief` (sujet + audience) ou,
   à défaut, du contenu lui-même. Ils doivent passer dans le texte sans
   sentir l'incrustation SEO.
3. **Émotion / objectif** : je le déduis du brief (`tone`) et du type de
   post. *Informer* pour un post analytique, *choquer / interpeller* pour un
   post news, *inspirer* pour un retour d'expérience, etc.
4. **Appel à l'action** :
   - Si le dernier slide est un `dmCta` → CTA = « commente [MOT-CLÉ] pour
     recevoir [ressource] ». Le mot-clé doit être identique à celui du slide.
   - Si le dernier slide est un `thanks` → CTA léger (enregistre / partage),
     ou pas de CTA du tout si le post se suffit à lui-même.
   - Si c'est un `cta` legacy → suit la logique du slide.
5. **Style** : par défaut, voix LMDM — direct, conversationnel, tutoiement,
   zéro hedging (cf. [[writing-anti-slop]]).

## Règles dures que j'enforce

- **Aucun hashtag**. Jamais. Même pas un.
- **CTA commentaire→DM en PREMIÈRE ligne (validé Alex 2026-06-25).** Si le post a un CTA
  « commente [MOT-CLÉ] pour recevoir [X] », la **toute première ligne de la légende EST ce CTA**
  (ex. « Commente SKILL et je t'envoie le 🔗 du repo en DM. ») — le lecteur voit l'offre
  immédiatement. On enchaîne ENSUITE sur le hook + le contenu. (Override la structure « hook en
  ligne 1 » ci-dessous dès qu'il y a un CTA mot-clé. Pas de CTA → on garde le hook en ligne 1.)
- **Pas d'attaque par « Êtes-vous curieux »** ni équivalent (« Vous saviez
  que », « Saviez-vous », « Vous êtes-vous déjà demandé »).
- **Une phrase = une ligne**. Saut de ligne après chaque phrase. Aération
  obligatoire (Instagram tronque, l'œil scanne).
- **Pas de répétition du carrousel**. Si le slide 4 dit déjà X, la légende
  ne redit pas X — elle ajoute une couche : conséquence, anecdote, contre-
  point, implication business, observation personnelle.
- **Emojis** : 2 à 5 sur l'ensemble de la légende. Inline, pas en bullet.
  Pertinents (un 📊 pour de la data, un 🧠 pour une réflexion, etc.). Pas de
  ✨ par défaut — c'est slop.
- **Longueur** : ~10 lignes. Pas 5, pas 20. Si je dépasse, je coupe.
- **Antislop** : aucun « ce n'est pas X, c'est Y », aucune règle de 3,
  aucun « voici pourquoi ». Cf. [[writing-anti-slop]].

## Comment je rédige (structure-type, pas obligatoire)

> ⚠️ **Si CTA commentaire→DM** : **ligne 1 = le CTA**, PUIS le hook en ligne 2 et la suite décalée
> d'un cran. Le CTA n'est alors PAS répété en bas. Sinon (pas de CTA mot-clé) la structure
> ci-dessous s'applique telle quelle.

1. **Ligne 1 — hook** : observation surprenante, chiffre, citation, contraste.
   Doit faire ralentir le pouce.
2. **Lignes 2-4 — angle complémentaire** : ce que le carrousel n'a pas dit.
   Une perspective, une implication, un bout d'analyse.
3. **Lignes 5-7 — élargissement** : pourquoi ça compte, pour qui, en quoi
   c'est inattendu.
4. **Lignes 8-9 — transition vers le CTA** : on referme l'angle et on amène
   l'action.
5. **Ligne 10 — CTA** : direct. « Commente RAPPORT pour recevoir le rapport
   complet en DM. » Pas de fioriture.

## Stockage

Dans `carousel.json`, champ racine :

```json
{
  "title": "...",
  "slides": [...],
  "caption": "Première ligne hook 🎯\n\nDeuxième ligne...\n\n...\n\nCommente RAPPORT pour recevoir le rapport en DM."
}
```

La caption se lit / s'édite depuis l'onglet **Publication** du studio.
