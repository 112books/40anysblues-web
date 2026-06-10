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
- **Password gate:** JS localStorage, contrasenya a `hugo.toml → params.site_password`
- **Analytics:** GoatCounter (pendent — `params.goatcounter = ''`)
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
  password_protected = true
  site_password = '...'        # veure CLAUDE_privat.md a obsidian-projectes
  goatcounter = ''
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
    │   ├── _default/baseof.html         # base: favicon, fonts, header, footer, password
    │   ├── musics/list.html             # llistat amb filtres JS
    │   ├── musics/single.html           # fitxa músic (born/death, instruments, bandes)
    │   ├── page/projecte.html           # stats, llibres, autors, logos, cita Dixon
    │   ├── partials/header.html         # logo + nav + cerca
    │   ├── partials/footer.html         # legal + xarxes socials
    │   ├── partials/og.html             # Open Graph / Twitter Card
    │   └── partials/scroll-utils.html  # progress bar + back-to-top
    └── static/css/main.css
```

---

## Convencions de contingut

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
- [ ] GoatCounter: afegir ID a `hugo.toml → params.goatcounter`
- [ ] Brevo DNS: verificar propagació SPF/DKIM, traduir templates al català

### Contingut
- [ ] Fotografies dels músics → `content/ca/musics/{id}/`
- [ ] Bios en castellà i anglès
- [ ] Schema markup: Organization, Person

### Funcionalitats
- [ ] Tooltip Wikipedia per a músics externs referenciats a les bios
- [ ] WebP + srcset per a imatges (Hugo image processing)
- [ ] Traduccions ES/EN: estratègia pendent de decidir
