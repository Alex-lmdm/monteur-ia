# Les CTA (la chute du script)

Choisir **une** formule selon la ressource à partager. Le CTA par défaut du créateur et la liste des
types autorisés viennent de `brand.config.json` → `cta.types` (le **commentaire → DM** est le défaut
le plus fréquent) ; l'outil de DM automatisé vient de `cta.dmTool`. Le type de CTA se choisit **dès
l'étape 2 du workflow** : il conditionne la fin du script.

## a) Commentaire → DM (mot-clé)

Le plus fréquent. Mot-clé déclencheur, traité ensuite par `cta.dmTool` (ex. ManyChat).

- « Commente **[MOT-CLÉ]** et je t'envoie le 🔗. »
- « Si tu veux le 🔗, commente « **[MOT-CLÉ]** » et je te l'envoie directement en DM. »
- « Commente **[MOT-CLÉ]** sous cette vidéo, je t'envoie le 🔗 + [bonus]. »
- « Tu peux écrire **[MOT-CLÉ]** sous cette vidéo et je te l'envoie en DM. »

> **Règle du MOT-CLÉ** : **un seul mot**, court, **en lien direct avec le sujet**, souvent en
> MAJUSCULES. Le mot-clé par défaut est dans `cta.defaultKeyword`. Souvent on ajoute un **bonus**
> pour augmenter la valeur perçue : « + comment le configurer en 30 secondes », « + un guide qui
> détaille tout », « 5 exemples avec le résultat ».

> ⚠️ **Ne jamais écrire le mot « lien »** dans le CTA (risque de shadowban) → utiliser l'emoji défini
> dans `cta.linkEmoji` (par défaut 🔗).

**Le DM et la légende Instagram ne se rédigent PAS à l'étape script.** Ils sont livrés à la **TOUTE
FIN du pipeline** (étape publication), après le montage validé + les SFX/musique. À l'étape script, on
**note juste** le mot-clé. Le moment venu : demander au créateur **le lien réel** (repo, article,
plateforme), ne jamais inventer d'URL, et suivre `design-system/manychat-dm.md` +
`design-system/instagram-caption.md`.

## b) Lien en bio

Pour une plateforme/produit (souvent un partenaire récurrent).

- « Le 🔗 est en bio si tu veux en savoir plus. » / « Le 🔗 de [produit] est en bio. »

## c) Lien en description

Ressource directe à partager sans passer par le DM automatisé (un prompt, un lien).

- « Il suffit de copier ce prompt. Je te le mets en description. »

## d) Screenshot

Quand on partage un artefact directement à l'écran.

- « Je mets [le prompt / la checklist] à l'écran, fais pause, prends une capture d'écran. »
- Combinable : « …ou je peux te l'envoyer en DM si tu commentes "[MOT-CLÉ]". »

## e) Abonnement

Pour finir une vidéo « série de hacks / conseils ».

- « Et si tu veux d'autres [trucs] comme celui-là… abonne-toi. »

## f) Pas de CTA dur

Pour une news / un contenu pur, finir sur du hype, on laisse l'effet.

- « Mais franchement… c'est le début d'un truc énorme. » / « …et c'est assez fou. »
