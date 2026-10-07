import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync, spawnSync } from 'node:child_process';
import {
  assetsReferences, aucunChangement, appliquer, calculerManifeste, cheminsDepuisLaRacine, decrire, fusionnerJson,
  modeleAvecExtensions, neutre, planifier, reporterSons, reporterZones,
} from './mettre-a-jour.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Dernière version publiée de Monteur IA 1 (un seul plan de travail à la racine).
const V1 = '14b03af';

const read = (dir, name) => fs.readFileSync(path.join(dir, name), 'utf8');
function write(dir, name, value) {
  fs.mkdirSync(path.dirname(path.join(dir, name)), { recursive: true });
  fs.writeFileSync(path.join(dir, name), value);
}
const edit = (dir, name, from, to) => {
  const before = read(dir, name);
  const after = before.replace(from, to);
  assert.notEqual(after, before, `${name} : motif introuvable`);
  write(dir, name, after);
};
const hash = (file) => crypto.createHash('sha1').update(fs.readFileSync(file)).digest('hex');
function arbre(dir, sous = '') {
  return fs.readdirSync(path.join(dir, sous), { withFileTypes: true }).flatMap((e) => {
    const rel = sous ? `${sous}/${e.name}` : e.name;
    if (e.isDirectory()) return e.name === '.git' ? [] : arbre(dir, rel);
    return [`${rel} ${hash(path.join(dir, rel))}`];
  }).sort();
}

