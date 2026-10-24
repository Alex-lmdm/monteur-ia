// Moteur du montage d'un Reel : sous-titres (alignement sur la voix, bornes sur les images, allure),
// sons posés dans le montage, cadrage du visage, réglages propres à un Reel. Chaque réglage optionnel
// laisse, absent, le résultat d'avant à l'identique.
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
  fs.writeFileSync(path.join(dir, name), typeof value === 'string' ? value : JSON.stringify(value, null, 1));
}
const git = (dir, ...args) => execFileSync('git', args, { cwd: dir, encoding: 'utf8' });
const shipped = () => git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')
  .split('\0').filter((f) => f && fs.existsSync(path.join(root, f)));
const config = () => JSON.parse(read(root, 'brand.config.example.json'));
const sync = (dir) => execFileSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });

function outils(t, { ffmpeg = false, pil = false } = {}) {
  const manque = (cmd, args) => spawnSync(cmd, args, { stdio: 'ignore' }).status !== 0;
  if (manque('python3', ['--version'])) return t.skip('python3 absent'), false;
  if (pil && manque('python3', ['-c', 'import PIL'])) return t.skip('Pillow absent'), false;
  if (ffmpeg && (manque('ffmpeg', ['-version']) || manque('ffprobe', ['-version']))) return t.skip('ffmpeg absent'), false;
  return true;
}
const python = (cwd, ...args) => execFileSync('python3', args, { cwd, encoding: 'utf8', stdio: 'pipe' });
// Copie complète du template livré (sans les skills), dans un dossier temporaire.
function maison(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'monteur-montage-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  for (const file of shipped().filter((f) => !/^\.(agents|claude)\//.test(f))) {
    fs.mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
    fs.copyFileSync(path.join(root, file), path.join(dir, file));
  }
  return dir;
}
function nouveauReel(dir, sujet = 'Essai') {
  python(dir, 'tools/nouveau_reel.py', sujet, '--date', '2026-10-15');
  return path.join(dir, 'reels', `${sujet} · 2026-10-15 · ${path.basename(dir)}`);
}

// Un Reel de trois prises, ses mots tels que Whisper les rend et le découpage écrit à la main.
// prises : [[début, fin, [[mot, départ], ...], [chunk, ...]], ...]
function plan(reel, prises, { layout = null, duree = null } = {}) {
  const fin = duree ?? prises.at(-1)[1];
  write(reel, 'derush/exemple_cuts.json', {
    source: 'derush/exemple_enhanced.mp4', duration: fin,
    takes: prises.map(([a, b], i) => ({ i, start: a, end: b, text: '' })),
  });
  write(reel, 'derush/exemple_words.json', prises.flatMap(([, , mots], i) =>
    mots.map(([w, start]) => ({ w, start, end: start + 0.2, take: i }))));
  const manual = `MANUAL = [\n${prises.map(([, , , chunks]) => `    ${JSON.stringify(chunks)},`).join('\n')}\n]`;
  write(reel, 'tools/montage_captions.py', read(reel, 'tools/montage_captions.py')
    .replace(/MANUAL = \[\n[\s\S]*?\n\]/, manual));
  if (layout) {
    write(reel, 'tools/sections.py', read(reel, 'tools/sections.py')
      .replace('    ("exemple-section", "split", [0, 1, 2]),', layout));
  }
}
// Les sous-titres générés : texte, y, départ et durée tels qu'écrits dans le HTML.
function sousTitres(reel, ...args) {
  const sortie = python(reel, 'tools/montage_captions.py', ...args);
  const html = read(reel, args.includes('--write') ? 'compositions/captions.html' : 'work/captions.generated.html');
  const caps = [...html.matchAll(/<div class="cap clip" id="cap-(\d+)" style="top:(\d+)px" data-start="([\d.]+)" data-duration="([\d.]+)"[^>]*>(.*?)<\/div>/g)]
    .map(([, , y, start, dur, texte]) => ({ texte, y: Number(y), start: Number(start), dur: Number(dur) }));
  return { caps, html, sortie };
}
const image = (t) => Math.round(t * 30);

// ---------------------------------------------------------------------------
// 1. Nombres : le sous-titre retrouve son premier mot, que le nombre soit en chiffres ou en lettres
// ---------------------------------------------------------------------------
test('un nombre écrit en chiffres dans le découpage retrouve le mot de la voix, en lettres ou en chiffres', (t) => {
  if (!outils(t, { pil: true })) return;
  const reel = nouveauReel(maison(t));
  plan(reel, [
    [0, 2.4, [['Ensuite,', 0.1], ['il', 0.5], ['dessine', 0.7], ['trois', 1.2], ['concepts.', 1.5]],
      ['ensuite', 'il dessine', '3 concepts']],
    [2.4, 5.1, [['À', 2.5], ['plus', 2.6], ['de', 2.8], ['mille', 3.1], ['quatre', 3.4], ['cents', 3.6], ['vrais', 3.9], ['logos.', 4.2]],
      ['à plus de', '1 400 vrais logos']],
    [5.1, 8.0, [['Et', 5.2], ['50', 5.5], ['%', 5.8], ['de', 6.1], ['réussite,', 6.4], ['vingt-deux', 7.0], ['fois.', 7.5]],
      ['et 50 %', 'de réussite', 'vingt deux fois']],
  ]);
  const { caps } = sousTitres(reel);
  const depart = (texte) => caps.find((c) => c.texte === texte).start;
  assert.equal(image(depart('3 CONCEPTS')), image(1.2), '« 3 » = « trois »');
  assert.equal(image(depart('1 400 VRAIS LOGOS')), image(3.1), '« 1 400 » = « mille quatre cents »');
  assert.equal(image(depart('DE RÉUSSITE')), image(6.1));
  assert.equal(image(depart('VINGT DEUX FOIS')), image(7.0), '« vingt deux » = « vingt-deux »');
});

test('les nombres : chiffres, lettres, milliers et pourcentages ; un texte sans nombre reste un jeton par mot', (t) => {
  if (!outils(t)) return;
  const jetons = (...textes) => JSON.parse(python(path.join(root, 'tools'), '-c',
    'import json, sys; from nombres import jetons; print(json.dumps([[j for j, _ in jetons(t.split())] for t in sys.argv[1:]]))', ...textes));
  assert.deepEqual(jetons('trois', '3', 'quatre-vingt-dix-neuf', 'soixante et onze', 'mille quatre cents', '1 400',
    '1 400', '150 000', 'deux cents', 'deux millions trois cent mille', '50 %', 'cinquante pour cent', 'dix-sept'),
  [['3'], ['3'], ['99'], ['71'], ['1400'], ['1400'], ['1400'], ['150000'], ['200'], ['2300000'], ['50%'], ['50%'], ['17']]);
  // « un », « une » seuls restent des articles ; deux nombres qui se suivent ne fusionnent pas.
  assert.deepEqual(jetons('un logo', 'une tasse', 'deux trois', 'en 2026'), [['un', 'logo'], ['une', 'tasse'], ['2', '3'], ['en', '2026']]);
  // Sans nombre : exactement la normalisation d'avant, un jeton par mot (alignement inchangé).
  const phrase = "Ça s'appelle Logo Design Skill, et c'est peut-être le meilleur ? vraiment ! 🔗";
  const attendu = phrase.split(/\s+/).map((m) => m.normalize('NFD').toLowerCase().replace(/\p{Mn}/gu, '').replace(/[^a-z0-9%]/g, ''));
  assert.deepEqual(jetons(phrase), [attendu]);
});

// ---------------------------------------------------------------------------
// 2. Bornes sur les images du rendu : sous-titres, sections et durée tombent sur des images exactes
// ---------------------------------------------------------------------------
// Règle du rendu (HyperFrames 0.8.136, vérifiée par un vrai rendu) : un clip s'affiche à partir de
// la première image n telle que n / 30 >= data-start (à 0,001 image près). Une coupe à 2,667 s
// (image 80,01) s'affichait donc à l'image 81, une image après le visage (posé, lui, sur l'image 80).
const premiereImage = (t) => {
  const f = t * 30;
  return Math.abs(f - Math.round(f)) <= 0.001 ? Math.round(f) : Math.ceil(f);
};
// Trois prises coupées entre deux images, la deuxième en plein écran motion.
const PRISES_HORS_IMAGES = [
  [0, 2.667, [['Désolé', 0.03], ['pour', 0.28], ['les', 0.48], ['graphistes,', 0.52], ['mais', 1.016], ['Claude', 1.18]],
    ['désolé', 'pour les graphistes', 'mais Claude']],
  [2.667, 5.345, [['Quelqu’un', 2.71], ['a', 3.05], ['créé', 3.112], ['un', 3.6], ['repo', 3.71], ['GitHub.', 3.95]],
    ["quelqu'un a créé", 'un repo GitHub']],
  [5.345, 8.008, [['Il', 5.4], ['étudie', 5.52], ['ton', 6.016], ['secteur.', 6.2]], ['il étudie', 'ton secteur']],
];
const LAYOUT_SPLIT_FULL_SPLIT = '    ("s0", "split", [0]),\n    ("s1", "full", [1]),\n    ("s2", "split", [2]),';

