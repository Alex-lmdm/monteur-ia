# Mettre à jour Monteur IA (tu l'as déjà installé)

Cette version range chaque Reel dans son propre dossier et, si tu veux, s'ouvre dans l'app gratuite
HyperFrames (Mac, Linux). Elle garde tout ce qui est à toi : tes réglages, ton style, ta voix, tes CTA, tes images,
musiques et sons, tes extensions, tes Reels. Rien de ce qui est à toi n'est effacé : un fichier du
moteur que tu avais retouché est d'abord sauvegardé.

1. Ouvre ton dossier Monteur IA dans Claude Code ou Codex, comme pour monter une vidéo.
2. Colle cette phrase :

```text
Mets Monteur IA à jour : suis https://github.com/Alex-lmdm/monteur-ia/blob/main/MISE-A-JOUR.md
```

3. Ton IA télécharge la nouvelle version et te montre ce qu'elle va faire, sans rien toucher.
   Réponds **« go »**.

Elle met ton dossier à jour, branche ton monteur sur l'app HyperFrames, puis met à jour tes
extensions. Tu as le Pack SFX ? C'est le seul geste à faire toi-même : le retélécharger depuis ta
formation (elle te dit où, au moment du « go »).

Tu as plusieurs dossiers Monteur IA, un par client ou par format ? Dis-le-lui : elle les met à jour
un par un.

