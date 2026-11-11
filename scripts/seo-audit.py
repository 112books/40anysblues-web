#!/usr/bin/env python3
"""Auditoria de SEO i de cerca amb IA sobre el web generat.

Revisa l'HTML de public/ (cal haver executat `hugo` abans) i comprova:

  - Que cada pagina tingui canonical i els quatre enllacos hreflang (ca, es, en,
    x-default).
  - Que la metadescripcio no caigui al text general del lloc (senyal que la
    pagina no te descripcio propia) i que no superi els 160 caracters.
  - Que els titols no es repeteixin dins del mateix idioma.
  - Que el JSON-LD sigui valid i quins tipus de schema porta cada seccio.
  - Quines pagines porten noindex (nomes hauria de ser /cerca/).

Sortida: 0 si no hi ha errors greus (JSON-LD invalid, canonical o hreflang que
falten), 1 si n'hi ha.

Us:
    hugo --minify --cleanDestinationDir --baseURL 'https://40anysblues.112books.eu/'
    python3 scripts/seo-audit.py
"""

from __future__ import annotations

import collections
import glob
import html as html_lib
import json
import os
import re
import sys

ARREL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ARREL, "public")

DESC_GENERICA = (
    "Arxiu fotogràfic i biogràfic de l'escena del blues barcelonina",
    "Archivo fotográfico y biográfico de la escena del blues barcelonés",
    "Photographic and biographical archive of Barcelona's blues scene",
)
LD = re.compile(r"<script type=application/ld[+]json>(.*?)</script>", re.S)


def seccio(ruta: str) -> str:
    """Retorna la seccio de la pagina, sense el prefix d'idioma."""
    parts = ruta.strip("/").split("/")
    if parts and parts[0] in ("es", "en"):
        parts = parts[1:]
    return parts[0] if parts and parts[0] else "(portada)"


def analitza(fitxer: str) -> dict:
    html = open(fitxer, encoding="utf-8", errors="replace").read()
    cap = html.split("</head>")[0]
    titol = re.search(r"<title>(.*?)</title>", html, re.S)
    # El minificador pot fer servir cometes simples si el valor en porta
    desc = re.search(r"""<meta name=description content=(?:"([^"]*)"|'([^']*)')""", cap)
    robots = re.search(r"""<meta name=robots content=(?:"([^"]*)"|'([^']*)')""", cap)
    es_alias = "http-equiv=refresh" in cap
    return {
        "ruta": fitxer.replace(PUBLIC, "").replace("/index.html", "/"),
        "titol": titol.group(1) if titol else "",
        # Es mesura sobre el text descodificat: «&amp;» ocupa set caracters a
        # l'HTML pero nomes un al text que llegeix el cercador.
        "desc": html_lib.unescape((desc.group(1) or desc.group(2))) if desc else "",
        "robots": (robots.group(1) or robots.group(2)) if robots else "",
        "alias": es_alias,
        "canonical": bool(re.search(r"<link rel=canonical", cap)),
        "hreflang": len(re.findall(r"hreflang=[A-Za-z-]+ href=", cap)),
        "ld": LD.findall(html),
    }


def main() -> int:
    fitxers = sorted(glob.glob(os.path.join(PUBLIC, "**", "index.html"), recursive=True))
    if not fitxers:
        print("No hi ha HTML a public/. Executa abans: hugo --minify")
        return 1

    pagines = [p for p in (analitza(f) for f in fitxers) if not p["alias"]]
    errors = 0

    sense_canonical = [p["ruta"] for p in pagines if not p["canonical"]]
    sense_hreflang = [p["ruta"] for p in pagines if p["hreflang"] < 4]
    generic = [p["ruta"] for p in pagines if p["desc"] in DESC_GENERICA]
    llargues = [p["ruta"] for p in pagines if len(p["desc"]) > 160]

    titols = collections.defaultdict(list)
    for p in pagines:
        idioma = p["ruta"].split("/")[1] if p["ruta"].startswith(("/es/", "/en/")) else "ca"
        titols[(idioma, p["titol"])].append(p["ruta"])
    repetits = {k: v for k, v in titols.items() if len(v) > 1 and k[1]}

    tipus = collections.Counter()
    invalid = []
    per_seccio = collections.defaultdict(set)
    for p in pagines:
        for blob in p["ld"]:
            try:
                d = json.loads(blob)
            except Exception:
                invalid.append(p["ruta"])
                continue
            for it in d if isinstance(d, list) else [d]:
                t = it.get("@type")
                tipus[t] += 1
                per_seccio[seccio(p["ruta"])].add(t)

    noindex = [p["ruta"] for p in pagines if "noindex" in p["robots"]]

    print(f"Pagines analitzades: {len(pagines)}")
    print(f"\nDescripcio generica del lloc (hauria de ser nomes la portada): {len(generic)}")
    if len(generic) > 3:
        for r in generic[:10]:
            print("  ", r)
    print(f"Descripcions de mes de 160 caracters: {len(llargues)}")
    print(f"Pagines sense canonical: {len(sense_canonical)}")
    print(f"Pagines amb menys de 4 hreflang: {len(sense_hreflang)}")
    print(f"Titols repetits dins d'un idioma: {len(repetits)}")
    for (idioma, titol), rutes in list(repetits.items())[:5]:
        print(f"  [{idioma}] {titol} -> {len(rutes)} pagines")
    print(f"\nJSON-LD invalid: {len(invalid)}")
    if invalid:
        errors += len(invalid)
        for r in invalid[:10]:
            print("  ", r)
    print("Tipus de schema:", dict(tipus.most_common()))
    for s, t in sorted(per_seccio.items()):
        print(f"  {s:14} {sorted(t)}")
    print(f"\nPagines amb noindex: {noindex or 'cap'}")

    if sense_canonical or sense_hreflang:
        errors += len(sense_canonical) + len(sense_hreflang)

    print("\nOK" if not errors else f"\n{errors} errors")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
