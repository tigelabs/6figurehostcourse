"""Mark translatable units in the built page and export them for translation.
A unit is an element (or a wrapped text node) whose content is text plus inline tags only."""
import re, json, sys
from bs4 import BeautifulSoup, NavigableString, Tag, Comment

INLINE = {'strong', 'em', 'b', 'i', 'a', 'br', 'small', 'span', 'mark', 'sup', 'u'}
SKIP = {'script', 'style', 'textarea', 'svg', 'title'}
ATTRS = ('placeholder', 'aria-label', 'alt', 'data-ph')

def has_letters(s):
    return bool(re.search(r'[A-Za-zÀ-ÿ]', s))

def inline_only(el):
    for d in el.descendants:
        if isinstance(d, Tag):
            if d.name not in INLINE or d.get('id') or d.has_attr('data-show') or d.has_attr('data-count') or d.get('class') and set(d.get('class')) & {'esym', 'pcount', 'steps', 'st', 'brk', 'ring', 'n', 'tag', 'chip', 'icon-ph', 'mgmt-pct'}:
                return False
    return True

def tokenize(inner):
    """Replace tags that carry attributes with short tokens so the translator cannot break them."""
    toks = []
    def sub(m):
        tag = m.group(0)
        if re.fullmatch(r'<(strong|em|b|i|br|small|u|sup)>|<br/>', tag):
            return tag.replace('<br/>', '<br>')
        toks.append(tag)
        return '<x%d>' % len(toks)
    out = re.sub(r'<(?!/)[^>]+>', sub, inner)
    return out, toks

def run(html_in):
    m = re.search(r'<body>(.*?)<script>', html_in, flags=re.S)
    body = m.group(1)
    soup = BeautifulSoup('<div id="__root">' + body + '</div>', 'html.parser')
    root = soup.find(id='__root')
    units, order = {}, []
    def register(el):
        for mk in el.find_all('mark', class_='fill'):
            mk.string = ''
        inner = el.decode_contents()
        inner = re.sub(r'[ \t]*\n[ \t]*', '\n', inner) if 'src' in (el.get('class') or []) else re.sub(r'\s+', ' ', inner).strip()
        tok, toks = tokenize(inner)
        if tok not in units:
            units[tok] = dict(id=len(units) + 1, toks=toks, en=inner)
            order.append(tok)
        el['data-t'] = str(units[tok]['id'])
    def walk(el):
        if el.name in SKIP or el.get('id') in ('lbcap',):
            return
        direct = [c for c in el.children if isinstance(c, NavigableString) and not isinstance(c, Comment) and has_letters(str(c))]
        has_el = any(isinstance(c, Tag) for c in el.children)
        if el.name == 'mark':
            return
        if direct and inline_only(el) and (el.name not in ('div', 'section', 'article', 'nav', 'header', 'main', 'aside') or 'src' in (el.get('class') or [])):
            register(el); return
        if direct:
            for c in direct:
                sp = soup.new_tag('span'); c.wrap(sp); 
            # fallthrough: children (including the new spans) are walked below
        for c in list(el.children):
            if isinstance(c, Tag):
                if c.name == 'span' and not c.attrs and len(c.contents) == 1 and isinstance(c.contents[0], NavigableString) and has_letters(str(c.contents[0])):
                    register(c)
                else:
                    walk(c)
    walk(root)
    attrs = {}
    for el in root.find_all(True):
        for a in ATTRS:
            v = el.get(a)
            if v and has_letters(v) and not re.fullmatch(r'[\d#€$. ,/+-]+', v):
                attrs.setdefault(v, 0); attrs[v] += 1
    tas = {}
    for ta in root.find_all('textarea'):
        if ta.get('data-edit') and ta.get('id', '').startswith('ed-'):
            tas[ta['data-edit']] = ta.string or ''
    new_body = root.decode_contents()
    return html_in[:m.start(1)] + new_body + html_in[m.end(1):], units, order, attrs, tas

if __name__ == '__main__':
    src = open('/home/claude/site/index.html', encoding='utf-8').read()
    out, units, order, attrs, tas = run(src)
    words = sum(len(re.sub(r'<[^>]+>', ' ', u).split()) for u in order)
    taw = sum(len(v.split()) for v in tas.values())
    print('units', len(order), 'words', words, '| attrs', len(attrs), '| textareas', len(tas), 'words', taw)
    json.dump(dict(order=order, units=units, attrs=list(attrs), tas=tas), open('/home/claude/build/i18n_units.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
