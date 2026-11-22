import os
import html
"""Build the course hub: content.txt (light markup + page pulls from the PDF) -> site/index.html"""
import json, re, sys, html, os

BLOCKS = {}
GDIR = os.environ['GUIDE_DIR']
TPL = open(os.path.join(GDIR, 'template.html'), encoding='utf-8').read()
SRC = open(os.path.join(GDIR, 'content.txt'), encoding='utf-8').read().split('\n')
warnings = []

def norm(s):
    return re.sub(r'\s+', ' ', s.replace('&amp;', '&')).strip().lower()

def pull(spec):
    m = re.match(r'@p(\d+)(?:-(\d+))?(.*)', spec)
    a, b, rest = int(m.group(1)), int(m.group(2) or m.group(1)), m.group(3)
    opts = re.findall(r'(from|until|skip|strip)\s+"([^"]+)"', rest)
    blocks = []
    for n in range(a, b + 1):
        blocks += BLOCKS[str(n)]
    def find(needle):
        for i, bl in enumerate(blocks):
            if norm(needle) in norm(bl['text'])[:90]:
                return i
        warnings.append('anchor not found: %s -> "%s"' % (spec, needle))
        return None
    opts_s = [o for o in opts if o[0] == 'strip']
    for kind, needle in opts:
        if kind == 'from':
            i = find(needle)
            if i is not None: blocks = blocks[i:]
    for kind, needle in opts:
        if kind == 'until':
            i = find(needle)
            if i is not None: blocks = blocks[:i]
    for kind, needle in opts:
        if kind == 'skip':
            i = find(needle)
            if i is not None: blocks = blocks[:i] + blocks[i + 1:]
    out, items = [], []
    def flush():
        if items:
            out.append('<ul>' + ''.join('<li>%s</li>' % x for x in items) + '</ul>')
            items.clear()
    for bl in blocks:
        if bl['type'] == 'ul':
            items.extend(bl['items'])
        else:
            flush()
            out.append(('<h4>%s</h4>' if bl['type'] == 'h' else '<p>%s</p>') % bl['html'])
    flush()
    res = '\n'.join(out)
    for kind, needle in opts:
        if kind == 'strip':
            for ch in needle: res = res.replace(ch, '')
            res = re.sub(r'<p>\s+', '<p>', res)
    return res

def VS(t):
    return re.sub(r'\b(vs\.?|versus)(?=\s)', r'<span class="vs">vs</span>', t)

def fills(text):
    t = html.escape(text, quote=False)
    return re.sub(r'\{\{(\w+)\|([^}]+)\}\}', r'<mark class="fill" data-fill="\1" data-ph="\2">[\2]</mark>', t)


NOTE_NIGHT = 'This is the price that guests will pay for your room per night. To estimate the nightly rate, I recommend doing two types of research:<ul><li>Check similar listings on the Airbnb platform.</li><li>Use a market data tool like AirROI to review local metrics.</li></ul>Airbnb applies platform fees and taxes of approximately 17%, depending on the country. These fees are typically paid by the guest. Therefore, the prices you see on Airbnb as a traveler usually already include this additional 17%.'
CCY = ['EUR', 'USD', 'CAD', 'BRL', 'IDR', 'THB', 'AUD', 'MXN', 'JPY', 'CHF', 'AED']
EXP = [
 ('util', 'Utilities', [('ex_elec', 'Electricity'), ('ex_gas', 'Gas (optional)'), ('ex_net', 'Internet'), ('ex_water', 'Water'), ('ex_ins', 'Insurance (optional)')]),
 ('team', 'Team', [('ex_cl1', 'Cleaner 1'), ('ex_cl2', 'Cleaner 2 (optional)'), ('ex_handy', 'Handyman'), ('ex_mgr', 'Manager (optional)'), ('ex_pool', 'Pool cleaner (optional)'), ('ex_gard', 'Gardener (optional)'), ('ex_acc', 'Accountant (optional)')]),
 ('other', 'Other costs', [('ex_sup', 'Supplies'), ('ex_maint', 'Monthly maintenance')]),
]
SETUP = [('su_kitchen', 'Kitchen'), ('su_living', 'Living room'), ('su_bed', 'Bedroom'), ('su_bath', 'Bathroom'), ('su_out', 'Outside area (optional)'), ('su_laundry', 'Laundry room')]
def erow(key, lab):
    return '<div class="erow"><label for="e-%s">%s</label><span class="esym"></span><input id="e-%s" data-field="%s" inputmode="decimal"></div>' % (key, lab, key, key)
