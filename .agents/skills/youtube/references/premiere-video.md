# Première vidéo YouTube : brief de style, montage d'une traite, débrief

La première vidéo YouTube d'un dossier (`youtube.firstVideoDone` pas `true`) suit le même principe
que la première vidéo d'un Reel : le client découvre son montage complet, puis dit ce qu'il aurait
fait autrement. Une seule différence : **un brief court avant**, parce qu'une vidéo YouTube engage
plus de choix visibles qu'un Reel, et qu'on ne remonte pas 15 minutes pour un détail de goût.

## 1. Le brief (un seul message, avant le dérush)

- **Ce qui est déjà connu ne se redemande pas.** Couleurs, polices, style des textes viennent de
  `brand.config.json` (ceux de ses Reels, le même univers de marque). Un style encore « Papier »
  non choisi reste Papier : on ne le change pas ici.
- Trois questions au plus, chacune avec son défaut, pour qu'un « fais comme tu veux » suffise :

> « Avant de monter ta vidéo YouTube, trois choix rapides (réponds juste par les numéros, ou
> « comme tu veux ») :
> 1. **Le style** : sobre (surtout toi à l'écran, quelques panneaux), dynamique (un visuel
>    toutes les 10 à 20 s, les logos des marques citées, du plein écran sur les temps forts) ou pédagogique (des schémas qui se
>    construisent à côté de toi). Par défaut : dynamique.
> 2. **Une chaîne que tu aimes** pour le montage ? (son nom ou un lien, facultatif)
> 3. **Une musique de fond** discrète ? Si oui, glisse le fichier ici. Par défaut : sans. »

- Une chaîne de référence donnée : ne télécharge rien ; retiens ce que le client en dit (« comme
  Ali Abdaal », « comme Micode ») et traduis-le en réglages de la doctrine (densité, cadres, place
  du visage), sans copier un habillage reconnaissable.
- Écris dans `brand.config.json` → `youtube` : `style` (`sobre`, `dynamique`, `pedagogique`),
  `musicFile` (copié dans `assets/music/`), `styleChosen: true`. Une préférence explicite (« jamais
  de plein écran ») va dans `youtube.preferences`, une phrase par règle. Puis `node scripts/sync.mjs`
  depuis le dossier Monteur IA.
- S'il ne répond qu'au premier message par sa vidéo : prends les défauts, dis-le en une phrase, et
  monte.

## 2. Le montage d'une traite

Annonce une fois : « Je m'occupe de tout le montage : coupes, cadrages, panneaux, textes, sons.
Pour une vidéo de cette durée, compte une à deux heures de travail de mon côté, plus l'export.
Tu peux faire autre chose. Ensuite tu me diras tout ce que tu aurais fait autrement. »

- Toutes les étapes du parcours (SKILL.md §2), **sans arrêt de validation** : dérush, plan,
  montage, sons, export, finalisation. Les **contrôles automatiques restent obligatoires**
  (re-transcription, écarts du dérush, alertes de `sections.py`, `npm run check`, snapshots,
  `finaliser.py`) : tu valides toi-même ce que le client aurait validé.
- Voix brute mise au niveau (pas d'Adobe Podcast : il demande une action du client, proposée au
  débrief). Sons : sobres (doctrine §6). Musique : celle du brief, sinon aucune.
- Tiens `work/suivi.md` à jour à chaque étape franchie, une ligne de nouvelles au client à chaque
  étape. Ne t'arrête que sur un vrai blocage, avec une seule consigne.
- Dans l'app : « Clique sur Export » quand le montage est prêt, puis `finaliser.py` sur son export.

## 3. Le débrief (après la livraison)

> « Ta vidéo est prête, dans tes Téléchargements (« <nom>.mp4 »), au bon niveau sonore pour
> YouTube. Regarde-la et dis-moi tout ce que tu aurais fait autrement, avec le moment si tu peux
> (« à 2:30… »). Tout se règle :
> - **le rythme** : plus serré, plus aéré, un passage à couper ;
> - **les cadres** : plus ou moins de zooms, plus de plans où tu es seul à l'écran ;
> - **les panneaux et graphiques** : plus, moins, plus simples, d'autres couleurs ;
> - **les textes à l'écran** : plus, moins, ou des sous-titres partout ;
> - **le son** : ta voix plus propre (deux gestes de ton côté), une musique, plus ou moins de
>   bruitages. »

- Applique ses retours à cette vidéo, réexporte, refinalise.
- Reformule chaque préférence en une règle courte et montre-la-lui ; après son OK, écris-les dans
  `youtube.preferences`, passe `youtube.firstVideoDone` à `true`, puis `node scripts/sync.mjs`
  (elles apparaissent dans les consignes de chaque vidéo YouTube).
- Ensuite seulement : la publication (`references/publication.md`).

Dès la deuxième vidéo : brief sauté, parcours normal avec ses validations (plan, revue), les
préférences apprises appliquées d'office.
