import re,sys,glob
from check import parse
bad=0
for f in sys.argv[1:]:
    n=re.search(r'(\d\d)',f).group(1); src=parse('c%s.txt'%n); dst=parse(f)
    for k,v in dst.items():
        if k not in src: print(f,'unknown',k);bad+=1;continue
        if sorted(re.findall(r'\{\d+\}',src[k]))!=sorted(re.findall(r'\{\d+\}',v)): print(f,k,'tokens');bad+=1
    miss=[k for k in src if k not in dst]
    print(f,len(dst),'/',len(src),'miss:',' '.join(miss)[:200])
print('BAD',bad)
