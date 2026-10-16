# Modèle de `style.md`

La fiche complète, relue au montage (et copiée dans `brand/style-montage.md` si le client la garde
comme son style). Elle se suffit : quelqu'un qui n'a pas vu la vidéo doit pouvoir monter dans ce
style. Les titres restent ; une dimension sans objet le dit en quelques mots (« Aucune transition :
coupes sèches seulement. »). Langue : celle du client.

```markdown
# Reel Cloneur™ · style de montage

**D'après :** {plateforme} · {@compte, « fichier », ou « ta vidéo »} · {durée} s · {format : vertical 9:16…}
**La signature :** {2 ou 3 phrases : ce qu'on reconnaît en une seconde.}
**Les gestes signature :** {3 à 5 règles courtes, les plus reconnaissables d'abord.}

> On reprend la manière de monter, jamais la signature de l'auteur (logo, nom, filigrane, visuels
> maison, musique, images). {Sa propre vidéo : « C'est ta vidéo : tout est à toi. »}

## 1. Le rythme
- **Changements d'image :** {un toutes les ~x s ; x coupes sur les 5 premières secondes, puis…}
- **Silences et respirations :** {tout est serré, aucune pause / quelques pauses gardées sur…}
- **Ce qui fait le rythme entre deux coupes :** {zooms, animations, textes qui arrivent…}
- **Chez toi :** {coupes serrées comme ça ; un changement d'image toutes les ~x s}

## 2. Le cadrage
- **Visage :** {plein écran / en bas, une image au-dessus / alternance : quand}
- **Zooms :** {sur quoi, à quel moment (mot fort, chute), serré ou léger, sec ou progressif}
- **Chez toi :** {cadrage principal ; alternance ; zooms}

## 3. Les sous-titres
- **Police :** {famille reconnue ou description : bâton très gras, condensée, arrondie… ; « à confirmer » si doute}
- **Allure :** {bandeau plein / contour / plaque / ombre / souligné / texte seul} · couleur du texte {hex} · fond {hex}
- **Casse et taille :** {majuscules ou non ; grande, moyenne, discrète}
- **Mots par sous-titre :** {2 à 3 ; une ou deux lignes}
- **Place :** {centre, jointure entre les deux images, bas…}
- **Comment ils apparaissent :** {d'un bloc, mot par mot, mot prononcé surligné en {couleur}, petit saut…} (rafale « sous-titres »)
- **Mots mis en valeur :** {lesquels (chiffres, noms), comment : autre couleur, plus gros, emoji}
- **Chez toi :** {réglage le plus proche ; ce qui ne se fera pas à l'identique}

## 4. Les textes et animations à l'écran
- **Ce qu'on voit :** {titres, mots-clés, schémas, logos, captures, emojis, flèches…}
- **Quand et combien :** {sur l'accroche seulement / toutes les ~x s / sur les chiffres}
- **Place et taille :** {au-dessus du visage, plein écran, petit coin…}
- **Comment ça bouge :** {arrive en glissant, rebondit, s'écrit…}
- **Chez toi :** {ce que le monteur fera : densité, type, place}

## 5. Les images d'illustration
- **Ce que c'est :** {captures d'écran, plans filmés, images de banque, vidéos générées…}
- **Fréquence et place :** {plein écran x s / au-dessus du visage / jamais}
- **Chez toi :** {ce qu'il te faudra fournir ou filmer, ce que le monteur trouvera}

## 6. Les transitions
- {coupe sèche partout / glissé / zoom brusque / flash blanc / flou… et où} (rafales « coupe »)
- **Chez toi :** {équivalent}

## 7. Les couleurs et l'habillage
- **Palette :** fond {hex} · accent {hex} · texte {hex} (relevés avec l'outil « couleurs »)
- **Allure générale :** {claire ou sombre, vive ou sobre ; cadre, bordure, barre de progression, logo…}
- **Image filmée :** {étalonnage, grain, teinte : décrit, non reproduit}
- **Chez toi :** {couleurs reprises ou les tiennes}

## 8. Le son (d'après le client)
- **Musique de fond :** {ce qu'il a dit, ou « non précisé »} · son déclaré par la plateforme : {…}
- **Bruitages :** {ce qu'il a dit}

## 9. L'ouverture et la fin
- **Les 3 premières secondes :** {ce qui arrête le pouce, image par image}
- **La fin :** {appel à l'action affiché, écran de fin, logo, boucle…}

## Ce qui ne se fera pas à l'identique
- {point} → {équivalent chez Monteur IA}

## Ce qu'on laisse de côté
- {la signature de l'auteur : logo, pseudo, filigrane, visuels maison, musique ; un effet qu'il ne
  veut pas} : {pourquoi, en quelques mots}

---

## Pour Monteur IA

*(Bloc technique pour le montage : le client n'a pas besoin de le lire.)*

- `visual` : {stylePreset si l'un colle, sinon bg / accent / text en hex} · fontCaptions {…} ·
  captionsSkin {block | outline | plate | shadow | underline} · captionsCase {upper | asis} ·
  captionsLines {1 | 2} · captionsPosition {…} · captionsSize {px, si différent de 50}
- `montage.defaultLayout` : {split | faceplein} · alternance : {…}
- Dérush : coupes {serrées : padStart / padEnd proches de 0 | aérées}
- Préférences (4 à 6, une ligne chacune, telles qu'à écrire) :
  - « … »
- Sons : {musique : fichier du client ou aucune ; bruitages : où, combien}
- Plafonds : jamais plus de zooms, d'animations ni de bruitages que l'original ; les règles
  s'appliquent aux moments de la vidéo du client, pas au minutage de l'original.
- Contrôle après l'export : `python3 tools/cloner_reel.py <vidéo exportée> --style`, puis comparer
  le rythme (plan le plus fréquent, coupes par tranche de 5 s) à celui de cette fiche. Un écart de
  plus d'un quart : une règle a été oubliée, la retrouver avant de livrer.
- Source : `clones/{dossier}/` (images, rafales, style.json).
```

