# Grille d'observation d'un style de montage

Méthode reprise des projets open source de clonage de style (voir `CREDITS.md`), adaptée à
Monteur IA. On **décrit** comment la vidéo est montée, avec des valeurs (secondes, nombre de mots,
position, couleur) ; on ne la note pas. Chaque dimension se lit sur une source précise : les images
une par une (0 à 5 s), les planches (le reste), les rafales (sous-titres et transitions),
`style.json` (rythme, couleurs). Ce qui ne se voit pas s'écrit « à confirmer » ; une valeur
estimée à l'œil porte « environ ».

**Un style est un système, pas une suite de moments.** On en tire des **règles** qui s'appliquent
à n'importe quelle vidéo du client (« un zoom serré sur chaque chiffre », « le titre du haut change
à chaque idée »), jamais un minutage à recopier (« un zoom à 0:07 »). Trois réflexes :
- **Les règles dépendent souvent du cadrage** : sous-titres à la jointure en écran partagé, en bas
  en plein écran ; titres seulement quand le visage est en bas. Note la condition avec la règle.
- **Le geste unique** (un effet vu une seule fois) reste unique : il se note « une fois par vidéo,
  au plus », il ne devient pas une habitude.
- **Les 3 à 5 gestes signature** : ce qu'on reconnaît en une seconde. Ils ouvrent la fiche.

---

## 1. Le rythme

Source : `style.json` → `rythme` (coupes par tranche de 5 s, plan le plus fréquent), les planches.

- **Changement d'image** : pas seulement les coupes franches. Un zoom, un texte qui arrive, une
  illustration qui recouvre l'écran changent aussi l'image. Compte-les sur les planches : « une
  coupe franche toutes les ~4 s, mais un changement d'image toutes les ~1,5 s ».
- **Accroche plus nerveuse** que la suite ? (coupes sur les 5 premières secondes contre la suite)
- **Silences retirés** : la voix enchaîne sans respiration (montage « jump cut ») ou garde des
  pauses. Les phrases collées, les gestes qui sautent d'une image à l'autre trahissent des coupes
  serrées.

| Plan le plus fréquent | Lecture |
|---|---|
| < 1,5 s | très nerveux |
| 1,5 à 3 s | rapide, le standard des Reels qui marchent |
| 3 à 6 s | posé |
| > 6 s, ou un seul plan | le rythme vient des animations, du zoom ou du texte |

## 2. Le cadrage

Source : images une par une, planches.

- **Visage plein écran**, **écran partagé** (visage en bas, image au-dessus), **visage en petit**
  dans un coin, **pas de visage** (voix sur images). Et l'alternance : quand on passe de l'un à
  l'autre (accroche plein écran puis partagé, retour plein écran sur l'appel à l'action…).
- **Zooms** : deux images d'un même plan où le visage grossit. Sec (d'une image à l'autre, souvent
  sur un mot fort) ou progressif (lent, tout le plan). Combien, et sur quels mots.
- **Hauteur des yeux** : vers le tiers supérieur, centrés, ou bas dans l'image.

## 3. Les sous-titres

Source : rafale « sous-titres » d'abord, puis images et planches. Le marqueur d'identité le plus
visible : prends le temps.

- **Police** : décris sa forme si tu ne la reconnais pas avec certitude (bâton très gras, condensée
  haute, arrondie, à empattements, manuscrite). Les plus courantes en short-form : Montserrat
  ExtraBold/Black, The Bold Font, Poppins Bold, Anton, Bebas Neue, Archivo Black, Inter Black,
  Komika. Un nom donné sans certitude s'écrit « proche de … ».
- **Allure** : texte seul avec contour, bandeau plein derrière le texte, plaque arrondie
  translucide, ombre portée, souligné. Couleur du texte et du fond (outil `couleurs`).
- **Casse** (majuscules, tel qu'écrit), **taille** (part de la largeur de l'écran), **graisse**.
- **Mots par sous-titre** (compte sur plusieurs images) et **nombre de lignes**.
- **Place** : centre, tiers inférieur, jointure entre les deux images d'un écran partagé, haut.
  Fixe ou qui bouge selon le cadrage.
- **Apparition** (la rafale le montre) : d'un bloc ; mot par mot ; mot prononcé surligné ou d'une
  autre couleur (effet « karaoké ») ; petit saut ou grossissement à l'arrivée ; fondu.
