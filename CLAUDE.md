# 40 Anys de Blues a Barcelona — Web

Lloc web estàtic generat amb Hugo per al projecte fotogràfic i biogràfic dels 40 anys de l'escena blues barcelonina.

**URL producció:** https://40anysblues.112books.eu/
**Directori arrel del web:** `web/` (dins del vault Obsidian del projecte)
**Directori del projecte:** `Projectes/112Books/40anysBluesBarcelona/`

---

## Stack tècnic

- **Hugo** v0.159+ · tema propi `40anys` (a `themes/40anys/`)
- **Idioma actiu:** Català (CA). Castellà i anglès preparats però `disabled = true`
- **Password gate:** JS localStorage, contrasenya a `hugo.toml` → `params.site_password`
- **Analytics:** GoatCounter (pendent configurar — `params.goatcounter = ''`)
- **Font de dades:** Obsidian vault → `scripts/generate-exports.py` → `web/content/ca/musics/`

---

## Flux de dades

```
_fitxes/*.md (Obsidian)
    ↓
scripts/generate-exports.py
    ↓
web/content/ca/musics/{id}/index.md   ← pàgina de cada músic
web/data/stats.yaml                   ← estadístiques en viu
    ↓
hugo build → web/public/
```

**Per actualitzar el contingut dels músics**, sempre cal executar:
```bash
cd Projectes/112Books/40anysBluesBarcelona
python3 scripts/generate-exports.py
cd web && hugo
```

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
  site_password = '...'        # veure CLAUDE_privat.md
  goatcounter = ''             # afegir ID quan es configuri
```

---

## Estructura de directoris

```
web/
├── hugo.toml
├── content/ca/              # tot el contingut en català
│   ├── _index.md            # homepage data
│   ├── musics/              # 147 músics (generat per Python)
│   │   ├── _index.md        # secció: llistat amb filtres JS
│   │   └── {id}/index.md   # pàgina individual de cada músic
│   ├── historia/_index.md   # text de Manolo Poy
│   ├── sales/               # temples del blues
│   │   ├── _index.md        # secció llista les 11 sales
│   │   └── {sala}.md        # pàgina individual de cada sala
│   ├── entitats/_index.md   # qui dona suport (pàgines individuals PENDENTS)
│   ├── projecte/index.md    # El Projecte (usa layout 'projecte')
│   └── cerca/               # pàgina de cerca full-text
├── data/
│   └── stats.yaml           # auto-generat per generate-exports.py
├── static/
│   ├── autors/              # fotos dels autors (Joan Linux, Manolo Poy)
│   ├── llibres/             # portades dels llibres
│   └── logotips/            # logos del projecte
└── themes/40anys/
    ├── layouts/
    │   ├── _default/
    │   │   ├── baseof.html  # base: favicon, fonts, header, footer, password gate
    │   │   ├── single.html  # pàgina genèrica (historia, entitats, sales individuals)
    │   │   └── list.html    # secció/taxonomia genèrica
    │   ├── musics/
    │   │   ├── list.html    # llistat músics amb filtres JS
    │   │   └── single.html  # fitxa de músic (instruments/bandes clickables)
    │   ├── page/
    │   │   ├── projecte.html  # layout especial amb stats, llibres, autors
    │   │   └── cerca.html     # pàgina de cerca
    │   ├── taxonomy/        # llistats de taxonomia (instruments, bandes)
    │   ├── bands/           # pàgines de bandes
    │   ├── partials/
    │   │   ├── header.html      # logo rodó + nav + buscador
    │   │   ├── footer.html      # dos columnes: Powered by LinuxBCN | copyright + legal
    │   │   └── password-gate.html
    │   ├── index.html       # homepage: hero dos cols + músic aleatori + llibres
    │   └── index.json       # per cerca full-text
    └── static/css/main.css  # tot el CSS del tema
