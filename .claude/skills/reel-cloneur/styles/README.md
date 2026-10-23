# Les styles du catalogue

Onze styles de montage prêts à l'emploi, chacun repris d'un Reel public qui marche et déjà cloné,
construit et contrôlé sur une vraie vidéo. Le client les voit en vidéo dans la formation (module
« Templates », rappelés au module 2 « Monte ta première vidéo ») et les demande par leur numéro,
leur nom ou leur créateur : « monte ma vidéo dans le style 4 », « le style Hors cadre », « le style
de Dan Martell ».

**Un style est un look, pas un sujet.** Il se choisit à ce qu'on voit (sous-titres, cadrage,
animations, couleurs, rythme) et se monte sur n'importe quelle vidéo : une histoire, un avis, une
actu, un tuto, une liste. Ce qui suivait le sujet de l'original (un classement, une question
d'abonné, une page produit) s'adapte au sien : section « Sur un autre sujet » de chaque fiche.

> On reprend la manière de monter de ces créateurs, jamais leurs vidéos, leurs mots ni leur
> signature (logo, musique, images). Les couleurs se changent comme le reste.

| N° | Style | Ce qu'on voit | D'après | Souvent utilisé pour | En plus de la vidéo brute |
|---|---|---|---|---|---|
| 1 | Fenêtre orange | mot géant au-dessus de la tête, fenêtre à bord orange sur le torse, flash blanc | @aiwithsachi | plusieurs outils ou sites d'affilée | rien (logos et images se trouvent seuls) |
| 2 | Carte crème | grande carte crème au-dessus de la tête, remplacée à chaque idée ; un mot de sous-titre | @nocode.joshua | une liste face caméra | rien |
| 3 | Hors cadre | fond crème, fenêtre arrondie, tête qui dépasse ; grand « #1 » doré à chaque partie | @BrockMesarich | énumérer des conseils | rien |
| 4 | Karaoké couleur | écran partagé, sous-titres en capitales au mot allumé en couleur | @mattfarmerai | un top, un classement | rien |
| 5 | Schéma vivant | schéma en barres de couleur qui se dessine au-dessus de la tête, frise de progression | @realskytan | une méthode en étapes | rien |
| 6 | Plongée écran | plongée dans un ordinateur sur fond bleu vif, mot dit dans une pastille rouge | @KevinStratvert | montrer un outil ou un site | des captures ou images de ce dont il parle, ou les pages publiques à capturer |
| 7 | Titre explosif | titre géant qui explose, mot manuscrit lumineux, tuiles épinglées autour de la tête | @danmartell | annoncer une nouveauté | rien |
| 8 | Gros plan | carte d'ouverture tapée, plan très serré, plaque claire, phrase clé au-dessus de la tête | Ali Abdaal | répondre à une question | la phrase de la carte d'ouverture (sinon sa première phrase) |
| 9 | Collage | papier déchiré, collages plein écran, machine à écrire, traits de craie | Ali Abdaal | expliquer une idée | rien (images libres ou tirées de sa vidéo) |
| 10 | Incrustation | détouré devant une page qui bouge, un mot de sous-titre au milieu, carte flottante | @ugc.rachelll | présenter un produit testé | une page ou des images liées au sujet (sinon tirées de sa vidéo) |
| 11 | Autocollant | détouré en autocollant sur bleu ciel, typo géante empilée, scènes d'objets | @anyway.julia | raconter un parcours | 5 à 10 photos liées au sujet (sinon tirées de sa vidéo) |

Pour tous les styles, en plus de cette colonne : ce que sa voix montre sans le dire (« voici combien
ça m'a coûté », « regarde le résultat ») se demande, la capture ou le chiffre, dans la même question
groupée ; sans réponse, la carte se fait sans chiffre, jamais avec un chiffre inventé.

Les styles 3, 9, 10 et 11 détourent la personne sur l'ordinateur du client, gratuitement (quelques
minutes, modèle de 170 Mo téléchargé la première fois) : dis-le-lui avant de lancer.

## Appliquer un style du catalogue

