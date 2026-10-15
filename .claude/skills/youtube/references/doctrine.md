# Doctrine du montage YouTube face caméra (16:9)

Les règles qui font qu'une vidéo face caméra de 5 à 20 minutes se regarde jusqu'au bout. Elles
viennent des montages par IA qui ont le mieux marché en 2026 (kits HyperFrames de Nate Herk,
claude-youtube-editor, video-use, le skill talking-head-recut de HyperFrames, les retours publiés
sur X par ceux qui montent leurs vidéos avec Claude ou Codex) et des règles officielles de YouTube.
Ce sont des **points de départ** : les préférences du client (`youtube.preferences`) priment.

Avant chaque plan de montage, se demander : **« à quel moment quelqu'un décroche, et qu'est-ce qui
change à l'écran juste avant ? »**

---

## 1. Rythme du dérush

- **Le rythme des Reels** : environ 0,10 s entre deux phrases, les marges du bloc `derush`
  (retour terrain : 0,3 à 0,5 s de respiration sonnait lent et peu naturel sur une voix lue au
  prompteur). Un créateur qui veut garder sa respiration règle `youtube.derush` (0,10 / 0,25 :
  0,3 à 0,5 s entre deux phrases).
- **Couper entre les phrases, jamais dedans.** Un « euh » qui court dans le mot suivant reste :
  le couper abîme les mots autour. Ne jamais accélérer la voix.
- **Prises multiples** : la dernière prise propre de chaque phrase ; une phrase doublée → couper la
  première. Les consignes dites à voix haute (« je la refais ») partent.
- **Fin de phrase** : garder la retombée de la voix ; une fin de voix très basse se rallonge juste
  assez pour ne pas la couper (skill `derush`).
- **Début** : la parole démarre tout de suite. Ni intro animée, ni « salut à tous » de 10 s.

## 2. Les cadrages (et quand les utiliser)

Quatre formats de section (`tools/sections.py`) :

| Format | Ce qu'on voit | Pour | Durée typique |
|---|---|---|---|
| `face` | le créateur plein cadre | parler, raconter, convaincre, le hook, les phrases perso | prises de 2 à 10 s, plan large |
| `cote` | le créateur glisse d'un quart d'écran, un **panneau** entre de l'autre côté | expliquer, lister, comparer, chiffrer, une étape | **15 à 40 s** : tout le sujet |
| `over` | le créateur plein cadre + un élément **par-dessus** (fond transparent) | un nom, un outil cité (son logo près de la tête), un bandeau, un chiffre | 2 à 8 s |
| `full` | un **plan plein écran** (motion, capture, B-roll) | montrer : une démo, un résultat, une thèse forte, une transition de chapitre | **3 à 12 s** |

**Zoom avec parcimonie (punch-in).** Plan large par défaut (`youtube.punchIn` = `parcimonie`) ;
le serré (1,3×) seulement sur ce qui compte : une chute, un mot clé, l'annonce d'une offre, de
préférence en raccord pile sur le mot. Le **très serré** (1,55×) est rare. Retour terrain : au
rythme des Reels (une coupe toutes les 1,5 à 2 s), un zoom / dézoom à chaque coupe fatigue vite ;
les incrustations, le panneau et les plans plein écran font le rythme visuel. Pas de zoom
progressif : un changement sec. `"punchIn": "alterne"` remet un cadre différent à chaque coupe
(une vidéo aux phrases longues, coupes espacées).

**Changer de cadre sur un mot** (« comme ça », « offert », la chute) sans coupe : la prise est
partagée en deux au dérush, en un **raccord** (deux îlots qui se touchent, skill `derush` étape 5) ;
le son et l'image restent d'un seul tenant, seul le cadre change, pile avant le mot. Au plus deux
ou trois par vidéo : c'est un appui, pas un rythme.

