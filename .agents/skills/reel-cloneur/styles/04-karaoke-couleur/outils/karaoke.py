#!/usr/bin/env python3
"""KARAOKÉ : sous-titres du style n°04 « Karaoké couleur » (mot prononcé allumé en couleur).

╔══════════════════════════════════════════════════════════════════════════════╗
║ OUTIL DU KIT 04 : a copier dans tools/ du Reel. ADAPTE A CHAQUE REEL : EMOJIS. ║
║ Le reste est generique au style n°04.                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

A lancer APRES `python3 tools/montage_captions.py --write` (qui pose texte, hauteur et minutage de
chaque sous-titre). Ce script reprend compositions/captions.html et, sans toucher au minutage :
  1. coupe chaque sous-titre en mots (<span class="w">), ponctuation retiree ;
  2. le met sur 2 lignes des 3 mots (2 + 1, 2 + 2, 3 + 2), la 1re ligne restant a la hauteur de
     la section (le bloc descend, il ne remonte pas vers l'etiquette de rang) ;
  3. allume le mot prononce dans UNE couleur par sous-titre, a tour de role : accent (jaune),
     muted (vert), negative (rouge) ; les autres mots restent en texte (blanc), contour du skin ;
  4. fait surgir un petit emoji sous le sous-titre sur quelques mots (EMOJIS, 1 toutes les ~10 s
     au plus, comme l'original) ;
  5. ecrit la timeline GSAP `captions` (tl.set calés sur derush/<video>_words.json : deterministe).
Relancable : le texte d'origine est garde dans data-texte.
"""
import html
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sections  # noqa: E402
from nombres import normaliser  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAPS = ROOT / "compositions/captions.html"
WORDS = sections.CUTS_PATH.with_name(sections.CUTS_PATH.name.replace("_cuts.json", "_words.json"))
FPS = getattr(sections, "FPS", 30)

# >>> A ADAPTER A CHAQUE REEL : mot (en capitales, tel qu'affiche) -> emoji, au 1er sous-titre qui le
#     contient. L'original en pose un toutes les ~10 s, sur un mot concret (outil, objet, action).
EMOJIS = {
    # "OUTIL": "🛠️",      # exemple : le mot tel qu'affiche (capitales), puis l'emoji
}
COULEURS = ["hl-a", "hl-b", "hl-c"]       # accent, muted, negative : une par sous-titre, a tour de role
TAILLE, INTERLIGNE = None, None           # lus dans brand/tokens.css (--brand-cap-size, line-height)

tokens = (ROOT / "brand/tokens.css").read_text(encoding="utf-8")
TAILLE = float(re.search(r"--brand-cap-size:\s*([\d.]+)px", tokens).group(1))
INTERLIGNE = float(re.search(r"\.cap \{[^}]*line-height:\s*([\d.]+)", tokens, re.S).group(1))
DEMI_LIGNE = round(TAILLE * INTERLIGNE / 2)

mots = [w for w in json.loads(WORDS.read_text(encoding="utf-8")) if any(c.isalnum() for c in w["w"])]

src = CAPS.read_text(encoding="utf-8")
CAP = re.compile(r'<div class="cap clip(?: hl-[abc])?" id="cap-(\d+)" style="top:(\d+)px"( data-texte="[^"]*")? '
                 r'data-start="([\d.]+)" data-duration="([\d.]+)" data-track-index="(\d+)">(.*?)</div>')


