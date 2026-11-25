import sys,glob,os,docx,importlib,subprocess
from units import paras
L=sys.argv[1]; CFG=importlib.import_module('cfg_'+L)
os.makedirs('out_%s/clean'%L,exist_ok=True); os.makedirs('final_%s'%L,exist_ok=True)
for f in glob.glob('out_%s/*.docx'%L):
    d=docx.Document(f); n=0
    for p in paras(d):
        if any(m in p.text for m in CFG.STOP):
            for r in p.runs: r.text=''
            n+=1
    o='out_%s/clean/%s'%(L,os.path.basename(f)); d.save(o); print(os.path.basename(f),'cleared',n)
subprocess.run('soffice --headless --convert-to pdf --outdir final_%s out_%s/clean/*.docx'%(L,L),shell=True,capture_output=True)
print(sorted(os.listdir('final_%s'%L)))