test('sous-titres, sections et durée posés sur les images : jamais une image de retard, ni une image de trop', (t) => {
  if (!outils(t, { pil: true })) return;
  const reel = nouveauReel(maison(t));
  plan(reel, PRISES_HORS_IMAGES, { layout: LAYOUT_SPLIT_FULL_SPLIT });
  const { caps, html } = sousTitres(reel);
  // Chaque borne tombe sur une image : départ un centième d'image sous la frontière, durée entière.
  for (const c of caps) {
    const k = premiereImage(c.start);
    assert.ok(c.start === 0 || Math.abs((c.start * 30 + 0.01) - k) < 1e-3, `${c.texte} : départ ${c.start} hors image`);
    assert.ok(Math.abs(c.dur * 30 - Math.round(c.dur * 30)) < 1e-3, `${c.texte} : durée ${c.dur} hors image`);
  }
  // Le sous-titre arrive sur l'image la plus proche de son mot, et ne bouge que de là : par rapport
  // à l'ancien départ au millième, au plus une image plus tôt, jamais plus tard.
  const attendu = { 'POUR LES GRAPHISTES': 0.28, 'MAIS CLAUDE': 1.016, 'UN REPO GITHUB': 3.6, 'TON SECTEUR': 6.016 };
  for (const [texte, mot] of Object.entries(attendu)) {
    const c = caps.find((x) => x.texte === texte);
    assert.equal(premiereImage(c.start), Math.round(mot * 30), `${texte} sur l'image de son mot`);
    assert.ok([0, -1].includes(premiereImage(c.start) - premiereImage(Number(mot.toFixed(3)))), `${texte} : déplacé de plus d'une image`);
  }
  // La 1re image du Reel porte un sous-titre (avant : image 1, le 1er mot tombant 0,03 s après la coupe).
  assert.equal(caps[0].start, 0);
  // Coupe à 2,667 s = image 80 : le dernier sous-titre du split finit à 80, celui du plein écran y
  // commence, à sa hauteur ; même règle que les sections et le visage dans le master.
  const avant = caps.find((c) => c.texte === 'MAIS CLAUDE');
  const apres = caps.find((c) => c.texte === "QUELQU&#x27;UN A CRÉÉ");
  assert.equal(premiereImage(avant.start + avant.dur), 80);
  assert.equal(premiereImage(apres.start), 80);
  assert.deepEqual([avant.y, apres.y], [920, 1500]);
  python(reel, 'tools/build_master.py', '--write');
  const master = read(reel, 'index.html');
  const debut = (id) => Number(new RegExp(`id="${id}"[^>]*data-start="([\\d.]+)"`).exec(master)[1]);
  assert.deepEqual(['section-s0', 'section-s1', 'section-s2'].map((id) => premiereImage(debut(id))), [0, 80, 160]);
  assert.deepEqual(['faceA', 'faceB'].map((id) => premiereImage(debut(id))), [0, 160], 'visage et sections sur les mêmes images');
  // Durée : un nombre entier d'images (8,008 s = 240,24 images : le rendu en sortait 241).
  assert.match(master, /data-composition-id="main" data-start="0" data-duration="8\.0"/);
  assert.match(html, /data-composition-id="captions" data-start="0" data-duration="8\.0"/);
  assert.equal(premiereImage(caps.at(-1).start + caps.at(-1).dur), 240);
});

// Le même Reel rendu pour de vrai (lent : MONTEUR_RENDU=1 npm test, à chaque nouvelle version de
// HyperFrames). Chaque section et chaque sous-titre a sa couleur ; à chaque image rendue, on lit la
// section et le sous-titre visibles : aucune image en retard, aucune image de l'ancienne section ou
// de l'ancien sous-titre après une coupe, un sous-titre dès la 1re image, la durée en images entières.
const cliHyperframes = () => path.join(root, 'node_modules', '.bin', process.platform === 'win32' ? 'hyperframes.cmd' : 'hyperframes');
test('rendu : à chaque coupe, section, sous-titre et hauteur changent sur la même image', { skip: !process.env.MONTEUR_RENDU }, (t) => {
  if (!outils(t, { pil: true, ffmpeg: true })) return;
  const reel = nouveauReel(maison(t));
  plan(reel, PRISES_HORS_IMAGES, { layout: LAYOUT_SPLIT_FULL_SPLIT });
  const gris = { s0: 60, s1: 120, s2: 180 };
  for (const [id, g] of Object.entries(gris)) {
    const h = id === 's1' ? 1920 : 920;
    write(reel, `compositions/${id}.html`, `<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>
<div id="${id}" data-composition-id="${id}" data-start="0" data-duration="9" data-width="1080" data-height="${h}" style="position:absolute;left:0;top:0;width:1080px;height:${h}px;background:rgb(${g},${g},${g})"></div>
<script>window.__timelines=window.__timelines||{};window.__timelines["${id}"]=gsap.timeline({paused:true});</script></body></html>`);
  }
  const { caps } = sousTitres(reel, '--write');
  // Un sous-titre = un bandeau rouge dont le vert porte son numéro (texte transparent).
  const couleurs = caps.map((_, n) => `#cap-${n}{background:rgb(255,${10 + 20 * n},0)!important;color:transparent!important}`).join('');
  write(reel, 'compositions/captions.html', read(reel, 'compositions/captions.html').replace('</head>', `<style>${couleurs}</style></head>`));
  python(reel, 'tools/build_master.py', '--write');
  execFileSync(cliHyperframes(), ['render', '-o', 'exports/FINAL.mp4'], { cwd: reel, stdio: 'ignore', timeout: 600000 });
  const pixels = (y) => {
    const brut = execFileSync('ffmpeg', ['-v', 'error', '-i', path.join(reel, 'exports/FINAL.mp4'), '-vf',
      `format=rgb24,crop=1:1:540:${y}`, '-f', 'rawvideo', '-'], { maxBuffer: 1 << 24 });
    return Array.from({ length: brut.length / 3 }, (_, n) => [brut[3 * n], brut[3 * n + 1], brut[3 * n + 2]]);
  };
  const [haut, joint, bas] = [pixels(400), pixels(920), pixels(1500)];
  assert.equal(haut.length, 240, '8,008 s = 240 images (pas 241)');
  const sousTitre = ([r, g]) => (r > 200 ? Math.max(0, Math.round((g - 10) / 20)) : null);
  for (let n = 0; n < haut.length; n += 1) {
    const section = n < 80 ? 's0' : n < 160 ? 's1' : 's2';
    assert.ok(Math.abs(haut[n][0] - gris[section]) < 12, `image ${n} : section ${section} attendue, gris ${haut[n][0]}`);
    const attendu = caps.findIndex((c) => premiereImage(c.start) <= n && n < premiereImage(c.start + c.dur));
    const [aJoint, aBas] = [sousTitre(joint[n]), sousTitre(bas[n])];
    if (section === 's1') {
      assert.deepEqual([aJoint, aBas], [null, attendu], `image ${n} : sous-titre ${attendu} attendu en bas (plein écran)`);
    } else {
      assert.deepEqual([aJoint, aBas], [attendu, null], `image ${n} : sous-titre ${attendu} attendu à la jointure`);
    }
  }
});

// ---------------------------------------------------------------------------
// 3. Option : le 1er sous-titre d'une prise part sur la coupe ; un chunk peut imposer son mot de départ
// ---------------------------------------------------------------------------
test('sous-titres depuis la coupe (option) et mot de départ imposé ; sans eux, rien ne change', (t) => {
  if (!outils(t, { pil: true })) return;
  const dir = maison(t);
  const reel = nouveauReel(dir);
  const prises = [
    [0, 4.7, [['Désolé', 0.03], ['pour', 0.28], ['les', 0.48], ['graphistes.', 0.52]], ['désolé', 'pour les graphistes']],
    [4.7, 7.1, [['Ça', 4.76], ["s'appelle", 4.94], ['Logo', 5.64], ['Design', 5.95]], ["ça s'appelle", 'Logo Design']],
    [7.1, 9.6, [['Tu', 7.15], ['peux', 7.26], ['commenter', 7.38], ['le', 7.8], ['logo', 7.88], ['sous', 8.09], ['cette', 8.27], ['vidéo.', 8.49]],
      ['tu peux commenter', ['LOGO', 3], 'sous cette vidéo']],
  ];
  plan(reel, prises);
  const depart = (caps, texte) => premiereImage(caps.find((c) => c.texte === texte).start);
  const sans = sousTitres(reel);
  assert.equal(depart(sans.caps, 'ÇA S&#x27;APPELLE'), Math.round(4.76 * 30), 'par défaut : sur le 1er mot reconnu');
  assert.equal(depart(sans.caps, 'LOGO'), Math.round(7.8 * 30), '["LOGO", 3] : départ sur « le », le mot de rang 3');
  // Absente ou à false, l'option laisse le fichier à l'identique (octet pour octet).
  write(dir, 'brand.config.json', { ...config(), montage: { ...config().montage, sousTitresDepuisCoupe: false } });
  assert.equal(sousTitres(reel).html, sans.html);
  // Sans rang imposé, le même découpage donne le départ calculé d'avant (le mot affiché).
  write(reel, 'tools/montage_captions.py', read(reel, 'tools/montage_captions.py').replace('["LOGO",3]', '"LOGO"'));
  assert.equal(depart(sousTitres(reel).caps, 'LOGO'), Math.round(7.88 * 30));
  write(reel, 'tools/montage_captions.py', read(reel, 'tools/montage_captions.py').replace('"LOGO"', '["LOGO",3]'));
  write(dir, 'brand.config.json', { ...config(), montage: { ...config().montage, sousTitresDepuisCoupe: true } });
  const avec = sousTitres(reel);
  assert.equal(depart(avec.caps, 'DÉSOLÉ'), 0);
  assert.equal(depart(avec.caps, 'ÇA S&#x27;APPELLE'), Math.round(4.7 * 30), 'option : sur la coupe');
  assert.equal(depart(avec.caps, 'TU PEUX COMMENTER'), Math.round(7.1 * 30));
  assert.equal(depart(avec.caps, 'LOGO DESIGN'), depart(sans.caps, 'LOGO DESIGN'), 'les suivants ne bougent pas');
  assert.equal(depart(avec.caps, 'LOGO'), Math.round(7.8 * 30));
  // Un rang hors de la phrase est signalé, et le départ reste calculé.
  write(reel, 'tools/montage_captions.py', read(reel, 'tools/montage_captions.py').replace('["LOGO",3]', '["LOGO",40]'));
  assert.match(sousTitres(reel).sortie, /pas de mot de rang 40/);
});

