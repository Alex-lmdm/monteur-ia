import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync, spawnSync } from 'node:child_process';
import {
  VARIABLE, APP_ID, brancher, readBranchement, settingsPath, claudeHome, findApp, isProject, ouvrir,
  brancherCodex, CODEX_LIMITE, sourceWindows, installerWindows, DOSSIER_WIN,
} from './app-hyperframes.mjs';

const script = path.join(path.dirname(fileURLToPath(import.meta.url)), 'app-hyperframes.mjs');
// Chaque test a sa propre config Claude Code temporaire, supprimée à la fin du test.
function configDir(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-app-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}
// Configs de Claude Code ET de Codex dans le dossier du test : jamais celles de la machine.
const cli = (dir, ...args) => execFileSync(process.execPath, [script, ...args], { encoding: 'utf8',
  env: { ...process.env, CLAUDE_CONFIG_DIR: dir, CODEX_HOME: path.join(dir, 'codex') }, stdio: ['ignore', 'pipe', 'pipe'] });

test('la config est lue là où Claude Code et l’app la lisent', () => {
  assert.equal(claudeHome({ CLAUDE_CONFIG_DIR: '/x/claude' }, '/home/a'), '/x/claude');
  assert.equal(claudeHome({}, '/home/a'), path.join('/home/a', '.claude'));
  assert.equal(settingsPath({}, '/home/a'), path.join('/home/a', '.claude', 'settings.json'));
});

test('brancher crée la config si elle manque, sans sauvegarde inutile', (t) => {
  const file = path.join(configDir(t), 'sous-dossier', 'settings.json');
  const result = brancher(file);
  assert.equal(result.changed, true);
  assert.equal(result.backup, null);
  assert.deepEqual(JSON.parse(fs.readFileSync(file, 'utf8')), { env: { [VARIABLE]: '1' } });
});

test('brancher garde tous les réglages existants, sauvegarde, puis ne refait rien', (t) => {
  const dir = configDir(t);
  const file = path.join(dir, 'settings.json');
  const before = { model: 'opus', env: { AUTRE: 'x' }, permissions: { allow: ['Bash(ls)'] } };
  fs.writeFileSync(file, JSON.stringify(before));
  const first = brancher(file, new Date('2026-10-06T10:00:00Z'));
  assert.equal(first.changed, true);
  assert.deepEqual(JSON.parse(fs.readFileSync(first.backup, 'utf8')), before);
  assert.deepEqual(JSON.parse(fs.readFileSync(file, 'utf8')),
    { ...before, env: { AUTRE: 'x', [VARIABLE]: '1' } });
  const second = brancher(file);
  assert.equal(second.changed, false);
  assert.equal(fs.readdirSync(dir).filter((f) => f.includes('avant-monteur-ia')).length, 1);
  assert.equal(readBranchement(file).branche, true);
});

