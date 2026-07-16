#!/usr/bin/env node
/**
 * sync.mjs — régénère CLAUDE.md / AGENTS.md depuis templates/AGENT.md.tpl
 * et miroir des skills métier (.claude/skills/ -> .agents/skills/).
 *
 * Node pur, zéro dépendance, cross-platform.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const rel = (p) => path.relative(ROOT, p) || ".";
const log = (msg) => console.log(msg);
const warn = (msg) => console.warn(`⚠️  ${msg}`);
const err = (msg) => console.error(`❌ ${msg}`);

let hadError = false;

// ---------------------------------------------------------------------------
// 1. Charger la config
// ---------------------------------------------------------------------------
function loadConfig() {
  const configPath = path.join(ROOT, "brand.config.json");
  const examplePath = path.join(ROOT, "brand.config.example.json");
  if (fs.existsSync(configPath)) {
    return { config: readJSON(configPath), source: "brand.config.json", isExample: false };
  }
  warn(
    "brand.config.json introuvable — `/setup` n'a pas encore été lancé. " +
      "Utilisation de brand.config.example.json (valeurs d'exemple)."
  );
  return { config: readJSON(examplePath), source: "brand.config.example.json", isExample: true };
}

function readJSON(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

// ---------------------------------------------------------------------------
// 2. Générer CLAUDE.md / AGENTS.md
// ---------------------------------------------------------------------------
function buildPlaceholderMap(config) {
  const brand = config.brand ?? {};
  const audio = config.audio ?? {};
  const derush = config.derush ?? {};

  // valeur -> string, ou null si absente (=> placeholder laissé visible)
  const raw = {
    FIRST_NAME: brand.firstName,
    BRAND_NAME: brand.name,
    BRAND_HANDLE: brand.handle,
    MUSIC_FILE: audio.musicFile ?? "(aucune — à fournir)",
    MUSIC_DB: audio.musicDb,
    CAMERA: derush.camera,
  };

  const map = {};
  for (const [key, val] of Object.entries(raw)) {
    map[key] = val === null || val === undefined ? null : String(val);
  }
  return map;
}

function substitutePlaceholders(tpl, map) {
  const missing = new Set();
  const out = tpl.replace(/\{\{([A-Z0-9_]+)\}\}/g, (whole, key) => {
    if (key in map) {
      if (map[key] === null) {
        missing.add(key);
        return whole; // laissé tel quel (visible = à setup)
      }
      return map[key];
    }
    // placeholder inconnu (ex. futur) : on le laisse visible
    missing.add(key);
    return whole;
  });
  return { out, missing };
}

/**
 * Résout les zones conditionnelles {{#BLOCK}}...{{/BLOCK}}.
 * `keep` = nom du bloc à conserver (marqueurs retirés, contenu gardé).
 * Tous les autres blocs sont retirés (marqueurs + contenu).
 */