test('les zones personnalisées, les polices et les consignes des extensions passent dans la nouvelle version', () => {
  const neuf = 'A\n<!-- BEGIN GENERATED: cta -->\nneuf\n<!-- END GENERATED: cta -->\nB nouvelle ligne\n/* BEGIN GENERATED: x */ 1 /* END GENERATED: x */\n';
  const client = 'A\n<!-- BEGIN GENERATED: cta -->\nCTA DU CLIENT\n<!-- END GENERATED: cta -->\nB\n/* BEGIN GENERATED: x */ 2 /* END GENERATED: x */\n';
  const { texte, reportees } = reporterZones(neuf, client);
  assert.equal(reportees, 2);
  assert.match(texte, /CTA DU CLIENT/);
  assert.match(texte, /B nouvelle ligne/);
  assert.match(texte, /\/\* BEGIN GENERATED: x \*\/ 2 \/\* END GENERATED: x \*\//);

  const presets = fusionnerJson({ fonts: { Inter: { v: 2 } }, presets: { a: 1 } },
    { fonts: { Inter: { v: 1 }, MaPolice: { v: 1 } }, presets: { a: 0 } });
  assert.deepEqual(presets, { fonts: { Inter: { v: 2 }, MaPolice: { v: 1 } }, presets: { a: 1 } });

  const bloc = (nom, v) => `<!-- BEGIN EXTENSION: ${nom} (installé) -->\n${v}\n<!-- END EXTENSION: ${nom} -->`;
  const modele = modeleAvecExtensions(`# Neuf\n\n${bloc('egaree', 'x')}\n`,
    `# Ancien\n\n${bloc('double-ia', 'v1')}\n\n${bloc('pack-sfx', 'v1')}\n`);
  assert.match(modele, /^# Neuf/);
  assert.doesNotMatch(modele, /egaree|# Ancien/);
  assert.equal(modele.match(/BEGIN EXTENSION: double-ia/g).length, 1);
  assert.equal(modele.match(/BEGIN EXTENSION: pack-sfx/g).length, 1);
  assert.equal(modeleAvecExtensions(modele, modele), modele, 'une seconde mise à jour ne duplique rien');

  assert.equal(cheminsDepuisLaRacine('<script src="../assets/vendor/gsap.min.js"></script><link href="../brand/tokens.css">'
    + '<div style="background:url(\'../assets/images/a.png\')"></div><a href="../autre.html">'),
  '<script src="assets/vendor/gsap.min.js"></script><link href="brand/tokens.css">'
    + '<div style="background:url(\'assets/images/a.png\')"></div><a href="../autre.html">');

  assert.deepEqual(assetsReferences('<img src="assets/logos/a.svg"><div style="background:url(assets/images/b%20c.png)">'
    + '<script>const x = \'assets/images/d.png?v=2\'; const y = "assets/../secret";</script><a href="brand/x.css">'),
  ['assets/images/b c.png', 'assets/images/d.png', 'assets/logos/a.svg']);
  const sons = reporterSons('x\nevents = [\n    ("a.mp3", 1.0, -18, None),\n]\n\nevents.sort(key=f)\n',
    'y\nevents = []\nfor t in T:\n    events.append(t)\n\nevents.sort(key=f)\nfin\n');
  assert.equal(sons, 'y\nevents = [\n    ("a.mp3", 1.0, -18, None),\n]\n\nevents.sort(key=f)\nfin\n');
  assert.equal(reporterSons('pas de liste', 'events = []\nevents.sort()'), null);
});

// ---------------------------------------------------------------------------
// Un vrai dossier client de Monteur IA 1 (git archive de la version publiée)
// ---------------------------------------------------------------------------
function outilsOuSkip(t) {
  try {
    execFileSync('git', ['cat-file', '-e', `${V1}^{commit}`], { cwd: root, stdio: 'ignore' });
    for (const [cmd, arg] of [['python3', '--version'], ['ffmpeg', '-version'], ['ffprobe', '-version']]) {
      execFileSync(cmd, [arg], { stdio: 'ignore' });
    }
    return true;
  } catch {
    t.skip('historique git de Monteur IA 1, python3 ou ffmpeg absent');
    return false;
  }
}

function clientV1(t, nom = 'Monteur IA - Studio Lumiere') {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-maj-'));
  t.after(() => fs.rmSync(base, { recursive: true, force: true }));
  const dir = path.join(base, nom);
  fs.mkdirSync(dir);
  const archive = execFileSync('git', ['archive', '--format=tar', V1], { cwd: root, maxBuffer: 1 << 28 });
  execFileSync('tar', ['-x', '-C', dir], { input: archive });
  return dir;
}

const python = (dir, ...args) => execFileSync('python3', args, { cwd: dir, encoding: 'utf8' });

/** Le client a fait son setup, installé des extensions et monte un Reel (Méliès). */
function personnaliser(dir) {
  const config = JSON.parse(read(dir, 'brand.config.example.json'));
  config.brand.name = 'Studio Lumière';
  config.audio = { ...config.audio, musicFile: 'fond.mp3', musicDb: -26.5 };
  write(dir, 'brand.config.json', `${JSON.stringify(config, null, 2)}\n`);
  edit(dir, '.claude/skills/reel-script/SKILL.md', /(<!-- BEGIN GENERATED: voice-profile -->)[\s\S]*?(<!-- END GENERATED: voice-profile -->)/,
    '$1\nVOIX DU CLIENT\n$2');
  edit(dir, 'design-system/manychat-dm.md', /(<!-- BEGIN GENERATED: cta -->)[\s\S]*?(<!-- END GENERATED: cta -->)/, '$1\nCTA LUMIERE\n$2');
  write(dir, '.claude/skills/reel-script/references/scripts-exemples.md',
    `${read(dir, '.claude/skills/reel-script/references/scripts-exemples.md')}\n## Script du client\n`);
  const presets = JSON.parse(read(dir, 'templates/style-presets.json'));
  presets.fonts.MaPolice = { ...presets.fonts.Anton };
  write(dir, 'templates/style-presets.json', `${JSON.stringify(presets, null, 1)}\n`);
  write(dir, 'tools/build_overlay.py', `${read(dir, 'tools/build_overlay.py')}\n# retouche du client\n`);
  write(dir, 'assets/logos/logo.png', 'LOGO');
  // Police déposée à la main dans brand/fonts/ (l'ancienne consigne des formats statiques).
  write(dir, 'brand/fonts/Coluna.otf', 'POLICE DU CLIENT');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=220:duration=12', 'assets/music/fond.mp3'], { cwd: dir });
  // Une extension de Monteur IA 1 : outil, skill, consignes, réglages et données.
  write(dir, 'tools/double_ia.py', 'ROOT = None  # Monteur IA 1\n');
  write(dir, '.claude/skills/double-ia/SKILL.md', '# Ton Double IA\n');
  write(dir, 'templates/AGENT.md.tpl', `${read(dir, 'templates/AGENT.md.tpl')}\n<!-- BEGIN EXTENSION: double-ia (ajouté) -->\n`
    + 'Consignes Double IA\n<!-- END EXTENSION: double-ia -->\n');
  write(dir, 'double-ia.config.json', '{"avatar": "moi"}\n');
  write(dir, 'stories/promo/story.json', '{}\n');
  write(dir, 'assets/sfx/pack/catalog.json', '{}\n');
}

/** packSfx : un client du Pack SFX 1.0, dont la liste de sons remplace build_sfx.py. */
function reelEnCours(dir, { packSfx = false } = {}) {
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=1080x1920:rate=30:duration=8',
    '-f', 'lavfi', '-i', 'sine=frequency=330:duration=8', '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-shortest', 'assets/video/base.mp4'], { cwd: dir });
  const cuts = JSON.parse(read(dir, 'derush/exemple_cuts.json'));
  write(dir, 'derush/melies_cuts.json', JSON.stringify({ ...cuts, source: 'assets/video/base.mp4' }));
  edit(dir, 'tools/sections.py', 'derush/exemple_cuts.json', 'derush/melies_cuts.json');
  edit(dir, 'tools/sections.py', '    ("exemple-section", "split", [0, 1, 2]),',
    '    ("s0-hook", "split", [0]),\n    ("s1-corps", "full", [1]),\n    ("s2-face", "face", [2]),');
  const section = read(dir, 'compositions/exemple-section.html');
  for (const id of ['s0-hook', 's1-corps']) write(dir, `compositions/${id}.html`, section.replaceAll('exemple-section', id));
  // Logo, image et police partagés, rangés à la racine comme en Monteur IA 1, utilisés par le montage
  // (attribut, url() du CSS, chaîne du JavaScript, nom avec espace).
  write(dir, 'assets/logos/claude.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>');
  write(dir, 'assets/images/fond carte.png', 'PNG');
  edit(dir, 'compositions/s0-hook.html', '</body>', '<img id="logo-claude" src="../assets/logos/claude.svg">\n'
    + '<div id="carte" style="background: url(\'../assets/images/fond%20carte.png\')"></div>\n'
    + '<script>window.fondCarte = "../assets/images/fond carte.png";</script>\n</body>');
  edit(dir, 'compositions/captions.html', '</body>', '<!-- sous-titres du Reel -->\n</body>');
  edit(dir, 'tools/montage_captions.py', '["on garde", "tes mots"],', '["méliès", "le magicien"],');
  if (!packSfx) {
    edit(dir, 'tools/build_sfx.py', /^events = \[\][\s\S]*?(?=^events\.sort)/m,
      'events = [\n    ("starter/whoosh.mp3", 2.667, -18, 0.45),\n    ("starter/pop.mp3", 5.333, -22, None),\n]\n\n');
  }
  python(dir, 'tools/build_master.py', '--write');
  fs.copyFileSync(path.join(dir, 'assets/video/base.mp4'), path.join(dir, 'renders/FINAL_SFX_MUSIC.mp4'));
  write(dir, 'renders/sfx_events.json', packSfx ? '[{"sfx": "whoosh-swoosh", "t": 2.667}]\n' : '[]\n');
  write(dir, 'work/premiere-video.md', '# Première vidéo : débrief à faire\n');
  write(dir, 'work/index.generated.html', '<html></html>\n');
  write(dir, 'derush/build_derush.py', 'ISLANDS = [(1.0, 3.6, "Méliès")]\n');
}

test('un client de Monteur IA 1 passe à « un Reel = un projet » sans rien perdre', (t) => {
  if (!outilsOuSkip(t)) return;
  const dir = clientV1(t);
  personnaliser(dir);
  reelEnCours(dir);
  const avant = arbre(dir);
  const intouchables = ['brand.config.json', 'assets/logos/logo.png', 'assets/music/fond.mp3', 'tools/double_ia.py',
    '.claude/skills/double-ia/SKILL.md', 'double-ia.config.json', 'stories/promo/story.json', 'assets/sfx/pack/catalog.json',
    '.claude/skills/reel-script/references/scripts-exemples.md', 'brand/fonts/Coluna.otf', 'assets/logos/claude.svg',
    'assets/images/fond carte.png'].map((f) => [f, hash(path.join(dir, f))]);

  const plan = planifier(dir, { sujet: 'Méliès', date: '2026-10-02' });
  assert.deepEqual(plan.moteur.filter((m) => m.retouche), [], 'zones et consignes d’extensions seules : rien de retouché');
  assert.deepEqual(arbre(dir), avant, 'le plan à blanc ne touche à rien');
  assert.ok(plan.plan.reel, 'le Reel en cours est reconnu');
  assert.deepEqual(plan.plan.adaptes.sort(), ['build_sfx.py', 'montage_captions.py', 'sections.py']);
  assert.ok(plan.obsoletes.includes('tools/close_reel.py'));
  assert.deepEqual(plan.outilsExtensions, ['tools/double_ia.py']);
  assert.deepEqual(plan.moteur.filter((m) => m.action === 'remplace-modifie').map((m) => m.rel), ['tools/build_overlay.py']);

  const resultat = appliquer(plan, { npm: false, now: new Date(2026, 9, 6, 14, 30, 0) });
  assert.deepEqual(resultat.avertissements, []);
  for (const [f, h] of intouchables) assert.equal(hash(path.join(dir, f)), h, `${f} ne doit pas bouger`);
  assert.match(read(dir, '.claude/skills/reel-script/SKILL.md'), /VOIX DU CLIENT/);
  assert.match(read(dir, '.agents/skills/reel-script/SKILL.md'), /VOIX DU CLIENT/, 'copie Codex refaite avec le profil');
  assert.match(read(dir, 'design-system/manychat-dm.md'), /CTA LUMIERE/);
  assert.ok(JSON.parse(read(dir, 'templates/style-presets.json')).fonts.MaPolice, 'sa police reste déclarée');
  for (const f of ['CLAUDE.md', 'AGENTS.md', 'templates/AGENT.md.tpl']) {
    assert.equal(read(dir, f).match(/BEGIN EXTENSION: double-ia/g)?.length, 1, `${f} : consignes de l'extension une fois`);
  }

  // Le moteur est neuf, l'ancien est sauvegardé.
  const sauvegarde = path.join(dir, '.sauvegarde-mise-a-jour-2026-10-06-14h30-00');
  assert.equal(read(dir, 'tools/build_overlay.py'), read(root, 'tools/build_overlay.py'));
  assert.match(read(sauvegarde, 'moteur/tools/build_overlay.py'), /retouche du client/);
  assert.equal(fs.existsSync(path.join(dir, 'tools/close_reel.py')), false);
  assert.ok(fs.existsSync(path.join(sauvegarde, 'moteur/tools/close_reel.py')));
  assert.equal(fs.existsSync(path.join(dir, 'templates/demo/tools')), false);
  assert.equal(read(dir, 'tools/sections.py'), read(root, 'tools/sections.py'), 'les outils de la maison redeviennent neufs');

  // La racine n'est plus un plan de travail ; l'accueil est créé.
  for (const f of ['index.html', 'compositions', 'derush', 'renders', 'assets/video']) {
    assert.equal(fs.existsSync(path.join(dir, f)), false, `${f} ne doit plus être à la racine`);
  }
  assert.match(read(dir, 'work/premiere-video.md'), /débrief à faire/, 'la note de débrief reste dans le dossier');
  assert.ok(fs.existsSync(path.join(dir, 'Accueil · Studio Lumière', 'index.html')));

  // Le Reel en cours est un projet complet, prêt pour l'export natif.
  const reel = path.join(dir, 'reels', 'Méliès · 2026-10-02 · Studio Lumière');
  assert.equal(resultat.reel.reel, reel);
  assert.deepEqual(resultat.reel.reste, []);
  assert.equal(JSON.parse(read(reel, 'meta.json')).monteurIa.lieu, 'reel');
  assert.match(read(reel, 'tools/sections.py'), /derush\/melies_cuts\.json/);
  assert.match(read(reel, 'tools/montage_captions.py'), /le magicien/);
  assert.doesNotMatch(read(reel, 'tools/montage_captions.py'), /"\.\.\//);
  assert.match(read(reel, 'tools/build_sfx.py'), /starter\/pop\.mp3", 5\.333/);
  assert.match(read(reel, 'tools/build_sfx.py'), /from lieux import MAISON/, 'build_sfx neuf, liste de sons reportée');
  for (const f of ['s0-hook.html', 's1-corps.html', 'captions.html']) {
    assert.doesNotMatch(read(reel, `compositions/${f}`), /(src|href)="\.\.\//, `${f} : chemins depuis la racine`);
  }
  assert.match(read(reel, 'compositions/captions.html'), /sous-titres du Reel/);
  const master = read(reel, 'index.html');
  assert.match(master, /id="section-s0-hook"/);
  assert.match(master, /data-track-kind="captions"/);
  assert.match(master, /visage-split\.mp4/);
  assert.match(master, /<!-- SONS:DEBUT[\s\S]*id="sfx-02"[\s\S]*<!-- SONS:FIN -->/);
  assert.ok(fs.existsSync(path.join(reel, 'work/migration-v1/index.html')), 'ancien master gardé');
  assert.ok(fs.existsSync(path.join(reel, 'exports/FINAL_SFX_MUSIC-avant-mise-a-jour.mp4')),
    'la vidéo publiée garde son nom : un nouvel export ne l’écrase pas');
  assert.ok(fs.existsSync(path.join(reel, 'work/sfx_events.json')));
  assert.ok(fs.existsSync(path.join(reel, 'work/index.generated.html')));
  assert.ok(fs.existsSync(path.join(reel, 'CLAUDE.md')));
  // Logo, image et police partagés : le Reel a sa copie, au chemin que son montage utilise.
  for (const f of ['assets/logos/claude.svg', 'assets/images/fond carte.png']) {
    assert.equal(hash(path.join(reel, f)), hash(path.join(dir, f)), `${f} : copié dans le Reel`);
  }
  assert.match(read(reel, 'compositions/s0-hook.html'), /src="assets\/logos\/claude\.svg"/);
  assert.match(read(reel, 'compositions/s0-hook.html'), /window\.fondCarte = "assets\/images\/fond carte\.png"/);
  assert.match(read(reel, 'work/MIGRATION.md'), /copiés dans le Reel[^\n]*assets\/images\/fond carte\.png, assets\/logos\/claude\.svg/);
  const cli = path.join(root, 'node_modules', '.bin', process.platform === 'win32' ? 'hyperframes.cmd' : 'hyperframes');
  if (fs.existsSync(cli)) {
    const controle = spawnSync(cli, ['lint', reel], { cwd: dir, encoding: 'utf8', shell: process.platform === 'win32' });
    assert.doesNotMatch(`${controle.stdout}${controle.stderr}`, /missing_local_asset/, 'aucun fichier manquant pour HyperFrames');
  }

  const encore = planifier(dir);
  assert.ok(aucunChangement(encore), `seconde mise à jour : rien à faire (${JSON.stringify(encore.moteur)})`);
  // Une extension réinstallée à la main espace ses consignes autrement : ce n'est pas un changement.
  write(dir, 'templates/AGENT.md.tpl', read(dir, 'templates/AGENT.md.tpl').replace('<!-- BEGIN EXTENSION', '\n\n<!-- BEGIN EXTENSION'));
  assert.ok(aucunChangement(planifier(dir)), 'des lignes vides en plus ne relancent pas une mise à jour');
});

// Une retouche faite hors des zones personnalisées, ou hors des consignes d'extensions du modèle
// d'instructions, ne se perd pas en silence : le plan la signale, la sauvegarde la garde, l'étape 4 de
// MISE-A-JOUR.md la reprend. Le manifeste garde pour cela la forme neutralisée des fichiers livrés.
test('une retouche hors zones ou hors consignes des extensions est signalée, jamais écartée en silence', (t) => {
  if (!outilsOuSkip(t)) return;
  const manifeste = calculerManifeste(V1, root).fichiers;
  assert.ok(manifeste['design-system/manychat-dm.md'].some((h) => h.startsWith('z:')), 'forme neutralisée des fichiers à zones');
  const vide = path.join(os.tmpdir(), 'monteur-archive-vide');
  const dir = clientV1(t);
  personnaliser(dir);   // zones et consignes d'extension seulement : rien à signaler
  assert.deepEqual(planifier(dir, { manifeste, archive: vide }).moteur.filter((m) => m.retouche), []);

  write(dir, 'templates/AGENT.md.tpl', read(dir, 'templates/AGENT.md.tpl').replace('<!-- BEGIN EXTENSION: double-ia',
    '## Règle maison\nToujours finir par le slogan SLOGAN-PERSO.\n\n<!-- BEGIN EXTENSION: double-ia'));
  edit(dir, 'design-system/manychat-dm.md', '<!-- END GENERATED: cta -->', '<!-- END GENERATED: cta -->\n\nJamais de majuscules : RETOUCHE-DM.');
  const plan = planifier(dir, { manifeste, archive: vide });
  assert.deepEqual(plan.moteur.filter((m) => m.retouche).map((m) => m.rel).sort(),
    ['design-system/manychat-dm.md', 'templates/AGENT.md.tpl']);
  const texte = decrire(plan);
  assert.match(texte, /retouchés \(ta version reste dans la sauvegarde\) : [^\n]*templates\/AGENT\.md\.tpl \(hors consignes des extensions\)/);
  assert.match(texte, /design-system\/manychat-dm\.md \(hors zones personnalisées\)/);
  // Le manifeste publié sans formes neutralisées signale déjà le modèle (il n'a pas de zones).
  assert.ok(planifier(dir, { archive: vide }).moteur.some((m) => m.rel === 'templates/AGENT.md.tpl' && m.retouche));

  const r = appliquer(plan, { npm: false, now: new Date(2026, 9, 6, 15, 0, 0) });
  assert.match(read(r.sauvegarde, 'moteur/templates/AGENT.md.tpl'), /SLOGAN-PERSO/);
  assert.match(read(r.sauvegarde, 'moteur/design-system/manychat-dm.md'), /RETOUCHE-DM/);
  assert.match(read(dir, 'design-system/manychat-dm.md'), /CTA LUMIERE/, 'ses zones restent');

  // Étape 4 : la consigne repart dans un bloc « consignes-perso », gardé par chaque mise à jour.
  write(dir, 'templates/AGENT.md.tpl', `${read(dir, 'templates/AGENT.md.tpl')}\n<!-- BEGIN EXTENSION: consignes-perso -->\n`
    + 'Toujours finir par le slogan SLOGAN-PERSO.\n<!-- END EXTENSION: consignes-perso -->\n');
  execFileSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  assert.match(read(dir, 'CLAUDE.md'), /SLOGAN-PERSO/);
  const encore = planifier(dir, { manifeste, archive: vide });
  assert.ok(aucunChangement(encore), JSON.stringify(encore.moteur));
  assert.deepEqual(encore.extensions, ['double-ia'], 'les consignes perso ne sont pas une extension');
  assert.equal(encore.consignesPerso, true);
  assert.equal(neutre(read(dir, 'templates/AGENT.md.tpl')), neutre(read(root, 'templates/AGENT.md.tpl')));
});

test('une mise à jour interrompue se reprend en relançant la même commande, sans doublon ni perte', (t) => {
  if (!outilsOuSkip(t)) return;
  if (process.platform === 'win32') return t.skip('panne simulée par les droits POSIX');
  const dir = clientV1(t);
  personnaliser(dir);
  reelEnCours(dir);
  // Panne au milieu du déplacement : le dossier derush/ refuse qu'on en retire un fichier.
  const derush = path.join(dir, 'derush');
  fs.chmodSync(derush, 0o555);
  t.after(() => fs.existsSync(derush) && fs.chmodSync(derush, 0o755));
  assert.throws(() => appliquer(planifier(dir, { sujet: 'Méliès', date: '2026-10-02' }), { npm: false }), /EACCES|EPERM/);
  fs.chmodSync(derush, 0o755);

  const reprise = planifier(dir);
  assert.ok(reprise.plan.inacheve, 'le Reel commencé est repris');
  assert.deepEqual(reprise.plan.adaptes, ['build_sfx.py', 'montage_captions.py', 'sections.py'], 'outils adaptés retrouvés');
  const r = appliquer(reprise, { npm: false });
  assert.deepEqual(fs.readdirSync(path.join(dir, 'reels')), ['Méliès · 2026-10-02 · Studio Lumière'], 'un seul Reel');
  assert.deepEqual(r.reel.reste, []);
  const reel = r.reel.reel;
  assert.match(read(reel, 'tools/sections.py'), /melies_cuts/);
  assert.match(read(reel, 'derush/build_derush.py'), /ISLANDS|.+/);
  assert.deepEqual(fs.readdirSync(path.join(reel, 'derush')).filter((f) => / \(\d+\)/.test(f)), [], 'aucun doublon');
  assert.equal(fs.existsSync(derush), false);
  assert.equal(JSON.parse(read(reel, 'meta.json')).monteurIa.migration, 'faite');
  assert.match(read(reel, 'index.html'), /<!-- SONS:DEBUT/);
  assert.ok(aucunChangement(planifier(dir)));
});

test('un plan de travail sans Reel en cours est retiré, un essai de cadrage rangé dans la sauvegarde', (t) => {
  if (!outilsOuSkip(t)) return;
  const dir = clientV1(t, 'monteur-ia');
  const plan = planifier(dir);
  assert.equal(plan.plan.reel, false);
  assert.deepEqual(plan.plan.perso, [], 'tel que livré');

  // Calage du cadrage au setup : master régénéré sur une vidéo d'essai, sans Reel.
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=1080x1920:rate=30:duration=8',
    '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', 'assets/video/base.mp4'], { cwd: dir });
  python(dir, 'tools/build_master.py', '--write');
  const essai = planifier(dir);
  assert.equal(essai.plan.reel, false, 'un essai de cadrage ne fait pas un Reel');
  assert.deepEqual(essai.plan.perso.sort(), ['assets/video/base.mp4', 'index.html']);
  const r = appliquer(essai, { npm: false, now: new Date(2026, 9, 6, 9, 0, 0) });
  assert.equal(r.reel, null);
  assert.equal(fs.existsSync(path.join(dir, 'reels')), false);
  assert.equal(fs.existsSync(path.join(dir, 'index.html')), false);
  assert.ok(fs.existsSync(path.join(r.sauvegarde, 'plan-de-travail/assets/video/base.mp4')), 'la vidéo d’essai est rangée, pas supprimée');
  assert.ok(fs.existsSync(path.join(dir, 'Accueil Monteur IA', 'index.html')), 'dossier au nom par défaut : accueil générique');
  assert.ok(aucunChangement(planifier(dir)));
});

// La première vidéo se décide par dossier (setup.firstVideoDone), plus par l'archive des Reels publiés,
// commune à tous les dossiers d'un client : elle sautait le débrief d'un 2e dossier. Un client de
// Monteur IA 1 qui a déjà livré des Reels le reçoit donc noté par la mise à jour, une fois.
test('Monteur IA 1 qui a déjà publié des Reels : la mise à jour note sa première vidéo faite, rien d’autre', (t) => {
  if (!outilsOuSkip(t)) return;
  const dir = clientV1(t);
  personnaliser(dir);
  const archive = path.join(path.dirname(dir), 'Movies', 'reels-publies');
  write(archive, 'LISEZ-MOI.txt', 'archive\n');
  assert.equal(planifier(dir, { archive }).premiereVideoFaite, false, 'une archive sans Reel ne compte pas');
  fs.mkdirSync(path.join(archive, 'melies'));
  const plan = planifier(dir, { archive });
  assert.equal(plan.premiereVideoFaite, true);
  assert.match(decrire(plan), /Première vidéo : tu as déjà monté des Reels/);
  const avant = JSON.parse(read(dir, 'brand.config.json'));
  const r = appliquer(plan, { npm: false, now: new Date(2026, 9, 7, 9, 0, 0) });
  const apres = JSON.parse(read(dir, 'brand.config.json'));
  assert.equal(apres.setup.firstVideoDone, true);
  assert.deepEqual({ ...apres, setup: { ...apres.setup, firstVideoDone: false } }, avant, 'rien d’autre ne change dans ses réglages');
  assert.deepEqual(JSON.parse(read(r.sauvegarde, 'moteur/brand.config.json')), avant, 'ses réglages d’avant sont sauvegardés');
  assert.match(read(dir, 'CLAUDE.md'), /État : première vidéo faite\./);
  assert.doesNotMatch(read(dir, 'CLAUDE.md'), /reels-publies\/` non vide/, 'plus de règle sur l’archive commune');
  assert.ok(aucunChangement(planifier(dir, { archive })), 'une seconde mise à jour ne refait rien');

  // Sans Reel ni archive : sa première vidéo reste à faire, ses réglages ne bougent pas.
  const neuf = clientV1(t, 'Monteur IA - Client B');
  write(neuf, 'brand.config.json', read(neuf, 'brand.config.example.json'));
  const vide = path.join(path.dirname(neuf), 'Movies', 'reels-publies');
  const planNeuf = planifier(neuf, { archive: vide });
  assert.equal(planNeuf.premiereVideoFaite, false);
  const reglages = read(neuf, 'brand.config.json');
  appliquer(planNeuf, { npm: false });
  assert.equal(read(neuf, 'brand.config.json'), reglages);
  assert.match(read(neuf, 'CLAUDE.md'), /État : première vidéo pas encore faite\./);
});

test('Pack SFX de Monteur IA 1 : sa liste de sons passe avant la liste de départ, et la pose attend le pack à jour', (t) => {
  if (!outilsOuSkip(t)) return;
  const dir = clientV1(t);
  personnaliser(dir);
  reelEnCours(dir);   // build_sfx.py adapté (whoosh et pop de départ)
  write(dir, 'work/premiere-video.md', '# Première vidéo : débrief à faire\n');
  write(dir, 'renders/sfx_events.json', '[{"sfx": "whoosh-swoosh", "t": 2.667}, {"file": "pack/ui/pop.mp3", "t": 5.3}]\n');
  const vide = path.join(path.dirname(dir), 'vide');
  const r = appliquer(planifier(dir, { sujet: 'Méliès', date: '2026-10-02', archive: vide }), { npm: false });
  assert.equal(r.reel.reste.length, 1);
  assert.match(r.reel.reste[0], /^sons : la liste du Pack SFX a suivi le Reel/);
  assert.doesNotMatch(read(r.reel.reel, 'index.html'), /starter/, 'les sons de départ ne passent pas devant ceux du pack');
  assert.match(read(r.reel.reel, 'work/MIGRATION.md'), /## Reste à faire\n- sons : /);

  // Une liste illisible pour le pack ne passe pas devant : build_sfx.py pose ses sons.
  const autre = clientV1(t, 'Monteur IA - Client C');
  personnaliser(autre);
  reelEnCours(autre);
  write(autre, 'renders/sfx_events.json', '[{"t": 2.667, "son": "whoosh"}]\n');
  const r2 = appliquer(planifier(autre, { sujet: 'Méliès', date: '2026-10-02', archive: vide }), { npm: false });
  assert.deepEqual(r2.reel.reste, []);
  assert.match(read(r2.reel.reel, 'index.html'), /<!-- SONS:DEBUT[\s\S]*starter[\s\S]*<!-- SONS:FIN -->/);
});

test('coupée juste après la création du Reel, la mise à jour reprend ce Reel au lieu d’en créer un second', (t) => {
  if (!outilsOuSkip(t)) return;
  const vide = path.join(os.tmpdir(), 'monteur-archive-vide');
  for (const casse of ['marque', 'copie']) {
    const dir = clientV1(t, `Monteur IA - Coupure ${casse}`);
    personnaliser(dir);
    reelEnCours(dir);
    const plan = planifier(dir, { sujet: 'Méliès', date: '2026-10-02', archive: vide });
    // La coupure : le dossier du Reel existe, tel que tools/nouveau_reel.py le crée, noté mais pas
    // encore marqué « en-cours ». Plus tôt encore (« copie ») : la démo copiée, pas de meta.json.
    const nom = 'Méliès · 2026-10-02 · Studio Lumière';
    const reel = path.join(dir, 'reels', nom);
    for (const rel of fs.readdirSync(path.join(root, 'templates', 'demo'), { recursive: true })) {
      const src = path.join(root, 'templates', 'demo', rel);
      if (fs.statSync(src).isFile() && rel.endsWith('.demo')) write(reel, rel.slice(0, -'.demo'.length), fs.readFileSync(src));
    }
    for (const outil of fs.readdirSync(path.join(root, 'tools')).filter((f) => /\.(py|sh)$/.test(f))) {
      write(reel, `tools/${outil}`, fs.readFileSync(path.join(root, 'tools', outil)));
    }
    if (casse === 'marque') {
      write(reel, 'meta.json', JSON.stringify({ id: nom, name: nom, monteurIa: { lieu: 'reel', etat: 'en-cours', sujet: 'Méliès', date: '2026-10-02' } }));
    }
    write(dir, '.monteur-ia-reel-en-creation', `${nom}\n`);
    const r = appliquer(planifier(dir, { sujet: 'Méliès', date: '2026-10-02', archive: vide }), { npm: false });
    assert.deepEqual(fs.readdirSync(path.join(dir, 'reels')), [nom], `${casse} : un seul Reel`);
    assert.equal(r.reel.reel, path.join(dir, 'reels', nom));
    assert.equal(JSON.parse(read(r.reel.reel, 'meta.json')).monteurIa.migration, 'faite');
    assert.equal(fs.existsSync(path.join(dir, '.monteur-ia-reel-en-creation')), false, 'la note disparaît');
    assert.match(read(r.reel.reel, 'tools/sections.py'), /melies_cuts/);
    assert.ok(plan.plan.reel);
  }
});

test('le manifeste connaît chaque fichier de la dernière version publiée', (t) => {
  let arbre;
  try {
    arbre = execFileSync('git', ['ls-tree', '-r', '-z', 'origin/main'], { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  } catch {
    t.skip('historique git absent (ZIP)');
    return;
  }
  const manifeste = JSON.parse(read(root, 'scripts/versions-livrees.json')).fichiers;
  const manquants = arbre.split('\0').map((e) => /^\d+ blob ([0-9a-f]{40})\t(.+)$/s.exec(e)).filter(Boolean)
    .filter(([, h, p]) => p !== 'scripts/versions-livrees.json' && !(manifeste[p] ?? []).includes(h.slice(0, 12)))
    .map(([, , p]) => p);
  assert.deepEqual(manquants, [], 'version publiée inconnue : depuis le commit de fusion dans main, '
    + 'node scripts/mettre-a-jour.mjs --manifeste HEAD, puis committe le manifeste avant de pousser');
});

// ---------------------------------------------------------------------------
// Le parcours de MISE-A-JOUR.md tel qu'un agent le suit, téléchargement compris : ses commandes
// sont lues dans le fichier et lancées telles quelles, l'archive de GitHub remplacée par une
// archive locale de cette version (même format : monteur-ia-main/ dans un .tar.gz).
// ---------------------------------------------------------------------------
const DEPOT_ARCHIVE = 'https://github.com/Alex-lmdm/monteur-ia/archive/refs/heads/main.tar.gz';

/** Cette version, empaquetée comme GitHub la sert (fichiers suivis et nouveaux, hors ignorés). */
function archiveCommeGithub(base) {
  const liste = execFileSync('git', ['ls-files', '-z', '--cached', '--others', '--exclude-standard'], { cwd: root, encoding: 'utf8' });
  const dossier = path.join(base, 'github', 'monteur-ia-main');
  for (const rel of new Set(liste.split('\0').filter(Boolean))) {
    if (!fs.existsSync(path.join(root, rel)) || fs.statSync(path.join(root, rel)).isDirectory()) continue;
    fs.mkdirSync(path.dirname(path.join(dossier, rel)), { recursive: true });
    fs.copyFileSync(path.join(root, rel), path.join(dossier, rel));
  }
  const archive = path.join(base, 'main.tar.gz');
  execFileSync('tar', ['-czf', archive, 'monteur-ia-main'], { cwd: path.dirname(dossier) });
  return archive;
}

const blocsBash = (doc) => [...doc.matchAll(/```bash\n([\s\S]*?)```/g)].map((m) => m[1].trim());

test('MISE-A-JOUR.md : télécharger, montrer le plan, appliquer, brancher, avec les commandes du fichier', (t) => {
  if (!outilsOuSkip(t)) return;
  if (process.platform === 'win32') return t.skip('commandes bash du fichier');
  const dir = clientV1(t);
  personnaliser(dir);
  reelEnCours(dir, { packSfx: true });
  // Pack SFX 1.0.0 installé : il faudra le retélécharger depuis la formation.
  write(dir, 'assets/sfx/.pack-sfx-manifest.json', '{"pack": "pack-sfx", "version": "1.0.0", "files": {}}\n');
  write(dir, 'templates/AGENT.md.tpl', `${read(dir, 'templates/AGENT.md.tpl')}\n<!-- BEGIN EXTENSION: pack-sfx (ajouté) -->\n`
    + 'Consignes Pack SFX\n<!-- END EXTENSION: pack-sfx -->\n');
  const base = path.dirname(dir);
  const archive = archiveCommeGithub(base);
  const config = { ...process.env, HOME: base, USERPROFILE: base, CLAUDE_CONFIG_DIR: path.join(base, 'claude'),
    CODEX_HOME: path.join(base, 'codex') };
  fs.mkdirSync(config.CODEX_HOME);
  const bash = (commande, cwd = dir) => execFileSync('bash', ['-c', commande], { cwd, encoding: 'utf8', env: config });

  const doc = read(root, 'MISE-A-JOUR.md');
  assert.match(doc, /suis https:\/\/github\.com\/Alex-lmdm\/monteur-ia\/blob\/main\/MISE-A-JOUR\.md/, 'la phrase à coller');
  const blocs = blocsBash(doc);
  const bloc = (motif) => {
    const trouve = blocs.find((b) => motif.test(b));
    assert.ok(trouve, `MISE-A-JOUR.md : commande introuvable (${motif})`);
    return trouve;
  };

  // 1. Télécharger dans un dossier temporaire neuf, hors du dossier du client.
  const tmp = bash(bloc(/mkdtempSync/)).trim();
  t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));
  assert.equal(path.relative(dir, tmp).startsWith('..'), true, 'dossier temporaire hors du dossier du client');
  const telechargement = bloc(/monteur-ia\/archive\/refs\/heads\/main\.tar\.gz/);
  assert.ok(telechargement.includes(DEPOT_ARCHIVE));
  bash(telechargement.replace(DEPOT_ARCHIVE, pathToFileURL(archive).href).replaceAll('<TMP>', tmp));
  const neuf = path.join(tmp, 'monteur-ia-main');
  assert.ok(fs.existsSync(path.join(neuf, 'scripts/mettre-a-jour.mjs')), 'NEUF = <TMP>/monteur-ia-main');
  const remplir = (b) => b.replaceAll('<NEUF>', neuf).replaceAll('<CLIENT>', dir);

  // 3. Le plan, à blanc : Reel en cours, extensions à mettre à jour, branchement à faire.
  const avant = arbre(dir);
  const [planBloc, etatBloc] = bloc(/mettre-a-jour\.mjs" "<CLIENT>"\n/).split('\n');
  const planTexte = bash(remplir(planBloc));
  assert.deepEqual(arbre(dir), avant, 'le plan à blanc ne touche à rien');
  assert.match(planTexte, /Reel en cours : déplacé dans reels\/, il s'appellera « melies · \d{4}-\d{2}-\d{2} · Studio Lumière » dans l'app/);
  assert.match(planTexte, /à mettre à jour ensuite : Ton Double IA, nouvelle version sur https:\/\/github\.com\/Alex-lmdm\/double-ia/);
  assert.match(planTexte, /à mettre à jour ensuite : Pack SFX \(version 1\.0\.0 installée, il faut la 1\.1\.0 ou plus\)/);
  assert.doesNotMatch(planTexte, /tools\/double_ia\.py/, 'une extension connue est nommée, pas ses fichiers');
  assert.match(bash(remplir(etatBloc)), /à brancher/);

  // 4. Appliquer (sans npm install : pas de réseau dans les tests).
  const application = bloc(/--appliquer/);
  const sortie = bash(`${remplir(application).replace('<sujet>', 'Méliès').replace('AAAA-MM-JJ', '2026-10-02')} --sans-npm`);
  assert.match(sortie, /✅ Mis à jour/);
  assert.match(sortie, /Reel déplacé : reels\/Méliès · 2026-10-02 · Studio Lumière/);
  assert.match(sortie, /puis mets à jour : Ton Double IA, Pack SFX/);
  // Seul reste à faire : poser les sons du Pack SFX une fois le pack à jour (étape 6).
  assert.deepEqual(sortie.match(/⚠️.*/g), ['⚠️ sons : la liste du Pack SFX a suivi le Reel (work/sfx_events.json), ses sons ne sont pas encore'
    + ' dans le montage. Pack SFX à jour (1.1.0 ou plus), lance python3 tools/sfx_mix.py depuis le Reel.']);
  assert.ok(fs.existsSync(path.join(dir, 'Accueil · Studio Lumière', 'index.html')));
  const encore = bash(remplir(planBloc));
  assert.match(encore, /Moteur déjà à jour/);
  assert.match(encore, /Ton Double IA/, 'les extensions restent à mettre à jour tant qu’elles ne le sont pas');

  // 5. Brancher, depuis le dossier du client : la config isolée reçoit la variable.
  bash(bloc(/app-hyperframes\.mjs brancher/));
  assert.equal(JSON.parse(fs.readFileSync(path.join(config.CLAUDE_CONFIG_DIR, 'settings.json'), 'utf8'))
    .env.CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD, '1');
  assert.match(fs.readFileSync(path.join(config.CODEX_HOME, 'config.toml'), 'utf8'), /project_doc_max_bytes = 131072/);

  // 6. Extensions mises à jour (leurs nouvelles versions écrivent pour les Reels) : plus rien à faire.
  write(dir, 'tools/double_ia.py', 'from lieux import MAISON, REEL\n');
  write(dir, 'assets/sfx/.pack-sfx-manifest.json', '{"pack": "pack-sfx", "version": "1.1.0", "files": {}}\n');
  assert.match(bash(remplir(planBloc)), /Déjà à jour : rien à faire\./);
  for (const url of ['double-ia', 'systeme-stories']) {
    assert.ok(blocs.some((b) => b.includes(`https://github.com/Alex-lmdm/${url}/archive/refs/heads/main.tar.gz`)), `${url} : téléchargement décrit`);
  }
  // Étape 4 : la ligne du contrôle que la commande affiche est bien celle que le fichier fait traiter.
  assert.match(read(root, 'scripts/mettre-a-jour.mjs'), /contrôle HyperFrames \(lint\) : \$\{/);
  assert.match(doc, /« contrôle HyperFrames \(lint\) : à revoir »/);

  // 8. Le dossier temporaire se supprime ; la commande refuse tout autre dossier, à commencer par celui du client.
  const nettoyage = bloc(/rmSync/);
  assert.throws(() => bash(nettoyage.replaceAll('<TMP>', dir)), (e) => /Refusé/.test(e.stderr));
  assert.ok(fs.existsSync(path.join(dir, 'templates/AGENT.md.tpl')), 'le dossier du client est intact');
  const voisin = fs.mkdtempSync(path.join(base, 'monteur-ia-'));   // bon nom, mauvais endroit
  assert.throws(() => bash(nettoyage.replaceAll('<TMP>', voisin)), (e) => /Refusé/.test(e.stderr));
  assert.ok(fs.existsSync(voisin));
  bash(nettoyage.replaceAll('<TMP>', tmp));
  assert.equal(fs.existsSync(tmp), false, 'dossier temporaire supprimé');
});


test("Système Stories d'avant la story montée comme un Reel (déjà écrite pour les Reels) est à mettre à jour", async (t) => {
  const { EXTENSIONS } = await import(pathToFileURL(path.join(root, 'scripts/mettre-a-jour.mjs')).href);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-stories-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  fs.mkdirSync(path.join(dir, 'tools'));
  const story = path.join(dir, 'tools/story.py');
  fs.writeFileSync(story, 'from lieux import MAISON as ROOT\n');
  assert.equal(EXTENSIONS['systeme-stories'].aJour(dir), false, 'une story doit devenir un projet de l’app');
  fs.writeFileSync(story, 'from lieux import MAISON as ROOT\ndef composer(slug, publiee=False, ecraser=False, auto=True):\n    pass\n');
  assert.equal(EXTENSIONS['systeme-stories'].aJour(dir), true);
});
