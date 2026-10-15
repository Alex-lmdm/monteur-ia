---
name: youtube
description: >-
  Monte une VIDÉO YOUTUBE horizontale (16:9, 1920×1080) à partir d'un rush face caméra lu au
  prompteur : dérush au rythme des Reels, zoom sur ce qui compte, logos des marques citées, créateur qui glisse sur
  le côté pour laisser place à un panneau, plans plein écran, textes d'appui ponctuels, sons,
  export à -14 LUFS, chapitres, sous-titres SRT, titre et description. Écrit aussi le script d'une
  vidéo YouTube. Use when the user says « vidéo YouTube », « vidéo longue », « format horizontal »,
  « 16:9 », « monte ma vidéo YouTube », « script YouTube », « vídeo de YouTube », or works inside a
  youtube/<nom>/ project. PAS un Reel (vertical : pipeline du fichier agent) ni une story.
---

# Vidéo YouTube (16:9) : le mode intégré de Monteur IA

Une vidéo YouTube n'est pas un long Reel. On garde la méthode de Monteur IA (dérush au script près,
motion de marque, tout piloté par l'IA, contrôles automatiques), mais presque tous les réglages
changent : le format, le rythme, les cadrages, la place du texte, le son, la publication.

| | Reel | Vidéo YouTube |
|---|---|---|
| Format | 1080×1920 vertical | **1920×1080 horizontal** |
| Souffle entre deux phrases | ≈ 0,10 s | **≈ 0,10 s, comme les Reels** (réglable : `youtube.derush`) |
| Cadrage | split haut/bas | **plan large**, serré **avec parcimonie** (les moments qui comptent), créateur **décalé + panneau** |
| Rythme visuel | un plan toutes les 1 à 2 s | **un changement visuel toutes les 15 à 30 s** |
| Texte | sous-titres mot à mot, en continu | **textes d'appui ponctuels** (1 à 3 par minute) + fichier SRT |
| Graphique | une idée par phrase | **une carte par sujet** (20 à 40 s) qui se construit |
| Son final | -16 LUFS | **-14 LUFS**, posé après l'export (`tools/finaliser.py`) |
| Publication | légende Instagram + DM | **titre, description, chapitres, SRT, écran de fin** |

Les règles de montage complètes, avec leurs sources : **`references/doctrine.md`**. À relire avant
chaque plan de montage : c'est elle qui fait la différence entre « une vidéo coupée » et « une
vidéo qu'on regarde jusqu'au bout ».

