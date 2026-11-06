#!/usr/bin/env python3
"""Comprova l'estat de les traduccions (castella i angles) respecte del catala.

Revisa, per a cada pagina:
  - Que existeixi a content/es i content/en la mateixa ruta que a content/ca.
  - Que el frontmatter que no es tradueix (any de naixement, mort, ordre,
    data de sessio, formacions) sigui identic als tres idiomes.
  - Que el cos no sigui el catala sense traduir.
  - Que els enllacos interns portin el prefix d'idioma (/es/ o /en/).
  - Que les traduccions no perdin ni afegeixin enllacos respecte del catala.

Us:
    python3 scripts/check-i18n.py            # informe complet
    python3 scripts/check-i18n.py --quiet    # nomes errors

Sortida: 0 si tot quadra, 1 si hi ha errors.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import Counter

import yaml

ARREL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDIOMES = ("ca", "es", "en")
PREFIX = {"ca": "", "es": "/es/", "en": "/en/"}
CAMP_IDENTICS = ("born_year", "death_year", "ordre", "session_date", "draft", "bands")
# Rutes que no son contingut i no porten prefix d'idioma
EXEMPCIONS = ("/logotips/", "/css/", "/js/", "/llibres/", "/autors/", "/images/", "/fonts/", "/favicon")


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text.lstrip("\ufeff"), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def cos(text: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---", "", text.lstrip("\ufeff"), count=1, flags=re.S)


def enllacos_interns(text: str) -> list:
    """Objectius interns del cos, en ordre d'aparicio."""
    return re.findall(r"\]\((/[^)\s#]*)", cos(text))


def clau_relativa(ruta: str) -> str:
    return os.path.relpath(ruta, os.path.join(ARREL, "content", "ca"))


def carrega_pagines() -> dict:
    """Retorna {idioma: {ruta_relativa: text}}."""
    pages = {}
    for idioma in IDIOMES:
        arrel = os.path.join(ARREL, "content", idioma)
        fitxers = glob.glob(os.path.join(arrel, "**", "*.md"), recursive=True)
        pages[idioma] = {os.path.relpath(f, arrel): open(f, encoding="utf-8").read() for f in fitxers}
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Comprova les traduccions del web.")
    parser.add_argument("--quiet", action="store_true", help="nomes mostra els errors")
    args = parser.parse_args()

    pages = carrega_pagines()
    base_ca = pages["ca"]
    errors = []
    avisos = []

    # 1. Pagines que falten o sobren
    for idioma in ("es", "en"):
        falten = sorted(set(base_ca) - set(pages[idioma]))
        sobren = sorted(set(pages[idioma]) - set(base_ca))
        if not args.quiet:
            print(f"Pagines: ca={len(base_ca)} {idioma}={len(pages[idioma])}")
        for ruta in falten:
            errors.append(f"{idioma}: falta la pagina {ruta}")
        for ruta in sobren:
            errors.append(f"{idioma}: pagina sense equivalent al catala: {ruta}")

    # 2. Frontmatter que no es tradueix
    for idioma in ("es", "en"):
        for ruta, text in sorted(pages[idioma].items()):
            if ruta not in base_ca:
                continue
            a = frontmatter(base_ca[ruta])
            b = frontmatter(text)
            for camp in CAMP_IDENTICS:
                if a.get(camp) != b.get(camp):
                    errors.append(f"{idioma}: {ruta} te {camp}={b.get(camp)!r} i el catala {a.get(camp)!r}")

    # 3. Cos sense traduir i enllacos
    for idioma in ("es", "en"):
        for ruta, text in sorted(pages[idioma].items()):
            if ruta not in base_ca:
                continue
            ca_text = base_ca[ruta]
            ca_cos = cos(ca_text).strip()
            tr_cos = cos(text).strip()
            if ca_cos and ca_cos == tr_cos:
                errors.append(f"{idioma}: {ruta} te el cos catala sense traduir")

            prefix = PREFIX[idioma]
            for enllac in enllacos_interns(text):
                if enllac.startswith(EXEMPCIONS):
                    continue
                if not enllac.startswith(prefix):
                    avisos.append(f"{idioma}: {ruta} enllac intern sense prefix: {enllac}")

            # Compara els enllacos interns amb els del catala
            norm = lambda xs: Counter(re.sub(r"^/es/|^/en/", "/", x.split("#")[0]) for x in xs)
            a, b = norm(enllacos_interns(ca_text)), norm(enllacos_interns(text))
            if a - b:
                avisos.append(f"{idioma}: {ruta} perd enllacos: {sorted((a - b).elements())}")
            if b - a:
                avisos.append(f"{idioma}: {ruta} afegeix enllacos: {sorted((b - a).elements())}")

    # 4. Instruments: cada fitxa ha de tenir el mateix nombre que al catala
    for idioma in ("es", "en"):
        for ruta, text in sorted(pages[idioma].items()):
            if not ruta.endswith("index.md") or ruta not in base_ca:
                continue
            a = frontmatter(base_ca[ruta]).get("instruments") or []
            b = frontmatter(text).get("instruments") or []
            if len(a) != len(b):
                errors.append(
                    f"{idioma}: {ruta} te {len(b)} instruments i el catala {len(a)} ({b} / {a})"
                )

    for avis in avisos:
        print(f"AVIS: {avis}")
    for err in errors:
        print(f"ERROR: {err}")

    if errors:
        print(f"\n{len(errors)} errors i {len(avisos)} avisos.")
        return 1
    print(f"\nTraduccions correctes ({len(avisos)} avisos).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
