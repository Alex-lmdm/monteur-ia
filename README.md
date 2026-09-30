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

Ouvre le dossier **monteur-ia-main** dans Claude Code ou Codex, puis écris :

```text
Lis INSTALL.md et accompagne-moi pour installer Monteur IA. Occupe-toi de la partie technique.
```

L'IA vérifie ton ordinateur et affiche un petit bilan. **« À installer » n'est pas une erreur.**
Quand elle te le propose, réponds simplement **« go » dans la conversation** : elle exécute les
commandes et vérifie le résultat. Si une étape doit être faite à la main (par exemple installer
Node.js), elle te guide puis reprend la suite.

Les menus et les messages peuvent différer de la vidéo de formation : ils s'adaptent à ton
ordinateur. Tu n'as pas de commandes à recopier depuis sa réponse.

Pas encore d'agent ? Voir [INSTALL.md](INSTALL.md#installer-lagent-ia-avant-tout).

### 3. Monte ta première vidéo

Quand l'installation est vérifiée, **glisse ta vidéo brute dans la conversation** et écris :

```text
On monte celle-ci.
```

**Pour cette première vidéo, le monteur fait tout, sans te poser de questions** : coupes,
sous-titres, animations, bruitages, avec des réglages de base (habillage noir et blanc, **ta
vidéo reste en couleur**). Ça prend un moment : tu peux faire autre chose en attendant.

Ensuite vient le **débrief** : tu regardes ta vidéo et tu lui dis tout ce que tu aurais fait
autrement. Coupes, visage en grand ou non, type d'animations, sous-titres, couleurs, musique :
tout se règle, même en vrac ou en vocal. Il corrige la vidéo, te résume ce qu'il a retenu, et
**tes vidéos suivantes sont montées directement comme tu aimes.**

Tu peux aussi personnaliser avant, ou à tout moment : dis **« personnalise mon style »**
(ou `/setup`). Le reste de l'Empreinte (ta voix pour écrire tes scripts, ton funnel…) est optionnel.

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
Dis à ton IA ce qui bloque ; elle doit te guider pour la prochaine étape. Si elle ne peut pas
résoudre le problème, demande-lui un message de diagnostic court à transmettre au support de la
formation, avec une capture. Pas besoin de créer un compte GitHub.