```

---

## Convencions de contingut

### index.md vs _index.md
- **`_index.md`** → branch bundle (secció amb sub-pàgines). Usar per: `musics/`, `sales/`, `historia/`, `entitats/`
- **`index.md`** → leaf bundle (pàgina individual). Usar per: cada músic `musics/{id}/index.md`, `projecte/index.md`

**No confondre mai `index.md` amb `_index.md` en seccions** — si s'usa `index.md` en una secció, les sub-pàgines no es generen.

### Fitxes de músic (generades per Python)
Frontmatter estàndard:
```yaml
title: "Nom de Pantalla"      # malnom si en té, o nom complet
nom_complet: "Nom Complet"
malnom: "Alias"
born_year: 1965
born_city: "Barcelona"
instruments: ["Guitarra", "Veu"]
bands: ["Nom Banda 1", "Nom Banda 2"]
ordre: 42                     # ordre al llibre (de l'arxiu docs/Ordre dels músics)
draft: false
```
La **display name** és el `nickname` si és diferent del `title`, sinó el `title`.

### Pàgines de secció amb layout específic
Si una pàgina necessita layout especial, cal afegir `layout: "nom"` al frontmatter **i** crear el fitxer a `layouts/page/nom.html` (per a pàgines individuals) o `layouts/{seccio}/list.html` (per a seccions).

### URLs de taxonomies
- Instruments: `/instruments/{slug}/` — llista tots els músics que toquen aquell instrument
- Bandes: `/bands/{slug}/` — llista tots els músics de la banda
Els links a les fitxes de músic usen `{{ $inst | urlize }}` per generar el slug correcte.

---

## Executar en local

```bash
cd web
hugo server --disableFastRender
# Disponible a http://localhost:1313/
```

Per compilar per a producció:
```bash
cd web && hugo
# Genera a web/public/
```

---

## Idiomes (multilingüisme)

Estructura preparada per ES i EN. Per activar un idioma nou:
1. Eliminar `disabled = true` al `[languages.es]` o `[languages.en]` del `hugo.toml`
2. Afegir `contentDir = 'content/es'` (o `en`) a la secció de l'idioma
3. Crear el directori `content/es/` amb el contingut traduït
4. Afegir les traduccions a `scripts/generate-exports.py` (camp `BIO_ES` o `BIO_EN` a les fitxes)

---

## Tasques pendents

### Alta prioritat
- [ ] Pàgines individuals d'entitats (`/entitats/capibola-blues/`, etc.) — com les 11 sales
- [ ] Pàgines legals (`/legal/avis-legal/`, `/legal/privacitat/`, `/legal/cookies/`) — el footer ja hi apunta
- [ ] Configurar GoatCounter (afegir ID a `hugo.toml → params.goatcounter`)

### Funcionalitats
- [ ] Desplegament GitHub Pages (repo `40anysbluesbcn`, acció CI/CD)
- [ ] Repo privat `40anysbluesbcn-docs` per documentació i fitxes
- [ ] Rol comprador (registre per QR del llibre) — Fase 2
- [ ] Traducció ES i EN — contingut i activació al config

### Contingut
- [ ] Fotografies dels músics (quan estiguin disponibles, van a `musics/{id}/`)
- [ ] Bios en castellà i anglès per a cada músic
- [ ] Pàgines individuals de les entitats

---

## Imatges disponibles

| Ruta | Descripció |
|------|-----------|
| `/logotips/40-anys-de-Blues-a-Barcelona-logo-Rounded-150x150.png` | Logo rodó · favicon + header |
| `/logotips/40-anys-de-Blues-a-Barcelona-logo.png` | Logo complet · homepage hero |
| `/autors/joan-linux-retrat-4-1-300x300.jpg` | Retrat Joan Linux |
| `/autors/2021-02-22-Poy-010-300x297.jpg` | Retrat Manolo Poy |
| `/llibres/Preses-Falses.png` | Portada Preses Falses (2022) |
| `/llibres/Captura-de-pantalla-2025-03-11-a-les-11.19.12-743x1024.png` | Portada 40 Anys (en preparació) |

---

## Estadístiques en viu (`data/stats.yaml`)

Auto-generat per `generate-exports.py`. El layout `projecte.html` i la homepage el llegeixen via `hugo.Data.stats`.

Camps: `total_musics`, `total_fotos`, `total_instruments`, `total_formacions`, `total_ciutats`, `any_primer`, `any_ultim`, `anys_escena`.