**Références (charger selon l'étape) :**

| Étape | Fichier |
|---|---|
| Écrire ou retoucher le script | `references/script-youtube.md` |
| Plan de montage, choix des cadrages, densité, sons | `references/doctrine.md` |
| Construire : sections, visages, panneaux, master, textes d'appui | `references/montage-16-9.md` |
| Brief de style, première vidéo, débrief | `references/premiere-video.md` |
| Titre, description, chapitres, sous-titres, écran de fin | `references/publication.md` |

Pièges du rendu par couches (communs avec les Reels, valables tels quels en 16:9) : skill
`motion-design`, `references/montage-talking-head.md` §0bis et §0ter. Logos de marque : skill
`thesvg`. Animations : `hyperframes-animation`, `hyperframes-registry`.

---

## 1. Où on travaille

Chaque vidéo YouTube est un projet à elle : `youtube/<sujet · date · client>/` du dossier Monteur
IA, un projet de l'app HyperFrames, avec la même forme qu'un Reel (`index.html`, `compositions/`,
`derush/`, `assets/`, `tools/`, `work/`, `exports/`, `meta.json` avec `monteurIa.lieu = "youtube"`).

- Créer : `python3 tools/nouvelle_video_youtube.py "<sujet>" [--video "<rush>"] [--brief "<demande>"] --ouvrir`
  depuis le dossier Monteur IA (`../tools/…` depuis l'accueil, `tools/…` depuis un Reel).
- Les outils du 16:9 sont dans `tools/` de la vidéo, sous les mêmes noms que ceux d'un Reel
  (`sections.py`, `build_faces.py`, `build_master.py`…) mais en 1920×1080 : **jamais** un outil
  copié d'un Reel ou de la racine. Ceux marqués « A CHAQUE VIDEO » (`sections.py`, `build_sfx.py`)
  et ceux du dérush (`cut_boundaries.py`, `build_words.py`) appartiennent à cette vidéo.
- Suivi : tiens **`work/suivi.md`** à jour (étape faite, prochaine étape, fichiers). Une vidéo
  longue se monte souvent en plusieurs conversations : on reprend depuis ce fichier sans refaire ni
  redemander.
- Dans l'app HyperFrames, l'aperçu et l'export sont les siens : ne lance ni `npm run dev` ni rendu,
  dis « Clique sur **Export** en haut à droite ». Hors de l'app : `npm run render`.

## 2. Le parcours, étape par étape

Annonce toujours **la prochaine étape, une seule**, et ne déborde pas dessus. Chaque étape a sa
barrière « terminé quand ». **Première vidéo YouTube** (`youtube.firstVideoDone` pas `true` dans
`brand.config.json`) : brief court, puis montage d'une traite et débrief, comme pour la première
vidéo d'un Reel (`references/premiere-video.md`).

| # | Étape | Le client dit… | À faire | Terminé quand |
|---|---|---|---|---|
| 0 | **Brief de style** (1re vidéo YouTube seulement) | « monte ma vidéo YouTube » | `references/premiere-video.md` §1 : 3 questions max, en un message, avec un défaut pour chacune | `youtube.styleChosen = true`, réponses notées dans `youtube.*` |
| 1 | **Script** (optionnel) | « écris mon script YouTube », « on brainstorme une vidéo » | `references/script-youtube.md` | Hook 30 s + promesse + parties + fin, dans sa voix, validé |
| 2 | **Tournage** | (il filme) « voici ma vidéo » | conseils §3 si on te les demande | Le rush est là (horizontal, résolution max) |
| 3 | **Dérush** | « fais les cuts » | skill `derush`, avec les différences YouTube (§4) | Re-transcription = le texte voulu, coupes dans la cible (`ecarts_derush.py`), `_cuts.json` |
| 4 | **Plan de montage** | « passe au montage » | `references/doctrine.md`, puis plan dans `work/plan-montage.md` | Le client a validé le plan (sauf 1re vidéo) |
| 5 | **Montage** | (après le plan) | `references/montage-16-9.md` | `npm run check` vert, snapshots regardés, `sections.py` sans alerte grave |
| 6 | **Revue** | « là je veux plutôt ça », « à 3:12… » | retouches par horodatage | Le client a tout validé |
| 7 | **Sons** | « mets les sons et la musique » | `tools/build_sfx.py` (doctrine §6) ; **Pack SFX** (`tools/sfx_mix.py` dans la vidéo) : skill `pack-sfx` (§9) et `tools/sfx_mix.py` à sa place | Sons posés, `--probe` vérifié |
| 8 | **Export** | « exporte » | bouton Export (app) ou `npm run render`, puis **`python3 tools/finaliser.py`** | `✅ Prête à téléverser` (son à -14 LUFS, contrôles verts) |
| 9 | **Publication** | « le titre », « la description » | `references/publication.md`, `python3 tools/publication.py` | `publication.md` prêt : 3 titres, description, chapitres, SRT |
| 10 | **Ranger** | « c'est en ligne » | `python3 tools/ranger.py` | Vidéo copiée dans `Vidéos/youtube-publiees/`, marquée publiée |

**Pack SFX avant 1.2.0** (`tools/sfx_mix.py` dans le dossier Monteur IA, pas dans la vidéo) : il ne
connaît pas les vidéos YouTube. Dis au client de le retélécharger depuis sa formation (module
« Mises à jour », bouton jaune), puis de mettre Monteur IA à jour ; d'ici là, `tools/build_sfx.py`
(les sons du pack aussi, par leur chemin `pack/…`).

**Ordre verrouillé** (hors première vidéo) : pas de sons avant que le montage soit validé (6), pas
de publication avant l'export finalisé (8). Une vidéo de 15 minutes se revoit par passages : demande
au client ses retours **avec l'horodatage** (« à 3:12, je veux… »), pas section par section.

## 3. Tournage (si le client demande comment filmer)

- **À l'horizontale**, 4K et 30 im/s si possible (Réglages > Appareil photo > Enregistrer une vidéo
  sur iPhone), mode couleur normal (pas de HDR, pas de Log). La 4K permet des cadres serrés nets.
- Cadre : yeux vers le tiers haut, de l'espace au-dessus de la tête et sur les côtés. Le cadre
  serré est découpé dans l'image : ne te cadre pas trop serré au tournage.
- Prompteur, phrase par phrase ; on refait une phrase ratée sans s'arrêter : le dérush garde la
  dernière bonne prise.
- Le son compte plus que l'image : micro-cravate ou micro proche, pièce calme.
- Transfert en résolution maximale (AirDrop ou câble), jamais par messagerie.

Rush vertical (téléphone tenu droit) : il passe, mais le cadre large est une bande agrandie, moins
nette, et le cadre serré l'est encore plus. Dis-le simplement, et conseille l'horizontale pour la
prochaine.

## 4. Dérush : le skill `derush`, avec ces différences

Charge le skill `derush` et suis-le, sauf :

- **Rythme des coupes** : celui des Reels par défaut (`PAD_START` / `PAD_END` du bloc `derush`,
  0,04 / 0,02 : environ 0,10 s entre deux phrases). Un client qui veut garder sa respiration règle
  `brand.config.json` → `youtube.derush` (ex. 0,10 / 0,25) ; `python3 tools/ecarts_derush.py` mesure
  alors 0,15 à 0,60 s au lieu de 0,20 s au plus (la cible suit les marges du dérush).
- **Prises** : `python3 tools/prises.py "<rush>" --script <texte> --ecrire` propose les prises
  (la dernière prise propre de chaque phrase) et écrit `derush/build_derush.py` ; relis son tableau.
- **Couper entre les phrases, jamais au milieu** : un « euh » collé au mot suivant reste (le couper
  abîme les mots autour). Phrase doublée : garder la dernière prise propre.
- **Changer de cadre sur un mot** (doctrine §2) : partager la prise en deux îlots qui se touchent
  (fin du premier + `PAD_END` = début du second - `PAD_START`), la frontière juste avant le mot,
  dans un creux de la voix. C'est un **raccord** : monté d'un seul tenant, sans coupe ;
  `cut_boundaries.py` et `ecarts_derush.py` le reconnaissent.
- **Aperçu** : `python3 tools/apercu_derush.py derush/<cut>.mp4` (version 16:9 de l'outil).
- **Vidéo longue** : la transcription de tout le rush prend quelques minutes (dis-le une fois, puis
  travaille). Pour choisir les prises, avance chapitre par chapitre et écris la liste `ISLANDS` au
  fil de l'eau dans `derush/build_derush.py` : sur 150 prises, c'est ce qui évite de se perdre.
- Après le nettoyage de la voix (Adobe Podcast, comme pour un Reel ; première vidéo : voix brute
  mise au niveau -24 LUFS) : `tools/cut_boundaries.py` → `<cut>_cuts.json`, puis
  `python3 tools/build_words.py` (les mots horodatés servent aux textes d'appui et au SRT).
- `base.mp4` : le dérush réduit en **1920×1080** (même commande que motion-design étape 3, en
  remplaçant `1080:1920` par `1920:1080`).

## 5. Checklist anti-oubli YouTube

- [ ] **Frontières = `<cut>_cuts.json`**, jamais Whisper ; la table vit dans `tools/sections.py`,
      le master se **génère** (`python3 tools/build_master.py --write`), il ne s'édite pas.
- [ ] **Cadrage calé avant les visages** : `python3 tools/build_faces.py --apercu`, regarder
      `work/cadrage-apercu.jpg`, régler `youtube.cadrage` (`visageX`, `yeuxY`), puis
      `build_faces.py` et `build_master.py --write`.
- [ ] **Changement visuel toutes les 15 à 30 s**, jamais plus de 45 s sans panneau ni graphique ;
      `python3 tools/sections.py` affiche les alertes de rythme : les traiter.
- [ ] **Zoom avec parcimonie** : plan large par défaut, serré seulement sur ce qui compte (une
      chute, un mot clé, de préférence en raccord pile sur le mot), très serré rare. Un zoom /
      dézoom toutes les quelques secondes fatigue (retour client).
- [ ] **Début jamais vide** : dès la première phrase, une incrustation légère (logo d'une marque
      citée, une étiquette) ; pas de plein écran sur le hook ni sur une phrase personnelle ; **2 s
      de visage** au moins entre deux plans plein écran ; un plein écran motion sur chaque temps fort.
- [ ] **Panneau (cote)** : 960×1080, une carte qui se construit pendant tout le sujet ; textes dans la
      zone titre (`var(--brand-yt-title-x)`), rien de permanent dans les 150 px du bas (barre de
      lecture YouTube).
- [ ] **Incrustation (over)** : fond **transparent**, jamais sur la bouche ni le visage.
- [ ] **Textes d'appui** : 1 à 3 par minute, 1 à 4 mots, posés sur les mots prononcés
      (`EMPHASES` de `sections.py`, puis `python3 tools/build_emphases.py --write`). Jamais une phrase
      entière, jamais ce que le graphique montre déjà.
- [ ] **Chapitres** : `"chapitre"` sur les sections qui ouvrent une partie ; 00:00, au moins 3,
      chacun ≥ 10 s.
- [ ] **Couleurs et polices** : toujours `var(--brand-*)` (le style de la marque, le même que ses
      Reels), jamais un hex en dur.
- [ ] `npm run check` après chaque modif `.html`, `npx hyperframes snapshot --at …` après chaque
      animation, et **regarder** les images.
- [ ] **Export** : après le bouton Export, **toujours** `python3 tools/finaliser.py` (son à -14 LUFS,
      contrôle du visage et du format, copie à téléverser dans Téléchargements).
- [ ] Pas de tiret long dans les textes à l'écran, le titre ni la description.
