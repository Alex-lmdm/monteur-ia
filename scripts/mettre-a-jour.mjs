#!/usr/bin/env node
/**
 * mettre-a-jour.mjs : met un dossier Monteur IA à la version de CE dossier, sans rien perdre.
 *
 *   node scripts/mettre-a-jour.mjs "<dossier Monteur IA>"                # à blanc : montre le plan
 *   node scripts/mettre-a-jour.mjs "<dossier Monteur IA>" --appliquer    # applique
 *        [--sujet "<sujet du Reel en cours>"] [--date AAAA-MM-JJ] [--sans-npm]
 *
 * À lancer depuis la NOUVELLE version (téléchargée dans un dossier temporaire : MISE-A-JOUR.md,
 * étape 1), une fois par dossier Monteur IA (un par client ou par format).
 *
 * Le moteur (outils, scripts, modèles, skills, polices et sons livrés) est remplacé. Ce que le
 * client y a personnalisé passe dans la nouvelle version : profil de voix et CTA (zones
 * « BEGIN GENERATED »), ses polices déclarées (templates/style-presets.json), son corpus de
 * scripts, les consignes de ses extensions et ses consignes perso (blocs du modèle d'instructions).
 * Toute autre retouche d'un fichier du moteur, même hors zones ou hors blocs, est sauvegardée et
 * signalée dans le plan.
 * Jamais touchés : brand.config.json, brand/, ses images, logos, musiques et sons, ses extensions
 * (outils et skills), double-ia.config.json, stories/, ses Reels. Seule exception : un client de
 * Monteur IA 1 qui a déjà livré des Reels reçoit `setup.firstVideoDone: true` (la première vidéo se
 * décide désormais par dossier, plus par l'archive des Reels publiés, commune à tous ses dossiers).
 * Avant d'être remplacé ou retiré, chaque fichier du client est copié (ou rangé) dans
 * `.sauvegarde-mise-a-jour-<date>/`.
 *
 * Passage à « un Reel = un projet » (Monteur IA 1) : le Reel en cours sur le plan de travail de
 * la racine part dans reels/<sujet · date · client>/ avec ses outils adaptés, et son master est
 * régénéré pour l'export natif. Un plan de travail sans Reel en cours est rangé dans la sauvegarde.
 *
 * Mainteneur : `node scripts/mettre-a-jour.mjs --manifeste HEAD`, lancé depuis le commit de fusion
 * dans `main` puis commité avant de pousser, régénère scripts/versions-livrees.json : l'empreinte de
 * chaque fichier déjà livré (et sa forme neutralisée, sans zones ni blocs du client), lue dans
 * l'historique git. Sans argument : `origin/main`.
 *
 * Node pur, zéro dépendance, cross-platform.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const NEUF = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MANIFESTE = "scripts/versions-livrees.json";
const WIN = process.platform === "win32";
const TAILLE_MAX_LIVREE = 10 * 1024 * 1024;   // aucun fichier livré n'est plus gros : un rush ne se hache pas

// Jamais copiés depuis la nouvelle version : générés sur place, propres à un dossier, ou au chantier.
const JAMAIS = [/^Accueil /, /^reels\//, /^stories\//, /^exports\//, /^assets\/video\//, /^REFONTE-APP\.md$/,
  /^(CLAUDE|AGENTS)\.md$/, /^brand\/(tokens|fonts)\.css$/, /^brand\/fonts\//, /^brand\.config\.json$/,
  /(^|\/)\.DS_Store$/, /^\.git$/, /^\.claude\/settings\.local\.json$/, /^\.sauvegarde-mise-a-jour-/];
const ELAGUER = new Set(["node_modules", ".git", "reels", "exports", "worktrees", ".thumbnails", ".hyperframes",
  ".waveform-cache", ".transcode-cache"]);
// Fusionnés à part : le modèle d'instructions (consignes des extensions) et le .gitignore.
const A_PART = new Set(["templates/AGENT.md.tpl", ".gitignore"]);
// Entièrement écrits par le client (le setup les remplit) : jamais remplacés une fois modifiés.
const AU_CLIENT = new Set([".claude/skills/reel-script/references/scripts-exemples.md"]);
const PRESETS = "templates/style-presets.json";
// Plan de travail de Monteur IA 1, à la racine : il devient un Reel, ou rejoint la sauvegarde.
const PLAN = ["index.html", "compositions", "derush", "assets/video", "renders", "work", "snapshots", "probe",
  "overlay.html", "transcript.json"];
const CACHES = [".thumbnails", ".hyperframes", ".waveform-cache", ".transcode-cache"];
const GARDES_WORK = new Set(["work/.gitkeep", "work/premiere-video.md"]);   // appartiennent au dossier
const PAR_REEL_TELS_QUELS = new Set(["sections.py", "build_words.py", "cut_boundaries.py"]);
const PORTABLES = new Set([...PAR_REEL_TELS_QUELS, "montage_captions.py", "build_sfx.py"]);
// Outils adaptés au Reel en cours, mis de côté avant de remplacer le moteur : ils suivent le Reel
// (même chemin dans son dossier) et permettent de reprendre une mise à jour interrompue.
const DEPOT = "work/migration-v1/tools";
const BLOC_EXTENSION = /\n*<!-- BEGIN EXTENSION: ([\w-]+)[\s\S]*?<!-- END EXTENSION: \1 -->\n?/g;
// Les consignes propres au client, dans le modèle d'instructions : un bloc comme ceux des extensions,
// donc gardé par chaque mise à jour (MISE-A-JOUR.md, étape 4).
const BLOC_PERSO = "consignes-perso";
// Extensions officielles (clé = nom de leur bloc de consignes) : où le client trouve leur nouvelle
// version, et à quoi on reconnaît une version écrite pour « un Reel = un projet ».
const ecritePourLesReels = (outil) => (client) => existe(path.join(client, outil))
  && /\b(lieux|MAISON)\b/.test(lireTexte(path.join(client, outil)));
export const EXTENSIONS = {
  "double-ia": { nom: "Ton Double IA", depot: "Alex-lmdm/double-ia", outils: ["double_ia.py", "build_audio_cut.py"],
    aJour: ecritePourLesReels("tools/double_ia.py") },
  // Depuis le 07/10/2026, une story est un projet de l'app, montée comme un Reel : la version d'avant, déjà
  // écrite pour « un Reel = un projet », est à mettre à jour aussi.
  "systeme-stories": { nom: "Système Stories", depot: "Alex-lmdm/systeme-stories", outils: ["story.py", "story_text.py"],
    aJour: (client) => existe(path.join(client, "tools/story.py"))
      && /\bdef composer\(/.test(lireTexte(path.join(client, "tools/story.py")))
      && /"--brief"/.test(lireTexte(path.join(client, "tools/story.py"))) },   // script d'abord dans l'app
  // Privé (sons sous licence) : le client retélécharge pack-sfx.zip depuis sa formation.
  "pack-sfx": { nom: "Pack SFX", depot: null, outils: ["sfx.py", "sfx_mix.py"], versionMin: "1.1.0",
    aJour: (client) => comparerVersions(versionPackSfx(client) ?? "0", "1.1.0") >= 0 },
};

function comparerVersions(a, b) {
  const [x, y] = [a, b].map((v) => v.split(".").map(Number));
  for (let i = 0; i < Math.max(x.length, y.length); i += 1) if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) - (y[i] || 0);
  return 0;
}

/** La version du Pack SFX installée (manifeste posé par son installateur), ou null. */
function versionPackSfx(client) {
  try {
    return JSON.parse(lireTexte(path.join(client, "assets/sfx/.pack-sfx-manifest.json"))).version ?? null;
  } catch {
    return null;
  }
}
const ZONES = [/<!-- BEGIN GENERATED: ([\w-]+) -->([\s\S]*?)<!-- END GENERATED: \1 -->/g,
  /\/\* BEGIN GENERATED: ([\w-]+) \*\/([\s\S]*?)\/\* END GENERATED: \1 \*\//g];

const existe = (p) => fs.existsSync(p);
const lireTexte = (p) => fs.readFileSync(p, "utf8");
const z = (n) => String(n).padStart(2, "0");
const jour = (d) => `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}`;   // date locale
// Les vidéos finales d'un Reel repris gardent leur nom, suffixé : un nouvel export ne les écrase pas.
const SUFFIXE_ANCIEN = "-avant-mise-a-jour";

// --- empreintes (celles de git : un fichier livré se reconnaît dans l'historique) ---------------
function empreinte(buf) {
  return crypto.createHash("sha1").update(`blob ${buf.length}\0`).update(buf).digest("hex").slice(0, 12);
}

/** Empreintes d'un fichier du client : telle quelle, et sans les fins de ligne Windows (clone git). */
function empreintesClient(fichier) {
  if (fs.statSync(fichier).size > TAILLE_MAX_LIVREE) return [];
  const buf = fs.readFileSync(fichier);
  const out = [empreinte(buf)];
  if (buf.includes(13) && buf.length < 1024 * 1024) {
    out.push(empreinte(Buffer.from(buf.toString("latin1").replace(/\r\n/g, "\n"), "latin1")));
  }
  return out;
}

export function lireManifeste(racine = NEUF) {
  const p = path.join(racine, MANIFESTE);
  return existe(p) ? JSON.parse(lireTexte(p)).fichiers : {};
}

/** Le fichier du client est-il exactement une version livrée de ce chemin ? */
function livre(manifeste, rel, fichier) {
  const connues = manifeste[rel];
  return Boolean(connues) && empreintesClient(fichier).some((h) => connues.includes(h));
}

// Ce qui appartient au client dans un fichier du moteur : les consignes de ses extensions (blocs du
// modèle d'instructions) et ses zones personnalisées. Neutralisé, le texte se compare aux versions
// livrées : une différence restante est une retouche, à signaler plutôt qu'à écarter en silence.
const NEUTRE = "z:";
const MODELE = "templates/AGENT.md.tpl";

/** Le texte sans ce qui appartient au client : blocs d'extension retirés, zones vidées, fins de ligne
 *  et fin de fichier normalisées. */
export function neutre(texte) {
  return texte.replace(/\r\n/g, "\n").replace(BLOC_EXTENSION, "\n")
    .replace(ZONES[0], (_tout, cle) => `<!-- BEGIN GENERATED: ${cle} --><!-- END GENERATED: ${cle} -->`)
    .replace(ZONES[1], (_tout, cle) => `/* BEGIN GENERATED: ${cle} *//* END GENERATED: ${cle} */`)
    .replace(/\s*$/, "\n");
}

/** Fichier dont le manifeste garde la forme neutralisée (zones ou blocs du client). */
const neutralisable = (rel, texte) => rel === MODELE || texte.includes("BEGIN GENERATED");

/** Le fichier neutralisé du client est-il une version livrée ? null : le manifeste ne permet pas de
 *  le dire (manifeste d'avant les formes neutralisées, pour un fichier à zones). */
function livreNeutre(manifeste, rel, fichier) {
  const connues = manifeste[rel] ?? [];
  const h = empreinte(Buffer.from(neutre(lireTexte(fichier))));
  if (connues.includes(h) || connues.includes(`${NEUTRE}${h}`)) return true;
  return rel === MODELE || connues.some((c) => c.startsWith(NEUTRE)) ? false : null;
}

/** Empreintes de chaque fichier livré par `ref` et ses ancêtres (forme neutralisée comprise). */
export function calculerManifeste(ref = "origin/main", racine = NEUF) {
  const git = (...a) => execFileSync("git", a, { cwd: racine, encoding: "utf8", maxBuffer: 1 << 28 });
  const fichiers = {};
  const aNeutraliser = new Map();   // blob -> chemins
  for (const commit of git("rev-list", ref).trim().split("\n")) {
    for (const entree of git("ls-tree", "-r", "-z", commit).split("\0")) {
      const m = /^\d+ blob ([0-9a-f]{40})\t(.+)$/s.exec(entree);
      if (!m) continue;
      (fichiers[m[2]] ||= new Set()).add(m[1].slice(0, 12));
      if (/\.(md|tpl|css|html|js)$/.test(m[2]) && !/^(scripts|tools)\//.test(m[2])) {
        (aNeutraliser.get(m[1]) ?? aNeutraliser.set(m[1], new Set()).get(m[1])).add(m[2]);
      }
    }
  }
  // Contenu des blobs candidats, lus d'un coup (git cat-file --batch).
  const lot = execFileSync("git", ["cat-file", "--batch"], { cwd: racine, input: `${[...aNeutraliser.keys()].join("\n")}\n`,
    maxBuffer: 1 << 30 });
  for (let i = 0; i < lot.length;) {
    const fin = lot.indexOf(10, i);
    const [blob, , taille] = lot.subarray(i, fin).toString().split(" ");
    const texte = lot.subarray(fin + 1, fin + 1 + Number(taille)).toString("utf8");
    i = fin + 1 + Number(taille) + 1;
    for (const rel of aNeutraliser.get(blob) ?? []) {
      if (!neutralisable(rel, texte)) continue;
      const h = empreinte(Buffer.from(neutre(texte)));
      if (h !== blob.slice(0, 12)) fichiers[rel].add(`${NEUTRE}${h}`);
    }
  }
  const tri = Object.fromEntries(Object.keys(fichiers).sort().map((k) => [k, [...fichiers[k]].sort()]));
  return { ref, versions: Number(git("rev-list", "--count", ref).trim()), fichiers: tri };
}

export function genererManifeste(ref = "origin/main", racine = NEUF) {
  const sortie = calculerManifeste(ref, racine);
  const lignes = Object.entries(sortie.fichiers).map(([k, v]) => `    ${JSON.stringify(k)}: ${JSON.stringify(v)}`);
  fs.writeFileSync(path.join(racine, MANIFESTE),
    `{\n  "ref": ${JSON.stringify(ref)},\n  "versions": ${sortie.versions},\n  "fichiers": {\n${lignes.join(",\n")}\n  }\n}\n`);
  return sortie;
}

// --- arborescences ------------------------------------------------------------------------------
function fichiersDe(racine, sous = "", elaguer = ELAGUER) {
  const dir = path.join(racine, sous);
  if (!existe(dir)) return [];
  if (!fs.statSync(dir).isDirectory()) return [sous];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const rel = sous ? `${sous}/${e.name}` : e.name;
    if (e.isDirectory()) return elaguer.has(e.name) || /^\.sauvegarde-mise-a-jour-/.test(e.name) ? [] : fichiersDe(racine, rel, elaguer);
    return e.isFile() ? [rel] : [];
  });
}

