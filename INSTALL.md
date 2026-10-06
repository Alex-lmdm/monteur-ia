# Installer Monteur IA

Range d'abord le dossier dézippé **monteur-ia-main** dans ton dossier **Vidéos** (Movies sur Mac,
Videos sur Windows). Évite Documents et le Bureau : sur beaucoup d'ordinateurs, ils sont
synchronisés avec iCloud ou OneDrive, qui retirent les fichiers du disque pour faire de la place,
et chaque montage attend alors que tes rushes redescendent.

Ouvre ensuite le dossier **monteur-ia-main** dans Claude Code ou Codex, puis envoie ce message :

```text
Lis INSTALL.md et accompagne-moi pour installer Monteur IA. Occupe-toi de la partie technique.
```

C'est le même départ si la vidéo de formation dit simplement « lis INSTALL.md et installe tout ».
L'IA vérifie ton ordinateur, explique ce qu'il reste à préparer, puis te dit quoi faire.
**Quand elle te propose de commencer, réponds « go » dans la conversation.**

- **À installer** signifie que l'outil n'est pas encore présent. Ce n'est pas une erreur.
- L'IA exécute les commandes. Tu n'as pas à les recopier dans un terminal.
- Si une manipulation est nécessaire de ton côté, elle te guide pour cette seule étape.
- Les menus et les réponses peuvent différer de la vidéo : l'installation s'adapte à ton ordinateur.

Une fois les vérifications terminées, **envoie ta première vidéo brute** : l'IA la monte en entier
avec des réglages de base (habillage noir et blanc, ta vidéo reste en couleur), sans questionnaire.
Tu lui dis ensuite ce que tu aurais fait autrement, et elle retient ton style pour les suivantes.