def expenses_html():
    o = ['<div class="tool" id="expenses"><h5>Step 1 <span class="hsub">business expenses overview</span></h5>',
         '<p>Calculate your business expenses first. If you need help estimating any costs, use the AI prompt below. Once completed, your expenses automatically flow into the three calculators in step 2.</p>',
         '<div class="fields"><div class="field"><label for="e-ccy">Choose currency</label><select id="e-ccy" data-field="ccy">%s</select><small>Changes the currency everywhere in the course.</small></div></div>' % ''.join('<option>%s</option>' % c for c in CCY),
         '<div class="expgrid"><div class="expcol"><div class="label">Monthly costs</div>']
    for gid, gname, rows in EXP:
        o.append('<div class="egroup"><h6>%s</h6>%s<div class="erow tot"><span>Total</span><b id="ex-t-%s"></b></div></div>' % (gname, ''.join(erow(k, l) for k, l in rows), gid))
    o.append('</div><div class="expcol"><div class="label">One-time costs</div>')
    o.append('<div class="egroup"><h6>Set up</h6>%s<div class="erow tot"><span>Total</span><b id="ex-t-setup"></b></div></div>' % ''.join(erow(k, l) for k, l in SETUP))
    o.append('<p class="added">Not sure what the setup will cost? The <a href="#setup">setup checklist</a> gives you an estimated budget, room by room.</p>')
    o.append('<div class="out"><div><small>Total monthly costs</small><b id="ex-monthly"></b></div><div><small>Total one-time costs</small><b id="ex-onetime"></b></div></div>')
    o.append('</div></div>')
    o.append('<div class="copy"><header>AI prompt: estimate my costs<span><button type="button" class="btn-s cp">Copy</button></span></header><div class="src">You are an Airbnb business expert.\n\nI am planning an Airbnb property in <mark class="fill" data-fill="city" data-ph="DESTINATION">[DESTINATION]</mark>, with [# BEDROOMS] bedrooms, cleaned [CLEANING FREQUENCY PER MONTH] times per month.\n\nPlease give me realistic average monthly and one-time cost estimates for this destination, based on typical short-term rental operations.\n\nUse <mark class="fill" data-fill="ccy" data-ph="CURRENCY">[CURRENCY]</mark> for all numbers.\n\nBreak down the costs in the following structure:\nMonthly expenses: Utilities (electricity, gas if applicable, internet, water, insurance), Team (cleaner based on the cleaning frequency above, handyman, property manager if commonly used in this destination, pool cleaner if applicable, gardener if applicable, accountant / admin), Other monthly expenses (supplies such as toiletries and consumables based on turnover, maintenance reserve).\n\nOne-time setup costs: Kitchen setup, living room setup, bedroom setup, bathroom setup, laundry setup, outdoor / pool area if applicable.\n\nFor each cost, provide:\n- A realistic average range (low–high)\n- A recommended estimate to use for financial planning\n\nAlso mention:\n- Any costs that are commonly underestimated in this destination\n- Whether costs are higher or lower than average compared to similar markets\n\nKeep the answer practical, realistic, and suitable for plugging directly into an Airbnb profit &amp; ROI calculator.</div><div class="hint">Need a little help? Fill in your info in the brackets, then copy and paste into your AI assistant.</div>' + AILINKS + '</div>')
    o.append('</div>')
    return '\n'.join(o)

def fld(key, lab, note='', select=None):
    h = '<details class="help"><summary>What is this?</summary><div>%s</div></details>' % note if note else ''
    if select:
        return '<div class="field"><label for="pc-%s">%s</label><select id="pc-%s" data-field="%s">%s</select>%s</div>' % (key, lab, key, key, ''.join('<option value="%d">%d monthly rent%s</option>' % (n, n, '' if n == 1 else 's') if n else '<option value="0">0 monthly rent</option>' for n in select), h)
    return '<div class="field"><label for="pc-%s">%s</label><input id="pc-%s" data-field="%s" inputmode="decimal">%s</div>' % (key, lab, key, key, h)
