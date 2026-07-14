# Usage avec Remotion (legacy — les projets vidéo actuels sont en HyperFrames)

Pour un projet Remotion, créer un fichier `src/lmdm-tokens.ts` qui réexpose les tokens (source unique des valeurs : le JSON de tokens du SKILL, §8) :

```typescript
export const LMDM = {
  colors: {
    background: '#202022',
    surface: '#2b2b2d',
    white: '#ffffff',
    muted: '#a6a6a0',
    yellow: '#ffee00',
    titleStroke: '#000000',
  },
  fonts: {
    // pas de police display en motion : Poppins Black porte les hooks
    body: 'Poppins, Avenir Next, Arial, system-ui, sans-serif',
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

Pour les easings dans Remotion : `Easing.bezier(0.65, 0, 0.35, 1)` (inOut) ou `Easing.bezier(0.16, 1, 0.3, 1)` (outExpo). Pour des entrées punchy : `spring({ frame, fps, config: { damping: 200, stiffness: 100, mass: 0.5 } })`.

Toujours charger les fonts via `@remotion/google-fonts/Poppins` au montage de la composition.

**Porter une composition Remotion existante vers HyperFrames** : ne PAS faire de conversion ligne à ligne — reconstruire nativement en HyperFrames à partir du design system du SKILL.
