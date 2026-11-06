import glob, json, re, sys, urllib.parse, urllib.request, collections

ROOT = 'content/en'
LINK = re.compile(r'https://(ca|es)\.wikipedia\.org/wiki/([^)\s]+)')

links = collections.defaultdict(set)  # (lang, title) -> set()
for f in glob.glob(ROOT + '/**/*.md', recursive=True):
    for m in LINK.finditer(open(f, encoding='utf-8').read()):
        links[(m.group(1), m.group(2))].add(f)

print('enllaços únics ca/es:', len(links), 'fitxers:', len({f for s in links.values() for f in s}))

def query(lang, titles):
    out = {}
    for i in range(0, len(titles), 20):
        batch = titles[i:i+20]
        params = {'action': 'query', 'format': 'json', 'prop': 'langlinks',
                  'lllang': 'en', 'titles': '|'.join(batch), 'redirects': 1}
        url = 'https://' + lang + '.wikipedia.org/w/api.php?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': '40anysblues-web/1.0'})
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.load(r)
        q = data.get('query', {})
        norm = {n['from']: n['to'] for n in q.get('normalized', [])}
        redir = {r['from']: r['to'] for r in q.get('redirects', [])}
        pages = q.get('pages', {})
        for title, page in pages.items():
            t = page.get('title', title)
            ll = page.get('langlinks') or []
            if ll:
                out[t] = ll[0]['*']
        for src, dst in list(norm.items()) + list(redir.items()):
            dst2 = redir.get(dst, dst)
            if dst2 in out and src not in out:
                out[src] = out[dst2]
    return out

mapping = {}
for lang in ('ca', 'es'):
    titles = sorted({t for (l, t) in links if l == lang})
    res = query(lang, titles)
    print(lang, 'consultats:', len(titles), 'amb article anglès:', len(res))
    for t, en in res.items():
        mapping[(lang, t)] = en

# reescriu els fitxers
canviats = 0
total = 0
for f in sorted({f for s in links.values() for f in s}):
    s = open(f, encoding='utf-8').read()
    def repl(m):
        global total
        key = (m.group(1), m.group(2))
        if key in mapping:
            total += 1
            return 'https://en.wikipedia.org/wiki/' + mapping[key].replace(' ', '_')
        return m.group(0)
    new = LINK.sub(repl, s)
    if new != s:
        open(f, 'w', encoding='utf-8').write(new)
        canviats += 1

print('enllaços convertits:', total, 'fitxers afectats:', canviats)