- **Mise en valeur** : quels mots (chiffres, noms, mots forts), comment (couleur d'accent, taille,
  emoji accolé).
- **Ponctuation** affichée ou retirée.

## 4. Les textes et animations à l'écran (hors sous-titres)

Source : planches.

- **Types** : titre d'accroche, mots-clés, chiffres en grand, schémas, logos des outils cités,
  captures d'écran, flèches et cercles, emojis, barre de progression, compte à rebours.
- **Densité** : sur l'accroche seulement, toutes les ~x s, à chaque chiffre ou nom cité.
- **Place et taille** : au-dessus du visage, plein écran, petit coin ; part de l'écran.
- **Mouvement** : glisse, rebondit, s'écrit, apparaît d'un coup.
- **Redondance** : le texte répète-t-il la voix (titre = phrase dite) ou ajoute-t-il une
  information (un chiffre, un nom) ?

## 5. Les images d'illustration

Source : planches.

- **Nature** : captures d'écran ou d'une appli, plans filmés exprès, images de banque, vidéos
  générées par IA, mèmes ou extraits.
- **Durée et place** : plein écran x s, au-dessus du visage, en incrustation.
- **Fréquence** : à chaque idée, à chaque outil cité, rarement.

## 6. Les transitions

Source : rafales « coupe ».

- **Coupe sèche** (une image puis l'autre), **glissé** (l'image part sur le côté), **zoom
  brusque** (grossit puis coupe), **flash** (une image blanche), **fondu**, **flou de mouvement**,
  **effet de pellicule ou de glitch**.
- Partout pareil, ou réservé à certains moments (changement de partie, retour au visage).

## 7. Les couleurs et l'habillage

Source : `style.json` → `couleurs`, outil `couleurs`, images.

- **Palette** : 2 ou 3 couleurs qui reviennent (fond des cartes, accent, texte). Une couleur vive
  présente sur beaucoup d'images est souvent l'accent (mot surligné, bandeau) ; vérifie à quoi
  elle correspond avant de la retenir.
- **Fond** des zones d'habillage : clair, sombre, couleur, flou de la vidéo.
- **Éléments fixes** : cadre, bordure, logo, pseudo, barre de progression, filigrane.
- **Image filmée** : étalonnage (chaud, froid, contrasté, désaturé), grain, lumière. Décrit
  seulement : le monteur ne retouche pas l'image du visage.

## 8. Le son

Source : **le client**. Tu ne l'entends pas, l'outil ne le mesure pas. `meta.json` → `musique`
donne au mieux le son déclaré par la plateforme. Tu notes ce que le client répond à la question
du §3 de `mode-style.md`.

## 9. L'ouverture et la fin

- **0 à 3 s** : ce qui arrête le pouce, image par image (visage expressif, résultat montré
  d'abord, texte accroche, mouvement). Voir aussi `grille-analyse.md`, « Hook visuel ».
- **Fin** : appel à l'action affiché (mot-clé, flèche vers les commentaires), écran de fin, logo,
  vidéo qui boucle sur son début.

---

## Pièges

| Piège | Pourquoi c'est faux |
|---|---|
| Recopier des moments au lieu de règles | la vidéo du client n'a pas les mêmes phrases : on applique la règle à ses moments à lui |
| Faire plus que l'original | jamais plus de zooms, d'animations, de bruitages ni un visage plus gros que dans la vidéo : un style se reconnaît à sa retenue autant qu'à ses effets |
| Mettre un fondu là où l'original coupe sec | les coupes sèches font partie du style |
| Croire le rythme d'après les seules coupes franches | zooms, textes et illustrations changent l'image sans couper |
| Nommer une police au jugé | « proche de Montserrat Black » vaut mieux qu'un faux nom ; le client peut donner la vraie |
| Lire l'animation d'un sous-titre sur une image fixe | seule la rafale montre s'il arrive mot par mot |
| Prendre la couleur du décor pour l'accent | vérifie sur l'image ce que la couleur habille |
| Dire qu'il y a une musique ou des bruitages | tu n'entends pas : c'est au client de le dire |
| Promettre l'identique | ce que Monteur IA ne fait pas se dit, avec l'équivalent |
| Reprendre la signature de l'auteur | logo, pseudo, filigrane, visuels maison, musique : on décrit, on ne reprend pas |
