import re,json,glob,sys
sys.path.insert(0,'.')
from check import parse
P='/home/claude/deploy/public/hostcourse/index.html'
s=open(P).read()
src=json.load(open('src.json'))
items={x['id']:x for x in src['items']}
u={}
for f in sorted(glob.glob('n[0-9][0-9].txt')):
    for k,v in parse(f).items():
        tags=items[k]['tags']
        def rep(m): return tags[int(m.group(1))-1]
        u[k]=re.sub(r'\{(\d+)\}',rep,v)
# extra ids for new UI
EXTRA={'2517':('IMPORTANT','BELANGRIJK'),
 '2518':('Everything saves automatically on this device and browser. Want to continue your work on a different device? Save your data here, then restore it on the new device.','Alles wordt automatisch opgeslagen op dit apparaat en in deze browser. Wil je op een ander apparaat verder? Sla je gegevens hier op en herstel ze daarna op het nieuwe apparaat.'),
 '2519':('Don’t clear your browser history or site data, or everything you filled in will be deleted.','Wis je browsergeschiedenis of sitegegevens niet, anders wordt alles wat je hebt ingevuld verwijderd.'),
 '2520':('Save your data','Gegevens opslaan'),'2521':('Restore your data','Gegevens herstellen'),
 '2522':('Course','Cursus'),'2523':('Bonus &amp; extras','Bonus &amp; extra’s')}
for k,(en,nl) in EXTRA.items(): u[k]=nl
a={}
an=parse('attrs_nl.txt'); 
for i,en in enumerate(src['attrs']):
    if 'a%d'%i in an: a[en]=an['a%d'%i]
a['Show in menu']='Toon in het menu'; a['Language']='Taal'; a['Switch to English']='Overschakelen naar Engels'; a['Switch to Dutch']='Overschakelen naar Nederlands'
ta=parse('ta_nl.txt'); ta['dc-1']=ta['declutter-1']; ta['dc-2']=ta['declutter-2']
tids={x['id'] for x in src['ta']}; print('ta missing',tids-set(ta))
nl={'u':u,'a':a,'ta':ta}
js=json.dumps(nl,ensure_ascii=False).replace('</','<\\/')
assert '"nl":' not in s[:s.find('var I18N=')+200]
s=s.replace('var I18N={','var I18N={"nl": '+js+', ',1)
rt=open('rt_nl.js').read().strip()
s=s.replace('var RT={pt:','var RT={'+rt+',pt:',1)
# applyLang
old="LANG='en'; /* English only for now; the PT layer stays in the build for later */"
assert old in s
s=s.replace(old,"LANG=(S.fields.lang==='nl')?'nl':'en';",1)
s=s.replace("document.documentElement.lang=LANG==='pt'?'pt-BR':'en';","document.documentElement.lang=LANG;",1)
s=s.replace("toLocaleDateString('en-GB'","toLocaleDateString(LANG==='nl'?'nl-NL':'en-GB'")
s=s.replace("n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,',')","n.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,LANG==='nl'?'.':',')",1)
# savebox data-t
rep=[('<h3>IMPORTANT</h3>','<h3 data-t="2517">IMPORTANT</h3>'),
 ('<p>Everything saves automatically','<p data-t="2518">Everything saves automatically'),
 ('<p><strong>Don’t clear','<p><strong data-t="2519">Don’t clear'),
 ('id="sb-save" type="button">','data-t="2520" id="sb-save" type="button">'),
 ('id="sb-restore" type="button">','data-t="2521" id="sb-restore" type="button">'),
 ("'<button type=\"button\" data-sw=\"course\">Course</button><button type=\"button\" data-sw=\"extras\">Bonus &amp; extras</button>'","'<button type=\"button\" data-sw=\"course\" data-t=\"2522\">Course</button><button type=\"button\" data-sw=\"extras\" data-t=\"2523\">Bonus &amp; extras</button>'"),
 ("var top=mk('navsw-top');","EN_HTML['2522']='Course';EN_HTML['2523']='Bonus &amp; extras';var top=mk('navsw-top');"),
 ("return !hasData||window.confirm('Restoring","return !hasData||window.confirm(_('Restoring"),
 ("with the saved file. Continue?');","with the saved file. Continue?'));"),
]
for o,n in rep:
    assert s.count(o)>=1,o
    s=s.replace(o,n,1)
open(P,'w').write(s)
print('ok',len(u),len(a),len(ta))
