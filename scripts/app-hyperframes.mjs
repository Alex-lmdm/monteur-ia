#!/usr/bin/env node
/**
 * app-hyperframes.mjs — branche Monteur IA sur l'app HyperFrames Studio.
 *
 *   node scripts/app-hyperframes.mjs etat               où en est le branchement (ne modifie rien)
 *   node scripts/app-hyperframes.mjs brancher           l'app lit désormais les instructions du projet
 *   node scripts/app-hyperframes.mjs ouvrir <dossier>   ouvre un projet (accueil ou Reel) dans l'app
 *
 * Pourquoi « brancher » : l'app lance Claude Code sans charger le CLAUDE.md du projet ouvert
 * (`--setting-sources user`). La variable CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1, posée
 * dans la clé `env` de la config Claude Code de l'utilisateur, lui fait lire le CLAUDE.md du
 * dossier ouvert (l'app passe toujours ce dossier en `--add-dir`). Effet ailleurs : un dossier
 * ajouté à une session Claude Code fait lire son CLAUDE.md, rien d'autre. Rien d'autre n'est
 * modifié dans la config, et une sauvegarde est faite avant toute écriture.
 *
 * Codex lit AGENTS.md et les skills du dossier par lui-même, mais coupe AGENTS.md à 32 Kio par
 * défaut : avec ses extensions et les préférences apprises, Monteur IA peut dépasser. « brancher »
 * relève donc aussi `project_doc_max_bytes` dans la config de Codex, s'il est installé.
 *
 * Node pur, zéro dépendance, cross-platform.
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const VARIABLE = "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD";
export const APP_ID = "dev.hyperframes.desktop";
export const DOWNLOAD_URL = "https://hyperframes.dev/studio";
// Un dossier est un projet pour l'app s'il a un index.html et l'un de ces fichiers.
const PROJECT_MARKERS = ["hyperframes.json", "meta.json", "project.json"];

/** Le dossier de config de Claude Code, résolu comme Claude Code et l'app le résolvent. */
export function claudeHome(env = process.env, home = os.homedir()) {
  return env.CLAUDE_CONFIG_DIR || path.join(home, ".claude");
}

export const settingsPath = (env, home) => path.join(claudeHome(env, home), "settings.json");

const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

/** État du branchement, sans rien écrire. */
export function readBranchement(file) {
  if (!fs.existsSync(file)) return { file, exists: false, branche: false };
  let settings;
  try {
    settings = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    return { file, exists: true, branche: false, invalid: `JSON illisible (${error.message})` };
  }
  if (!isObject(settings)) return { file, exists: true, branche: false, invalid: "ce n'est pas un objet JSON" };
  if (settings.env !== undefined && !isObject(settings.env))
    return { file, exists: true, branche: false, invalid: "sa clé « env » n'est pas un objet" };
  return { file, exists: true, branche: settings.env?.[VARIABLE] === "1" };
}

const stamp = (date) => date.toISOString().replace(/[:.]/g, "-");

/** Pose la variable. Idempotent ; sauvegarde le fichier avant de l'écrire ; refuse un fichier
 *  qu'il ne sait pas lire plutôt que de l'écraser. */
export function brancher(file, now = new Date()) {
  const state = readBranchement(file);
  if (state.invalid)
    throw new Error(`${file} : ${state.invalid}. Rien n'a été modifié : corrige ce fichier, puis relance.`);
  if (state.branche) return { ...state, changed: false, backup: null };

  let settings = {};
  let backup = null;
  if (state.exists) {
    settings = JSON.parse(fs.readFileSync(file, "utf8"));
    backup = `${file}.avant-monteur-ia-${stamp(now)}`;
    fs.copyFileSync(file, backup);
  } else {
    fs.mkdirSync(path.dirname(file), { recursive: true });
  }
  settings.env = { ...(settings.env ?? {}), [VARIABLE]: "1" };
  // Écriture atomique : Claude Code peut relire ce fichier à tout moment.
  const tmp = `${file}.tmp-${process.pid}`;
  fs.writeFileSync(tmp, `${JSON.stringify(settings, null, 2)}\n`);
  fs.renameSync(tmp, file);
  return { file, exists: true, branche: true, changed: true, backup };
}