N_ADMIN = 'Extra admin costs can include rental taxes, agency fees ...'
N_ROOMS = 'How many rooms are you going to rent?'
CALCS = [
 ('rent', 'Renting a property', 'Rental arbitrage', [fld('rent', 'Monthly rent', 'How much is the monthly rental?'), fld('r_dep', 'Security deposit', 'Select how many months of deposit the agency or owner is asking.', range(0, 6)), fld('r_admin', 'Extra admin costs', N_ADMIN), fld('rooms', 'Rooms', N_ROOMS), fld('price', 'Nightly price per room', NOTE_NIGHT)], ''),
 ('buy', 'Buying a property', 'Property owner', [fld('bp_price', 'Property price', 'How much does the property cost?'), fld('bp_admin', 'Extra admin costs', 'Extra admin costs can include purchase taxes, agency fees ...'), fld('bp_rooms', 'Rooms', N_ROOMS), fld('bp_night', 'Nightly price per room', NOTE_NIGHT)], ''),
 ('lease', 'Leasing a property', 'Leasehold', [fld('ls_price', 'Lease price', 'How much do you pay for the lease?'), fld('ls_admin', 'Extra admin costs', N_ADMIN), fld('ls_rooms', 'Rooms', N_ROOMS), fld('ls_night', 'Nightly price per room', NOTE_NIGHT)],
  '<p class="added">*A leasehold is when you rent a property long-term, often for several years, with the right to use it as your own. In places like Bali, foreigners can’t own land, so leaseholds are the most common way to legally control and profit from a property without actually buying it. You pay upfront or yearly, and in return, you get full use of the property for the length of the lease.</p>'),
]
CASES = ((1, 'Worst-case'), (2, 'Average'), (3, 'Best-case'))
def calc_panels():
    o = ['<div class="tabs" role="tablist" aria-label="Business model">']
    for k, tab, title, fields, note in CALCS:
        o.append('<button type="button" role="tab" data-tab="%s">%s</button>' % (k, tab))
    o.append('</div>')
    for k, tab, title, fields, note in CALCS:
        o.append('<div class="tool cpanel" data-panel="%s"><h5>%s <span class="hsub">profit calculator</span></h5><div class="label">Enter your data here</div><div class="fields">%s</div>' % (k, title, ''.join(fields)))
        o.append('<div class="out"><div><small>Total initial investment</small><b id="%s-init"></b><span class="brk" id="%s-brk"></span></div><div><small>Monthly expenses</small><b id="%s-exp"></b><span class="brk">From step 1. <button type="button" class="linkbtn" data-jump="expenses">Change them</button></span></div></div>' % (k, k, k))
        o.append('<div class="tw"><table><tr><th>Occupancy rate</th><th class="num">Monthly income</th><th class="num">Monthly costs</th><th class="num">Monthly profit</th><th class="num">Yearly profit</th><th class="num">ROI</th><th class="num">Break even</th></tr>')
        for i, case in CASES:
            o.append('<tr><td><span class="occ"><input id="pc-%s-occ%d" data-field="occ%d" inputmode="decimal" aria-label="%s occupancy rate in percent">%%</span><small>%s</small></td>' % (k, i, i, case, case)
                     + ''.join('<td class="num" id="%s-%s-%d"></td>' % (k, c, i) for c in ('inc', 'cost', 'prof', 'yr', 'roi', 'be')) + '</tr>')
        o.append('</table></div>')
        o.append('<details class="help"><summary>What do the columns mean?</summary><div><p><strong>Occupancy rate.</strong> The occupation rate is the rental percentage, like how many days your accommodation is rented vs empty. For example: if your property gets booked for 15 days in the month and the other 15 days are not rented, your occupation rate is 50%. Worst-case, average and best-case are the worst, average and best occupancy in the zone where you are going to start. You can change each percentage.</p><p><strong>Monthly income.</strong> How much you would earn per month before deducting any expenses — also called Monthly Gross Profit.</p><p><strong>Monthly costs.</strong> The costs to manage an Airbnb property: cleaners, cleaning products, handyman services, utility bills (water, electricity, gas, internet) ... You can change them in step 1.</p><p><strong>Monthly profit.</strong> Your estimated income after subtracting all recurring monthly costs, such as rent, team, utilities and cleaning costs.</p><p><strong>ROI.</strong> This is the annual return of investment in percentage.</p><p><strong>Break even.</strong> How long (in months) it will take to recover your initial investment.</p></div></details>')
        o.append('<p class="verdict" id="%s-sum"></p>' % k)
        o.append('<div><div class="label">5 year profit</div><div class="tw"><table><tr><th>Scenario</th><th class="num">×1 property</th><th class="num">×2 properties</th><th class="num">×4 properties</th></tr>'
                 + ''.join('<tr><td>%s</td>%s</tr>' % (case, ''.join('<td class="num" id="%s-y5-%d-%d"></td>' % (k, i, m) for m in (1, 2, 4))) for i, case in CASES)
                 + '</table></div><p class="added">Your estimated profit after 5 years with 1, 2 or 4 similar properties.</p></div>')
        o.append('<div class="chartcard"><div class="charthead"><strong>Profit and months for break even</strong><span class="legend"><span><i style="background:var(--s1)"></i>Profit</span><span><i style="background:var(--s2)"></i>Initial capital</span></span></div><div class="chartwrap"><svg id="%s-chart" class="chart" viewBox="0 0 680 300" role="img" aria-label="Line chart: cumulative profit rising and remaining initial capital falling until break even, at the average occupancy rate"></svg><div class="tipbox" id="%s-tip"></div></div><p class="added">At your average occupancy rate. The lines cross halfway to break even; the capital line reaches zero at break even.</p>' % (k, k))
        o.append('<div class="tw"><table><thead><tr><th class="num">Months</th><th class="num">Profit</th><th class="num">Initial capital</th></tr></thead><tbody id="%s-pts"></tbody></table></div></div>' % k)
        o.append('<div><p><strong>The table does not consider taxes as it changes in every country, you still need to consider:</strong></p><details class="help"><summary>Company income tax</summary><div>That’s ok if you want to start small and do not open a company, but you should be aware of the company income tax if in the future you plan to open a company to manage your properties.</div></details><details class="help"><summary>Touristic tax</summary><div>Some cities apply touristic taxes directly through the Airbnb platform. You need to check what applies at your place.</div></details><details class="help"><summary>Dividends income tax</summary><div>If you already have a company to manage your property and plan to take profit from the company to your personal account, you should consider the applicable dividend taxes where you are fiscal resident.</div></details></div>')
        o.append(note + '</div>')
    return '\n'.join(o)

