// Mode YouTube (skill youtube, templates/youtube/) : une vidéo YouTube est un projet 16:9 complet,
// ses consignes ne parlent que de YouTube, ses outils ne se mélangent jamais avec ceux des Reels, et
// les Reels n'en sont pas alourdis.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync, spawnSync } from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (dir, name) => fs.readFileSync(path.join(dir, name), 'utf8');
function write(dir, name, value) {
  fs.mkdirSync(path.dirname(path.join(dir, name)), { recursive: true });
  fs.writeFileSync(path.join(dir, name), typeof value === 'string' ? value : JSON.stringify(value));
}
const git = (dir, ...args) => execFileSync('git', args, { cwd: dir, encoding: 'utf8' });
const shipped = () => git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')
  .split('\0').filter((f) => f && fs.existsSync(path.join(root, f)));
const sync = (dir) => execFileSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
const config = () => JSON.parse(read(root, 'brand.config.example.json'));
const exists = (dir, name) => fs.existsSync(path.join(dir, name));

function outils(t, ...cmds) {
  for (const cmd of ['python3', ...cmds]) {
    try {
      execFileSync(cmd, [cmd === 'python3' ? '--version' : '-version'], { stdio: 'ignore' });
    } catch {
      t.skip(`${cmd} absent`);
      return false;
    }
  }
  return true;
}
// Copie complète du template livré (sans les skills), dans un dossier temporaire.
function maison(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-youtube-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  for (const file of shipped().filter((f) => !/^\.(agents|claude)\//.test(f))) {
    fs.mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
    fs.copyFileSync(path.join(root, file), path.join(dir, file));
  }
  return dir;
}
const python = (cwd, ...args) => execFileSync('python3', args, { cwd, encoding: 'utf8', stdio: 'pipe' });
function nouvelle(dir, sujet = 'Ma vidéo', ...args) {
  python(dir, 'tools/nouvelle_video_youtube.py', sujet, '--date', '2026-10-15', ...args);
  return path.join(dir, 'youtube', `${sujet} · 2026-10-15 · ${path.basename(dir)}`);
}

test('une vidéo YouTube est un projet 16:9 complet, avec ses consignes et ses seuls outils', (t) => {
  if (!outils(t)) return;
  const dir = maison(t);
  const video = nouvelle(dir);
  const meta = JSON.parse(read(video, 'meta.json'));
  assert.deepEqual([meta.monteurIa.lieu, meta.monteurIa.etat, meta.monteurIa.format], ['youtube', 'en-cours', '16:9']);
  for (const file of ['index.html', 'compositions/exemple-panneau.html', 'derush/exemple_cuts.json', 'derush/exemple_words.json',
    'brand/tokens.css', 'brand/fonts.css', 'assets/vendor/gsap.min.js', 'hyperframes.json', 'package.json',
    'tools/sections.py', 'tools/build_master.py', 'tools/build_faces.py', 'tools/build_emphases.py', 'tools/finaliser.py',
    'tools/check_export.py', 'tools/build_sfx.py', 'tools/publication.py', 'tools/ranger.py', 'tools/lieux.py',
    'tools/sons.py', 'tools/ecarts_derush.py', 'tools/cut_boundaries.py', 'tools/build_words.py', 'tools/ranger_reel.py',
    'tools/prises.py']) {
    assert.ok(exists(video, file), `vidéo YouTube sans ${file}`);
  }
  // Jamais un outil vertical des Reels : même nom, autre géométrie.
  for (const file of ['tools/build_final.py', 'tools/cadrage.py', 'tools/montage_captions.py', 'tools/build_overlay.py',
    'tools/nouveau_reel.py', 'compositions/captions.html']) {
    assert.ok(!exists(video, file), `${file} n'a rien à faire dans une vidéo YouTube`);
  }
  assert.match(read(video, 'tools/sections.py'), /A CHAQUE VIDEO/);
  assert.match(read(video, 'tools/build_sfx.py'), /youtube\.musicDb/, 'la liste de sons des vidéos YouTube, pas celle des Reels');
  assert.match(read(video, 'index.html'), /data-width="1920" data-height="1080"/);

  // Ses consignes : le skill youtube, sans le pipeline vertical des Reels, sous la limite de Codex.
  const claude = read(video, 'CLAUDE.md');
  assert.match(claude, /Tu es dans la vidéo YouTube « Ma vidéo · 2026-10-15/);
  assert.match(claude, /skill \*\*`youtube`\*\*/);
  assert.match(claude, /Préférences YouTube apprises/);
  assert.match(claude, /`\.\.\/\.\.\/\.claude\/skills\/<nom>\/SKILL\.md`/);
  assert.doesNotMatch(claude, /Ordre séquentiel VERROUILLÉ|Checklist anti-oubli|Le pipeline en 7 étapes|Première vidéo : tout monter/);
  assert.doesNotMatch(claude, /\{\{[#/]/, 'aucun marqueur de modèle oublié');
  assert.ok(Buffer.byteLength(read(video, 'AGENTS.md')) < 16 * 1024);

  // Les outils tournent sur la démo : sections, textes d'appui, SRT, master, chapitres.
  assert.match(python(video, 'tools/sections.py'), /^exemple-panneau\s+cote\s+00:03/m);
  python(video, 'tools/build_emphases.py', '--write');
  assert.match(read(video, 'compositions/emphases.html'), />LE RYTHME</);
  assert.match(read(video, 'exports/sous-titres.srt'), /^1\n00:00:00,\d{3} --> /);
  python(video, 'tools/build_master.py', '--write');
  const master = read(video, 'index.html');
  assert.match(master, /<video id="video-large" src="assets\/video\/base\.mp4"/);
  assert.match(master, /data-composition-src="compositions\/exemple-panneau\.html"[^>]*left:960px/);
  assert.match(master, /data-composition-src="compositions\/emphases\.html"/);
  assert.match(master, /<!-- SONS -->/);
  python(video, 'tools/publication.py');
  assert.match(read(video, 'publication.md'), /<!-- CHAPITRES:DEBUT -->\nChapitres :\n00:00 Introduction/);
});

test('la synchro garde les outils propres à la vidéo, rafraîchit les autres, sans toucher aux Reels', (t) => {
  if (!outils(t)) return;
  const dir = maison(t);
  const video = nouvelle(dir);
  python(dir, 'tools/nouveau_reel.py', 'Un Reel', '--date', '2026-10-15');
  const reel = path.join(dir, 'reels', `Un Reel · 2026-10-15 · ${path.basename(dir)}`);
  write(video, 'tools/sections.py', read(video, 'tools/sections.py').replace('exemple_cuts.json', 'ma-video_cuts.json'));
  write(video, 'tools/check_export.py', '# copie abîmée\n');
  write(video, 'tools/lieux.py', '# copie abîmée\n');
  sync(dir);
  assert.match(read(video, 'tools/sections.py'), /ma-video_cuts\.json/, 'outil adapté à la vidéo : gardé');
  assert.equal(read(video, 'tools/check_export.py'), read(dir, 'templates/youtube/tools/check_export.py'));
  assert.equal(read(video, 'tools/lieux.py'), read(dir, 'tools/lieux.py'));
  // Le Reel garde ses outils verticaux et ne reçoit aucun outil du 16:9.
  assert.equal(read(reel, 'tools/check_export.py'), read(dir, 'tools/check_export.py'));
  assert.equal(read(reel, 'tools/sections.py'), read(dir, 'tools/sections.py'));
  for (const file of ['tools/build_emphases.py', 'tools/publication.py']) {
    assert.ok(!exists(reel, file), `${file} ne doit pas arriver dans un Reel`);
  }
  // Même nom, deux finalisations : -16 LUFS pour le Reel, -14 LUFS pour la vidéo, jamais échangées.
  assert.equal(read(reel, 'tools/finaliser.py'), read(dir, 'tools/finaliser.py'));
  assert.equal(read(video, 'tools/finaliser.py'), read(dir, 'templates/youtube/tools/finaliser.py'));
  // Une vidéo publiée garde le style qu'elle avait.
  const meta = JSON.parse(read(video, 'meta.json'));
  write(video, 'meta.json', { ...meta, monteurIa: { ...meta.monteurIa, etat: 'publie' } });
  const avant = read(video, 'brand/tokens.css');
  write(dir, 'brand.config.json', { ...config(), visual: { ...config().visual, stylePreset: 'neutral', accent: '#ff0055' } });
  sync(dir);
  assert.equal(read(video, 'brand/tokens.css'), avant);
  assert.match(read(reel, 'brand/tokens.css'), /#ff0055/i);
});

test("les consignes aiguillent vers YouTube là où une vidéo peut naître, sans alourdir les Reels", (t) => {
  if (!outils(t)) return;
  const dir = maison(t);
  python(dir, 'tools/nouveau_reel.py', 'Un Reel', '--date', '2026-10-15');
  write(dir, 'stories/promo/meta.json', { monteurIa: { lieu: 'story', etat: 'en-cours' } });
  sync(dir);
  const reel = path.join(dir, 'reels', `Un Reel · 2026-10-15 · ${path.basename(dir)}`);
  const racine = read(dir, 'CLAUDE.md');
  assert.match(racine, /## ▶️ Vidéo YouTube \(16:9\)/);
  assert.match(racine, /`python3 tools\/nouvelle_video_youtube\.py "<sujet>"/);
  assert.match(racine, /Checklist anti-oubli/, 'la racine garde la checklist des Reels');
  const accueil = read(path.join(dir, 'Accueil Monteur IA'), 'CLAUDE.md');
  assert.match(accueil, /`python3 \.\.\/tools\/nouvelle_video_youtube\.py "<sujet>" --video/);
  assert.doesNotMatch(accueil, /Checklist anti-oubli/, "rien ne se monte dans l'accueil");
  const claudeReel = read(reel, 'CLAUDE.md');
  assert.match(claudeReel, /Vidéo YouTube \(16:9\) : jamais ici/);
  assert.doesNotMatch(claudeReel, /## ▶️ Vidéo YouTube/);
  assert.match(claudeReel, /Checklist anti-oubli/);
  assert.doesNotMatch(read(path.join(dir, 'stories/promo'), 'CLAUDE.md'), /## ▶️ Vidéo YouTube/);
  for (const texte of [racine, accueil, claudeReel]) assert.doesNotMatch(texte, /\{\{[#/]/);
});

test("une vidéo YouTube coupe au rythme des Reels (respiration en option) et pose son niveau final après l'export", (t) => {
  if (!outils(t, 'ffmpeg')) return;
  const dir = maison(t);
  const video = nouvelle(dir);
  python(dir, 'tools/nouveau_reel.py', 'Un Reel', '--date', '2026-10-15');
  const reel = path.join(dir, 'reels', `Un Reel · 2026-10-15 · ${path.basename(dir)}`);
  const seuils = (cwd) => python(cwd, '-c', 'import sys; sys.path.insert(0, "tools"); import ecarts_derush as e; '
    + 'import sons, pathlib; print(e.MIN_BLANC, e.MAX_BLANC, sons.cible_lufs(pathlib.Path(".")))').trim();
  assert.equal(seuils(video), '0.15 0.6 -14.0');
  assert.equal(seuils(reel), '0.0 0.2 -16.0', 'les Reels gardent leurs réglages');
  // La cible suit les marges du dérush : rythme des Reels par défaut, respiration si youtube.derush la garde.
  const cible = (pad) => python(video, '-c', `import sys; sys.path.insert(0, "tools"); import ecarts_derush as e; print(*e.seuils(${pad}))`).trim();
  assert.equal(cible('0.04, 0.02'), '0.0 0.2');
  assert.equal(cible('0.10, 0.25'), '0.15 0.6');
  assert.equal(config().youtube.derush, null, 'par défaut, les marges des Reels');

  // Une « voix » vers -25 LUFS à crêtes brèves (crête -4 dBFS, comme une voix d'Adobe), image 1920x1080,
  // durée des coupes de la démo (9 s). Avec loudnorm, ce cas sortait à -15,8 LUFS au lieu de -14.
  const son = "anoisesrc=color=pink:amplitude=0.45:duration=9:seed=86,volume='0.6+0.4*sin(2*PI*1.7*t)':eval=frame[n];"
    + "aevalsrc='0.45*lt(mod(t,0.37),0.0012)*sin(2*PI*400*t)':s=48000:d=9[c];[n][c]amix=inputs=2:normalize=0";
  const exporter = (sortie) => execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=1920x1080:rate=30:duration=9',
    '-f', 'lavfi', '-i', son, '-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-preset', 'ultrafast',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', sortie], { cwd: video });
  exporter('assets/video/base.mp4');
  python(video, 'tools/build_master.py', '--write');
  // Pose : gain du bus vers -14 LUFS, borné par la marge de crête (au-delà, le rendu ne monte plus rien).
  const pose = python(video, 'tools/build_sfx.py');
  assert.match(pose, /finaliser\.py amène la vidéo à -14 LUFS/);
  const [, cretePose, gain] = pose.match(/crête (-?[\d.]+) dBTP ; gain \+([\d.]+) dB sur le bus/).map(Number);
  const chaine = JSON.parse(read(video, 'index.html').match(/<hf-audio-group id="mixage"[^>]*data-fx-chain="([^"]+)"/)[1]
    .replaceAll('&quot;', '"')).nodes;
  assert.deepEqual(chaine.map((n) => [n.type, Object.values(n.params)[0]]), [['gain', gain], ['limiter', -1.5]]);
  assert.equal(gain, Math.floor((-1.5 - cretePose) * 10) / 10, 'gain borné par la marge de crête');

  // Le bouton Export de l'app : renders/<id>.mp4, sa fiche, et sa copie dans Téléchargements. finaliser.py
  // (le cœur des Reels, à -14 LUFS) : niveau, crête, contrôles, puis une seule vidéo à téléverser.
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-home-'));
  t.after(() => fs.rmSync(home, { recursive: true, force: true }));
  const userbase = execFileSync('python3', ['-c', 'import site; print(site.getuserbase())'], { encoding: 'utf8' }).trim();
  const env = { ...process.env, HOME: home, USERPROFILE: home, PYTHONUSERBASE: userbase };
  const downloads = path.join(home, 'Downloads');
  fs.mkdirSync(downloads, { recursive: true });
  fs.mkdirSync(path.join(video, 'renders'), { recursive: true });
  exporter('renders/ma-video_2026-10-15_10-00-00.mp4');
  const copieApp = path.join(downloads, 'Ma vidéo 2026-10-15 10.00.mp4');
  fs.copyFileSync(path.join(video, 'renders/ma-video_2026-10-15_10-00-00.mp4'), copieApp);
  write(video, 'renders/ma-video_2026-10-15_10-00-00.meta.json', { status: 'complete', exportedTo: copieApp });
  const sortie = execFileSync('python3', ['tools/finaliser.py'], { cwd: video, env, encoding: 'utf8', stdio: 'pipe' });
  assert.match(sortie, /✅ Prête à téléverser[^\n]*remplace la copie posée par l'app/);
  const err = spawnSync('ffmpeg', ['-nostats', '-i', 'exports/FINAL-YOUTUBE.mp4', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
    { cwd: video, encoding: 'utf8' }).stderr;
  const lufs = Number([...err.matchAll(/I:\s+(-?[\d.]+) LUFS/g)].pop()[1]);
  const crete = Number([...err.matchAll(/Peak:\s+(-?[\d.]+) dBFS/g)].pop()[1]);
  assert.ok(Math.abs(lufs + 14) <= 0.5, `finalisé à ${lufs} LUFS, -14 visé`);
  assert.ok(crete <= -1, `crête à ${crete} dBTP`);
  assert.deepEqual(fs.readdirSync(downloads), [path.basename(copieApp)], 'une seule vidéo à téléverser');
  assert.ok(fs.readFileSync(copieApp).equals(fs.readFileSync(path.join(video, 'exports/FINAL-YOUTUBE.mp4'))));
  // Le même cœur que les Reels, jamais une copie qui divergerait.
  assert.equal(read(video, 'tools/niveau_final.py'), read(dir, 'tools/niveau_final.py'));
  assert.equal(read(reel, 'tools/niveau_final.py'), read(dir, 'tools/niveau_final.py'));
});

test('les cadres alternent, le glissement part du large, les alertes de rythme parlent', (t) => {
  if (!outils(t)) return;
  const dir = maison(t);
  const video = nouvelle(dir);
  // 12 prises de 5 s : un hook, un panneau, un plein écran, puis une longue section sur un seul cadre.
  const takes = Array.from({ length: 12 }, (_, i) => ({ i, start: i * 5, end: (i + 1) * 5, text: `phrase ${i}` }));
  write(video, 'derush/test_cuts.json', { source: 'derush/absent.mp4', duration: 60, takes });
  const sections = read(video, 'tools/sections.py')
    .replace('derush/exemple_cuts.json', 'derush/test_cuts.json')
    .replace(/LAYOUT = \[[\s\S]*?\n\]\n/, `LAYOUT = [
    ("s0", "face", [0, 1, 2], {"chapitre": "Introduction", "cadres": ["large", "serre"]}),
    ("s1", "cote", [3, 4]),
    ("s2", "full", [5]),
    ("s3", "face", [6, 7, 8, 9, 10, 11], {"cadre": "serre", "chapitre": "Fin"}),
]
`);
  write(video, 'tools/sections.py', sections);
  const etat = JSON.parse(python(video, '-c', 'import json, sys; sys.path.insert(0, "tools"); import sections as s; '
    + 'print(json.dumps({"cadres": [p["cadre"] for p in s.cadre_par_prise()], "cote": s.fenetres_cote(), "alertes": s.alertes()}))'));
  // Alterné large/serré, mais la prise juste avant le panneau passe en large (glissement animé).
  assert.deepEqual(etat.cadres, ['large', 'serre', 'large', 'large', 'large', null, 'serre', 'serre', 'serre', 'serre', 'serre', 'serre']);
  assert.deepEqual(etat.cote, [{ start: 15, end: 25, panneau: 'droite', avant: 'large', apres: null }]);
  // Sans option : plan large (youtube.punchIn = parcimonie, défaut) ; le serré se pose à la main.
  assert.equal(python(video, '-c', 'import sys; sys.path.insert(0, "tools"); import sections as s; print(s._cadres_par_defaut())').trim(), "['large']");
  const alertes = etat.alertes.join('\n');
  assert.match(alertes, /plan fixe de 30 s à 00:30/);
  assert.match(alertes, /YouTube n'affiche les chapitres qu'à partir de 3/);
});

test('un raccord change le cadre sur un mot sans coupe, et la 1re image montre le bon cadre', (t) => {
  if (!outils(t, 'ffmpeg')) return;
  const dir = maison(t);
  const video = nouvelle(dir);
  // Le gabarit du dérush monte d'un seul tenant deux îlots qui se touchent, et refuse ceux qui se chevauchent.
  const gabarit = read(root, '.claude/skills/derush/references/build_derush_template.py');
  const derush = (iles) => spawnSync('python3', ['-c', gabarit.replace(/ISLANDS = \[[\s\S]*?\n\]/, `ISLANDS = ${iles}`)
    .replace('SRC = "CHEMIN/VERS/video_brute.MP4"', 'SRC = "absent.mp4"')], { cwd: video, encoding: 'utf8' });
  const ok = derush('[(1.0, 2.0, "a"), (3.0, 3.75, "b"), (4.1, 5.0, "c")]');   // 3.75 + 0.02 = 3.77 ; 4.1 - 0.04 = 4.06
  assert.match(ok.stdout, /Prises : 3  \|/);
  const raccord = derush('[(1.0, 2.0, "a"), (3.0, 4.04, "b"), (4.10, 5.0, "c")]');   // 4.04 + 0.02 = 4.10 - 0.04 = 4.06
  assert.match(raccord.stdout, /Prises : 3 \(dont 1 raccord\(s\) sans coupe\)/);
  assert.match(derush('[(1.0, 2.0, "a"), (1.5, 3.0, "b")]').stderr, /prises qui se chevauchent/);

  // Prises : 0-2 hook large, 3 serré imposé juste avant le panneau, 4-5 panneau, 6 en raccord avec 5.
  const takes = Array.from({ length: 8 }, (_, i) => ({ i, start: i * 3, end: (i + 1) * 3, text: `phrase ${i}` }));
  takes[7].raccord = true;
  write(video, 'derush/test_cuts.json', { source: 'derush/absent.mp4', duration: 24, takes });
  write(video, 'tools/sections.py', read(video, 'tools/sections.py')
    .replace('derush/exemple_cuts.json', 'derush/test_cuts.json')
    .replace(/LAYOUT = \[[\s\S]*?\n\]\n/, `LAYOUT = [
    ("s0", "face", [0, 1, 2], {"cadre": "large"}),
    ("s1", "face", [3], {"cadre": "serre"}),
    ("s2", "cote", [4, 5]),
    ("s3", "face", [6, 7], {"cadres": ["large", "tres-serre"]}),
]
`));
  fs.copyFileSync(path.join(video, 'compositions/exemple-panneau.html'), path.join(video, 'compositions/s2.html'));
  python(video, 'tools/build_master.py', '--write');
  const master = read(video, 'index.html');
  // État de départ dans le CSS (un tl.set à 0 n'est pas rendu sur la 1re image).
  assert.match(master, /#visage-serre \{ opacity: 0; visibility: hidden; \}/);
  assert.match(master, /#visage-tres-serre \{ opacity: 0; visibility: hidden; \}/);
  assert.doesNotMatch(master, /tl\.set\("#visage-[a-z-]+", \{ autoAlpha: [01] \}, 0\);/);
  // Le glissement part du large même après une prise serrée.
  assert.match(master, /tl\.fromTo\("#visage-large", \{ x: 0 \}, \{ x: -480, duration: 0\.6/);
  // Le raccord (prise 7) change le cadre à 21 s.
  assert.match(master, /tl\.set\("#visage-tres-serre", \{ autoAlpha: 1 \}, 20\.99967\);/);

  // Sous-titres : jamais à cheval sur une coupe, même sans point ; un raccord n'en est pas une ;
  // une phrase trop longue se partage sans mot faible en bout.
  const srt = JSON.parse(python(video, '-c', `import json, sys; sys.path.insert(0, "tools"); import build_emphases as b
def m(w, s, k): return {"w": w, "n": b.normal(w), "start": s, "end": s + 0.2, "take": k}
liste = [m("monte", 5.0, 1), m("ma", 5.2, 1), m("vidéo", 5.4, 1), m("Il", 6.1, 2), m("a", 6.3, 2), m("coupé", 6.5, 2),
         m("Le", 20.3, 6), m("Mode", 20.5, 6), m("est", 20.7, 6), m("offert", 21.0, 7), m("avec", 21.25, 7)]
longue = [m(x, 30 + 0.2 * k, 9) for k, x in enumerate("Il a coupé les blancs et les ratés sans jamais rien abîmer".split())]
print(json.dumps([p["texte"] for p in b.phrases(liste)] + [p["texte"] for p in b.phrases(longue)]))`));
  assert.deepEqual(srt.slice(0, 3), ['monte ma vidéo', 'Il a coupé', 'Le Mode est offert avec']);
  for (const ligne of srt.slice(3)) assert.doesNotMatch(ligne, /\s(les|et|de|le|la)$/, `« ${ligne} » finit sur un mot faible`);
});

test("l'outil des prises garde la dernière prise propre de chaque phrase et écarte bruits et faux départs", (t) => {
  if (!outils(t)) return;
  const dir = maison(t);
  const video = nouvelle(dir);
  // Le rush du test de la vidéo de démonstration : reprises, faux départ, hallucinations de Whisper.
  const sortie = python(video, '-c', `import json, sys; sys.path.insert(0, "tools"); import prises as P
def p(n, a, b, texte): return {"n": n, "debut": a, "fin": b, "texte": texte}
rush = [p(0, 1.18, 1.19, "Sous-titrage Société Radio-Canada"), p(1, 5.66, 7.21, "Cette vidéo, ce n'est pas moi qui l'ai montée."),
  p(2, 25.96, 28.12, "J'ai donné la vidéo brute à mon monteur."), p(3, 35.21, 36.90, "J'ai donné la vidéo brute à Claude."),
  p(4, 53.32, 55.28, "Il change de cadre à chaque coupe, comme là."), p(5, 57.40, 58.44, "Il change de cadre."),
  p(6, 59.07, 61.63, "Il change de cadre à chaque coupe, comme tu peux le voir ici."),
  p(7, 72.62, 73.88, "Et quand j'explique quelque chose,"), p(8, 76.70, 78.08, "il me décale sur le côté"),
  p(9, 82.98, 87.26, "Et quand j'explique quelque chose, il me décale sur le côté pour montrer un schéma à côté de moi."),
  p(10, 100.92, 101.35, "Sous-titrage Société Radio-Canada"), p(11, 127.75, 127.75, "Merci."),
  p(12, 140.42, 142.71, "Le mode YouTube est offert avec ton achat"), p(13, 147.52, 149.85, "Le mode YouTube est offert avec Monteria."),
  p(14, 151.40, 154.94, "Le mode YouTube est offert avec Monteria, tu le reçois dès ton achat."),
  p(15, 160.0, 162.0, "Le Mode YouTube est simple."), p(16, 163.0, 164.0, "Le Mode YouTube")]
script = ["Le Mode YouTube est offert avec Monteur IA.", "Tu le reçois dès ton achat.", "Le Mode YouTube est simple."]
P.choisir(rush, script)
print(json.dumps({x["n"]: x["statut"] for x in rush}))`);
  const statut = JSON.parse(sortie);
  assert.deepEqual(Object.keys(statut).filter((n) => statut[n] === 'garde').map(Number), [1, 3, 6, 9, 14, 15]);
  for (const n of [0, 10, 11]) assert.equal(statut[n], 'bruit');
  for (const n of [2, 4, 5, 7, 8, 12, 13]) assert.equal(statut[n], 'reprise');
  assert.equal(statut[16], 'faux depart', 'une prise qui recommence la précédente sans aller au bout');
});

test('le Pack SFX installé arrive dans les vidéos YouTube (nouvelles et existantes) à partir de sa 1.2.0', (t) => {
  if (!outils(t)) return;
  const dir = maison(t);
  const avant = nouvelle(dir, 'Avant le pack');
  assert.ok(!exists(avant, 'tools/sfx_mix.py'), 'sans pack, rien à copier');
  // Pack 1.1.0 : il ne connaît pas les vidéos YouTube (musique et repères des Reels). Ses outils restent
  // hors des vidéos et le client apprend, à la création, qu'il doit le retélécharger.
  const pack = (version) => write(dir, 'assets/sfx/.pack-sfx-manifest.json', { pack: 'pack-sfx', version, files: {} });
  pack('1.1.0');
  write(dir, 'tools/sfx.py', '# Pack SFX (test)\n');
  write(dir, 'tools/sfx_mix.py', '# Pack SFX (test)\n');
  sync(dir);
  assert.ok(!exists(avant, 'tools/sfx_mix.py'), 'pack 1.1.0 : pas dans une vidéo existante');
  const sortie = python(dir, 'tools/nouvelle_video_youtube.py', 'Ancien pack', '--date', '2026-10-15');
  assert.match(sortie, /Pack SFX 1\.1\.0 : il ne sonorise pas encore les vidéos YouTube[^\n]*retélécharger depuis sa formation/);
  const ancien = path.join(dir, 'youtube', `Ancien pack · 2026-10-15 · ${path.basename(dir)}`);
  assert.ok(!exists(ancien, 'tools/sfx.py') && !exists(ancien, 'tools/sfx_mix.py'), 'pack 1.1.0 : pas dans une nouvelle vidéo');
  assert.ok(exists(ancien, 'tools/build_sfx.py'), 'les sons se posent par build_sfx.py');
  // Pack 1.2.0 : ses outils arrivent partout, sans message.
  pack('1.2.0');
  sync(dir);
  assert.equal(read(avant, 'tools/sfx_mix.py'), '# Pack SFX (test)\n', 'vidéo existante : outils du pack mirroirés');
  assert.equal(read(ancien, 'tools/sfx_mix.py'), '# Pack SFX (test)\n');
  const sortieApres = python(dir, 'tools/nouvelle_video_youtube.py', 'Après le pack', '--date', '2026-10-15');
  assert.doesNotMatch(sortieApres, /Pack SFX/);
  const apres = path.join(dir, 'youtube', `Après le pack · 2026-10-15 · ${path.basename(dir)}`);
  assert.ok(exists(apres, 'tools/sfx.py') && exists(apres, 'tools/sfx_mix.py'), 'nouvelle vidéo : outils du pack copiés');
});