// ---------------------------------------------------------------------------
// 4. Son hors catalogue rogné au début : préparé en fichier, il garde son attaque
// ---------------------------------------------------------------------------
// Un son de l'app (find_sound_effect) rogné à 0,35 s : 0,35 s de silence, puis l'attaque.
function sonRogne(t) {
  const dir = maison(t);
  const reel = nouveauReel(dir);
  python(reel, 'tools/build_master.py', '--write');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', "aevalsrc='if(gte(t\\,0.35)\\,0.8*sin(2*PI*1000*t)\\,0)':s=44100:d=0.9",
    '-c:a', 'libmp3lame', '-b:a', '192k', path.join(reel, 'assets', 'Verre eclats.mp3')]);
  write(reel, 'tools/build_sfx.py', read(reel, 'tools/build_sfx.py').replace('events.sort(key=lambda e: e[1])',
    'events += [("assets/Verre eclats.mp3", 1.0, -12, (0.35, 0.8)), ("assets/Verre eclats.mp3", 3.0, -12, None),\n'
    + '           ("starter/pop.mp3", 5.0, -12, (0.02, 0.2))]\nevents.sort(key=lambda e: e[1])'));
  python(reel, 'tools/build_sfx.py');
  return reel;
}
const echantillons = (fichier, debut = 0, duree = 1) => {
  const brut = execFileSync('ffmpeg', ['-v', 'error', '-ss', String(debut), '-t', String(duree), '-i', fichier,
    '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'], { maxBuffer: 1 << 26 });
  return new Float32Array(brut.buffer, brut.byteOffset, brut.length / 4);
};
const attaque = (x, seuil = 0.05) => x.findIndex((v) => Math.abs(v) > seuil) / 48000;

test('un son hors catalogue rogné au début est préparé en fichier ; catalogue et sons entiers inchangés', (t) => {
  if (!outils(t, { ffmpeg: true })) return;
  const reel = sonRogne(t);
  const master = read(reel, 'index.html');
  const rogne = /<audio id="sfx-\d+" src="(assets\/sons\/Verre eclats-rogne-[0-9a-f]{8}\.wav)" data-start="1\.000" data-duration="0\.450" data-media-start="0\.000"/.exec(master);
  assert.ok(rogne, 'son rogné hors catalogue : un fichier qui commence à la coupe');
  const x = echantillons(path.join(reel, rogne[1]));
  assert.ok(attaque(x) < 0.001, `attaque à ${attaque(x)} s du début du fichier`);
  assert.ok(Math.abs(x.length / 48000 - 0.45) < 0.01, `${x.length / 48000} s gardées`);
  // Sans rognage au début, le son reste sur place ; un son du catalogue garde la pose d'avant.
  assert.match(master, /src="assets\/Verre eclats\.mp3" data-start="3\.000" data-duration="0\.\d+" data-media-start="0\.000"/);
  assert.match(master, /src="assets\/sons\/starter-pop\.mp3" data-start="5\.000" data-duration="0\.180" data-media-start="0\.020"/);
});

