#!/usr/bin/env python3
"""Comprova que les estadistiques del projecte siguin coherents.

Compara data/stats.yaml amb el contingut real de content/{ca,es,en}/musics/
i amb els fitxers de fotografia que hi ha a cada carpeta.

Us:
    python3 scripts/check-stats.py            # informe i codi de sortida
    python3 scripts/check-stats.py --quiet    # nomes els errors

Sortida: 0 si tot quadra, 1 si hi ha alguna incoherencia.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import yaml

ARREL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDIOMES = ("ca", "es", "en")
EXT_IMATGE = (".jpg", ".jpeg", ".png", ".webp")


def frontmatter(ruta: str) -> dict:
    """Retorna el frontmatter YAML d'una pagina de contingut."""
    with open(ruta, encoding="utf-8") as f:
        text = f.read().lstrip("\ufeff")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def carrega_musics(idioma: str) -> dict:
    """Retorna {id: frontmatter} de les fitxes d'un idioma."""
    musics = {}
    patro = os.path.join(ARREL, "content", idioma, "musics", "*", "index.md")
    for ruta in sorted(glob.glob(patro)):
        musics[os.path.basename(os.path.dirname(ruta))] = frontmatter(ruta)
    return musics


def recompte(musics: dict, camp: str) -> set:
    """Conjunt de valors distints d'un camp (llista) de totes les fitxes."""
    valors = set()
    for fm in musics.values():
        for valor in fm.get(camp) or []:
            if valor:
                valors.add(valor)
    return valors


def fotos_per_fitxa() -> dict:
    """Recompte de fitxers d'imatge a cada carpeta de music (versio CA)."""
    fotos = {}
    for carpeta in sorted(glob.glob(os.path.join(ARREL, "content", "ca", "musics", "*"))):
        if not os.path.isdir(carpeta):
            continue
        n = sum(
            1
            for fitxer in os.listdir(carpeta)
            if fitxer.lower().endswith(EXT_IMATGE)
        )
        fotos[os.path.basename(carpeta)] = n
    return fotos


def main() -> int:
    parser = argparse.ArgumentParser(description="Comprova les estadistiques del projecte.")
    parser.add_argument("--quiet", action="store_true", help="nomes mostra els errors")
    args = parser.parse_args()

    with open(os.path.join(ARREL, "data", "stats.yaml"), encoding="utf-8") as f:
        stats = yaml.safe_load(f) or {}

    errors = []
    avisos = []
    linies = []

    # 1. Nombre de pagines per idioma
    musics = {idioma: carrega_musics(idioma) for idioma in IDIOMES}
    total_musics = stats.get("total_musics")
    for idioma, fitxes in musics.items():
        linies.append(f"  pagines {idioma}: {len(fitxes)}")
        if total_musics is not None and len(fitxes) != total_musics:
            errors.append(
                f"total_musics ({total_musics}) no coincideix amb les pagines de {idioma} ({len(fitxes)})"
            )

    # 2. Mateix conjunt d'ids als tres idiomes
    ids_ca = set(musics["ca"])
    for idioma in IDIOMES[1:]:
        nomes = ids_ca - set(musics[idioma])
        sobren = set(musics[idioma]) - ids_ca
        if nomes:
            errors.append(f"{idioma}: falten {len(nomes)} fitxes que si son a CA: {sorted(nomes)[:5]}")
        if sobren:
            errors.append(f"{idioma}: te {len(sobren)} fitxes que no son a CA: {sorted(sobren)[:5]}")

    # 3. Comptadors calculats sobre CA
    calculats = {
        "total_instruments": len(recompte(musics["ca"], "instruments")),
        "total_formacions": len(recompte(musics["ca"], "bands")),
        "total_ciutats": len({fm.get("born_city") for fm in musics["ca"].values() if fm.get("born_city")}),
    }
    anys = [int(fm["born_year"]) for fm in musics["ca"].values() if fm.get("born_year")]
    if anys:
        calculats["any_primer"] = min(anys)
        calculats["any_ultim"] = max(anys)

    for camp, valor in calculats.items():
        linies.append(f"  {camp}: stats.yaml={stats.get(camp)} calculat={valor}")
        if stats.get(camp) != valor:
            errors.append(f"{camp}: stats.yaml diu {stats.get(camp)} i el contingut dona {valor}")

    # 4. Instruments i formacions han de tenir el mateix nombre de termes als tres idiomes
    for camp in ("instruments", "bands"):
        referencia = len(recompte(musics["ca"], camp))
        for idioma in IDIOMES[1:]:
            n = len(recompte(musics[idioma], camp))
            linies.append(f"  {camp} distints {idioma}: {n} (CA: {referencia})")
            if n != referencia:
                avisos.append(
                    f"{camp} a {idioma}: {n} termes distints en comptes de {referencia}; revisa les traduccions"
                )

    # 5. Fotografies
    fotos = fotos_per_fitxa()
    total_fitxers = sum(fotos.values())
    linies.append(f"  fitxers d'imatge a content/ca/musics: {total_fitxers}")
    linies.append(f"  total_fotos a stats.yaml: {stats.get('total_fotos')}")
    if stats.get("total_fotos") not in (None, total_fitxers):
        avisos.append(
            "total_fotos de stats.yaml ("
            + str(stats.get("total_fotos"))
            + ") no es el nombre de fitxers presents al web ("
            + str(total_fitxers)
            + "); es el recompte de fotografies declarades a les fitxes"
        )
    sense_foto = sorted(mid for mid, n in fotos.items() if n == 0)
    if sense_foto:
        avisos.append(f"{len(sense_foto)} fitxes sense cap fotografia: {sense_foto[:5]}")

    if not args.quiet:
        print("Estadistiques del projecte")
        print("\n".join(linies))
        print()

    for avis in avisos:
        print(f"AVIS: {avis}")
    for err in errors:
        print(f"ERROR: {err}")

    if errors:
        print(f"\n{len(errors)} incoherencies i {len(avisos)} avisos.")
        return 1
    print(f"\nTot quadra ({len(avisos)} avisos).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
