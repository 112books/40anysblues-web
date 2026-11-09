#!/usr/bin/env python3
"""Comprova que tots els enllacos interns del web generat apunten a un fitxer
o a una pagina que existeix.

Es pensat per executar-se despres de «hugo» i abans de publicar:

    hugo --minify --baseURL "https://40anysblues.112books.eu/"
    python3 scripts/check-links.py public

Revisa els atributs href i src de tots els fitxers HTML generats. Els enllacos
externs (http, https, mailto, tel, javascript, data) i les ancores pures (#)
se salten. Els enllacos interns amb parametres de consulta o fragment es
comproven pel cami, sense el fragment.

Us:
    python3 scripts/check-links.py [directori]

Sortida: 0 si tot quadra, 1 si hi ha enllacos trencats.
"""

from __future__ import annotations

import html.parser
import os
import sys
import urllib.parse


class Enllacos(html.parser.HTMLParser):
    """Recull href, src i srcset de cada etiqueta."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.enllacos: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        valors = dict(attrs)
        for attr in ("href", "src", "poster"):
            valor = valors.get(attr)
            if valor:
                self.enllacos.append(valor)
        srcset = valors.get("srcset")
        if srcset:
            for candidat in srcset.split(","):
                url = candidat.strip().split(" ")[0]
                if url:
                    self.enllacos.append(url)


def es_extern(url: str) -> bool:
    url = url.strip()
    if not url or url.startswith("#"):
        return True
    if url.startswith("//"):
        return True
    esquema = url.split(":", 1)[0].lower()
    return esquema in {"http", "https", "mailto", "tel", "javascript", "data", "ftp"}


def existeix(public: str, url: str, origen: str) -> bool:
    """Retorna True si l'URL interna resol a un fitxer o a una pagina generada."""
    cami = urllib.parse.urlsplit(url).path
    cami = urllib.parse.unquote(cami)
    if not cami:
        return True

    if cami.startswith("/"):
        desti = os.path.join(public, cami.lstrip("/"))
    else:
        desti = os.path.join(os.path.dirname(origen), cami)
    desti = os.path.normpath(desti)

    if os.path.isdir(desti):
        return os.path.isfile(os.path.join(desti, "index.html"))
    if os.path.isfile(desti):
        return True
    # Hugo tambe pot generar /pagina/ com a /pagina/index.html
    if not os.path.splitext(desti)[1]:
        return os.path.isfile(os.path.join(desti, "index.html"))
    return False


def main() -> int:
    public = sys.argv[1] if len(sys.argv) > 1 else "public"
    if not os.path.isdir(public):
        print(f"ERROR: no existeix el directori {public!r}; executa abans hugo.")
        return 1

    trencats = []
    total = 0
    for arrel, _, fitxers in os.walk(public):
        for nom in fitxers:
            if not nom.endswith(".html"):
                continue
            ruta = os.path.join(arrel, nom)
            parser = Enllacos()
            try:
                with open(ruta, encoding="utf-8") as f:
                    parser.feed(f.read())
            except UnicodeDecodeError:
                continue
            origen = os.path.relpath(ruta, public)
            for url in parser.enllacos:
                if es_extern(url):
                    continue
                total += 1
                if not existeix(public, url, ruta):
                    trencats.append((origen, url))

    for origen, url in trencats:
        print(f"ERROR: {origen}: enllac trencat -> {url}")

    if trencats:
        print(f"\n{len(trencats)} enllacos trencats de {total} revisats.")
        return 1
    print(f"Enllacos correctes ({total} revisats).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