test('une config illisible n’est jamais écrasée', (t) => {
  const dir = configDir(t);
  for (const [name, content] of [['casse.json', '{ "model": '], ['env.json', '{"env": "texte"}'], ['liste.json', '[]']]) {
    const file = path.join(dir, name);
    fs.writeFileSync(file, content);
    assert.throws(() => brancher(file), /Rien n'a été modifié/);
    assert.equal(fs.readFileSync(file, 'utf8'), content);
  }
  assert.deepEqual(fs.readdirSync(dir).sort(), ['casse.json', 'env.json', 'liste.json']);
});

test('la ligne de commande dit l’état, branche, puis confirme', (t) => {
  const dir = configDir(t);
  assert.match(cli(dir, 'etat'), /à brancher/);
  assert.match(cli(dir, 'brancher'), /^Branché/);
  assert.match(cli(dir, 'brancher'), /^Déjà branché/);
  assert.match(cli(dir, 'etat'), /lit les instructions/);
  assert.equal(JSON.parse(cli(dir, 'etat', '--json')).branche, true);
});

test('seul un vrai projet HyperFrames s’ouvre dans l’app', (t) => {
  const dir = configDir(t);
  assert.equal(isProject(dir), false);
  assert.throws(() => ouvrir(dir, { platform: 'darwin', app: '/Applications/HyperFrames.app', run: () => {} }),
    /n'est pas un projet HyperFrames/);
  fs.writeFileSync(path.join(dir, 'index.html'), '<!doctype html>');
  assert.equal(isProject(dir), false);
  fs.writeFileSync(path.join(dir, 'meta.json'), '{}');
  assert.equal(isProject(dir), true);

  const calls = [];
  const opened = ouvrir(dir, { platform: 'darwin', app: '/Applications/HyperFrames.app', run: (...a) => calls.push(a) });
  assert.equal(opened.opened, true);
  assert.deepEqual(calls, [['open', ['-b', APP_ID, dir]]]);

  const noApp = ouvrir(dir, { platform: 'darwin', app: null, cli: null, run: () => assert.fail('rien à lancer') });
  assert.match(noApp.how, /Ouvrir un dossier \(Cmd \+ O\).*hyperframes\.dev\/studio/);
  // Windows : l'app reçoit le dossier sur sa ligne de commande, lancée sans être attendue.
  const exe = 'C:\\Users\\a\\AppData\\Local\\Programs\\HyperFrames\\HyperFrames.exe';
  const win = [];
  assert.equal(ouvrir(dir, { platform: 'win32', app: exe, run: () => assert.fail('pas d\'appel bloquant'),
    launch: (...a) => win.push(a) }).opened, true);
  assert.deepEqual(win, [[exe, [dir]]]);
  assert.match(ouvrir(dir, { platform: 'win32', app: null, cli: null }).how, /Ouvrir un dossier \(Ctrl \+ O\).*hyperframes\.dev\/studio/);
  // Linux : la CLI HyperFrames du dossier Monteur IA ouvre le projet dans l'app.
  const linux = [];
  assert.equal(ouvrir(dir, { platform: 'linux', app: null, cli: '/m/node_modules/.bin/hyperframes', run: (...a) => linux.push(a) }).opened, true);
  assert.deepEqual(linux, [['/m/node_modules/.bin/hyperframes', ['open', dir]]]);
  assert.match(ouvrir(dir, { platform: 'linux', app: null, cli: null }).how, /Ouvrir un dossier/);
});

test('l’app est cherchée dans les dossiers Applications du Mac et dans celui de Windows', () => {
  const seen = (paths) => (p) => paths.includes(p);
  assert.equal(findApp({ platform: 'darwin', home: '/Users/a', exists: seen(['/Users/a/Applications/HyperFrames.app']) }),
    '/Users/a/Applications/HyperFrames.app');
  assert.equal(findApp({ platform: 'darwin', home: '/Users/a', exists: seen([]) }), null);
  assert.equal(findApp({ platform: 'linux', exists: () => true }), null);
  // Windows : le dossier d'installation de l'app, dans LOCALAPPDATA.
  const local = 'C:\\Users\\a\\AppData\\Local';
  assert.equal(findApp({ platform: 'win32', env: { LOCALAPPDATA: local }, exists: seen([`${local}\\Programs\\HyperFrames\\HyperFrames.exe`]) }),
    `${local}\\Programs\\HyperFrames\\HyperFrames.exe`);
  assert.equal(findApp({ platform: 'win32', env: { LOCALAPPDATA: local }, exists: seen([]) }), null);
  assert.equal(findApp({ platform: 'win32', env: {}, exists: () => true }), null);
});

test('brancher relève la limite de lecture de Codex, sans toucher au reste de sa config', (t) => {
  const dir = configDir(t);
  assert.equal(brancherCodex(path.join(dir, 'absent')).changed, false, 'Codex absent : rien à faire');
  const codex = path.join(dir, 'codex');
  fs.mkdirSync(codex);
  const file = path.join(codex, 'config.toml');
  // Une clé de premier niveau doit précéder la première table : sinon elle tomberait dans [profiles.x].
  fs.writeFileSync(file, 'model = "gpt-5"\n\n[profiles.rapide]\nmodel = "gpt-5-mini"\n');
  const first = brancherCodex(codex, new Date('2026-10-06T10:00:00Z'));
  assert.equal(first.changed, true);
  const after = fs.readFileSync(file, 'utf8');
  assert.ok(after.indexOf(`project_doc_max_bytes = ${CODEX_LIMITE}`) < after.indexOf('[profiles.rapide]'));
  assert.match(after, /model = "gpt-5"[\s\S]*\[profiles\.rapide\]\nmodel = "gpt-5-mini"/);
  assert.equal(fs.readFileSync(first.backup, 'utf8'), 'model = "gpt-5"\n\n[profiles.rapide]\nmodel = "gpt-5-mini"\n');
  assert.equal(brancherCodex(codex).changed, false, 'idempotent');
  // Une limite plus basse déjà réglée est relevée ; une plus haute est gardée.
  fs.writeFileSync(file, 'project_doc_max_bytes = 4096\n');
  brancherCodex(codex);
  assert.equal(fs.readFileSync(file, 'utf8'), `project_doc_max_bytes = ${CODEX_LIMITE}\n`);
  fs.writeFileSync(file, 'project_doc_max_bytes = 200000\n');
  assert.equal(brancherCodex(codex).changed, false);
  // Pas encore de config.toml : il est créé.
  fs.rmSync(file);
  assert.equal(brancherCodex(codex).changed, true);
  assert.match(fs.readFileSync(file, 'utf8'), new RegExp(`^project_doc_max_bytes = ${CODEX_LIMITE}`));
});

// Les deux branchements sont indépendants : une config Claude Code illisible (laissée telle quelle)
// ne doit pas priver Codex de sa limite de lecture, et l'échec se voit dans le code de sortie.
test('une config Claude Code illisible ne bloque pas le branchement de Codex', (t) => {
  const dir = configDir(t);
  fs.writeFileSync(path.join(dir, 'settings.json'), '{ "model": ');
  fs.mkdirSync(path.join(dir, 'codex'));
  const r = spawnSync(process.execPath, [script, 'brancher'], { encoding: 'utf8',
    env: { ...process.env, CLAUDE_CONFIG_DIR: dir, CODEX_HOME: path.join(dir, 'codex') } });
  assert.equal(r.status, 1, 'échec signalé');
  assert.match(r.stderr, /Claude Code : .*JSON illisible/);
  assert.equal(fs.readFileSync(path.join(dir, 'settings.json'), 'utf8'), '{ "model": ', 'jamais écrasée');
  assert.match(fs.readFileSync(path.join(dir, 'codex', 'config.toml'), 'utf8'), new RegExp(`project_doc_max_bytes = ${CODEX_LIMITE}`));
  assert.match(r.stdout, /Codex lira les instructions de Monteur IA en entier/);
});

// Windows depuis le 02/11/2026 : l'app arrive en ZIP (HyperFrames-win-x64.zip → HyperFrames-win32-x64\HyperFrames.exe).
// Les chemins POSIX d'un dossier temporaire tiennent lieu de ceux de Windows ; `tar` décompresse le ZIP comme sous Windows.
function fauxWindows(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-win-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const env = { USERPROFILE: path.join(dir, 'user'), LOCALAPPDATA: path.join(dir, 'local'), APPDATA: path.join(dir, 'roaming') };
  fs.mkdirSync(path.join(env.USERPROFILE, 'Downloads'), { recursive: true });
  const app = path.join(dir, 'zip', DOSSIER_WIN);
  fs.mkdirSync(path.join(app, 'resources'), { recursive: true });
  fs.writeFileSync(path.join(app, 'HyperFrames.exe'), 'exe');
  fs.writeFileSync(path.join(app, 'resources', 'app.asar'), 'asar');
  return { dir, env, app, downloads: path.join(env.USERPROFILE, 'Downloads') };
}
const avecTar = (calls) => (cmd, args) => { calls.push(cmd); return cmd === 'tar' ? execFileSync(cmd, args) : ''; };

test('Windows : le ZIP téléchargé est rangé là où findApp la cherche, et mis au menu Démarrer', (t) => {
  const { env, downloads } = fauxWindows(t);
  execFileSync('tar', ['-a', '-cf', path.join(downloads, 'HyperFrames-win-x64.zip'), DOSSIER_WIN], { cwd: path.join(path.dirname(downloads), '..', 'zip') });
  assert.deepEqual(sourceWindows(downloads, { p: path }), { zip: path.join(downloads, 'HyperFrames-win-x64.zip') });
  const calls = [];
  const res = installerWindows({ env, p: path, run: avecTar(calls) });
  assert.equal(res.exe, path.join(env.LOCALAPPDATA, 'Programs', 'HyperFrames', 'HyperFrames.exe'));
  assert.ok(fs.existsSync(res.exe));
  assert.ok(fs.existsSync(path.join(env.LOCALAPPDATA, 'Programs', 'HyperFrames', 'resources', 'app.asar')));
  assert.ok(!fs.existsSync(path.join(env.LOCALAPPDATA, 'Programs', 'HyperFrames.nouvelle')), 'rien de provisoire ne reste');
  assert.deepEqual(calls, ['tar', 'powershell']);
  assert.match(res.raccourci, /Start Menu[\\/]Programs[\\/]HyperFrames\.lnk$/);
  // Refaire remplace l'app rangée, sans doublon.
  installerWindows({ env, p: path, run: avecTar([]) });
  assert.deepEqual(fs.readdirSync(path.join(env.LOCALAPPDATA, 'Programs')), ['HyperFrames']);
});

test('Windows : un dossier déjà décompressé par « Extraire tout » est pris tel quel', (t) => {
  const { env, app, downloads } = fauxWindows(t);
  fs.cpSync(app, path.join(downloads, 'HyperFrames-win-x64', DOSSIER_WIN), { recursive: true });
  assert.deepEqual(sourceWindows(downloads, { p: path }), { dossier: path.join(downloads, 'HyperFrames-win-x64', DOSSIER_WIN) });
  const calls = [];
  const res = installerWindows({ env, p: path, run: avecTar(calls) });
  assert.ok(fs.existsSync(res.exe));
  assert.deepEqual(calls, ['powershell'], 'rien à décompresser');
  assert.ok(fs.existsSync(path.join(downloads, 'HyperFrames-win-x64', DOSSIER_WIN, 'HyperFrames.exe')), 'Téléchargements reste intact');
});

test('Windows : rien de téléchargé, ou un raccourci impossible, se dit sans casser', (t) => {
  const { env } = fauxWindows(t);
  assert.throws(() => installerWindows({ env, p: path, run: () => '' }), /aucun HyperFrames-win-x64\.zip/);
  assert.throws(() => installerWindows({ env: {}, p: path }), /LOCALAPPDATA/);
  const { env: env2, app, downloads } = fauxWindows(t);
  fs.cpSync(app, path.join(downloads, DOSSIER_WIN), { recursive: true });
  const res = installerWindows({ env: env2, p: path, run: (cmd) => { if (cmd === 'powershell') throw new Error('pas de COM'); return ''; } });
  assert.ok(fs.existsSync(res.exe));
  assert.equal(res.raccourci, null);
});

test('Windows : un ZIP sans l’app est refusé, rien n’est rangé', (t) => {
  const { dir, env, downloads } = fauxWindows(t);
  fs.writeFileSync(path.join(dir, 'autre.txt'), 'x');
  execFileSync('tar', ['-a', '-cf', path.join(downloads, 'HyperFrames-win-x64.zip'), 'autre.txt'], { cwd: dir });
  assert.throws(() => installerWindows({ env, p: path, run: avecTar([]) }), /ne contient pas HyperFrames-win32-x64\\HyperFrames\.exe/);
  assert.ok(!fs.existsSync(path.join(env.LOCALAPPDATA, 'Programs', 'HyperFrames')));
  assert.ok(!fs.existsSync(path.join(env.LOCALAPPDATA, 'Programs', 'HyperFrames.nouvelle')));
});
