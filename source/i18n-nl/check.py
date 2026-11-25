import re,sys,glob
def parse(f):
    d={};cur=None;buf=[]
    for line in open(f).read().split('\n'):
        m=re.match(r'^@@([\w.-]+)$',line)
        if m:
            if cur is not None: d[cur]='\n'.join(buf)
            cur=m.group(1);buf=[]
        else: buf.append(line)
    if cur is not None: d[cur]='\n'.join(buf)
    return {k:v.rstrip('\n') if not v.endswith('\n\n') else v[:-1] for k,v in d.items()}
bad=0
for n in sys.argv[1:]:
    c=n.replace('/n','/c') if '/' in n else 'c'+n[1:]
    src=parse(c);dst=parse(n)
    for k,v in dst.items():
        if k not in src: print(n,'unknown id',k);bad+=1;continue
        a=sorted(re.findall(r'\{\d+\}',src[k]));b=sorted(re.findall(r'\{\d+\}',v))
        if a!=b: print(n,k,'tokens',a,b);bad+=1
    miss=[k for k in src if k not in dst]
    print(n,len(dst),'/',len(src),'missing:',' '.join(miss)[:300])
print('BAD',bad)