ROAD_KEYS = {'Preparation': 'prep', 'Find property': 'find', 'Set up property': 'prop', 'Set up listing': 'list', 'Create your team': 'team', 'Set up systems': 'sys', 'Launch your listing': 'launch', 'Scale for 6 figures': 'scale'}

def setup_html():
    rows = [l.rstrip('\n').split('|') for l in open('/home/claude/build/setup.tsv', encoding='utf-8') if l.strip()]
    o, room, n, rooms = [], None, 0, []
    for item, rm, amount, imp, price, meas, notes in rows:
        n += 1
        if rm != room:
            if room is not None: o.append('</div></div>')
            room = rm; rooms.append(rm)
            o.append('<div class="phase" data-phase data-room="%s"><div class="phead"><h3>%s</h3><span class="pcount"></span></div><div class="slist">' % (html.escape(rm), rm))
        cls = {'Must-have': 'must', 'Recommended': 'rec', 'Nice to have': 'nice'}.get(imp, 'none')
        mq = re.match(r'\s*(\d+)', amount or ''); dq = int(mq.group(1)) if mq else 1
        unit_lbl = (amount or '')[mq.end():].strip() if mq else (amount or '')
        meta = meas or ''
        unit = (float(price) / dq) if price else 0
        o.append('<div class="srow" data-n="%d" data-imp="%s" data-unit="%.2f" data-dq="%d"><label class="scheck"><input type="checkbox" data-check="setup-%d" aria-label="I have this"></label><div class="sinfo"><strong>%s</strong>%s%s<span class="chip %s">%s</span></div><div class="sprices"><div><small>Qty</small><input class="sq" data-field="setup_qty_%d" inputmode="numeric" placeholder="%d" aria-label="Quantity"></div><div><small>Estimated</small><b class="sest"></b></div><div><small>Actual / item</small><input class="sa" data-field="setup_act_%d" inputmode="decimal" placeholder="" aria-label="Actual price per item"><span class="stot"></span></div></div><button type="button" class="sx" aria-label="I don’t need this" title="I don’t need this">✕</button></div>' % (
            n, cls, unit, dq, n, html.escape(item), '<small>%s</small>' % html.escape(meta) if meta else '', '<em>%s</em>' % html.escape(notes) if notes else '', cls, imp or 'Optional', n, dq, n))
    o.append('</div></div>')
    opts = ''.join('<option>%s</option>' % html.escape(r) for r in rooms)
    o.append('<div class="card sadd"><div class="label">Add your own item</div><div class="fields"><div class="field"><label for="sa-name">Item</label><input id="sa-name" autocomplete="off" placeholder="Example: Coffee grinder"></div><div class="field"><label for="sa-room">Room</label><select id="sa-room">%s</select></div><div class="field"><label for="sa-price">Estimated price</label><input id="sa-price" inputmode="decimal" placeholder="Example: 30"></div></div><button type="button" class="btn dark" id="sa-add">Add item</button></div>' % opts)
    o.append('<div class="phase dontneed"><div class="phead"><h3>Don’t need</h3></div><p class="added" id="setup-dont-empty">Tap ✕ on an item you don’t need and it moves here. Tap ↺ to put it back.</p><div class="slist" id="setup-dont"></div></div>')
    return '\n'.join(o)

AILINKS = '<div class="ai-links"><span>Copy and open in:</span><a href="https://chatgpt.com/" target="_blank" rel="noopener">ChatGPT</a><a href="https://gemini.google.com/" target="_blank" rel="noopener">Gemini</a><a href="https://claude.ai/" target="_blank" rel="noopener">Claude</a></div>'
dropped = []
lessons, groups, prompts = [], [], []
cur = None
i = 0
def emit(s):
    cur['html'].append(s)
def close_group():
    if cur and cur.get('open'):
        emit(cur['open']); cur['open'] = None
def close_part():
    close_group()
    if cur and cur.get('inpart'):
        emit('</section>'); cur['inpart'] = False

def open_group(kind, opener, closer):
    if cur.get('open') != closer or cur.get('okind') != kind:
        close_group(); emit(opener); cur['open'] = closer; cur['okind'] = kind

