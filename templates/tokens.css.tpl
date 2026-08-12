/* ==========================================================================
   Design system — Design tokens (HyperFrames / HTML+CSS)

   ⚠️ FICHIER GÉNÉRÉ. Ne pas éditer : il est réécrit à chaque `npm run sync`.
   Source : templates/tokens.css.tpl + brand.config.json (+ templates/style-presets.json).
   Pour changer une valeur : `/setup visuel`, ou édite brand.config.json puis `npm run sync`.

   Les VALEURS d'identité (couleurs, polices, skin de sous-titres) viennent de la config.
   Les STRUCTURES (easings, durées, safe areas, utilitaires) sont fixes : c'est la méthode,
   elle est la même pour tout le monde.

   Style actif : {{STYLE_PRESET_ID}}
   ========================================================================== */

:root {
  /* --- Palette ------------------------------------------------------------ */
  --brand-bg: {{VISUAL_BG}};            /* Fond principal. Jamais noir pur.            */
  --brand-surface: {{VISUAL_SURFACE}};  /* Cartes / blocs surélevés.                   */
  --brand-text: {{VISUAL_TEXT}};        /* Texte principal, lisible sur le fond.       */
  --brand-muted: {{VISUAL_MUTED}};      /* Texte secondaire / métadonnées.             */
  --brand-accent: {{VISUAL_ACCENT}};    /* Accent unique. Jamais décoratif.            */
  --brand-contrast: {{VISUAL_CONTRAST}};/* Couleur lisible POSÉE SUR l'accent.         */
  --brand-stroke: {{VISUAL_STROKE}};    /* Contour de lisibilité (sous-titres, titres).*/
  --brand-surface-contrast: {{VISUAL_SURFACE_CONTRAST}}; /* Surface qui tranche (rare).*/

  /* Alias de compatibilité — du code plus ancien parle encore de `white`/`yellow`/`light`.
     Ils suivent maintenant le style choisi : ne PAS les utiliser dans du code neuf. */
  --brand-white: var(--brand-text);
  --brand-yellow: var(--brand-accent);
  --brand-surface-light: var(--brand-surface-contrast);
  --brand-title-stroke: var(--brand-stroke);

  /* Couleur d'erreur (croix) — hors palette de marque, usage dataviz/compare */
  --brand-negative: #ff5050;

  /* --- Typographies ------------------------------------------------------- */
  --brand-font-display: {{FONT_DISPLAY}}, Impact, Haettenschweiler, "Arial Narrow", sans-serif;
  --brand-font-body: {{FONT_BODY}}, "Avenir Next", Arial, system-ui, sans-serif;
  --brand-font-captions: {{FONT_CAPTIONS}}, "Arial Black", Impact, sans-serif;
  --brand-font-mono: "Courier New", ui-monospace, monospace;

  /* --- Sous-titres : réglages du skin « {{CAPTIONS_SKIN}} » ---------------- */
  --brand-cap-size: 50px;
  --brand-cap-stroke-width: 8px;   /* skins outline / shadow                    */
  --brand-cap-radius: 14px;        /* skins plate / block arrondi               */

  /* --- Motion : easings (CSS) --------------------------------------------- */
  /* Fixes : c'est le rythme de la méthode, pas une préférence de marque.      */
  --brand-ease-inout: cubic-bezier(0.65, 0, 0.35, 1);   /* in-out aggressive   */
  --brand-ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1); /* entrées punchy      */

  /* --- Motion : durées (ms) ----------------------------------------------- */
  --brand-dur-appear: 300ms;          /* apparition d'un élément (250-400)     */
  --brand-dur-slide: 250ms;           /* slide transition rapide               */
  --brand-dur-hold-hook: 1200ms;      /* hold d'un hook                        */
  --brand-dur-hold-word: 400ms;       /* hold par mot                          */

  /* --- Safe areas (px, base 1080×1920 Reels/Stories/TikTok) --------------- */
  /* Contraintes Instagram, PAS du goût : ne pas personnaliser.               */
  --brand-safe-top: 220px;
  --brand-safe-bottom: 380px;
  --brand-safe-x: 100px;   /* cotes : IG recadre -> 100px (54 = plancher) */

  /* --- Sous-titres : hauteurs par contexte (dérivées du cadrage) ---------- */
  --brand-cap-y-split: 920px;    /* jointure du split-screen                   */
  --brand-cap-y-face: 1140px;    /* plein écran visage                         */
  --brand-cap-y-media: 1100px;   /* plein écran b-roll filmé                   */
  --brand-cap-y-motion: 1500px;  /* plein écran motion / images                */
}