def lignes(toks):
    """Mots par ligne : un bloc court (2 mots, ou 11 caracteres au plus, comme « TOP SIX AI » dans
    l'original) tient sur une ligne ; au-dela deux lignes, la 1re plus longue (2 + 1, 2 + 2, 3 + 2)."""
    n = len(toks)
    if n <= 2 or len(" ".join(toks)) <= 11:
        return [n]
    return [(n + 1) // 2, n // 2]


def nettoie(m):
    return m.strip(".,;:!?«»\"").strip()


caps, emojis_poses = [], set()
for m in CAP.finditer(src):
    idx, top, texte_attr, st, du, piste, inner = m.groups()
    texte = html.unescape(re.search(r'data-texte="([^"]*)"', texte_attr).group(1)) if texte_attr else html.unescape(inner)
    caps.append({"i": int(idx), "top": int(top), "texte": texte, "start": float(st), "dur": float(du),
                 "piste": piste, "brut": m.group(0)})
if not caps:
    sys.exit("ERREUR : aucun sous-titre trouve dans compositions/captions.html (lance d'abord montage_captions.py --write).")

rows, tweens, emo_rows = [], [], []
curseur = 0
for j, c in enumerate(caps):
    debut, fin = c["start"], c["start"] + c["dur"]
    toks = [t for t in (nettoie(x) for x in c["texte"].split()) if t]
    # Temps de chaque mot : le mot transcrit correspondant, cherche dans la fenetre du sous-titre.
    fen = [w for w in mots if debut - 0.35 <= w["start"] < fin + 0.05]
    temps, k = [], 0
    for t in toks:
        n = normaliser(t)
        trouve = None
        for q in range(k, len(fen)):
            if n and normaliser(fen[q]["w"]) == n:
                trouve, k = fen[q]["start"], q + 1
                break
        temps.append(trouve)
    temps[0] = debut                                   # le 1er mot est allume des l'apparition
    for q in range(1, len(temps)):                     # mot introuvable (🔗…) : entre ses voisins
        if temps[q] is None:
            suiv = next((temps[r] for r in range(q + 1, len(temps)) if temps[r] is not None), fin)
            temps[q] = temps[q - 1] + (suiv - temps[q - 1]) / 2
        temps[q] = min(max(temps[q], temps[q - 1] + 0.06), fin - 0.04)
    couleur = COULEURS[j % len(COULEURS)]
    parts, pos = [], 0
    for li, n in enumerate(lignes(toks)):
        bout = []
        for q in range(pos, pos + n):
            w = html.escape(toks[q])
            bout.append(f'<span class="w w{q}"><span class="b">{w}</span><span class="h" data-layout-allow-overlap>{w}</span></span>')
        parts.append(" ".join(bout))
        pos += n
    top = c["top"] + (DEMI_LIGNE if len(lignes(toks)) == 2 else 0)
    texte_attr = html.escape(c["texte"], quote=True)
    rows.append(f'      <div class="cap clip {couleur}" id="cap-{c["i"]}" style="top:{top}px" data-texte="{texte_attr}" '
                f'data-start="{c["start"]:.5f}" data-duration="{c["dur"]:.5f}" data-track-index="{c["piste"]}">'
                + "<br>".join(parts) + "</div>")
    sel = f'#captions #cap-{c["i"]} .w'
    for q, t in enumerate(temps):
        tweens.append(f"tl.set('{sel}{q} .h', {{opacity: 1}}, {t:.3f});")
        if q + 1 < len(temps):
            tweens.append(f"tl.set('{sel}{q} .h', {{opacity: 0}}, {temps[q + 1]:.3f});")
    # Emoji : sous le bloc, au mot qui le declenche.
    for q, t in enumerate(toks):
        cle = next((e for e in EMOJIS if e not in emojis_poses and normaliser(e) == normaliser(t)), None)
        if cle:
            emojis_poses.add(cle)
            n_e = len(emo_rows)
            y = top + (DEMI_LIGNE if len(lignes(toks)) == 2 else 0) + round(TAILLE * 1.6)
            t0 = temps[q]
            d = max(fin - t0, 0.7)
            a, b = round(t0 * FPS), round((t0 + d) * FPS)
            emo_rows.append(f'      <div class="emoji clip" id="emo-{n_e}" style="top:{y}px" '
                            f'data-start="{(a - 0.01) / FPS:.5f}" data-duration="{(b - a) / FPS:.5f}" '
                            f'data-track-index="{4 + n_e % 2}"><span class="emo-in">{EMOJIS[cle]}</span></div>')
            tweens.append(f"tl.fromTo('#captions #emo-{n_e} .emo-in', {{scale: 0.3, opacity: 0}}, "
                          f"{{scale: 1, opacity: 1, duration: 0.18, ease: 'back.out(2.2)'}}, {t0:.3f});")
            break

style = """
      /* Style n°04 : karaoke (tools/karaoke.py). Couleurs = tokens du style, jamais en dur. */
      #captions .cap .w { position: relative; display: inline-block; }
      #captions .cap .w .h { position: absolute; left: 0; top: 0; opacity: 0; }
      #captions .cap.hl-a .w .h { color: var(--brand-accent); }
      #captions .cap.hl-b .w .h { color: var(--brand-muted); }
      #captions .cap.hl-c .w .h { color: var(--brand-negative); }
      #captions .emoji { position: absolute; left: 50%; width: 0; height: 0; }
      #captions .emoji .emo-in { position: absolute; left: -60px; top: -60px; width: 120px; height: 120px;
        display: flex; align-items: center; justify-content: center; font-size: 84px; line-height: 1;
        -webkit-text-stroke: 0; }
"""
debut_rows = src.index(caps[0]["brut"])
fin_rows = src.index(caps[-1]["brut"]) + len(caps[-1]["brut"])
out = src[:debut_rows] + "\n".join(rows).lstrip() + src[fin_rows:]
out = re.sub(r"\n      <div class=\"emoji clip\".*?</div>", "", out)              # emojis d'un passage precedent
out = out.replace("\n    </div>\n    <script>", "\n" + "\n".join(emo_rows) + "\n    </div>\n    <script>", 1) if emo_rows else out
if "Style n°04 : karaoke" not in out:
    out = out.replace("    </style>", style + "    </style>", 1)
tl = ("      window.__timelines = window.__timelines || {};\n"
      "      (function () {\n"
      "        var tl = gsap.timeline({ paused: true });\n"
      + "".join(f"        {t}\n" for t in tweens)
      + "        window.__timelines[\"captions\"] = tl;\n"
      "      })();\n")
out = re.sub(r"      window\.__timelines = window\.__timelines \|\| \{\};\n.*?\n    </script>",
             tl + "    </script>", out, count=1, flags=re.S)
CAPS.write_text(out, encoding="utf-8")
print(f"{len(caps)} sous-titres en karaoke, {len(emo_rows)} emoji(s), {len(tweens)} reglages -> {CAPS.relative_to(ROOT)}")
