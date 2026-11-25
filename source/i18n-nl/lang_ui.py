P='/home/claude/deploy/public/hostcourse/index.html'
s=open(P).read()
uk='<svg class="flag" viewBox="0 0 60 30" aria-hidden="true"><clipPath id="fuk"><path d="M0 0v30h60V0z"/></clipPath><clipPath id="fuk2"><path d="M30 15h30v15zv15H0zH0V0zV0h30z"/></clipPath><g clip-path="url(#fuk)"><path d="M0 0v30h60V0z" fill="#012169"/><path d="M0 0l60 30m0-30L0 30" stroke="#fff" stroke-width="6"/><path d="M0 0l60 30m0-30L0 30" clip-path="url(#fuk2)" stroke="#C8102E" stroke-width="4"/><path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/><path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/></g></svg>'
nlf='<svg class="flag" viewBox="0 0 9 6" aria-hidden="true"><path fill="#21468B" d="M0 0h9v6H0z"/><path fill="#fff" d="M0 0h9v4H0z"/><path fill="#AE1C28" d="M0 0h9v2H0z"/></svg>'
html='<div class="lang" role="group" aria-label="Language"><button type="button" data-lang="en" aria-label="Switch to English" title="English">'+uk+'<span>EN</span></button><button type="button" data-lang="nl" aria-label="Switch to Dutch" title="Nederlands">'+nlf+'<span>NL</span></button></div>'
anchor='<div aria-label="Guide progress" class="prog">'
assert s.count(anchor)==1
i=s.find(anchor); j=s.find('</div></div>',i)+12  # prog contains .bar div
print(repr(s[i:j]))
s=s[:j]+' '+html+s[j:]
css='''/* language switch */
.lang{display:inline-flex;gap:3px;padding:3px;border-radius:999px;background:rgba(244,242,239,.12);border:1px solid rgba(244,242,239,.22);flex:none}
.lang button{display:inline-flex;align-items:center;gap:6px;font:700 12px/1 var(--body);letter-spacing:.04em;color:#f4f2ef;background:transparent;border:0;border-radius:999px;padding:6px 10px 6px 7px;cursor:pointer;transition:background .15s,color .15s}
.lang button:hover{background:rgba(244,242,239,.12)}
.lang button.on{background:var(--paper);color:var(--ink)}
.lang button:focus-visible{outline:2px solid #fff;outline-offset:2px}
.lang .flag{width:20px;height:14px;border-radius:3px;display:block;box-shadow:0 0 0 1px rgba(0,0,0,.12)}
@media (max-width:860px){.lang button{padding:5px 6px}.lang button span{display:none}.lang .flag{width:22px;height:15px}.prog .bar{width:70px}}
'''
s=s.replace('/* course / bonus switch */',css+'/* course / bonus switch */',1)
open(P,'w').write(s)
