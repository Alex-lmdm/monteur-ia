---
name: reel-script
description: >-
  Écrit le script parlé d'un Reel dans la voix du créateur,
  prêt à lire au prompteur (langue parlée, face caméra). Use whenever the user wants a short-form
  script in their voice: turning a reference transcript into "leur version", turning rough ideas or
  links into a finished script, or rewriting a draft so it sounds like them. Sujet typique : la
  niche du créateur. Produit du texte, pas d'image : le visuel relève de motion-design.
---

# Script de Reel (voix du créateur, prêt prompteur)

Ce skill sert à **écrire le script parlé** d'un Reel / short-form vidéo pour le compte du créateur.
Identité, voix et niche viennent de `brand.config.json` (`brand.firstName`, `brand.handle`,
`brand.name`, `brand.niche`, `brand.language`) et du **profil de voix** (§4, généré par `/setup`).
Le script est lu **au prompteur**, face caméra : il doit donc sonner comme le créateur qui parle
**naturellement**, pas comme un texte écrit.

> Ce skill couvre **l'écriture du voiceover**. Le visuel (schémas, motion, overlays) relève de
> `motion-design`.

---

## 0. Quand utiliser ce skill

Dès que le créateur veut un script de Reel, dans l'un de ces 3 cas :

1. **Avec une vidéo de référence** — il fournit un transcript (dans sa langue ou une autre) d'un Reel
   qui l'a inspiré et demande « fais-en ma version ». → On garde le **sujet** et l'**angle**, on jette
   la formulation, on réécrit 100 % dans sa voix. **Ne jamais traduire littéralement** un transcript.
2. **Avec des idées en vrac** — quelques angles, références, bullet points, un lien. → On structure
   et on rédige le script complet.
3. **Avec un brouillon** — il a déjà un jet et veut qu'on le « passe à sa sauce » + qu'on corrige le
   rythme / le hook / le CTA.

---

## 1. Le workflow (de l'input au script)

1. **Identifier le sujet + l'angle.** C'est quoi le produit / la news / le hack / le conseil ? Quel
   est l'angle qui accroche (gratuit ? rapide ? contre-intuitif ? un résultat chiffré ? une démo
   visuelle ?).
2. **Choisir le type de CTA** — ça conditionne le reste. Toutes les formules exactes :
   **`references/cta.md`**. Le type de CTA se choisit dans `brand.config.json` → `cta.types` /
   `cta.defaultKeyword`.
   - Ressource avec lien à partager → **commentaire → DM (mot-clé)**, **lien en bio** ou **lien en
     description**.
   - Un artefact à donner (prompt, template, checklist) → **screenshot** et/ou **commentaire → DM**.
   - News/conseil pur sans ressource → **chute hype** (pas de CTA dur) ou **abonnement**.
3. **Écrire le hook** (§3.1). Le hook est 80 % du job, donc : **toujours 3 variantes, sur 3 patterns
   différents du tableau §3.1** (jamais 3 fois le même pattern reformulé). Le créateur choisit.
4. **Construire le corps** en suivant la structure type (§3) et les outils du corps (§3.3).
5. **Poser le CTA** (`references/cta.md`).
6. **Passer au format prompteur** (§2) : phrases courtes, fragments, ellipses, mots à accentuer.
7. **Vérifier la longueur** (§6).
8. **Si CTA = mot-clé → juste NOTER le mot-clé.** Le DM (`cta.dmTool`) et la légende Instagram se
   rédigent à la publication (projet vidéo), pas ici.

Livrer le script **en bloc lisible** (une idée par ligne / saut de ligne aux respirations), pas en
paragraphe dense.

---

## 2. La voix — règles d'écriture prompteur

C'est le cœur du skill. Le texte doit pouvoir être lu **à voix haute sans buter**. Les mots et tics
**propres au créateur** vivent dans le profil de voix (§4) ; ici, les **règles de dosage et de
rythme**, universelles quelle que soit la niche.

- **Tutoiement systématique** (adapter à la langue `brand.language`). Toujours « tu / te / ton ».
- **« Je » pour le vécu.** Le créateur raconte ce qu'il a testé : « j'ai testé », « je l'ai fait et
  voilà le résultat », « j'me suis créé ce système ».
- **Phrases courtes. Souvent des fragments.** Une idée par ligne. Le point sert de respiration.
- **Oralité assumée.** Élisions et tournures parlées, piochées dans le profil de voix (§4).
- **Ellipses « … » pour suspendre** juste avant un reveal : « Mais le plus fou… c'est même pas ça. »
- **Rythme en vagues** : alterner une phrase un peu plus longue puis une rafale de fragments staccato
  (« Rapide. Simple. Sans matériel. »).
