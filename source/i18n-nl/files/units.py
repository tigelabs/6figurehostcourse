import openpyxl,docx,json,re,glob
def fmt(r): return (r.bold,r.italic,r.underline,r.font.size,r.font.name,str(r.font.color.rgb) if r.font.color and r.font.color.type else None,r.style.name if r.style else None)
def merge_runs(p):
    runs=p.runs;i=0
    while i<len(runs)-1:
        a,b=runs[i],runs[i+1]
        if fmt(a)==fmt(b) and not a._r.xpath('.//w:br|.//w:tab|.//w:drawing') and not b._r.xpath('.//w:drawing'):
            a.text=a.text+b.text; b._r.getparent().remove(b._r); runs=p.runs
        else: i+=1
def paras(d):
    ps=list(d.paragraphs)
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                ps+=c.paragraphs
                for t2 in c.tables:
                    for r2 in t2.rows:
                        for c2 in r2.cells: ps+=c2.paragraphs
    for s in d.sections:
        ps+=s.header.paragraphs+s.footer.paragraphs
    return ps
def need(t): return t is not None and isinstance(t,str) and re.search('[A-Za-z]{2}',t) and not t.startswith('=')
if __name__=='__main__':
    U=[]
    for f in sorted(glob.glob('src/*.docx')):
        d=docx.Document(f)
        for p in paras(d):
            merge_runs(p)
            for r in p.runs:
                if need(r.text): U.append(r.text)
    for f in ['checklists','inventory','finance']:
        wb=openpyxl.load_workbook('src/%s.xlsx'%f)
        for ws in wb:
            U.append(ws.title)
            for row in ws.iter_rows():
                for c in row:
                    if need(c.value): U.append(c.value)
            # data validations
            for dv in ws.data_validations.dataValidation:
                if dv.formula1 and '"' in dv.formula1: U.append('DV:'+dv.formula1)
    seen=[];[seen.append(u) for u in U if u not in seen]
    print(len(seen),sum(len(x) for x in seen))
    with open('u_en.txt','w') as fo:
        for i,u in enumerate(seen): fo.write('@@%d\n%s\n'%(i,u))