while i < len(SRC):
    line = SRC[i]; s = line.strip(); i += 1
    if s.startswith('::group '):
        groups.append(dict(name=s[8:].strip(), ids=[])); continue
    if s.startswith('::lesson '):
        f = [x.strip() for x in s[9:].split('|')]
        cur = dict(id=f[0], num=f[1], nav=f[2], eyebrow=f[3], title=f[4], script=f[5], sub=f[6] if len(f) > 6 else '',
                   tag=f[7] if len(f) > 7 else '', html=[], parts=[], tasks=0, done=None, inpart=False, open=None)
        lessons.append(cur); groups[-1]['ids'].append(cur['id']); continue
    if s == '::endlesson':
        close_part(); cur = None; continue
    if cur is None:
        continue
    if s.startswith('::video '):
        f = [x.strip() for x in s[8:].split('|')]
        ids = dict(kv.split(':') for kv in f[0].split()); cur.setdefault('vlangs', set()).update(ids)
        close_group()
        emit('<div class="video" %s><a class="vplay" target="_blank" rel="noopener"><i></i><span><b>Watch the video</b><small>%s</small></span></a></div>' % (' '.join('data-yt-%s="%s"' % kv for kv in ids.items()), f[1] if len(f) > 1 else ''))
        continue
    if s.startswith('::part '):
        close_part()
        title = s[7:].strip(); pid = '%s-p%d' % (cur['id'], len(cur['parts']) + 1)
        cur['parts'].append((pid, title)); cur['inpart'] = True
        emit('<section class="part" id="%s"><div class="eyebrow">Section %d</div><h2>%s</h2>' % (pid, len(cur['parts']), VS(title))); continue
    if s.startswith('::h '):
        close_group(); f = [x.strip() for x in s[4:].split('|')]
        _w = lambda t: set(re.findall(r'[a-z0-9]+', re.sub(r'&\w+;', ' ', t.lower()))) - {'and', 'for', 'the', 'to', 'a', 'vs', 'of', 'your', 'bonus'}
        _pw = _w(cur['parts'][-1][1]) if cur['parts'] else set()
        if cur['html'] and cur['html'][-1].startswith('<section class="part" id=') and _pw and len(_pw & _w(f[0])) >= 0.6 * len(_pw):
            if len(f) > 1: emit('<p class="sub">%s</p>' % f[1])
            dropped.append((cur['nav'], f[0])); continue
        emit('<h3>%s%s</h3>' % (VS(f[0]), ' <em>%s</em>' % f[1] if len(f) > 1 else '')); continue
    if s.startswith('::li '):
        cur['pending_li'] = s[5:].strip(); continue
    if s.startswith('@p'):
        close_group(); h = pull(s)
        if cur.get('pending_li'):
            assert '<ul>' in h, 'no list to add the item to'
            h = h.replace('<ul>', '<ul><li>%s</li>' % cur.pop('pending_li'), 1)
        emit(h); continue
    if s.startswith('::task '):
        open_group('task', '<div class="checklist"><div class="label">Your tasks</div>', '</div>')
        cur['tasks'] += 1
        cur.setdefault('tasklist', []).append(('%s-t%d' % (cur['id'], cur['tasks']), s[7:].strip()))
        emit('<label class="task"><input type="checkbox" data-task="%s-t%d"><span>%s</span></label>' % (cur['id'], cur['tasks'], s[7:].strip())); continue
    if s.startswith('::tip ') or s.startswith('::warn '):
        close_group(); k = 'tip' if s.startswith('::tip') else 'warn'
        emit('<p class="%s">%s</p>' % (k, s.split(' ', 1)[1].strip())); continue
    if s.startswith('::prompt ') or s.startswith('::edit '):
        close_group(); is_edit = s.startswith('::edit ')
        f = [x.strip() for x in s.split(' ', 1)[1].split('|')]
        body = []
        while SRC[i].strip() != '::end':
            body.append(SRC[i]); i += 1
        i += 1
        body = '\n'.join(body).strip('\n')
        if is_edit:
            key, title, hint = f[0], f[1], (f[2] if len(f) > 2 else 'Edit the parts in [brackets], then copy. Your changes are saved on this device.')
            block = ('<div class="copy"><header>%s<span><button type="button" class="btn-s ghost reset">Reset</button><button type="button" class="btn-s cp">Copy</button></span></header>'
                     '<textarea data-edit="%s" id="ed-%s" aria-label="%s" rows="%d">%s</textarea><div class="hint">%s</div></div>'
                     % (title, key, key, html.escape(title), min(max(body.count('\n') + 3, 6), 22), html.escape(body, quote=False), hint))
        else:
            block = ('<div class="copy"><header>%s<span><button type="button" class="btn-s cp">Copy</button></span></header><div class="src">%s</div></div>'
                     % (f[0], fills(body)))
            if re.match(r'(AI|ChatGPT) prompt', f[0]): block = block[:-6] + AILINKS + '</div>'
        emit(block)
        if not (is_edit and f[0].split('-')[0] in ('qr', 'sm')): prompts.append((cur['nav'], block))
        continue
    if s.startswith('::done '):
        cur['done'] = [x.strip() for x in s[7:].split('||')]; continue
    if s.startswith('::road '):
        f = [x.strip() for x in s[7:].split('|')]
        cur['road'] = cur.get('road', 0) + 1
        if cur.get('phase') != f[0]:
            close_group(); cur['phase'] = f[0]; cur['phn'] = cur.get('phn', 0) + 1
            emit('<div class="phase" data-phase data-ph="%s"><div class="phead"><h3>%s <span class="pweek" hidden></span></h3><span class="pcount"></span></div>' % (ROAD_KEYS.get(f[0], ''), f[0])); cur['open'] = '</div>'
        link = ''
        if len(f) > 2:
            tgt = '' if f[3].startswith('#') else ' target="_blank" rel="noopener"'
            link = '<a class="rlink" href="%s"%s>%s</a>' % (f[3], tgt, f[2])
        n = cur['road']
        cond = 'find' if f[0] == 'Find property' else 'furn' if f[1].startswith('Buy furniture') else 'shared' if f[1].startswith('Shared apartment') else ''
        emit('<div class="rrow"%s><label class="task soft"><input type="checkbox" data-check="road-%d"><span>%s</span></label>%s</div>' % (' data-cond="%s"' % cond if cond else '', n, f[1], link)); continue
    if s.startswith('::dl '):
        f = [x.strip() for x in s[5:].split('|')]
        open_group('res', '<div class="resgrid dl">', '</div>')
        btns = ''
        if f[1]: btns += '<a class="btn" href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(f[1]), 'Make your own copy' if '/copy' in f[1] else 'Edit the template in Google Drive')
        for part in [x.strip() for x in f[2].split(';') if x.strip()]:
            fn, lab = [y.strip() for y in part.split(':', 1)]
            btns += '<button type="button" class="btn dark" data-download="files/%s" data-name="%s">%s</button>' % (fn, fn, lab)
        emit('<div class="res"><h5>%s</h5><p>%s</p><div class="btnrow">%s</div></div>' % (f[0], f[3] if len(f) > 3 else '', btns)); continue
    if s == '::setup':
        close_group(); emit(setup_html()); continue
    if s.startswith('::res '):
        f = [x.strip() for x in s[6:].split('|')]
        open_group('res', '<div class="resgrid">', '</div>')
        tgt = '' if f[1].startswith('#') else ' target="_blank" rel="noopener"'
        emit('<div class="res"><h5>%s</h5><p>%s</p><a class="btn" href="%s"%s>%s</a></div>' % (f[0], f[3] if len(f) > 3 else '', html.escape(f[1]), tgt, f[2])); continue
    if s.startswith('::img '):
        close_group(); f = [x.strip() for x in s[6:].split('|')]
        emit('<figure><img src="img/%s" alt="%s" loading="lazy">%s</figure>' % (f[0], html.escape(f[1]), '<figcaption>%s</figcaption>' % f[2] if len(f) > 2 else '')); continue
    if s.startswith('::share '):
        close_part()
        emit('<div class="share"><div class="label" style="color:var(--ink)">Share your win</div><p><strong>%s</strong></p><a class="btn" href="https://instagram.com/6figurehost" target="_blank" rel="noopener">Message us on Instagram</a><small>@6figurehost</small></div>' % s[8:].strip()); continue
    if s == '::expenses':
        close_group(); emit(expenses_html()); continue
    if s == '::calcpanels':
        close_group(); emit(calc_panels()); continue
    if s == '::collect':
        close_group(); cur['collect'] = len(cur['html']); emit(''); continue
    if s == '':
        continue
    close_group() if not s.startswith('<label class="task') else None
    emit(line)