## Le message au client (250 à 400 mots)

```markdown
**En bref.** {2 ou 3 phrases : la signature du style.}

**Ce que je reprends**
- {Rythme : un changement d'image toutes les 2 secondes environ, coupes très serrées.}
- {Cadrage : ton visage en plein écran sur l'accroche, puis en bas avec une image au-dessus.}
- {Sous-titres : majuscules, 2 à 3 mots, bandeau jaune, texte noir très gras, au milieu.}
- {Animations : un logo ou un schéma à chaque outil cité, jamais de gros titre.}
- {Sous-titres : le mot prononcé s'allume en jaune, comme dans sa vidéo.}
- {Transitions : coupes sèches, un zoom rapide sur les mots forts.}
- {Couleurs : fond presque noir, accent jaune.}

**Ce qui ne se fera pas à l'identique** *(seulement s'il y en a)*
- {La police de ses titres : Inter, la plus proche ; avec le fichier de la tienne, ce sera la vraie.}

**Le son.** Je n'entends pas la vidéo : il y a une musique de fond ? Des bruitages (un souffle sur
les changements de plan, un « pop » quand un texte apparaît) ?

{Selon ce qu'il a dit (mode-style.md, §3, point 5), UNE de ces trois fins :}
{Vidéo brute fournie :} Je monte ta vidéo dans ce style, pour elle seulement : tes réglages ne
bougent pas. Quand tu l'auras validée, je te demanderai si on le garde pour tes prochaines vidéos.
{« Garde-le » déjà dit :} **Je garde tout ça ?**
{Sinon :} Envoie-moi une vidéo brute : je la monte dans ce style, pour elle seulement, et tu me
diras ensuite si on le garde. Et si c'est déjà ton style, dis « garde-le » : je l'enregistre tout
de suite.

*Le détail est dans `clones/{dossier}/style.md`.*
```