Chaque dossier `NN-nom/` est un **kit** : `style.md` (la fiche, à suivre comme une fiche clonée),
`reel.config.json` (couleurs, polices, sous-titres), `compositions/` (les pièces signature, déjà
construites), et parfois `outils/` (un script propre au style, que sa fiche explique).

1. **Le bon style.** Il donne un numéro, un nom ou un créateur : prends ce kit, quel que soit le
   sujet de sa vidéo. **Ne déconseille jamais un style parce que sa vidéo ne ressemble pas à
   l'original** : c'est un look, tu adaptes ce qui suivait le sujet (section « Sur un autre sujet »
   de la fiche). Il hésite (« je ne sais pas », « lequel tu me conseilles ? ») : demande-lui ce
   qu'il aime voir (sous-titres, cadrage, animations, couleurs), puis propose 2 ou 3 styles de la
   colonne « Ce qu'on voit » qui y répondent, numéro et nom, chacun avec la raison en une ligne ;
   le sujet de sa vidéo n'est qu'un indice en plus (colonne « Souvent utilisé pour »). Les
   exemples en vidéo sont dans la formation, module « Templates ».
   À la première vidéo du client (question du style, section « Première vidéo » des consignes),
   demande dans un seul message ce que la colonne « En plus de la vidéo brute » réclame et ce que sa
   voix montre sans le dire, puis monte d'une traite comme le veut cette section.
2. **Comme un style cloné, pour cette vidéo seulement** : suis `references/mode-style.md`, §4,
   « Sur une vidéo », avec le kit à la place de `clones/<dossier>/` :
   - le `--brief` du nouveau Reel pointe vers la fiche, vue depuis le Reel :
     `../../.claude/skills/reel-cloneur/styles/<NN-nom>/style.md` ;
   - `reel.config.json` du kit à la racine du Reel, plus le recadrage que la fiche fait calculer
     sur sa vidéo (`montage`) ; puis `npm run sync` depuis le dossier Monteur IA ;
   - les `compositions/` du kit dans `compositions/` du Reel, une copie par section, remplies
     selon leur en-tête ; les `outils/` du kit dans `tools/` du Reel s'il y en a ; retire
     `compositions/exemple-section.html`, la démo que `tools/nouveau_reel.py` y a posée ;
   - une partie de sa vidéo qui commence au milieu d'une prise (fréquent sur un récit) : partage la
     prise par un raccord au creux de voix juste avant son premier mot (skill derush §5, raccord),
     puis relance `tools/cut_boundaries.py` : la vidéo ne change pas, seul `<cut>_cuts.json` gagne
     la frontière (les sous-titres s'en accommodent seuls) ;
   - sa vidéo ne ressemble pas à l'original (une histoire dans un style né d'un classement) : la
     section « Sur un autre sujet » de la fiche dit ce que deviennent les pièces liées au sujet,
     et comment relire son bloc technique ; le reste du look ne change pas ;
   - tout le reste du §4 vaut : la fiche passe avant les règles de base, les données que la vidéo
     ne dit pas se demandent, le contrôle avant de livrer compare le rythme par tiers à celui de
     la fiche (pas de comparaison côte à côte : l'original n'est pas fourni, les pièces du kit en
     tiennent lieu). Au contrôle du rythme, chaque saut net d'un élément compte comme un changement
     d'image : ce qui bouge pendant une image bouge en continu, jamais par pas.
3. **Après sa validation** : « On garde ce style pour tes prochaines vidéos ? ». Oui : §4, « Pour
   toutes ses vidéos », avec le kit (fiche dans `brand/style-montage.md`, pièces et réglages dans
   `brand/style-montage/`). Ses retouches s'ajoutent par-dessus, comme pour tout style. Il vaut
   pour tous ses sujets : la section « Sur un autre sujet » de la fiche suit le style.

Les polices des styles sont livrées avec Monteur IA (`assets/fonts/`, licences OFL) et nommées dans
`reel.config.json` (`fontDisplay`, `fontBody`, `fontCaptions`, `fontAccent`) : rien à installer.