test('rendu : le son hors catalogue rogné au début part à l’instant posé, attaque comprise', { skip: !process.env.MONTEUR_RENDU }, (t) => {
  if (!outils(t, { ffmpeg: true })) return;
  const reel = sonRogne(t);
  // La voix de démonstration se tait : seul le son reste à mesurer.
  write(reel, 'index.html', read(reel, 'index.html').replace(/(<audio id="vo"[^>]*data-volume=")1"/, '$10"'));
  execFileSync(cliHyperframes(), ['render', '-o', 'exports/FINAL.mp4'], { cwd: reel, stdio: 'ignore', timeout: 600000 });
  const x = echantillons(path.join(reel, 'exports/FINAL.mp4'), 0.9, 0.3);
  const crete = x.reduce((m, v) => Math.max(m, Math.abs(v)), 0);
  const debut = 0.9 + attaque(x, crete / 10);
  assert.ok(Math.abs(debut - 1.0) < 0.002, `attaque rendue à ${debut.toFixed(4)} s, posée à 1,000 s`);
  const pleine = 0.9 + attaque(x, crete / 2);
  assert.ok(pleine - debut < 0.002, `attaque adoucie : ${((pleine - debut) * 1000).toFixed(1)} ms pour atteindre la moitié de la crête`);
});

// ---------------------------------------------------------------------------
// 5. Allure des sous-titres : casse, interligne, graisse, marge, encre (réglages de visual)
// ---------------------------------------------------------------------------
const regleCap = (css) => /\n\.cap \{\n  position: absolute;[\s\S]*?\n\}/.exec(css)[0];
const skinActif = (css) => /\/\* Skin actif[^\n]*\n(\.cap \{[\s\S]*?\n\})/.exec(css)[1];

test("allure des sous-titres : absents, les réglages laissent tokens.css à l'identique ; posés, ils s'appliquent", (t) => {
  if (!outils(t, { pil: true })) return;
  const dir = maison(t);
  const reglage = (visual) => {
    write(dir, 'brand.config.json', { ...config(), visual: { ...config().visual, stylePreset: 'pulse', ...visual } });
    const r = spawnSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
    return { sortie: r.stdout + r.stderr, css: read(dir, 'brand/tokens.css') };
  };
  const avant = reglage({});
  // Le rendu d'avant, à l'octet : capitales, graisse 900, interligne 1,35, marge et encre du skin.
  assert.equal(regleCap(avant.css), '\n.cap {\n  position: absolute;\n  left: 50%;\n  transform: translate(-50%, -50%);\n'
    + '  font-family: var(--brand-font-captions);\n  font-size: var(--brand-cap-size);\n  /* Graisse maximale : règle de lisibilité en short-form (écran petit, lecture en 1 s),\n'
    + '     pas un choix d\'identité. Sans effet sur une police à graisse unique (Anton…). */\n  font-weight: 900;\n'
    + '  line-height: 1.35;\n  white-space: nowrap;\n  text-transform: uppercase;\n}');
  assert.equal(skinActif(avant.css), '.cap {\n  color: var(--brand-contrast);\n  background: var(--brand-accent);\n  padding: 8px 20px;\n}');
  assert.equal(reglage({ captionsCase: 'upper', captionsLineHeight: 1.35, captionsWeight: 900, captionsInk: 'contrast' }).css, avant.css,
    'les valeurs par défaut écrites à la main donnent le même fichier');

  const apres = reglage({ captionsCase: 'asis', captionsLineHeight: 1.18, captionsWeight: 'auto', captionsPadding: '7px  18px', captionsInk: 'bg' });
  assert.match(regleCap(apres.css), /font-weight: 400;\n  line-height: 1\.18;\n  white-space: nowrap;\n  text-transform: none;/,
    'ArchivoBlack n\'a qu\'une graisse (400) : plus de faux gras');
  assert.equal(skinActif(apres.css), '.cap {\n  color: var(--brand-bg);\n  background: var(--brand-accent);\n  padding: 7px 18px;\n}');
  assert.match(apres.css, /\.cap\.cap-skin-block \{\n  color: var\(--brand-contrast\);/, 'les skins nommés restent ceux du catalogue');
  assert.doesNotMatch(apres.sortie, /ignoré/);
  const faux = reglage({ captionsCase: 'titre', captionsWeight: 950, captionsPadding: 'large', captionsInk: 'rouge' });
  assert.equal(faux.css, avant.css, 'une valeur invalide garde le réglage par défaut');
  assert.equal(faux.sortie.match(/visual\.captions\w+ « [^»]+ » ignoré/g).length, 4, 'chaque valeur invalide est signalée');

  // Le découpage suit la casse : le texte écrit tel quel, et mesuré tel qu'il s'affiche.
  reglage({ captionsCase: 'asis' });
  const reel = nouveauReel(dir);
  plan(reel, [[0, 2.6, [['On', 0.1], ['garde', 0.3]], ['on garde']], [2.6, 5.3, [['tes', 2.7], ['mots', 2.9]], ['tes mots']],
    [5.3, 8.0, [['ça', 5.4], ['marche', 5.6]], ['ça marche']]]);
  const largeur = (s) => Number(/largeur max (\d+)px/.exec(s)[1]);
  const telQuel = sousTitres(reel);
  assert.deepEqual(telQuel.caps.map((c) => c.texte), ['on garde', 'tes mots', 'ça marche']);
  reglage({});
  const capitales = sousTitres(reel);
  assert.deepEqual(capitales.caps.map((c) => c.texte), ['ON GARDE', 'TES MOTS', 'ÇA MARCHE']);
  assert.ok(largeur(capitales.sortie) > largeur(telQuel.sortie), 'la largeur mesurée suit la casse affichée');
});

// ---------------------------------------------------------------------------
// 7. Cadrage : la zone du rush suit le transform CSS du master, translations seules comprises
// ---------------------------------------------------------------------------
const crop = (...cas) => JSON.parse(python(path.join(root, 'tools'), '-c',
  'import json, sys; from cadrage import crop_from_transform as c; '
  + 'print(json.dumps([c(t, int(top), o or None) for t, top, o in json.loads(sys.argv[1])]))', JSON.stringify(cas)));

test('cadrage : translateX, translateY, translate et scale lus dans leur ordre, autour de l’origine du master', (t) => {
  if (!outils(t)) return;
  assert.deepEqual(crop(
    ['translate(-216px, 410px) scale(1.40)', 920, '0 0'],   // défaut livré : inchangé
    ['scale(1.4)', 0, 'center 34%'],                        // plein écran par défaut : inchangé
    ['translate(-164px, 461px) scale(1.22)', 920, '0 0'],   // cadrage de logo-designer (VH)
    // Un translateY seul était ignoré : la tête remontée au studio redescendait de 14 px à l'export.
    // Attendu = le crop calibré à la main sur l'installation de la recette (projet 0).
    ['translateY(-25px) scale(1.75)', 0, 'center 35%'],
  ), ['771:714:154:364', '771:1371:154:187', '885:820:134:376', '617:1097:231:302']);
  const [a, b, c, d] = crop(['translateX(-20px) translateY(30px) scale(1.5)', 0, 'center 34%'],
    ['translate(-20px, 30px) scale(1.5)', 0, 'center 34%'], ['translate(-20px,30px) scale(1.5, 1.5)', 0, 'center 34%'],
    ['translate(-20px) translateY(30px) scale(1.5)', 0, 'center 34%']);
  assert.deepEqual([b, c, d], [a, a, a], 'les quatre écritures donnent la même zone');
  assert.notEqual(a, crop(['scale(1.5)', 0, 'center 34%'])[0], 'la translation compte, origine comprise');
  // L'ordre compte : « scale(2) translate(10px, 20px) » = « translate(20px, 40px) scale(2) ».
  assert.deepEqual(crop(['scale(2) translate(10px, 20px)', 920, '0 0'], ['translate(20px, 40px) scale(2)', 920, '0 0']),
    ['540:500:0:440', '540:500:0:440']);
  // En split, l'origine est celle du master (0 0), même sans translation.
  assert.deepEqual(JSON.parse(python(path.join(root, 'tools'), '-c',
    'import json; from cadrage import crops; print(json.dumps(crops({"splitTransform": "scale(1.4)"})))')),
  ['771:714:0:657', '771:1371:154:187']);
});

// ---------------------------------------------------------------------------
// 6. Réglages propres à un Reel (reel.config.json) : cadrage du visage et taille des sous-titres
// ---------------------------------------------------------------------------
test('reel.config.json cadre ce Reel et lui donne son propre style sans toucher aux autres ; rien sans le fichier', async (t) => {
  if (!outils(t, { pil: true, ffmpeg: true })) return;
  const dir = maison(t);
  // La maison : un cadrage calibré, crop compris (installation de la recette).
  write(dir, 'brand.config.json', { ...config(), montage: { ...config().montage,
    splitTransform: 'translate(-216px, 375px) scale(1.40)', faceCrop: '771:714:154:389' } });
  const proche = nouveauReel(dir, 'Proche');
  const autre = nouveauReel(dir, 'Autre');
  const avant = { tokens: read(autre, 'brand/tokens.css'), master: (python(autre, 'tools/build_master.py', '--write'), read(autre, 'index.html')) };
  // Tourné plus près de la caméra : cadrage et sous-titres de CE Reel. Un transform sans crop fait
  // recalculer le crop (celui de la maison suit un autre cadrage).
  write(proche, 'reel.config.json', { montage: { splitTransform: 'translate(-164px, 461px) scale(1.22)' },
    visual: { captionsSize: 46, captionsSkin: 'outline', accent: '#ff2e7e', fontCaptions: 'Anton', bg: 'pas une couleur' },
    audio: { musicFile: 'ignore.mp3' } });
  const lu = (reel, code) => JSON.parse(python(reel, '-c', `import json, sys; sys.path.insert(0, "tools"); ${code}`));
  assert.deepEqual(lu(proche, 'from cadrage import crops; from lieux import config; print(json.dumps(crops(config()["montage"])))'),
    ['885:820:134:376', '771:1371:154:187']);
  assert.deepEqual(lu(autre, 'from cadrage import crops; from lieux import config; print(json.dumps(crops(config()["montage"])))'),
    ['771:714:154:389', '771:1371:154:187']);
  const style = 'import brand_style; s = brand_style.style(); print(json.dumps([s.captions_size, s.captions_skin, s.accent, s.font_captions, s.bg]))';
  const maisonStyle = lu(autre, style);
  // Le style de CE Reel : taille, apparence, couleur et police des sous-titres ; une valeur invalide
  // (le fond) est ignorée, comme par la synchro. L'audio n'est jamais lu ici.
  assert.deepEqual(lu(proche, style), [46, 'outline', '#ff2e7e', 'Anton', maisonStyle[4]]);
  assert.deepEqual(maisonStyle.slice(0, 2), [50, 'block']);
  assert.match(python(proche, 'tools/build_faces.py'), /zone 885:820:134:376 du rush/);
  python(proche, 'tools/build_master.py', '--write');
  fs.rmSync(path.join(proche, 'assets/video/visage-split.mp4'));
  python(proche, 'tools/build_master.py', '--write');
  assert.match(read(proche, 'index.html'), /transform: translate\(-164px, 461px\) scale\(1\.22\)/, 'aperçu sans visages pré-cadrés');

  // La synchro donne au Reel son style (sous-titres de 46 px en contour, accent rose, Anton déclarée
  // pour toute la maison), signale le fond invalide, garde le fichier, et n'écrit plus rien ensuite.
  const sortie = spawnSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  assert.match(sortie.stderr, /visual\.bg « pas une couleur » ignoré/);
  const tokens = read(proche, 'brand/tokens.css');
  for (const attendu of [/--brand-cap-size: 46px;/, /--brand-accent: #ff2e7e;/, /skin CHOISI \(outline\)/, /Anton/]) assert.match(tokens, attendu);
  assert.match(read(dir, 'brand/fonts.css'), /font-family: "Anton"/);
  assert.match(read(proche, 'brand/fonts.css'), /font-family: "Anton"/);
  // Ses instructions annoncent son style à lui ; celles des autres Reels, le style de base.
  assert.match(read(proche, 'CLAUDE.md'), /Style visuel actif : propre à ce Reel[^\n]*accent `#ff2e7e`/);
  assert.doesNotMatch(read(autre, 'CLAUDE.md'), /propre à ce Reel/);
  assert.equal(read(autre, 'brand/tokens.css'), avant.tokens, 'les autres Reels gardent le style de la maison');
  python(autre, 'tools/build_master.py', '--write');
  assert.equal(read(autre, 'index.html'), avant.master);
  const date = fs.statSync(path.join(proche, 'brand/tokens.css')).mtimeMs;
  sync(dir);
  assert.equal(fs.statSync(path.join(proche, 'brand/tokens.css')).mtimeMs, date);
  assert.ok(fs.existsSync(path.join(proche, 'reel.config.json')));
  // Sans le fichier, le Reel revient au style de la maison.
  fs.rmSync(path.join(proche, 'reel.config.json'));
  sync(dir);
  assert.equal(read(proche, 'brand/tokens.css'), read(dir, 'brand/tokens.css'));
  write(proche, 'reel.config.json', { visual: { captionsSize: 46 } });

  // La mise à jour ne touche jamais un Reel ; une variante (--depuis) garde ses réglages.
  const { planifier } = await import('./mettre-a-jour.mjs');
  const plan = planifier(dir, { archive: path.join(os.tmpdir(), 'monteur-archive-vide') });
  assert.deepEqual([...plan.moteur.map((m) => m.rel), ...plan.obsoletes].filter((rel) => rel.startsWith('reels/')), []);
  python(dir, 'tools/nouveau_reel.py', 'Variante', '--date', '2026-10-15', '--depuis', proche);
  assert.deepEqual(JSON.parse(read(path.join(dir, 'reels', `Variante · 2026-10-15 · ${path.basename(dir)}`), 'reel.config.json')),
    { visual: { captionsSize: 46 } });
  // Suivi par git avec le montage du Reel (le .gitignore livré ne l'écarte pas).
  git(dir, 'init', '-q');
  const ignore = (rel) => spawnSync('git', ['check-ignore', '-q', '--no-index', rel], { cwd: dir }).status;
  assert.deepEqual([ignore('reels/Proche · 2026-10-15/reel.config.json'), ignore('reels/Proche · 2026-10-15/exports/FINAL.mp4')], [1, 0]);
});

// ---------------------------------------------------------------------------
// 5. Cartes sur le décor : la vidéo filmée reste plein cadre, les cartes se posent dessus
// ---------------------------------------------------------------------------
// Le format des Reels « cartes au-dessus de la tête » (style cloné ou style du catalogue) : jamais un
// écran partagé sur un fond uni. Un Reel sans section « decor » garde exactement son montage d'avant.
test('cadrage décor : la vidéo filmée passe sous les cartes, cadrée par reel.config.json ; sans décor, rien ne change', (t) => {
  if (!outils(t, { pil: true, ffmpeg: true })) return;
  const dir = maison(t);
  const reel = nouveauReel(dir, 'Decor');
  plan(reel, PRISES_HORS_IMAGES, { layout: LAYOUT_SPLIT_FULL_SPLIT });
  python(reel, 'tools/build_master.py', '--write');
  const avant = read(reel, 'index.html');
  assert.doesNotMatch(avant, /<video id="decor/, 'sans section décor, aucun calque décor');

  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py')
    .replace(LAYOUT_SPLIT_FULL_SPLIT, '    ("s0", "split", [0]),\n    ("s1", "decor", [1, 2]),'));
  // Visage trop haut pour laisser la place aux cartes : la vidéo agrandie depuis le haut le fait descendre.
  // Le skin « ombre douce » et le texte secondaire (`muted`) sont des réglages valides d'un Reel.
  write(reel, 'reel.config.json', { montage: { decorTransform: 'scale(1.5)' },
    visual: { captionsSkin: 'soft', muted: '#555555' } });
  const lu = (code) => JSON.parse(python(reel, '-c', `import json, sys; sys.path.insert(0, "tools"); ${code}`));
  assert.equal(lu('from cadrage import crop_decor; from lieux import config; print(json.dumps(crop_decor(config()["montage"])))'),
    '720:1280:180:0', 'scale(1.5) autour de « center top » : le haut du cadre, agrandi');
  assert.deepEqual(lu('import brand_style; s = brand_style.style(); print(json.dumps([s.captions_skin, s.muted]))'), ['soft', '#555555']);

  assert.match(python(reel, 'tools/build_faces.py'), /visage-decor\.mp4 : zone 720:1280:180:0 du rush, sous les cartes/);
  assert.equal(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
    '-of', 'csv=p=0', path.join(reel, 'assets/video/visage-decor.mp4')], { encoding: 'utf8' }).trim(), '1080,1920');
  python(reel, 'tools/build_master.py', '--write');
  const master = read(reel, 'index.html');
  // La vidéo filmée AVANT les sections (les cartes se peignent dessus), sur la fenêtre de la section,
  // posée sans agrandissement ; la section est plein cadre, sur sa propre piste.
  assert.ok(master.indexOf('<div class="face-decor">') < master.indexOf('===== SECTIONS ====='));
  assert.match(master, /<video id="decor0" src="assets\/video\/visage-decor\.mp4"[^>]*data-start="2\.6\d+"/);
  assert.match(master, /\.face-decor video \{[^}]*transform: none;/);
  assert.match(master, /id="section-s1"[^>]*data-track-index="4" data-width="1080" data-height="1920"/);
  fs.rmSync(path.join(reel, 'assets/video/visage-decor.mp4'));
  python(reel, 'tools/build_master.py', '--write');
  assert.match(read(reel, 'index.html'), /\.face-decor video \{[^}]*transform: scale\(1\.5\); transform-origin: center top;/,
    'aperçu sans vidéo pré-cadrée : le cadrage du Reel');

  // Les sous-titres de la section décor passent juste sous les cartes.
  const { caps } = sousTitres(reel);
  assert.deepEqual([...new Set(caps.map((c) => c.y))], [920, 760]);

  // La synchro accepte ces réglages sans rien signaler et donne au Reel son skin.
  const sortie = spawnSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
  assert.doesNotMatch(sortie.stderr, /reel\.config\.json/);
  const tokens = read(reel, 'brand/tokens.css');
  assert.match(tokens, /skin CHOISI \(soft\)/);
  assert.match(tokens, /--brand-muted: #555555;/);
  assert.match(read(dir, 'brand/tokens.css'), /\.cap\.cap-skin-soft \{/, 'le skin reste disponible partout');
});

test('sous-titres mot à mot (--mots) : la voix telle que transcrite, ponctuation comprise ; sans l’option, le découpage écrit', (t) => {
  if (!outils(t, { pil: true })) return;
  const reel = nouveauReel(maison(t));
  plan(reel, PRISES_HORS_IMAGES);
  const ecrit = sousTitres(reel).caps;
  assert.equal(ecrit.length, 7, 'le découpage MANUAL');
  const { caps } = sousTitres(reel, '--mots', '1');
  assert.equal(caps.length, 16, 'un sous-titre par mot dit');
  assert.deepEqual(caps.slice(0, 4).map((c) => c.texte), ['DÉSOLÉ', 'POUR', 'LES', 'GRAPHISTES,']);
  assert.equal(image(caps[1].start), image(0.28), 'chaque mot part sur sa voix');
  assert.equal(sousTitres(reel, '--mots', '2').caps.length, 8, '6, 6 et 4 mots : 3 + 3 + 2');
  // Un signe que Whisper rend seul suit son mot ; --sans laisse une section sans sous-titres.
  const mots = JSON.parse(read(reel, 'derush/exemple_words.json'));
  mots.splice(6, 0, { w: '?', start: 1.3, end: 1.35, take: 0 });
  write(reel, 'derush/exemple_words.json', mots);
  assert.deepEqual(sousTitres(reel, '--mots', '1').caps.slice(4, 6).map((c) => c.texte), ['MAIS', 'CLAUDE ?']);
  mots.splice(7, 0, { w: '?', start: 2.69, end: 2.7, take: 1 });   // fin de la phrase d'avant, rendue au début de la suivante
  write(reel, 'derush/exemple_words.json', mots);
  assert.equal(sousTitres(reel, '--mots', '1').caps[6].texte, 'QUELQU’UN', 'jamais « ?QUELQU’UN »');
  // Un mot horodaté un peu avant sa coupe (Whisper en avance) reste dans sa phrase, grâce à sa prise.
  const avance = JSON.parse(read(reel, 'derush/exemple_words.json'));
  avance.find((w) => w.w === 'Quelqu’un').start = 2.6;
  write(reel, 'derush/exemple_words.json', avance);
  assert.ok(sousTitres(reel, '--mots', '1').caps.some((c) => c.texte === 'QUELQU’UN'), 'le premier mot de la phrase n’est pas perdu');
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py')
    .replace('    ("exemple-section", "split", [0, 1, 2]),', '    ("s0-hook", "split", [0]),\n    ("s1", "split", [1, 2]),'));
  const sans = sousTitres(reel, '--mots', '1', '--sans', 's0-hook').caps;
  assert.equal(sans.length, 10, 'les 6 mots de l’accroche sans sous-titre');
  assert.ok(sans.every((c) => c.start >= 2.6));
  // Une section --sans au milieu : aucun mot de la section d'avant n'y déborde.
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py')
    .replace('    ("s0-hook", "split", [0]),\n    ("s1", "split", [1, 2]),', '    ("s0", "split", [0]),\n    ("s1-carte", "split", [1]),\n    ("s2", "split", [2]),'));
  const milieu = sousTitres(reel, '--mots', '1', '--sans', 's1-carte').caps;
  assert.ok(milieu.every((c) => c.start + c.dur <= 2.67 + 1e-3 || c.start >= 5.33), 'rien d’affiché sur la carte');
  const refus = spawnSync('python3', ['tools/montage_captions.py', '--mots', '4'], { cwd: reel, encoding: 'utf8' });
  assert.notEqual(refus.status, 0);
  assert.match(refus.stderr, /--mots attend 1, 2 ou 3/);
  // Des raccords posés après la transcription renumérotent les prises : un fichier de mots plus ancien
  // que les coupes n'est plus rangé par ses numéros de prise, mais par le temps (et c'est signalé).
  const perimes = JSON.parse(read(reel, 'derush/exemple_words.json')).map((w) => ({ ...w, take: 0 }));
  write(reel, 'derush/exemple_words.json', perimes);
  const coupes = path.join(reel, 'derush/exemple_cuts.json');
  const plusTard = new Date(Date.now() + 60_000);
  fs.utimesSync(coupes, plusTard, plusTard);
  const parTemps = spawnSync('python3', ['tools/montage_captions.py', '--mots', '1'], { cwd: reel, encoding: 'utf8' });
  assert.match(parTemps.stdout, /plus ancien que les coupes/);
  assert.ok(sousTitres(reel, '--mots', '1').caps.some((c) => c.texte === 'QUELQU’UN' && c.start >= 2.6),
    'chaque mot reste dans sa phrase malgré des numéros de prise périmés');
  const avantDerush = new Date(Date.now() - 60_000);
  fs.utimesSync(coupes, avantDerush, avantDerush);
  write(reel, 'derush/exemple_words.json', avance);
  // Un nombre reste avec son voisin : après un nom il s'y accroche (« GPT 6 »), sinon il part avec
  // le mot qui suit (« 72 GRAPHISTES ») ; jamais « GPT » puis « 6 ».
  const nombres = (avant, chiffre) => {
    const mots = JSON.parse(read(reel, 'derush/exemple_words.json'));
    mots.find((w) => w.w === 'pour').w = avant;
    mots.find((w) => w.w === 'les').w = chiffre;
    write(reel, 'derush/exemple_words.json', mots);
    return sousTitres(reel, '--mots', '1').caps.map((c) => c.texte);
  };
  assert.ok(nombres('GPT', '6').includes('GPT 6'));
  write(reel, 'derush/exemple_words.json', avance);
  assert.ok(nombres('il', '72').includes('72 GRAPHISTES,'));
});

// ---------------------------------------------------------------------------
// 6. Reel Cloneur : le rythme qu'on voit (cartes comprises) et le contrôle côte à côte
// ---------------------------------------------------------------------------
// Une vidéo dont la carte du haut change à 1,5 s et 3 s sans coupe (le visage, en bas, ne bouge pas),
// puis une vraie coupe à 4,5 s. L'ancien relevé ne voyait que la coupe : c'est le cas du Reel
// « 10/10 Claude Skills » (8 coupes trouvées pour 16 changements d'image, essai du 21/10/2026).
test('Reel Cloneur : un changement de carte sans coupe compte dans le rythme ; côte à côte, original et montage', (t) => {
  if (!outils(t, { ffmpeg: true })) return;
  const dir = maison(t);
  const clone = path.join(dir, 'clones', 'essai');
  fs.mkdirSync(clone, { recursive: true });
  const carte = (x, quand) => `drawbox=x=${x}:y=70:w=120:h=60:color=0x202020@1:t=fill:enable='${quand}'`;
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=0x606060:s=360x640:r=30:d=6', '-vf',
    ['drawbox=x=20:y=40:w=320:h=150:color=0xf0e8dc@1:t=fill', carte(40, 'lt(t,1.5)'), carte(200, 'between(t,1.5,3)'),
      carte(120, 'gte(t,3)'), "drawbox=x=0:y=0:w=360:h=640:color=0x1060c0@1:t=fill:enable='gte(t,4.5)'"].join(','),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', path.join(clone, 'media.mp4')]);
  const [changements, coupes] = JSON.parse(python(path.join(dir, 'tools'), '-c', [
    'import json, pathlib, sys', 'sys.argv = ["x"]', 'import cloner_reel as c',
    `v = pathlib.Path(${JSON.stringify(path.join(clone, 'media.mp4'))})`,
    'print(json.dumps([c.detecter_changements("ffmpeg", v, 6.0)[0], c.detecter_coupes("ffmpeg", v, 6.0)[0]]))'].join('\n')));
  assert.deepEqual(changements.map((x) => Math.round(x * 10) / 10), [1.5, 3, 4.5]);
  assert.ok(coupes.length < changements.length, 'les coupes franches seules ratent les cartes');

  const sortie = python(dir, 'tools/cloner_reel.py', 'cote-a-cote', clone, path.join(clone, 'media.mp4'), '1.0', '2.0:5.0');
  assert.match(sortie, /2 paires \(original à gauche, montage à droite\)/);
  const paire = path.join(clone, 'kit/apercu/paire-002.00-005.00.jpg');
  assert.equal(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', paire],
    { encoding: 'utf8' }).trim(), '1080,960');
});

// ---------------------------------------------------------------------------
// 7. Personne détourée devant les visuels (styles « Incrustation », « Autocollant »)
// ---------------------------------------------------------------------------
// Le vrai détourage (hyperframes remove-background, modèle de 170 Mo) est remplacé ici par un faux qui
// rend une vidéo transparente de même taille : on vérifie la place des couches, pas le modèle.
test('cadrage détouré : la personne passe devant la section, détourée une fois ; l’ancien export refuse', (t) => {
  if (!outils(t, { pil: true, ffmpeg: true })) return;
  const dir = maison(t);
  const reel = nouveauReel(dir, 'Detoure');
  plan(reel, PRISES_HORS_IMAGES, { layout: '    ("s0", "split", [0]),\n    ("s1", "detoure", [1, 2]),' });
  const faux = path.join(dir, 'faux-hyperframes.sh');
  write(dir, 'faux-hyperframes.sh', '#!/bin/sh\n# remove-background <entree> -o <sortie> ...\n'
    + 'ffmpeg -v error -y -i "$2" -c:v libvpx-vp9 -deadline realtime -cpu-used 8 -pix_fmt yuva420p -an "$4"\n');
  const env = { ...process.env, MONTEUR_HYPERFRAMES: `sh ${faux}` };
  const faces = () => execFileSync('python3', ['tools/build_faces.py'], { cwd: reel, encoding: 'utf8', env });
  // Seul le passage montré est détouré (2,67 s à 8 s), pas toute la vidéo.
  assert.match(faces(), /visage-detoure-0\.webm : 2\.67 s, 5\.33 s, zone 1080:1920:0:0 du rush, personne détourée/);
  assert.match(faces(), /déjà détourée \(1 passage\(s\), même zone, même dérush\)/, 'pas le calcul à chaque fois');
  const duree = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
    path.join(reel, 'assets/video/visage-detoure-0.webm')], { encoding: 'utf8' }));
  assert.ok(Math.abs(duree - 5.33) < 0.1, `le passage seul : ${duree} s`);
  assert.ok(!fs.existsSync(path.join(reel, 'work/visage-detoure-source.mp4')), 'le fichier de travail part');

  python(reel, 'tools/build_master.py', '--write');
  const master = read(reel, 'index.html');
  const ordre = ['<div class="face-decor">', '===== SECTIONS =====', '<div class="face-detoure">', '<div class="face-full">']
    .map((m) => master.indexOf(m));
  assert.deepEqual([...ordre].sort((a, b) => a - b), ordre, 'la personne passe après les sections, avant le visage plein écran');
  assert.match(master, /<video id="detoure0" src="assets\/video\/visage-detoure-0\.webm"[^>]*data-start="2\.6\d+" data-media-start="0"/);
  // Rapetissée et déplacée sans perte de netteté : la place se règle dans reel.config.json.
  write(reel, 'reel.config.json', { montage: { detourePlace: 'translate(220px, 300px) scale(0.6)' } });
  python(reel, 'tools/build_master.py', '--write');
  assert.match(read(reel, 'index.html'), /\.face-detoure \{[^}]*transform: translate\(220px, 300px\) scale\(0\.6\)/);
  assert.match(master, /id="section-s1"[^>]*data-track-index="5" data-width="1080" data-height="1920"/);
  assert.deepEqual([...new Set(sousTitres(reel).caps.map((c) => c.y))], [920, 1250]);

  // Options du passage : la personne monte du bas, puis la vidéo filmée revient en fondu (style 9).
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py')
    .replace('("s1", "detoure", [1, 2]),', '("s1", "detoure", [1, 2], {"entree": "monte", "visageRevient": 2}),'));
  assert.match(faces(), /visage-plein\.mp4 : zone [\d:]+ du rush, visage plein écran/, 'le visage qui revient est préparé');
  python(reel, 'tools/build_master.py', '--write');
  const anime = read(reel, 'index.html');
  assert.match(anime, /fromTo\("#detoure0", \{ y: 1920, filter: "blur\(18px\)" \}, \{ y: 0, filter: "blur\(0px\)", duration: 0\.4, ease: "power2\.out" \}, 2\.6\d+\);/);
  assert.match(anime, /<video id="faceretour0" src="assets\/video\/visage-plein\.mp4"[^>]*data-start="4\.6\d+" data-media-start="4\.6\d+" data-duration="3\.3\d+"/);
  assert.match(anime, /fromTo\("#faceretour0", \{ opacity: 0 \}, \{ opacity: 1, duration: 0\.4, ease: "none" \}, 4\.6\d+\);/);
  assert.ok(anime.indexOf('id="faceretour0"') > anime.indexOf('<div class="face-full">'), 'le visage revient par-dessus la personne');
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('"visageRevient": 2', '"visageRevient": 9'));
  assert.match(spawnSync('python3', ['tools/build_master.py'], { cwd: reel, encoding: 'utf8' }).stderr, /visageRevient \(9\.0 s\) après la fin/);

  const ancien = spawnSync('python3', ['tools/build_final.py'], { cwd: reel, encoding: 'utf8' });
  assert.notEqual(ancien.status, 0);
  assert.match(ancien.stderr, /ne sait pas poser une personne detouree/);
});

