# Premier montage : qualité immédiate avec le style Papier

Lire avant un premier montage ou une section utilisant le style de départ. Complète la méthode
`montage-talking-head.md`, sans remplacer ses validations ni son ordre.

## Parcours

L'installation est vérifiée, une vidéo a été fournie : annoncer le style Papier en une phrase,
puis préparer le dérush. Aucun questionnaire de marque, de police ou de matériel n'est requis.
Le cadrage est adapté à la vraie vidéo par l'agent. Faire valider le dérush, puis une première
section représentative avant de décliner le montage. Montrer le résultat, pas les commandes.

Demande simple : « Voilà le début monté. Le rythme et l'habillage te plaisent ? »
Le client peut répondre « continue » ou donner un retour en langage naturel. Ne pas ajouter une
étape de choix de presets. Après la première livraison, proposer la personnalisation une fois.

## Direction visuelle prête à utiliser

**Papier est un habillage éditorial abouti.** Le fond est blanc cassé, les formes et les labels
noirs, les sous-titres blancs sur bandeau noir. La vidéo du visage garde ses couleurs naturelles.
Toutes les valeurs proviennent des tokens du preset, jamais d'une identité inventée ou empruntée.

- **Composition :** le visage reste le repère. En split, le haut illustre une idée principale,
  avec un objet visuel dominant, des marges franches et quelques labels courts. En plein visage,
  garder le centre du visage dégagé et poser seulement les éléments utiles.
- **Hiérarchie :** un objet dominant, au plus deux niveaux secondaires. La différence d'échelle,
  les surfaces et l'espace créent le relief. Éviter la grille de trois cartes textuelles identiques.
- **Lisible sur téléphone :** la vidéo est vue sur un écran de téléphone, pas sur un 27 pouces.
  Suivre la hiérarchie du skill (§3, ×1,4 en vertical) : titre de section ≈ 64–70 px Black,
  labels 40–50 px, métadonnées 28 px minimum. **Rien sous 28 px.** Si ça ne rentre pas, mettre
  moins de texte, jamais du texte plus petit.
- **Contraste : l'encre d'abord.** Textes et formes qui portent le sens en `--brand-text`, contours
  francs (2–3 px) ; `--brand-muted` réservé à une métadonnée secondaire ; `--brand-surface` en aplat
  discret. Pas de contour pointillé gris, pas de texte gris sur gris. Texte sur accent =
  `--brand-contrast`. Ni glow ni dégradé coloré par défaut.
- **Sous-titres :** 2–3 mots, unités grammaticales intactes, police Inter Black livrée, bandeau
  noir dimensionné au texte. Se caler sur les vrais mots ; aucun mot sur le visage ou hors cadre.
- **Mouvement :** montrer une transformation compréhensible (séparer, relier, classer, comparer),
  synchronisée avec la parole. Entrées courtes de 0,25–0,4 s, arrêt net mais souple, temps de lecture.
  Un changement visuel à chaque idée, sans ajouter du mouvement perpétuel à une image déjà lisible.
- **Variété :** choisir les scènes selon le sens. Ne pas appliquer le même template à chaque phrase.
  L'exemple livré démontre un geste ; il ne dicte ni le sujet ni les timings des vrais montages.

## Traduire les idées en images

| Idée entendue | Piste visuelle |
|---|---|
| Enlever les hésitations | Une forme d'onde avec des trous, puis des prises assemblées |
| Comparer deux méthodes | Deux chemins qui aboutissent à leurs résultats, quelques labels |
| Décrire un processus | Objets reliés, le focus passe d'une étape à la suivante |
| Montrer un résultat chiffré | Barres ou jauge proportionnelles aux chiffres réellement fournis |
| Montrer un outil | Capture réelle cadrée sur l'action, annotation discrète |

Aucun chiffre, faux témoignage ou logo inventé pour faire joli. Le texte du motion ajoute des
repères ; il ne recopie pas la voix et les sous-titres. Pas de gros titre plein écran.

## Référence exécutable

`compositions/exemple-section.html` est une section de 8 secondes à 1080×920 : une piste brute,
les silences identifiés, puis une piste montée. Elle utilise les polices locales, les tokens,
des SVG et une timeline GSAP déterministe. Pas de dépendance réseau ni de média payant.
C'est aussi la section-témoin à dupliquer : ses invariants [1]-[7] (commentés dans le fichier)
se gardent tels quels, seuls le sujet, les formes et les timings changent.
`compositions/captions.html` montre le bandeau. L'`index.html` livré est un aperçu : le bas est une
zone d'attente, pas un exemple de cadrage. Le vrai master (calque visage, voix, pièges) est généré
par `tools/build_master.py` ; calibrer le cadrage depuis la vraie vidéo.

Avant de composer une nouvelle scène, consulter le registry comme prévu par le skill, puis adapter
les blocs retenus à ce langage visuel. L'exemple local reste disponible sans téléchargement.

## Vérifier le résultat avant de le montrer

- Inspecter des images au début, au milieu et à la fin de chaque nouvelle section.
- Vérifier le mouvement par lecture ou par échantillons temporels : un beau arrêt sur image ne
  prouve pas que l'animation fonctionne. Aucun écran vide prolongé ni élément figé involontaire.
- Contrôler visage, sous-titres, contraste et marges au format téléphone.
- Faire les vérifications techniques du projet et regarder le rendu réel du calque.
- Ne jamais promettre « prêt à publier » si l'audio, le cadrage ou l'export n'a pas été vérifié.

La qualité vient de la précision des coupes, des visuels pertinents et de la lisibilité. Ajouter
une animation ou une couleur de plus ne compense pas un de ces points manquants.