function skillsFramework(racine = NEUF) {
  try {
    return new Set(Object.keys(JSON.parse(lireTexte(path.join(racine, "skills-lock.json"))).skills ?? {}));
  } catch {
    return new Set();
  }
}

/** Un chemin de skill : sa source (true) ou sa copie miroir refaite par `npm run sync` (false). */
function sourceDeSkill(rel, framework) {
  const skill = /^\.(claude|agents)\/skills\/([^/]+)\//.exec(rel);
  // Skill métier : source dans .claude/skills ; skill framework (skills-lock.json) : dans .agents/skills.
  return skill ? (skill[1] === "agents") === framework.has(skill[2]) : null;
}

/** Fichiers livrés par la nouvelle version, hors générés et hors copies miroir des skills. */
export function fichiersDuMoteur(racine = NEUF) {
  const framework = skillsFramework(racine);
  return fichiersDe(racine).filter((rel) => !JAMAIS.some((re) => re.test(rel)) && sourceDeSkill(rel, framework) !== false);
}

const estOutilParReel = (rel) => /^tools\/[^/]+\.py$/.test(rel) && existe(path.join(NEUF, rel))
  && /^║.*A CHAQUE REEL/m.test(lireTexte(path.join(NEUF, rel)));   // cadre d'en-tête, comme sync.mjs