test('zoom par section : une vidéo nette par niveau de zoom, la section serrée sur sa fenêtre ; sans zoom, rien ne change', (t) => {
  if (!outils(t, { pil: true, ffmpeg: true })) return;
  const reel = nouveauReel(maison(t), 'Zoom');
  plan(reel, PRISES_HORS_IMAGES, { layout: '    ("s0", "face", [0]),\n    ("s1", "decor", [1]),\n    ("s2", "decor", [2]),' });
  const sansZoom = (python(reel, 'tools/build_faces.py'), python(reel, 'tools/build_master.py', '--write'), read(reel, 'index.html'));
  assert.doesNotMatch(sansZoom, /-zoom-/);
  assert.match(sansZoom, /<video id="decor0" src="assets\/video\/visage-decor\.mp4"/);
  assert.doesNotMatch(sansZoom, /id="decor1"/, 'deux sections décor contiguës sans zoom : une seule fenêtre');

  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py')
    .replace('("s2", "decor", [2]),', '("s2", "decor", [2], {"zoom": 1.25}),')
    .replace('("s0", "face", [0]),', '("s0", "face", [0], {"zoom": 1.2, "zoomOrigin": "center 40%"}),'));
  const lu = (code) => JSON.parse(python(reel, '-c', `import json, sys; sys.path.insert(0, "tools"); ${code}`));
  // Les yeux (30 % du haut) restent à leur place : la zone se resserre autour d'eux.
  assert.deepEqual(lu('from cadrage import zoom_crop; print(json.dumps(zoom_crop(None, 1.25)))'), ['864:1536:108:115', false]);
  assert.deepEqual(lu('from cadrage import zoom_crop; print(json.dumps(zoom_crop(None, 0.8)))'), ['1080:1920:0:0', true],
    'jamais plus que la vidéo filmée');
  const sortie = python(reel, 'tools/build_faces.py');
  assert.match(sortie, /visage-decor-zoom-0\.mp4 : zoom 1\.25 autour de « center 30% », zone 864:1536:108:115/);
  assert.match(sortie, /visage-plein-zoom-0\.mp4 : zoom 1\.2 autour de « center 40% »/);
  assert.equal(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
    '-of', 'csv=p=0', path.join(reel, 'assets/video/visage-decor-zoom-0.mp4')], { encoding: 'utf8' }).trim(), '1080,1920');

  python(reel, 'tools/build_master.py', '--write');
  const master = read(reel, 'index.html');
  // La section zoomée a sa propre fenêtre, posée sans agrandissement ; celle d'avant garde le cadrage du Reel.
  assert.match(master, /<video id="decor0" src="assets\/video\/visage-decor\.mp4"[^>]*data-start="2\.6\d+"[^>]*data-duration="2\.6\d+"/);
  assert.match(master, /<video id="decor1" src="assets\/video\/visage-decor-zoom-0\.mp4"[^>]*data-start="5\.3\d+" data-media-start="5\.3\d+"/);
  assert.match(master, /<video id="facefull0" src="assets\/video\/visage-plein-zoom-0\.mp4"/);
  assert.match(master, /\.face-decor video \{[^}]*transform: none;/);

  // Le contrôle final compare chaque section à la vidéo qu'elle montre : une section resserrée à sa
  // vidéo resserrée (comparée à celle du Reel, elle passait pour un visage absent et rien n'était livré).
  const bornes = JSON.parse(python(reel, '-c', 'import json, sys; sys.path.insert(0, "tools"); import sections; '
    + 'print(json.dumps([[s["start"], s["end"]] for s in sections.sections()]))'));
  const exporte = (sources) => {
    const morceaux = sources.map((src, i) => `[${i}:v]trim=${bornes[i][0]}:${bornes[i][1]},setpts=PTS-STARTPTS,fps=30[v${i}]`);
    execFileSync('ffmpeg', ['-y', '-v', 'error', ...sources.flatMap((src) => ['-i', path.join(reel, 'assets/video', src)]),
      '-i', path.join(reel, 'assets/video/base.mp4'), '-filter_complex',
      `${morceaux.join(';')};${sources.map((_, i) => `[v${i}]`).join('')}concat=n=${sources.length}:v=1:a=0[v]`,
      '-map', '[v]', '-map', `${sources.length}:a:0`, '-shortest', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
      path.join(reel, 'exports/FINAL.mp4')]);
    return spawnSync('python3', ['tools/check_export.py', 'exports/FINAL.mp4'], { cwd: reel, encoding: 'utf8' });
  };
  fs.mkdirSync(path.join(reel, 'exports'), { recursive: true });
  const bon = exporte(['visage-plein-zoom-0.mp4', 'visage-decor.mp4', 'visage-decor-zoom-0.mp4']);
  assert.match(bon.stdout, /s2 +ressemblance 0\.9\d+ +OK/, bon.stdout);
  assert.match(bon.stdout, /s0 +ressemblance 0\.9\d+ +OK/);
  const faux = exporte(['visage-plein-zoom-0.mp4', 'visage-decor.mp4', 'visage-decor.mp4']);
  assert.match(faux.stdout, /s2 +ressemblance [\d.]+ +!! KO/, 'une section qui aurait dû être resserrée est signalée');

  // Zoom progressif : la vidéo de la section part resserrée et s'élargit en 0,8 s (timeline du master),
  // sur la vidéo du Reel, sans nouvelle copie.
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('("s1", "decor", [1]),', '("s1", "decor", [1], {"zoom": [1.25, 1]}),'));
  python(reel, 'tools/build_master.py', '--write');
  assert.match(read(reel, 'index.html'),
    /fromTo\("#decor0", \{ scale: 1\.25, transformOrigin: "center 30%" \}, \{ scale: 1, duration: 0\.8, ease: "power2\.out" \}, 2\.6\d+\);/);
  assert.match(read(reel, 'index.html'), /<video id="decor0" src="assets\/video\/visage-decor\.mp4"/);
  assert.match(read(reel, 'index.html'), /<video id="decor1" src="assets\/video\/visage-decor-zoom-0\.mp4"/);
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('{"zoom": [1.25, 1]}', '{"zoom": [2, 1]}'));
  assert.match(spawnSync('python3', ['tools/build_master.py'], { cwd: reel, encoding: 'utf8' }).stderr, /1,3 fois d'écart au plus/);
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('("s1", "decor", [1], {"zoom": [2, 1]}),', '("s1", "decor", [1]),'));

  // Zoom retiré : sa vidéo part au prochain passage.
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('("s2", "decor", [2], {"zoom": 1.25})', '("s2", "decor", [2])'));
  python(reel, 'tools/build_faces.py');
  assert.ok(!fs.existsSync(path.join(reel, 'assets/video/visage-decor-zoom-0.mp4')));

  const ancien = spawnSync('python3', ['tools/build_final.py'], { cwd: reel, encoding: 'utf8' });
  assert.notEqual(ancien.status, 0);
  assert.match(ancien.stderr, /ne sait pas zoomer une section/);
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('{"zoom": 1.2, "zoomOrigin": "center 40%"}', '{"zoom": "fort"}'));
  const invalide = spawnSync('python3', ['tools/build_master.py'], { cwd: reel, encoding: 'utf8' });
  assert.match(invalide.stderr, /section s0 : zoom 'fort' invalide/);

  // En écran partagé, le zoom est sec : le visage resserré garde sa place sous la jointure.
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('("s0", "face", [0], {"zoom": "fort"})', '("s0", "split", [0], {"zoom": 1.15})'));
  assert.match(python(reel, 'tools/build_faces.py'), /visage-split-zoom-0\.mp4 : zoom 1\.15/);
  python(reel, 'tools/build_master.py', '--write');
  assert.match(read(reel, 'index.html'), /<video id="faceA" src="assets\/video\/visage-split-zoom-0\.mp4"/);
  assert.ok(!fs.existsSync(path.join(reel, 'assets/video/visage-plein-zoom-0.mp4')), 'plus de section face zoomée');
  write(reel, 'tools/sections.py', read(reel, 'tools/sections.py').replace('{"zoom": 1.15}', '{"zoom": [1.15, 1]}'));
  assert.match(spawnSync('python3', ['tools/build_master.py'], { cwd: reel, encoding: 'utf8' }).stderr, /zoom progressif en écran partagé impossible/);
});

