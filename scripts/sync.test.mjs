import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Chaque test travaille dans une copie temporaire, supprimée à la fin du test.
function fixture(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-onboarding-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  for (const file of ['scripts/sync.mjs', 'templates', 'assets/fonts', 'brand.config.example.json', 'hyperframes.json',
    '.claude/skills/setup', '.claude/skills/motion-design']) {
    const dest = path.join(dir, file);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.cpSync(path.join(root, file), dest, { recursive: true });
  }
  fs.mkdirSync(path.join(dir, 'brand'));
  write(dir, 'skills-lock.json', { skills: { framework: {} } });
  return dir;
}
function write(dir, name, value) {
  const dest = path.join(dir, name);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, typeof value === 'string' ? value : JSON.stringify(value));
}
const read = (dir, name) => fs.readFileSync(path.join(dir, name), 'utf8');
const sync = (dir, ...args) => execFileSync(process.execPath, ['scripts/sync.mjs', ...args],
  { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
const config = () => JSON.parse(read(root, 'brand.config.example.json'));

test('un dossier neuf fonctionne en Papier sans identité ni questionnaire', (t) => {
  const dir = fixture(t);
  const output = sync(dir);
  assert.match(output, /Personnalisation possible plus tard/);
  assert.doesNotMatch(output, /⚠️|❌|obligatoire|PAS ENCORE PERSONNALISÉ/);
  assert.match(read(dir, 'brand/tokens.css'), /--brand-bg: #f7f7f5/);
  assert.match(read(dir, 'brand/fonts.css'), /Inter-900.woff2/);
  assert.equal(fs.existsSync(path.join(dir, 'brand.config.json')), false);
  const codex = read(dir, 'AGENTS.md');
  const claude = read(dir, 'CLAUDE.md');
  assert.match(codex, /Codex : \*\*ouvre le fichier\*\*/);
  assert.match(claude, /Claude Code : utilise l'outil/);
  assert.match(codex, /Le setup n'est jamais un prérequis/);
  assert.match(codex, /references\/premier-montage.md/);
  assert.doesNotMatch(codex + claude, /\{\{#|\{\{\//);
  const normalized = read(dir, '.agents/skills/motion-design/SKILL.md')
    .split('\n').filter(line => !line.startsWith('<!-- Copie générée')).join('\n');
  assert.equal(normalized, read(dir, '.claude/skills/motion-design/SKILL.md'));
});

test('la préparation du template ne fuit ni ne modifie une identité personnelle', (t) => {
  const dir = fixture(t);
  const own = config();
  own.brand.name = 'MARQUE_PRIVEE_TEST';
  own.visual = { stylePreset: 'midnight', accent: '#abcdef' };
  write(dir, 'brand.config.json', own);
  const before = read(dir, 'brand.config.json');
  sync(dir, '--template');
  assert.equal(read(dir, 'brand.config.json'), before);
  for (const file of ['AGENTS.md', 'CLAUDE.md', 'brand/tokens.css']) {
    assert.doesNotMatch(read(dir, file), /MARQUE_PRIVEE_TEST|#abcdef/);
  }
  sync(dir);
  assert.equal(read(dir, 'brand.config.json'), before);
  assert.match(read(dir, 'CLAUDE.md'), /MARQUE_PRIVEE_TEST/);
  assert.match(read(dir, 'brand/tokens.css'), /--brand-accent: #abcdef/);
});

test("les copies de skills suivent la source à l'identique et sont idempotentes", (t) => {
  const dir = fixture(t);
  write(dir, '.agents/skills/setup/references/perime.md', 'consigne périmée');
  write(dir, '.agents/skills/framework/SKILL.md', '# Source framework');
  write(dir, '.claude/skills/framework/perime.md', 'copie périmée');
  sync(dir);
  const before = read(dir, '.agents/skills/setup/SKILL.md');
  sync(dir);
  assert.equal(read(dir, '.agents/skills/setup/SKILL.md'), before);
  assert.equal(fs.existsSync(path.join(dir, '.agents/skills/setup/references/perime.md')), false);
  assert.equal(fs.existsSync(path.join(dir, '.claude/skills/framework/perime.md')), false);
  assert.equal(read(dir, '.claude/skills/framework/SKILL.md'), '# Source framework');
});

test('les préférences apprises au débrief arrivent dans les fichiers agent', (t) => {
  const dir = fixture(t);
  let claude = (sync(dir), read(dir, 'CLAUDE.md'));
  assert.match(claude, /première vidéo pas encore faite/);
  assert.match(claude, /Aucune pour l'instant/);
  const own = config();
  own.montage.preferences = ['Pas d\'animation par-dessus le visage', '  ', 'Sous-titres {{GRANDS}}\nen jaune'];
  own.setup.firstVideoDone = true;
  write(dir, 'brand.config.json', own);
  sync(dir);
  for (const file of ['CLAUDE.md', 'AGENTS.md']) {
    const text = read(dir, file);
    assert.match(text, /première vidéo faite/);
    assert.match(text, /^- Pas d'animation par-dessus le visage$/m);
    assert.match(text, /^- Sous-titres GRANDS en jaune$/m);
    assert.doesNotMatch(text, /Aucune pour l'instant|\{\{GRANDS/);
  }
  sync(dir, '--template');
  assert.doesNotMatch(read(dir, 'CLAUDE.md'), /Pas d'animation par-dessus le visage/);
});

// Codex lit les AGENTS.md jusqu'à project_doc_max_bytes (32 Kio par défaut, cumulé sur la chaîne)
// et tronque la fin sans prévenir. Le template livré garde 2 Kio de marge pour les préférences
// apprises au débrief ; une fois personnalisé, il doit toujours tenir sous la limite.
test('AGENTS.md et CLAUDE.md tiennent dans la limite de lecture de Codex', (t) => {
  const LIMIT = 32 * 1024;
  const MARGIN = 2 * 1024;
  const dir = fixture(t);
  const size = (file) => fs.statSync(path.join(dir, file)).size;
  sync(dir, '--template');
  const accueil = 'Accueil Monteur IA';
  for (const file of ['AGENTS.md', 'CLAUDE.md', `${accueil}/AGENTS.md`, `${accueil}/CLAUDE.md`]) {
    assert.ok(size(file) <= LIMIT - MARGIN,
      `${file} livré : ${size(file)} octets, max ${LIMIT - MARGIN}. Déplacer du détail de templates/AGENT.md.tpl vers un skill.`);
  }
  const own = config();
  own.brand = { ...own.brand, name: 'Une marque au nom assez long', handle: '@une.marque.au.nom.long', firstName: 'Prénom' };
  own.montage.preferences = Array.from({ length: 8 }, (_, i) =>
    `Préférence ${i + 1} : une consigne de montage apprise au débrief, formulée en une phrase complète.`);
  own.setup.firstVideoDone = true;
  write(dir, 'brand.config.json', own);
  const reel = `reels/Un sujet de Reel volontairement assez long · 2026-10-12 · ${own.brand.name}`;
  write(dir, `${reel}/meta.json`, { monteurIa: { lieu: 'reel', etat: 'en-cours' } });
  // Les trois extensions officielles ajoutent chacune ses consignes (budget : 1 100 octets par bloc).
  for (const nom of ['double-ia', 'systeme-stories', 'pack-sfx']) {
    fs.appendFileSync(path.join(dir, 'templates/AGENT.md.tpl'), `\n<!-- BEGIN EXTENSION: ${nom} (installation) -->\n`
      + `${'Consigne extension. '.repeat(50).slice(0, 1000)}\n<!-- END EXTENSION: ${nom} -->\n`);
  }
  sync(dir);
  for (const file of ['AGENTS.md', 'CLAUDE.md', `${accueil}/AGENTS.md`, `${accueil}/CLAUDE.md`,
    `${reel}/AGENTS.md`, `${reel}/CLAUDE.md`]) {
    assert.ok(size(file) <= LIMIT, `${file} personnalisé : ${size(file)} octets, Codex en tronquerait la fin.`);
  }
});

test('les polices sont copiées à côté de fonts.css, sans chemin qui remonte', (t) => {
  const dir = fixture(t);
  sync(dir);
  const css = read(dir, 'brand/fonts.css');
  assert.doesNotMatch(css, /url\("\.\.\//, 'HyperFrames 0.8 refuse les chemins en ../');
  for (const [, file] of css.matchAll(/url\("fonts\/([^"]+)"\)/g)) {
    assert.ok(fs.existsSync(path.join(dir, 'brand', 'fonts', file)), `brand/fonts/${file} manquant`);
  }
  assert.ok(fs.readdirSync(path.join(dir, 'brand', 'fonts')).length > 0);
});

// brand/fonts/ est tenu par la synchro, mais un client a pu y déposer une police (l'ancienne consigne
// des formats statiques l'y envoyait) : elle ne doit jamais être effacée, ni écrasée en silence.
test('la synchro ne retire de brand/fonts/ que ses propres copies, jamais une police du client', (t) => {
  const dir = fixture(t);
  const fonts = (...p) => path.join(dir, 'brand', 'fonts', ...p);
  sync(dir);
  assert.ok(fs.existsSync(fonts('Anton-400.woff2')), 'Papier utilise Anton');
  write(dir, 'brand/fonts/Coluna.otf', 'POLICE DU CLIENT');
  write(dir, 'brand/fonts/Inter-900.woff2', 'INTER RETOUCHEE PAR LE CLIENT');
  write(dir, 'reels/Essai · 2026-10-12/meta.json', { monteurIa: { lieu: 'reel', etat: 'en-cours' } });
  const own = config();
  own.visual.stylePreset = 'midnight';   // Inter seulement : la copie d'Anton ne sert plus
  write(dir, 'brand.config.json', own);
  const sortie = sync(dir);
  assert.equal(read(dir, 'brand/fonts/Coluna.otf'), 'POLICE DU CLIENT', 'police du client effacée');
  assert.match(sortie, /gardée {2}brand\/fonts\/Coluna\.otf/);
  assert.equal(fs.existsSync(fonts('Anton-400.woff2')), false, 'copie devenue inutile : retirée');
  assert.ok(fs.readFileSync(fonts('Inter-900.woff2')).equals(fs.readFileSync(path.join(dir, 'assets/fonts/Inter-900.woff2'))));
  assert.equal(read(dir, 'assets/fonts/Inter-900-a-toi.woff2'), 'INTER RETOUCHEE PAR LE CLIENT', 'sa version est rangée, pas perdue');
  assert.doesNotMatch(read(dir, 'brand/fonts.css'), /Anton/);
  // Le relevé des copies reste dans la maison ; une police à jour n'est pas réécrite au passage suivant.
  const reel = path.join(dir, 'reels', 'Essai · 2026-10-12', 'brand', 'fonts');
  assert.ok(fs.existsSync(path.join(reel, 'Inter-900.woff2')));
  assert.equal(fs.readdirSync(reel).some((f) => f.startsWith('.copies')), false);
  const date = fs.statSync(fonts('Inter-900.woff2')).mtimeMs;
  sync(dir);
  assert.equal(read(dir, 'brand/fonts/Coluna.otf'), 'POLICE DU CLIENT');
  assert.equal(fs.statSync(fonts('Inter-900.woff2')).mtimeMs, date);
  // Sa source change (nouvelle version de la police) : la copie suit, sans rien ranger de plus.
  fs.appendFileSync(path.join(dir, 'assets/fonts/Inter-900.woff2'), 'v2');
  sync(dir);
  assert.ok(read(dir, 'brand/fonts/Inter-900.woff2').endsWith('v2'));
  assert.deepEqual(fs.readdirSync(path.join(dir, 'assets/fonts')).filter((f) => f.includes('-a-toi')), ['Inter-900-a-toi.woff2']);
  // Une copie dont la source a disparu de assets/fonts/ est la dernière : elle reste.
  own.visual.stylePreset = 'neutral';
  write(dir, 'brand.config.json', own);
  sync(dir);
  fs.rmSync(path.join(dir, 'assets/fonts/Anton-400.woff2'));
  own.visual.stylePreset = 'midnight';
  write(dir, 'brand.config.json', own);
  sync(dir);
  assert.ok(fs.existsSync(fonts('Anton-400.woff2')), 'dernière copie d’une police gardée');
});

test('garder Papier compte comme un choix et la taille des sous-titres est réglable', (t) => {
  const dir = fixture(t);
  const own = config();
  own.visual.stylePreset = 'neutral';
  own.visual.captionsSize = 60;
  own.setup.styleChosen = true;
  write(dir, 'brand.config.json', own);
  sync(dir);
  assert.doesNotMatch(read(dir, 'CLAUDE.md'), /personnalisable plus tard/);
  assert.doesNotMatch(read(dir, 'brand/tokens.css'), /pas encore personnalisé/);
  assert.match(read(dir, 'brand/tokens.css'), /--brand-cap-size: 60px;/);
  own.visual.captionsSize = 'énorme';
  write(dir, 'brand.config.json', own);
  sync(dir, '--style-only');
  assert.match(read(dir, 'brand/tokens.css'), /--brand-cap-size: 50px;/);
});

test('tous les presets conservent leurs couleurs et leurs polices locales', (t) => {
  const dir = fixture(t);
  const { presets, fonts } = JSON.parse(read(root, 'templates/style-presets.json'));
  for (const preset of presets) {
    const own = config();
    own.visual.stylePreset = preset.id;
    write(dir, 'brand.config.json', own);
    sync(dir, '--style-only');
    const css = read(dir, 'brand/tokens.css');
    assert.ok(css.includes(`--brand-accent: ${preset.visual.accent}`), preset.id);
    assert.doesNotMatch(css, /\{\{/);
    for (const family of [preset.visual.fontBody, preset.visual.fontCaptions]) {
      for (const face of fonts[family].faces) {
        assert.ok(read(dir, 'brand/fonts.css').includes(face.file), `${preset.id}: ${face.file}`);
      }
    }
  }
});

// ---------------------------------------------------------------------------
// Un Reel = un projet : maison, accueil et Reels (tools/nouveau_reel.py, tools/ranger_reel.py)
// ---------------------------------------------------------------------------
const git = (cwd, ...args) => execFileSync('git', args, { cwd, encoding: 'utf8' });
// Fichiers du template tels que livrés (suivis par git + nouveaux fichiers pas encore commités).
const shipped = () => git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')
  .split('\0').filter(f => f && fs.existsSync(path.join(root, f)));
const isProject = (dir) => fs.existsSync(path.join(dir, 'index.html'))
  && ['hyperframes.json', 'meta.json', 'project.json'].some(f => fs.existsSync(path.join(dir, f)));
function pythonOrSkip(t) {
  try {
    return execFileSync('python3', ['-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' }).trim();
  } catch {
    t.skip('python3 absent');
    return null;
  }
}
// Copie complète du template livré (sans les skills, inutiles ici), dans un dossier temporaire.
function maison(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-maison-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  for (const file of shipped().filter(f => !/^\.(agents|claude)\//.test(f))) {
    fs.mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
    fs.copyFileSync(path.join(root, file), path.join(dir, file));
  }
  return dir;
}

test("la racine n'est pas un projet HyperFrames ; l'accueil livré en est un, avec ses instructions", () => {
  assert.equal(isProject(root), false, 'un index.html à la racine ferait scanner tous les Reels par l’app');
  const accueil = path.join(root, 'Accueil Monteur IA');
  assert.ok(isProject(accueil), 'accueil livré incomplet');
  assert.equal(JSON.parse(read(accueil, 'meta.json')).monteurIa.lieu, 'accueil');
  for (const file of ['brand/tokens.css', 'brand/fonts.css', 'assets/vendor/gsap.min.js', 'brand/fonts/Inter-900.woff2']) {
    assert.ok(fs.existsSync(path.join(accueil, file)), `accueil sans ${file}`);
  }
  const claude = read(accueil, 'CLAUDE.md');
  assert.match(claude, /Tu es dans l'accueil de Monteur IA/);
  assert.match(claude, /`\.\.\/\.claude\/skills\/<nom>\/SKILL\.md`/);
  assert.doesNotMatch(claude, /Tu es dans le Reel|Tu es à la racine|\{\{#|\{\{\/|\{\{MAISON\}\}|\{\{REEL_NOM\}\}/);
  assert.match(read(accueil, 'AGENTS.md'), /`\.\.\/\.agents\/skills\/<nom>\/SKILL\.md`/);
  // Le gabarit d'un Reel couvre tout le plan de travail de départ.
  for (const file of ['index.html', 'compositions/captions.html', 'compositions/exemple-section.html',
    'derush/exemple_cuts.json', 'assets/video/base.mp4']) {
    assert.ok(fs.existsSync(path.join(root, 'templates/demo', `${file}.demo`)), `gabarit sans ${file}`);
  }
});

// Sous Windows, la sortie d'un outil lue par l'agent est en cp1252 : un « ✅ » ou un « · » de nom de
// Reel y faisait planter l'outil (UnicodeEncodeError), Reel pourtant créé. On simule ce terminal.
test('les outils écrivent en UTF-8 même dans un terminal Windows (cp1252)', (t) => {
  const python = pythonOrSkip(t);
  if (!python) return;
  const dir = maison(t);
  write(dir, 'brand.config.json', { ...config(), brand: { ...config().brand, name: 'Studio Lumière' } });
  const env = { ...process.env, PYTHONIOENCODING: 'cp1252', PYTHONUTF8: '0' };
  const sortie = execFileSync(python, ['tools/nouveau_reel.py', 'Méliès → 424 techniques', '--date', '2026-10-12'],
    { cwd: dir, encoding: 'utf8', env });
  assert.match(sortie, /✅/);
  assert.ok(fs.existsSync(path.join(dir, 'reels', 'Méliès → 424 techniques · 2026-10-12 · Studio Lumière', 'meta.json')));
  // Tout outil qui affiche un caractère absent de cp1252 écrit en UTF-8 (via lieux.py, ou lui-même).
  // cp1252 = Latin-1 plus ces 27 signes (0x80-0x9F) ; tout autre caractère au-delà de U+00FF plante.
  const CP1252 = '€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ';
  const horsCp1252 = (ligne) => [...ligne].some((c) => c.codePointAt(0) > 0xff && !CP1252.includes(c));
  for (const nom of fs.readdirSync(path.join(root, 'tools')).filter((f) => f.endsWith('.py'))) {
    const source = fs.readFileSync(path.join(root, 'tools', nom), 'utf8');
    const affiche = source.split('\n').some((l) => /print\(|exit\(/.test(l) && horsCp1252(l));
    if (!affiche) continue;
    assert.ok(/from lieux import|reconfigure\(encoding="utf-8"/.test(source), `${nom} affiche un caractère que Windows ne sait pas écrire`);
  }
});

test('un nouveau Reel est un projet complet, avec ses instructions, sans toucher aux autres', (t) => {
  const python = pythonOrSkip(t);
  if (!python) return;
  const dir = maison(t);
  write(dir, 'brand.config.json', { ...config(), brand: { ...config().brand, name: 'Studio Lumière' } });
  const create = (sujet) => execFileSync(python, ['tools/nouveau_reel.py', sujet, '--date', '2026-10-12'],
    { cwd: dir, encoding: 'utf8' });
  create('Méliès : 424 techniques');
  const name = 'Méliès - 424 techniques · 2026-10-12 · Studio Lumière';
  const reel = path.join(dir, 'reels', name);
  assert.ok(isProject(reel), 'le Reel ne s’ouvrirait pas dans l’app');
  const meta = JSON.parse(read(reel, 'meta.json'));
  assert.deepEqual([meta.name, meta.monteurIa.lieu, meta.monteurIa.etat], [name, 'reel', 'en-cours']);
  for (const file of ['compositions/exemple-section.html', 'derush/exemple_cuts.json', 'assets/video/base.mp4',
    'brand/tokens.css', 'brand/fonts.css', 'brand/fonts/Inter-900.woff2', 'assets/vendor/gsap.min.js',
    'tools/sections.py', 'tools/lieux.py', 'tools/build_final.py', 'tools/ranger_reel.py', 'hyperframes.json']) {
    assert.ok(fs.existsSync(path.join(reel, file)), `Reel sans ${file}`);
  }
  assert.equal(read(reel, 'brand/tokens.css'), read(dir, 'brand/tokens.css'));
  const claude = read(reel, 'CLAUDE.md');
  assert.match(claude, new RegExp(`Tu es dans le Reel « ${name} »`));
  assert.match(claude, /`\.\.\/\.\.\/\.claude\/skills\/<nom>\/SKILL\.md`/);
  assert.match(read(reel, 'AGENTS.md'), /`\.\.\/\.\.\/\.agents\/skills\/<nom>\/SKILL\.md`/);
  assert.doesNotMatch(claude, /Tu es dans l'accueil|Tu es à la racine|\{\{#|\{\{MAISON\}\}/);
  // Les outils du Reel lisent ses coupes, et les réglages dans la maison.
  const sections = execFileSync(python, ['tools/sections.py'], { cwd: reel, encoding: 'utf8' });
  assert.match(sections, /^exemple-section\s+split\s+0\.000 ->\s+8\.000/m);
  execFileSync(python, ['tools/build_master.py'], { cwd: reel, encoding: 'utf8' });
  assert.ok(fs.existsSync(path.join(reel, 'work/index.generated.html')));
  // Même sujet : un second dossier, jamais un écrasement.
  create('Méliès : 424 techniques');
  assert.ok(isProject(path.join(dir, 'reels', `${name} (2)`)));

  // Resynchroniser : les outils propres au Reel gardent ses réglages, les génériques suivent la
  // maison, le style suit tant que le Reel n'est pas publié.
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('exemple_cuts.json', 'mon-reel_cuts.json'));
  write(reel, 'tools/check_export.py', '# copie abîmée\n');
  const accent = (value) => write(dir, 'brand.config.json',
    { ...JSON.parse(read(dir, 'brand.config.json')), visual: { ...config().visual, stylePreset: 'neutral', accent: value } });
  accent('#ff0055');
  sync(dir);
  assert.match(read(reel, 'tools/sections.py'), /mon-reel_cuts\.json/);
  assert.equal(read(reel, 'tools/check_export.py'), read(dir, 'tools/check_export.py'));
  assert.match(read(reel, 'brand/tokens.css'), /#ff0055/i);
  write(reel, 'meta.json', { ...meta, monteurIa: { ...meta.monteurIa, etat: 'publie' } });
  accent('#00aa55');
  sync(dir);
  assert.match(read(reel, 'brand/tokens.css'), /#ff0055/i, 'un Reel publié doit garder son style');
  assert.match(read(path.join(dir, 'reels', `${name} (2)`), 'brand/tokens.css'), /#00aa55/i);
});

test("dupliquer un Reel garde son montage et ses outils adaptés, sans ses exports ni la copie de l'app", (t) => {
  const python = pythonOrSkip(t);
  if (!python) return;
  const dir = maison(t);
  const create = (...args) => execFileSync(python, ['tools/nouveau_reel.py', ...args], { cwd: dir, encoding: 'utf8' });
  create('Original', '--date', '2026-10-12');
  const original = path.join(dir, 'reels', `Original · 2026-10-12 · ${path.basename(dir)}`);
  write(original, 'tools/sections.py', read(original, 'tools/sections.py').replace('exemple_cuts.json', 'original_cuts.json'));
  write(original, 'compositions/s1-corps.html', '<div>section</div>');
  write(original, 'exports/FINAL.mp4', 'video');
  write(original, '.thumbnails/a.jpg', 'x');
  assert.match(create('Variante', '--date', '2026-10-13', '--depuis', original), /copie de « Original · .* »/);
  const copie = path.join(dir, 'reels', `Variante · 2026-10-13 · ${path.basename(dir)}`);
  assert.ok(isProject(copie));
  assert.match(read(copie, 'tools/sections.py'), /original_cuts\.json/, 'outils adaptés gardés');
  assert.ok(fs.existsSync(path.join(copie, 'compositions/s1-corps.html')));
  assert.deepEqual(fs.readdirSync(path.join(copie, 'exports')), [], 'les exports restent au Reel d’origine');
  assert.equal(fs.existsSync(path.join(copie, '.thumbnails')), false);
  assert.equal(JSON.parse(read(copie, 'meta.json')).name, `Variante · 2026-10-13 · ${path.basename(dir)}`);
  assert.match(read(copie, 'CLAUDE.md'), /Tu es dans le Reel « Variante · .* »/);
  // Copie faite par le bouton Duplicate de l'app, hors du dossier Monteur IA : l'outil dit quoi faire.
  const app = fs.mkdtempSync(path.join(os.tmpdir(), 'copie-app-'));
  t.after(() => fs.rmSync(app, { recursive: true, force: true }));
  fs.cpSync(original, path.join(app, 'Copy of Original'), { recursive: true });
  assert.throws(() => execFileSync(python, ['tools/ranger_reel.py'], { cwd: path.join(app, 'Copy of Original'), stdio: 'pipe' }),
    (e) => /pas rangé dans un dossier Monteur IA[\s\S]*--depuis/.test(String(e.stderr)));
});

test('ranger un Reel garde ses vidéos finales, le marque publié et ne vide rien sans --alleger', (t) => {
  const python = pythonOrSkip(t);
  if (!python) return;
  const dir = maison(t);
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-home-'));
  t.after(() => fs.rmSync(home, { recursive: true, force: true }));
  write(dir, 'brand.config.json', { ...config(), setup: { ...config().setup, firstVideoDone: false } });
  execFileSync(python, ['tools/nouveau_reel.py', 'Premier Reel', '--date', '2026-10-12'], { cwd: dir, encoding: 'utf8' });
  const reel = path.join(dir, 'reels', `Premier Reel · 2026-10-12 · ${path.basename(dir)}`);
  // Le bouton Export de l'app rend dans renders/<id>.mp4 et note le résultat à côté (aucun « FINAL »).
  const appExport = 'reel_2026-10-12_15-30-00';
  const files = { 'exports/FINAL_SFX_MUSIC.mp4': 'master', 'renders/overlay.mov': 'calque',
    [`renders/${appExport}.mp4`]: 'export app', [`renders/${appExport}.meta.json`]: JSON.stringify({ status: 'complete', exportedTo: '/nulle-part.mp4' }),
    'renders/reel_2026-10-11_09-00-00.meta.json': JSON.stringify({ status: 'failed' }),
    'derush/mon-reel_cut.mp4': 'rush', 'derush/mon-reel_cuts.json': '{}', 'work/premiere-video.md': 'étape : SFX',
    'assets/video/base.mp4': 'visage', 'snapshots/frame.png': 'png' };
  for (const [file, content] of Object.entries(files)) write(reel, file, content);
  const env = { ...process.env, HOME: home, USERPROFILE: home };
  const ranger = (...args) => execFileSync(python, ['tools/ranger_reel.py', ...args], { cwd: reel, env, encoding: 'utf8' });

  ranger();
  const archive = path.join(home, process.platform === 'win32' ? 'Videos' : 'Movies', 'reels-publies', path.basename(reel));
  assert.equal(fs.readFileSync(path.join(archive, 'FINAL_SFX_MUSIC.mp4'), 'utf8'), 'master');
  assert.equal(fs.readFileSync(path.join(archive, `${path.basename(reel)}.mp4`), 'utf8'), 'export app', 'l\'export de l\'app est rangé');
  assert.equal(JSON.parse(read(reel, 'meta.json')).monteurIa.etat, 'publie');
  assert.match(read(dir, 'work/premiere-video.md'), /débrief à faire[\s\S]*Premier Reel/);
  for (const file of Object.keys(files)) assert.ok(fs.existsSync(path.join(reel, file)), `${file} effacé sans --alleger`);

  ranger('--alleger');
  for (const file of ['derush/mon-reel_cut.mp4', 'renders/overlay.mov', 'work/premiere-video.md', 'snapshots/frame.png']) {
    assert.ok(!fs.existsSync(path.join(reel, file)), `${file} aurait dû être effacé`);
  }
  for (const file of ['exports/FINAL_SFX_MUSIC.mp4', `renders/${appExport}.mp4`, `renders/${appExport}.meta.json`, 'derush/mon-reel_cuts.json', 'assets/video/base.mp4', 'index.html']) {
    assert.ok(fs.existsSync(path.join(reel, file)), `${file} perdu par --alleger`);
  }
  // Depuis la maison, l'outil refuse au lieu de deviner un Reel.
  assert.throws(() => execFileSync(python, ['tools/ranger_reel.py'], { cwd: dir, env, stdio: 'pipe' }),
    /travaille sur un Reel/);
});

// ---------------------------------------------------------------------------
// Export natif : visages pré-cadrés et sons dans le montage (bouton Export de l'app)
// ---------------------------------------------------------------------------
function ffmpegOrSkip(t) {
  try {
    execFileSync('ffprobe', ['-version'], { stdio: 'ignore' });
    execFileSync('ffmpeg', ['-version'], { stdio: 'ignore' });
    return true;
  } catch {
    t.skip('ffmpeg absent');
    return false;
  }
}
const probeSize = (file) => execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries',
  'stream=width,height', '-of', 'csv=p=0', file], { encoding: 'utf8' }).trim();

test('les visages sont pré-cadrés en pleine résolution et posés sans agrandissement', (t) => {
  const python = pythonOrSkip(t);
  if (!python || !ffmpegOrSkip(t)) return;
  const dir = maison(t);
  execFileSync(python, ['tools/nouveau_reel.py', 'Visages', '--date', '2026-10-12'], { cwd: dir, encoding: 'utf8' });
  const reel = path.join(dir, 'reels', `Visages · 2026-10-12 · ${path.basename(dir)}`);
  // Un dérush « pleine résolution » (1,6 fois base.mp4), mêmes images : cas d'un rush DJI.
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', 'assets/video/base.mp4', '-vf', 'scale=1728:3072',
    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', 'derush/exemple_enhanced.mp4'], { cwd: reel });
  const cuts = JSON.parse(read(reel, 'derush/exemple_cuts.json'));
  write(reel, 'derush/exemple_cuts.json', { ...cuts, source: 'derush/exemple_enhanced.mp4' });
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace(
    '    ("exemple-section", "split", [0, 1, 2]),', '    ("exemple-section", "split", [0, 1]),\n    ("plein", "face", [2]),'));
  const out = execFileSync(python, ['tools/build_faces.py'], { cwd: reel, encoding: 'utf8' });
  assert.match(out, /exemple_enhanced\.mp4 \(1728x3072\)/, 'le visage doit être lu dans le dérush pleine résolution');
  assert.doesNotMatch(out, /moins net/);
  assert.equal(probeSize(path.join(reel, 'assets/video/visage-split.mp4')), '1080,1920');
  assert.equal(probeSize(path.join(reel, 'assets/video/visage-plein.mp4')), '1080,1920');
  execFileSync(python, ['tools/build_master.py', '--write'], { cwd: reel, encoding: 'utf8' });
  const master = read(reel, 'index.html');
  assert.match(master, /src="assets\/video\/visage-split\.mp4"/);
  assert.match(master, /src="assets\/video\/visage-plein\.mp4"/);
  assert.doesNotMatch(master, /\.face-(bottom|full) video \{[^}]*scale\(/, 'aucun agrandissement du visage en export natif');

  // Synchro : visages à la cadence du rendu, chaque fenêtre calée sur une image (départ juste sous la
  // frontière, entrée juste au-dessus : le rendu arrondit l'un vers le haut, l'autre vers le bas).
  const cadence = (f) => execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
    '-of', 'csv=p=0', path.join(reel, f)], { encoding: 'utf8' }).trim();
  assert.equal(cadence('assets/video/visage-split.mp4'), '30/1');
  assert.equal(cadence('assets/video/visage-plein.mp4'), '30/1');
  const videos = [...master.matchAll(/<video id="face[^"]*"[^>]*data-start="([\d.]+)" data-media-start="([\d.]+)"/g)];
  assert.ok(videos.length >= 2);
  for (const [, depart, entree] of videos) {
    const [d, e] = [Number(depart) * 30, Number(entree) * 30];
    if (d === 0) { assert.equal(e, 0); continue; }
    assert.equal(Math.ceil(d), Math.floor(e), `départ ${depart} et entrée ${entree} sur la même image`);
    assert.ok(Math.ceil(d) - d < 0.05 && e - Math.floor(e) < 0.05, 'à un centième d\'image de la frontière');
  }
});

// Le comportement du moteur que fenetre() compense, vérifié par un vrai rendu (lent) : à lancer à
// chaque nouvelle version de HyperFrames (MONTEUR_RENDU=1 npm test). Une vidéo numérotée par blocs
// remplace les visages ; à chaque image rendue, le numéro lu doit être celui de l'image.
test('rendu : le visage tombe sur la même image que la voix, dans chaque fenêtre', { skip: !process.env.MONTEUR_RENDU }, (t) => {
  const python = pythonOrSkip(t);
  if (!python || !ffmpegOrSkip(t)) return;
  const dir = maison(t);
  execFileSync(python, ['tools/nouveau_reel.py', 'Synchro', '--date', '2026-10-12'], { cwd: dir, encoding: 'utf8' });
  const reel = path.join(dir, 'reels', `Synchro · 2026-10-12 · ${path.basename(dir)}`);
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace(
    '    ("exemple-section", "split", [0, 1, 2]),', '    ("exemple-section", "split", [0, 1]),\n    ("plein", "face", [2]),'));
  // Numéro de l'image en 11 bits, blocs de 96 px, en haut (plein écran) et en bas (split).
  const numero = "if(mod(floor(N/pow(2\\,floor(X/96)))\\,2)\\,235\\,16)";
  for (const f of ['visage-split.mp4', 'visage-plein.mp4']) {
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:r=30:d=8', '-vf',
      `format=gray,geq=lum='if(lt(X\\,1056)*(lt(Y\\,200)+gt(Y\\,1700)*lt(Y\\,1900))\\,${numero}\\,16)',format=yuv420p`,
      '-c:v', 'libx264', '-crf', '10', '-r', '30', `assets/video/${f}`], { cwd: reel });
  }
  execFileSync(python, ['tools/build_master.py', '--write'], { cwd: reel, encoding: 'utf8' });
  const cli = path.join(dir, 'node_modules', '.bin', process.platform === 'win32' ? 'hyperframes.cmd' : 'hyperframes');
  execFileSync(fs.existsSync(cli) ? cli : path.join(root, 'node_modules', '.bin', 'hyperframes'), ['render', '-o', 'exports/FINAL.mp4'],
    { cwd: reel, stdio: 'ignore', timeout: 600000 });
  const lire = (y) => {
    const brut = execFileSync('ffmpeg', ['-v', 'error', '-i', path.join(reel, 'exports/FINAL.mp4'), '-vf',
      `format=gray,crop=1080:1:0:${y}`, '-f', 'rawvideo', '-'], { maxBuffer: 1 << 26 });
    return Array.from({ length: brut.length / 1080 }, (_, n) =>
      Array.from({ length: 11 }, (_, i) => (brut[n * 1080 + 48 + 96 * i] > 128 ? 1 << i : 0)).reduce((a, b) => a + b, 0));
  };
  const [haut, bas] = [lire(100), lire(1800)];
  const sections = JSON.parse(execFileSync(python, ['-c', 'import json, sys; sys.path.insert(0, "tools"); import sections; '
    + 'print(json.dumps([[s["fmt"], s["start"], s["dur"]] for s in sections.sections()]))'], { cwd: reel, encoding: 'utf8' }));
  for (const [fmt, debut, duree] of sections) {
    const lu = fmt === 'face' ? haut : bas;
    for (let n = Math.round(debut * 30) + 2; n < Math.round((debut + duree) * 30) - 2; n += 5) {
      assert.equal(lu[n], n, `section ${fmt} à ${debut} s : l'image ${n} montre l'image ${lu[n]} du visage`);
    }
  }
});

test('les sons sont posés dans le montage, survivent au master et ne sont jamais écrasés en silence', (t) => {
  const python = pythonOrSkip(t);
  if (!python || !ffmpegOrSkip(t)) return;
  const dir = maison(t);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=220:duration=12', 'assets/music/fond.mp3'], { cwd: dir });
  write(dir, 'brand.config.json', { ...config(), audio: { musicFile: 'fond.mp3', musicDb: -26.5 } });
  execFileSync(python, ['tools/nouveau_reel.py', 'Sons', '--date', '2026-10-12'], { cwd: dir, encoding: 'utf8' });
  const reel = path.join(dir, 'reels', `Sons · 2026-10-12 · ${path.basename(dir)}`);
  const run = (...args) => execFileSync(python, args, { cwd: reel, encoding: 'utf8', stdio: 'pipe' });
  // Deux sections : l'exemple d'EVENTS pose un SFX de transition à chaque nouvelle section.
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace(
    '    ("exemple-section", "split", [0, 1, 2]),', '    ("exemple-section", "split", [0, 1]),\n    ("plein", "face", [2]),'));
  run('tools/build_master.py', '--write');
  assert.match(read(reel, 'index.html'), /<!-- SONS -->/);
  run('tools/build_sfx.py');
  let master = read(reel, 'index.html');
  assert.match(master, /<hf-audio-group id="mixage"[^>]*limiter/, 'plafond du mixage manquant');
  assert.match(master, /<audio id="vo"[^>]*data-audio-group="mixage"/, 'la voix doit passer par le plafond');
  assert.match(master, /<audio id="musique" src="assets\/sons\/musique-fond\.mp3"[^>]*data-volume="0\.0473"/);
  assert.match(master, /<audio id="sfx-01" src="assets\/sons\/starter-[^"]+"[^>]*data-volume="0\.1"[^>]*data-automation=/);
  assert.ok(fs.existsSync(path.join(reel, 'assets/sons/musique-fond.mp3')), 'le Reel doit rester autonome');
  // Le master régénéré garde les sons tels quels.
  run('tools/build_master.py', '--write');
  assert.equal(read(reel, 'index.html').match(/<!-- SONS:DEBUT[\s\S]*?<!-- SONS:FIN -->/)[0],
    master.match(/<!-- SONS:DEBUT[\s\S]*?<!-- SONS:FIN -->/)[0]);
  // Un son retouché à la main (ou dans l'app) n'est pas écrasé sans --ecraser.
  write(reel, 'index.html', read(reel, 'index.html').replace(/(id="sfx-01"[^>]*data-start=")[\d.]+/, '$19.999'));
  assert.throws(() => run('tools/build_sfx.py'), (e) => /retouches a la main ou dans l'app/.test(e.stdout));
  assert.match(read(reel, 'index.html'), /data-start="9\.999"/);
  run('tools/build_sfx.py', '--ecraser');
  assert.doesNotMatch(read(reel, 'index.html'), /data-start="9\.999"/);

  // Sons trouvés dans l'app (find_sound_effect, find_music) : déposés dans assets/ du Reel, nommés
  // comme HeyGen les nomme (espaces), passés par la liste de build_sfx.py, posés sans copie.
  for (const [nom, args] of [['Whoosh Transition.mp3', 'sine=frequency=880:duration=0.6'], ['Calm Piano.mp3', 'sine=frequency=440:duration=90']]) {
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', args, path.join(reel, 'assets', nom)]);
  }
  write(reel, 'tools/build_sfx.py', read(reel, 'tools/build_sfx.py')
    .replace('MUSIQUE_REEL = None', 'MUSIQUE_REEL = "assets/Calm Piano.mp3"')
    .replace('MUSIQUE_REEL_DB = None', 'MUSIQUE_REEL_DB = -24')
    .replace('events.sort(key=lambda e: e[1])', 'events.append(("assets/Whoosh Transition.mp3", 0.8, -18, None))\nevents.sort(key=lambda e: e[1])'));
  run('tools/build_sfx.py');
  master = read(reel, 'index.html');
  assert.match(master, /<audio id="musique" src="assets\/Calm Piano\.mp3"[^>]*data-volume="0\.0631"/, 'musique du Reel, sur place');
  assert.match(master, /<audio id="sfx-01" src="assets\/Whoosh Transition\.mp3" data-start="0\.800"/, 'son de l’app, sur place');
  assert.match(master, /src="assets\/sons\/starter-/, 'la bibliothèque reste copiée dans assets/sons/');
  for (const nom of ['Whoosh Transition.mp3', 'Calm Piano.mp3', 'musique-Calm Piano.mp3']) {
    assert.equal(fs.existsSync(path.join(reel, 'assets/sons', nom)), false, `${nom} : pas de copie`);
  }
  run('tools/build_master.py', '--write');
  assert.match(read(reel, 'index.html'), /src="assets\/Whoosh Transition\.mp3"/, 'survit au master régénéré');
});

test("la vidéo glissée dans l'accueil part dans le Reel créé ; celle du client reste où elle est", (t) => {
  const python = pythonOrSkip(t);
  if (!python) return;
  const dir = maison(t);
  execFileSync('node', ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  const accueil = path.join(dir, fs.readdirSync(dir).find((n) => n.startsWith('Accueil')));
  // L'app recopie la vidéo glissée dans assets/ de l'accueil, puis donne ce chemin à l'agent.
  write(accueil, 'assets/DJI_0042.MP4', 'RUSH');
  const out = execFileSync(python, ['../tools/nouveau_reel.py', 'Méliès', '--date', '2026-10-12', '--video', 'assets/DJI_0042.MP4'],
    { cwd: accueil, encoding: 'utf8' });
  const reel = path.join(dir, 'reels', fs.readdirSync(path.join(dir, 'reels'))[0]);
  assert.match(out, /vidéo rangée dans le Reel : derush\/DJI_0042\.MP4/);
  assert.equal(fs.existsSync(path.join(accueil, 'assets/DJI_0042.MP4')), false, "plus de copie dans l'accueil");
  assert.equal(read(reel, 'derush/DJI_0042.MP4'), 'RUSH');
  assert.match(read(reel, 'work/brief.md'), new RegExp(`Vidéo brute : .*derush/DJI_0042\\.MP4`));

  // Une vidéo du client, hors du dossier Monteur IA : notée, jamais déplacée.
  const ailleurs = path.join(path.dirname(dir), `rush-client-${path.basename(dir)}.mov`);
  fs.writeFileSync(ailleurs, 'ORIGINAL');
  t.after(() => fs.rmSync(ailleurs, { force: true }));
  execFileSync(python, ['tools/nouveau_reel.py', 'Autre', '--date', '2026-10-13', '--video', ailleurs], { cwd: dir, encoding: 'utf8' });
  assert.equal(fs.readFileSync(ailleurs, 'utf8'), 'ORIGINAL');
  const autre = path.join(dir, 'reels', fs.readdirSync(path.join(dir, 'reels')).find((n) => n.includes('Autre')));
  assert.match(read(autre, 'work/brief.md'), new RegExp(`Vidéo brute : ${fs.realpathSync(ailleurs).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`));
  assert.deepEqual(fs.readdirSync(path.join(autre, 'derush')).filter((n) => /rush-client/.test(n)), []);
});

test("une synchro sans changement n'écrit rien dans l'accueil ni dans les Reels (l'app afficherait des modifications)", (t) => {
  const python = pythonOrSkip(t);
  if (!python) return;
  const dir = maison(t);
  execFileSync('node', ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  execFileSync(python, ['tools/nouveau_reel.py', 'Calme', '--date', '2026-10-12'], { cwd: dir, encoding: 'utf8' });
  const projets = fs.readdirSync(dir).filter((n) => n.startsWith('Accueil')).map((n) => path.join(dir, n))
    .concat(fs.readdirSync(path.join(dir, 'reels')).map((n) => path.join(dir, 'reels', n)));
  const dates = () => projets.flatMap((p) => fs.readdirSync(p, { recursive: true }).map((f) => path.join(p, String(f))))
    .filter((f) => fs.statSync(f).isFile()).map((f) => `${f} ${fs.statSync(f).mtimeMs}`).sort();
  const avant = dates();
  execFileSync('node', ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  assert.deepEqual(dates(), avant);
});

test("l'aperçu du dérush pose la vidéo coupée dans le montage, sans écraser un montage construit", (t) => {
  const python = pythonOrSkip(t);
  if (!python || !ffmpegOrSkip(t)) return;
  const dir = maison(t);
  execFileSync(python, ['tools/nouveau_reel.py', 'Apercu', '--date', '2026-10-12'], { cwd: dir, encoding: 'utf8' });
  const reel = path.join(dir, 'reels', fs.readdirSync(path.join(dir, 'reels'))[0]);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=1728x3072:rate=30:duration=3', '-f', 'lavfi', '-i',
    'sine=frequency=330:duration=3', '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest',
    'derush/coupe.mp4'], { cwd: reel });
  const run = (...args) => execFileSync(python, ['tools/apercu_derush.py', ...args], { cwd: reel, encoding: 'utf8', stdio: 'pipe' });
  run('derush/coupe.mp4');
  const index = read(reel, 'index.html');
  assert.match(index, /APERCU DU DERUSH/);
  assert.match(index, /<video id="derush" class="clip" src="work\/apercu-derush\.mp4"[^>]*data-duration="3(\.\d+)?"/);
  assert.match(index, /<audio id="vo" src="work\/apercu-derush\.mp4"/);
  const taille = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
    path.join(reel, 'work/apercu-derush.mp4')], { encoding: 'utf8' }).trim();
  assert.equal(taille, '1080,1920', 'copie légère pour le lecteur de l’app');
  assert.ok(fs.existsSync(path.join(reel, 'work/index-avant-apercu.html')), 'le modèle d’avant est gardé');
  run('derush/coupe.mp4');   // un aperçu remplace un aperçu
  // Un montage construit n'est pas écrasé sans --ecraser.
  execFileSync(python, ['tools/build_master.py', '--write'], { cwd: reel, encoding: 'utf8' });
  assert.throws(() => run('derush/coupe.mp4'), (e) => /déjà un montage construit|deja un montage construit/.test(e.stdout));
  assert.match(read(reel, 'index.html'), /id="bgbase"/);
});

test("les écarts du dérush signalent une coupe qui traîne (souffle isolé puis blanc), pas les autres", (t) => {
  const python = pythonOrSkip(t);
  if (!python || !ffmpegOrSkip(t)) return;
  const dir = maison(t);
  // Une vidéo livrée : coupe 1 serrée (0,08 s), coupe 2 = 0,08 s + souffle 0,15 s + blanc 0,35 s.
  execFileSync(python, ['-c', `
import math, os, struct, wave
os.makedirs('derush', exist_ok=True)
segs = [(1.0, 1), (0.08, 0), (0.96, 1), (0.08, 0), (0.15, 1), (0.35, 0), (1.06, 1)]
w = wave.open("derush/coupe.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
for duree, son in segs:
    w.writeframes(b"".join(struct.pack("<h", int(son * 12000 * math.sin(2 * math.pi * 440 * i / 48000))) for i in range(int(duree * 48000))))
w.close()`], { cwd: dir });
  write(dir, 'derush/build_derush.py', 'OUT = "derush/coupe.wav"\nPAD_START = 0.0\nPAD_END = 0.0\n'
    + 'ISLANDS = [\n    (0.0, 1.04, "un"),\n    (10.0, 11.04, "deux"),\n    (20.0, 21.6, "trois"),\n]\n');
  let sortie = '';
  try {
    execFileSync(python, ['tools/ecarts_derush.py'], { cwd: dir, encoding: 'utf8', stdio: 'pipe' });
    assert.fail('la coupe 2 traîne : code de sortie 1 attendu');
  } catch (e) {
    sortie = e.stdout;
  }
  assert.match(sortie, /coupe  1 a   1\.04 s : blanc 0\.0\d s/);
  assert.match(sortie, /coupe  2 a   2\.08 s : blanc 0\.5\d s .*<- traine/);
  assert.doesNotMatch(sortie, /coupe  1 .*traine/);
});

// Un outil n'appartient à un Reel que si son cadre d'en-tête le dit. tools/nouveau_reel.py en parlait
// dans un commentaire : la copie des Reels n'était plus jamais rafraîchie (un correctif ne les
// atteignait pas).
test("seuls les outils dont l'en-tête le dit appartiennent au Reel ; les autres suivent la maison", (t) => {
  const dir = maison(t);
  const reel = path.join(dir, 'reels', 'Essai · 2026-10-12');
  write(reel, 'meta.json', { monteurIa: { lieu: 'reel', etat: 'en-cours' } });
  write(reel, 'tools/nouveau_reel.py', '# ancienne version\n');
  write(reel, 'tools/sections.py', '# adapté à ce Reel\n');
  execFileSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  assert.equal(read(reel, 'tools/nouveau_reel.py'), read(dir, 'tools/nouveau_reel.py'), 'outil générique rafraîchi');
  assert.equal(read(reel, 'tools/sections.py'), '# adapté à ce Reel\n', 'outil du Reel jamais écrasé');
  for (const outil of ['sections.py', 'build_master.py', 'build_sfx.py', 'build_words.py', 'cut_boundaries.py', 'montage_captions.py']) {
    assert.match(read(dir, `tools/${outil}`), /^║.*A CHAQUE REEL/m, `${outil} : cadre d'en-tête attendu`);
  }
});

// npm lance les scripts avec cmd.exe sous Windows : « || true » y est une commande inconnue, et
// « python3 » ouvre souvent le Microsoft Store.
test('les scripts npm marchent aussi sous Windows', () => {
  const { scripts } = JSON.parse(read(root, 'package.json'));
  assert.doesNotMatch(scripts.postinstall, /\|\|\s*true\b/);
  assert.match(scripts.postinstall, /\|\| exit 0$/);
  for (const [nom, commande] of Object.entries(scripts)) assert.doesNotMatch(commande, /\bpython3\b/, nom);
});

// Un dossier Monteur IA suivi par git (Monteur IA 1 le créait au rangement d'un Reel) : les sons
// posés dans un Reel sont des copies, dont celles du Pack SFX, sous licence ; ni elles ni les autres
// copies régénérées ne doivent partir dans un dépôt.
test("le .gitignore garde hors de git les copies régénérées ou sous licence d'un Reel, pas son montage", (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-gitignore-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  git(dir, 'init', '-q');
  fs.copyFileSync(path.join(root, '.gitignore'), path.join(dir, '.gitignore'));
  const ignore = (rel) => {
    try {
      git(dir, 'check-ignore', '-q', '--no-index', rel);
      return true;
    } catch {
      return false;
    }
  };
  const reel = 'reels/Méliès · 2026-10-12 · Studio';
  for (const rel of ['assets/sons/pack-ui-pop.mp3', 'assets/vendor/gsap.min.js', 'brand/fonts/Inter-900.woff2', 'CLAUDE.md',
    'AGENTS.md', 'assets/video/base.mp4', 'exports/FINAL.mp4', 'work/brief.md']) {
    assert.ok(ignore(`${reel}/${rel}`), `${rel} devrait être ignoré`);
  }
  for (const rel of ['index.html', 'compositions/s1.html', 'tools/sections.py', 'derush/melies_cuts.json', 'meta.json', 'publication.md']) {
    assert.equal(ignore(`${reel}/${rel}`), false, `${rel} fait partie du montage`);
  }
});

// Règle de la marque : pas de tiret long dans ce que le client peut lire, messages des outils compris
// (l'agent les relaie). Les commentaires et les docstrings ne comptent pas.
test('les messages des outils et des scripts sont sans tiret long', () => {
  const fautifs = [];
  const fichiers = [...fs.readdirSync(path.join(root, 'tools')).filter((f) => /\.(py|sh)$/.test(f)).map((f) => `tools/${f}`),
    ...fs.readdirSync(path.join(root, 'scripts')).filter((f) => f.endsWith('.mjs') && !f.includes('.test.')).map((f) => `scripts/${f}`)];
  for (const fichier of fichiers) {
    let docstring = false;
    let bloc = false;
    read(root, fichier).split('\n').forEach((ligne, i) => {
      const t = ligne.trim();
      if (fichier.endsWith('.py')) {
        const guillemets = (ligne.match(/"""/g) ?? []).length;
        const dedans = docstring || guillemets > 0;
        if (guillemets % 2) docstring = !docstring;
        if (dedans && !/=\s*f?"""/.test(ligne)) return;   // docstring (pas une chaîne affectée)
      }
      if (fichier.endsWith('.mjs')) {
        if (bloc || t.startsWith('/*')) {
          bloc = !t.includes('*/');
          return;
        }
        if (t.startsWith('//') || t.startsWith('*')) return;
      }
      if (t.startsWith('#') || t.includes('<!--')) return;   // commentaires, gabarits HTML générés
      if (ligne.includes('—')) fautifs.push(`${fichier}:${i + 1}`);
    });
  }
  assert.deepEqual(fautifs, []);
});
