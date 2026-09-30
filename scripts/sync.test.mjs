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
