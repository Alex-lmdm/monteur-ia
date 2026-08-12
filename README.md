# Monteur IA — monte tes Reels en langage naturel

Tu tournes ta vidéo face caméra. Ton IA fait le montage : elle coupe les blancs et les ratés,
pose le motion design, cale les sous-titres, ajoute les SFX et la musique.
Toi, tu fais tes retours en français — « ça en plein écran », « mets cette image ici » — et elle refait.

Pas besoin de savoir coder. Tu parles à ton IA comme à un monteur.

---

Ce repo accompagne la formation **[Monteur IA](https://www.lemondedumarketing.fr/monteur-ia)**.
La formation te montre chaque étape en vidéo, pas-à-pas. Le repo s'utilise aussi seul si tu es déjà à l'aise
avec Claude Code ou Codex.

---

## Ce que tu obtiens

Un système de montage complet pour un seul format : le **Reel Instagram talking-head vertical**
(1080×1920, 30 fps) — ta vraie vidéo face caméra, avec du motion design par-dessus, section par section.

Le montage se pilote en conversation. Tu ne touches pas une ligne de code : tu écris ce que tu veux,
l'IA le fait, tu valides ou tu corriges.

---

## Démarrage en 3 étapes

### 1. Vérifie que ta machine est prête

| | Minimum | Conseillé |
|---|---|---|
| **Ordinateur** | Mac (Apple Silicon M1+, macOS 13+) ou Windows 10/11 64-bit | Mac Apple Silicon |
| **Mémoire (RAM)** | 8 Go | 16 Go |
| **Disque libre** | ~10 Go | 20 Go |
| **Abonnement IA** | Claude Pro **ou** ChatGPT Plus — ~20 €/mois | — |

L'abonnement IA (~20 €/mois) est **le seul coût**. Tout le reste du système est gratuit et open source
(Node.js, ffmpeg, Whisper, HyperFrames).

### 2. Installe le système

Clique dans ce dossier, ouvre **Claude Code** (ou **Codex**), et colle **le prompt d'installation unique**.
L'IA détecte ton système, installe ce qui manque, et vérifie que tout marche.

👉 Le prompt et la marche à suivre détaillée sont dans **[INSTALL.md](INSTALL.md)**.

Tu n'as jamais installé Claude Code ou Codex ? INSTALL.md t'explique aussi ça, avant le prompt.

### 3. Choisis ton style (2 minutes)

Une fois installé, tape :

```
/setup
```

L'**Empreinte** commence par la seule chose qu'on ne peut pas deviner à ta place : **tes couleurs,
ta police et l'allure de tes sous-titres**. Tu choisis parmi 5 styles prêts, ou tu donnes tes
propres couleurs si tu les as déjà. **2 minutes, une seule fois.**

**Et si tu ne sais pas encore ?** Tu montes quand même. Le style de départ, « Papier », est en
noir et blanc : propre, lisible, ça rend bien tel quel. Tu fais ta première vidéo, tu vois le
système tourner, et tu choisis tes couleurs en connaissance de cause. **Rien n'est définitif** :
`/setup visuel` se relance à tout moment et tout le montage suit.

Ce qu'il ne faut pas faire, c'est le garder par défaut sans y penser. « Papier » ne contient
aucune couleur à toi — c'est un point de départ, pas une identité. Ce système ne te donne pas le
look de quelqu'un d'autre, il t'aide à poser le tien.

Le reste de l'Empreinte (ta voix, ton funnel, ta caméra, ta musique, le cadrage de ton visage)
est **optionnel** et se fait quand tu veux — mais c'est ce qui tire le résultat le plus haut.
Compte ~15 minutes en tout, et tu peux t'arrêter entre deux blocs.

---

## Comment on s'en sert ensuite

Le montage suit un **pipeline en 7 étapes**, dans l'ordre. Tu dis simplement à l'IA où tu en es :

1. **Script** — « on brainstorm un script » / « voici mon script ». L'IA l'écrit dans ta voix.
2. **Tournage** — tu tournes toi-même face caméra (export en **résolution MAX**), puis « voici la vidéo brute ».
3. **Dérush** — « coupe les blancs et les ratés, clean l'audio ». L'IA garde la meilleure prise de chaque phrase.
4. **Montage** — « passe au montage ». Split-screens, motion design, sous-titres.
5. **Tes retours** — « ça en plein écran », « mets cette vidéo ici », « les sous-titres vont pas ». Tu valides section par section.
6. **SFX + musique** — « mets le sound effect et la musique ». Uniquement une fois le montage validé.
7. **Publication** — « la légende », « le message DM ». La toute dernière étape.

Une règle d'or : **une étape à la fois, dans l'ordre**. L'IA ne saute pas devant.

---

## FAQ

**Faut-il savoir coder ?**
Non. Tu parles à ton IA en français. Elle écrit le code, toi tu regardes le résultat et tu donnes ton avis.

**Ça marche sur Windows ?**
Oui, Windows 10/11 64-bit. Mac Apple Silicon reste le plus confortable. INSTALL.md couvre les deux.

**Combien ça coûte ?**
Le repo est gratuit. Il te faut un abonnement IA — Claude Pro ou ChatGPT Plus, ~20 €/mois. C'est tout.

**Mes vidéos vont ressembler à celles des autres utilisateurs ?**
Non, et le système est construit pour l'empêcher. **Aucune couleur de marque n'est livrée** : les
couleurs, les polices et l'allure des sous-titres sont générées depuis ton `/setup`, et le style
de départ est volontairement en noir et blanc — beau, mais neutre, et il te le rappelle. Ce qui
est partagé, c'est la **méthode** : le rythme des coupes, le découpage des sous-titres, les safe
zones Instagram, les règles de motion. Ça, c'est ce que tu es venu chercher. Le reste est à toi.

**Je peux changer de style après avoir fait des vidéos ?**
Oui, sans rien casser. Les compositions ne contiennent aucune couleur en dur : tout passe par des
variables. Tu relances `/setup visuel`, et tes prochains montages sortent dans le nouveau style.

**Quel type de vidéos ?**
Un seul format : le Reel Instagram **talking-head vertical** (toi face caméra, 1080×1920).
Le système est réglé pour ça et le fait très bien.

**Claude Code ou Codex ?**
Les deux marchent. Claude Code va avec l'abonnement Claude Pro, Codex avec ChatGPT Plus.
Prends celui dont tu as déjà l'abonnement.

**Et si je bloque ?**
La [formation Monteur IA](https://www.lemondedumarketing.fr/monteur-ia) reprend chaque étape en vidéo.
Pour un souci technique du repo, ouvre une *issue* sur GitHub.