export function estMonteurIA(dir) {
  return ["templates/AGENT.md.tpl", "scripts/sync.mjs", "tools"].every((f) => existe(path.join(dir, f)));
}

// --- reports de personnalisation ---------------------------------------------------------------
function zones(texte) {
  const out = new Map();
  ZONES.forEach((re, i) => {
    for (const m of texte.matchAll(re)) out.set(`${i}:${m[1]}`, m[2]);
  });
  return out;
}

/** La nouvelle version, avec le contenu des zones personnalisées du client. */
export function reporterZones(neuf, client) {
  const anciennes = zones(client);
  let reportees = 0;
  let texte = neuf;
  ZONES.forEach((re, i) => {
    texte = texte.replace(re, (tout, cle) => {
      if (!anciennes.has(`${i}:${cle}`)) return tout;
      reportees += 1;
      const contenu = anciennes.get(`${i}:${cle}`);
      return i === 0 ? `<!-- BEGIN GENERATED: ${cle} -->${contenu}<!-- END GENERATED: ${cle} -->`
        : `/* BEGIN GENERATED: ${cle} */${contenu}/* END GENERATED: ${cle} */`;
    });
  });
  return { texte, reportees };
}

const estObjet = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

/** La nouvelle version gagne ; ce que le client a ajouté (ex. sa police) reste. */
export function fusionnerJson(neuf, client) {
  if (!estObjet(neuf) || !estObjet(client)) return neuf;
  const out = {};
  for (const [k, v] of Object.entries(neuf)) out[k] = k in client ? fusionnerJson(v, client[k]) : v;
  for (const [k, v] of Object.entries(client)) if (!(k in out)) out[k] = v;
  return out;
}

export function blocsExtensions(modele) {
  return [...modele.matchAll(BLOC_EXTENSION)].map((m) => ({ nom: m[1], texte: m[0].trim() }));
}

/** Le modèle d'instructions neuf, suivi des consignes des extensions installées chez le client. */
export function modeleAvecExtensions(neuf, ancien) {
  const base = neuf.replace(BLOC_EXTENSION, "\n").replace(/\s*$/, "\n");
  return base + blocsExtensions(ancien).map((b) => `\n${b.texte}\n`).join("");
}

/** Les chemins « ../ » des sous-compositions (refusés par HyperFrames 0.8) partent de la racine du
 *  projet : attributs, url() du CSS et chaînes du JavaScript. */
