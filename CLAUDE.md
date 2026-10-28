# 40 Anys de Blues a Barcelona — Web

Hugo SSG per al projecte fotogràfic/biogràfic dels 40 anys de l'escena blues barcelonina.

**URL producció:** https://40anysblues.112books.eu/
**Directori web (aquest repo):** `/Volumes/1TbExt/Obsidian/hugo-websites/40anysblues-web/`
**Directori fitxes músics:** `/Volumes/1TbExt/Obsidian/Projectes/Projectes/112Books/40anysBluesBarcelona/`

---

## Arquitectura — DOS REPOS, NO UN

| Repo | Visibilitat | Contingut | Mai tocar |
|------|-------------|-----------|-----------|
| `112books/obsidian-projectes` | Privat | `_fitxes/`, `scripts/`, `docs/` | `web/` (eliminat del tracking) |
| `112books/40anysblues-web` | Públic | Tot el codi Hugo | — |

**`web/` ja NO existeix a `obsidian-projectes`** (eliminat el 2026-06-10 per evitar conflictes de merge).

---

## Font de veritat: `_fitxes/*.md`

**MAI editar `content/ca/musics/` directament.** Aquests fitxers són generats per Python.
Totes les correccions (noms de bandes, bios, dates, etc.) es fan a `_fitxes/` i es re-exporta.

### Flux complet de dades

```
obsidian-projectes/_fitxes/*.md   ← EDITAR AQUÍ
         ↓
scripts/generate-exports.py
         ↓
├── content/ca/musics/{id}/index.md   (web Hugo)
├── data/stats.yaml                   (estadístiques)
├── exports/bios-ca.rtf               (Affinity Publisher)
└── exports/musics.csv                (Affinity Data Merge)
```

### Correcció de fitxes + deploy (flux normal)

```bash
# 1. Editar fitxes a obsidian-projectes
cd /Volumes/1TbExt/Obsidian/Projectes/Projectes/112Books/40anysBluesBarcelona

# 2. Regenerar contingut web
python3 scripts/generate-exports.py

# 3. Copiar contingut generat cap al repo web
rsync -av --delete web/content/ca/musics/ \
  /Volumes/1TbExt/Obsidian/hugo-websites/40anysblues-web/content/ca/musics/
cp web/data/stats.yaml \
  /Volumes/1TbExt/Obsidian/hugo-websites/40anysblues-web/data/stats.yaml

# 4. Pujar fitxes (repo privat)
cd /Volumes/1TbExt/Obsidian/Projectes
git add Projectes/112Books/40anysBluesBarcelona/_fitxes/
git add Projectes/112Books/40anysBluesBarcelona/scripts/
git commit -m "..." && git push

# 5. Pujar web (repo públic) → CI/CD fa el deploy automàticament
cd /Volumes/1TbExt/Obsidian/hugo-websites/40anysblues-web
git add content/ca/musics/ data/stats.yaml
git commit -m "..." && git push
```

### Canvis de templates/CSS/JS (flux web)

```bash
# Editar directament a 40anysblues-web, commit i push
cd /Volumes/1TbExt/Obsidian/hugo-websites/40anysblues-web
# ... editar themes/40anys/ o content/ca/ (no musics/)
git add ... && git commit -m "..." && git push
```

### Servidor local

```bash
cd /Volumes/1TbExt/Obsidian/hugo-websites/40anysblues-web
hugo server --buildDrafts --disableFastRender
# http://localhost:1313/
```

---

## Portada del llibre: porta programada i panell lateral

Tota la informació de la presentació, la venda i la reserva del llibre viu al
parcial `themes/40anys/layouts/partials/llibre-popup.html`. Substitueix els
antics `coming-soon.html` (overlay «Pròximament») i `newsletter-popup.html`
(pestanya del butlletí), que es van eliminar.

### Comportament programat per dates

