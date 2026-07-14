# Message DM (automation de commentaire → DM)

Quand le contenu a un CTA mot-clé (l'audience doit commenter un mot-clé pour recevoir une ressource),
**tu écris aussi le message DM** que le créateur collera dans son automation (`brand.config.json` →
`cta.dmTool`, ex. ManyChat). Il est stocké dans le champ `dmMessage` du livrable de publication.

Pas de DM à générer si le CTA n'est pas un mot-clé (chute hype, lien en bio, screenshot…) — le champ
reste absent du JSON.

Le mot « lien » est **interdit** partout : utiliser l'emoji `cta.linkEmoji` (défaut 🔗). C'est la
signature visuelle du message.

<!-- BEGIN GENERATED: cta -->
_Section vide — lance `/setup` (bloc Funnel) : ton outil de DM, ton ouverture type et la ressource
que tu livres seront décrits ici._
<!-- END GENERATED: cta -->

## Voix et structure

### Ouverture

Trois ouvertures possibles, par ordre de fréquence :

1. `Hello 👋` — défaut. C'est l'ouverture qu'on prend si rien ne justifie un autre choix.
2. `Hey !` — quand on évoque un ton plus rapide, plus direct, ou un partage « entre potes »
   (typiquement une ressource courte).
3. Pas d'ouverture, on attaque direct par `Voici le 🔗 comme promis : URL` — uniquement quand l'URL
   est l'élément principal et que tout le reste est du contexte court.

### Livraison

C'est la colonne vertébrale du DM. Pattern quasi systématique :

```
Voici le 🔗 [du / de la / avec / pour / comme promis] [ressource]
```

Variantes (exemples fictifs, multi-niches) :
- « Voici le 🔗 de ma liste de courses pour les 5 repas »
- « Voici le 🔗 comme promis : https://… »
- « Voilà tout ce qu'il te faut pour le programme 👇 » → « Le 🔗 de la séance : … »
- « Voici le 🔗 du template qui gère ton budget »
- « Voici le 🔗 pour accéder au guide où je t'explique en détail… »

### Contexte (1-4 paragraphes, optionnel)

Si la ressource a besoin d'être située, on ajoute 1 à 4 paragraphes très courts. Objectifs :

- **Expliquer ce qu'il y a dedans** (« 12 recettes triées par temps de préparation »).
- **Donner du contexte personnel** (« ça fait des mois que j'affine ce système »).
- **Cadrer l'usage** (« imprime-la et colle-la sur le frigo »).

Règles :
- Phrases courtes. Une idée par paragraphe.
- Aération maximale : ligne vide entre chaque paragraphe.
- Tutoiement systématique.
- Pas de superlatif gratuit (« incroyable », « hallucinant »). On reste factuel et chaleureux.

### Mode d'emploi (optionnel)

Si la ressource nécessite un setup (compte, étapes, réglage) :

- Numéroter avec `1️⃣ 2️⃣ 3️⃣ 4️⃣`.
- Une étape = une ligne courte.
- Ajouter un `⚠️ Important : …` quand il y a un piège à éviter.
- Ajouter un `👨‍💻 Pour les plus avancés : …` quand on tease une version avancée.

### Cross-promo soft (optionnel)

Pour orienter vers une ressource complémentaire :

```
Je te mets aussi le 🔗 de [ressource complémentaire] si tu veux aller plus loin.
```

Une seule cross-promo max. Elle doit sentir l'extra généreux, pas la vente.

### Fermeture

**Pas de signature**. Pas de « Bisous », pas de « Belle journée », pas de « N'hésite pas si tu as des
questions ». On termine sur la valeur livrée, point.

## Anti-patterns (ce qu'on n'écrit jamais)

- ❌ Hashtags
- ❌ Le mot « lien » (→ 🔗)
- ❌ « J'espère que ça te plaira »
- ❌ « Merci de m'avoir contacté » / « Merci pour ton commentaire »
- ❌ Paragraphes longs et denses
- ❌ Ton commercial (« profite-en », « offre limitée »)
- ❌ Plus de 2 emojis par paragraphe
- ❌ Vous au lieu de tu
- ❌ Phrases qui paraphrasent le contenu (le DM délivre, il ne récapitule pas)

## Longueur

- **Court (3-5 lignes)** : la ressource parle d'elle-même, l'URL suffit presque.
- **Moyen (6-10 lignes)** : ressource avec contexte.
- **Long (15-25 lignes)** : ressource avec setup ou tutoriel (avec ses étapes numérotées).

Adapter à la complexité de la ressource, jamais à la longueur du contenu.

## URL

- Si l'URL définitive est connue (donnée par le créateur), on l'écrit directement.
- Sinon, placeholder `[LIEN À COMPLÉTER]` à remplacer par le créateur avant de coller dans l'outil de
  DM. Toujours préfixé par 🔗 dans le texte. **Ne jamais inventer d'URL.**

## Squelette type

```
Hello 👋

Voici le 🔗 [du / de la / avec / pour] [ressource] : [URL ou placeholder]

[1-2 phrases qui situent ce qu'il y a dedans et à qui ça sert.]

[Optionnel : setup, instructions, ou tip d'usage.]

[Optionnel : cross-promo soft d'une seule ressource complémentaire.]
```

## Stockage

Dans le livrable de publication, champ `dmMessage`, **uniquement** si le CTA est un mot-clé :

```json
{
  "title": "...",
  "caption": "...",
  "dmMessage": "Hello 👋\n\nVoici le 🔗 du guide complet sur…\n\n…"
}
```

Le DM se lit / s'édite depuis l'onglet **Publication** du studio, sous la caption.