order = [l['id'] for l in lessons]
by = {l['id']: l for l in lessons}

def words(l):
    return len(re.sub(r'<[^>]+>', ' ', ' '.join(l['html'])).split())

# Bonus bundles: (name, icon, [lesson ids]). Add a new tuple here to create another bundle.
BUNDLES = [
    ('Operations template kit', '★', ['bonus-contracts', 'bonus-labels', 'bonus-inspections', 'bonus-checklists', 'bonus-booklets', 'bonus-sheet', 'bonus-declutter']),
]
nav = []
def _navlinks(ids, done_b):
    o = []
    for lid in ids:
        l = by[lid]
        if lid in ('home', 'kit'): continue
        if lid == 'roadmap':
            o.append('<a class="home" href="#roadmap"><span class="t">Your launch roadmap</span></a>'); continue
        _bd = next((bd for bd in BUNDLES if lid in bd[2]), None)
        if _bd:
            if _bd[0] in done_b: continue
            done_b.add(_bd[0])
            items = ''.join('<a href="#%s"><span class="n">%s</span><span class="t">%s</span></a>' % (x, by[x]['num'], by[x]['nav']) for x in _bd[2] if x in by)
            o.append('<details class="bundle"><summary><span class="n">%s</span><span class="t">%s<small>%d resources</small></span><span class="chev" aria-hidden="true"></span></summary><div class="bundle-items">%s</div></details>' % (_bd[1], _bd[0], len([x for x in _bd[2] if x in by]), items))
            continue
        o.append('<a href="#%s"><span class="n">%s</span><span class="t">%s</span>%s%s</a>' % (
            lid, ('<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5zM12 6.5v13"/></svg>' if lid == 'story' else l['num']), l['nav'], '<span class="tag">%s</span>' % l['tag'] if l['tag'] else '', '<span class="ring"></span>' if l['done'] else ''))
    return o
KIT_GROUPS = ('Your toolkit', 'Bonus resource library')
for g in groups:
    if g['name'] == KIT_GROUPS[1]: continue
    if g['name'] == KIT_GROUPS[0]:
        ids = [x for gg in groups if gg['name'] in KIT_GROUPS for x in gg['ids']]
        _pref = ['calculator', 'setup', 'manual'] + list(BUNDLES[0][2]) + ['finance', 'bonus-mistakes']
        ids = [x for x in _pref if x in ids] + [x for x in ids if x not in _pref]
        inner = ''.join(_navlinks(ids, set()))
        nav.append('<h6>Bonus</h6>')
        nav.append('<details class="bundle kitdd"><summary><a href="#kit" class="kitlink"><span class="n">★</span><span class="t">Your host starter kit</span></a><span class="chev" aria-hidden="true"></span></summary><div class="bundle-items">%s</div></details>' % inner)
        continue
    if g['name'] != '-':
        nav.append('<h6>%s</h6>' % g['name'])
    nav.extend(_navlinks(g['ids'], set()))

