import re,json,lxml.html,html
s=open('/home/claude/deploy/public/hostcourse/index.html').read()
doc=lxml.html.fromstring(s)
u={};order=[]
for e in doc.xpath('//*[@data-t]'):
    t=e.get('data-t')
    if t in u: continue
    inner=html.escape(e.text or '',quote=False)+''.join(lxml.html.tostring(c,encoding='unicode') for c in e)
    u[t]=inner;order.append(t)
# NOTE: lxml serialisation may differ from browser innerHTML; we store tokenized text and rebuild from tag list
items=[]
for t in order:
    h=u[t]
    tags=re.findall(r'<[^>]+>',h)
    i=[0]
    def rep(m):
        i[0]+=1;return '{%d}'%(i[0])
    txt=re.sub(r'<[^>]+>',rep,h)
    plain=re.sub(r'\{\d+\}','',txt)
    if not re.search(r'[A-Za-z]{2,}',plain): continue
    items.append({'id':t,'en':txt,'tags':tags})
tas=[]
for e in doc.xpath('//textarea[@data-edit]'):
    tas.append({'id':e.get('data-edit'),'en':e.text or ''})
attrs=[]
seen=set()
for a in ['placeholder','aria-label','alt','data-ph']:
    for e in doc.xpath('//*[@%s]'%a):
        v=e.get(a)
        if v and re.search('[A-Za-z]{2,}',v) and v not in seen: seen.add(v);attrs.append(v)
json.dump({'items':items,'ta':tas,'attrs':attrs},open('src.json','w'),ensure_ascii=False)
print(len(items),sum(len(x['en']) for x in items),len(tas),sum(len(x['en']) for x in tas),len(attrs))
# chunk
ch=[];cur=[];n=0
for x in items:
    cur.append(x);n+=len(x['en'])
    if n>9000: ch.append(cur);cur=[];n=0
if cur: ch.append(cur)
for k,c in enumerate(ch):
    with open('c%02d.txt'%k,'w') as f:
        for x in c: f.write('@@%s\n%s\n'%(x['id'],x['en']))
print(len(ch))
