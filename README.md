# 40 Anys de Blues a Barcelona — Web

Lloc web estàtic generat amb Hugo. Desplegat automàticament a [40anysblues.112books.eu](https://40anysblues.112books.eu/) via GitHub Actions quan es fa push a `main`.

---

## Flux de treball: com sincronitzar en local

Aquest repo (`40anysblues-web`) és un directori dins el vault Obsidian (`obsidian-projectes`). **Són dos repos git independents.** Cal gestionar-los per separat.

### Abans de treballar (pull)

```bash
cd ~/Documents/Obsidian/obsidian-projectes/Projectes/112Books/40anysBluesBarcelona/web
git pull origin main
```

### Servidor local

```bash
cd ~/Documents/Obsidian/obsidian-projectes/Projectes/112Books/40anysBluesBarcelona/web
hugo server --disableFastRender
# → http://localhost:1313/
```

### Quan acabes (commit + push → deploy automàtic)

```bash
cd ~/Documents/Obsidian/obsidian-projectes/Projectes/112Books/40anysBluesBarcelona/web
git add -A
git commit -m "Descripció dels canvis"
git push origin main
```

El push dispara la GitHub Action que compila Hugo i desplega a GitHub Pages. En 1-2 minuts els canvis són visibles a producció.

### Sincronitzar també el vault Obsidian

Després de fer push al web, sincronitza el vault perquè no quedin desincronitzats:

```bash
cd ~/Documents/Obsidian/obsidian-projectes
git add -A
git commit -m "Sync web - descripció"
git push origin main
```

---

## Estructura del tema

```
themes/40anys/
├── layouts/          # plantilles Hugo
│   ├── index.html    # portada
│   ├── page/
│   │   └── projecte.html
│   ├── musics/       # fitxa músic
│   ├── autors/       # fitxa autor
│   └── partials/     # header, footer, breadcrumb
└── static/css/
    └── main.css      # tot el CSS
```

## Contingut

```
content/ca/
├── musics/           # fitxes de músics (generades per Python)
├── autors/           # els culpables (Joan Linux, Manolo Poy, Ricky Gil)
├── entitats/         # qui dona suport
├── sales/            # els temples del blues
├── historia/         # la història
└── projecte/         # el projecte
```

Per regenerar les fitxes de músics des del vault Obsidian:

```bash
cd ~/Documents/Obsidian/obsidian-projectes/Projectes/112Books/40anysBluesBarcelona
python3 scripts/generate-exports.py
```