function resolveConditionals(text, keep) {
  return text.replace(
    /\{\{#([A-Z0-9_]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g,
    (_whole, name, inner) => (name === keep ? inner : "")
  );
}

function generateAgentFiles(config) {
  const tplPath = path.join(ROOT, "templates", "AGENT.md.tpl");
  const tpl = fs.readFileSync(tplPath, "utf8");
  const map = buildPlaceholderMap(config);
  const { out: substituted, missing } = substitutePlaceholders(tpl, map);

  const targets = [
    { file: "CLAUDE.md", keep: "CLAUDE_CODE" },
    { file: "AGENTS.md", keep: "CODEX" },
  ];

  for (const { file, keep } of targets) {
    const content = resolveConditionals(substituted, keep);
    fs.writeFileSync(path.join(ROOT, file), content);
    log(`  généré  ${file}  (bloc conditionnel: ${keep})`);
  }

  if (missing.size > 0) {
    warn(
      `Placeholders non renseignés (laissés visibles, à compléter via /setup) : ${[...missing]
        .map((k) => `{{${k}}}`)
        .join(", ")}`
    );
  }
}

// ---------------------------------------------------------------------------
// 3. Miroir des skills métier
// ---------------------------------------------------------------------------
function loadLockedSkillNames() {
  const lockPath = path.join(ROOT, "skills-lock.json");
  if (!fs.existsSync(lockPath)) {
    warn("skills-lock.json introuvable — aucun skill framework protégé.");
    return new Set();
  }
  const lock = readJSON(lockPath);
  return new Set(Object.keys(lock.skills ?? {}));
}

const COMMENT_PREFIX = "<!-- Copie générée — éditer .claude/skills/";
function generatedComment(name) {
  return `${COMMENT_PREFIX}${name}/ puis npm run sync -->`;
}

/**
 * Insère la ligne de commentaire "en tête" du SKILL.md copié.
 * Si le fichier commence par un frontmatter YAML (--- ... ---),
 * le commentaire est inséré JUSTE APRÈS pour ne pas casser le parsing.
 */
function stampSkillMd(skillMdPath, name) {
  if (!fs.existsSync(skillMdPath)) return;
  const original = fs.readFileSync(skillMdPath, "utf8");
  const comment = generatedComment(name);

  // éviter un double tampon
  const withoutOldStamp = original
    .split("\n")
    .filter((line) => !line.startsWith(COMMENT_PREFIX))
    .join("\n");

  let result;
  const fm = withoutOldStamp.match(/^(---\n[\s\S]*?\n---\n)/);
  if (fm) {
    result = fm[1] + comment + "\n" + withoutOldStamp.slice(fm[1].length);
  } else {
    result = comment + "\n" + withoutOldStamp;
  }
  fs.writeFileSync(skillMdPath, result);
}

function mirrorSkills(lockedNames) {
  const srcRoot = path.join(ROOT, ".claude", "skills");
  const destRoot = path.join(ROOT, ".agents", "skills");

  if (!fs.existsSync(srcRoot)) {
    warn(".claude/skills/ introuvable — rien à miroir.");
    return;
  }
  fs.mkdirSync(destRoot, { recursive: true });

  const entries = fs
    .readdirSync(srcRoot, { withFileTypes: true })
    .filter((e) => e.isDirectory());

  for (const entry of entries) {
    const name = entry.name;

    // Un dossier au nom d'un skill framework verrouillé dans .claude/skills/ est une
    // copie miroir (cf. mirrorFrameworkSkills) : on ne le repousse JAMAIS vers
    // .agents/skills/ (le lock fait autorité là-bas). Skip silencieux.
    if (lockedNames.has(name)) continue;

    const src = path.join(srcRoot, name);
    const dest = path.join(destRoot, name);

    fs.rmSync(dest, { recursive: true, force: true });
    fs.cpSync(src, dest, { recursive: true, force: true });
    stampSkillMd(path.join(dest, "SKILL.md"), name);

    const hasSkillMd = fs.existsSync(path.join(dest, "SKILL.md"));
    log(
      `  miroir  .claude/skills/${name}/ -> ${rel(dest)}/` +
        (hasSkillMd ? "" : "  (pas de SKILL.md — copié tel quel)")
    );
  }
}

/**
 * Miroir inverse : les skills FRAMEWORK (.agents/skills/, gérés par skills-lock.json)
 * sont copiés vers .claude/skills/ pour que Claude Code les découvre aussi
 * (Claude Code ne lit que .claude/skills/ ; sans ça, /hyperframes etc. n'existent
 * pas pour les utilisateurs Claude Code). Copie one-way, jamais l'inverse.
 */
function mirrorFrameworkSkills(lockedNames) {
  const srcRoot = path.join(ROOT, ".agents", "skills");
  const destRoot = path.join(ROOT, ".claude", "skills");

  if (!fs.existsSync(srcRoot)) {
    warn(".agents/skills/ introuvable — skills framework non miroirés.");
    return;
  }
  fs.mkdirSync(destRoot, { recursive: true });

  let count = 0;
  for (const name of lockedNames) {
    const src = path.join(srcRoot, name);
    if (!fs.existsSync(src)) continue;

    const dest = path.join(destRoot, name);
    fs.rmSync(dest, { recursive: true, force: true });
    fs.cpSync(src, dest, { recursive: true, force: true });
    count++;
  }
  log(`  ${count} skills framework miroirés vers .claude/skills/ (découverte Claude Code).`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
  log("🔄 sync — régénération CLAUDE.md / AGENTS.md + miroir des skills\n");

  const { config, source, isExample } = loadConfig();
  log(`Config : ${source}${isExample ? "  (exemple — lance /setup)" : ""}\n`);

  log("Génération des fichiers agent :");
  generateAgentFiles(config);

  log("\nMiroir des skills métier (.claude -> .agents) :");
  const lockedNames = loadLockedSkillNames();
  log(`  ${lockedNames.size} skills framework verrouillés (jamais écrasés).`);
  mirrorSkills(lockedNames);

  log("\nMiroir des skills framework (.agents -> .claude) :");
  mirrorFrameworkSkills(lockedNames);

  log("");
  if (hadError) {
    err("Terminé AVEC erreurs (voir ci-dessus).");
    process.exit(1);
  }
  log("✅ Sync terminé.");
}

main();
