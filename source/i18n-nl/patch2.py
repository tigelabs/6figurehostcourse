P='/home/claude/deploy/public/hostcourse/index.html'
s=open(P).read()
R=[
("$('.bl-t',b).textContent='Go back';b.setAttribute('aria-label','Back to the previous page'+(n?': '+n:''));","$('.bl-t',b).textContent=_('Go back');b.setAttribute('aria-label',_('Back to the previous page'+(n?': '+n:'')));"),
("'aria-label':'Month '+p.m.toFixed(1)+': profit '+money(p.p)+', initial capital left '+money(p.c)}","'aria-label':_('Month '+p.m.toFixed(1)+': profit '+money(p.p)+', initial capital left '+money(p.c))}"),
("[['Month '+p.m.toFixed(1),''],['Profit',money(p.p)],['Initial capital',money(p.c)]]","[[_('Month '+p.m.toFixed(1)),''],[_('Profit'),money(p.p)],[_('Initial capital'),money(p.c)]]"),
("x.title=isD?'Put it back':'I don’t need this';","x.title=_(isD?'Put it back':'I don’t need this');"),
("d.setAttribute('aria-label','Show in menu');","d.setAttribute('aria-label',_('Show in menu'));"),
("var v=(ta&&ta.value.trim())?ta.value:DEF;","var v=(ta&&ta.value.trim())?ta.value:(document.documentElement.lang==='nl'?DEF_NL:DEF);"),
('(function(){var DEF="Drinking water only','(function(){var DEF_NL="Alleen drinkwater\\nRecycling\\nRestafval\\nKamer 1\\nKamer 2\\nKamer 3\\nReservehanddoeken\\nVoorraad wc-papier\\nSchoonmaakmiddelen\\nGevonden voorwerpen\\nHanddoeken voor gasten: niet voor het strand\\nWASSEN: snelprogramma 30\\u00b0";var DEF="Drinking water only'),
# applyLang extras: refresh image aria + backlink text + labels preview
("var z=document.getElementById('lbzoom');if(z)z.textContent=_('Zoom in');\n}","var z=document.getElementById('lbzoom');if(z)z.textContent=_('Zoom in');\n  $$('figure img, .brochure img').forEach(function(i){i.setAttribute('aria-label',_((i.alt||'Image')+'. Open larger'));});\n  $$('.backlink .bl-t').forEach(function(e){e.textContent=_('Go back');});\n  try{document.dispatchEvent(new Event('sixfig-lang'));}catch(e){}\n}"),
]
for o,n in R:
    assert s.count(o)==1,(s.count(o),o[:60])
    s=s.replace(o,n)
# labels preview refresh on lang change: find prev() definition and add listener
o="function prev(){var p=document.querySelector('.lbl-preview');"
assert s.count(o)==1
s=s.replace(o,"document.addEventListener('sixfig-lang',function(){try{prev();}catch(e){}});"+o)
# RT additions
add=("'Complete this page →':'Rond deze pagina af →','Page complete ✓':'Pagina afgerond ✓','Is it furnished?':'Is de woning gemeubileerd?','Will you look for a furnished place?':'Ga je op zoek naar een gemeubileerde woning?','Your launch roadmap':'Jouw stappenplan','Target launch date: ':'Beoogde lanceerdatum: ','Add a start date to see your launch date.':'Vul een startdatum in om je lanceerdatum te zien.','Answer the first two questions to see your timeline.':'Beantwoord de eerste twee vragen om je planning te zien.','Image':'Afbeelding','Go back':'Ga terug','Back to the previous page':'Terug naar de vorige pagina','Put it back':'Terugzetten','I don’t need this':'Dit heb ik niet nodig',")
s=s.replace("var RT={nl:{exact:{","var RT={nl:{exact:{"+add,1)
pat=("[/^(\\d+) of (\\d+) done$/,'$1 van $2 klaar'],[/^Your roadmap: (\\d+) days$/,'Jouw stappenplan: $1 dagen'],[/^Your (\\d+)-day launch roadmap$/,'Jouw stappenplan van $1 dagen'],[/^Weeks (\\d+)–(\\d+)(.*)$/,'Weken $1–$2$3'],[/^Back to the previous page: (.+)$/,'Terug naar de vorige pagina: $1'],")
i=s.find("var RT={nl:"); j=s.find("pat:[",i)+5
s=s[:j]+pat+s[j:]
open(P,'w').write(s)
print('ok')
s=open(P).read()
o="lab.textContent=o?'Hide':'Show';}\n    set(false);"
assert s.count(o)==1
s=s.replace(o,"var nl=document.documentElement.lang==='nl';lab.textContent=o?(nl?'Verbergen':'Hide'):(nl?'Tonen':'Show');}\n    set(false);document.addEventListener('sixfig-lang',function(){set(c.classList.contains('open'));});")
o="s.setAttribute('aria-label',n+' out of 5');"
assert s.count(o)==1
s=s.replace(o,"s.setAttribute('aria-label',(document.documentElement.lang==='nl'?n+' van 5':n+' out of 5'));")
open(P,'w').write(s);print('ok2')
