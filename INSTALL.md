# Installation

Tu as deux voies :

- **La voie rapide** — tu colles un seul prompt et l'IA installe tout pour toi. Recommandé.
- **L'installation manuelle** — tu fais chaque étape à la main. Pour ceux qui préfèrent, ou si la voie rapide bloque.

> ⚠️ **Avant de coller le prompt, il faut que Claude Code ou Codex soit déjà installé et ouvert dans ce dossier.**
> Si ce n'est pas encore le cas, va d'abord à la section [Installer l'agent IA](#installer-lagent-ia-avant-tout).

---

## 🚀 La voie rapide — le prompt d'installation

Ouvre **Claude Code** (ou **Codex**) à la racine de ce dossier, puis **copie-colle exactement le bloc ci-dessous**
comme premier message :

```text
Tu es mon assistant d'installation pour le projet « Monteur IA ». Installe tout l'environnement,
étape par étape, sans jamais rien casser. Suis ces règles :

1. DÉTECTE mon système d'exploitation (macOS ou Windows) et mon architecture, puis annonce-moi
   le PLAN d'installation en une liste courte avant de commencer. Attends que je confirme.

2. Procède par étapes IDEMPOTENTES : pour chaque outil, d'abord VÉRIFIE s'il est déjà là
   (check), installe seulement si absent (install), puis RE-VÉRIFIE (re-check). Ne réinstalle
   jamais un outil déjà présent et fonctionnel. Ordre imposé :

   a) Node.js 22 minimum (vérifie `node --version`). S'il est absent ou trop vieux : donne-moi
      le lien https://nodejs.org (installeur LTS officiel, .pkg macOS / .msi Windows) et
      ARRÊTE-TOI — je l'installe moi-même, puis je relance ce prompt. Ne tente pas de
      l'installer par un gestionnaire de paquets.
   b) `npm install` à la racine du projet (installe HyperFrames et les dépendances).
   c) chrome-headless-shell : `npx puppeteer browsers install chrome-headless-shell`.
   d) ffmpeg (vérifie `ffmpeg -version`). Si absent :
      - macOS : installe via Homebrew (`brew install ffmpeg`). Si Homebrew est absent,
        demande-moi d'ABORD mon accord EXPLICITE avant d'installer Homebrew, puis installe-le.
      - Windows : `winget install Gyan.FFmpeg`. Préviens-moi qu'il faut ROUVRIR un terminal
        pour que le PATH soit pris en compte. Si `winget` est introuvable, dis-moi de mettre à
        jour « App Installer » depuis le Microsoft Store, puis de relancer.
   e) Whisper (transcription locale) : télécharge le binaire précompilé whisper.cpp adapté à
      mon OS/architecture depuis les GitHub Releases de ggml-org/whisper.cpp, PLUS le modèle
      `ggml-large-v3-turbo.bin`. PRÉVIENS-MOI que le modèle pèse ~1,6 Go AVANT de le
      télécharger, et propose le modèle `medium` en alternative si ma connexion est lente.
      Range binaire et modèle dans le cache :
        - macOS : ~/.cache/monteur-ia/whisper/
        - Windows : %USERPROFILE%\.cache\monteur-ia\whisper\
   f) Configuration : si `brand.config.json` n'existe pas, crée-le à partir de
      `brand.config.example.json`. Écris-y les chemins réellement détectés (ffmpeg, binaire et
      modèle whisper). Sur Windows, ajoute la variable d'environnement
      PRODUCER_FORCE_SCREENSHOT=true (elle évite les rendus blancs/lents).
   g) Skills : si le dossier `.agents/skills` est incomplet, lance `npx hyperframes skills`.
   h) `npm run sync` (régénère CLAUDE.md / AGENTS.md et les skills).

3. Ne PASSE JAMAIS à l'étape suivante si l'étape en cours a échoué. En cas d'échec :
   diagnostique en trois lignes — message d'erreur → cause probable → UNE action corrective —
   puis retente. Si c'est un blocage système (droits admin, proxy réseau, antivirus), NE
   force pas : pointe-moi vers la section « Problèmes courants » correspondante d'INSTALL.md
   et attends.

4. DIAGNOSTIC FINAL, une fois tout installé :
   - lance `npx hyperframes doctor` ;
   - smoke test rendu : rends 2 secondes de la composition-témoin
     `compositions/exemple-section.html` et vérifie qu'un fichier vidéo est bien produit ;
   - smoke test transcription : génère un son de test avec
     `ffmpeg -f lavfi -i "sine=frequency=440:duration=5" work/test-whisper.wav`
     puis transcris ce fichier avec whisper pour vérifier qu'il répond ;
   - affiche un TABLEAU récapitulatif avec ✅ / ❌ par composant (Node, npm, chrome-headless-shell,
     ffmpeg, whisper, config, doctor, rendu, transcription).
   Si tout est ✅, conclus par : « Installation terminée. Lance /setup pour personnaliser ton
   Monteur IA. » S'il reste un ❌, explique-moi précisément quoi faire.
```

C'est tout. Laisse l'IA travailler et réponds-lui quand elle te pose une question.

Si à un moment ça coince et que l'IA ne s'en sort pas, passe à l'installation manuelle ci-dessous
pour l'étape concernée.

---

## Installer l'agent IA (avant tout)

Le prompt ci-dessus s'adresse à une IA. Il faut donc d'abord installer **Claude Code** OU **Codex**
(un seul des deux suffit — prends celui dont tu as l'abonnement).

### Option A — Claude Code (abonnement Claude Pro, ~20 €/mois)

**macOS**
1. Ouvre le Terminal (Applications → Utilitaires → Terminal).
2. Colle et lance :
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```
   *Alternative sans terminal :* télécharge l'app **Claude Desktop** depuis claude.ai.
3. Succès : la commande `claude` répond dans un nouveau terminal.

**Windows** (sans WSL, natif)
1. Ouvre **PowerShell**.
2. Colle et lance :
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
3. Succès : la commande `claude` répond dans un nouveau PowerShell.

Ensuite : place-toi dans ce dossier et lance `claude`. Puis colle le prompt d'installation.

### Option B — Codex (inclus dans ChatGPT Plus, ~20 €/mois)

Codex a besoin de Node.js (voir étape Node.js plus bas si tu ne l'as pas encore).

1. Installe Codex :
   ```bash
   npm install -g @openai/codex
   ```
   (Attention au `@openai/` : le paquet est bien sous ce scope.)
2. Succès : la commande `codex` répond.
3. Sous **Windows**, le support natif est expérimental : s'il manque des runtimes
   « Visual C++ » au lancement, installe-les, ou passe par **WSL2** en alternative.

Ensuite : place-toi dans ce dossier, lance `codex`, et colle le prompt d'installation.
Sous Codex, quand un skill est mentionné, ouvre le fichier `.agents/skills/<nom>/SKILL.md` indiqué.

---

## Installation manuelle pas à pas

Tu peux tout installer toi-même, dans l'ordre. Après chaque commande, un « ✅ Succès » te dit à quoi
ça ressemble quand c'est bon.

### macOS

**1. Node.js 22+**
```bash
node --version
```
S'il affiche `v22` (ou plus) : c'est bon, passe à la suite.
Sinon, télécharge l'installeur **LTS** (.pkg) sur https://nodejs.org et lance-le.
✅ Succès : `node --version` affiche `v22.x` ou plus.

**2. Dépendances du projet**
```bash
npm install
```
✅ Succès : un dossier `node_modules/` apparaît, sans erreur rouge à la fin.

**3. Navigateur de rendu (chrome-headless-shell)**
```bash
npx puppeteer browsers install chrome-headless-shell
```
✅ Succès : un message « chrome-headless-shell … downloaded ».

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
Télécharge le binaire whisper.cpp pour **macOS Apple Silicon** depuis les Releases de
`ggml-org/whisper.cpp` sur GitHub, plus le modèle `ggml-large-v3-turbo.bin` (~1,6 Go ; prends
`medium` si ta connexion est lente). Place les deux dans :
```
~/.cache/monteur-ia/whisper/
```
Si macOS bloque le binaire (« impossible de vérifier le développeur »), voir *Problèmes courants*.
✅ Succès : lancer le binaire whisper affiche son aide.

**6. Configuration**
```bash
cp brand.config.example.json brand.config.json
```
Renseigne dans `brand.config.json` les chemins de ffmpeg et de whisper détectés.
✅ Succès : `brand.config.json` existe.

**7. Vérification**
```bash
npx hyperframes doctor
```
✅ Succès : chaque ligne du doctor est au vert. Tu peux lancer `/setup`.

### Windows

**1. Node.js 22+**
```powershell
node --version
```
S'il affiche `v22` ou plus : passe à la suite. Sinon, télécharge l'installeur **LTS** (.msi)
sur https://nodejs.org et lance-le. Rouvre PowerShell après.
✅ Succès : `node --version` affiche `v22.x` ou plus.

**2. Dépendances du projet**
```powershell
npm install
```
✅ Succès : un dossier `node_modules\` apparaît, sans erreur.

**3. Navigateur de rendu (chrome-headless-shell)**
```powershell
npx puppeteer browsers install chrome-headless-shell
```
✅ Succès : message « … downloaded ».

**4. ffmpeg**
```powershell
ffmpeg -version
```
S'il répond : passe à la suite. Sinon :
```powershell
winget install Gyan.FFmpeg
```
Puis **ferme et rouvre PowerShell** (sinon `ffmpeg` reste introuvable — c'est le PATH).
Si `winget` est introuvable : ouvre le **Microsoft Store**, mets à jour « **App Installer** »,
rouvre PowerShell et réessaie.
✅ Succès : après réouverture, `ffmpeg -version` affiche un numéro de version.

**5. Whisper (transcription locale)**
Télécharge le binaire whisper.cpp pour **Windows x64** depuis les Releases de
`ggml-org/whisper.cpp` sur GitHub, plus le modèle `ggml-large-v3-turbo.bin` (~1,6 Go ; prends
`medium` si ta connexion est lente). Place les deux dans :
```
%USERPROFILE%\.cache\monteur-ia\whisper\
```
✅ Succès : lancer le binaire whisper affiche son aide.

**6. Configuration**
```powershell
copy brand.config.example.json brand.config.json
```
Renseigne les chemins ffmpeg/whisper dans `brand.config.json`, et ajoute la variable
d'environnement `PRODUCER_FORCE_SCREENSHOT=true` (évite les rendus blancs/lents sous Windows).
✅ Succès : `brand.config.json` existe.

**7. Vérification**
```powershell
npx hyperframes doctor
```
✅ Succès : chaque ligne du doctor est au vert. Tu peux lancer `/setup`.

---

## Problèmes courants

**`winget` est introuvable (Windows)**
Ton « App Installer » est trop vieux ou absent. Ouvre le Microsoft Store, cherche
« App Installer », mets-le à jour. Rouvre PowerShell et réessaie. Sur un vieux Windows 10,
fais d'abord les mises à jour Windows.

**ffmpeg installé mais « commande introuvable »**
C'est le PATH. **Ferme et rouvre** ton terminal après l'installation — le nouveau chemin n'est
pris en compte que dans un terminal ouvert après coup. Si ça persiste, redémarre la machine.

**Rendu blanc ou très lent (Windows)**
Ajoute la variable d'environnement `PRODUCER_FORCE_SCREENSHOT=true`, puis relance le rendu.
Elle force un mode de capture compatible avec Windows.

**Le modèle Whisper est très long à télécharger**
`ggml-large-v3-turbo.bin` fait ~1,6 Go. Sur une connexion lente, prends le modèle **medium**
(plus léger) : la transcription reste très bonne pour du talking-head. Tu pourras passer au
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
Si un antivirus bloque l'écriture dans `node_modules`, mets le dossier du projet en exception.

**« Quota atteint » / l'IA refuse de continuer**
Tu as épuisé le quota de ton abonnement (Claude Pro ou ChatGPT Plus). Attends la remise à zéro
du quota, ou monte d'offre. Ce n'est pas un bug d'installation.
