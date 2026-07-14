---
name: lmdm-reel-script
description: >-
  Écrit le script parlé d'un Reel dans la voix d'Alex / @LeMondeDuMarketing, prêt à lire au
  prompteur (français parlé, face caméra). Use whenever the user wants a short-form script in
  their voice: turning a reference transcript into "leur version", turning rough ideas or links
  into a finished script, or rewriting a draft so it sounds like him. Sujet typique : actu,
  outils et hacks IA. Produit du texte, pas d'image : le visuel relève de lmdm-motion-design.
---

# LMDM — Script de Reel (voix Alex, prêt prompteur)

Ce skill sert à **écrire le script parlé** d'un Reel / short-form vidéo pour le compte
**@LeMondeDuMarketing** (Alex). Le script est lu **au prompteur**, face caméra : il doit donc
sonner comme Alex qui parle **naturellement**, pas comme un texte écrit.

> Ce skill couvre **l'écriture du voiceover**. Le visuel (schémas, motion, overlays) relève de
> `lmdm-motion-design`.

---

## 0. Quand utiliser ce skill

Dès qu'Alex veut un script de Reel, dans l'un de ces 3 cas :

1. **Avec une vidéo de référence** — il fournit un transcript (FR ou autre langue) d'un Reel qui
   l'a inspiré et demande « fais-en ma version ». → On garde le **sujet** et l'**angle**, on jette
   la formulation, on réécrit 100 % dans sa voix. **Ne jamais traduire littéralement** un transcript.
2. **Avec des idées en vrac** — quelques angles, références, bullet points, un lien GitHub. → On
   structure et on rédige le script complet.
3. **Avec un brouillon** — il a déjà un jet et veut qu'on le « passe à sa sauce » + qu'on corrige
   le rythme / le hook / le CTA.

---

## 1. Le workflow (de l'input au script)

1. **Identifier le sujet + l'angle.** C'est quoi l'outil / la news / le hack ? Quel est l'angle qui
   accroche (gratuit ? open source ? « ça tue une boîte » ? un personnage ? une démo visuelle ?).
2. **Choisir le type de CTA** — ça conditionne le reste. Toutes les formules exactes :
   **`references/cta.md`**.
   - Outil/repo avec lien à partager → **commentaire → DM (mot-clé)**, **lien en bio** ou
     **lien en description**.
   - Un prompt à donner → **screenshot** et/ou **commentaire → DM**.
   - News pure sans ressource → **chute hype** (pas de CTA dur) ou **abonnement**.
3. **Écrire le hook** (§3.1). Le hook est 80 % du job, donc : **toujours 3 variantes, sur 3
   patterns différents du tableau §3.1** (jamais 3 fois le même pattern reformulé). Alex choisit.
4. **Construire le corps** en suivant la structure type (§3) et les outils du corps (§3.3).
5. **Poser le CTA** (`references/cta.md`).
6. **Passer au format prompteur** (§2) : phrases courtes, fragments, ellipses, mots à accentuer.
7. **Vérifier la longueur** (§6).
8. **Si CTA = mot-clé → juste NOTER le mot-clé.** Le DM ManyChat et la légende Instagram se
   rédigent à la publication (projet vidéo), pas ici.

Livrer le script **en bloc lisible** (une idée par ligne / saut de ligne aux respirations), pas en
paragraphe dense.

---

## 2. La voix — règles d'écriture prompteur

C'est le cœur du skill. Le texte doit pouvoir être lu **à voix haute sans buter**. Les mots eux-mêmes
sont dans la banque (§4) ; ici, les **règles de dosage et de rythme**.

- **Tutoiement systématique.** Toujours « tu / te / ton ».
- **« Je » pour le vécu.** Alex raconte ce qu'il a testé : « j'ai testé », « je lui ai dit… et il
  l'a fait », « j'ai généré ces images », « j'me suis créé ce prompt ».
- **Phrases courtes. Souvent des fragments.** Une idée par ligne. Le point sert de respiration.
- **Oralité assumée.** Élisions et tournures parlées, piochées dans la banque (§4).
- **Ellipses « … » pour suspendre** juste avant un reveal : « Mais le plus fou… c'est même pas la
  qualité. » / « Et d'inventer lui-même ce qu'il est censé restaurer. »
- **Rythme en vagues** : alterner une phrase un peu plus longue puis une rafale de fragments
  staccato (« Colonnes. Typographie. Hiérarchie visuelle. Alignements. »).
