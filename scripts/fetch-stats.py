#!/usr/bin/env python3
"""Descarrega les estadístiques de GoatCounter durant la compilació.

Genera static/stats-data.json amb els períodes de 30, 90 i 365 dies perquè la
pàgina /stats/ no hagi de cridar l'API des del navegador: així no depèn de CORS,
no exposa el token i no falla si l'API té un problema puntual.

Variable d'entorn: GOATCOUNTER_TOKEN (secret del repositori).
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

SITE = os.environ.get("GOATCOUNTER_SITE", "https://40anysbluesbcn.goatcounter.com")
TOKEN = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
OUT = os.environ.get("STATS_OUT", "static/stats-data.json")
PERIODS = (30, 90, 365)
QR_PATH = "/qr-llibre"


def api(path, params):
    url = SITE + "/api/v0" + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + TOKEN})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    if not TOKEN:
        print("Sense GOATCOUNTER_TOKEN: no es generen les estadístiques", file=sys.stderr)
        return 0

    # Mateixa franja que calculava la pàgina: inclou el dia d'avui (hora de Barcelona).
    today = datetime.now(ZoneInfo("Europe/Madrid")).date()
    out = {"generated": today.isoformat(), "qr_path": QR_PATH, "periods": {}}

    for days in PERIODS:
        end = today
        start = today - timedelta(days=days - 1)
        rng = {"start": start.isoformat(), "end": end.isoformat()}
        out["periods"][str(days)] = {
            "range": rng,
            "hits": api("/stats/hits", {"limit": 500, **rng}),
            "refs": api("/stats/toprefs", {"limit": 20, **rng}),
        }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print("escrit", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
