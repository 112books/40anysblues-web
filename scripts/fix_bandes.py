#!/usr/bin/env python3
"""
Normalitza noms de bandes als fitxers de músics.
Dry-run per defecte. Afegeix --apply per modificar fitxers.
"""
import os, sys, re

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'ca', 'musics')

# (forma incorrecta, forma canònica)
CORRECCIONS = [
    ("Amadeu Casas Blues a Go Go",           "Amadeu Casas & Blues a Go Go"),
    ("Las Balas  Perdidas",                  "Las Balas Perdidas"),
    ("Balta Bordoy and The Bad Boys",        "Balta Bordoy & The Bad Boys"),
    ("Chef Dave and The Cooks",              "Chef Dave & The Cooks"),
    ("Chino & the Big Bet",                  "Chino & The Big Bet"),
    ("Chino and The Big Bet",               "Chino & The Big Bet"),
    ("Crazy blues",                          "Crazy Blues"),
    ("Dani Baraldes & XXX Band",             "Dani Baraldés & The XXX Band"),
    ("Harmonica Zumel Blues Band",           "Harmònica Zúmel Blues Band"),
    ("Harmònica Zumel Blues Band",           "Harmònica Zúmel Blues Band"),
    ("Harmónica Zumel Blues Band",           "Harmònica Zúmel Blues Band"),
    ("Koko Jean & the Tonics",               "Koko Jean & The Tonics"),
    ("Koko-Jean & the Tonics",               "Koko Jean & The Tonics"),
    ("Lazy Jumpers",                         "The Lazy Jumpers"),
    ("Lluis Coloma Trio",                    "Lluís Coloma Trio"),
    ("Los Mambo jambo",                      "Los Mambo Jambo"),
    ("Los Mambo Jambo Arkestra",             "Mambo Jambo Arkestra"),
    ("Martin Burguez & His Rhythm Combo",    "Martín Burguez & His Rhythm Combo"),
    ("Midnight Rockets",                     "The Midnight Rockets"),
    ("The New Blues Explosion",              "New Blues Explosion"),
    ("Nu Niles",                             "The Nu-Niles"),
    ("The Nu Niles",                         "The Nu-Niles"),
    ("Ray Gelato And The Giants",            "Ray Gelato & The Giants"),
    ("Ray Gelato and The Giants",            "Ray Gelato & The Giants"),
    ("The Red and the Rotten",               "The Red & The Rotten"),
    ("Sedgwick and Shingles",                "Sedgwick & Shingles"),
    ("Sweet Little and the Midnight Laters", "Sweet Little & Midnight Laters"),
    ("Sweet Marta & the Blues Shakers",      "Sweet Marta & The Blues Shakers"),
    ("Sweet Marta & The Blues Shakers,",     "Sweet Marta & The Blues Shakers"),
    ("Swingset",                             "SwingSet"),
    ("Los tres cerditos",                    "Los Tres Cerditos"),
    ("The Velvet Candles",                   "Velvet Candles"),
    ("Victor Puertas & The Mellow Tones",    "Víctor Puertas & The Mellow Tones"),
    ("Victor Puertas & Mellowtones",         "Víctor Puertas & The Mellow Tones"),
    ("Víctor Puertas & the Mellowtones",     "Víctor Puertas & The Mellow Tones"),
    ("Víctor Puertas & Mellowtones",         "Víctor Puertas & The Mellow Tones"),
    ("Wax and Boogie",                       "Wax & Boogie"),
    ("Wax&Boogie",                           "Wax & Boogie"),
]

apply = '--apply' in sys.argv
total = 0

for slug in sorted(os.listdir(CONTENT_DIR)):
    idx = os.path.join(CONTENT_DIR, slug, 'index.md')
    if not os.path.isfile(idx):
        continue
    with open(idx, encoding='utf-8') as f:
        original = f.read()

    modified = original
    canvis = []
    for wrong, correct in CORRECCIONS:
        # Match as a full band line: "- WrongName" (with optional trailing spaces)
        pattern = re.compile(r'^(- )' + re.escape(wrong) + r'\s*$', re.MULTILINE)
        if pattern.search(modified):
            modified = pattern.sub(r'\g<1>' + correct, modified)
            canvis.append(f"  {wrong!r} → {correct!r}")

    if canvis:
        total += len(canvis)
        print(f"{slug}:")
        for c in canvis:
            print(c)
        if apply:
            with open(idx, 'w', encoding='utf-8') as f:
                f.write(modified)

print(f"\n{'Aplicat' if apply else 'Previsualització'}: {total} correccions")
if not apply:
    print("Executa amb --apply per modificar els fitxers.")
