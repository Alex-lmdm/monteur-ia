# Message ManyChat (DM)

Quand le dernier slide du carrousel est un `dmCta` (l'audience doit commenter
un mot-clé pour recevoir une ressource), **tu écris aussi le message DM
ManyChat** que Alex collera dans son automation. Il est stocké dans le champ
racine `dmMessage` du `carousel.json`.

Pas de DM à générer si le dernier slide est `thanks` ou `cta` legacy — le
champ reste absent du JSON.

## Voix et structure (dérivées des messages réels d'Alex)

### Ouverture

Trois ouvertures possibles, par ordre de fréquence :

1. `Hello 👋` — défaut (≈ 6 cas sur 8). C'est l'ouverture qu'on prend si
   rien ne justifie un autre choix.
2. `Hey !` — quand on évoque un ton plus rapide, plus direct, ou un partage
   "entre potes" (typiquement un prompt court ou une vidéo).
3. Pas d'ouverture, on attaque direct par `Voici le 🔗 comme promis : URL` —
   uniquement quand l'URL est l'élément principal et que tout le reste est
   du contexte court.

### Livraison

C'est la colonne vertébrale du DM. Pattern quasi systématique :

```
Voici le 🔗 [du / de la / avec / pour / comme promis] [ressource]
```

Variantes observées :
- « Voici le 🔗 avec les 100 codes à utiliser sur ChatGPT »
- « Voici le 🔗 comme promis : https://… »
- « Voilà tout ce qu'il te faut pour G0DM0D3 👇 » → « Le 🔗 de la plateforme : … »
- « Voici le 🔗 du prompt qui encode les règles pour… »
- « Voici le 🔗 pour accéder au guide où je t'explique en détail… »
- « Voici le 🔗 de la vidéo de 8 minutes qui te montre… »

🔗 est obligatoire. C'est la signature visuelle du message.

### Contexte (1-4 paragraphes, optionnel)

Si la ressource a besoin d'être située, on ajoute 1 à 4 paragraphes très
courts. Objectifs :

- **Expliquer ce qu'il y a dedans** (« 95 micro-SaaS triés et catégorisés,
  des petits outils qui répondent chacun à un besoin précis »).
- **Donner du contexte personnel** (« ça fait quelques semaines que je
  construis cette base »).
- **Cadrer l'usage** (« ce sont des raccourcis de prompt à copier-coller au
  début ou à la fin de tes demandes »).

Règles :
- Phrases courtes. Une idée par paragraphe.
- Aération maximale : ligne vide entre chaque paragraphe.
- Tutoiement systématique.
- Pas de superlatif gratuit (« incroyable », « hallucinant »). On reste
  factuel et chaleureux.

### Mode d'emploi (optionnel)

Si la ressource nécessite un setup (clé API, étapes, traduction, etc.) :

- Numéroter avec `1️⃣ 2️⃣ 3️⃣ 4️⃣` (cf. exemple G0DM0D3).
- Une étape = une ligne courte.
- Ajouter un `⚠️ Important : …` quand il y a un piège à éviter.
- Ajouter un `👨‍💻 Pour les plus tech : …` quand on tease une version
  avancée (open source, self-host, etc.).

### Cross-promo soft (optionnel)

Pour orienter vers une ressource complémentaire :

```
Je te mets aussi le 🔗 de [Cofondateur IA™️] si tu veux aller plus loin.
```

Une seule cross-promo max. Elle doit sentir l'extra généreux, pas la vente.

### Fermeture

**Pas de signature**. Pas de « Bisous, Alex », pas de « Belle journée »,
pas de « N'hésite pas si tu as des questions ». On termine sur la valeur
livrée, point.

## Anti-patterns (ce qu'on n'écrit jamais)

- ❌ Hashtags
- ❌ « J'espère que ça te plaira »
- ❌ « Merci de m'avoir contacté » / « Merci pour ton commentaire »
- ❌ Paragraphes longs et denses
- ❌ Ton commercial (« profite-en », « offre limitée »)
- ❌ Plus de 2 emojis par paragraphe
- ❌ Vous au lieu de tu
- ❌ Phrases qui paraphrasent le carrousel (le DM délivre, il ne récapitule pas)

## Longueur

- **Court (3-5 lignes)** : la ressource parle d'elle-même, l'URL suffit
  presque (ex. vidéo Dupliq, prompt Z-Image).
- **Moyen (6-10 lignes)** : ressource avec contexte (ex. 100 codes ChatGPT,
  base micro-SaaS).
- **Long (15-25 lignes)** : ressource avec setup ou tutoriel (ex. G0DM0D3
  avec ses 4 étapes).

Adapter à la complexité de la ressource, jamais à la longueur du carrousel.

## URL

- Si l'URL définitive est connue (ex. présente dans `brief.source` ou
  donnée par Alex), on l'écrit directement.
- Sinon, placeholder `[LIEN À COMPLÉTER]` à remplacer par Alex avant de
  coller dans ManyChat. Toujours préfixé par 🔗 dans le texte.

## Squelette type

```
Hello 👋

Voici le 🔗 [du / de la / avec / pour] [ressource] : [URL ou placeholder]

[1-2 phrases qui situent ce qu'il y a dedans et à qui ça sert.]

[Optionnel : setup, instructions, ou tip d'usage.]

[Optionnel : cross-promo soft d'une seule ressource complémentaire.]
```

## Stockage

Dans `carousel.json`, champ racine, **uniquement** si le dernier slide est
un `dmCta` :

```json
{
  "title": "...",
  "slides": [..., { "type": "dmCta", "keyword": "RAPPORT", ... }],
  "caption": "...",
  "dmMessage": "Hello 👋\n\nVoici le 🔗 du rapport complet sur…\n\n…"
}
```

Le DM se lit / s'édite depuis l'onglet **Publication** du studio, sous la
caption.
