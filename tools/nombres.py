#!/usr/bin/env python3
"""NOMBRES : « 1 400 » = « 1400 » = « mille quatre cents », « trois » = « 3 », « 50 % » = « 50% ».

Partagé par tools/montage_captions.py. Le découpage des sous-titres (écrit à la main) et la
transcription mot à mot (Whisper, derush/<video>_words.json) n'écrivent pas un nombre de la même
façon : « 3 concepts » contre « trois concepts », « 1 400 vrais logos » contre « 1400 vrais logos ».
Sans cette normalisation, le sous-titre ne retrouve pas son premier mot et part en retard (son
départ est interpolé entre ses voisins : +0,3 s et +0,6 s mesurés sur un vrai Reel).

    from nombres import jetons
    jetons(["à", "plus", "de", "1", "400", "vrais"])
    # [("a", 0), ("plus", 1), ("de", 2), ("1400", 3), ("vrais", 5)]

Chaque jeton garde l'indice du premier mot dont il vient. Un texte sans nombre donne exactement un
jeton par mot (normalisé comme avant : minuscules, sans accents ni ponctuation), donc
l'alignement des sous-titres ne change que là où un nombre s'écrit autrement.

Règles (français) :
  - séparateurs de milliers : espace, espace insécable, espace fine insécable (« 1 400 ») ;
  - nombres en lettres, traits d'union compris : « vingt-deux », « soixante et onze »,
    « quatre-vingt-dix-neuf », « deux cents », « mille quatre cents », « deux millions » ;
  - « un » et « une » seuls restent des mots (des articles, presque toujours) ;
  - pourcentage : « 50 % », « 50 pour cent », « cinquante pourcent » = « 50% ».
"""
from __future__ import annotations

import re
import unicodedata

UNITES = {"zero": 0, "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6,
          "sept": 7, "huit": 8, "neuf": 9}
DIX_A_SEIZE = {"dix": 10, "onze": 11, "douze": 12, "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16}
DIZAINES = {"vingt": 20, "vingts": 20, "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60,
            "septante": 70, "huitante": 80, "octante": 80, "nonante": 90}
CENT = {"cent", "cents"}
GRANDS = {"mille": 1000, "million": 10 ** 6, "millions": 10 ** 6, "milliard": 10 ** 9, "milliards": 10 ** 9}
VOCABULAIRE = set(UNITES) | set(DIX_A_SEIZE) | set(DIZAINES) | CENT | set(GRANDS)


def normaliser(mot: str) -> str:
    """Minuscules, sans accents ni ponctuation (« Ça » -> « ca », « logos. » -> « logos »)."""
    w = unicodedata.normalize("NFD", str(mot).lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", w)


def _morceaux(mot: str) -> list[str]:
    """« quatre-vingt-dix » -> ["quatre", "vingt", "dix"] ; tout autre mot reste entier."""
    parts = [normaliser(p) for p in re.split(r"[-‐‑]", str(mot))]
    if len(parts) > 1 and all(p in VOCABULAIRE or p == "et" for p in parts) and any(p != "et" for p in parts):
        return parts
    return [normaliser(mot)]


def _lire(toks: list[str], i: int) -> tuple[int, int] | None:
    """Le nombre en lettres qui commence à toks[i] : (valeur, indice après lui), sinon None."""
    total, groupe, dernier, j = 0, 0, None, i
    while j < len(toks):
        t = toks[j]
        libre = dernier in (None, "cent", "mille", "grand")
        if t in UNITES:
            v = UNITES[t]
            if libre or (dernier == "dizaine" and groupe % 10 == 0 and v > 0) \
                    or (dernier == "dix" and v >= 7) or (dernier == "et" and v == 1):
                groupe, dernier = groupe + v, "unite"
            else:
                break
        elif t in DIX_A_SEIZE:
            v = DIX_A_SEIZE[t]
            if libre or (dernier == "dizaine" and groupe % 100 in (60, 80)) \
                    or (dernier == "et" and v == 11 and groupe % 100 == 60):
                groupe, dernier = groupe + v, "dix" if v == 10 else "unite"
            else:
                break
        elif t in DIZAINES:
            v = DIZAINES[t]
            if v == 20 and dernier == "unite" and groupe % 100 == 4:      # quatre-vingt(s)
                groupe, dernier = groupe + 76, "dizaine"
            elif libre and groupe % 100 == 0:
                groupe, dernier = groupe + v, "dizaine"
            else:
                break
        elif t == "et":
            suite = toks[j + 1] if j + 1 < len(toks) else ""
            if dernier == "dizaine" and groupe % 100 in (20, 30, 40, 50, 60) and suite in ("un", "une", "onze"):
                dernier = "et"
            else:
                break
        elif t in CENT:
            if dernier in (None, "mille") and groupe == 0:
                groupe, dernier = 100, "cent"
            elif dernier == "unite" and 1 < groupe < 10:
                groupe, dernier = groupe * 100, "cent"
            else:
                break
        elif t in GRANDS:
            m = GRANDS[t]
            if dernier == "mille" or (m > 1000 and dernier == "grand") or (total and total < m):
                break
            total, groupe, dernier = total + (groupe or 1) * m, 0, "mille" if m == 1000 else "grand"
        else:
            break
        j += 1
    if j == i or (j == i + 1 and toks[i] in ("un", "une")):
        return None
    return total + groupe, j


def jetons(mots) -> list[tuple[str, int]]:
    """(jeton normalisé, indice du 1er mot source) pour une suite de mots. Les mots vides après
    normalisation (ponctuation seule, emoji) donnent un jeton vide : à l'appelant de les garder ou non."""
    brut = [(m, i) for i, mot in enumerate(mots) for m in _morceaux(mot)]
    toks = [m for m, _ in brut]
    out = []
    k = 0
    while k < len(toks):
        t, source = toks[k], brut[k][1]
        if t.isdigit() and len(t) <= 3:                  # « 1 400 », « 150 000 »
            fin = k + 1
            while fin < len(toks) and len(toks[fin]) == 3 and toks[fin].isdigit() and brut[fin][1] != brut[fin - 1][1]:
                t, fin = t + toks[fin], fin + 1
            k = fin
        elif t in VOCABULAIRE and _lire(toks, k):
            valeur, k = _lire(toks, k)
            t = str(valeur)
        else:
            out.append((t, source))
            k += 1
            continue
        # Pourcentage collé au nombre : « 50 % », « 50 pour cent », « 50 pourcent ».
        if k < len(toks) and toks[k] in ("%", "pourcent"):
            t, k = t + "%", k + 1
        elif toks[k:k + 2] == ["pour", "cent"]:
            t, k = t + "%", k + 2
        out.append((t, source))
    return out


if __name__ == "__main__":
    import sys
    print(jetons(sys.argv[1:]))
