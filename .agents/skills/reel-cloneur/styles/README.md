# Les styles du catalogue

Onze styles de montage prêts à l'emploi, chacun repris d'un Reel public qui marche et déjà cloné,
construit et contrôlé sur une vraie vidéo. Le client les voit en vidéo dans la formation (module 2,
« Monte ta première vidéo ») et les demande par leur numéro, leur nom ou leur créateur :
« monte ma vidéo dans le style 4 », « le style Top outils », « le style de Dan Martell ».

> On reprend la manière de monter de ces créateurs, jamais leurs vidéos, leurs mots ni leur
> signature (logo, musique, images). Les couleurs se changent comme le reste.

| N° | Style | D'après | Idéal pour | En plus de la vidéo brute |
|---|---|---|---|---|
| 1 | Top outils | @aiwithsachi | présenter plusieurs outils, applis ou sites d'affilée | rien (les logos se trouvent seuls) |
| 2 | Liste en cartes | @nocode.joshua | une liste face caméra, chaque idée sur une carte posée sur le décor | rien |
| 3 | Liste de conseils | @BrockMesarich | énumérer 3 à 6 conseils, outils ou erreurs, appel à l'action à la fin | rien |
| 4 | Le classement | @mattfarmerai | un top ou un classement numéroté | rien |
| 5 | Méthode en schéma | @realskytan | une méthode ou un tutoriel en 3 à 6 étapes | rien |
| 6 | Démo sur ordinateur | @KevinStratvert | montrer un outil, un site ou une appli sur ordinateur | captures ou lien du site |
| 7 | Annonce choc | @danmartell | annoncer une nouveauté ou un conseil fort en 30 à 45 s | rien |
| 8 | Réponse à un abonné | Ali Abdaal | répondre à la question d'un abonné | le texte de la question |
| 9 | Collage illustré | Ali Abdaal | expliquer une idée façon carnet de collage | rien (images libres ou tirées de sa vidéo) |
| 10 | Avis produit | @ugc.rachelll | présenter un produit testé, devant sa page | le lien de la page, ses vrais avis s'il en a |
| 11 | Mon histoire | @anyway.julia | raconter son parcours façon carnet visuel | 5 à 10 de ses photos (sinon tirées de sa vidéo) |

Les styles 10 et 11 détourent la personne sur l'ordinateur du client (quelques minutes, modèle de
170 Mo téléchargé la première fois) : dis-le-lui avant de lancer.

## Appliquer un style du catalogue

Chaque dossier `NN-nom/` est un **kit** : `style.md` (la fiche, à suivre comme une fiche clonée),
`reel.config.json` (couleurs, polices, sous-titres), `compositions/` (les pièces signature, déjà
construites), et parfois `outils/` (un script propre au style, que sa fiche explique).

1. **Le bon style.** Il donne un numéro, un nom ou un créateur : prends ce kit. Il hésite (« je ne
   sais pas », « lequel tu me conseilles ? ») : lis ce que dit sa vidéo et propose 2 ou 3 styles
   du tableau, numéro et nom, chacun avec la raison en une ligne ; les exemples en vidéo sont dans
   la formation, module 2. Sa vidéo ne colle pas au style choisi (un « Top outils » sans outil
   cité) : dis-le en une ligne et propose le plus proche ; s'il maintient, tu montes dans le sien.
2. **Comme un style cloné, pour cette vidéo seulement** : suis `references/mode-style.md`, §4,
   « Sur une vidéo », avec le kit à la place de `clones/<dossier>/` :
   - le `--brief` du nouveau Reel pointe vers la fiche, vue depuis le Reel :
     `../../.claude/skills/reel-cloneur/styles/<NN-nom>/style.md` ;
   - `reel.config.json` du kit à la racine du Reel, plus le recadrage que la fiche fait calculer
     sur sa vidéo (`montage`) ; puis `npm run sync` depuis le dossier Monteur IA ;
   - les `compositions/` du kit dans `compositions/` du Reel, une copie par section, remplies
     selon leur en-tête ; les `outils/` du kit dans `tools/` du Reel s'il y en a ;
   - tout le reste du §4 vaut : la fiche passe avant les règles de base, les données que la vidéo
     ne dit pas se demandent, le contrôle avant de livrer compare le rythme par tiers à celui de
     la fiche (pas de comparaison côte à côte : l'original n'est pas fourni, les pièces du kit en
     tiennent lieu).
3. **Après sa validation** : « On garde ce style pour tes prochaines vidéos ? ». Oui : §4, « Pour
   toutes ses vidéos », avec le kit (fiche dans `brand/style-montage.md`, pièces et réglages dans
   `brand/style-montage/`). Ses retouches s'ajoutent par-dessus, comme pour tout style.

Les polices des styles sont livrées avec Monteur IA (`assets/fonts/`, licences OFL) et nommées dans
`reel.config.json` (`fontDisplay`, `fontBody`, `fontCaptions`, `fontAccent`) : rien à installer.
