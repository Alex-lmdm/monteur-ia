# Styles de sous-titres du catalogue

Trente looks de sous-titres prêts à l'emploi, montrés en vidéo dans la formation (module
« Templates », chapitre des styles de sous-titres). Le client les demande par numéro ou par nom :
« mets mes sous-titres en style 12 », « les sous-titres Néon », « sous-titres 4, mais en bleu ».

**À ne pas confondre avec les 11 styles de montage** (skill `reel-cloneur`, `styles/README.md`) :
« style 4 » seul = un style de montage ; un numéro avec « sous-titres » = ce catalogue. Dans le
doute, une seule question : « Le style de montage 12, ou le style de sous-titres 12 ? ».

**Un style de sous-titres est un look**, rien d'autre : la police, les couleurs, la façon dont les
mots arrivent (d'un bloc, mot à mot, un mot à la fois) et ce qui marque le mot dit. La place des
sous-titres reste celle du montage. Il se pose donc sur tout montage : les réglages de base, un
style de montage du catalogue (il remplace alors la section « Les sous-titres » de sa fiche et
l'outil de sous-titres du kit : `karaoke.py` du style 4 ne se lance pas), un style cloné.
Reels et stories verticaux seulement : une vidéo YouTube (skill `youtube`) n'en a pas encore ;
dis-le au client et propose le style le plus proche à fabriquer pour cette vidéo.

| N° | Style | Famille | Ce qu'on voit |
|---|---|---|---|
| 1 | Karaoké jaune | Le mot dit s'allume | Capitales très grasses, blanc cerclé de noir ; le mot dit s'allume en jaune, chaque sous-titre surgit. |
| 2 | Karaoké vert | Le mot dit s'allume | Capitales hautes et serrées ; le mot dit passe au vert et grossit un instant. |
| 3 | Trois couleurs | Le mot dit s'allume | Deux lignes en capitales cerclées de noir ; le mot dit s'allume en jaune, vert ou rouge, une couleur par sous-titre. |
| 4 | Bulle rose | Le mot dit s'allume | Lettres rondes et gonflées, contour prune et halo rose ; le mot dit passe au rose, chaque sous-titre rebondit. |
| 5 | Bande dessinée | Le mot dit s'allume | Lettrage de BD, contour noir et ombre dure ; le mot dit change de couleur, chaque sous-titre surgit. |
| 6 | Cartoon violet | Le mot dit s'allume | Grosses lettres de dessin animé, contour et ombre dure ; le mot dit passe au violet. |
| 7 | Bloc 3D | Le mot dit s'allume | Lettres carrées en relief ; le mot dit passe au bleu, chaque sous-titre glisse vers le haut. |
| 8 | Course | Le mot dit s'allume | Italique de course, ombre dure ; le mot dit passe au vert fluo, chaque sous-titre glisse. |
| 9 | Rétro | Le mot dit s'allume | Capitales étroites façon affiche, ombre dure ; le mot dit passe au jaune pâle. |
| 10 | Feutre | Le mot dit s'allume | Lettres dessinées au gros feutre, cerclées de noir ; le mot dit passe au vert tendre. |
| 11 | Surligneur rouge | Une boîte derrière le mot | Capitales blanches ; une boîte rouge se pose derrière le mot dit, comme sur TikTok. |
| 12 | Boîte orange | Une boîte derrière le mot | Deux lignes en capitales cerclées de noir ; le mot dit se pose sur une boîte orange. |
| 13 | Marqueur fluo | Une boîte derrière le mot | Une serif noire sur une carte blanche ; le mot dit passe au surligneur jaune fluo. |
| 14 | Lignes en boîtes | Une boîte derrière le mot | Chaque ligne dans sa boîte noire ; le mot dit passe sur une boîte verte. |
| 15 | Bandeau noir | Sur un bandeau | Capitales étroites blanches sur un bandeau noir : sobre, lisible sur n'importe quelle image. |
| 16 | Étiquette jaune | Sur un bandeau | Capitales noires sur une étiquette jaune vif, qui surgit à chaque sous-titre. |
| 17 | Pilule claire | Sur un bandeau | Une pilule gris clair ; les mots passent du gris au noir à mesure qu'ils sont dits. |
| 18 | Pilule sombre | Sur un bandeau | Capitales blanches dans une pilule sombre ; le mot dit passe au rose. |
| 19 | Marine élégant | Sur un bandeau | Une serif crème sur un bandeau bleu marine ; le mot dit passe au doré. |
| 20 | Un mot géant | Mot à mot | Un seul mot à la fois, en capitales géantes qui claquent ; le mot fort en jaune. |
| 21 | Mot cyan | Mot à mot | Un mot à la fois, cyan cerclé de noir, qui rebondit à chaque mot. |
| 22 | Montée douce | Mot à mot | Petites capitales espacées ; chaque mot monte doucement au moment où il est dit. |
| 23 | Net en douceur | Mot à mot | Chaque mot sort du flou au moment où il est dit, en blanc simple. |
| 24 | Machine à écrire | Mot à mot | Lettres de machine à écrire, tapées une à une sur une bande de papier crème. |
| 25 | Mots forts | Le mot fort ressort | Capitales blanches ; le mot fort de chaque sous-titre en vert, rouge ou jaune, avec un petit saut. |
| 26 | Éditorial | Le mot fort ressort | Texte simple qui arrive mot à mot, et le mot fort en grande serif italique crème. |
| 27 | Signature | Le mot fort ressort | Texte simple, et le mot fort écrit à la main, comme une signature. |
| 28 | Néon | Le mot fort ressort | Texte blanc lumineux ; le mot fort s'allume en néon vert, rose ou bleu. |
| 29 | Lueur dorée | Doux et sobre | Une serif dorée qui brille doucement ; chaque sous-titre sort du flou. |
| 30 | Sobre | Doux et sobre | Texte blanc simple avec une ombre douce : discret, il va sur tout. |

Le détail de chaque style (police, tailles, couleurs, animations) est dans
`templates/styles-sous-titres.json`, lu par l'outil : ne le recopie jamais dans une compo.

## Poser un style sur un Reel

Depuis le dossier du Reel, à l'étape des sous-titres :

1. `python3 tools/sous_titres.py --choisir N` : écrit le style dans `reel.config.json` (police,
   taille, casse, et `visual.captionsStyle`) puis lance la synchro. Pour CE Reel seulement.
2. `python3 tools/montage_captions.py --write` (styles 20 et 21, un mot à la fois : `--mots 1`),
   puis le découpage final par unité grammaticale comme d'habitude (`references/sous-titres.md`).
   Styles à mot fort (20, 25 à 28) : entoure le mot fort d'astérisques dans `MANUAL`
   (`"tes *vidéos*"`), un par sous-titre au plus, choisi pour le sens (le chiffre, le résultat,
   le nom propre) ; sans astérisque, l'outil prend le chiffre ou le mot le plus long.
3. `python3 tools/sous_titres.py` : réécrit `compositions/captions.html` (un `<span>` par mot,
   timeline calée sur `derush/<vidéo>_words.json`). Relance-le après chaque `montage_captions.py
   --write` : il repart toujours de leur sortie (`work/captions.origine.html`).
4. `npm run check`, puis les snapshots comme pour toute animation. Un sous-titre trop large pour
   l'image est réduit tout seul (message de l'outil) ; s'il reste serré, recoupe-le.

Jamais de couleur, de police ni d'animation écrite à la main dans le bloc généré : elle partirait
au prochain passage de l'outil. Tout passe par les réglages.

## Tout se personnalise

Le client veut le style « mais » autrement : une retouche, gardée dans `visual.captionsLook`,
puis le point 3 (ou 2 et 3 si la taille ou la police change).

| Il dit | Tu fais |
|---|---|
| « le mot en bleu », « avec ma couleur » | `--retouche allume=#3aa0ff` ; sa couleur d'accent : `allume=accent` |
| « le texte en jaune » | `--retouche couleur=#ffe600` |
| « une boîte derrière le mot », « la boîte en vert » | `--retouche boite=#35e035` |
| « sans le bandeau », « un bandeau blanc » | `--retouche plaque=aucune`, `plaque=#ffffff` |
| « sans contour », « contour plus épais » | `--retouche contour=aucun`, `contour="9px #000000"` |
| « une ombre », « un halo rose » | `--retouche ombre=douce`, `ombre="lueur #ff2d95"` |
| « mot par mot », « un mot à la fois », « d'un bloc » | `--retouche mode=mot-a-mot` (`un-mot`, `bloc`, `karaoke`) |
| « qu'ils rebondissent », « sans animation » | `--retouche entree=rebond` (`pop`, `glisse`, `fondu`, `flou`, `zoom`, `machine`, `aucune`) |
| « sur deux lignes » | `--retouche lignes=2` |
| « plus gros », « plus petit » | `visual.captionsSize` dans `reel.config.json`, synchro, points 2 et 3 |
| « avec ma police » | `visual.fontCaptions` (police livrée ou la sienne, `/setup visuel`), synchro, points 2 et 3 |

Montre, ajuste. Une fois validé, demande s'il le garde pour ses prochaines vidéos ; oui :
`python3 tools/sous_titres.py --choisir N --maison`, puis ses retouches avec `--maison`
(`brand.config.json`). Il vaut ensuite pour toutes ses vidéos, quel que soit le montage.

Revenir aux sous-titres de base : `python3 tools/sous_titres.py --sans` (ce Reel) ou
`--sans --maison` (toutes ses vidéos), puis le point 3.
