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
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

SITE = os.environ.get("GOATCOUNTER_SITE", "https://40anysbluesbcn.goatcounter.com")
TOKEN = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
OUT = os.environ.get("STATS_OUT", "static/stats-data.json")
PERIODS = (1, 7, 30, 90, 365, 'total')
QR_PATH = "/qr-llibre"


def api(path, params, intents=4):
    url = SITE + "/api/v0" + path + "?" + urllib.parse.urlencode(params)
    ultim = None
    for i in range(intents):
        try:
            req = urllib.request.Request(url, headers={"Authorization": "Bearer " + TOKEN})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except Exception as e:
            ultim = e
            time.sleep(2 * (i + 1))
    raise ultim


def main():
    if not TOKEN:
        print("Sense GOATCOUNTER_TOKEN: no es generen les estadístiques", file=sys.stderr)
        return 0

    # Mateixa franja que calculava la pàgina: inclou el dia d'avui (hora de Barcelona).
    today = datetime.now(timezone.utc).date()   # GoatCounter compta els dies en UTC
    out = {"generated": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="minutes"), "qr_path": QR_PATH, "periods": {}}

    for days in PERIODS:
        end = today
        if days == 'total':
            start = date(2020, 1, 1)   # inici del projecte
        else:
            start = today - timedelta(days=days - 1)
        rng = {"start": start.isoformat(), "end": end.isoformat()}
        # L'API de GoatCounter perd el darrer dia si la finestra es d'un sol dia;
        # demanem un dia mes i despres filtrem pel rang real.
        qstart = start - timedelta(days=1)
        try:
            out["periods"][str(days)] = {
                "range": rng,
                "hits": api("/stats/hits", {"limit": 500, "start": qstart.isoformat(), "end": rng["end"]}),
                "refs": api("/stats/toprefs", {"limit": 20, "start": qstart.isoformat(), "end": rng["end"]}),
            }
        except Exception as e:
            print("AVIS: no s ha pogut baixar el periode " + str(days) + ": " + str(e), file=sys.stderr)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print("escrit", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