// ---------------------------------------------------------------------------
// 8. Le catalogue de styles (skill reel-cloneur, styles/) : chaque kit tient debout tout seul
// ---------------------------------------------------------------------------
test('catalogue de styles : chaque kit a sa fiche, ses pièces, des réglages acceptés et des polices livrées', (t) => {
  const dossier = path.join(root, '.claude/skills/reel-cloneur/styles');
  const kits = fs.readdirSync(dossier).filter((d) => /^\d\d-/.test(d)).sort();
  assert.ok(kits.length >= 11, `${kits.length} kits`);
  const index = read(dossier, 'README.md');
  const polices = JSON.parse(read(root, 'templates/style-presets.json')).fonts;
  const connues = new Set([...Object.keys(config().visual), 'muted']);
  for (const kit of kits) {
    const n = Number(kit.slice(0, 2));
    assert.match(read(path.join(dossier, kit), 'style.md'), new RegExp(`Style n°${kit.slice(0, 2)} · `), `${kit} : en-tête de la fiche`);
    assert.match(index, new RegExp(`^\\| ${n} \\| `, 'm'), `${kit} : dans l'index`);
    const visual = JSON.parse(read(path.join(dossier, kit), 'reel.config.json')).visual;
    for (const [cle, val] of Object.entries(visual)) {
      assert.ok(connues.has(cle), `${kit} : réglage inconnu ${cle}`);
      if (/^font/.test(cle)) assert.ok(polices[val]?.faces, `${kit} : police ${val} absente de la table`);
    }
    for (const face of Object.entries(polices).filter(([nom]) => Object.values(visual).includes(nom)).flatMap(([, p]) => p.faces)) {
      assert.ok(fs.existsSync(path.join(root, 'assets/fonts', face.file)), `${kit} : ${face.file} livrée`);
    }
    const pieces = fs.readdirSync(path.join(dossier, kit, 'compositions')).filter((f) => f.endsWith('.html'));
    assert.ok(pieces.length >= 2, `${kit} : pièces`);
    for (const piece of pieces) {
      const html = read(path.join(dossier, kit, 'compositions'), piece);
      assert.doesNotMatch(html, /@font-face|url\([^)]*(assets\/fonts|polices)\//, `${kit}/${piece} : les polices viennent de brand/fonts.css`);
    }
  }
  if (!outils(t)) return;
  // La synchro accepte les réglages de chaque kit sans en écarter aucun.
  const dir = maison(t);
  const reel = nouveauReel(dir, 'Catalogue');
  for (const kit of kits) {
    fs.copyFileSync(path.join(dossier, kit, 'reel.config.json'), path.join(reel, 'reel.config.json'));
    const sortie = spawnSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' });
    assert.doesNotMatch(sortie.stderr + sortie.stdout, /ignoré|absente de la table|manquant/, `${kit} : réglages refusés`);
  }
});

// ---------------------------------------------------------------------------
// 9. Styles de sous-titres (templates/styles-sous-titres.json, tools/sous_titres.py)
// ---------------------------------------------------------------------------
const catalogueSousTitres = () => JSON.parse(read(root, 'templates/styles-sous-titres.json')).styles;

test('styles de sous-titres : catalogue numéroté, indexé pour l’IA, réglages acceptés et polices livrées', () => {
  const styles = catalogueSousTitres();
  assert.deepEqual(styles.map((s) => s.n), styles.map((_, i) => i + 1), 'numéros 1, 2, 3… sans trou');
  assert.equal(new Set(styles.map((s) => s.slug)).size, styles.length, 'slugs uniques');
  const index = read(root, '.claude/skills/motion-design/references/styles-sous-titres.md');
  const polices = JSON.parse(read(root, 'templates/style-presets.json')).fonts;
  const connues = new Set(Object.keys(config().visual));
  for (const s of styles) {
    assert.ok(index.includes(`| ${s.n} | ${s.nom} | ${s.famille} | ${s.voit} |`), `${s.n} : ligne de l'index identique au catalogue`);
    for (const [cle, val] of Object.entries(s.visual)) {
      assert.ok(connues.has(cle), `${s.n} : réglage inconnu ${cle}`);
      if (/^font/.test(cle)) {
        assert.ok(polices[val]?.faces, `${s.n} : police ${val} absente de la table`);
        for (const face of polices[val].faces) assert.ok(fs.existsSync(path.join(root, 'assets/fonts', face.file)), `${s.n} : ${face.file} livrée`);
      }
    }
    assert.ok(polices[s.visual.fontCaptions].measureFile, `${s.n} : police de sous-titres mesurable (measureFile)`);
    assert.ok(['bloc', 'karaoke', 'mot-a-mot', 'un-mot'].includes(s.look.mode), `${s.n} : mode`);
    assert.ok(['aucune', 'pop', 'rebond', 'glisse', 'fondu', 'flou', 'zoom', 'machine'].includes(s.look.entree), `${s.n} : entrée`);
    assert.doesNotMatch(JSON.stringify(s), /—/, `${s.n} : pas de tiret long`);
  }
});

test('styles de sous-titres : choisir, appliquer sur la voix, relancer, retoucher, retirer', (t) => {
  if (!outils(t, { pil: true })) return;
  const dir = maison(t);
  sync(dir);
  const reel = nouveauReel(dir, 'Sous-titres');
  plan(reel, [[0, 2.6, [['On', 0.1], ['garde', 0.4], ['tes', 1.2], ['mots', 1.5]], ['on garde', 'tes *mots*']],
    [2.6, 5.3, [['on', 2.7], ['coupe', 3.0], ['les', 3.6], ['silences.', 3.9]], ['on coupe', 'les silences']],
    [5.3, 8.0, [['ça', 5.4], ['marche', 5.7]], ['ça marche']]]);
  const outil = (...a) => spawnSync('python3', ['tools/sous_titres.py', ...a], { cwd: reel, encoding: 'utf8' });
  const caps = () => read(reel, 'compositions/captions.html');

  // Sans style choisi : rien ne change.
  python(reel, 'tools/montage_captions.py', '--write');
  const origine = caps();
  assert.match(outil().stdout, /rien à faire/);
  assert.equal(caps(), origine);

  // Style 1 (karaoké) pour ce Reel : réglages écrits et acceptés par la synchro, police du style.
  assert.equal(outil('--choisir', '1').status, 0);
  const reglages = JSON.parse(read(reel, 'reel.config.json')).visual;
  assert.equal(reglages.captionsStyle, 1);
  assert.equal(reglages.fontCaptions, 'Montserrat');
  assert.doesNotMatch(spawnSync(process.execPath, ['scripts/sync.mjs'], { cwd: dir, encoding: 'utf8' }).stderr, /ignoré/);
  assert.match(read(reel, 'brand/tokens.css'), /--brand-font-captions: Montserrat/);
  python(reel, 'tools/montage_captions.py', '--write');
  const apres = outil();
  assert.equal(apres.status, 0, apres.stderr);
  const html = caps();
  assert.match(html, /data-sous-titres="1"/);
  assert.match(html, /<span class="w w1"><span class="b"[^>]*>MOTS<\/span><span class="h"[^>]*>MOTS<\/span><\/span>/, 'astérisques retirés à l’affichage');
  assert.match(html, /tl\.fromTo\('#captions #cap-1 \.w1 \.h', \{opacity: 0\}, \{opacity: 1[^)]*\}, 1\.500\);/, 'le mot s’allume quand il est dit');
  assert.match(html, /--st-allume-0: #ffe600/);
  assert.doesNotMatch(html, /<div class="cap clip" /, 'tous les sous-titres portent le style');

  // Relancé : même résultat ; la sortie de montage_captions.py est gardée.
  outil();
  assert.equal(caps(), html, 'relançable à l’identique');
  assert.match(read(reel, 'work/captions.origine.html'), /<div class="cap clip" id="cap-0"/);
  assert.doesNotMatch(read(reel, 'work/captions.origine.html'), /data-sous-titres/);

  // Retouche : le mot dit en bleu ; une retouche absurde est refusée.
  assert.equal(outil('--retouche', 'allume=#3aa0ff').status, 0);
  outil();
  assert.match(caps(), /--st-allume-0: #3aa0ff/);
  assert.notEqual(outil('--retouche', 'allume=bleu').status, 0);

  // Un mot à la fois (style 20) : un sous-titre par mot, calé sur les images de la voix.
  outil('--choisir', '20');
  python(reel, 'tools/montage_captions.py', '--write', '--mots', '1');
  outil();
  const mots = [...caps().matchAll(/class="cap clip st[^"]*"[^>]*data-start="([\d.]+)"/g)].map(([, s]) => Number(s));
  assert.equal(mots.length, 10, 'dix mots, dix sous-titres');
  for (const s of mots) assert.ok(Math.abs((s + 0.01 / 30) * 30 - Math.round((s + 0.01 / 30) * 30)) < 1e-3 || s === 0, `${s} sur une image`);
  assert.doesNotMatch(read(reel, 'reel.config.json'), /captionsLook/, 'un nouveau choix efface les retouches du précédent');

  // Retiré : les sous-titres reviennent exactement à la sortie de montage_captions.py.
  assert.equal(outil('--sans').status, 0);
  outil();
  assert.doesNotMatch(caps(), /data-sous-titres/);
  assert.equal(caps(), read(reel, 'work/captions.origine.html'));
});
