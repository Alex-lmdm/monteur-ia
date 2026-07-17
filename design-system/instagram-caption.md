# Légende Instagram (caption)

À chaque contenu écrit (Reel ou carrousel), **tu génères aussi la légende Instagram** qui ira sous le
post. Elle est stockée dans le champ `caption` du livrable de publication. Pas de question, c'est
systématique — la légende fait partie du livrable au même titre que le contenu.

Identité et ton viennent de `brand.config.json` (`brand.name`, `brand.handle`, `brand.niche`) ; l'offre
et le funnel (ce vers quoi pointe le CTA) sont **définis par `/setup` (bloc Funnel)**.

<!-- BEGIN GENERATED: cta -->
_La méthode ci-dessous est déjà active : chaque légende est générée dès maintenant, sans configuration._

_Bonus (optionnel) : lance `/setup` (bloc Funnel) pour mémoriser ton offre, ton CTA par défaut et ton
mot-clé — ils seront décrits ici pour que le monteur ne te repose plus la question à chaque post. En
attendant, il déduit le CTA du script (mot-clé s'il y en a un, sinon CTA léger)._
<!-- END GENERATED: cta -->

## Le prompt source

C'est le prompt de rédaction du créateur, **déjà actif et appliqué tel quel** (aucune configuration
requise). `/setup` (bloc Funnel) peut ensuite l'ajuster à ton offre, mais il tourne sans. Les blocs
entre crochets sont les seuls inputs qui changent d'un post à l'autre.

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

## Comment l'appliquer

1. **Contenu du post** : condenser le script dans ta tête — le hook, les insights clés, la chute.
   C'est la matière première, mais **on ne la paraphrase pas**. On l'utilise pour savoir ce qui a déjà
   été dit (et donc ce qu'il faut éviter de répéter).
2. **Mots-clés** : dériver 4–6 mots-clés du sujet + de l'audience (`brand.niche`) ou, à défaut, du
   contenu lui-même. Ils doivent passer dans le texte sans sentir l'incrustation SEO.
3. **Émotion / objectif** : le déduire du type de post. *Informer* pour un post analytique,
   *choquer / interpeller* pour un post news, *inspirer* pour un retour d'expérience, etc.
4. **Appel à l'action** :
   - Si le contenu a un CTA mot-clé (commentaire → DM) → CTA = « commente [MOT-CLÉ] pour recevoir
     [ressource] ». Le mot-clé doit être identique à celui du script.
   - Sinon → CTA léger (enregistre / partage), ou pas de CTA du tout si le post se suffit à lui-même.
5. **Style** : par défaut, la voix de la marque — direct, conversationnel, tutoiement, zéro hedging
   (cf. `writing-anti-slop.md`).

## Règles dures à enforcer

- **Aucun hashtag**. Jamais. Même pas un.
- **CTA commentaire→DM en PREMIÈRE ligne.** Si le post a un CTA « commente [MOT-CLÉ] pour recevoir
  [X] », la **toute première ligne de la légende EST ce CTA** (ex. « Commente REPAS et je t'envoie le
  🔗 de ma liste en DM. ») — le lecteur voit l'offre immédiatement. On enchaîne ENSUITE sur le hook +
  le contenu. (Override la structure « hook en ligne 1 » ci-dessous dès qu'il y a un CTA mot-clé. Pas
  de CTA → on garde le hook en ligne 1.) Le mot « lien » est **interdit** → emoji `cta.linkEmoji`
  (défaut 🔗).
- **Pas d'attaque par « Êtes-vous curieux »** ni équivalent (« Vous saviez que », « Saviez-vous »,
  « Vous êtes-vous déjà demandé »).
- **Une phrase = une ligne**. Saut de ligne après chaque phrase. Aération obligatoire (Instagram
  tronque, l'œil scanne).
- **Pas de répétition du contenu**. Si le script dit déjà X, la légende ne redit pas X — elle ajoute
  une couche : conséquence, anecdote, contre-point, implication, observation personnelle.
- **Emojis** : 2 à 5 sur l'ensemble de la légende. Inline, pas en bullet. Pertinents (un 📊 pour de la
  data, un 🧠 pour une réflexion, etc.). Pas de ✨ par défaut — c'est slop.
- **Longueur** : ~10 lignes. Pas 5, pas 20. Si tu dépasses, coupe.
- **Antislop** : aucun « ce n'est pas X, c'est Y », aucune règle de 3, aucun « voici pourquoi ». Cf.
  `writing-anti-slop.md`.

## Comment rédiger (structure-type, pas obligatoire)

> ⚠️ **Si CTA commentaire→DM** : **ligne 1 = le CTA**, PUIS le hook en ligne 2 et la suite décalée
> d'un cran. Le CTA n'est alors PAS répété en bas. Sinon (pas de CTA mot-clé) la structure ci-dessous
> s'applique telle quelle.

1. **Ligne 1 — hook** : observation surprenante, chiffre, citation, contraste. Doit faire ralentir le
   pouce.
2. **Lignes 2-4 — angle complémentaire** : ce que le script n'a pas dit. Une perspective, une
   implication, un bout d'analyse.
3. **Lignes 5-7 — élargissement** : pourquoi ça compte, pour qui, en quoi c'est inattendu.
4. **Lignes 8-9 — transition vers le CTA** : on referme l'angle et on amène l'action.
5. **Ligne 10 — CTA** : direct. « Commente [MOT-CLÉ] pour recevoir [ressource] en DM. » Pas de
   fioriture.

## Stockage

Dans le livrable de publication, champ `caption` :

```json
{
  "title": "...",
  "caption": "Première ligne hook 🎯\n\nDeuxième ligne...\n\n...\n\nCommente [MOT-CLÉ] pour recevoir [ressource] en DM."
}
```

La caption se lit / s'édite depuis l'onglet **Publication** du studio.
