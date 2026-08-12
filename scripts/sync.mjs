#!/usr/bin/env node
/**
 * sync.mjs — régénère les fichiers dérivés de brand.config.json :
 *   - brand/tokens.css + brand/fonts.css (depuis templates/*.tpl + style-presets.json)
 *   - CLAUDE.md / AGENTS.md (depuis templates/AGENT.md.tpl)
 *   - miroir des skills (.claude/skills/ <-> .agents/skills/)
 *
 * Aucune identité visuelle n'est versionnée : tokens.css et fonts.css sont GÉNÉRÉS.
 * Tant que le style n'est pas choisi (`/setup visuel`), on retombe sur le preset
 * `neutral` — volontairement fade, pour que « je n'ai rien choisi » se voie.
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
// 1 bis. Style : presets, couleurs dérivées, tokens.css + fonts.css
// ---------------------------------------------------------------------------
function loadStylePresets() {
  return readJSON(path.join(ROOT, "templates", "style-presets.json"));
}

/** #abc / #aabbcc -> [r,g,b] (0-255). Renvoie null si ce n'est pas un hex. */
function hexToRgb(hex) {
  const m = /^#?([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(String(hex ?? "").trim());
  if (!m) return null;
  let h = m[1];
  if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

const toHex = (rgb) =>
  "#" + rgb.map((v) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, "0")).join("");

