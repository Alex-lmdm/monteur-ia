# Monteur IA : monte tes Reels en langage naturel

Tu tournes ta vidéo face caméra. Ton IA fait le montage : elle coupe les blancs et les ratés,
pose le motion design, cale les sous-titres, ajoute les SFX et la musique.
Toi, tu fais tes retours en français (« ça en plein écran », « mets cette image ici ») et elle refait.

Pas besoin de savoir coder. Tu parles à ton IA comme à un monteur.

---

Ce repo accompagne la formation **[Monteur IA](https://www.lemondedumarketing.fr/monteur-ia)**.
La formation te montre chaque étape en vidéo, pas-à-pas. Le repo s'utilise aussi seul si tu es déjà à l'aise
avec Claude Code ou Codex.

**Tu utilises déjà Monteur IA ?** Pour passer à cette version (un dossier par Reel, l'app gratuite HyperFrames en option),
ouvre ton dossier Monteur IA dans Claude Code ou Codex et colle cette phrase :

```text
Mets Monteur IA à jour : suis https://github.com/Alex-lmdm/monteur-ia/blob/main/MISE-A-JOUR.md
```

Ton IA te montre ce qu'elle va faire, tu réponds « go ». Tes réglages, ta voix, tes sons et tes
extensions sont gardés ([détails](MISE-A-JOUR.md)).

---

## Ce que tu obtiens

Un système de montage complet pour un seul format : le **Reel Instagram talking-head vertical**
(1080×1920, 30 fps), c'est-à-dire ta vraie vidéo face caméra, avec du motion design par-dessus,
section par section.

Le montage se pilote en conversation. Tu ne touches pas une ligne de code : tu écris ce que tu veux,
l'IA le fait, tu valides ou tu corriges. Sur Mac et Linux, l'**app HyperFrames** (gratuite) te montre
en plus ton montage sur une timeline, comme un logiciel de montage : tu le regardes, tu retouches à
la souris si tu veux, et tu exportes d'un clic.

---

## Démarrage en 3 étapes

### 1. Vérifie que ta machine est prête

| | Minimum | Conseillé |
|---|---|---|
| **Ordinateur** | Mac (Apple Silicon M1+, macOS 13+), Windows 10/11 64-bit ou Linux 64-bit | Mac Apple Silicon |
| **Mémoire (RAM)** | 8 Go | 16 Go |
| **Disque libre** | ~10 Go | 20 Go |
| **Abonnement IA** | Claude Pro **ou** ChatGPT Plus (~20 €/mois) | |

L'abonnement IA (~20 €/mois) est **le seul coût**. Tout le reste du système est gratuit et open source
(Node.js, ffmpeg, Whisper, HyperFrames), l'app HyperFrames comprise.

### 2. Installe le système

Range le dossier dézippé **monteur-ia-main** dans ton dossier **Vidéos**, pas dans Documents ni sur
le Bureau : ils sont souvent synchronisés avec iCloud ou OneDrive, ce qui ralentit le montage.
Ouvre-le ensuite dans Claude Code ou Codex, puis écris :

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

## Un dossier par Reel

Chaque vidéo a son propre dossier dans `reels/`, nommé `<sujet> · <date> · <marque>`. Le monteur
le crée quand tu lui envoies une nouvelle vidéo. Tes Reels restent côte à côte : tu peux reprendre
n'importe lequel, et un nouveau Reel ne touche jamais aux précédents.

- **Reprendre un Reel** : « on reprend le Reel Méliès ».
- **Faire une variante** : « fais une variante de ce Reel » (même montage, nouveau dossier).
- **Ranger un Reel publié** : « range ce Reel ». Sa vidéo finale est copiée dans
  `Vidéos/reels-publies/`, et le monteur te propose de libérer la place des rushes.

---

## Monter et retoucher dans l'app HyperFrames (Mac, Linux)

L'app HyperFrames Studio utilise ton abonnement Claude ou ChatGPT : c'est le même monteur, avec une
timeline en plus. Rien d'obligatoire, tout reste faisable dans Claude Code ou Codex.

1. **Installe l'app** depuis [hyperframes.dev/studio](https://hyperframes.dev/studio), puis
   « Continue with HeyGen » pour te connecter.
2. **Branche ton monteur** (une fois par ordinateur) : l'installation de Monteur IA s'en charge.
   Sinon, demande à ton IA « branche Monteur IA sur l'app HyperFrames ».
3. **Ouvre l'accueil** : glisse le dossier « Accueil … » de ton dossier Monteur IA sur l'icône de
   l'app (ou Fichier > Ouvrir un dossier). Au premier message, l'app te propose de connecter
   Claude Code (pour Codex : Settings > Agent).
4. **Nouvelle vidéo** : dans l'accueil, glisse ta vidéo brute et écris « On monte celle-ci ». Le
   monteur crée le Reel et l'ouvre dans l'app. Il montre d'abord un modèle : ta vidéo y entre au dérush.
   Écris-lui la même phrase dans ce Reel. Pas encore filmé ? Écris « écris-moi un script sur… » dans
   l'accueil : il crée le Reel, tu l'ouvres, tu écris « On y va » et le script s'écrit dedans ; après
   le tournage, glisse la vidéo dans ce même Reel.
5. **Retouches** : en le demandant au monteur, comme d'habitude, ou à la souris sur la timeline
   (déplacer un plan, un son, régler un volume).
6. **Export** : le bouton **Export** sort la vidéo finale complète, sons et musique compris.

**Tout part de l'accueil.** Le bouton **New project** et le champ « Make something. » de l'app
créent un projet hors de ton dossier Monteur IA : ton monteur n'y est pas, l'IA qui répond ne connaît
ni ton style ni tes sons. Dans l'app, n'utilise pas non plus le bouton **Duplicate** sur un Reel : la
copie sortirait de ton dossier Monteur IA, sans tes réglages ni tes sons. Demande une variante au
monteur. Pour cacher un Reel de la liste : **Archive**.

---

## Comment on s'en sert ensuite

Le montage suit un **pipeline en 7 étapes**, dans l'ordre. Tu dis simplement à l'IA où tu en es :

1. **Script** : « on brainstorm un script » / « voici mon script ». L'IA l'écrit dans ta voix.
2. **Tournage** : tu tournes toi-même face caméra (export en **résolution MAX**), puis « voici la vidéo brute ».
3. **Dérush** : « coupe les blancs et les ratés, clean l'audio ». L'IA garde la meilleure prise de chaque phrase.
4. **Montage** : « passe au montage ». Split-screens, motion design, sous-titres.
5. **Tes retours** : « ça en plein écran », « mets cette vidéo ici », « les sous-titres vont pas ». Tu valides section par section.
6. **SFX + musique** : « mets le sound effect et la musique ». Uniquement une fois le montage validé.
7. **Publication** : « la légende », « le message DM ». La toute dernière étape.

Une règle d'or : **une étape à la fois, dans l'ordre**. L'IA ne saute pas devant.

---

## FAQ

**Faut-il savoir coder ?**
Non. Tu parles à ton IA en français. Elle écrit le code, toi tu regardes le résultat et tu donnes ton avis.

**Ça marche sur Windows ?**
Oui, Windows 10/11 64-bit, dans Claude Code ou Codex. L'app HyperFrames n'existe pas encore sous
Windows : tu montes et tu exportes depuis la conversation. INSTALL.md couvre les deux systèmes.

**Combien ça coûte ?**
Le repo est gratuit, l'app HyperFrames aussi. Il te faut un abonnement IA : Claude Pro ou ChatGPT
Plus, ~20 €/mois. C'est tout.

**J'ai plusieurs clients ou plusieurs formats.**
Fais une copie du dossier Monteur IA par client ou par format (« Monteur IA - Client A »…), chacune
avec son style et ses Reels. Dans l'app, ouvre l'accueil de chaque copie : les noms de ses Reels
finissent par la marque du client.

**Mes vidéos vont ressembler à celles des autres utilisateurs ?**
Non, et le système est construit pour l'empêcher. **Aucune couleur de marque n'est livrée** : les
couleurs, les polices et l'allure des sous-titres sont générées depuis ton `/setup`, et le style
de départ est volontairement en noir et blanc : beau, mais neutre, et il te le rappelle. Ce qui
est partagé, c'est la **méthode** : le rythme des coupes, le découpage des sous-titres, les safe
zones Instagram, les règles de motion. Ça, c'est ce que tu es venu chercher. Le reste est à toi.

**Je peux changer de style après avoir fait des vidéos ?**
Oui, sans rien casser. Les compositions ne contiennent aucune couleur en dur : tout passe par des
variables. Tu relances `/setup visuel`, et tes prochains montages sortent dans le nouveau style.
Un Reel déjà publié garde le sien.

**Quel type de vidéos ?**
Un seul format : le Reel Instagram **talking-head vertical** (toi face caméra, 1080×1920).
Le système est réglé pour ça et le fait très bien.

**Claude Code ou Codex ?**
Les deux marchent, dans la conversation comme dans l'app. Claude Code va avec l'abonnement Claude
Pro, Codex avec ChatGPT Plus. Prends celui dont tu as déjà l'abonnement.

**Et si je bloque ?**
La [formation Monteur IA](https://www.lemondedumarketing.fr/monteur-ia) reprend chaque étape en vidéo.
Dis à ton IA ce qui bloque ; elle doit te guider pour la prochaine étape. Si elle ne peut pas
résoudre le problème, demande-lui un message de diagnostic court à transmettre au support de la
formation, avec une capture. Pas besoin de créer un compte GitHub.