/* ==========================================================================
   Utilitaires — à composer dans les compositions
   ========================================================================== */

/* Scène plein écran sur fond de marque (équivalent <AbsoluteFill>) */
.brand-stage {
  position: absolute;
  inset: 0;
  background: var(--brand-bg);
  font-family: var(--brand-font-body);
  color: var(--brand-text);
  overflow: hidden;
}

/* Zone safe centrale (Reels) : padding latéral + marges interface IG */
.brand-safe {
  position: absolute;
  left: var(--brand-safe-x);
  right: var(--brand-safe-x);
  top: var(--brand-safe-top);
  bottom: var(--brand-safe-bottom);
}

/* Carte / bloc surélevé */
.brand-surface {
  background: var(--brand-surface);
  border-radius: 18px;
}

/* --- Couleurs texte ------------------------------------------------------ */
.brand-accent { color: var(--brand-accent); }
.brand-muted  { color: var(--brand-muted); }
.brand-yellow { color: var(--brand-accent); } /* alias historique */

/* --- Typo : labels body (les SEULS textes autorisés en motion) ----------- */
/* Label de colonne / section title : Black UPPERCASE, 22-36px               */
.brand-label {
  font-family: var(--brand-font-body);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--brand-text);
}

/* Métadonnée / numérotation : SemiBold 20px */
.brand-meta {
  font-family: var(--brand-font-body);
  font-weight: 600;
  font-size: 20px;
  color: var(--brand-text);
}

/* Valeur dans un schéma : SemiBold */
.brand-value {
  font-family: var(--brand-font-body);
  font-weight: 600;
}

/* Sous-titres : police captions dédiée */
.brand-captions {
  font-family: var(--brand-font-captions);
}

/* Mono : prompts / terminaux / valeurs techniques */
.brand-mono {
  font-family: var(--brand-font-mono);
}

/* ==========================================================================
   SOUS-TITRES — base commune + skin actif

   `.cap` porte le skin CHOISI ({{CAPTIONS_SKIN}}). Les 5 skins restent disponibles
   en classes `.cap-skin-<nom>` : pour en essayer un autre sur une compo, ajoute la
   classe. Pour changer le défaut de toutes tes vidéos : `/setup visuel`.
   ========================================================================== */

.cap {
  position: absolute;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--brand-font-captions);
  font-size: var(--brand-cap-size);
  line-height: 1.35;
  white-space: nowrap;
  text-transform: uppercase;
}

/* Skin actif (injecté depuis le style choisi) */
{{CAPTIONS_SKIN_ACTIVE_CSS}}

/* Les 5 skins, nommés — pour override ponctuel sur une compo */
{{CAPTIONS_SKINS_ALL_CSS}}

/* ==========================================================================
   Patterns motion transposables (états statiques — anim. via motion.js)

   Ce sont des OPTIONS du catalogue, pas une signature obligatoire : n'en pose un
   que s'il sert la section. Trois patterns identiques dans toutes tes vidéos, c'est
   ce qui rend deux comptes indistinguables.
   ========================================================================== */

/* Ghost number : grand chiffre déco, texte 10%, haut-droite. 1 = 1 entrée. */
.brand-ghost {
  position: absolute;
  top: 0;
  right: 24px;
  font-family: var(--brand-font-body);
  font-weight: 700;
  font-size: 180px;
  line-height: 1;
  color: var(--brand-text);
  opacity: 0.1;
  user-select: none;
}

/* Accent underline : trait accent sous un mot-clé (largeur animée 0 -> 100%) */
.brand-underline-wrap { position: relative; display: inline-block; }
.brand-underline {
  position: absolute;
  left: 0;
  bottom: -8px;
  height: 6px;
  width: 0; /* animé de gauche à droite via motion.js / GSAP */
  background: var(--brand-accent);
  border-radius: 3px;
}

/* Circular cutout : cercle bordé (logo / visage / preuve) */
.brand-cutout {
  border-radius: 50%;
  border: 4px solid var(--brand-text);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-surface);
}
