# Modèle de `script.md`

Le texte prompteur sort du skill `reel-script` (cas « avec une vidéo de référence »), avec les
règles de clonage du skill `reel-cloneur` §5. Ce modèle fixe la forme du fichier.

```markdown
# Reel Cloneur™ · ton script

**D'après :** {plateforme} · {@compte ou « fichier »} · {durée} s · l'analyse est dans le même dossier
**Ton choix :** {la piste, en mots simples : « la même chose en français, même outil » / « la même mécanique, pour ton appli X »}
**Ton appel à l'action :** {commente **MOT** · ce qu'il reçoit} · **Durée visée :** ~{s} s

> On a repris la mécanique de ce Reel (son accroche, sa structure, son rythme, la place de l'appel
> à l'action){ et l'outil qu'il présente}, jamais ses phrases ni son vécu. Ce texte est le tien.

## Ton accroche (choisis A, B ou C)

Même mécanique que l'original : **{type d'accroche, en mots simples} + {ressort}**.

- **A.** {accroche}
  *À l'écran : {texte court, 6 mots max, ou « visage seul »}*
- **B.** {accroche}
  *À l'écran : …*
- **C.** {accroche}
  *À l'écran : …*

## Ton script (format prompteur)

*Temps 1 · L'accroche · ~{s} s* → ton accroche A, B ou C.

*Temps 2 · {rôle dans l'original, ex. relance par la preuve sociale} · ~{s} s*

{ligne prompteur}
{ligne prompteur}

*Temps 3 · {rôle} · ~{s} s*

{…}

*Temps {n} · Ton appel à l'action · ~{s} s*

{ton appel à l'action}

{Trou `[à compléter : …]` seulement s'il a dit avoir un essai ou un chiffre sans le donner. Sinon, aucun trou : tournure sans chiffre.}

## À vérifier avant de tourner

{Les faits sur l'outil repris de la vidéo (ce qu'il fait, gratuit ou non, ses chiffres annoncés), un par ligne, avec où vérifier (« sur le site »). Section omise s'il n'y en a pas.}

## À reproduire au montage

- **Rythme :** {un changement d'image toutes les ~x s ; sur les 3 premières secondes : …}
- **Cadrage proposé :** {0:00-0:05 ton visage en plein écran · 0:05-0:20 ton visage en bas, {ce qu'on montre} au-dessus · …}
- **Texte à l'écran :** {ce que l'original affiche et quand → chez toi : sous-titres, petit mot clé, image}
- **À filmer en plus :** {ton écran, un objet, le résultat, ou rien}
- **Son :** {musique et bruitages à vérifier à l'oreille ; son déclaré par la plateforme s'il y en a un}

Quand tu as tourné : glisse ta vidéo et dis « on monte celle-ci ». Ton monteur part de ces choix.

---

## Pour Monteur IA

*(Bloc technique pour le montage : tu n'as pas besoin de le lire.)*

- Cadrages proposés : {0:00-0:05 `faceplein` · 0:05-0:20 `split`, haut = {contenu} · …}. Proposition
  seulement : réglages par défaut et préférences du client d'abord ; première vidéo = réglages de base.
- Rythme cible : {plan moyen ~x s ; n changements sur 0-3 s}.
- Texte à l'écran : {équivalent motion design / sous-titres, dans la doctrine de `motion-design`}.
- Appel à l'action : {type de `cta.types`} · mot-clé `{MOT}` · `{cta.dmTool}` envoie {ce qu'il envoie} (DM et légende rédigés à la publication).
- Durée : débit de l'original {x} mots/s ; temps visés {…} s ; texte du client ~{…} s.
- Source : `clones/{dossier}/analyse.md`.
```

Pas de jargon au-dessus du bloc « Pour Monteur IA » : ni `faceplein`, ni `split`, ni « beat », ni
« CTA », ni « hook », ni nom de fichier ou de skill. On dit « temps », « accroche », « appel à
l'action ».
