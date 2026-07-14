/* ==========================================================================
   Design system — Motion (HyperFrames / GSAP)
   Miroir de la section motion de src/brand/tokens.ts. HyperFrames raisonne en
   SECONDES (pas en frames). Les durées Remotion (frames @30fps) sont donc
   reconverties : frames / 30.
   Charger APRÈS gsap.min.js. Expose window.BRAND.
   ========================================================================== */
(function () {
  // --- Easings -------------------------------------------------------------
  // Fidélité exacte aux cubic-bezier du design system via CustomEase si le
  // plugin est chargé ; sinon fallback sur les easings GSAP natifs les plus
  // proches (expo.out ≈ outExpo, power2.inOut ≈ inOut).
  var ease = { inOut: "power2.inOut", outExpo: "expo.out" };

  if (typeof CustomEase !== "undefined" && typeof gsap !== "undefined") {
    gsap.registerPlugin(CustomEase);
    ease.inOut = CustomEase.create("brandInOut", "0.65,0,0.35,1");
    ease.outExpo = CustomEase.create("brandOutExpo", "0.16,1,0.3,1");
  }

  // --- Durées (secondes) ---------------------------------------------------
  var dur = {
    appear: 0.3,    // apparition d'un élément (250-400 ms)
    slide: 0.25,    // slide transition rapide
    holdHook: 1.2,  // hold d'un hook
    holdWord: 0.4,  // hold par mot
  };

  // --- Helpers de pattern --------------------------------------------------
  var helpers = {
    /**
     * Trace un trait SVG (Checkmark, Cross…) de 0 à 100% via stroke-dashoffset.
     * Équivalent du `strokeDashoffset={dashLen*(1-progress)}` Remotion.
     * @param {gsap.core.Timeline} tl  timeline paused enregistrée
     * @param {string} selector        sélecteur du <path>
     * @param {number} at              position sur la timeline (s)
     * @param {object} [opts]          { duration, ease }
     */
    drawStroke: function (tl, selector, at, opts) {
      opts = opts || {};
      document.querySelectorAll(selector).forEach(function (path) {
        var len = path.getTotalLength();
        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = len;
      });
      tl.to(
        selector,
        {
          strokeDashoffset: 0,
          duration: opts.duration || 0.47, // ~14 frames @30fps
          ease: opts.ease || ease.inOut,
        },
        at
      );
    },

    /**
     * Anime le yellow underline de gauche à droite (width 0 -> targetPx).
     * @param {gsap.core.Timeline} tl
     * @param {string} selector  sélecteur de .brand-underline
     * @param {number} targetPx  largeur finale en px
     * @param {number} at        position sur la timeline (s)
     */
    traceUnderline: function (tl, selector, targetPx, at) {
      tl.fromTo(
        selector,
        { width: 0 },
        {
          width: targetPx,
          duration: 0.4,
          ease: ease.outExpo,
        },
        at
      );
    },

    /**
     * Entrée standard d'un bloc : fade + glissée latérale (out-expo).
     * Équivalent du translateX(-60 -> 0) + opacity des InputRow Remotion.
     */
    enterFromLeft: function (tl, selector, at, opts) {
      opts = opts || {};
      tl.from(
        selector,
        {
          opacity: 0,
          x: opts.x != null ? opts.x : -60,
          duration: opts.duration || dur.appear,
          ease: ease.outExpo,
        },
        at
      );
    },
  };

  window.BRAND = { ease: ease, dur: dur, helpers: helpers };
})();