- **Chiffres concrets** pour la crédibilité : « +30k développeurs », « 20x plus rapide »,
  « 30x moins cher », « -8% en une journée », « 1512 de score », « 55 modèles en même temps ».
- **Superlatifs émotionnels, mais ciblés** (liste en §4) : un ou deux par script, sur le pic — pas à
  toutes les lignes.
- **Émphase à l'oral.** Mettre en *italique* ou **gras** les 1-3 mots qu'Alex doit accentuer
  (« est *encore plus fou* », « C'est la *densité* »). Ce sont des indices prompteur, pas du style.

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

Le plus important. Choisir le pattern qui colle au sujet. Patterns d'Alex (avec ses vrais exemples) :

| Pattern | Formule | Exemple réel |
|---|---|---|
| **Bénéfice « maintenant »** | « Tu peux maintenant [bénéfice fou] [gratuitement / pour toujours]. » / « [Marque] peut maintenant [truc inattendu]. » | « Tu peux maintenant utiliser Claude Code gratuitement pour toujours. » · « Claude peut maintenant t'aider avec ta comptabilité française. » |
| **News-bombe** | « [Entreprise] vient de [lâcher une bombe / tuer des centaines de startups / lancer X]. » | « Anthropic vient de lâcher une bombe. » · « Claude vient de tuer des centaines de startups. » |
| **How-to chronométré** | « Comment [verbe fort] [chiffre] en 30 secondes. » | « Comment jailbreaker plus de 55 IA en 30 secondes. » |
| **Superlatif + curiosité** | « J'ai trouvé le [prompt/outil] le plus [étrange] à tester sur [ChatGPT]. » / « [Produit]… est encore plus fou que ce que tu penses. » | « J'ai trouvé le prompt le plus étrange à tester sur ChatGPT. » · « GPT Image 2… est *encore plus fou* que ce que tu penses. » |
| **Conséquence choc chiffrée** | « Cet outil [gratuit] de [boîte] a fait [résultat choc + chiffre]. » | « Cet outil gratuit de Google a fait chuter l'action Figma de 8% en une seule journée. » |
| **Le pouvoir d'un artefact** | « Ce prompt / Ce skill / Cet outil force/permet [résultat fou]. » | « Ce prompt force ChatGPT & Claude à écrire comme un vrai humain. » |
| **Provocation « désolé »** | « Désolé pour [groupe] mais [vous êtes obsolètes]. » | « désolé pour les graphistes qui créent des miniatures YouTube mais la plupart viennent de devenir obsolètes. » |
| **Problème agité** | « Les [X] [ont tous le même défaut] parce que [cause]. » (le second hook renverse) | « Les sites créés par IA se ressemblent tous parce que l'IA ne sait pas vraiment composer une page. » |
| **Démo visuelle directe** | « ça c'est X, ça c'est Y, et ça c'est Z. » (comparaison montrée à l'écran) | « ça c'est NanoBanana, ça c'est nano banana Pro, et ça c'est z-image-turbo. » |

**Ingrédients qui boostent un hook** : *gratuit*, *open source*, *« maintenant »*, un nom de marque
IA connue (Claude, ChatGPT, Google, Anthropic), un chiffre, un délai (« en 30 secondes », « 2 minutes »).

### 3.2 Le second hook / la relance

Juste après le hook, on **confirme la promesse et on creuse** avant de livrer. Patterns :

- **Le retournement** : « mais ce skill change ça. » / « Et la mise à jour de cette semaine change
  vraiment tout. »
- **On monte les enjeux** : « Et je te parle pas d'un simple prompt. » / « Mais le plus fou, c'est que… »
- **Le mécanisme intriguant** : « Quelqu'un vient de créer un outil qui fait croire à Claude Code
  qu'il parle à Claude… alors qu'en réalité, il utilise d'autres modèles beaucoup moins chers. »
- **La preuve sociale** : « +30k développeurs l'utilisent déjà. » / « Sur LLM Arena, il est numéro 1. »
- **Le personnage / storytelling** : « Il y a un mec sur Twitter qui s'appelle Pliny the liberator.
  Il passe son temps à jailbreaker toutes les IA… au point où il s'est déjà fait bannir plusieurs fois. »
- **Le cue de démo** : « Regarde ça. » (puis on montre)

### 3.3 Le corps

Outils à piocher selon le sujet :