/** Luminance relative WCAG (0 = noir, 1 = blanc). */
function luminance(hex) {
  const rgb = hexToRgb(hex);
  if (!rgb) return 0;
  const [r, g, b] = rgb.map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Ratio de contraste WCAG entre deux couleurs (1 = identique, 21 = max). */
function contrastRatio(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Mélange linéaire de deux couleurs. t=0 -> a, t=1 -> b. */
function mix(a, b, t) {
  const ra = hexToRgb(a);
  const rb = hexToRgb(b);
  if (!ra || !rb) return a;
  return toHex(ra.map((v, i) => v + (rb[i] - v) * t));
}

/** Parmi `candidates`, celle qui contraste le plus avec `base`. */
function pickReadable(base, candidates) {
  return candidates
    .filter(Boolean)
    .map((c) => ({ c, r: contrastRatio(base, c) }))
    .sort((x, y) => y.r - x.r)[0].c;
}

/**
 * Fusionne le preset choisi et les surcharges explicites de brand.config.json.
 * La config gagne toujours : le preset n'est qu'un point de départ.
 */
function resolveStyle(config, presetsFile) {
  const presets = presetsFile.presets;
  const wanted = config?.visual?.stylePreset ?? null;
  const preset = presets.find((p) => p.id === wanted) ?? presets.find((p) => p.isUnset) ?? presets[0];

  // Une clé absente / à null dans la config ne doit PAS écraser le preset :
  // `visual` de brand.config.json ne contient que ce que l'utilisateur a vraiment réglé.
  const overrides = Object.fromEntries(
    Object.entries(config.visual ?? {}).filter(([, val]) => val !== null && val !== undefined && val !== "")
  );
  const visual = { ...preset.visual, ...overrides };
  delete visual.stylePreset;

  // Couleurs dérivées : jamais demandées à l'utilisateur, toujours calculées.
  const bg = visual.bg;
  const text = visual.text ?? pickReadable(bg, ["#ffffff", "#111111"]);
  const accent = visual.accent;
  const derived = {
    // Ce qu'on pose SUR un aplat d'accent (texte d'un sous-titre en bloc plein).
    contrast: pickReadable(accent, [bg, text, "#ffffff", "#111111"]),
    // Contour de lisibilité : l'opposé du texte.
    stroke: luminance(text) > 0.5 ? "#0b0b0b" : "#ffffff",
    // Surface qui tranche avec le fond (claire sur un thème sombre, et l'inverse).
    surfaceContrast: mix(visual.surface ?? bg, pickReadable(bg, ["#ffffff", "#111111"]), 0.82),
    muted: visual.muted ?? mix(text, bg, 0.42),
  };

  const chosen = Boolean(wanted) && !preset.isUnset;
  return { preset, visual: { ...visual, text, ...derived }, chosen };
}

/** Corps CSS de chaque skin de sous-titres. Une seule source de vérité. */
const CAPTION_SKINS = {
  block: `  color: var(--brand-contrast);
  background: var(--brand-accent);
  padding: 8px 20px;`,
  outline: `  color: var(--brand-text);
  background: none;
  padding: 0;
  -webkit-text-stroke: var(--brand-cap-stroke-width) var(--brand-stroke);
  paint-order: stroke fill;`,
  plate: `  color: var(--brand-text);
  background: var(--brand-surface);
  background: color-mix(in srgb, var(--brand-bg) 78%, transparent);
  padding: 10px 26px;
  border-radius: var(--brand-cap-radius);`,
  shadow: `  color: var(--brand-text);
  background: none;
  padding: 0;
  text-shadow: 4px 4px 0 var(--brand-accent), 0 0 14px var(--brand-stroke);`,
  underline: `  color: var(--brand-text);
  background: none;
  padding: 0 0 12px;
  border-bottom: 8px solid var(--brand-accent);
  text-shadow: 0 2px 6px var(--brand-stroke);`,
};

function buildCaptionCss(skinName) {
  const skin = CAPTION_SKINS[skinName] ? skinName : "plate";
  if (!CAPTION_SKINS[skinName]) {
    warn(`Skin de sous-titres inconnu « ${skinName} » — repli sur « plate ».`);
  }
  const active = `.cap {\n${CAPTION_SKINS[skin]}\n}`;
  const all = Object.entries(CAPTION_SKINS)
    .map(([name, body]) => `.cap.cap-skin-${name} {\n${body}\n}`)
    .join("\n\n");
  return { active, all };
}

function generateTokensCss(style, presetsFile) {
  const v = style.visual;
  const caption = buildCaptionCss(v.captionsSkin);
  const map = {
    STYLE_PRESET_ID: style.chosen ? style.preset.id : `${style.preset.id} (AUCUN STYLE CHOISI — lance /setup visuel)`,
    VISUAL_BG: v.bg,
    VISUAL_SURFACE: v.surface,
    VISUAL_SURFACE_CONTRAST: v.surfaceContrast,
    VISUAL_TEXT: v.text,
    VISUAL_MUTED: v.muted,
    VISUAL_ACCENT: v.accent,
    VISUAL_CONTRAST: v.contrast,
    VISUAL_STROKE: v.stroke,
    FONT_DISPLAY: v.fontDisplay,
    FONT_BODY: v.fontBody,
    FONT_CAPTIONS: v.fontCaptions,
    CAPTIONS_SKIN: v.captionsSkin,
    CAPTIONS_SKIN_ACTIVE_CSS: caption.active,
    CAPTIONS_SKINS_ALL_CSS: caption.all,
  };
  const tpl = fs.readFileSync(path.join(ROOT, "templates", "tokens.css.tpl"), "utf8");
  const out = tpl.replace(/\{\{([A-Z0-9_]+)\}\}/g, (whole, key) => (key in map ? String(map[key]) : whole));
  fs.writeFileSync(path.join(ROOT, "brand", "tokens.css"), out);
  log(`  généré  brand/tokens.css  (style: ${style.preset.id}, sous-titres: ${v.captionsSkin})`);

  // Contrôle de lisibilité — on n'échoue pas, on prévient (c'est le goût de l'utilisateur).
  const rAccentBg = contrastRatio(v.accent, v.bg);
  const rTextBg = contrastRatio(v.text, v.bg);
  if (rTextBg < 7) warn(`Texte peu lisible sur le fond (ratio ${rTextBg.toFixed(1)}:1, viser ≥ 7).`);
  if (rAccentBg < 3) warn(`Accent peu lisible sur le fond (ratio ${rAccentBg.toFixed(1)}:1, viser ≥ 3).`);
  return presetsFile;
}

function generateFontsCss(style, presetsFile) {
  const v = style.visual;
  const table = presetsFile.fonts ?? {};
  const families = [...new Set([v.fontBody, v.fontDisplay, v.fontCaptions].filter(Boolean))];

  const blocks = [];
  for (const family of families) {
    const faces = table[family]?.faces;
    if (!faces) {
      warn(
        `Police « ${family} » absente de la table de templates/style-presets.json — ` +
          `aucun @font-face généré. Dépose les fichiers dans assets/fonts/ et déclare-les.`
      );
      continue;
    }
    for (const f of faces) {
      const file = path.join(ROOT, "assets", "fonts", f.file);
      if (!fs.existsSync(file)) {
        warn(`Fichier de police manquant : assets/fonts/${f.file} (famille ${family}).`);
        continue;
      }
      blocks.push(
        `@font-face {\n` +
          `  font-family: "${family}";\n` +
          `  font-style: ${f.style ?? "normal"};\n` +
          `  font-weight: ${f.weight ?? 400};\n` +
          `  font-display: block;\n` +
          `  src: url("../assets/fonts/${f.file}") format("${f.format ?? "woff2"}");\n` +
          `}`
      );
    }
  }

  // La police de sous-titres a besoin d'un .ttf pour que PIL mesure la largeur d'un chunk
  // (tools/montage_captions.py). Sans lui, le découpage ne peut plus garantir une seule ligne.
  const capFamily = v.fontCaptions;
  const measure = table[capFamily]?.measureFile;
  if (!measure) {
    warn(`Police de sous-titres « ${capFamily} » sans \`measureFile\` (.ttf) dans style-presets.json — le découpage ne pourra pas mesurer la largeur.`);
  } else if (!fs.existsSync(path.join(ROOT, "assets", "fonts", measure))) {
    warn(`Fichier de mesure manquant : assets/fonts/${measure} (police de sous-titres ${capFamily}).`);
  }

  const tpl = fs.readFileSync(path.join(ROOT, "templates", "fonts.css.tpl"), "utf8");
  fs.writeFileSync(path.join(ROOT, "brand", "fonts.css"), tpl.replace("{{FONT_FACES}}", blocks.join("\n\n") + "\n"));
  log(`  généré  brand/fonts.css  (${families.join(", ")})`);
}

// ---------------------------------------------------------------------------
// 2. Générer CLAUDE.md / AGENTS.md
// ---------------------------------------------------------------------------
function buildPlaceholderMap(config, style) {
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
    STYLE_PRESET: style.chosen ? style.preset.label : "AUCUN — style non choisi",
    STYLE_ACCENT: style.visual.accent,
    STYLE_BG: style.visual.bg,
    STYLE_CAPTIONS: `${style.visual.fontCaptions}, skin « ${style.visual.captionsSkin} »`,
    STYLE_LAYOUT: config?.montage?.defaultLayout ?? style.preset.montage?.defaultLayout ?? "split",
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

function generateAgentFiles(config, style) {
  const tplPath = path.join(ROOT, "templates", "AGENT.md.tpl");
  const tpl = fs.readFileSync(tplPath, "utf8");
  const map = buildPlaceholderMap(config, style);
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
  // --style-only : régénère juste brand/tokens.css + brand/fonts.css. Utilisé par les hooks
  // pre-dev / pre-check / pre-render, pour qu'un projet fraîchement cloné ne tourne jamais
  // sans design system (les deux fichiers ne sont pas versionnés).
  const styleOnly = process.argv.includes("--style-only");

  if (!styleOnly) log("🔄 sync — design system + fichiers agent + miroir des skills\n");

  const { config, source, isExample } = loadConfig();
  if (!styleOnly) log(`Config : ${source}${isExample ? "  (exemple — lance /setup)" : ""}\n`);

  const presetsFile = loadStylePresets();
  const style = resolveStyle(config, presetsFile);

  if (!styleOnly) log("Génération du design system :");
  generateTokensCss(style, presetsFile);
  generateFontsCss(style, presetsFile);

  if (styleOnly) return;

  log("\nGénération des fichiers agent :");
  generateAgentFiles(config, style);

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
  if (!style.chosen) {
    log("✅ Sync terminé.\n");
    log("┌──────────────────────────────────────────────────────────────────────┐");
    log("│  ⚠️  AUCUN STYLE VISUEL CHOISI                                        │");
    log("│                                                                      │");
    log("│  Tes vidéos sortiront dans le style « neutre » : gris, sans accent,   │");
    log("│  sans caractère. C'est fait exprès — c'est un réglage d'usine, pas    │");
    log("│  une identité.                                                       │");
    log("│                                                                      │");
    log("│      Lance  /setup visuel  (2 minutes) pour choisir le tien.          │");
    log("└──────────────────────────────────────────────────────────────────────┘");
    return;
  }
  log(`✅ Sync terminé — style « ${style.preset.label} ».`);
}

main();