- **Chiffres concrets** pour la crédibilité : « +30 000 personnes », « 20x plus rapide », « -8 % en
  une journée », « 3 fois par semaine ». Les chiffres viennent du sujet réel, jamais inventés.
- **Superlatifs émotionnels, mais ciblés** (le créateur a les siens dans le profil §4) : un ou deux
  par script, sur le pic — pas à toutes les lignes.
- **Émphase à l'oral.** Mettre en *italique* ou **gras** les 1-3 mots à accentuer. Ce sont des indices
  prompteur, pas du style.

---

## 3. Anatomie d'un script

Structure type (AIDA orale) — c'est **la** référence de structure, les autres sections y renvoient :

```
HOOK            (1 ligne)        → stoppe le scroll en < 2 s
SECOND HOOK     (1-2 lignes)     → confirme + creuse la curiosité (souvent preuve sociale)
CORPS           (le gros)        → ça s'appelle X → en gros → étapes/specs/démo → le pic → caveat
CTA / CHUTE     (1-2 lignes)     → l'action (commentaire/bio/description/screenshot/abo) ou hype final
```

### 3.1 Le hook (ligne 1)

Le plus important. Choisir le pattern qui colle au sujet. Les 9 patterns (avec des exemples
**multi-niches** — remplace-les par un exemple dans la niche `brand.niche` du créateur) :

| Pattern | Formule | Exemple (à décliner dans TA niche) |
|---|---|---|
| **Bénéfice « maintenant »** | « Tu peux maintenant [bénéfice fou] [gratuitement / sans X]. » | « Tu peux maintenant suivre tout ton budget en 2 minutes par semaine. » |
| **News-bombe** | « [Acteur] vient de [lâcher une bombe / tout changer / lancer X]. » | « Cette marque vient de casser tous les prix du marché. » |
| **How-to chronométré** | « Comment [verbe fort] [chiffre] en [délai court]. » | « Comment préparer 5 repas de la semaine en 30 minutes. » |
| **Superlatif + curiosité** | « J'ai trouvé le [truc] le plus [étrange/sous-coté] pour [résultat]. » | « J'ai trouvé l'exercice le plus sous-coté pour le dos. » |
| **Conséquence choc chiffrée** | « Ce [truc] a fait [résultat choc + chiffre]. » | « Cette habitude m'a fait économiser 300 € par mois. » |
| **Le pouvoir d'un artefact** | « Ce [prompt/template/routine] permet [résultat fou]. » | « Ce template gère toute ma compta d'indépendant tout seul. » |
| **Provocation « désolé »** | « Désolé pour [groupe] mais [vous êtes obsolètes]. » | « Désolé pour ceux qui vendent encore des plans PDF, mais c'est fini. » |
| **Problème agité** | « Les [X] [ont tous le même défaut] parce que [cause]. » (le second hook renverse) | « Les régimes échouent tous pour la même raison. » |
| **Démo visuelle directe** | « ça c'est X, ça c'est Y, et ça c'est Z. » (comparaison montrée à l'écran) | « ça c'est la version classique, ça c'est la mienne, et ça c'est le résultat. » |

**Ingrédients qui boostent un hook** : *gratuit*, *rapide*, *« maintenant »*, un nom concret que
l'audience reconnaît, un chiffre, un délai (« en 30 secondes », « en 2 minutes »).

### 3.2 Le second hook / la relance

Juste après le hook, on **confirme la promesse et on creuse** avant de livrer. Patterns :

- **Le retournement** : « mais ça change tout. » / « Et cette semaine, ça a vraiment tout changé. »
- **On monte les enjeux** : « Et je te parle pas d'un simple truc. » / « Mais le plus fou, c'est que… »
- **Le mécanisme intriguant** : explique en une phrase le tour de passe-passe qui rend le sujet
  surprenant.
- **La preuve sociale** : « +30 000 personnes l'utilisent déjà. » / « C'est le mieux noté de sa catégorie. »
- **Le personnage / storytelling** : « Il y a une personne qui fait ça depuis 10 ans… »
- **Le cue de démo** : « Regarde ça. » (puis on montre)

### 3.3 Le corps

Outils à piocher selon le sujet :