Ton IA n'arrive pas à télécharger (Codex sans accès complet, réseau d'entreprise) ? Télécharge
toi-même [la nouvelle version](https://github.com/Alex-lmdm/monteur-ia/archive/refs/heads/main.zip)
dans Téléchargements, puis dis-lui « elle est dans Téléchargements ».

---

## Instructions pour l'IA

Tu mets à jour un dossier Monteur IA existant. Parle au client dans sa langue, simplement, en
résultats (« tes réglages sont gardés »), jamais en chemins de fichiers sauf s'il le demande. Pas de
tiret long dans tes messages.

**Règles.**

- Tu lis peut-être ce fichier sur GitHub : fais l'étape 1, puis relis le `MISE-A-JOUR.md` de la
  version téléchargée. C'est lui qui fait foi pour la suite.
- Le moteur se met à jour uniquement par `scripts/mettre-a-jour.mjs` de la NOUVELLE version : jamais
  de copie, de déplacement ou de suppression à la main dans le dossier du client. Seule exception,
  les extensions (étape 6) : elles s'installent comme leur `INSTALL.md` le décrit.
- Rien n'est appliqué avant que le client ait vu le plan et répondu « go ». Ce « go » vaut pour
  tout ce que tu as annoncé (mise à jour, branchement de l'app, extensions) : ne redemande pas son
  accord à chaque étape.
- Plusieurs dossiers Monteur IA : un seul message de plan qui les présente tous, un seul « go »
  pour tous, puis la mise à jour de chacun, l'un après l'autre, et une seule conclusion.

### 1. Télécharger la nouvelle version

Toujours dans un dossier temporaire neuf, jamais dans le dossier du client. Crée-le (même commande
sur Mac, Linux et Windows) :

```bash
node -p "require('fs').mkdtempSync(require('path').join(require('os').tmpdir(), 'monteur-ia-'))"
```

Le dossier affiché est `TMP`. Télécharge et décompresse dedans (Mac, Linux, Git Bash) :

```bash
cd "<TMP>" && curl -fL -o monteur-ia.tar.gz https://github.com/Alex-lmdm/monteur-ia/archive/refs/heads/main.tar.gz && tar -xzf monteur-ia.tar.gz
```

Sous PowerShell :

```powershell
cd "<TMP>"; curl.exe -fL -o monteur-ia.tar.gz https://github.com/Alex-lmdm/monteur-ia/archive/refs/heads/main.tar.gz; tar -xzf monteur-ia.tar.gz
```

`NEUF` = `<TMP>/monteur-ia-main`. Vérifie que `NEUF/scripts/mettre-a-jour.mjs` existe.

Le téléchargement échoue (pas d'accès au réseau, proxy) : au plus deux nouvelles tentatives, puis
demande au client de télécharger https://github.com/Alex-lmdm/monteur-ia/archive/refs/heads/main.zip
dans Téléchargements. Un ZIP se décompresse dans `TMP` : `python3 -m zipfile -e "<ZIP>" "<TMP>"`
(Windows : `python`). Un dossier déjà décompressé par le navigateur convient aussi. Dans les deux
cas, le bon dossier contient `scripts/mettre-a-jour.mjs` : un `monteur-ia-main` sans ce fichier est
une ancienne version (souvent celle de sa première installation), ne t'en sers pas.

### 2. Repérer le dossier du client

`CLIENT` = le dossier ouvert s'il contient `templates/AGENT.md.tpl`, sinon demande-lui où est son
dossier Monteur IA. S'il en a plusieurs, fais la liste avec lui : les étapes 3 et 4 se font pour
chacun, avec le même `NEUF` (étape 3 : un plan par dossier, dans le même message).

### 3. Montrer le plan, à blanc, et demander « go »

```bash
node "<NEUF>/scripts/mettre-a-jour.mjs" "<CLIENT>"
node "<NEUF>/scripts/app-hyperframes.mjs" etat
```

Puis un seul message, court :

- ce qui change : le moteur, chaque Reel dans son propre dossier, l'app HyperFrames ;
- ce qui est gardé, et que chaque fichier du moteur remplacé est sauvegardé ;
- s'il y a un **Reel en cours** : le nom qu'il aura dans l'app (le plan l'affiche), avec un sujet
  lisible en deux ou trois mots à la place de celui que le plan devine depuis ses coupes (`melies`
  devient « Méliès ») ; il peut corriger sujet et date dans sa réponse. Si le plan dit seulement
  « Reel en cours », demande-lui le sujet en même temps que le « go » ;
- ce que `etat` dit « à brancher » (Claude Code, Codex, ou les deux) : « je règle aussi <celui-là>
  pour qu'il lise les consignes de ton monteur dans l'app, ton réglage actuel est sauvegardé » ;
- les extensions « à mettre à jour ensuite » : leurs réglages sont gardés. Pour le **Pack SFX**,
  demande-lui de le retélécharger pendant la mise à jour : dans sa formation, module Pack SFX,
  leçon « Installe ton Pack SFX », bouton jaune ; le fichier arrive dans Téléchargements (s'il a
  gardé l'ancien, le nouveau s'appelle `pack-sfx (1).zip` : c'est normal, tu prendras le bon) ;
- termine par : **« Réponds “go” pour lancer la mise à jour. »**

Le plan dit « Déjà à jour » : dis-le-lui et passe à l'étape 7. Il dit « Moteur déjà à jour » avec
des extensions à mettre à jour : annonce-les, puis, après son « go », passe à l'étape 6.

### 4. Appliquer

```bash
node "<NEUF>/scripts/mettre-a-jour.mjs" "<CLIENT>" --appliquer --sujet "<sujet>" --date AAAA-MM-JJ
```

`--sujet` et `--date` ne servent que s'il y a un Reel en cours. La commande remplace le moteur,
déplace le Reel en cours dans `reels/`, régénère son montage pour l'export natif, crée l'accueil,
puis installe la version de HyperFrames de l'app (`npm install`, une à deux minutes). Interrompue,
elle reprend là où elle s'est arrêtée si tu relances exactement la même commande.

- Une ligne ⚠️ ou un « Reste à faire » dans `work/MIGRATION.md` du Reel déplacé : traite-le avec le
  client avant de passer à la suite (les versions d'origine sont dans `work/migration-v1/`). Seule
  la ligne « sons » du Pack SFX attend l'étape 6.
- « contrôle HyperFrames (lint) : à revoir » : corrige dans le Reel chaque erreur affichée, puis
  relance `npx hyperframes lint "<dossier du Reel>"` depuis `CLIENT` jusqu'à zéro erreur. Un fichier
  manquant (`missing_local_asset`) est souvent dans les `assets/` de `CLIENT` : copie-le au même
  chemin dans le Reel (l'original reste où il est).
- Fichiers du moteur qu'il avait retouchés (le plan les liste, `templates/AGENT.md.tpl` et les
  fichiers à zones compris) : compare sa version (dans la sauvegarde) à la nouvelle et dis-lui en
  une phrase ce qu'il avait changé. Une note ou un commentaire : dis-le, sans question. Un vrai
  réglage : propose de le reporter, avec ses mots à lui, là où les mises à jour le gardent, jamais
  dans un fichier du moteur (il serait remplacé à la prochaine) :
  - une consigne pour l'IA : à la fin de `templates/AGENT.md.tpl`, entre
    `<!-- BEGIN EXTENSION: consignes-perso -->` et `<!-- END EXTENSION: consignes-perso -->`, puis
    `node scripts/sync.mjs` ;
  - une préférence de montage : `montage.preferences` de `brand.config.json`, puis
    `node scripts/sync.mjs` ;
  - un texte de CTA ou de voix : la zone `BEGIN GENERATED` de son fichier.
- Relance le plan à blanc : il doit dire « Déjà à jour » ou « Moteur déjà à jour ».

### 5. Brancher l'app HyperFrames (une fois par ordinateur)

Depuis `CLIENT`, même si `etat` disait déjà « branché » (la commande ne change alors rien) :

```bash
node scripts/app-hyperframes.mjs brancher
```

### 6. Mettre à jour les extensions

Une par une, celles que le plan disait « à mettre à jour ensuite ». Leurs réglages sont gardés : ne
relance pas leur setup (`/setup-double-ia`, `/setup-stories`). Leur `INSTALL.md` finit par une
invitation au setup ou un tableau récapitulatif : saute-les, tu conclus une seule fois, à l'étape 8.

**Ton Double IA, Système Stories** (publiques) : télécharge-les dans `TMP` comme à l'étape 1, avec
leur adresse :

```bash
cd "<TMP>" && curl -fL -o double-ia.tar.gz https://github.com/Alex-lmdm/double-ia/archive/refs/heads/main.tar.gz && tar -xzf double-ia.tar.gz
cd "<TMP>" && curl -fL -o systeme-stories.tar.gz https://github.com/Alex-lmdm/systeme-stories/archive/refs/heads/main.tar.gz && tar -xzf systeme-stories.tar.gz
```

Puis, depuis `CLIENT`, suis le bloc « Le prompt d'installation » de leur `INSTALL.md`
(`<TMP>/double-ia-main/INSTALL.md`, `<TMP>/systeme-stories-main/INSTALL.md`), avec ce dossier
comme dossier de l'extension (pas besoin d'un autre dossier temporaire).

**Pack SFX** (privé : jamais sur GitHub) : suis l'`INSTALL.md` du pack, qui le trouve dans
Téléchargements. Avant d'installer, vérifie que le `VERSION` du pack décompressé est au moins celle
que le plan demandait : sinon c'est l'ancien fichier, redemande-lui le téléchargement (formation,
module Pack SFX, leçon « Installe ton Pack SFX », bouton jaune). S'il ne peut pas le faire
maintenant : d'ici là, les sons du pack se posent encore à l'ancienne (vidéo finale sortie depuis la
conversation, pas par le bouton Export de l'app) ; il lui suffira de redire la phrase de mise à jour
quand il aura le fichier.

Pack SFX à jour et, dans `work/MIGRATION.md` du Reel déplacé, une ligne « sons » sous « Reste à
faire » : lance `python3 tools/sfx_mix.py` (Windows : `python`) depuis le dossier de ce Reel. Sa liste
de sons a suivi le Reel ; cette commande remet ses sons dans le montage (sans elle, l'export de
l'app sortirait sans sons).

Relance enfin le plan à blanc : plus aucune extension « à mettre à jour ensuite ».

### 7. L'app HyperFrames (Mac, Linux)

- Pas encore installée (`etat`) : https://hyperframes.dev/studio. Au premier lancement (même
  installée mais jamais ouverte), elle demande « Continue with HeyGen » : une connexion gratuite,
  rien à payer.
- Ouvre-lui l'accueil (le dossier de `CLIENT` dont le nom commence par `Accueil` : `Accueil · <nom>`,
  ou `Accueil Monteur IA` pour un dossier au nom par défaut), puis le Reel déplacé s'il y en a un, avec
  leur chemin complet entre guillemets :
  `node scripts/app-hyperframes.mjs ouvrir "<CLIENT>/Accueil · <nom>"`. Sans l'app ou si la
  commande échoue, il glisse ce dossier sur l'icône de l'app.
- Au premier message dans l'app, elle propose de connecter Claude Code (Codex : Settings > Agent).
- Son ancien dossier Monteur IA était ouvert dans l'app ? Il archive cette tuile (menu de la tuile
  > Archive) : ce dossier n'est plus un projet, ses Reels le sont.
- Pour une variante d'un Reel, c'est à toi de la créer (`tools/nouveau_reel.py --depuis`) : le
  bouton Duplicate de l'app copie le Reel hors du dossier Monteur IA, sans ses réglages ni ses sons.
- Windows : pas encore d'app. Tout marche comme avant dans Claude Code ou Codex, chaque Reel dans
  son dossier `reels/`.

### 8. Conclure

Dis-lui en clair :

- ses Reels sont dans `reels/` (un dossier par Reel, c'est ce que l'app affiche) ;
- les vidéos finales d'un Reel déplacé portent le suffixe `-avant-mise-a-jour` : un nouvel export
  ne les écrase pas ;
- la sauvegarde (dossier `.sauvegarde-mise-a-jour-<date>`, caché : Cmd+Maj+point dans le Finder
  pour le voir, Affichage > Éléments masqués sous Windows) peut être supprimée quand tout marche
  depuis quelques semaines ;
- si son dossier Monteur IA est dans Documents ou sur le Bureau (souvent synchronisés avec iCloud
  ou OneDrive, ce qui ralentit le montage), il gagne à le ranger dans Vidéos, dans le Finder, app
  et conversation fermées. Ensuite, dans l'app : il archive les tuiles de l'ancien emplacement
  (menu de la tuile > Archive) et glisse le dossier « Accueil · … » du nouvel emplacement sur
  l'icône de l'app.

Supprime enfin le dossier temporaire `TMP`. La commande refuse tout autre dossier qu'un
`monteur-ia-…` du dossier temporaire du système :

```bash
node -e "const f = require('fs'), p = require('path'), t = f.realpathSync(process.argv[1]), r = p.relative(f.realpathSync(require('os').tmpdir()), t); if (r !== p.basename(t) || !r.startsWith('monteur-ia-')) { console.error('Refusé, pas le dossier temporaire de la mise à jour : ' + t); process.exit(1); } f.rmSync(t, { recursive: true, force: true });" "<TMP>"
```

S'il avait téléchargé la nouvelle version lui-même, il peut supprimer ce téléchargement.

**Retour arrière.** Les fichiers d'origine du moteur sont dans
`.sauvegarde-mise-a-jour-<date>/moteur/`, le plan de travail d'essai éventuel dans
`.sauvegarde-mise-a-jour-<date>/plan-de-travail/`. En cas de doute, ne lance aucune commande qui
efface : décris le problème au client et propose un message court pour le support de la formation.