**Le glissement sur le côté** (`cote`) est un seul geste : le créateur glisse et le panneau entre
en même temps (0,6 s, `power2.inOut`). Le master le fait depuis et vers le cadre large ; la prise
qui précède ou suit un panneau passe donc d'office en large quand sa section alterne les cadres.
Une prise au cadre imposé (`"cadre": "serre"`) le garde : la coupe passe en large et le glissement
part aussitôt. Panneau à droite par défaut
(`youtube.panneau`), à gauche si le créateur est décentré vers la droite au tournage.

**Ne jamais couvrir** : le hook (les premières secondes, face caméra), une phrase personnelle,
émotionnelle ou d'opinion, une chute. Au moins **2 s de visage** entre deux plans plein écran.
Le visage est à l'écran 40 à 70 % du temps selon le style (`youtube.style`).

## 3. Densité : ce qui change à l'écran

- **Un changement visuel toutes les 15 à 30 s** (panneau, incrustation, plein écran, texte
  d'appui) ; jamais plus de 45 s sans rien (`tools/sections.py` alerte). Plus dense dans la
  première minute (un élément visuel avant 10 s), plus posé ensuite.
- **Une carte par sujet, pas par phrase** : un panneau vit tout le temps du sujet (20 à 40 s) et se
  **construit** en suivant la voix (une ligne s'ajoute quand elle est dite, la ligne dont on parle
  s'allume). Un texte d'une ligne qui reste plus de 8 s ennuie ; une carte de plus de 15 s doit
  avoir plusieurs étapes.
- **Quand poser un visuel** (déclencheurs dans le texte) : « je vais te montrer », un outil ou un
  site nommé, un chiffre, une liste (« trois raisons »), une comparaison (« avant / après »), une
  étape d'un processus, un résultat.
- **Ne jamais 3 ou 4 plans du même type d'affilée.** Chaque changement doit aider à comprendre ;
  une animation qui ne dit rien de plus que la voix ne compte pas.
- Repère de quantité (talking-head-recut) : 3 à 10 min → un graphique toutes les 12 à 20 s ;
  10 à 30 min → toutes les 20 à 35 s ; ×0,7 si le contenu est dense (chiffres, listes), ×1,5 s'il
  est narratif.

**Styles de départ** (`youtube.style`, choisi au brief) :

| Style | Visage | Graphiques | Cadres |
|---|---|---|---|
| `sobre` | ~70 % | panneaux et incrustations, peu de plein écran | large, un serré de temps en temps |
| `dynamique` (défaut) | ~55 % | un visuel toutes les 10 à 20 s, logos des marques citées, plein écran motion sur chaque temps fort | large, serré sur les mots clés (raccords) |
| `pedagogique` | ~45 % | panneaux longs qui se construisent, schémas, captures | large surtout, le serré pour insister |

## 4. Textes à l'écran

- **Pas de sous-titres mot à mot en continu** (format Reel). YouTube a ses sous-titres : on livre
  un **fichier SRT** (`exports/sous-titres.srt`) que le client téléverse. Sous-titres incrustés
  seulement si le client le veut (`youtube.sousTitres = "partout"`).
- **Textes d'appui** : 1 à 3 par minute, **1 à 4 mots**, posés pile sur les mots prononcés : un
  chiffre (« 100 % GRATUIT »), un nom (« LOGO DESIGN SKILL »), l'idée-clé d'une partie. Jamais une
  phrase entière, jamais deux à la fois, jamais sur un plein écran (le texte va dans le graphique).
- **Rien n'apparaît avant d'être dit** ; un graphique peut entrer 0,2 s avant son mot, un texte
  d'appui sur le mot.
- Rédaction des cartes : compréhensible en moins d'une seconde ; un titre et une sous-ligne, ou une
  liste de 2 à 4 éléments ; environ 20 mots par carte au plus. Pas de tiret long.
- **Motion first** : comme pour les Reels, un schéma, une icône, un vrai logo, une capture valent
  mieux qu'une phrase écrite. Le vrai logo de toute marque citée (skill `thesvg`).

## 5. B-roll et captures

Ordre de préférence : 1) une vraie vidéo de la chose citée ; 2) une vraie capture d'écran zoomée
sur la partie dont on parle, avec le curseur ; 3) une maquette d'interface animée ; 4) une vidéo
générée par IA ; 5) un recadrage court d'une vraie page. **Chaque plan bouge** (une image fixe :
zoom très lent, ~1,5 %/s). Plans de 2 à 4 s, jamais moins de 1,2 s. Ne jamais inventer un chiffre
ou un résultat pour illustrer. Un média qui ne remplit pas le 16:9 : fond flou (motion-design §5.6).
Le son du rush continue sous le B-roll.