export function cheminsDepuisLaRacine(html) {
  return html.replace(/((?:src|href)=["']|url\(\s*["']?|["'`])\.\.\/((?:brand|assets)\/)/g, "$1$2");
}

/** Les fichiers `assets/…` qu'une page du montage référence (attributs, url(), chaînes). */
export function assetsReferences(html) {
  const refs = new Set();
  for (const m of html.matchAll(/["'`(]\s*(?:\.\/)?(assets\/[^"'`)\n?#]+)/g)) {
    let rel = m[1].trim();
    try {
      rel = decodeURIComponent(rel);
    } catch { /* gardé tel quel */ }
    if (!rel.split("/").includes("..") && !rel.endsWith("/")) refs.add(rel);
  }
  return [...refs].sort();
}

/**
 * Ce que le montage d'un Reel repris référence dans `assets/` et qui n'est pas dans son dossier : en
 * Monteur IA 1, logos, images et polices vivaient à la racine, partagés. L'app et le rendu ne voient
 * que le dossier du Reel : la copie de la maison y est posée (l'original ne bouge pas).
 */
function copierMediasPartages(reel, client) {
  const pages = ["index.html", ...fichiersDe(reel, "compositions", new Set()).filter((f) => f.endsWith(".html"))]
    .filter((rel) => existe(path.join(reel, rel)));
  const copies = [];
  const introuvables = [];
  for (const rel of new Set(pages.flatMap((page) => assetsReferences(lireTexte(path.join(reel, page)))))) {
    if (existe(path.join(reel, rel))) continue;
    const source = path.join(client, rel);
    if (existe(source) && fs.statSync(source).isFile()) {
      fs.mkdirSync(path.dirname(path.join(reel, rel)), { recursive: true });
      fs.copyFileSync(source, path.join(reel, rel));
      copies.push(rel);
    } else introuvables.push(rel);
  }
  return { copies: copies.sort(), introuvables: introuvables.sort() };
}

/** La liste de sons d'un build_sfx.py adapté, reportée dans le build_sfx.py neuf (null si introuvable). */
export function reporterSons(ancien, neuf) {
  const re = /^events = [\s\S]*?(?=^events\.sort)/m;
  const liste = re.exec(ancien);
  return liste && re.test(neuf) ? neuf.replace(re, () => liste[0]) : null;
}

/** Ce que la mise à jour écrit pour un fichier fusionné : la nouvelle version plus ce qui est au client. */
function fusion(action, rel, client) {
  const neuf = path.join(NEUF, rel);
  const actuel = path.join(client, rel);
  if (action === "fusion-zones") return reporterZones(lireTexte(neuf), lireTexte(actuel)).texte;
  if (action === "fusion-json") {
    return `${JSON.stringify(fusionnerJson(JSON.parse(lireTexte(neuf)), JSON.parse(lireTexte(actuel))), null, 2)}\n`;
  }
  if (action === "modele") return modeleAvecExtensions(lireTexte(neuf), lireTexte(actuel));
  // .gitignore : les règles du client, puis celles de la nouvelle version qui lui manquent.
  const lignes = (p) => (existe(p) ? lireTexte(p).split(/\r?\n/) : []);
  const out = lignes(actuel);
  for (const l of [...lignes(neuf), ".sauvegarde-mise-a-jour-*/"]) if (l.trim() && !out.includes(l)) out.push(l);
  return `${out.join("\n").replace(/\n+$/, "")}\n`;
}

/** Même texte aux lignes vides près (une extension installée à la main espace ses blocs à sa façon). */
const pareil = (a, b) => a.replace(/\r\n/g, "\n").replace(/\n{2,}/g, "\n\n").trim()
  === b.replace(/\r\n/g, "\n").replace(/\n{2,}/g, "\n\n").trim();

/** L'action pour un fichier du moteur retouché par le client (null : rien à faire). */
function actionRetouche(rel, client, manifeste) {
  const neuf = empreinte(fs.readFileSync(path.join(NEUF, rel)));
  // Son corpus : gardé ; signalé seulement si la nouvelle version avait changé ce fichier.
  if (AU_CLIENT.has(rel)) return (manifeste[rel] ?? []).includes(neuf) ? null : "garde";
  // Les zones personnalisables vivent dans les skills, le design system et le style, jamais dans le code.
  const zonable = !/^(scripts|tools)\//.test(rel);
  const candidates = rel === PRESETS ? ["fusion-json"]
    : zonable && zones(lireTexte(path.join(client, rel))).size && zones(lireTexte(path.join(NEUF, rel))).size ? ["fusion-zones"] : [];
  for (const action of candidates) {
    try {
      return fusion(action, rel, client) === lireTexte(path.join(client, rel)) ? null : action;
    } catch { /* fichier du client illisible (JSON cassé) : remplacé, sa version sauvegardée */ }
  }
  return "remplace-modifie";
}

// --- plan -----------------------------------------------------------------------------------------
/** Ce que la mise à jour fera, sans rien toucher. */
export function planifier(client, { manifeste = lireManifeste(), sujet = null, date = null, archive = archivePubliee() } = {}) {
  const plan = { client, v2: existe(path.join(client, "tools/lieux.py")), moteur: [], obsoletes: [],
    extensions: [], outilsExtensions: [], extensionsAMettreAJour: [], plan: null };
  const neufs = new Set(fichiersDuMoteur());
  for (const rel of neufs) {
    const cible = path.join(client, rel);
    if (A_PART.has(rel)) {
      const action = rel === ".gitignore" ? "gitignore" : "modele";
      if (!existe(cible) || !pareil(fusion(action, rel, client), lireTexte(cible))) {
        // Le modèle retouché hors consignes des extensions : signalé (sa version reste dans la sauvegarde).
        const retouche = action === "modele" && existe(cible) && livreNeutre(manifeste, rel, cible) === false;
        plan.moteur.push({ rel, action, ...(retouche && { retouche }) });
      }
      continue;
    }
    if (!existe(cible)) {
      plan.moteur.push({ rel, action: "ajout" });
      continue;
    }
    if (empreintesClient(cible).includes(empreinte(fs.readFileSync(path.join(NEUF, rel))))) continue;
    const action = livre(manifeste, rel, cible) || estOutilParReel(rel) ? "remplace" : actionRetouche(rel, client, manifeste);
    // Zones reportées, mais une retouche ailleurs dans le fichier ne passe pas : elle est signalée.
    const retouche = action === "fusion-zones" && livreNeutre(manifeste, rel, cible) === false;
    if (action) plan.moteur.push({ rel, action, ...(retouche && { retouche }) });
  }
  // Fichiers d'une ancienne version que la nouvelle n'a plus (tels que livrés : jamais une retouche).
  const framework = skillsFramework();
  const dansLePlan = (rel) => PLAN.some((p) => rel === p || rel.startsWith(`${p}/`));
  for (const rel of Object.keys(manifeste)) {
    if (neufs.has(rel) || A_PART.has(rel) || dansLePlan(rel) || JAMAIS.some((re) => re.test(rel))) continue;
    if (/^(assets|brand)\//.test(rel)) continue;              // médias et style : jamais retirés
    if (sourceDeSkill(rel, framework) === false) continue;   // copie miroir : refaite par le sync
    const cible = path.join(client, rel);
    if (existe(cible) && livre(manifeste, rel, cible)) plan.obsoletes.push(rel);
  }
  const blocs = blocsExtensions(lireTexte(path.join(client, MODELE))).map((b) => b.nom);
  plan.extensions = blocs.filter((nom) => nom !== BLOC_PERSO);
  plan.consignesPerso = blocs.includes(BLOC_PERSO);
  // Outils d'extension écrits pour Monteur IA 1 : ils ne connaissent pas encore les Reels séparés.
  for (const rel of fichiersDe(client, "tools")) {
    if (neufs.has(rel) || manifeste[rel] || !/\.py$/.test(rel)) continue;
    if (!/\b(lieux|MAISON)\b/.test(lireTexte(path.join(client, rel)))) plan.outilsExtensions.push(rel);
  }
  // Extensions officielles installées mais pas encore dans leur version « un Reel = un projet ».
  plan.extensionsAMettreAJour = plan.extensions.filter((nom) => EXTENSIONS[nom] && !EXTENSIONS[nom].aJour(client));
  if (plan.extensionsAMettreAJour.includes("pack-sfx")) plan.versionPackSfx = versionPackSfx(client);
  plan.plan = planDeTravail(client, manifeste, { sujet, date, v2: plan.v2 });
  plan.premiereVideoFaite = premiereVideoDejaFaite(client, plan, archive);
  return plan;
}

/** L'archive des Reels publiés (tools/ranger_reel.py, close_reel.py en Monteur IA 1), commune à tous les dossiers. */
export const archivePubliee = (home = os.homedir()) => path.join(home, WIN ? "Videos" : "Movies", "reels-publies");

/**
 * Monteur IA 1 qui a déjà livré des vidéos (un Reel en cours, ou un Reel dans l'archive des publiés)
 * sans que son dossier le dise : la première vidéo se décide désormais par dossier
 * (`setup.firstVideoDone`), la mise à jour le note pour lui. Une note `work/premiere-video.md`
 * (première vidéo en cours, ou débrief à faire) suffit déjà : on n'y touche pas.
 */
function premiereVideoDejaFaite(client, plan, archive) {
  if (plan.v2 || existe(path.join(client, "work/premiere-video.md"))) return false;
  let config;
  try {
    config = JSON.parse(lireTexte(path.join(client, "brand.config.json")));
  } catch {
    return false;   // pas de réglages (ou illisibles) : on n'en crée pas
  }
  if (!estObjet(config) || config.setup?.firstVideoDone === true) return false;
  const archivee = existe(archive) && fs.readdirSync(archive, { withFileTypes: true }).some((e) => e.isDirectory());
  return archivee || Boolean(plan.plan?.reel);
}

/** Un Reel dont la reprise (depuis Monteur IA 1) a été interrompue : la mise à jour le termine. */
function reelInacheve(client) {
  const reels = path.join(client, "reels");
  if (!existe(reels)) return null;
  return fs.readdirSync(reels).map((n) => path.join(reels, n)).find((dir) => {
    try {
      return JSON.parse(lireTexte(path.join(dir, "meta.json"))).monteurIa?.migration === "en-cours";
    } catch {
      return false;
    }
  }) ?? null;
}

function marquer(reel, etat) {
  const fichier = path.join(reel, "meta.json");
  const meta = JSON.parse(lireTexte(fichier));
  meta.monteurIa = { ...meta.monteurIa, migration: etat };
  fs.writeFileSync(fichier, `${JSON.stringify(meta, null, 2)}\n`);
}

/** Outil par Reel adapté par le client : ni tel que livré, ni identique à la nouvelle version. */
const outilAdapte = (manifeste, rel, client) => existe(path.join(client, rel)) && !livre(manifeste, rel, path.join(client, rel))
  && !fs.readFileSync(path.join(client, rel)).equals(fs.readFileSync(path.join(NEUF, rel)));

/**
 * Le plan de travail de la racine (Monteur IA 1) : un Reel en cours à déplacer, des essais à
 * ranger, ou rien (null). Examiné à chaque passage : une mise à jour interrompue se reprend.
 */
function planDeTravail(client, manifeste, { sujet, date, v2 }) {
  const elements = PLAN.filter((p) => existe(path.join(client, p)));
  const fichiers = elements.flatMap((p) => fichiersDe(client, p, new Set())).filter((rel) => !GARDES_WORK.has(rel));
  // Ce qui n'est pas la démo livrée : le travail du client.
  const perso = fichiers.filter((rel) => !livre(manifeste, rel, path.join(client, rel)));
  const caches = CACHES.filter((c) => existe(path.join(client, c)));
  const inacheve = reelInacheve(client);
  // Monteur IA 2 n'adapte jamais les outils de la maison : seuls ceux de Monteur IA 1 suivent un Reel.
  const aDeposer = v2 ? [] : Object.keys(manifeste).filter((rel) => estOutilParReel(rel) && outilAdapte(manifeste, rel, client))
    .map((rel) => path.basename(rel));
  const adaptes = [...new Set([...aDeposer, ...fichiersDe(client, DEPOT, new Set()).map((rel) => path.basename(rel))])].sort();
  // Un Reel existe dès qu'il a ses prises, ses sections ou ses rendus. Un master régénéré et une
  // vidéo d'essai seuls (calage du cadrage au setup) ne font pas un Reel.
  const reel = Boolean(inacheve) || adaptes.length > 0 || perso.some((rel) => /^(derush|compositions|renders)\//.test(rel));
  if (!reel) return perso.length || caches.length || elements.some((e) => e !== "work") ? { reel: false, elements, caches, perso } : null;
  const meta = inacheve ? JSON.parse(lireTexte(path.join(inacheve, "meta.json"))).monteurIa : null;
  const quand = perso.map((rel) => fs.statSync(path.join(client, rel)).mtime).sort((a, b) => b - a)[0] ?? new Date();
  return { reel: true, elements, caches, perso, adaptes, aDeposer, inacheve,
    sujet: meta?.sujet ?? (sujet || sujetDevine(client)), sujetDevine: !meta?.sujet && !sujet,
    date: meta?.date ?? (date || jour(quand)), dateDevinee: !meta?.date && !date,
    master: perso.includes("index.html"), finals: perso.filter((rel) => rel.startsWith("renders/") && /FINAL/.test(path.basename(rel))) };
}

// Noms de dossier Monteur IA laissés par défaut (tools/nouveau_reel.py) : ils ne disent rien du client.
const NOMS_PAR_DEFAUT = new Set(["monteur-ia", "monteur-ia-main", "monteur ia", "monteur-ia-template"]);
const propre = (texte) => String(texte).replace(/[<>:"/\\|?*\x00-\x1f]/g, "-").replace(/\s+/g, " ")
  .replace(/^[ .-]+|[ .-]+$/g, "").slice(0, 60).replace(/[ .-]+$/, "");

/** Le nom que le Reel prendra dans l'app, calculé comme tools/nouveau_reel.py : « sujet · date · client ». */
export function nomDuReel(client, sujet, date) {
  let marque = null;
  for (const nom of ["brand.config.json", "brand.config.example.json"]) {
    try {
      marque = String(JSON.parse(lireTexte(path.join(client, nom))).brand?.name ?? "").trim() || null;
      break;
    } catch { /* absent ou illisible : le suivant */ }
  }
  marque ??= NOMS_PAR_DEFAUT.has(path.basename(client).trim().toLowerCase()) ? null : path.basename(client);
  return [sujet, date, marque].filter((x) => x && propre(x)).map(propre).join(" · ");
}

/** Le sujet du Reel en cours, deviné depuis ses coupes (derush/<slug>_cuts.json). */
function sujetDevine(client) {
  const sections = path.join(client, "tools/sections.py");
  const viaSections = existe(sections) && /CUTS_PATH\s*=\s*ROOT\s*\/\s*["']derush\/(.+?)_cuts\.json["']/.exec(lireTexte(sections));
  const slug = viaSections?.[1] ?? fichiersDe(client, "derush", new Set()).map((f) => /([^/]+)_cuts\.json$/.exec(f)?.[1]).find(Boolean);
  return slug && slug !== "exemple" ? slug.replace(/[-_]+/g, " ").trim() : "Reel en cours";
}

/** Le master peut-il être régénéré sans perdre une adaptation (un outil qu'on ne sait pas reporter) ? */
const masterRegenerable = (adaptes) => adaptes.every((n) => PORTABLES.has(n));

export const aucunChangement = (plan) => !plan.moteur.length && !plan.obsoletes.length && !plan.plan;

// --- affichage ------------------------------------------------------------------------------------
const nomExtension = (cle) => EXTENSIONS[cle]?.nom ?? cle;

/** Les extensions à mettre à jour après le moteur, et où trouver leur nouvelle version. */
function lignesExtensions(plan) {
  const l = plan.extensionsAMettreAJour.map((cle) => {
    const e = EXTENSIONS[cle];
    if (e.depot) return `  à mettre à jour ensuite : ${e.nom}, nouvelle version sur https://github.com/${e.depot}`;
    const installee = plan.versionPackSfx ? `version ${plan.versionPackSfx} installée` : "version installée inconnue";
    return `  à mettre à jour ensuite : ${e.nom} (${installee}, il faut la ${e.versionMin} ou plus),`
      + " pack-sfx.zip à retélécharger depuis la formation";
  });
  const connus = new Set(plan.extensions.flatMap((cle) => (EXTENSIONS[cle]?.outils ?? []).map((o) => `tools/${o}`)));
  const autres = plan.outilsExtensions.filter((rel) => !connus.has(rel));
  if (autres.length) l.push(`  à réinstaller avec leur nouvelle version (outils écrits pour Monteur IA 1) : ${autres.join(", ")}`);
  return l;
}

export function decrire(plan) {
  const l = [];
  const par = (action) => plan.moteur.filter((m) => m.action === action).map((m) => m.rel);
  const remplaces = ["remplace", "remplace-modifie", "modele", "gitignore"].reduce((n, a) => n + par(a).length, 0);
  l.push(`Dossier : ${plan.client}`);
  if (aucunChangement(plan)) {
    const extensions = lignesExtensions(plan);
    return extensions.length ? [l[0], "Moteur déjà à jour.", "• Extensions :", ...extensions].join("\n")
      : `${l[0]}\nDéjà à jour : rien à faire.`;
  }
  l.push(plan.v2 ? "Version : Monteur IA 2, mise à jour du moteur."
    : "Version : Monteur IA 1 (un seul plan de travail) : passage à « un Reel = un projet », pour l'app HyperFrames.");
  l.push(`• Moteur : ${remplaces} fichier(s) remplacé(s), ${par("ajout").length} ajouté(s), ${plan.obsoletes.length} retiré(s) (ancienne version).`);
  const perso = [...par("fusion-zones"), ...par("fusion-json"), ...par("garde")];
  if (perso.length) l.push(`• Ta personnalisation, gardée : ${perso.join(", ")}`);
  const retouches = [...par("remplace-modifie"), ...plan.moteur.filter((m) => m.retouche)
    .map((m) => `${m.rel} (${m.action === "modele" ? "hors consignes des extensions" : "hors zones personnalisées"})`)];
  if (retouches.length) {
    l.push(`• Fichiers du moteur que tu avais retouchés (ta version reste dans la sauvegarde) : ${retouches.join(", ")}`);
  }
  l.push(`• Extensions : ${plan.extensions.length
    ? `${plan.extensions.map(nomExtension).join(", ")} (leurs consignes et leurs réglages sont gardés)` : "aucune"}`);
  l.push(...lignesExtensions(plan));
  const p = plan.plan;
  if (p && !p.reel) {
    l.push(p.perso.length
      ? `• Plan de travail de la racine : pas de Reel en cours (${p.perso.length} fichier(s) d'essai, ex. le calage du cadrage), rangé dans la sauvegarde.`
      : "• Plan de travail de la racine : tel que livré, retiré (chaque Reel aura son dossier dans reels/).");
  } else if (p) {
    l.push(p.inacheve ? `• Reprise de la mise à jour interrompue : Reel « ${path.basename(p.inacheve)} ».`
      : `• Reel en cours : déplacé dans reels/, il s'appellera « ${nomDuReel(plan.client, p.sujet, p.date)} » dans l'app`
        + (p.sujetDevine || p.dateDevinee
          ? ` (${p.sujetDevine ? `sujet « ${p.sujet} » deviné` : `sujet « ${p.sujet} »`}, date du ${p.date}${p.dateDevinee ? " devinée" : ""} :`
            + " modifiables avec --sujet et --date)."
          : "."));
    if (p.adaptes.length) l.push(`  ses outils adaptés le suivent : ${p.adaptes.join(", ")}`);
    if (p.finals.length) {
      l.push(`  ses vidéos finales vont dans son dossier exports/, suffixées ${SUFFIXE_ANCIEN} : ${p.finals.map((f) => path.basename(f)).join(", ")}`);
    }
    if (p.master && masterRegenerable(p.adaptes)) l.push("  son master sera régénéré pour l'export natif (visage net, sons dans le montage).");
  }
  if (plan.premiereVideoFaite) {
    l.push("• Première vidéo : tu as déjà monté des Reels, je le note dans tes réglages (pas de montage d'essai ni de débrief à refaire).");
  }
  l.push(`• Jamais touchés : ${plan.premiereVideoFaite ? "tes autres réglages" : "tes réglages"} et ton style (brand.config.json, brand/), ton profil de voix, tes CTA et tes polices,${plan.consignesPerso ? " tes consignes perso," : ""}`
    + " tes images, logos, musiques et sons, tes extensions, stories/, double-ia.config.json, tes Reels.");
  return l.join("\n");
}

// --- application ------------------------------------------------------------------------------------
const horodatage = (d) => `${jour(d)}-${z(d.getHours())}h${z(d.getMinutes())}-${z(d.getSeconds())}`;

/** Copie un fichier ou un dossier du client dans la sauvegarde. */
function sauvegarder(client, rel, sauvegarde) {
  const src = path.join(client, rel);
  if (!existe(src)) return;
  const dest = path.join(sauvegarde, "moteur", rel);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.cpSync(src, dest, { recursive: true });
}

/** Deux fichiers au contenu identique (lu par blocs : un rush ne tient pas en mémoire). */
function memesOctets(a, b) {
  if (!fs.statSync(a).isFile() || !fs.statSync(b).isFile() || fs.statSync(a).size !== fs.statSync(b).size) return false;
  const [fa, fb] = [fs.openSync(a, "r"), fs.openSync(b, "r")];
  const [ba, bb] = [Buffer.alloc(1 << 20), Buffer.alloc(1 << 20)];
  try {
    for (;;) {
      const n = fs.readSync(fa, ba, 0, ba.length, null);
      if (n !== fs.readSync(fb, bb, 0, bb.length, null) || !ba.subarray(0, n).equals(bb.subarray(0, n))) return false;
      if (n === 0) return true;
    }
  } finally {
    fs.closeSync(fa);
    fs.closeSync(fb);
  }
}

/** Déplace (renommage, ou copie puis suppression d'un disque à l'autre), sans écraser sauf `ecrasable(dest)`. */
function deplacer(src, dest, ecrasable = () => false) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (ecrasable(dest)) fs.rmSync(dest, { force: true });
  // Déjà copié par une mise à jour interrompue : il ne reste qu'à retirer l'original.
  if (existe(dest) && memesOctets(src, dest)) {
    fs.rmSync(src, { force: true });
    return dest;
  }
  let cible = dest;
  for (let n = 2; existe(cible); n += 1) {
    const { dir, name, ext } = path.parse(dest);
    cible = path.join(dir, `${name} (${n})${ext}`);
  }
  try {
    fs.renameSync(src, cible);
  } catch {
    fs.cpSync(src, cible, { recursive: true });
    fs.rmSync(src, { recursive: true, force: true });
  }
  return cible;
}

/** Retire un dossier s'il ne contient plus que des dossiers vides. */
function retirerVides(dir) {
  if (!existe(dir) || !fs.statSync(dir).isDirectory()) return;
  for (const e of fs.readdirSync(dir)) retirerVides(path.join(dir, e));
  if (!fs.readdirSync(dir).length) fs.rmdirSync(dir);
}

/** Fichier de démo d'un Reel neuf (copie exacte de templates/demo/) : le travail du client le remplace. */
function estDemoNeuve(reel, fichier) {
  const demo = path.join(NEUF, "templates", "demo", `${path.relative(reel, fichier)}.demo`);
  return existe(fichier) && existe(demo) && fs.readFileSync(fichier).equals(fs.readFileSync(demo));
}

function pythonDisponible() {
  for (const cmd of WIN ? ["python", "py", "python3"] : ["python3", "python"]) {
    const r = spawnSync(cmd, ["--version"], { encoding: "utf8" });
    if (r.status === 0 && /Python 3\./.test(`${r.stdout}${r.stderr}`)) return cmd;
  }
  throw new Error("Python 3 introuvable (installé avec Monteur IA : voir INSTALL.md). Rien n'a été modifié.");
}

function lancer(cmd, args, cwd) {
  // Windows : npm et hyperframes sont des .cmd, lancés par le shell ; un chemin avec espaces est cité.
  const shell = WIN && /\.cmd$/.test(cmd);
  const cite = (s) => (shell && /[\s&()^]/.test(s) ? `"${s}"` : s);
  const r = spawnSync(cite(cmd), args.map(cite), { cwd, encoding: "utf8", shell, maxBuffer: 1 << 26,
    env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" } });
  return { ok: r.status === 0, sortie: `${r.stdout ?? ""}${r.stderr ?? ""}${r.error ? r.error.message : ""}`.trim() };
}

/** Termine la reprise d'un Reel (relançable) : outils adaptés reportés, master régénéré pour l'export natif. */
function terminer(reel, python, client) {
  const anciennes = fichiersDe(reel, "exports", new Set()).filter((rel) => rel.includes(SUFFIXE_ANCIEN));
  const faits = [`montage, dérush, vidéo et rendus déplacés${anciennes.length
    ? ` (vidéos finales dans exports/, suffixées ${SUFFIXE_ANCIEN} : un nouvel export ne les écrase pas)` : ""}`];
  const reste = [];
  const reference = path.join(reel, "work", "migration-v1");
  const adaptes = fichiersDe(reel, DEPOT, new Set()).map((rel) => path.basename(rel)).sort();
  // Pack SFX de Monteur IA 1 : sa liste (work/sfx_events.json) est celle que le client a écoutée en
  // dernier ; elle gagne sur la liste de départ de build_sfx.py, que seul le pack posera (étape 6).
  const listePack = listeDeSons(path.join(reel, "work", "sfx_events.json"));
  let sonsReportes = false;
  for (const nom of adaptes) {
    const ancien = lireTexte(path.join(reel, DEPOT, nom));
    const dest = path.join(reel, "tools", nom);
    const sons = nom === "build_sfx.py" && existe(dest) ? reporterSons(ancien, lireTexte(dest)) : null;
    if (PAR_REEL_TELS_QUELS.has(nom)) fs.writeFileSync(dest, ancien);
    else if (nom === "montage_captions.py") fs.writeFileSync(dest, cheminsDepuisLaRacine(ancien));
    else if (sons) {
      fs.writeFileSync(dest, sons);
      sonsReportes = true;
    } else reste.push(`tools/${nom} : ta version adaptée (${DEPOT}/${nom}) est à reporter dans la nouvelle.`);
  }
  if (adaptes.length) faits.push(`outils adaptés repris : ${adaptes.join(", ")}`);

  // Sous-compositions : chemins depuis la racine du projet (format HyperFrames 0.8).
  let corriges = 0;
  for (const rel of fichiersDe(reel, "compositions", new Set()).filter((f) => f.endsWith(".html"))) {
    const fichier = path.join(reel, rel);
    const html = lireTexte(fichier);
    if (cheminsDepuisLaRacine(html) !== html) {
      fs.writeFileSync(fichier, cheminsDepuisLaRacine(html));
      corriges += 1;
    }
  }
  if (corriges) faits.push(`${corriges} sous-composition(s) passée(s) au format HyperFrames 0.8`);

  // Master régénéré : visages pré-cadrés en pleine résolution, sons posés dans le montage.
  const index = path.join(reel, "index.html");
  const master = existe(index) && !estDemoNeuve(reel, index);
  if (master && masterRegenerable(adaptes)) {
    fs.mkdirSync(reference, { recursive: true });
    if (!existe(path.join(reference, "index.html"))) fs.copyFileSync(index, path.join(reference, "index.html"));
    if (existe(path.join(reel, "assets/video/base.mp4"))) {
      const visages = lancer(python, ["tools/build_faces.py"], reel);
      if (visages.ok) faits.push("visages pré-cadrés en pleine résolution (assets/video/visage-*.mp4)");
      else reste.push(`visages : python3 tools/build_faces.py a échoué :\n${visages.sortie.slice(-600)}`);
    }
    const regeneration = lancer(python, ["tools/build_master.py", "--write"], reel);
    if (!regeneration.ok) {
      reste.push(`master : python3 tools/build_master.py --write a échoué, l'ancien est resté en place :\n${regeneration.sortie.slice(-600)}`);
    } else {
      faits.push("master régénéré pour l'export natif (l'ancien : work/migration-v1/index.html)");
      if (sonsReportes && !listePack) {
        const sons = lancer(python, ["tools/build_sfx.py"], reel);
        if (sons.ok) faits.push("sons et musique posés dans le montage (bloc SONS de index.html)");
        else reste.push(`sons : python3 tools/build_sfx.py a échoué (liste reportée, à vérifier) :\n${sons.sortie.slice(-600)}`);
      }
    }
  } else if (master) {
    reste.push("master : à régénérer pour l'export natif (python3 tools/build_faces.py, puis"
      + " python3 tools/build_master.py --write) une fois les outils adaptés reportés.");
  }
  // Logos, images et polices de la maison que le montage utilise : le Reel en garde sa copie.
  const medias = copierMediasPartages(reel, client);
  if (medias.copies.length) {
    faits.push(`médias de ton dossier Monteur IA copiés dans le Reel, qui se suffit à lui-même : ${medias.copies.join(", ")}`);
  }
  if (medias.introuvables.length) {
    reste.push(`fichiers que le montage utilise, introuvables dans le Reel comme dans le dossier Monteur IA : ${medias.introuvables.join(", ")}`
      + " (à retrouver, ou à retirer du montage).");
  }
  // Pack SFX de Monteur IA 1 : sa liste de sons a suivi le Reel, mais seul le Pack SFX 1.1 sait la
  // poser dans un montage ; build_sfx.py, lui, ne la lit pas.
  if (listePack) {
    reste.push("sons : la liste du Pack SFX a suivi le Reel (work/sfx_events.json), ses sons ne sont pas encore"
      + " dans le montage. Pack SFX à jour (1.1.0 ou plus), lance python3 tools/sfx_mix.py depuis le Reel.");
  }

  fs.mkdirSync(path.join(reel, "work"), { recursive: true });
  fs.writeFileSync(path.join(reel, "work", "MIGRATION.md"), ["# Reel repris de Monteur IA 1", "",
    `Déplacé le ${jour(new Date())} depuis le plan de travail de la racine du dossier Monteur IA.`,
    ...(existe(reference) ? ["Versions d'origine (master, outils adaptés) : `work/migration-v1/`."] : []), "",
    "## Fait", ...faits.map((f) => `- ${f}`), "",
    "## Reste à faire", ...(reste.length ? reste.map((f) => `- ${f}`) : ["- rien"]), ""].join("\n"));
  return { faits, reste };
}

/** Vrai si ce fichier est une liste de sons du Pack SFX : non vide, chaque son nommé (« sfx ») ou
 *  désigné par son fichier (« file »). Une liste mal formée ne passe pas devant build_sfx.py. */
function listeDeSons(fichier) {
  try {
    const data = JSON.parse(lireTexte(fichier));
    const sons = Array.isArray(data) ? data : data?.events ?? [];
    return sons.length > 0 && sons.every((s) => estObjet(s) && (typeof s.sfx === "string" || typeof s.file === "string"));
  } catch {
    return false;
  }
}

/** Note du Reel en cours de création (racine du dossier, hors du plan de travail qui déménage) :
 *  une coupure entre sa création et son marquage ne doit pas en créer un second. */
const NOTE_CREATION = ".monteur-ia-reel-en-creation";

/** Déplace le Reel en cours de la racine dans reels/ (ou reprend un déplacement interrompu). */
function migrerReel(client, p, python) {
  let reel = p.inacheve;
  const note = path.join(client, NOTE_CREATION);
  const reels = path.join(client, "reels");
  if (!reel && existe(note)) {
    const nom = lireTexte(note).trim();
    const dossier = nom && path.join(reels, nom);
    if (dossier && existe(path.join(dossier, "meta.json"))) reel = dossier;
    // Coupé pendant la copie de la démo (pas encore de meta.json) : ce dossier n'a rien du client.
    else if (dossier && existe(dossier)) fs.rmSync(dossier, { recursive: true, force: true });
  }
  if (!reel) {
    const avant = new Set(existe(reels) ? fs.readdirSync(reels) : []);
    fs.writeFileSync(note, `${nomDuReel(client, p.sujet, p.date)}\n`);
    const creation = lancer(python, ["tools/nouveau_reel.py", p.sujet, "--date", p.date], client);
    const nouveaux = existe(reels) ? fs.readdirSync(reels).filter((n) => !avant.has(n)) : [];
    if (nouveaux.length !== 1) throw new Error(`création du dossier du Reel impossible :\n${creation.sortie}`);
    reel = path.join(reels, nouveaux[0]);
    fs.writeFileSync(note, `${nouveaux[0]}\n`);
  }
  marquer(reel, "en-cours");
  // Le travail du client remplace la démo de départ du Reel ; les fichiers de démo de l'ancienne
  // version restent derrière (le Reel a ceux de la nouvelle). Les outils déposés le suivent.
  const aDeplacer = [...new Set([...p.perso, ...fichiersDe(client, DEPOT, new Set())])].filter((rel) => existe(path.join(client, rel)));
  for (const rel of aDeplacer) {
    let dest = path.join(reel, rel);
    if (rel.startsWith("renders/") && /FINAL/.test(path.basename(rel))) {
      const { name, ext } = path.parse(rel);
      dest = path.join(reel, "exports", `${name}${SUFFIXE_ANCIEN}${ext}`);
    } else if (rel.startsWith("renders/")) dest = path.join(reel, "work", rel.slice("renders/".length));
    deplacer(path.join(client, rel), dest, (d) => estDemoNeuve(reel, d));
  }
  for (const el of p.elements) if (el !== "work") fs.rmSync(path.join(client, el), { recursive: true, force: true });
  retirerVides(path.join(client, "work", "migration-v1"));
  for (const c of p.caches) deplacer(path.join(client, c), path.join(reel, c));
  const { faits, reste } = terminer(reel, python, client);
  marquer(reel, "faite");
  fs.rmSync(note, { force: true });
  return { reel, faits, reste };
}

/** Applique le plan. Renvoie la sauvegarde, le Reel déplacé et les avertissements. */
export function appliquer(plan, { now = new Date(), npm = true } = {}) {
  const client = plan.client;
  const sauvegarde = path.join(client, `.sauvegarde-mise-a-jour-${horodatage(now)}`);
  const resultat = { sauvegarde, reel: null, avertissements: [] };
  const p = plan.plan;
  const python = p?.reel ? pythonDisponible() : null;   // vérifié avant la moindre écriture

  // 0. Monteur IA 1 qui a déjà livré des Reels : noté avant tout le reste (une fois le moteur posé,
  //    le dossier passe pour un Monteur IA 2 et une reprise ne le saurait plus).
  if (plan.premiereVideoFaite) {
    sauvegarder(client, "brand.config.json", sauvegarde);
    const fichier = path.join(client, "brand.config.json");
    const config = JSON.parse(lireTexte(fichier));
    config.setup = { ...(estObjet(config.setup) ? config.setup : {}), firstVideoDone: true };
    fs.writeFileSync(fichier, `${JSON.stringify(config, null, 2)}\n`);
  }

  // 1. Sauvegarde de ce qui va bouger dans le moteur ; les outils adaptés au Reel en cours sont mis
  //    de côté dans son plan de travail : ils le suivront, même si la mise à jour est interrompue.
  const aSauver = [...plan.obsoletes, ...plan.moteur.filter((m) => !["ajout", "garde"].includes(m.action)).map((m) => m.rel)];
  for (const rel of new Set(aSauver)) sauvegarder(client, rel, sauvegarde);
  for (const nom of p?.aDeposer ?? []) {
    fs.mkdirSync(path.join(client, DEPOT), { recursive: true });
    fs.copyFileSync(path.join(client, "tools", nom), path.join(client, DEPOT, nom));
  }

  // 2. Moteur : chaque contenu est calculé avant la première écriture.
  const ecritures = plan.moteur.filter((m) => m.action !== "garde").map(({ rel, action }) =>
    [rel, ["ajout", "remplace", "remplace-modifie"].includes(action) ? null : fusion(action, rel, client)]);
  for (const [rel, contenu] of ecritures) {
    const dest = path.join(client, rel);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    if (contenu === null) fs.copyFileSync(path.join(NEUF, rel), dest);
    else fs.writeFileSync(dest, contenu);
  }
  for (const rel of plan.obsoletes) {
    fs.rmSync(path.join(client, rel), { force: true });
    for (let dir = path.dirname(path.join(client, rel)); dir !== client && existe(dir) && !fs.readdirSync(dir).length;
      dir = path.dirname(dir)) fs.rmdirSync(dir);
  }

  // 3. Plan de travail de la racine (Monteur IA 1) : le Reel en cours part dans reels/ ; sinon
  //    les essais rejoignent la sauvegarde et la démo livrée est retirée.
  if (p?.reel) resultat.reel = migrerReel(client, p, python);
  else if (p) {
    for (const rel of p.perso) deplacer(path.join(client, rel), path.join(sauvegarde, "plan-de-travail", rel));
    for (const el of p.elements) if (el !== "work") fs.rmSync(path.join(client, el), { recursive: true, force: true });
    for (const c of p.caches) fs.rmSync(path.join(client, c), { recursive: true, force: true });
  }

  // 4. Accueil, instructions de chaque projet, style et outils des Reels.
  const sync = lancer(process.execPath, ["scripts/sync.mjs"], client);
  if (!sync.ok) resultat.avertissements.push(`npm run sync a échoué :\n${sync.sortie.slice(-1500)}`);

  // 5. Dépendances (la version de HyperFrames de l'app), puis contrôle du Reel déplacé.
  if (npm) {
    const install = lancer(WIN ? "npm.cmd" : "npm", ["install", "--no-fund", "--no-audit"], client);
    if (!install.ok) resultat.avertissements.push(`npm install a échoué (à relancer dans le dossier) :\n${install.sortie.slice(-1500)}`);
    else resultat.npm = true;
    if (install.ok && resultat.reel) {
      const cli = path.join(client, "node_modules", ".bin", WIN ? "hyperframes.cmd" : "hyperframes");
      resultat.reel.controle = lancer(cli, ["lint", resultat.reel.reel], client);
    }
  }
  return resultat;
}

// --- ligne de commande -------------------------------------------------------------------------------
function options(argv) {
  const valeur = (nom) => {
    const i = argv.indexOf(nom);
    return i !== -1 ? argv[i + 1] : null;
  };
  const prises = new Set(["--sujet", "--date"].map(valeur).filter(Boolean));
  return { dossier: argv.find((a) => !a.startsWith("--") && !prises.has(a)), sujet: valeur("--sujet"),
    date: valeur("--date"), appliquer: argv.includes("--appliquer"), npm: !argv.includes("--sans-npm") };
}

const dedans = (a, b) => {
  const rel = path.relative(b, a);
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
};

function main(argv) {
  if (argv[0] === "--manifeste") {
    const m = genererManifeste(argv[1] || "origin/main");
    console.log(`${MANIFESTE} : ${Object.keys(m.fichiers).length} fichiers, ${m.versions} versions (${m.ref}).`);
    return 0;
  }
  const o = options(argv);
  if (!o.dossier) {
    console.error('Usage : node scripts/mettre-a-jour.mjs "<dossier Monteur IA>" [--appliquer] [--sujet "<sujet>"] [--date AAAA-MM-JJ]');
    return 2;
  }
  const client = path.resolve(o.dossier.replace(/^~(?=$|[\\/])/, process.env.HOME || process.env.USERPROFILE || "~"));
  if (dedans(NEUF, client) || dedans(client, NEUF)) {
    console.error("La nouvelle version et ton dossier Monteur IA doivent être deux dossiers séparés"
      + " (ex. la nouvelle dans Téléchargements). Déplace la nouvelle version, puis relance.");
    return 2;
  }
  if (!estMonteurIA(client)) {
    console.error(`${client} n'est pas un dossier Monteur IA (il y manque templates/AGENT.md.tpl, scripts/sync.mjs ou tools/).`);
    return 2;
  }
  if (o.date && !/^\d{4}-\d{2}-\d{2}$/.test(o.date)) {
    console.error("La date s'écrit AAAA-MM-JJ.");
    return 2;
  }
  const plan = planifier(client, { sujet: o.sujet, date: o.date });
  console.log(decrire(plan));
  if (aucunChangement(plan)) return 0;
  if (!o.appliquer) {
    console.log("\nÀ blanc : rien n'a été modifié. Relance avec --appliquer pour mettre à jour.");
    return 0;
  }
  let r;
  try {
    r = appliquer(plan, { npm: o.npm });
  } catch (error) {
    console.error(`\n❌ ${error.message}\nRien n'est perdu (sauvegarde dans le dossier). Relance la même commande :`
      + " la mise à jour reprend là où elle s'est arrêtée.");
    return 1;
  }
  console.log(`\n✅ Mis à jour. Sauvegarde : ${path.relative(client, r.sauvegarde)}/`);
  if (r.npm) console.log("Version de HyperFrames de l'app installée (npm install).");
  if (r.reel) {
    console.log(`Reel déplacé : ${path.relative(client, r.reel.reel)}`);
    for (const f of r.reel.faits) console.log(`  ✓ ${f}`);
    for (const f of r.reel.reste) console.log(`  ⚠️ ${f}`);
    if (r.reel.controle) {
      console.log(`  contrôle HyperFrames (lint) : ${r.reel.controle.ok ? "OK" : "à revoir"}`);
      if (!r.reel.controle.ok) console.log(r.reel.controle.sortie.slice(-1500));
    }
  }
  for (const a of r.avertissements) console.log(`⚠️ ${a}`);
  const extensions = plan.extensionsAMettreAJour.map(nomExtension);
  console.log("\nEnsuite : node scripts/app-hyperframes.mjs brancher (une fois par ordinateur)"
    + (extensions.length ? `, puis mets à jour : ${extensions.join(", ")} (MISE-A-JOUR.md, étape 6).`
      : plan.outilsExtensions.length ? ", puis réinstalle tes extensions avec leur nouvelle version." : "."));
  return r.avertissements.length ? 1 : 0;
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
