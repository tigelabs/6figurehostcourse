import re,zipfile,shutil,os,glob,io,sys,importlib
LANG=sys.argv[1]
CFG=importlib.import_module('cfg_'+LANG)
from lxml import etree
import docx
rich_lookup=importlib.import_module('rich_'+LANG).rich_lookup
from units import merge_runs,paras,need
def parse(f):
    d={};cur=None;buf=[]
    for line in open(f).read().split('\n'):
        m=re.match(r'^@@(\d+)$',line)
        if m:
            if cur is not None: d[cur]='\n'.join(buf)
            cur=int(m.group(1));buf=[]
        else: buf.append(line)
    if cur is not None: d[cur]='\n'.join(buf)
    return d
en=parse('u_en.txt'); nl={}
for f in ['u_%s_1.txt'%LANG,'u_%s_2.txt'%LANG]: nl.update(parse(f))
T={}
for k,v in en.items():
    v=v[:-1] if v.endswith('\n') and False else v
for k in en:
    e=en[k]
    if k in nl:
        n=nl[k].strip('\n')
        lead=re.match(r'^\s*',e).group(0); trail=re.search(r'\s*$',e).group(0)
        T[e]=lead+n.strip()+trail
# en strings in u_en.txt were written with trailing \n separators: original unit = text as written; parse joins lines, original may end with "\n" (blank line) -> handled by trail
def tr(s):
    if s in T: return T[s]
    if s.strip() and s in [x.rstrip('\n') for x in T]: pass
    return None
miss=set()
T.update(CFG.T_EXTRA)
OUT='out_'+LANG;os.makedirs(OUT,exist_ok=True)
# DOCX
names=CFG.names
for f in sorted(glob.glob('src/*.docx')):
    d=docx.Document(f)
    for p in paras(d):
        merge_runs(p)
        for r in p.runs:
            if need(r.text):
                t=tr(r.text)
                if t is None: miss.add(r.text)
                else: r.text=t
    b=os.path.basename(f)[:-5]
    d.save(OUT+'/%s.docx'%names[b])
# XLSX at XML level
SHEETS=CFG.SHEETS
LIT=CFG.LIT
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
def fix_formula(s):
    for a,b in SHEETS.items():
        s=s.replace("'%s'!"%a,"'%s'!"%b)
        if ' ' not in a: s=re.sub(r"(?<![\w'])%s!"%re.escape(a),"'%s'!"%b if ' ' in b else b+'!',s)
    for a,b in LIT.items(): s=s.replace('"%s"'%a,'"%s"'%b)
    return s
xnames=CFG.xnames
for f,o in xnames.items():
    zin=zipfile.ZipFile('src/%s.xlsx'%f); zout=zipfile.ZipFile(OUT+'/%s.xlsx'%o,'w',zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data=zin.read(it.filename)
        if it.filename=='xl/sharedStrings.xml':
            x=etree.fromstring(data)
            for si in x.findall('{%s}si'%NS):
                ts=si.findall('.//{%s}t'%NS); full=''.join(t.text or '' for t in ts)
                rr=rich_lookup([t.text or '' for t in ts]) if len(ts)>1 else None
                if rr:
                    for t,v in zip(ts,rr):
                        t.text=v; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
                    continue
                if need(full):
                    t=tr(full)
                    if t is None: miss.add(full)
                    else:
                        ts[0].text=t
                        ts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
                        for t2 in ts[1:]: t2.text=''
            data=etree.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif it.filename=='xl/workbook.xml':
            x=etree.fromstring(data)
            for s in x.iter('{%s}sheet'%NS):
                if s.get('name') in SHEETS: s.set('name',SHEETS[s.get('name')])
            for dn in x.iter('{%s}definedName'%NS):
                dn.text=fix_formula(dn.text or '')
            data=etree.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif it.filename.startswith('xl/worksheets/sheet'):
            x=etree.fromstring(data)
            for fe in x.iter('{%s}f'%NS):
                if fe.text: fe.text=fix_formula(fe.text)
            for fe in x.iter('{%s}formula'%NS):
                if fe.text: fe.text=fix_formula(fe.text)
            for isel in x.iter('{%s}is'%NS):
                ts=isel.findall('.//{%s}t'%NS); full=''.join(t.text or '' for t in ts)
                if need(full):
                    t=tr(full)
                    if t is None: miss.add(full)
                    else:
                        ts[0].text=t
                        for t2 in ts[1:]: t2.text=''
            data=etree.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif it.filename.startswith('xl/charts/'):
            s=data.decode('utf8')
            for a,b in SHEETS.items(): s=s.replace("'%s'!"%a,"'%s'!"%b).replace(">%s!"%a,">'%s'!"%b if ' ' in b else ">%s!"%b)
            for m in set(re.findall(r'<a:t>([^<]+)</a:t>',s)):
                t=tr(m)
                if t: s=s.replace('<a:t>%s</a:t>'%m,'<a:t>%s</a:t>'%t)
                elif need(m): miss.add('CHART:'+m)
            data=s.encode('utf8')
        zout.writestr(it,data)
    zout.close()
print('missing',len(miss));[print(repr(m)[:120]) for m in sorted(miss)]