// ---------------------------------------------------------------------------
// Codex : lire AGENTS.md en entier (project_doc_max_bytes, 32 Kio par défaut). Dans un Reel d'un
// dossier Monteur IA suivi par git, Codex lit à la suite l'AGENTS.md du dossier puis celui du Reel.
// ---------------------------------------------------------------------------
export const CODEX_LIMITE = 131072;
const CODEX_CLE = "project_doc_max_bytes";

/** Le dossier de config de Codex : $CODEX_HOME, sinon ~/.codex. */
export const codexHome = (env = process.env, home = os.homedir()) => env.CODEX_HOME || path.join(home, ".codex");

/** Relève la limite de lecture d'AGENTS.md dans config.toml. Ne fait rien si Codex n'est pas installé
 *  (pas de dossier de config) ; idempotent ; sauvegarde avant d'écrire. */
export function brancherCodex(dir, now = new Date()) {
  if (!fs.existsSync(dir)) return { changed: false, skipped: "Codex n'est pas installé" };
  const file = path.join(dir, "config.toml");
  const before = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  const lignes = before ? before.replace(/(\r?\n)+$/, "").split(/\r?\n/) : [];
  // Une clé de premier niveau doit précéder la première table [section] du TOML.
  const premiereTable = lignes.findIndex((l) => /^\s*\[/.test(l));
  const fin = premiereTable === -1 ? lignes.length : premiereTable;
  const i = lignes.slice(0, fin).findIndex((l) => new RegExp(`^\\s*${CODEX_CLE}\\s*=`).test(l));
  if (i !== -1) {
    const valeur = Number(lignes[i].split("=")[1].replace(/#.*/, "").trim());
    if (valeur >= CODEX_LIMITE) return { changed: false, file };
    lignes[i] = `${CODEX_CLE} = ${CODEX_LIMITE}`;
  } else {
    lignes.splice(fin, 0, `${CODEX_CLE} = ${CODEX_LIMITE}  # Monteur IA : lire AGENTS.md en entier`, ...(fin < lignes.length && fin > 0 ? [""] : []));
  }
  let backup = null;
  if (before) {
    backup = `${file}.avant-monteur-ia-${stamp(now)}`;
    fs.copyFileSync(file, backup);
  }
  const tmp = `${file}.tmp-${process.pid}`;
  fs.writeFileSync(tmp, `${lignes.join("\n").replace(/\n*$/, "")}\n`);
  fs.renameSync(tmp, file);
  return { changed: true, file, backup };
}

/** État de Codex, sans rien écrire : pas installé, ou lit-il AGENTS.md en entier ? */
export function readCodex(dir) {
  if (!fs.existsSync(dir)) return { installe: false, branche: false };
  const file = path.join(dir, "config.toml");
  const lignes = fs.existsSync(file) ? fs.readFileSync(file, "utf8").split(/\r?\n/) : [];
  const fin = lignes.findIndex((l) => /^\s*\[/.test(l));
  const ligne = lignes.slice(0, fin === -1 ? lignes.length : fin).find((l) => new RegExp(`^\\s*${CODEX_CLE}\\s*=`).test(l));
  return { installe: true, branche: Boolean(ligne) && Number(ligne.split("=")[1].replace(/#.*/, "").trim()) >= CODEX_LIMITE };
}

/** Chemin de l'app installée, ou null. Sur Linux, l'emplacement varie : on n'en cherche pas. */
export function findApp({ platform = process.platform, home = os.homedir(), exists = fs.existsSync } = {}) {
  if (platform !== "darwin") return null;
  return ["/Applications/HyperFrames.app", path.join(home, "Applications", "HyperFrames.app")].find(exists) ?? null;
}

/** Vrai si l'app reconnaît ce dossier comme un projet. */
export function isProject(dir) {
  if (!fs.existsSync(path.join(dir, "index.html"))) return false;
  return PROJECT_MARKERS.some((name) => fs.existsSync(path.join(dir, name)));
}

/** La CLI HyperFrames du dossier Monteur IA (0.8 et plus : elle sait ouvrir un projet dans l'app). */
export function localCli({ platform = process.platform, exists = fs.existsSync } = {}) {
  const maison = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const bin = path.join(maison, "node_modules", ".bin", platform === "win32" ? "hyperframes.cmd" : "hyperframes");
  return exists(bin) ? bin : null;
}

/** Ouvre un projet dans l'app (Mac, Linux). Ailleurs, explique le geste à faire à la main. */
export function ouvrir(dir, {
  platform = process.platform, app = findApp({ platform }), cli = localCli({ platform }), run = execFileSync,
} = {}) {
  const target = path.resolve(dir);
  if (!isProject(target))
    throw new Error(`${target} n'est pas un projet HyperFrames : il lui faut un index.html et un meta.json.`);
  if (platform === "darwin" && app) {
    run("open", ["-b", APP_ID, target]);
    return { opened: true, target };
  }
  if (platform === "linux" && cli) {
    run(cli, ["open", target]);
    return { opened: true, target };
  }
  const how =
    platform === "win32"
      ? "L'app HyperFrames n'existe pas encore sous Windows : continue dans Claude Code ou Codex."
      : `Dans l'app HyperFrames, menu Fichier > Ouvrir un dossier, puis choisis ${target}.` +
        (platform === "darwin" ? ` (App introuvable : télécharge-la sur ${DOWNLOAD_URL}.)` : "");
  return { opened: false, target, how };
}

function describe(env = process.env) {
  const state = readBranchement(settingsPath(env));
  const app = findApp();
  const lines = [];
  if (state.invalid) lines.push(`Config Claude Code : ${state.invalid} (${state.file}).`);
  else if (state.branche) lines.push("Config Claude Code : l'app lit les instructions de Monteur IA.");
  else lines.push("Config Claude Code : à brancher (node scripts/app-hyperframes.mjs brancher).");
  const codex = readCodex(codexHome(env));
  if (!codex.installe) lines.push("Config Codex : Codex n'est pas installé, rien à brancher.");
  else lines.push(codex.branche ? "Config Codex : lit les instructions de Monteur IA en entier."
    : "Config Codex : à brancher (node scripts/app-hyperframes.mjs brancher).");
  if (process.platform === "win32") lines.push("App HyperFrames : pas encore disponible sous Windows.");
  else if (process.platform !== "darwin") lines.push("App HyperFrames : à ouvrir depuis le menu de ton système (Linux).");
  else lines.push(app ? `App HyperFrames : installée (${app}).` : `App HyperFrames : pas installée (${DOWNLOAD_URL}).`);
  return { state, codex, app, text: lines.join("\n") };
}

function main(argv) {
  const [command, arg] = argv;
  if (command === "etat") {
    const { state, codex, app, text } = describe();
    console.log(argv.includes("--json") ? JSON.stringify({ ...state, codex, app }, null, 2) : text);
    return 0;
  }
  if (command === "brancher") {
    // Claude Code et Codex se branchent chacun de leur côté : une config illisible de l'un ne
    // prive pas l'autre de son réglage.
    let echecs = 0;
    try {
      const result = brancher(settingsPath());
      if (!result.changed) console.log("Déjà branché : l'app lit les instructions de Monteur IA.");
      else {
        console.log("Branché : l'app HyperFrames lira les instructions de Monteur IA.");
        if (result.backup) console.log(`Sauvegarde de l'ancienne config : ${result.backup}`);
        console.log("Effet à la prochaine conversation ouverte dans l'app.");
      }
    } catch (error) {
      echecs += 1;
      console.error(`❌ Claude Code : ${error.message}`);
    }
    try {
      const codex = brancherCodex(codexHome());
      if (codex.changed) {
        console.log("Codex lira les instructions de Monteur IA en entier.");
        if (codex.backup) console.log(`Sauvegarde de l'ancienne config Codex : ${codex.backup}`);
      }
    } catch (error) {
      echecs += 1;
      console.error(`❌ Codex : ${error.message}`);
    }
    return echecs ? 1 : 0;
  }
  if (command === "ouvrir" && arg) {
    const result = ouvrir(arg);
    console.log(result.opened ? `Ouvert dans l'app : ${result.target}` : result.how);
    return 0;
  }
  console.error("Usage : node scripts/app-hyperframes.mjs etat [--json] | brancher | ouvrir <dossier>");
  return 2;
}

// Lancé directement (pas importé par un test) : Node donne au module son chemin réel, liens résolus
// (dossier temporaire du Mac sous /var, dossier rangé derrière un lien) ; argv[1] garde le chemin tapé.
if (process.argv[1] && fs.realpathSync(path.resolve(process.argv[1])) === fileURLToPath(import.meta.url)) {
  try {
    process.exitCode = main(process.argv.slice(2));
  } catch (error) {
    console.error(`❌ ${error.message}`);
    process.exitCode = 1;
  }
}
