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
  for (const file of ['scripts/sync.mjs', 'templates', 'assets/fonts', 'brand.config.example.json',
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
  assert.match(codex, /Codex — \*\*ouvre le fichier\*\*/);
  assert.match(claude, /Claude Code — utilise l'outil/);
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
// Clôture d'un reel (tools/close_reel.py) : retour à l'état d'un ZIP neuf
// ---------------------------------------------------------------------------
const DEMO = 'templates/demo';
const git = (cwd, ...args) => execFileSync('git', args, { cwd, encoding: 'utf8' });
// Fichiers du template tels que livrés (suivis par git + nouveaux fichiers pas encore commités).
const shipped = () => git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')
  .split('\0').filter(f => f && fs.existsSync(path.join(root, f)));
const demoCopies = () => fs.readdirSync(path.join(root, DEMO), { recursive: true })
  .filter(f => f.endsWith('.demo')).map(f => f.split(path.sep).join('/').slice(0, -'.demo'.length));
function tree(dir) {
  const out = new Map();
  for (const f of fs.readdirSync(dir, { recursive: true })) {
    const rel = f.split(path.sep).join('/');
    if (rel === '.git' || rel.startsWith('.git/')) continue;
    const p = path.join(dir, f);
    if (fs.statSync(p).isFile()) out.set(rel, fs.readFileSync(p));
  }
  return out;
}

test('la copie de démo est identique aux fichiers livrés et couvre tout le plan de travail', () => {
  const copies = demoCopies();
  for (const file of copies) {
    assert.ok(fs.readFileSync(path.join(root, DEMO, `${file}.demo`)).equals(fs.readFileSync(path.join(root, file))),
      `${DEMO}/${file}.demo diffère de ${file} : recopie-le (cp ${file} ${DEMO}/${file}.demo)`);
  }
  // Tout ce que close_reel vide ou que le pipeline adapte à chaque reel doit avoir sa copie.
  const needed = shipped().filter(f => f === 'index.html'
    || /^(compositions|derush|assets\/video)\//.test(f) && !f.endsWith('.gitkeep')
    || /^tools\/[^/]+\.py$/.test(f) && /A CHAQUE REEL/.test(read(root, f)));
  for (const file of needed) {
    assert.ok(copies.includes(file), `${file} n'a pas de copie dans ${DEMO}/ (cp ${file} ${DEMO}/${file}.demo)`);
  }
});

test('close_reel remet le projet à neuf, avec ou sans git, sans toucher aux réglages du client', (t) => {
  let python;
  try {
    python = execFileSync('python3', ['-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' }).trim();
  } catch {
    return t.skip('python3 absent');
  }
  // Avec git : débrief de la première vidéo repoussé (la note reste). Sans git : débrief fait.
  for (const withGit of [true, false]) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-cloture-'));
    const home = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-home-'));
    t.after(() => [dir, home].forEach(d => fs.rmSync(d, { recursive: true, force: true })));
    for (const file of shipped().filter(f => !/^\.(agents|claude)\//.test(f))) {
      fs.mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
      fs.copyFileSync(path.join(root, file), path.join(dir, file));
    }
    const neuf = tree(dir);

    // Un reel monté de bout en bout : outils adaptés, médias du client, restes des outils.
    const edit = (file, from, to) => write(dir, file, read(dir, file).replace(from, to));
    edit('tools/sections.py', 'derush/exemple_cuts.json', 'derush/mon-reel_cuts.json');
    for (const file of ['tools/build_words.py', 'tools/cut_boundaries.py', 'tools/montage_captions.py',
      'tools/build_sfx.py', 'tools/build_master.py', 'index.html', 'compositions/captions.html',
      'compositions/exemple-section.html', 'derush/exemple_cuts.json']) {
      write(dir, file, `${read(dir, file)}\n<!-- réglage du reel précédent -->\n`);
    }
    write(dir, 'assets/video/base.mp4', 'vidéo du client');
    write(dir, 'assets/video/hook-broll-v2.mp4', 'b-roll');
    write(dir, 'derush/build_derush.py', 'ISLANDS = [(1.0, 2.0, "ancienne prise")]\n');
    write(dir, 'derush/mon-reel_cuts.json', '{}');
    write(dir, 'derush/mon-reel_enhanced.mp4', 'cut');
    write(dir, 'compositions/s0-hook.html', '<div data-composition-id="s0-hook"></div>');
    write(dir, 'compositions/components/grain.html', '<div></div>');
    write(dir, 'renders/FINAL_SFX_MUSIC.mp4', 'master');
    write(dir, 'renders/overlay.mov', 'calque');
    write(dir, 'work/premiere-video.md', 'étape : dérush fait, débrief à faire');
    write(dir, 'snapshots/frame-01.png', 'png');
    write(dir, 'probe/index.html', '<div data-composition-id="probe"></div>');
    write(dir, 'overlay.html', '<div data-composition-id="overlay"></div>');
    write(dir, 'transcript.json', '[]');
    write(dir, '.thumbnails/index.jpg', 'jpg');
    // Réglages et fichiers personnels : doivent survivre à la clôture.
    const personal = { 'brand.config.json': JSON.stringify({ brand: { name: 'CLIENT' }, setup: { firstVideoDone: !withGit } }),
      'assets/images/logo.png': 'logo', 'assets/music/theme.mp3': 'musique', 'assets/sfx/perso.mp3': 'sfx' };
    for (const [file, content] of Object.entries(personal)) write(dir, file, content);

    const env = { ...process.env, HOME: home, USERPROFILE: home, GIT_CONFIG_GLOBAL: os.devNull,
      GIT_CONFIG_NOSYSTEM: '1', PATH: withGit ? process.env.PATH : home };
    const out = execFileSync(python, ['tools/close_reel.py', 'mon-reel'], { cwd: dir, env, encoding: 'utf8' });
    const mode = withGit ? 'avec git' : 'sans git';

    const after = tree(dir);
    const note = after.get('work/premiere-video.md')?.toString();
    after.delete('work/premiere-video.md');
    if (withGit) {
      assert.match(note ?? '', /débrief à faire[\s\S]*reel mon-reel/, `${mode} : note de débrief perdue`);
      assert.doesNotMatch(note, /étape/);
    } else {
      assert.equal(note, undefined, `${mode} : suivi de première vidéo laissé alors que le débrief est fait`);
    }
    for (const [file, content] of Object.entries(personal)) {
      assert.equal(after.get(file)?.toString(), content, `${mode} : ${file} perdu`);
      after.delete(file);
    }
    assert.deepEqual([...after.keys()].sort(), [...neuf.keys()].sort(), `${mode} : fichiers en trop ou manquants`);
    for (const [file, content] of neuf) {
      assert.ok(after.get(file).equals(content), `${mode} : ${file} n'est pas revenu à l'état livré`);
    }
    const archive = path.join(home, process.platform === 'win32' ? 'Videos' : 'Movies', 'reels-publies', 'mon-reel');
    assert.equal(fs.readFileSync(path.join(archive, 'FINAL_SFX_MUSIC.mp4'), 'utf8'), 'master');
    if (withGit) {
      assert.match(out, /tag reel\/mon-reel posé/);
      assert.equal(git(dir, 'status', '--porcelain'), '');
      assert.match(git(dir, 'show', 'reel/mon-reel:tools/sections.py'), /mon-reel_cuts\.json/);
    } else {
      assert.match(fs.readFileSync(path.join(archive, 'projet/tools/sections.py'), 'utf8'), /mon-reel_cuts\.json/);
      assert.ok(fs.existsSync(path.join(archive, 'projet/build_derush.py')));
    }
    // Les outils repartent sur la démo livrée.
    const sections = execFileSync(python, ['tools/sections.py'], { cwd: dir, encoding: 'utf8' });
    assert.match(sections, /^exemple-section\s+split\s+0\.000 ->\s+8\.000/m);
  }
});