nav.append('<h6>Your library</h6><a href="/hostcourse/guides/"><span class="n">←</span><span class="t">All guides</span></a><a href="/hostcourse/"><span class="n">★</span><span class="t">6-Figure Host Course</span></a>')
out = []
course = [l for l in lessons if l['done']]
for l in lessons:
    body = l['html']
    if 'collect' in l:
        lib, last, seen = [], None, set()
        for navname, block in prompts:
            if block in seen: continue
            seen.add(block)
            if navname != last:
                lib.append('<h3>%s</h3>' % navname); last = navname
            lib.append(re.sub(r'data-edit="([^"]+)" id="ed-', r'data-edit="\1" id="lib-', block))
        body[l['collect']] = '\n'.join(lib)
    h = ['<article class="lesson" id="%s">' % l['id']]
    if l['id'] == 'home':
        maprows = ''.join('<a href="#%s"><span class="n">%s</span><span><b>%s</b><small>%s</small></span><span class="st"></span></a>' % (c['id'], c['num'], c['nav'], c['sub']) for c in course)
        h.append('\n'.join(body).replace('%%MAP%%', maprows))
    else:
        mins = max(5, int(round((words(l) / 190 + l['tasks'] * 2) / 5.0)) * 5)
        meta = ((('%d sections · ' % len(l['parts'])) if l['parts'] else '') + 'about %d min' % mins) if l['done'] else ''
        num = l['num'].strip()
        if num.isdigit(): blab, bnum, bcls = 'Lesson', num, ''
        else: blab, bnum, bcls = {'calculator': 'Tool', 'finance': 'Tool', 'story': 'Intro', 'kit': 'Bonus'}.get(l['id'], 'Bonus' if l['id'] in ('roadmap', 'setup', 'manual') or l['id'].startswith('bonus-') else 'Extras'), num, ' sym'
        badge = '<span class="mbadge%s" aria-hidden="true"><small>%s</small><b>%s</b></span>' % (bcls, blab, bnum)
        if l['id'] in ('roadmap', 'setup', 'manual'):
            badge = '<span class="mbadge sym" aria-hidden="true"><small>Tool</small><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></span>'
        h.append('<header class="lhead"><div class="lh-main"><span class="eyebrow">%s</span><h1>%s%s</h1>%s</div><div class="lh-side">%s%s</div>' % (
            l['eyebrow'], l['title'], ' <span class="s">%s</span>' % l['script'] if l['script'] else '', '<p class="sub">%s</p>' % l['sub'] if l['sub'] else '',
            '<span class="meta">%s</span>' % meta if meta else '', badge + '<button type="button" class="backlink" hidden><span aria-hidden="true">←</span> <span class="bl-t">Back</span></button>'))
        if len(l['parts']) > 1:
            h.append('<div class="pills">' + ''.join('<button type="button" data-jump="%s"><b>%d</b>%s</button>' % (pid, n + 1, t) for n, (pid, t) in enumerate(l['parts'])) + '</div>')
        h.append('</header>')
        if l.get('vlangs'):
            h.append('<div class="vmode" role="group" aria-label="Lesson format" data-langs="%s"><span class="vlab">This lesson</span><button type="button" data-mode="video">Video + text</button><button type="button" data-mode="text">Text only</button></div>' % ' '.join(sorted(l['vlangs'])))
        _body = '\n'.join(body)
        if l['done']:
            _body = re.sub(r'<div class="checklist"><div class="label">Your tasks</div>\s*(?:<label class="task">(?:(?!</label>).)*</label>\s*)+</div>\s*(</section>\s*)?$', lambda m: m.group(1) or '', _body, flags=re.S)
        h.append(_body)
        if l['id'] == 'roadmap':
            pass
        elif l['done'] and not l.get('tasklist') and l['id'] not in ('start','story'):
            h.append('<div class="donebox notasks"><button type="button" class="donebtn">Complete this page →</button></div>')
        elif l['done']:
            h.append(('<div class="donebox" data-group="intro">' if l['id'] in ('start', 'story') else '<div class="donebox">') + '<div class="db-head"><span class="label">Your tasks for this page</span><span class="steps"></span></div><div class="db-bar"><i></i></div><div class="checklist db-list">%s</div><button type="button" class="donebtn">Complete this page →</button></div>' % ''.join('<label class="task"><input type="checkbox" data-mtask="%s"><span>%s</span></label>' % kt for kt in l.get('tasklist', [])))
        k = order.index(l['id'])
        prev = by[order[k - 1]] if k > 0 else None
        nxt = by[order[k + 1]] if k + 1 < len(order) else None
        h.append('<div class="pn">%s%s</div>' % (
            '<a href="#%s"><small>← Back</small>%s</a>' % (prev['id'], prev['nav'] if prev['id'] != 'home' else 'Overview') if prev else '',
            '<a class="next" href="#%s"><small>Next →</small>%s</a>' % (nxt['id'], nxt['nav']) if nxt else ''))
    h.append('<div class="foot"><span>© <span class="yr">2026</span> 6 Figure Host. All rights reserved. For individual use only.</span><span class="foot-r"><a class="ig" href="https://www.instagram.com/6figurehost/" target="_blank" rel="noopener" aria-label="Instagram @6figurehost" title="Instagram @6figurehost"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg></a><a class="ig" href="https://www.facebook.com/groups/6figurehost" target="_blank" rel="noopener" aria-label="Facebook community" title="Facebook community"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.3H8v3h2.5V21h3z"/></svg></a><span class="foot-btn"><button type="button" class="revbtn" data-review="feedback">Feedback &amp; review</button><a class="pplink" href="/privacy" target="_blank" rel="noopener">Privacy policy</a></span></span></div>')
    h.append('</article>')
    _art = '\n'.join(h)
    if l['id'] == 'start': _art = re.sub(r'<header class="lhead">.*?</header>', '', _art, count=1, flags=re.S)
    if l['id'] == 'start':
        _m = re.search(r'<div class="vmode".*?</div>\n?', _art, flags=re.S)
        if _m:
            _art = _art.replace(_m.group(0), '', 1).replace('<div data-vm></div>', _m.group(0), 1)
        _cp = re.search(r'<p class="added" style="margin-top:18px;max-width:none"><strong>Copyright notice\.</strong>.*?</p>\n?', _art, flags=re.S)
        if _cp:
            _art = _art.replace(_cp.group(0), '', 1); _k = _art.index('<div class="pn">'); _art = _art[:_k] + _cp.group(0) + _art[_k:]
    out.append(_art)

