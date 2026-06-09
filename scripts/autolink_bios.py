#!/usr/bin/env python3
"""
Auto-link musician name mentions in biography text.
Dry-run by default. Run with --apply to modify files.
"""
import os, re, sys

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'ca', 'musics')


def parse_md(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if not text.startswith('---'):
        return {}, text, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text, text
    import re as _re
    fm = {}
    for line in parts[1].splitlines():
        m = _re.match(r'^(\w[\w_]*):\s*(.+)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm, parts[2], text


def collect_musicians(content_dir):
    """Returns sorted list of (name, url) longest-first."""
    result = []
    for slug in os.listdir(content_dir):
        idx = os.path.join(content_dir, slug, 'index.md')
        if not os.path.isfile(idx):
            continue
        fm, _, _ = parse_md(idx)
        name = fm.get('title', '').strip()
        if name:
            result.append((name, f'/musics/{slug}/'))
    # Longest names first to avoid partial matches
    result.sort(key=lambda x: len(x[0]), reverse=True)
    return result


def autolink_bio(bio, my_name, musicians):
    """Replace first occurrence of each other musician's name with a markdown link."""
    result = bio
    for name, url in musicians:
        if name == my_name:
            continue
        # Skip if already linked to this musician
        if f'({url})' in result:
            continue
        escaped = re.escape(name)
        # Match name not already inside a markdown link [...]
        pattern = re.compile(r'(?<!\[)' + escaped + r'(?!\]\()')
        m = pattern.search(result)
        if not m:
            continue
        # Make sure we're not inside an existing [...] block
        before = result[:m.start()]
        if before.count('[') > before.count(']'):
            continue
        result = result[:m.start()] + f'[{name}]({url})' + result[m.end():]
    return result


def main():
    apply = '--apply' in sys.argv
    musicians = collect_musicians(CONTENT_DIR)
    print(f"Músics trobats: {len(musicians)}\n")

    total_links = 0
    modified = 0

    for slug in sorted(os.listdir(CONTENT_DIR)):
        idx = os.path.join(CONTENT_DIR, slug, 'index.md')
        if not os.path.isfile(idx):
            continue

        fm, body, original = parse_md(idx)
        my_name = fm.get('title', '').strip()
        if not body.strip():
            continue

        new_body = autolink_bio(body, my_name, musicians)

        if new_body != body:
            new_links = new_body.count('](/musics/') - body.count('](/musics/')
            total_links += new_links
            modified += 1

            # Show which names were linked
            added = []
            for name, url in musicians:
                if f'({url})' in new_body and f'({url})' not in body:
                    added.append(name)
            print(f"  {my_name}: {', '.join(added)}")

            if apply:
                parts = original.split('---', 2)
                new_content = f"---{parts[1]}---{new_body}"
                with open(idx, 'w', encoding='utf-8') as f:
                    f.write(new_content)

    print(f"\n{'Aplicat' if apply else 'Previsualització'}: {total_links} links en {modified} fitxers")
    if not apply:
        print("Executa amb --apply per modificar els fitxers.")


if __name__ == '__main__':
    main()
