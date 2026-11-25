import re,json
from html.parser import HTMLParser
s=open('/home/claude/deploy/public/hostcourse/index.html').read()
body=s[s.find('<body'):s.find('<script>',s.find('<div class="toast"'))]
# data-t innerHTML via regex-ish parser: use lxml
import lxml.html
doc=lxml.html.fromstring(s)
u={}
for e in doc.xpath('//*[@data-t]'):
    t=e.get('data-t')
    if t in u: continue
    inner=(e.text or '')+''.join(lxml.html.tostring(c,encoding='unicode') for c in e)
    u[t]=inner
attrs={}
for a in ['placeholder','aria-label','alt','data-ph']:
    for e in doc.xpath('//*[@%s]'%a):
        v=e.get(a)
        if v and re.search('[A-Za-z]',v): attrs[v]=None
ta={}
for e in doc.xpath('//textarea[@data-edit]'):
    ta[e.get('data-edit')]=e.get('data-orig')
json.dump({'u':u,'a':list(attrs),'ta':ta},open('/home/claude/nl/en.json','w'),ensure_ascii=False,indent=0)
tot=sum(len(v) for v in u.values()); txt=sum(len(re.sub('<[^>]+>','',v)) for v in u.values())
print(len(u),tot,txt,len(attrs),sum(len(k) for k in attrs),len(ta),sum(len(v or '') for v in ta.values()))