page = TPL.replace('%%NAV%%', '\n'.join(nav)).replace('%%LESSONS%%', '\n'.join(out))
_IC = {
 'broom':'<path d="M14 4l6 6M12.5 5.5l6 6-5 5H8l-3-3v-5.5z"/><path d="M8 16.5L4 20.5"/>',
 'refresh':'<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20v-4h-4"/>',
 'key':'<circle cx="8" cy="15" r="4"/><path d="M10.8 12.2L19 4M16 7l2.5 2.5M14 9l2 2"/>',
 'box':'<path d="M3 7.5L12 3l9 4.5v9L12 21l-9-4.5z"/><path d="M3 7.5l9 4.5 9-4.5M12 12v9"/>',
 'alert':'<path d="M12 3.5L2.5 20h19z"/><path d="M12 10v4.5M12 17.2v.3"/>',
 'phone':'<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
 'calendar':'<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
 'washer':'<rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="12" cy="13" r="4.5"/><path d="M7.5 6.5h.01M10.5 6.5h3"/>',
 'coffee':'<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.5a2.5 2.5 0 0 1 0 5H16M8 3.5v2M12 3.5v2"/>',
 'camera':'<path d="M4 8h3.5L9 5.5h6L16.5 8H20v11H4z"/><circle cx="12" cy="13.2" r="3.4"/>',
 'bed':'<path d="M3 18V6M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3"/><circle cx="7" cy="10.5" r="1.6"/>',
 'pan':'<circle cx="9.5" cy="12" r="6"/><path d="M15.5 12H22"/>',
 'spoon':'<ellipse cx="12" cy="7" rx="3.5" ry="4.5"/><path d="M12 11.5V21"/>',
 'recycle':'<path d="M7 19H4.5l3.5-6M9.5 6.5L12 3l3.5 6M17 19h2.5L16 13"/><path d="M8 13l-2.5-1M15.5 9l.5-3M16 13l2.5 1"/>',
 'bulb':'<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
 'wrench':'<path d="M14.5 6.5a4 4 0 0 0 5 5L14 17l-4.5 4.5-3-3L11 14l5.5-5.5a4 4 0 0 0-2-2z"/>',
 'sparkle':'<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.5 16l.7 2 .8.7-.8.6-.7 2-.6-2-.9-.6.9-.7z"/>',
}
page = re.sub(r'\[\[ic:(\w+)\]\]\s?', lambda m: '<svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % _IC[m.group(1)], page)

page = re.sub(r'(?i)chat ?gpt prompt', 'AI prompt', page)
_scp = os.path.join(GDIR, 'scorecard.html')
if os.path.exists(_scp): page = page.replace('%%SCORECARD%%', open(_scp, encoding='utf-8').read())
page = page.replace('%%I18N%%', '{"pt":{"u":{},"a":{},"ta":{}}}')
open(os.path.join(GDIR, 'index.html'), 'w', encoding='utf-8').write(page)
print('lessons', len(lessons), 'tasks', sum(l['tasks'] for l in lessons), 'prompts', len(prompts), 'bytes', len(page.encode()))
for w in warnings: print('WARN', w)
for d in dropped: print('dropped second title:', d)
