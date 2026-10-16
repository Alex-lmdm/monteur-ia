# Mode style : cloner une façon de monter

Le client veut reprendre **le style de montage** d'une vidéo, pas son texte : le rythme des coupes,
le cadrage et les zooms, l'allure des sous-titres, les textes et animations à l'écran, les images
d'illustration, les transitions, les couleurs, les sons. Le résultat : une **fiche de style** que son
monteur applique à ses prochaines vidéos brutes.

Le cas le plus utile : **il clone sa propre vidéo**. Il monte depuis des années avec un style à lui ;
il colle une vidéo qui le représente bien, et toutes les suivantes sortent dans ce style. Pour une
vidéo d'un autre créateur, c'est la même chose, avec la règle ci-dessous.

> **La règle : on reprend la manière de monter, jamais la signature de l'auteur.** Un rythme, une
> allure de sous-titres, un type de transition, une palette, ça ne s'invente pas deux fois : ça se
> reprend. Son logo, son nom, son filigrane, sa mascotte, ses visuels faits maison, son générique,
> sa musique, ses images (plans, B-rolls), non : on les décrit pour en tirer la manière, on ne les
> réutilise pas. Sa vidéo à lui, le client en fait ce qu'il veut.

Vocabulaire face au client : « style de montage », « rythme », « cadrage », « sous-titres »,
« animations », « images d'illustration », « transitions », « bruitages ». Jamais « B-roll »,
« skin », « split », « faceplein », « preset », « token », ni nom de champ ou de fichier technique
(sauf `style.md`, le fichier qu'il peut ouvrir).

---

## 1. Préparer

```bash
python3 tools/cloner_reel.py "<lien ou fichier>" --style
```

Mêmes règles qu'au §1 du skill (échec de téléchargement, repli sur le fichier glissé, `installer`).
En plus de tout le reste, l'outil écrit `style.json` et le dossier `rafales/` ; ses images font
768 px de large, pour reconnaître une police ou un contour.

**Plusieurs vidéos** (les siennes, ou un mélange avec celles d'autres créateurs) : une commande par
vidéo, cinq au plus (au-delà, demande-lui ses cinq préférées). Lis-les toutes, puis écris **une
seule fiche**, dans le dossier de la première : ce qui revient dans toutes devient une règle ; ce
qui change d'une vidéo à l'autre se note « selon la vidéo », ou se laisse de côté s'il ne dit pas
laquelle suivre. Le message du §3 dit sur combien de vidéos la liste s'appuie.

Lis, dans cet ordre :
1. `meta.json` (plateforme, compte ; `musique` = le son déclaré par la plateforme, s'il y en a un) ;
2. `style.json` : `rythme` (plans, coupes par tranche de 5 s), `couleurs` (couleurs vives qui
   reviennent, avec leur valeur ; allure claire ou sombre, vive ou sobre) ;
3. les images comme au §1 du skill : les 5 premières secondes une par une, puis chaque planche ;
4. **chaque rafale** (`style.json` → `rafales`) : des images rapprochées, l'heure en haut à gauche.
   « sous-titres » : 8 images en 1,2 s pendant une phrase (les paroles sont dans la rafale) ; tu y
   vois si le texte arrive d'un bloc, mot par mot, s'il se surligne au mot prononcé, s'il saute ou
   grossit. « coupe » : 6 images autour d'une coupe (étiquette jaune = après) : coupe sèche, glissé,
   zoom, flash, fondu, effet de flou ;
5. `transcript.json` seulement pour caler un sous-titre ou un temps sur la voix.

Couleur exacte d'un élément (un mot surligné, un fond de titre) : `python3 tools/cloner_reel.py
couleurs clones/<dossier>/frames/<image>.jpg --zone bas` (`haut`, `milieu` ou `bas` : la bande où
est l'élément). Elle donne les couleurs les plus présentes et les couleurs vives.

**Le son ne se voit pas.** Tu n'entends pas la vidéo et l'outil ne mesure pas le son : n'écris
jamais qu'il y a ou non une musique ou des bruitages. Tu le demandes au client (§3).

---

## 2. Observer et écrire `style.md`

Observe avec **`references/grille-style.md`** : chaque dimension, ce qu'il faut regarder, les
pièges. Note les valeurs (secondes, nombre de mots, position, couleur) plutôt que des adjectifs, et
des **règles** plutôt que des moments. Une dimension que les images ne permettent pas de trancher
s'écrit « à confirmer », jamais devinée.

Puis écris `clones/<dossier>/style.md` sur le modèle de **`references/modele-style.md`** : la fiche
complète, dimension par dimension, avec pour chacune ce que fait la vidéo et **ce que ton monteur en
fera** (le réglage de Monteur IA qui le reproduit, ou l'équivalent le plus proche). Ce fichier sert
au montage : il doit se suffire, sans cette conversation.

Ce que Monteur IA reproduit, et ce qu'il approche seulement :

| Dans la vidéo | Chez Monteur IA |
|---|---|
| Couleurs de l'habillage (fond, accent, texte) | ses couleurs, à la valeur près, pour une vidéo ou pour toutes |
| Police des sous-titres | Inter, Anton ou Archivo Black livrées ; la police exacte si le client fournit le fichier (skill `setup`, bloc D3) |
| Allure des sous-titres | 5 apparences (bandeau plein, contour, plaque arrondie, ombre portée, souligné), taille, majuscules ou non, graisse, interligne, 1 ou 2 lignes, position |
| Sous-titre mot par mot, mot surligné quand il est prononcé, en escalier… | se fabrique pour la vidéo, sur le minutage de chaque mot |
| Cadrage (visage plein écran, écran partagé, alternance) | les deux cadrages et leur alternance |
| Zooms sur le visage | zooms animés (préférence) |
| Rythme des coupes, silences retirés | coupes plus ou moins serrées (marges du dérush) et préférence de rythme |
| Animations, schémas, logos, textes à l'écran, images d'illustration | motion design de Monteur IA (préférences : densité, type, place) |
| Gros titres plein écran | se font : le réglage de base les évite, une demande ou un style cloné le remplace |
| Transitions | coupe sèche, glissé rapide, fondu court de base ; toute autre (flash, flou, zoom brusque) se fabrique |
| Musique de fond, bruitages | sa musique (fichier fourni) et ses bruitages, si le client confirme qu'il y en a |
| Étalonnage de l'image (teinte, grain, contraste) | jamais par défaut : le monteur ne retouche pas l'image filmée, sauf si le client le demande pour une vidéo |

---

## 3. Le message au client (250 à 400 mots)

D'abord le fichier, puis le message, sa version courte. Dans cet ordre :

1. **En bref** : la signature du style en 2 ou 3 phrases (ce qu'on reconnaît en une seconde).
2. **Ce que je reprends** : 6 à 9 lignes, une par trait, en français courant, concrètes, chacune
   formulée comme une consigne qu'on peut garder telle quelle (« Sous-titres en majuscules, 2 à 3
   mots, bandeau jaune, au milieu de l'écran », « Un changement d'image toutes les 2 secondes
   environ : coupe, zoom ou illustration »). C'est cette liste qu'il valide.
3. **Ce qui ne se fera pas à l'identique**, s'il y en a (rare : presque tout se fabrique) : une
   ligne par point, avec l'équivalent.
4. **Le son**, une question : « Je n'entends pas la vidéo : il y a une musique de fond ? Des
   bruitages (un souffle sur les changements de plan, un « pop » quand un texte apparaît) ? »
5. **La suite**, selon ce qu'il a dit :
   - **Il a glissé sa vidéo brute avec** (« monte ma vidéo dans ce style ») : « Je monte ta vidéo
     dans ce style, pour elle seulement : tes réglages ne bougent pas. Quand tu l'auras validée, je
     te demanderai si on le garde pour tes prochaines vidéos. » Puis §4, « Sur une vidéo », dès sa réponse au son.
   - **Il a dit « garde-le »** (« garde-le pour toutes mes prochaines vidéos », le cas de sa propre
     vidéo) : « Je garde tout ça ? ». Sa réponse vaut accord : §4, « Pour toutes ses vidéos ».
   - **Sinon** : « Envoie-moi une vidéo brute : je la monte dans ce style, pour elle seulement, et
     tu me diras ensuite si on le garde. Et si c'est déjà ton style, dis "garde-le" : je
     l'enregistre tout de suite. »
6. Une ligne en italique : « *Le détail est dans `clones/<dossier>/style.md`.* »

Il veut retirer ou changer un point (« pas les gros titres », « garde mes couleurs ») : tu
l'enlèves ou le modifies dans la liste et dans `style.md`, puis tu continues, sans reposer la
question.

---

## 4. Appliquer et garder

**Par défaut, un style cloné ne s'applique qu'à une vidéo.** Il ne touche à ses réglages (son
style de base) que s'il dit oui. Une vidéo dans un tout autre style ne change donc jamais les
suivantes.

**Sur une vidéo, sans toucher à ses réglages.** Dès qu'il a sa vidéo brute :
1. `python3 tools/nouveau_reel.py "<sujet en 2 à 4 mots>" --video "<sa vidéo>" --brief "Style de
   montage de cette vidéo : ../../clones/<dossier>/style.md (Reel Cloneur), pour elle seulement.
   Une fois la vidéo validée, demande-moi si je garde ce style pour mes prochaines vidéos ; si oui,
   suis le skill reel-cloneur, references/mode-style.md, §4, pour toutes mes vidéos."` (ajoute
   `--ouvrir` s'il travaille dans l'app HyperFrames ; le chemin du Reel créé s'affiche). Le chemin
   de la fiche est écrit vu depuis le Reel (`reels/<nom>/`, deux dossiers sous le dossier Monteur IA).
2. Écris à la racine de ce Reel un **`reel.config.json`** avec le `visual` de la fiche (couleurs,
   polices, allure, taille, casse et position des sous-titres : les mêmes clés que dans
   `brand.config.json`), puis `npm run sync` depuis le dossier Monteur IA : ce Reel, et lui seul, a
   ce style. Police à une seule graisse (Anton, Archivo Black…) : `captionsWeight` = `"auto"`, sinon
   le navigateur la grossit d'un faux gras. Tout le reste (rythme, cadrage, zooms, animations, transitions, sons) est dans la fiche,
   que le montage de ce Reel suit.
3. Le montage se fait comme d'habitude dans ce Reel, avec ses validations. Ce qui sort des réglages
   de Monteur IA (sous-titres mot par mot ou karaoké, transition marquée, gros titres) se fabrique
   pour ce Reel (skill `motion-design`, `references/sous-titres.md`).
4. Vidéo validée : « On garde ce style pour tes prochaines vidéos ? ». Oui : « Pour toutes ses vidéos » ci-dessous, avec les
   retouches qu'il a demandées pendant le montage. Non : rien d'autre, il reste sur ce Reel.

**Pour toutes ses vidéos** (sur son oui, ou d'emblée s'il a dit « garde-le »).
1. Lis `brand.config.json` et les préférences déjà apprises (`montage.preferences`).
2. Écris comme au débrief de la première vidéo : **charge le skill `setup` et suis la section 4 de
   `references/debrief-premiere-video.md`** (la table « où l'enregistrer » et les règles d'écriture
   d'une préférence), avec ces précisions :
   - couleurs, police, allure et position des sous-titres → `visual.*`, comme au bloc D (police non
     livrée : la plus proche des trois, et dis-lui qu'avec le fichier de la sienne ce sera la vraie ;
     police à une seule graisse : `captionsWeight` = `"auto"`) ;
   - cadrage dominant → `montage.defaultLayout`, l'alternance en préférence ;
   - musique : seulement s'il en a une et te donne le fichier (`audio.musicFile`) ; sinon rien ;
   - tout le reste en **4 à 6 préférences au plus**, une phrase de 140 caractères au plus
     chacune (les valeurs fines vont dans la fiche), qui remplacent les anciennes sur le même sujet
     (jamais deux consignes contraires) ; les préférences sont relues à chaque conversation et la
     place y est comptée ;
   - le détail complet : copie `style.md` dans **`brand/style-montage.md`** (il remplace l'ancien)
     et ajoute une préférence : « Style de montage cloné : détail dans brand/style-montage.md du
     dossier Monteur IA, à relire avant chaque montage ».
3. `setup.styleChosen = true`. S'il n'a encore monté aucune vidéo (`setup.firstVideoDone` n'est
   pas `true`), passe-le à `true` : sa première vidéo se montera directement dans ce style, avec
   les validations habituelles, au lieu des réglages de base.
4. `npm run sync`, et relis sa sortie : un avertissement (contraste faible, police manquante) se
   dit au client avant de conclure.
5. Confirme : « C'est enregistré. Ta prochaine vidéo sera montée dans ce style, et tu peux toujours
   me dire de changer quelque chose. »

Le style évolue avec lui : une correction qu'il demande ensuite et veut garder (« moins de zooms »)
se reporte dans `brand/style-montage.md` en plus de sa préférence, pour que la fiche ne contredise
jamais ses réglages.

**Il ne fait ni l'un ni l'autre pour l'instant** : la fiche reste dans `clones/`. « Dis-moi "garde
le style cloné", ou envoie une vidéo à monter dans ce style, quand tu veux. »

---

## 5. Les deux : script et style

Le client veut le script **et** le style : prépare avec `--style`, rends l'analyse du script comme
d'habitude (§2 et §3 du skill), avec en plus, juste avant la question « tu veux faire quoi ? », une
ligne : « J'ai aussi relevé son style de montage (le détail est dans `style.md`). » Puis déroule le
script jusqu'à `script.md` (§4 et §5) : sa liste « À reproduire au montage » renvoie à `style.md`.
Une fois le script livré, pose la question du son du §3 en un message court, sans répéter
l'analyse. Quand il a tourné, le Reel créé pour ce script reçoit les deux fichiers dans son brief,
et le style s'y applique comme au §4, « Sur une vidéo » (pour ce Reel seulement, puis « on le garde ? »).