**Pas encore d'agent installé ?** Commence par [Installer l'agent IA](#installer-lagent-ia-avant-tout).

**L'app HyperFrames (Mac, Linux) vient ensuite.** L'installation se fait ici, dans Claude Code ou
Codex ; elle branche aussi ton monteur sur l'app. Tu ouvres ensuite l'accueil de Monteur IA dans
l'app pour monter avec une timeline (voir le [README](README.md#monter-et-retoucher-dans-lapp-hyperframes-mac-linux)).

**Pas encore le dossier ?** Dans ton dossier Vidéos, demande à ton agent :
« Télécharge https://github.com/Alex-lmdm/monteur-ia ici, puis lis son INSTALL.md et aide-moi à l'installer. »
Il doit te guider pour rouvrir le dossier téléchargé si nécessaire.

---

## Instructions pour l'IA : accompagner l'installation

**Langue :** accompagne l'utilisateur dans la langue qu'il demande ou utilise, y compris
l'espagnol. Traduis les explications et les exemples de réponses, jamais les commandes ni
les noms de fichiers. Sa langue de conversation ne change pas automatiquement la langue de
ses vidéos : configure `brand.language` et `derush.whisperLanguage` selon sa demande ou
l'audio réel. Le français des exemples ci-dessous n'est pas imposé au client.

Cette section est ton mode opératoire. **Applique-la aussi quand l'utilisateur dit seulement
« lis INSTALL.md et installe tout »** : il n'a pas à recopier un autre prompt.
Le protocole technique plus bas est destiné à toi. Ne le transforme pas en tutoriel terminal
pour l'utilisateur et ne lui demande pas de le lire.

### 1. Vérifier, expliquer simplement, proposer de commencer

- Détecte le système et l'architecture, vérifie le dossier et les outils présents en lecture seule.
  Distingue un outil absent d'un outil présent mais non fonctionnel. Ne change rien à cette étape.
- Commence par un constat réel et rassurant, sans garantir à l'avance que tout réussira.
- Présente un tableau court avec des **fonctions compréhensibles** : base du système (Node.js),
  outils du monteur (Python), traitement vidéo, moteur de montage, export vidéo, transcription,
  réglages du projet.
  États : **✅ Déjà prêt**, **À installer**, **À préparer**. Réserve **À réparer** aux échecs constatés.
  Pas de croix rouges pour une absence normale avant l'installation.
- Pas de liste de commandes, chemins, noms de paquets ou choix de modèles dans ce premier message.
  Les outils de l'application peuvent afficher leurs propres commandes : explique au besoin
  « ce sont les opérations que j'exécute, tu n'as rien à recopier ».
- Choisis toi-même la méthode compatible avec la machine. Propose un réglage recommandé,
  sans faire arbitrer « Homebrew ou binaire », « large-v3-turbo ou medium » à un débutant.
- Annonce les interventions prévisibles et les téléchargements volumineux AVANT le « go ».
  Si Homebrew est absent et nécessaire, explique sa fonction et inclus explicitement son
  installation dans ce qui est autorisé. Le modèle de transcription recommandé pèse environ
  1,6 Go **s'il manque**. S'il existe déjà, ne propose pas de le télécharger à nouveau.
- Termine par **une action unique**, très visible. « Go », « oui », « vas-y », « lance » valent
  accord pour le plan annoncé ; ne redemande pas ensuite l'accord pour chacune de ses étapes.
  Une nouvelle action système non annoncée ou une permission de l'application reste à valider.

Exemple de formulation, à adapter au bilan réel :

> J'ai vérifié ton ordinateur : une partie des outils est déjà prête 😊
>
> [Tableau du bilan réel]
>
> Je vais installer ce qui manque et vérifier que le montage et les sous-titres fonctionnent.
> Je m'occupe des commandes, tu n'as rien à recopier dans un terminal.
>
> La transcription nécessite un téléchargement d'environ 1,6 Go. Garde ton ordinateur connecté.
> Si ta connexion est limitée, dis-le-moi : je pourrai choisir une version plus légère.
>
> **Pour commencer, réponds simplement « go » ici.**

**Exception Node.js absent ou trop ancien :** c'est la prochaine action, donc ne demande pas
« go » pour t'arrêter aussitôt. Dis : « Il manque Node.js, un outil gratuit nécessaire au montage.
Cette étape se fait manuellement ; je te guide, puis je m'occupe de la suite. » Donne le lien
https://nodejs.org et indique l'installeur LTS adapté au système (.pkg sur Mac, .msi sur Windows).
Demande de terminer l'installation puis de fermer et rouvrir l'agent dans le même dossier.
**« Quand c'est fait, écris “c'est installé”. »** Re-vérifie, reprends au bon endroit et demande
l'accord pour les étapes restantes si elles n'ont pas encore été autorisées. Ne fais pas recopier
le prompt ou tout recommencer.

### 2. Pendant l'installation : toujours dire qui agit

- Exécute toi-même les commandes. Donne des nouvelles aux étapes utiles, en une ou deux phrases :
  « Je prépare l'export vidéo. Tu n'as rien à faire pour le moment. »
- Un téléchargement lent : précise ce qui attend, sans inventer un pourcentage ni un délai.
- Une autorisation système : explique le bouton ou la manipulation nécessaire, puis attends.
  Un mot de passe système se saisit uniquement dans la fenêtre du système, jamais dans le chat.
- Ne propose pas de désactiver les protections du système ni l'antivirus. Le mode bypass de
  l'application, lui, est recommandé par la formation (section « Les demandes d'autorisation »).
- Un échec réparable : explique « Cette étape n'a pas abouti. Je vérifie la cause avant de reprendre. »
  Diagnostique et corrige de façon ciblée, avec au plus deux nouvelles tentatives adaptées.
  Ne relance pas en boucle et ne passe pas à l'étape suivante en masquant l'erreur.
- Si l'utilisateur doit agir : une explication courte, **une seule action concrète**, puis reprise
  après sa réponse. Ne le renvoie pas seul vers toute l'installation manuelle.
- Si tu restes bloqué : indique ce qui est prêt, ce qui bloque et fournis un court message à
  transmettre au support (étape, erreur utile, système ; aucun secret). Garde les détails techniques
  disponibles sur demande, sans en remplir la conversation.

### 3. Protocole technique à exécuter