- **Nommer** : « Ça s'appelle **[Nom]**. » (toujours une fois, clairement)
- **Vulgariser** : « En gros, [reformulation simple]. » (systématique après un passage technique)
- **Étapes** : « D'abord, tu… Ensuite tu… puis tu… » (pour les tutos)
- **Avant / maintenant** : « Avant tu pouvais X, mais maintenant tu peux Y. »
- **Capacités en staccato** : une fonctionnalité / un bénéfice par ligne.
- **Preuve perso** : « Je l'ai testé. » / « Je l'ai fait pendant un mois. Et voilà. »
- **Specs / chiffres** : « 20x plus rapide et 30x moins cher. »
- **Le pic** (obligatoire ou presque) : « Mais le plus fou, c'est que… » / « le truc le plus fou… »
- **Le caveat honnête** (un aveu franc renforce la confiance) : « ⚠️ Par contre… » / « Seule chose à
  savoir… ». Marquer d'un ⚠️ quand c'est un vrai warning.

### 3.4 La chute / CTA

→ **`references/cta.md`** (6 types, formules exactes, règle du mot-clé).

---

## 4. Profil de voix (banque de vocabulaire & tics du créateur)

<!-- BEGIN GENERATED: voice-profile -->
**Profil de voix perso pas encore généré — et ce n'est pas grave : le skill écrit déjà tes scripts
avec la méthode complète** (§2 règles de voix, §3 hooks/structure, `references/cta.md`). Tu obtiens un
script prêt à lire dès maintenant.

**Bonus (optionnel) :** pour que ton monteur attrape *ta* voix à toi (tes accroches, tes tics
d'oralité, tes superlatifs signature), colle 5 à 15 de tes propres scripts via **`/setup` (bloc
Voix)** — tu peux le faire quand tu veux, même après plusieurs vidéos. Le squelette généré vit dans
`templates/voice-profile.md.tpl`. Tant que cette section est là, appuie-toi sur les règles
universelles de §2 et écris dans une voix directe, parlée et sobre.
<!-- END GENERATED: voice-profile -->

---

## 5. Anti-slop (ce qu'il ne faut JAMAIS faire)

Détail complet dans `design-system/writing-anti-slop.md`. Les essentiels côté script :

- ❌ **Pas de tirets longs (—) partout.** Bannis.
- ❌ **Pas de mots de remplissage** (« il est important de noter que », « afin de »).
- ❌ **Pas de ton corporate / IA générique** : « Découvrez », « Plongeons dans », « Dans cette vidéo
  nous allons », « N'attendez plus ».
- ❌ **Pas de listes à puces formelles dans le script** — on parle, on enchaîne.
- ❌ **Pas de sur-explication.** On garde le mystère jusqu'au reveal (« et c'est là que ça devient
  intéressant… »).

---

## 6. Longueur & rythme

- **Cible : ~30 à 45 secondes** parlés, soit environ **80 à 200 mots**.
- Le **hook** doit tomber dans la **première seconde** — pas d'intro, pas de « salut c'est moi ».
- Le **CTA** est dans la **dernière phrase** (sauf chute hype).
- Plus le sujet est technique, plus on raccourcit les phrases et on multiplie les fragments.

---

## 7. Checklist avant de livrer

- [ ] Le hook stoppe le scroll en < 2 s et contient un angle fort (gratuit / chiffre / « maintenant » / choc).
- [ ] Un second hook relance la curiosité avant le contenu.
- [ ] L'outil/sujet est **nommé clairement** une fois.
- [ ] Il y a un **pic** et un **caveat honnête** si pertinent.
- [ ] Tutoiement partout, langue parlée, fragments, ellipses, 0 tiret long.
- [ ] Un CTA unique et clair (mot-clé / bio / description / screenshot / abo / hype).
- [ ] Si mot-clé : le mot est court, en lien direct, + un bonus de valeur, et il est **noté** (le DM
      se rédige à la publication).
- [ ] Longueur conforme (§6). Mots à accentuer balisés en gras/italique.
- [ ] Mise en page « prompteur » : une idée par ligne, sauts de ligne aux respirations.
- [ ] Le script sonne comme le **profil de voix** (§4) — si le profil est vide, sonne au moins direct
      et parlé (§2).

---

## 8. Corpus de référence

Les scripts déjà postés et performants du créateur (annotés par structure et type de CTA) vivent dans
**`references/scripts-exemples.md`**. À relire pour caler le ton avant d'écrire, et pour retrouver le
bon pattern de hook / CTA selon le sujet. Ce corpus est rempli par `/setup` (bloc Voix) à partir des
propres scripts de l'utilisateur.