| Moment (hora de Barcelona) | Estat |
|---|---|
| Fins a `params.esdeveniment.obertura` (6/11/2026, 18:00) | Web tancat: només el pop-up centrat, fons fosc, desplaçament bloquejat i contingut `inert`. El pop-up no es pot tancar. |
| A partir de l'obertura | Web obert per a tothom. El panell apareix a la dreta 5 segons, s'amaga sol i queda la pestanya vertical «El llibre». |
| Segons la data | El contingut canvia sol: reserva oberta, reserva tancada, dia de la presentació (des d'una hora abans) i venda posterior. |

- El càlcul es fa al navegador amb les dates de `hugo.toml` i es revisa cada
  30 segons: si algú té la pàgina oberta quan arriba l'hora, el web s'obre i el
  text s'actualitza sol.
- Les dates són instants absoluts (acaben en `+01:00`): l'obertura és a les
  18:00 de Barcelona per a qualsevol visitant, sigui quina sigui la seva zona
  horària.
- Si el visitant té el rellotge desajustat, veurà l'obertura abans o després.
- Amb JavaScript desactivat no apareix la porta: el web es veu sense pop-up.

### Configuració

Les dates, els preus i els textos són a `hugo.toml` (`[params.esdeveniment]`
i `[params.venda]`). Per canviar la presentació cal tocar `inici`, `obertura`,
`data_text`, `data_curta`, `reserva_fins`, `reserva_fins_text` i també
`static/40anysblues.ics`. Un cop fet: commit i push; el desplegament és
automàtic i no cal tocar res el dia de la presentació.

**No hi ha venda en línia.** Tots els modes acaben en un correu a
`params.venda.email` amb l'assumpte de `params.venda.assumpte`; el paràmetre
de botiga en línia es va retirar expressament.

### Verificació abans de publicar

```bash
hugo --minify --cleanDestinationDir --baseURL 'https://40anysblues.112books.eu/'

# La porta i les dates han de sortir a l'HTML generat:
grep -o 'data-obertura=[^ >]*' public/index.html
grep -c 'lb-panel' public/index.html

# El recompte de músics ha de coincidir amb les fitxes i amb data/stats.yaml:
ls -d content/ca/musics/*/ | wc -l
grep total_musics data/stats.yaml
```

El canvi de mode del panell es pot provar sense esperar la data: es pot simular
amb el rellotge del navegador o canviant temporalment `obertura` en local.

---

## Ús del web com a eina de revisió

El web és útil per detectar errors visualment (bandes duplicades, malnoms incorrectes, bios incompletes). El flux és:

1. Navegar el web en local → detectar error
2. Corregir a `_fitxes/{músic}.md` (obsidian-projectes)
3. Re-exportar i sincronitzar (flux de dalt)

El web **no és** l'editor — és el visualitzador de qualitat.

---

## Stack tècnic

- **Hugo** v0.159+ · tema propi `40anys` (a `themes/40anys/`)
- **Idioma actiu:** Català (CA). Castellà i anglès preparats però `disabled = true`
- **Password gate:** desactivat (`password_protected = false`); el mecanisme (JS + localStorage) continua disponible
- **Portada / panell del llibre:** `partials/llibre-popup.html`, programat per dates (vegeu "Portada del llibre")
- **Analytics:** GoatCounter actiu (`params.goatcounter = '40anysbluesbcn'`)
- **CI/CD:** GitHub Actions → deploy a `40anysblues.112books.eu`

---

## Configuració Hugo (`hugo.toml`)

```toml
baseURL = 'https://40anysblues.112books.eu/'
theme = '40anys'
defaultContentLanguage = 'ca'
defaultContentLanguageInSubdir = false   # CA a l'arrel, sense prefix /ca/

[languages.ca]
  contentDir = 'content/ca'             # CRÍTIC: sense això les URLs van a /ca/*
  weight = 1

[taxonomies]
  instrument = 'instruments'   # → /instruments/{slug}/
  banda = 'bands'              # → /bands/{slug}/

[params]
  password_protected = false
  goatcounter = '40anysbluesbcn'
  telegram = 'https://t.me/blues40anysbcn'
  telegram_name = '40 anys de blues a Barcelona'
  author = 'Joan Linux'

# Dates i textos de la presentació i de la venda del llibre (font única)
[params.esdeveniment]
  inici = '2026-11-06T19:00:00+01:00'       # presentació
  obertura = '2026-11-06T18:00:00+01:00'    # una hora abans: el web s'obre sol
  data_text = '6 de novembre · 19h'
  data_curta = '6 de novembre'
  lloc = 'Centre Cultural Collblanc La Torrassa'
  # ...

[params.venda]
  preu = '38'
  preu_soci = '33'
  email = 'info@societatbluesbarcelona.org'
  reserva_fins = '2026-11-04T23:59:59+01:00'
  reserva_fins_text = 'dimecres 4 de novembre'
```

---

## Estructura de directoris

```
40anysblues-web/
├── hugo.toml
├── content/ca/
│   ├── _index.md                        # homepage data
│   ├── musics/                          # GENERAT per Python — no editar
│   │   ├── _index.md                    # intro editorial (sí editable)
│   │   └── {id}/index.md               # fitxa de músic (NO editar, regenerar)
│   ├── historia/_index.md               # text Manuel López Poy
│   ├── sales/_index.md + {sala}/        # temples del blues
│   ├── entitats/_index.md + {entitat}/  # qui dona suport
│   ├── autors/{autor}/                  # fitxes d'autors
│   ├── projecte/index.md               # El Projecte (layout especial)
│   ├── cerca/                           # cerca full-text
│   ├── butlleti/, contacte/             # pàgines de servei
│   └── legal/                           # avís legal, cookies, privacitat
├── data/
│   └── stats.yaml                       # GENERAT per Python
├── static/
│   ├── autors/                          # fotos Joan Linux, Manolo Poy
│   ├── llibres/                         # portades
│   └── logotips/                        # logos del projecte + entitats
└── themes/40anys/
    ├── layouts/
    │   ├── _default/baseof.html         # base: favicon, fonts, header, footer, panell del llibre
    │   ├── musics/list.html             # llistat amb filtres JS
    │   ├── musics/single.html           # fitxa músic (born/death, instruments, bandes)
    │   ├── page/projecte.html           # stats, llibres, autors, logos, cita Dixon
    │   ├── partials/header.html         # logo + nav + cerca
    │   ├── partials/footer.html         # legal + xarxes socials
    │   ├── partials/og.html             # Open Graph / Twitter Card
    │   ├── partials/llibre-popup.html   # porta + panell del llibre (dates a hugo.toml)
    │   └── partials/scroll-utils.html  # progress bar + back-to-top
    └── static/css/main.css
```

---

## Convencions de contingut

### Idioma i estil
- **Només català.** No fem servir el castellà en cap comunicació, text ni document del projecte. Si algú no ho entén, que ho demani.
- **Sense emoticones.** No fem servir emojis ni emoticones enlloc (web, correus, xarxes socials, documentació).


### index.md vs _index.md
- **`_index.md`** → secció amb sub-pàgines (musics/, sales/, historia/)
- **`index.md`** → pàgina individual (musics/{id}/index.md, projecte/index.md)

### Fitxes de músic — frontmatter estàndard
```yaml
title: "Nom de Pantalla"      # malnom si en té, sinó nom complet
nom_complet: "Nom Complet"
malnom: "Alias"
born_year: 1965
born_city: "Barcelona"
death_year: 2020              # opcional, si escau
instruments: ["Guitarra", "Veu"]
bands: ["Nom Banda 1", "Nom Banda 2"]
ordre: 42
draft: false
session_date: "15/03/2021"
```

### Capitalització Catalan
Títols i menús: primera paraula + noms propis en majúscula, resta minúscula.
- ✓ "Els temples del blues"
- ✗ "Els Temples Del Blues"

### Signatures d'autor
Sempre cursiva amb link a fitxa: `*[Manuel López Poy](/autors/manuel-lopez-poy/)*`

---

## Tasques pendents

### Alta prioritat
- [ ] Brevo DNS: traduir templates al català
- [ ] Comprovar el 6/11 a les 18:00 que el web s'obre sol i el panell es plega als 5 segons
- [ ] Confirmar el recompte final de músics: 148 documentats (fitxes = pàgines). Si el llibre imprès en té més, calen les fitxes que falten

### Contingut
- [ ] Fotografies dels músics → `content/ca/musics/{id}/`
- [ ] (Futur, no ara) Valorar traducció de les bios a l'anglès
- [ ] Schema markup: Organization, Person

### Funcionalitats
- [ ] Tooltip Wikipedia per a músics externs referenciats a les bios
- [ ] WebP + srcset per a imatges (Hugo image processing)
