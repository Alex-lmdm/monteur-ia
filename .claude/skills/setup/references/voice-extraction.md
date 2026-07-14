# Extraction de voix — comment lire un corpus et en tirer un Profil de voix

C'est la méthode du **cœur du Clone Monteur** : à partir de 5-15 scripts de l'utilisateur, produire
un **Profil de voix** exploitable par le skill `reel-script` (celui-ci écrira ensuite dans sa voix).
Le but n'est pas de résumer ses vidéos — c'est d'isoler **ce qui fait que ça sonne comme LUI**,
indépendamment du sujet.

> Sortie attendue : un profil rempli dans `templates/voice-profile.md.tpl`, structuré comme le
> Profil de voix du skill `reel-script` (hooks, rythme prompteur, banque de tics, structure CTA,
> anti-slop perso). On restitue d'abord à l'utilisateur, on écrit après validation.

---

## 0. Avant de commencer — la règle qui évite 90 % des erreurs

1. **Ne jamais inventer un tic à partir d'UN seul exemple.** Un pattern n'entre dans le profil que
   s'il apparaît **au moins 2-3 fois** dans le corpus. Un « fou » isolé n'est pas un tic ; « le plus
   fou, c'est que… » vu 5 fois, oui.
2. **Distinguer la VOIX du SUJET.** Si le mot « ChatGPT » revient partout, c'est le sujet (sa niche),
   pas un trait de style. Ce qui compte : *comment* il tourne ses phrases, pas *de quoi* il parle.
   Test simple : « est-ce que ce trait resterait s'il parlait d'un tout autre sujet ? » Si oui →
   c'est de la voix.
3. **Citer des preuves.** Chaque pattern retenu s'accompagne d'1-2 exemples réels tirés du corpus.
   Pas de pattern sans citation.

---

## 1. Ce qu'on cherche (les 7 axes)

Passer le corpus au crible de ces 7 axes. Pour chacun : noter le motif dominant + 1-2 citations.

1. **Hooks (ligne 1).** Comment il ouvre. Classer chaque hook du corpus dans un pattern :
   bénéfice « maintenant », news-bombe, how-to chronométré, superlatif + curiosité, conséquence
   chiffrée, pouvoir d'un artefact, provocation, problème agité, démo visuelle directe… Repérer
   **ses 2-3 patterns favoris** (les plus fréquents) — c'est ce que `reel-script` proposera en
   priorité.
2. **Second hook / relance.** A-t-il un réflexe de relance juste après le hook ? (retournement
   « mais ça change tout », montée d'enjeu « le plus fou c'est que… », preuve sociale chiffrée,
   personnage/storytelling, cue de démo « regarde ça »).
3. **Longueur & rythme des phrases.** Phrases courtes staccato vs longues explicatives ? Alterne-t-il
   (vagues) ? Utilise-t-il des fragments (une idée par ligne) ? Des ellipses « … » avant un reveal ?
4. **Adresse.** Tutoiement ou vouvoiement (systématique ?). Usage du « je » pour le vécu
   (« j'ai testé », « je lui ai dit… »).
5. **Banque de tics & d'oralité.** Élisions et tournures parlées récurrentes (« un mec », « en gros »,
   « du coup », « franchement », « c'est cadeau »…). Vulgarisation (« en gros, … », « comme si… »).
   Superlatifs favoris (fou, dingue, une bombe…) et **à quelle fréquence** (ciblés ou partout).
6. **Structure des CTA.** Comment il termine : mot-clé → DM, lien bio, screenshot, abonnement, chute
   hype sans CTA dur ? Formulation type. Y a-t-il un caveat honnête récurrent (« par contre… »,
   « seule chose à savoir… ») ?
7. **Anti-slop perso.** Ce qu'il ne fait JAMAIS et qu'il faut bannir : tirets longs, ton corporate
   (« découvrez », « plongeons dans »), listes formelles, sur-explication. Noter ce qui, dans son
   corpus, montre qu'il fuit le style « IA générique ».

---

## 2. Comment classer (méthode de passage)

1. **Lire tout le corpus une fois** sans annoter (imprégnation).
2. **Deuxième passe, axe par axe** : pour chaque script, taguer le hook, relever tics et tournures,
   noter la longueur moyenne des phrases, repérer le CTA.
3. **Compter.** Regrouper par fréquence. Ne garder dans le profil que ce qui **récurre** (≥ 2-3×).
   Ranger les hooks par fréquence décroissante → les 2-3 premiers = ses favoris.
4. **Écarter le bruit** : hapax (mot vu une fois), termes de sujet (noms d'outils/marques), et tout
   ce qui relève de l'actu ponctuelle.
5. **Rédiger le profil** dans la structure de `templates/voice-profile.md.tpl` : une section par axe,
   chaque trait accompagné de sa/ses citation(s).

---

## 3. Pièges (déjà vus, à éviter)

- **Sur-généraliser depuis un petit corpus.** Avec 5 scripts, rester prudent : marquer les traits
  incertains « tendance à confirmer ». Ne pas présenter une hypothèse comme une règle.
- **Confondre thème et style** (cf §0.2). Le piège n°1.
- **Lisser la voix.** Ne pas « corriger » son oralité vers un français écrit propre — les élisions,
  les fragments, les « du coup » SONT la voix. Les garder tels quels.
- **Copier des phrases entières comme templates.** On extrait des *patterns* (formules à trous), pas
  des phrases figées qu'on ressortirait mot pour mot (ça sonnerait faux et répétitif).
- **Inventer des tics « qui feraient bien ».** Si ce n'est pas dans le corpus, ça n'entre pas.
- **Oublier le CTA et l'anti-slop.** Ce sont deux axes que l'analyse zappe souvent alors qu'ils
  pèsent lourd dans la restitution.

---

## 4. Restitution à l'utilisateur (avant écriture)

Présenter **une liste courte et lisible** : « Voici les N patterns que je retiens de ta voix. »
Pour chaque : le trait en une ligne + un exemple tiré de SES scripts. Puis :
> « Dis-moi ce qui sonne juste et ce qui sonne faux — je corrige avant de figer ton profil. »

Intégrer ses corrections, **puis seulement** remplir `templates/voice-profile.md.tpl`, l'injecter
entre les marqueurs `voice-profile` de `.claude/skills/reel-script/SKILL.md`, et copier le corpus
dans `.claude/skills/reel-script/references/scripts-exemples.md`.

---

## 5. Mode interview de secours (pas de corpus)

Si l'utilisateur n'a aucun script à coller, on ne peut pas mesurer — on **interviewe** (5 questions
du bloc B dans `questions.md`), on construit un profil **générique de sa niche** (`brand.niche`) et
on le **marque explicitement** en tête de profil :
> `> ⚠️ Profil générique (aucun script fourni). À affiner dès que tu auras 5+ vrais Reels : relance
> `/setup voix`.`
Rester modeste sur les traits : ce sont des hypothèses de départ, pas la vraie voix mesurée.
