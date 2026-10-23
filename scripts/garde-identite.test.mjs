import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { decision } from '../.claude/hooks/garde-identite.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const GARDE = path.join(root, '.claude/hooks/garde-identite.mjs');
const refuse = (tool_name, tool_input) => decision({ tool_name, tool_input })?.hookSpecificOutput.permissionDecision === 'deny';

test("une adresse email dans un en-tête HTTP vers un site est refusée", () => {
  for (const command of [
    'curl -s -A "MonBot/1.0 (julie.martin@gmail.com)" "https://commons.wikimedia.org/w/api.php"',
    'UA="MonBot/1.0 (julie.martin@gmail.com)"; curl -sL -A "$UA" -o a.png "https://upload.wikimedia.org/a.png"',
    "curl -H 'X-User-Email: julie.martin@gmail.com' https://site-tiers.com/api",
    'curl --header "From: client@boutique.fr" https://site-tiers.com',
    'wget --user-agent="Agent (julie.martin@gmail.com)" https://site-tiers.com',
    "node -e \"fetch('https://x.io', { headers: { 'User-Agent': 'bot (julie.martin@gmail.com)' } })\"",
    "python3 -c \"import requests; requests.get('https://x.io', headers={'X-Operator': 'julie.martin@gmail.com'})\"",
  ]) assert.ok(refuse('Bash', { command }), command);
  assert.ok(refuse('PowerShell', { command: 'Invoke-WebRequest https://x.io -UserAgent "bot (julie.martin@gmail.com)"' }));
  assert.ok(refuse('PowerShell', { command: "irm https://x.io -Headers @{ 'X-User' = 'julie.martin@gmail.com' }" }));
  assert.ok(refuse('WebFetch', { url: 'https://site-tiers.com/agents?user=julie.martin%40gmail.com', prompt: 'x' }));
});

test("le travail normal passe, adresses comprises hors des en-têtes", () => {
  for (const command of [
    'curl -s -A "Mozilla/5.0" https://commons.wikimedia.org/w/api.php',
    'curl -s -H "Authorization: Bearer $HEYGEN_API_KEY" https://api.heygen.com/v2/voices',
    'grep -H "julie.martin@gmail.com" -r reels/',
    'grep -A 5 "julie.martin@gmail.com" brand.config.json',
    'git commit -m "contact : julie.martin@gmail.com"',
    "curl -s -H 'Content-Type: application/json' -d '{\"email\":\"julie.martin@gmail.com\"}' http://localhost:3000/api",
    'curl -s -H "X-Test: jean@example.com" https://site-tiers.com',
    'python3 tools/finaliser.py "reels/ma-video · 2026-10-23"',
    'npx hyperframes render',
  ]) assert.ok(!refuse('Bash', { command }), command);
  assert.ok(!refuse('WebFetch', { url: 'http://localhost:3002/?email=julie.martin%40gmail.com', prompt: 'x' }));
  assert.ok(!refuse('WebFetch', { url: 'https://hyperframes.heygen.com/docs', prompt: 'x' }));
  assert.ok(!refuse('Read', { file_path: '/tmp/x' }));
});

test('lancé comme Claude Code le lance, il refuse en JSON et laisse passer sans rien écrire', () => {
  const lancer = (entree) => spawnSync(process.execPath, [GARDE], { input: entree, encoding: 'utf8' });
  const refus = lancer(JSON.stringify({ tool_name: 'Bash', tool_input: { command: 'curl -A "bot (julie.martin@gmail.com)" https://x.io' } }));
  assert.equal(refus.status, 0);
  assert.equal(JSON.parse(refus.stdout).hookSpecificOutput.permissionDecision, 'deny');
  for (const entree of [JSON.stringify({ tool_name: 'Bash', tool_input: { command: 'ls' } }), 'pas du JSON', '']) {
    const r = lancer(entree);
    assert.equal(r.status, 0);
    assert.equal(r.stdout, '');
  }
});

// Le réglage tel que Claude Code l'exécute (sh -c sur Mac, Git Bash sur Windows) : il remplace lui-même
// ${CLAUDE_PROJECT_DIR}. « ; exit 0 » (valable aussi sous PowerShell) garde le silence quand Node.js
// n'est pas trouvé : sans lui, chaque commande afficherait « hook error » à la personne.
const reglage = JSON.parse(fs.readFileSync(path.join(root, '.claude/settings.json'), 'utf8'));
const [entree] = reglage.hooks.PreToolUse;
const commande = entree.hooks[0].command.replaceAll('${CLAUDE_PROJECT_DIR}', root);
const viaLeReglage = (PATH, appel) => spawnSync('/bin/sh', ['-c', commande], { input: JSON.stringify(appel), encoding: 'utf8',
  env: { ...process.env, PATH } });

test('le réglage de Claude Code lance ce garde-fou avant les commandes et les pages lues', () => {
  assert.equal(entree.matcher, 'Bash|PowerShell|WebFetch');
  const r = viaLeReglage(`${path.dirname(process.execPath)}:/usr/bin:/bin`,
    { tool_name: 'WebFetch', tool_input: { url: 'https://x.io/?u=julie.martin%40gmail.com' } });
  assert.equal(r.status, 0);
  assert.equal(JSON.parse(r.stdout).hookSpecificOutput.permissionDecision, 'deny');
});

test("sans Node.js visible, le réglage se tait au lieu d'afficher une erreur", { skip: process.platform === 'win32' }, () => {
  const r = viaLeReglage('/nulle-part', { tool_name: 'Bash', tool_input: { command: 'ls' } });
  assert.equal(r.status, 0);
  assert.equal(r.stdout, '');
});