- **Nommer** : « Ça s'appelle **[Nom]**. » (toujours une fois, clairement)
- **Vulgariser** : « En gros, [reformulation simple]. » (systématique après un passage technique)
- **Étapes** : « D'abord, tu… Ensuite tu… puis tu… » (pour les tutos d'installation)
- **Avant / maintenant** : « Avant tu pouvais X, mais maintenant tu peux Y. »
- **Capacités en staccato** : une fonctionnalité par ligne.
- **Preuve perso** : « Je l'ai testé. » / « Je lui ai dit : "…" Et il l'a fait. »
- **Specs / chiffres** : « 20x plus rapide et 30x moins cher. »
- **Le pic** (obligatoire ou presque) : « Mais le plus fou, c'est que… » / « le truc le plus fou… »
- **Le caveat honnête** (un aveu franc renforce la confiance) : « ⚠️ Par contre… » / « Seule chose à
  savoir… » / « c'est encore en preview, donc c'est pas parfait ». Marquer d'un ⚠️ quand c'est un
  vrai warning.

### 3.4 La chute / CTA

→ **`references/cta.md`** (6 types, formules exactes, règle du mot-clé).

---

## 4. Banque de vocabulaire & tics de langage

À réutiliser pour que ça sonne « Alex » :

- **Accroches/relances** : « le plus fou, c'est que… », « le truc le plus fou… », « Et là, il vient
  de… », « Mais le plus fou… », « Regarde ça. », « Ce qui change tout, c'est que… ».
- **Vulgarisation** : « En gros, … », « tu lui demandes… et il te… », « comme si… ».
- **Oralité** : « un mec », « un mec sur Twitter », « bref », « franchement », « à peu près »,
  « du coup », « j'me suis », « c'est cadeau », « c'est en bonus », « pour toujours ».
- **Valeur** : « 100% gratuit et open source », « entièrement open source », « ça prend 2 minutes »,
  « rien à installer », « pas d'inscription », « ça coûte quasiment rien ».
- **Superlatifs** : fou, dingue, incroyable, impressionnant, énorme, une bombe, parfait, hyper réaliste.
- **Caveats** : « Par contre… », « Seule chose à savoir… », « c'est encore en preview, donc c'est
  pas parfait », « Il te faut un abonnement payant ».

---

## 5. Anti-slop (ce qu'il ne faut JAMAIS faire)

Alex a littéralement fait une vidéo contre l'écriture IA. Donc :

- ❌ **Pas de tirets longs (—) partout.** Bannis.
- ❌ **Pas de mots de remplissage** (« il est important de noter que », « afin de »).
- ❌ **Pas de ton corporate / IA générique** : « Découvrez », « Plongeons dans », « Dans cette
  vidéo nous allons », « N'attendez plus ».
- ❌ **Pas de listes à puces formelles dans le script** — on parle, on enchaîne.
- ❌ **Pas de sur-explication.** On garde le mystère jusqu'au reveal (« et c'est là que ça
  devient bizarre… »).

---

## 6. Longueur & rythme

- **Cible : ~30 à 45 secondes** parlés, soit environ **80 à 200 mots**. (La vidéo de réf de départ
  faisait ~29 s / ~110 mots.)
- Le **hook** doit tomber dans la **première seconde** — pas d'intro, pas de « salut c'est Alex ».
- Le **CTA** est dans la **dernière phrase** (sauf chute hype).
- Plus le sujet est technique, plus on raccourcit les phrases et on multiplie les fragments.

---

## 7. Checklist avant de livrer

- [ ] Le hook stoppe le scroll en < 2 s et contient un angle fort (gratuit / chiffre / « maintenant » / choc).
- [ ] Un second hook relance la curiosité avant le contenu.
- [ ] L'outil/sujet est **nommé clairement** une fois.
- [ ] Il y a un **pic** et un **caveat honnête** si pertinent.
- [ ] Tutoiement partout, français parlé, fragments, ellipses, 0 tiret long.
- [ ] Un CTA unique et clair (mot-clé / bio / description / screenshot / abo / hype).
- [ ] Si mot-clé : le mot est court, en lien direct, + un bonus de valeur, et il est **noté** (le DM
      se rédige à la publication).
- [ ] Longueur conforme (§6). Mots à accentuer balisés en gras/italique.
- [ ] Mise en page « prompteur » : une idée par ligne, sauts de ligne aux respirations.

---

## 8. Corpus de référence

14 scripts réels d'Alex (déjà postés, ont bien marché), annotés par structure et type de CTA :
voir **`references/scripts-exemples.md`**. À relire pour caler le ton avant d'écrire, et pour
retrouver le bon pattern de hook / CTA selon le sujet.