Procède par étapes idempotentes : vérifier, installer uniquement si nécessaire, re-vérifier.
Préserve les vidéos, les réglages personnels et les outils déjà fonctionnels. Ne mets pas à jour
la version HyperFrames épinglée dans ce projet pendant l'installation.

0. **Emplacement** : si le dossier est dans Documents, sur le Bureau ou dans un dossier iCloud
   Drive ou OneDrive, recommande de le ranger dans Vidéos avant d'installer : ces dossiers sont
   souvent synchronisés, et une synchronisation qui retire les rushes du disque ralentit chaque
   montage. Le déplacement se fait dans le Finder (ou l'Explorateur), agent fermé, puis on rouvre
   le dossier au nouvel endroit. S'il préfère rester où il est, continue.

1. **Node.js 22 minimum** : `node --version`. Absent ou trop ancien : appliquer l'exception ci-dessus.
   Ne pas tenter de l'installer via un gestionnaire de paquets.
1 bis. **Python 3.9 minimum** (les outils du monteur sont des scripts Python) :
   - macOS : `python3 --version`. S'il manque, le Mac propose d'installer les « outils de
     développement en ligne de commande » : c'est la bonne réponse (Homebrew les installe aussi).
   - Windows : `python --version`, sinon `py --version`. Absent, ou une fenêtre du Microsoft Store
     s'ouvre : `winget install -e --id Python.Python.3.12`, puis rouvrir l'agent (PATH). Sous
     Windows, les commandes `python3` des consignes s'écrivent `python` (ou `py`).
   - **Pillow** (mesure des sous-titres, contrôle de l'export) : `python3 -c "import PIL"`. Absent :
     `python3 -m pip install --user pillow` (Windows : `python -m pip install pillow`). Refusé avec
     « externally-managed-environment » (Python de Homebrew) : `brew install pillow`.
2. **Dépendances** : `npm install` à la racine du projet.
3. **Navigateur de rendu** : `npx hyperframes browser ensure` (garde un navigateur déjà là, sinon
   télécharge celui du rendu, environ 400 Mo une fois installé : à annoncer avant le « go » s'il
   manque, `npx hyperframes browser path` le dit en lecture seule). Jamais `npx puppeteer browsers
   install` : il tire en plus un Chrome complet, plus de 500 Mo pour rien.
4. **FFmpeg** : vérifier `ffmpeg -version` et `ffprobe -version`.
   - macOS : `brew install ffmpeg` si nécessaire. Si Homebrew manque, vérifier que son installation
     a été explicitement annoncée et autorisée ; sinon expliquer et demander cet accord.
   - Windows : `winget install Gyan.FFmpeg`. Après installation, rouvrir l'agent si son environnement
     ne voit pas le nouveau PATH. Si winget manque, guider pour mettre à jour App Installer depuis
     le Microsoft Store, puis reprendre cette étape.
5. **Whisper** : vérifier `whisper-cli` (macOS : `command -v whisper-cli` ; PowerShell :
   `Get-Command whisper-cli -ErrorAction SilentlyContinue`) et les modèles `ggml-*.bin` dans
   `~/.cache/monteur-ia/whisper/`, `~/.cache/hyperframes/whisper/models/`, `~/whisper-models/` et
   `~/.cache/whisper/`.
   - Garder un binaire et un modèle déjà fonctionnels, même si le modèle diffère du défaut recommandé.
   - macOS : privilégier `brew install whisper.cpp` avec Homebrew déjà disponible/autorisé.
     Vérifier la disponibilité de la formule ([source Homebrew](https://formulae.brew.sh/formula/whisper.cpp), ancien nom : `whisper-cpp`) ; ne pas promettre un binaire GitHub macOS sans
     avoir vérifié qu'il existe réellement pour cette architecture.
   - Windows : récupérer le binaire whisper.cpp compatible avec la machine dans les releases
     officielles `ggml-org/whisper.cpp` ; vérifier la présence réelle de l'archive attendue.
   - Modèle manquant : `ggml-large-v3-turbo.bin` (~1,6 Go), après l'annonce initiale. Si la connexion
     est limitée, proposer une alternative plus petite en vérifiant sa taille réelle : `medium`
     pèse encore environ 1,6 Go, ce n'est pas une solution nettement plus légère ; `small` environ
     0,5 Go. Expliquer le compromis de précision en français courant.
   - Stocker les nouveaux fichiers dans `~/.cache/monteur-ia/whisper/` (Windows : sous
     `%USERPROFILE%`). Rechercher les chemins réels après l'installation.
6. **Configuration** : créer `brand.config.json` depuis `brand.config.example.json` seulement s'il
   manque. Compléter les chemins réellement détectés dans `env`, sans écraser la personnalisation.
   Sous Windows, appliquer `PRODUCER_FORCE_SCREENSHOT=true` pour le rendu si nécessaire.
7. **Instructions et skills** : `npm run sync` (déjà lancé par `npm install`, le relancer ne coûte rien).
   Les skills sont livrés avec le système, à la version de HyperFrames épinglée : ne lance pas
   `npx hyperframes skills update`, qui installerait d'autres skills dans la configuration personnelle
   de Claude Code et de Codex (tous ses projets) au lieu de mettre à jour ceux du dossier.
   Une erreur de `npm run sync` reste bloquante.
8. **Branchement** : `node scripts/app-hyperframes.mjs brancher`, sur toutes les machines. Il permet
   à l'app HyperFrames de lire les consignes du monteur (réglage de Claude Code) et à Codex de les
   lire en entier (limite de lecture relevée). Il écrit dans la configuration personnelle de
   Claude Code et de Codex, avec une sauvegarde : l'annoncer dans le plan, avant le « go ».

### 4. Vérifier avant d'annoncer la réussite

- `npx hyperframes doctor` : Node, FFmpeg/FFprobe et Chrome doivent fonctionner. Docker, TTS (Kokoro)
  ou BGM (MusicGen) absents, « Some checks failed » pour ces seules lignes,
  une nouvelle version HyperFrames disponible ou une mémoire temporairement basse ne sont pas,
  seuls, la preuve d'une installation ratée. Ne pas mettre à jour HyperFrames pour effacer un avis.
- Rendre l'accueil (5 s) avec la CLI du projet, `npx hyperframes render "<dossier Accueil …>" -o
  work/test-rendu.mp4`, et vérifier qu'une vidéo non vide est produite, puis la supprimer. C'est
  un test technique, pas une commande à donner au client.
- Tester la transcription séparément : créer `work/` si besoin, produire un petit son de test
  avec FFmpeg, puis lancer le binaire Whisper avec le modèle et les chemins de `brand.config.json`.
  Vérifier le code de sortie et le chargement réel du modèle. Un son sans parole peut légitimement
  ne produire aucun mot : ne pas inventer une transcription ni conclure à un échec pour ce seul motif.
- Vérifier les outils du monteur : `python3 -c "import PIL"` (Windows : `python`) sans erreur.
- Afficher un bilan bref par fonction : montage, export vidéo, transcription, réglages.
  **✅ Vérifié** seulement si testé avec succès ; sinon **À terminer**, avec la prochaine action.
  Ne jamais annoncer « tout est prêt » tant qu'un test nécessaire reste en échec ou non exécuté.

Après réussite seulement :

> **Ton monteur est prêt 🎬**
>
> **Glisse ta vidéo brute ici et écris “on monte celle-ci”.**
>
> Pour cette première vidéo, je fais tout le montage avec les réglages de base, sans te poser
> de questions : coupes, sous-titres, animations, bruitages. Habillage noir et blanc, ta vidéo
> reste en couleur. Ensuite, tu me diras tout ce que tu aurais fait autrement, et j'apprendrai
> ton style pour les prochaines.
>
> Sur Mac et Linux, si tu veux voir ton montage sur une timeline, l'app gratuite HyperFrames est en option :
> ouvre-y le dossier « Accueil » de ton dossier Monteur IA et glisse-y ta vidéo.

Si une vidéo est déjà fournie, commence la première vidéo sans la redemander (fichier agent,
section 🟢 : montage d'une traite, puis débrief). Si l'utilisateur veut personnaliser avant,
ouvre `/setup visuel`. **Le setup n'est jamais une condition d'accès au premier montage.**

---

## Installer l'agent IA (avant tout)

Le message du début de cette page s'adresse à une IA. Il faut donc d'abord installer **Claude Code** OU **Codex**
(un seul des deux suffit : prends celui dont tu as l'abonnement).

### Option A : Claude Code

1. Télécharge l'application Claude pour ordinateur depuis [le site officiel](https://claude.com/download),
   puis connecte-toi avec ton compte disposant d'un accès à Claude Code.
2. Ouvre l'espace **Code** et choisis l'environnement **Local** pour travailler sur ton ordinateur.
3. Sélectionne le dossier dézippé **monteur-ia-main** via « Ouvrir un dossier » ou le sélecteur de projet.
4. Envoie le message du début de cette page. L'IA prend le relais.

La présentation des menus peut évoluer. Le repère à vérifier : **Code, Local, ton dossier sélectionné**.
Voir la [documentation officielle](https://code.claude.com/docs/en/desktop) si l'écran diffère.

### Option B : Codex

1. Télécharge l'application de bureau ChatGPT depuis le site officiel, puis connecte-toi avec ton compte.
2. Ouvre **Codex** et sélectionne le dossier local dézippé **monteur-ia-main** comme projet.
3. Envoie le message du début de cette page. L'IA prend le relais.

Le repère à vérifier est **Codex avec accès au dossier de ton ordinateur**. Joindre INSTALL.md à
une conversation sans accès aux fichiers locaux ne suffit pas pour installer les outils.
Les liens de téléchargement et les étapes à jour sont dans le
[guide officiel de démarrage](https://learn.chatgpt.com/docs/quickstart).

Si tu utilises déjà Claude Code ou Codex en terminal, tu peux garder cette méthode : ouvre ton
agent dans le dossier du projet et envoie le même message. Ce n'est pas nécessaire pour débuter.

Sous Codex, quand un skill est mentionné, l'agent lit `.agents/skills/<nom>/SKILL.md`.

---

## Les demandes d'autorisation

Le « go » autorise le plan expliqué dans la conversation. L'application peut encore te demander
une permission pour certaines opérations. L'IA doit t'expliquer ce qui est demandé et pourquoi.

**Pour que l'IA monte ta vidéo de A à Z sans t'interrompre**, active le mode qui saute les
demandes de permission (bypass), comme dans la vidéo de formation. Monteur IA ne travaille que
sur tes vidéos et sur ce dossier : rien de sensible.

- **Claude Code** : sous la zone de message, le sélecteur de mode → le mode qui contourne les
  permissions (« Bypass permissions »).
- **Codex** : dans les réglages de l'app, la section des permissions → l'accès complet, puis
  choisis-le dans ta conversation.

Les noms peuvent varier selon la version de l'application.

---

## Installation manuelle pas à pas

Cette section sert à l'IA pour dépanner, ou aux personnes qui choisissent de tout faire elles-mêmes.
Pour le parcours accompagné, reste dans la conversation : l'IA exécute ces commandes pour toi.

### macOS

**1. Node.js 22+**
```bash
node --version
```
S'il affiche `v22` (ou plus) : c'est bon, passe à la suite.
Sinon, télécharge l'installeur **LTS** (.pkg) sur https://nodejs.org et lance-le.
✅ Succès : `node --version` affiche `v22.x` ou plus.

**1 bis. Python 3**
```bash
python3 --version
```
S'il affiche `Python 3.9` ou plus : passe à la suite. Sinon, accepte l'installation des « outils de
développement en ligne de commande » que le Mac propose (ou installe Homebrew, étape 4, qui les ajoute).
Puis la librairie d'images (Pillow), si `python3 -c "import PIL"` affiche une erreur :
```bash
python3 -m pip install --user pillow
```
(Message « externally-managed-environment » : `brew install pillow` à la place.)
✅ Succès : `python3 --version` affiche `Python 3.9` ou plus, et `python3 -c "import PIL"` ne dit rien.

**2. Dépendances du projet**
```bash
npm install
```
✅ Succès : un dossier `node_modules/` apparaît, sans erreur rouge à la fin.

**3. Navigateur de rendu**
```bash
npx hyperframes browser ensure
```
✅ Succès : la commande affiche le chemin du navigateur (trouvé ou téléchargé).

**4. ffmpeg**
```bash
ffmpeg -version
```
S'il répond : passe à la suite. Sinon, installe Homebrew (si tu ne l'as pas) puis ffmpeg :
```bash
# Installe Homebrew seulement s'il est absent :
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ffmpeg
```
✅ Succès : `ffmpeg -version` affiche un numéro de version.

**5. Whisper (transcription locale)**
Vérifie d'abord `command -v whisper-cli` et la présence d'un modèle `ggml-*.bin` dans les
caches indiqués dans le protocole. Garde ce qui fonctionne déjà.
Si le binaire manque et que Homebrew est installé :
```bash
brew install whisper.cpp
```
Pour le modèle manquant, utilise les fichiers officiels de whisper.cpp : `ggml-large-v3-turbo.bin`
(~1,6 Go), ou `small` (~0,5 Go) si la connexion est limitée. Place le modèle dans
`~/.cache/monteur-ia/whisper/` et reporte son chemin réel dans la configuration.
✅ Succès : le binaire répond et charge le modèle lors du test de transcription.

**6. Configuration**
Crée le fichier seulement s’il n’existe pas déjà, pour conserver tes réglages :
```bash
if [ ! -f brand.config.json ]; then cp brand.config.example.json brand.config.json; fi
```
Renseigne dans `brand.config.json` les chemins de ffmpeg et de whisper détectés.
✅ Succès : `brand.config.json` existe.

**7. Vérification**
```bash
npx hyperframes doctor
```
✅ Succès : Node, FFmpeg/FFprobe et Chrome au vert. (Docker, Kokoro ou MusicGen absents, version plus récente
disponible ou mémoire basse = bénin, ce n'est pas un échec.) Tu peux lancer `/setup visuel` : les
couleurs et les sous-titres peuvent être personnalisés plus tard. Tu peux aussi envoyer ta vidéo
et demander un premier montage avec le style Papier, sans questionnaire préalable.

### Windows

**1. Node.js 22+**
```powershell
node --version
```
S'il affiche `v22` ou plus : passe à la suite. Sinon, télécharge l'installeur **LTS** (.msi)
sur https://nodejs.org et lance-le. Rouvre PowerShell après.
✅ Succès : `node --version` affiche `v22.x` ou plus.

**1 bis. Python 3**
```powershell
python --version
```
S'il affiche `Python 3.9` ou plus : passe à la suite. Sinon (message d'erreur, ou le Microsoft Store
s'ouvre) :
```powershell
winget install -e --id Python.Python.3.12
```
Puis **ferme et rouvre PowerShell**. Sous Windows, tape `python` là où la formation écrit `python3`.
Puis la librairie d'images (Pillow) :
```powershell
python -m pip install pillow
```
✅ Succès : `python --version` affiche `Python 3.12` (ou 3.9 et plus), et `python -c "import PIL"` ne dit rien.

**2. Dépendances du projet**
```powershell
npm install
```
✅ Succès : un dossier `node_modules\` apparaît, sans erreur.

**3. Navigateur de rendu**
```powershell
npx hyperframes browser ensure
```
✅ Succès : la commande affiche le chemin du navigateur (trouvé ou téléchargé).

**4. ffmpeg**
```powershell
ffmpeg -version
```
S'il répond : passe à la suite. Sinon :
```powershell
winget install Gyan.FFmpeg
```
Puis **ferme et rouvre PowerShell** (sinon `ffmpeg` reste introuvable : c'est le PATH).
Si `winget` est introuvable : ouvre le **Microsoft Store**, mets à jour « **App Installer** »,
rouvre PowerShell et réessaie.
✅ Succès : après réouverture, `ffmpeg -version` affiche un numéro de version.

**5. Whisper (transcription locale)**
Vérifie d'abord s'il est déjà là : `Get-Command whisper-cli` dans PowerShell, et cherche un fichier
`ggml-*.bin` dans `%USERPROFILE%\.cache\`. Si les deux existent, passe à l'étape 6.
Sinon : télécharge le binaire whisper.cpp pour **Windows x64** depuis les Releases de
`ggml-org/whisper.cpp` sur GitHub, plus le modèle `ggml-large-v3-turbo.bin` (~1,6 Go ; `small`, ~0,5 Go, est une alternative si ta connexion est limitée). Place les deux dans :
```
%USERPROFILE%\.cache\monteur-ia\whisper\
```
✅ Succès : lancer le binaire whisper affiche son aide.

**6. Configuration**
Crée le fichier seulement s’il n’existe pas déjà, pour conserver tes réglages :
```powershell
if (-not (Test-Path brand.config.json)) { Copy-Item brand.config.example.json brand.config.json }
```
Renseigne les chemins ffmpeg/whisper dans `brand.config.json`, et ajoute la variable
d'environnement `PRODUCER_FORCE_SCREENSHOT=true` (évite les rendus blancs/lents sous Windows).
✅ Succès : `brand.config.json` existe.

**7. Vérification**
```powershell
npx hyperframes doctor
```
✅ Succès : Node, FFmpeg/FFprobe et Chrome au vert. (Docker, Kokoro ou MusicGen absents, version plus récente
disponible ou mémoire basse = bénin, ce n'est pas un échec.) Tu peux lancer `/setup visuel` : les
couleurs et les sous-titres peuvent être personnalisés plus tard. Tu peux aussi envoyer ta vidéo
et demander un premier montage avec le style Papier, sans questionnaire préalable.

---

## Problèmes courants

**`winget` est introuvable (Windows)**
Ton « App Installer » est trop vieux ou absent. Ouvre le Microsoft Store, cherche
« App Installer », mets-le à jour. Rouvre PowerShell et réessaie. Sur un vieux Windows 10,
fais d'abord les mises à jour Windows.

**ffmpeg installé mais « commande introuvable »**
C'est le PATH. **Ferme et rouvre** ton terminal après l'installation : le nouveau chemin n'est
pris en compte que dans un terminal ouvert après coup. Si ça persiste, redémarre la machine.

**Rendu blanc ou très lent (Windows)**
Ajoute la variable d'environnement `PRODUCER_FORCE_SCREENSHOT=true`, puis relance le rendu.
Elle force un mode de capture compatible avec Windows.

**Le modèle Whisper est très long à télécharger**
`ggml-large-v3-turbo.bin` fait ~1,6 Go. Sur une connexion limitée, le modèle **small** (~0,5 Go) réduit le téléchargement
avec un compromis possible sur la précision : la transcription reste très bonne pour du talking-head. Tu pourras passer au
large plus tard.

**macOS bloque le binaire Whisper (« développeur non vérifié », Gatekeeper)**
Va dans Réglages Système → Confidentialité et sécurité, et clique « Ouvrir quand même » pour
le binaire whisper. Ou, en Terminal :
```bash
xattr -d com.apple.quarantine ~/.cache/monteur-ia/whisper/<nom-du-binaire>
```

**`npm install` échoue derrière un proxy d'entreprise**
Configure le proxy pour npm, puis relance :
```bash
npm config set proxy http://adresse-du-proxy:port
npm config set https-proxy http://adresse-du-proxy:port
npm install
```
Si un antivirus bloque l'installation, garde ses protections actives et transmets le message
exact à l'IA ou au support pour identifier le fichier concerné.

**« Quota atteint » / l'IA refuse de continuer**
Tu as épuisé le quota de ton abonnement (Claude Pro ou ChatGPT Plus). Attends la remise à zéro
du quota, ou monte d'offre. Ce n'est pas un bug d'installation.
Si ça arrive pendant un montage, rien n'est perdu : à la remise à zéro, rouvre la conversation (ou
une nouvelle, dans le même dossier) et écris « on reprend ». L'IA repart de l'étape où elle s'était
arrêtée.
