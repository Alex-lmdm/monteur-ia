# Usage avec Remotion (legacy — les projets vidéo actuels sont en HyperFrames)

Pour un projet Remotion, créer un fichier `src/brand-tokens.ts` qui réexpose les tokens.
⚠️ **Les valeurs ne s'écrivent pas à la main** : les lire dans `brand/tokens.css` (généré) ou dans
`brand.config.json`. Les `<…>` ci-dessous sont des emplacements, pas des couleurs à recopier.

```typescript
export const BRAND = {
  colors: {
    background: '<visual.bg>',
    surface: '<visual.surface>',
    text: '<visual.text>',
    muted: '<dérivée>',
    accent: '<visual.accent>',
    contrast: '<dérivée — à poser SUR l'accent>',
    stroke: '<dérivée — contour de lisibilité>',
  },
  fonts: {
    // pas de police display en motion : le body en Black porte les hooks
    body: '<visual.fontBody>, system-ui, sans-serif',
    mono: 'Courier New, ui-monospace, monospace',
  },
  motion: {
    // durations en frames @30fps  (= ms du JSON §8 × 30 / 1000)
    appearFrames: 9,
    holdHookFrames: 36,
    holdWordFrames: 12,
  },
} as const;
```

Pour les easings dans Remotion : `Easing.bezier(0.65, 0, 0.35, 1)` (inOut) ou
`Easing.bezier(0.16, 1, 0.3, 1)` (outExpo). Pour des entrées punchy :
`spring({ frame, fps, config: { damping: 200, stiffness: 100, mass: 0.5 } })`.

Toujours charger la police body via `@remotion/google-fonts/…` au montage de la composition.

**Porter une composition Remotion existante vers HyperFrames** : ne PAS faire de conversion ligne à
ligne — reconstruire nativement en HyperFrames à partir du design system du SKILL.