## 6. Son

- **Musique** : plus discrète que dans un Reel (`youtube.musicDb`, -30 dB par défaut), environ
  11 dB sous la voix. Énergie dans le hook, discrète ensuite ; on peut la couper sur un passage
  d'explication dense et la relancer à la partie suivante. Pas de musique sur l'écran de fin si on
  y parle.
- **SFX rares** : sur les gestes qui changent l'écran (glissement, plein écran, révélation d'un
  chiffre), **pas sur chaque coupe**. Sons doux (air, clic sec, papier), jamais de laser ni de
  whoosh à répétition. Un son « mème » 1 à 2 fois par vidéo au plus, sur une vraie chute.
- **Niveau final -14 LUFS**, crêtes sous -1 dBTP, mesuré sur le fichier final : `tools/finaliser.py`
  après chaque export (le rendu HyperFrames ne monte le niveau que de la marge de crête du mixage).

## 7. Structure : hook, relances, chapitres, fin

- **Hook (0 à 30 s)** : tenir tout de suite la promesse du titre et de la miniature, face caméra,
  le cadre qui change vite (coupes toutes les 3 à 5 s). Un premier visuel avant 10 s.
- **Sommaire** (optionnel) : une carte « Dans cette vidéo » après le hook, qui annonce les parties
  (une boucle ouverte qu'on ferme à la fin).
- **Relances** : un temps fort vers 3 min et vers 6 min (un plein écran, un chiffre, une démo), et
  une petite relance toutes les 2 à 3 min (changement de cadre + texte d'appui + respiration).
- **Chapitres** : une carte de section (plein écran court, 2 à 4 s, ou un panneau) à chaque
  chapitre ; `"chapitre"` dans `sections.py` ; 00:00, au moins 3, chacun ≥ 10 s.
- **Fin** : arriver au dénouement puis finir net, sans outro qui traîne. Les **5 à 20 dernières
  secondes** accueillent l'écran de fin de YouTube (vidéo suivante, abonnement) : le créateur peut
  continuer de parler, mais rien d'important à l'image dessous.

## 8. Zones de sécurité (16:9)

- **Zone d'action** : 5 % des bords (`var(--brand-yt-safe-x)` = 96 px, `--brand-yt-safe-y` = 54 px).
- **Zone titre** : 10 % (`--brand-yt-title-x` = 192 px, `--brand-yt-title-y` = 108 px) pour tout
  texte et tout chiffre clé. En panneau 960×1080, la marge extérieure est la zone titre, la marge
  côté visage peut être plus courte (~72 px).
- **Barre de lecture** : rien de permanent dans les **150 px du bas** (`--brand-yt-player`) ; les
  textes d'appui se posent au-dessus (y ≈ 800 à 870).
- **Écran de fin** : les 20 dernières secondes, laisser libres les zones où YouTube posera ses
  éléments.

## 9. Export

- 1920×1080, 30 im/s (`data-fps` du master). La 4K n'apporte du détail que si le rush est en 4K et
  que les visages sont pré-cadrés (ils le sont) ; elle quadruple le temps d'export : proposer la 1080p.
- Un export natif HyperFrames prend environ **0,8 à 1,3 fois la durée de la vidéo** sur un Mac
  récent (10 minutes de vidéo : 8 à 13 minutes). Prévenir le client une fois, puis le laisser faire.
- Après l'export : `python3 tools/finaliser.py` (son à -14 LUFS, AAC 48 kHz 384 kb/s comme le
  recommande YouTube, contrôle, vidéo à téléverser dans Téléchargements).
