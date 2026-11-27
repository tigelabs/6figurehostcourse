import re,json,glob,sys
sys.path.insert(0,'/home/claude/nl')
from check import parse
P='/home/claude/deploy/public/hostcourse/index.html'
s=open(P).read()
src=json.load(open('/home/claude/nl/src.json'))
items={x['id']:x for x in src['items']}
EXTRA={
 'es':{'2517':'IMPORTANTE','2518':'Todo se guarda automáticamente en este dispositivo y navegador. ¿Quieres seguir en otro dispositivo? Guarda aquí tus datos y luego restáuralos en el nuevo dispositivo.','2519':'No borres el historial del navegador ni los datos del sitio, o se eliminará todo lo que hayas rellenado.','2520':'Guardar tus datos','2521':'Restaurar tus datos','2522':'Curso','2523':'Bonus y extras','2524':'Continúa donde lo dejaste'},
 'pt':{'2517':'IMPORTANTE','2518':'Tudo é salvo automaticamente neste dispositivo e navegador. Quer continuar em outro dispositivo? Salve seus dados aqui e depois restaure no novo dispositivo.','2519':'Não apague o histórico do navegador nem os dados do site, ou tudo o que você preencheu será apagado.','2520':'Salvar seus dados','2521':'Restaurar seus dados','2522':'Curso','2523':'Bônus e extras','2524':'Continue de onde parou'}}
SW={'Switch to English':{'nl':'Overschakelen naar Engels','es':'Cambiar a inglés','pt':'Mudar para inglês'},
    'Switch to Dutch':{'nl':'Overschakelen naar Nederlands','es':'Cambiar a neerlandés','pt':'Mudar para holandês'},
    'Switch to Spanish':{'nl':'Overschakelen naar Spaans','es':'Cambiar a español','pt':'Mudar para espanhol'},
    'Switch to Portuguese':{'nl':'Overschakelen naar Portugees','es':'Cambiar a portugués','pt':'Mudar para português'},
    'Choose language':{'nl':'Kies een taal','es':'Elige el idioma','pt':'Escolha o idioma'}}
k0=s.find('var I18N=')+len('var I18N=')
d,end=json.JSONDecoder().raw_decode(s[k0:])
for k,v in [x for f in sorted(glob.glob('/home/claude/nl/n[0-9][0-9].txt')) for x in parse(f).items()]:
    d['nl']['u'][k]=re.sub(r'\{(\d+)\}',lambda m:items[k]['tags'][int(m.group(1))-1],v)
for L in ('es','pt'):
    u={}
    for f in sorted(glob.glob('/home/claude/nl/%s[0-9][0-9].txt'%L)):
        for k,v in parse(f).items():
            tags=items[k]['tags']
            u[k]=re.sub(r'\{(\d+)\}',lambda m:tags[int(m.group(1))-1],v)
    u.update(EXTRA[L])
    an=parse('/home/claude/nl/attrs_%s.txt'%L); a={}
    for i,en in enumerate(src['attrs']):
        if 'a%d'%i in an: a[en]=an['a%d'%i]
    a['Show in menu']={'es':'Mostrar en el menú','pt':'Mostrar no menu'}[L]; a['Language']='Idioma'
    ta=parse('/home/claude/nl/ta_%s.txt'%L); ta['dc-1']=ta['declutter-1']; ta['dc-2']=ta['declutter-2']
    tids={x['id'] for x in src['ta']}; assert not (tids-set(ta)),tids-set(ta)
    d[L]={'u':u,'a':a,'ta':ta}
    print(L,len(u),len(a),len(ta))
for en,m in SW.items():
    for L in ('nl','es','pt'): d[L]['a'][en]=m[L]
d={k:d[k] for k in ('nl','es','pt')}
js=json.dumps(d,ensure_ascii=False).replace('</','<\\/')
s=s[:k0]+js+s[k0+end:]
# RT: replace old pt block, add es
i=s.find('var RT={'); j=s.find(',pt:{exact:',i); e=s.find("}};\nvar LANG='en'",i)
assert i>0 and j>i and e>j
rt_es=open('/home/claude/nl/rt_es.js').read().strip(); rt_pt=open('/home/claude/nl/rt_pt.js').read().strip()
s=s[:j]+',\n'+rt_es+',\n'+rt_pt+s[e+1:]
R=[
("LANG=(S.fields.lang==='nl')?'nl':'en';","LANG=(['nl','es','pt'].indexOf(S.fields.lang)>-1)?S.fields.lang:'en';"),
("toLocaleDateString(LANG==='nl'?'nl-NL':'en-GB',{day:'numeric',month:'short'})","toLocaleDateString(({nl:'nl-NL',es:'es-ES',pt:'pt-BR'})[LANG]||'en-GB',{day:'numeric',month:'short'})"),
("toLocaleDateString(LANG==='nl'?'nl-NL':'en-GB',{day:'numeric',month:'long',year:'numeric'})","toLocaleDateString(({nl:'nl-NL',es:'es-ES',pt:'pt-BR'})[LANG]||'en-GB',{day:'numeric',month:'long',year:'numeric'})"),
("g,LANG==='nl'?'.':',');}","g,LANG==='en'?',':'.');}"),
("(document.documentElement.lang==='nl'?n+' van 5':n+' out of 5')","(({nl:n+' van 5',es:n+' de 5',pt:n+' de 5'})[document.documentElement.lang]||n+' out of 5')"),
("var nl=document.documentElement.lang==='nl';lab.textContent=o?(nl?'Verbergen':'Hide'):(nl?'Tonen':'Show');","var hl=document.documentElement.lang,T={nl:['Verbergen','Tonen'],es:['Ocultar','Mostrar'],pt:['Ocultar','Mostrar']}[hl]||['Hide','Show'];lab.textContent=o?T[0]:T[1];"),
("(document.documentElement.lang==='nl'?DEF_NL:DEF)","(({nl:DEF_NL,es:DEF_ES,pt:DEF_PT})[document.documentElement.lang]||DEF)"),
('(function(){var DEF_NL=','(function(){var DEF_ES='+json.dumps(d['es']['a'][[x for x in src['attrs'] if x.startswith('Drinking water only')][0]],ensure_ascii=False)+',DEF_PT='+json.dumps(d['pt']['a'][[x for x in src['attrs'] if x.startswith('Drinking water only')][0]],ensure_ascii=False)+';var DEF_NL='),
("(LANG==='nl'&&HREF_NL[e])?HREF_NL[e]:e","(HREF[LANG]&&HREF[LANG][e])?HREF[LANG][e]:e"),
("if(LANG==='nl'&&DL_NL[k]){b.dataset.download='files/nl/'+DL_NL[k]+'.pdf';b.dataset.name=DL_NL[k]+'.pdf';}","if(DL[LANG]&&DL[LANG][k]){b.dataset.download='files/'+LANG+'/'+DL[LANG][k]+'.pdf';b.dataset.name=DL[LANG][k]+'.pdf';}"),
]
for o,n in R:
    assert s.count(o)==1,(s.count(o),o[:70])
    s=s.replace(o,n)
# HREF/DL maps: wrap existing NL maps
o="$$('a[href]').forEach(function(a){if(a.dataset.hen===undefined)"
assert s.count(o)==1
s=s.replace(o,"var HREF={nl:HREF_NL,es:HREF_ES,pt:HREF_PT},DL={nl:DL_NL,es:DL_ES,pt:DL_PT};\n  "+o)
o="var HREF_NL="
s=s.replace(o,"var HREF_ES=/*HREF_ES*/{},HREF_PT=/*HREF_PT*/{},DL_ES=/*DL_ES*/{},DL_PT=/*DL_PT*/{};\n  var HREF_NL=",1)
# language selector UI
FL={'en':'<svg class="flag" viewBox="0 0 60 30" aria-hidden="true"><clipPath id="fuk%s"><path d="M0 0v30h60V0z"/></clipPath><clipPath id="fuk2%s"><path d="M30 15h30v15zv15H0zH0V0zV0h30z"/></clipPath><g clip-path="url(#fuk%s)"><path d="M0 0v30h60V0z" fill="#012169"/><path d="M0 0l60 30m0-30L0 30" stroke="#fff" stroke-width="6"/><path d="M0 0l60 30m0-30L0 30" clip-path="url(#fuk2%s)" stroke="#C8102E" stroke-width="4"/><path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/><path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/></g></svg>',
 'nl':'<svg class="flag" viewBox="0 0 9 6" aria-hidden="true"><path fill="#21468B" d="M0 0h9v6H0z"/><path fill="#fff" d="M0 0h9v4H0z"/><path fill="#AE1C28" d="M0 0h9v2H0z"/></svg>',
 'es':'<svg class="flag" viewBox="0 0 750 500" aria-hidden="true"><path fill="#AA151B" d="M0 0h750v500H0z"/><path fill="#F1BF00" d="M0 125h750v250H0z"/></svg>',
 'pt':'<svg class="flag" viewBox="0 0 20 14" aria-hidden="true"><path fill="#009C3B" d="M0 0h20v14H0z"/><path fill="#FFDF00" d="M10 1.6 18.3 7 10 12.4 1.7 7z"/><circle cx="10" cy="7" r="3.1" fill="#002776"/></svg>'}
NAME={'en':('English','Switch to English','EN'),'nl':('Nederlands','Switch to Dutch','NL'),'es':('Español','Switch to Spanish','ES'),'pt':('Português (Brasil)','Switch to Portuguese','PT')}
i=s.find('<div class="lang" role="group"'); j=s.find('</div>',i)+6
items_html=''.join('<button type="button" role="menuitemradio" aria-checked="false" data-lang="%s" aria-label="%s" lang="%s">%s<span>%s</span></button>'%(k,NAME[k][1],k,FL[k].replace('%s','m') if k=='en' else FL[k],NAME[k][0]) for k in ('en','nl','es','pt'))
cur='<button type="button" class="lang-cur" id="langCur" aria-haspopup="menu" aria-expanded="false" aria-controls="langMenu" aria-label="Choose language"><span class="lc-flag">%s</span><span class="lc-code">EN</span><svg class="lc-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'%FL['en'].replace('%s','c')
s=s[:i]+'<div class="lang" id="langSel">'+cur+'<div class="lang-menu" id="langMenu" role="menu" aria-label="Language" hidden>'+items_html+'</div></div>'+s[j:]
# CSS: replace lines 778-784 block
css_old_start=s.find('.lang{display:inline-flex;gap:3px')
css_old_end=s.find('.lang .flag{width:22px;height:15px}}',css_old_start)+len('.lang .flag{width:22px;height:15px}}')
assert css_old_start>0 and css_old_end>css_old_start
css_new=('.lang{position:relative;flex:none}\n'
'.lang .lang-cur{display:inline-flex;align-items:center;gap:7px;font:700 12px/1 var(--body);letter-spacing:.04em;color:#f4f2ef;background:rgba(244,242,239,.12);border:1px solid rgba(244,242,239,.22);border-radius:999px;padding:6px 10px 6px 7px;cursor:pointer;transition:background .15s}\n'
'.lang .lang-cur:hover,.lang .lang-cur[aria-expanded="true"]{background:rgba(244,242,239,.22)}\n'
'.lang .lang-cur:focus-visible{outline:2px solid #fff;outline-offset:2px}\n'
'.lang .lc-flag{display:block}.lang .lc-chev{width:12px;height:12px;opacity:.8;transition:transform .15s}\n'
'.lang .lang-cur[aria-expanded="true"] .lc-chev{transform:rotate(180deg)}\n'
'.lang .flag{width:20px;height:14px;border-radius:3px;display:block;box-shadow:0 0 0 1px rgba(0,0,0,.14)}\n'
'.lang-menu{position:absolute;right:0;top:calc(100% + 8px);z-index:80;min-width:200px;background:var(--paper);border:1.5px solid var(--ink);border-radius:14px;padding:6px;box-shadow:0 12px 30px rgba(56,51,48,.22);display:flex;flex-direction:column;gap:2px}\n'
'.lang-menu[hidden]{display:none}\n'
'.lang-menu button{display:flex;align-items:center;gap:10px;width:100%;text-align:left;font:600 14px/1.2 var(--body);color:var(--ink);background:transparent;border:0;border-radius:9px;padding:9px 10px;cursor:pointer}\n'
'.lang-menu button:hover{background:var(--stone)}\n'
'.lang-menu button.on{background:var(--ink);color:var(--paper)}\n'
'.lang-menu button:focus-visible{outline:2px solid var(--ink);outline-offset:1px}\n'
'@media (max-width:860px){.lang .lang-cur{padding:5px 7px 5px 6px}.lang .lc-code{display:none}.lang .lc-flag .flag{width:22px;height:15px}}')
s=s[:css_old_start]+css_new+s[css_old_end:]
# old early rules (lines 52-55, 524) apply to .lang button: neutralise by scoping
for o,n in [('.lang{display:flex;flex:none;border:1.5px solid var(--ink);border-radius:99px;overflow:hidden;background:var(--paper)}\n',''),
            ('.lang button{border:0;background:transparent;padding:5px 11px;font-size:12px;font-weight:700;letter-spacing:.06em;cursor:pointer;color:var(--ink)}\n',''),
            ('.lang button.on{background:var(--ink);color:var(--paper)}\n',''),
            ('.lang button[disabled]{opacity:.4;cursor:not-allowed}\n',''),
            ('  .lang button{padding:5px 8px}\n',''),
            (',.lang button.on,',',.lang-menu button.on,')]:
    assert s.count(o)==1,o
    s=s.replace(o,n)
# JS: toggle menu + update current
o="$$('.lang button').forEach(function(b){b.classList.toggle('on',b.dataset.lang===LANG);b.setAttribute('aria-pressed',b.dataset.lang===LANG?'true':'false');});"
assert s.count(o)==1
s=s.replace(o,"$$('.lang-menu button').forEach(function(b){var on=b.dataset.lang===LANG;b.classList.toggle('on',on);b.setAttribute('aria-checked',on?'true':'false');if(on){var c=document.getElementById('langCur');if(c){$('.lc-flag',c).innerHTML=$('svg',b).outerHTML.replace(/fuk(2?)m/g,'fuk$1c');$('.lc-code',c).textContent=LANG.toUpperCase();}}});")
o="$$('.lang button[data-lang]').forEach(function(b){b.addEventListener('click',function(){if(b.disabled)return;S.fields.lang=b.dataset.lang;save();applyLang();});});"
assert s.count(o)==1
s=s.replace(o,"""(function(){var cur=document.getElementById('langCur'),menu=document.getElementById('langMenu');if(!cur||!menu)return;
  function open(o){menu.hidden=!o;cur.setAttribute('aria-expanded',o?'true':'false');if(o){var on=$('button.on',menu)||$('button',menu);on.focus();}}
  cur.addEventListener('click',function(e){e.stopPropagation();open(menu.hidden);});
  document.addEventListener('click',function(e){if(!menu.hidden&&!menu.contains(e.target))open(false);});
  menu.addEventListener('keydown',function(e){var bs=$$('button',menu),i=bs.indexOf(document.activeElement);
    if(e.key==='Escape'){open(false);cur.focus();}
    else if(e.key==='ArrowDown'){e.preventDefault();bs[(i+1)%bs.length].focus();}
    else if(e.key==='ArrowUp'){e.preventDefault();bs[(i-1+bs.length)%bs.length].focus();}});
  $$('button[data-lang]',menu).forEach(function(b){b.addEventListener('click',function(){S.fields.lang=b.dataset.lang;save();applyLang();open(false);cur.focus();});});
})();""")
open(P,'w').write(s)
print('ok')
# --- post patches ---
s=open(P).read()
o="s.setAttribute('role','radio');s.setAttribute('aria-label',"
assert s.count(o)==1
s=s.replace(o,"s.setAttribute('role','radio');s.dataset.star=n;s.setAttribute('aria-label',")
o="  $$('.backlink .bl-t').forEach(function(e){e.textContent=_('Go back');});"
assert s.count(o)==1
s=s.replace(o,o+"\n  $$('[data-star]').forEach(function(e){e.setAttribute('aria-label',_(e.dataset.star+' out of 5'));});")
open(P,'w').write(s); print('post ok')
s=open(P).read()
o="e.setAttribute(a,(d.a&&d.a[en]!==undefined)?d.a[en]:en);"
assert s.count(o)==1
s=s.replace(o,"e.setAttribute(a,(d.a&&d.a[en]!==undefined)?d.a[en]:_(en));")
open(P,'w').write(s); print('post2 ok')
# --- download / Drive maps ---
EN={'scripts':'https://drive.google.com/file/d/1JuqXu2Od9KytAE2pmuU4Hdbqc5_g9HYW/view','finance':'https://docs.google.com/spreadsheets/d/1BynDFkxEJJ6sgWesCNk16-H5yS4rdDygEPy4EGptASQ/copy','checklists':'https://docs.google.com/spreadsheets/d/1uZWX8SkPEV_DZBOCHiAvD4iJ50xiBYHXyhUj0hnd7yY/copy','inventory':'https://docs.google.com/spreadsheets/d/1GPkIvqdpBINiczgUt_UkwidvIv7Se1kJupSf_qWnDmg/copy','cinsp':'https://docs.google.com/document/d/1g4ejZSGND_97PLSH710it51QL2Xx9yw20-AUVtrDZnQ/copy','contracts':'https://drive.google.com/drive/folders/1-hJUOC8Rk6EqzsgKYozNrEOaE9rUkjQK?usp=sharing','insp':'https://drive.google.com/drive/folders/1bGVu910xF7sFr34BNmb9EYjeVS9j1KFp?usp=drive_link'}
IDS={'es':{'scripts':'https://drive.google.com/file/d/1_-tVDmB2mtgiC9xN1cJf0dwypsEVCd4D/view','finance':'https://docs.google.com/spreadsheets/d/1lqCj1JK9wHnTwsq8erx676FVRQW6pdSbvqlRANCDI8w/copy','checklists':'https://docs.google.com/spreadsheets/d/1jgdgE5qjDeQsg2fFtRrT94zJ-WMcPKY6ONlMxK5j4h8/copy','inventory':'https://docs.google.com/spreadsheets/d/1SNuArxxon0Xc-n5w99FC5CnKzTQv4d5GwBlaYXRrigo/copy','cinsp':'https://docs.google.com/document/d/1GQ7LoQJ6vD8CUbetmy-pSZk1HGRcurs4sy7azYDNdUM/copy','contracts':'https://drive.google.com/drive/folders/1otwNaUim6hQdOs9OB3djB3-2Rz9-WiD8?usp=sharing','insp':'https://drive.google.com/drive/folders/1QEj4MpC84wojY4ud7A4thiE4GqJTrpBI?usp=sharing'},
     'pt':{'scripts':'https://drive.google.com/file/d/16TM7dmX0G0L0GVIpMTuzmBFAAFVE_e8U/view','finance':'https://docs.google.com/spreadsheets/d/14n1UYJdzRobrM01flpkxmYbRC_Dz8w5pEYGjUoB3W3A/copy','checklists':'https://docs.google.com/spreadsheets/d/1qBvIuEAxEnTuW7jBzQ_fb0SizfdwtD8_SsXVO_kiwJk/copy','inventory':'https://docs.google.com/spreadsheets/d/1ChgSaALZ26T3Enro3SNYFGMY2qDoW3cdMgQE5a2Hmzg/copy','cinsp':'https://docs.google.com/document/d/1YM4f67BGCPTFngVnR7xKuhYTuNmxR475rYVWhAiL-x0/copy','contracts':'https://drive.google.com/drive/folders/1u6Oc86RbVeHPVQxSfzHNSibn90B3r9L8?usp=sharing','insp':'https://drive.google.com/drive/folders/1U6a20UA1CKaxeDW-CnZM36v9-rXerU58?usp=sharing'}}
DLM={'es':{'cleaning-inspection':'inspeccion-limpieza','cleaning-services-agreement':'acuerdo-servicios-limpieza','deep-cleaning-checklist':'checklist-limpieza-a-fondo','handyman-agreement':'acuerdo-manitas','landlord-scripts':'guiones-propietarios','maintenance-inspection':'inspeccion-mantenimiento','pool-garden-checklist':'checklist-piscina-jardin','pool-garden-maintenance-agreement':'acuerdo-mantenimiento-piscina-jardin','property-manager-agreement':'acuerdo-gestor-alojamiento','turnover-checklist':'checklist-cambio-huesped'},
     'pt':{'cleaning-inspection':'inspecao-limpeza','cleaning-services-agreement':'acordo-servicos-limpeza','deep-cleaning-checklist':'checklist-faxina-pesada','handyman-agreement':'acordo-faz-tudo','landlord-scripts':'roteiros-proprietarios','maintenance-inspection':'inspecao-manutencao','pool-garden-checklist':'checklist-piscina-jardim','pool-garden-maintenance-agreement':'acordo-manutencao-piscina-jardim','property-manager-agreement':'acordo-gerente-imovel','turnover-checklist':'checklist-troca-hospede'}}
s=open(P).read()
for L in ('es','pt'):
    h={EN[k]:IDS[L][k] for k in EN}
    s=s.replace('/*HREF_%s*/{}'%L.upper(),json.dumps(h),1).replace('/*DL_%s*/{}'%L.upper(),json.dumps(DLM[L]),1)
assert '/*HREF' not in s and '/*DL_' not in s
open(P,'w').write(s); print('maps ok')
# --- plain text language switch: ENG | NL | ESP | POR ---
s=open(P).read()
i=s.find('<div class="lang" id="langSel">'); j=s.find('</div></div>',i)+12
assert i>0
LBL=[('en','ENG','Switch to English','English'),('nl','NL','Switch to Dutch','Nederlands'),('es','ESP','Switch to Spanish','Español'),('pt','POR','Switch to Portuguese','Português (Brasil)')]
btns='<span class="lsep" aria-hidden="true">|</span>'.join('<button type="button" data-lang="%s" aria-label="%s" title="%s" aria-pressed="false">%s</button>'%(k,a,t,c) for k,c,a,t in LBL)
s=s[:i]+'<div class="lang" id="langSel" role="group" aria-label="Language">'+btns+'</div>'+s[j:]
ci=s.find('.lang{position:relative;flex:none}'); cj=s.find('.lang .lc-flag .flag{width:22px;height:15px}}',ci)+len('.lang .lc-flag .flag{width:22px;height:15px}}')
assert ci>0 and cj>ci
s=s[:ci]+('.lang{display:flex;align-items:center;gap:2px;flex:none}\n'
'.lang button{font:700 12px/1 var(--body);letter-spacing:.06em;color:rgba(244,242,239,.7);background:transparent;border:0;border-radius:6px;padding:6px 6px;cursor:pointer;transition:color .15s}\n'
'.lang button:hover{color:#f4f2ef}\n'
'.lang button.on{color:#f4f2ef;text-decoration:underline;text-underline-offset:4px;text-decoration-thickness:2px}\n'
'.lang button:focus-visible{outline:2px solid #fff;outline-offset:1px}\n'
'.lang .lsep{color:rgba(244,242,239,.45);font-size:12px}\n'
'@media (max-width:860px){.lang button{padding:5px 3px;font-size:11px}.lang .lsep{font-size:11px}}')+s[cj:]
s=s.replace(',.lang-menu button.on,',',',1)
a=s.find("$$('.lang-menu button').forEach(function(b){var on="); b=s.find("});",s.find("$('.lc-code',c)",a))+3
assert a>0
s=s[:a]+"$$('.lang button[data-lang]').forEach(function(b){var on=b.dataset.lang===LANG;b.classList.toggle('on',on);b.setAttribute('aria-pressed',on?'true':'false');});"+s[b:]
a=s.find("(function(){var cur=document.getElementById('langCur')"); b=s.find("})();",a)+5
assert a>0
s=s[:a]+"$$('.lang button[data-lang]').forEach(function(b){b.addEventListener('click',function(){S.fields.lang=b.dataset.lang;save();applyLang();});});"+s[b:]
assert 'langCur' not in s and 'lang-menu' not in s
open(P,'w').write(s); print('plain switch ok')
# --- top switch: "Host starter kit" instead of "Bonus & extras" ---
s=open(P).read()
n=s.count('data-t=\\"2523\\">Bonus &amp; extras</button>')+s.count('data-t="2523">Bonus &amp; extras</button>')
s=s.replace('data-t=\\"2523\\">Bonus &amp; extras</button>','data-t=\\"2523\\">Host starter kit</button>').replace('data-t="2523">Bonus &amp; extras</button>','data-t="2523">Host starter kit</button>')
o="EN_HTML['2523']='Bonus &amp; extras'"; assert s.count(o)==1; s=s.replace(o,"EN_HTML['2523']='Host starter kit'")
k0=s.find('var I18N=')+len('var I18N='); d,end=json.JSONDecoder().raw_decode(s[k0:])
for L,v in {'nl':'Host-starterskit','es':'Kit de inicio para anfitriones','pt':'Kit inicial de anfitrião'}.items(): d[L]['u']['2523']=v
s=s[:k0]+json.dumps(d,ensure_ascii=False).replace('</','<\\/')+s[k0+end:]
open(P,'w').write(s); print('starter kit ok',n)
# --- texture + gradient finish (terracotta: wall texture, green: paper texture, both at 50%) ---
s=open(P).read()
TS='.top,.btn,.rlink,.share,.ig-btn,.commcta .cc-btn,.hero .herobtn,.revbtn,.resume-btn,.tnote a.tbtn,.side a.aff,.cel-badge,.pweek,.ba-a,.chip.rec,.side .tag'
TH='.btn:hover,.rlink:hover,.revbtn:hover,.resume-btn:hover,.side a.aff:hover,.ig-btn:hover,.commcta .cc-btn:hover,.hero .herobtn:hover,.tnote a.tbtn:hover'
GS='.hero,.video,.side .home,.side .home.on,.btn.dark,.btn.dark:hover,.share .btn,.share .btn:hover,.cel-next,.vk-stat,.gold,.finale,.trio3 div,.commcta,.vk-yes,.tipbox,.addon,.copy header,.toast'
fx=('\n/* finish: soft gradients + material textures. Terracotta carries the plaster wall, green carries the paper (both images at 50% opacity) */\n'
':root{--tex-t:url(img/tex-terra.webp);--tex-g:url(img/tex-paper.webp);'
'--grad-t:linear-gradient(135deg,#B06C5C 0%,#A05F50 52%,#8C5245 100%);'
'--grad-th:linear-gradient(135deg,#9A5A4C 0%,#8A4F42 52%,#763F34 100%);'
'--grad-g:linear-gradient(135deg,#3D483F 0%,#313A33 52%,#262D27 100%)}\n'
+TS+'{background-image:var(--tex-t),var(--grad-t)!important;background-size:620px auto,100% 100%!important;background-position:center,center!important;background-repeat:repeat,no-repeat!important;background-blend-mode:luminosity,normal!important}\n'
+TH+'{background-image:var(--tex-t),var(--grad-th)!important}\n'
+GS+'{background-image:var(--tex-g),var(--grad-g)!important;background-size:cover,100% 100%!important;background-position:center,center!important;background-repeat:no-repeat,no-repeat!important;background-blend-mode:soft-light,normal!important}\n'
''
'')
i=s.rfind('</style>'); s=s[:i]+fx+s[i:]
open(P,'w').write(s); print('fx ok')
# --- plant shadows: one per page, scrolls with the page ---
s=open(P).read()
ids=re.findall(r'<section[^>]*class="lesson[^"]*"[^>]*id="([^"]+)"|<section[^>]*id="([^"]+)"[^>]*class="lesson',s)
ids=[a or b for a,b in ids]
if not ids: ids=re.findall(r'class="lesson[^"]*" id="([^"]+)"',s)
SIDE={1:'right',2:'right',3:'right',4:'left',5:'right'}
css=['\n/* plant shadows: soft light through a window, pinned to the page so they scroll with it */',
 '#main{position:relative;overflow-x:clip}',
 '#main::before,#main::after{content:"";position:absolute;pointer-events:none;z-index:3;background-repeat:no-repeat;background-size:contain}',
 '#main::before{top:0;right:0;width:min(58%,720px);height:min(1080px,120vh);background-position:top right;opacity:.13;background-image:var(--shade-top,url(img/shade-1.webp))}',
 '#main::after{bottom:0;left:0;width:min(46%,560px);height:760px;background-position:top right;opacity:.11;background-image:var(--shade-bot,url(img/shade-5.webp));transform:scale(-1,-1)}',
 '#main.sh-l::before{right:auto;left:0;background-position:top left}',
 '#main.sh-r::after{left:auto;right:0;background-position:top left;transform:scaleY(-1)}',
 '@media (max-width:860px){#main::before{width:78%;height:720px;opacity:.11}#main::after{width:70%;height:520px;opacity:.09}}',
 '@media print{#main::before,#main::after{display:none}}']
open(P,'w').write(s)
s=s[:s.rfind('</style>')]+'\n'.join(css)+'\n'+s[s.rfind('</style>'):]
# JS: pick shades per page on route change
js=("<script>(function(){var m=document.getElementById('main');if(!m)return;var L=[].slice.call(document.querySelectorAll('.lesson')).map(function(e){return e.id;});"
 "var SIDE={1:'r',2:'r',3:'r',4:'l',5:'r'};"
 "function set(){var on=document.querySelector('.lesson.on');var i=Math.max(0,L.indexOf(on?on.id:''));var a=(i%5)+1,b=((i+2)%5)+1;if(b===a)b=(a%5)+1;"
 "m.style.setProperty('--shade-top','url(img/shade-'+a+'.webp)');m.style.setProperty('--shade-bot','url(img/shade-'+b+'.webp)');"
 "m.classList.toggle('sh-l',SIDE[a]==='l');m.classList.toggle('sh-r',SIDE[b]==='l');}"
 "set();window.addEventListener('hashchange',function(){setTimeout(set,0);});new MutationObserver(set).observe(m,{subtree:true,attributes:true,attributeFilter:['class']});})();</script>")
i=s.rfind('</body>'); s=s[:i]+js+s[i:]
open(P,'w').write(s); print('shades ok')
# --- buttons: gradient only, no texture ---
s=open(P).read()
BT='.btn,.rlink,.ig-btn,.commcta .cc-btn,.hero .herobtn,.revbtn,.resume-btn,.tnote a.tbtn,.side a.aff,.cel-badge,.chip.rec,.side .tag,.pweek,.ba-a'
BTH='.btn:hover,.rlink:hover,.revbtn:hover,.resume-btn:hover,.side a.aff:hover,.ig-btn:hover,.commcta .cc-btn:hover,.hero .herobtn:hover,.tnote a.tbtn:hover'
BG='.btn.dark,.btn.dark:hover,.share .btn,.share .btn:hover,.cel-next,.side .home,.side .home.on,.toast,.vk-yes'
fx=('\n/* buttons keep only the soft gradient */\n'+BT+'{background-image:var(--grad-t)!important;background-size:100% 100%!important;background-repeat:no-repeat!important;background-blend-mode:normal!important}\n'
 +BTH+'{background-image:var(--grad-th)!important}\n'
 +BG+'{background-image:var(--grad-g)!important;background-size:100% 100%!important;background-repeat:no-repeat!important;background-blend-mode:normal!important}\n')
i=s.rfind('</style>'); s=s[:i]+fx+s[i:]
open(P,'w').write(s); print('buttons ok')
# --- dynamic rewrites of text-heavy sections (L4 s1+s4, L5 s1+s3, L6 s1+s2 intro) ---
sys.path.insert(0,'/home/claude/nl')
from newcontent import T as NT
s=open(P).read()
def t(i,tag='span',cls=''):
    c=' class="%s"'%cls if cls else ''
    return '<%s%s data-t="%s">%s</%s>'%(tag,c,i,NT[i][0],tag)
def orig(i):
    m=re.search(r'<(\w+)([^>]*) data-t="%s"([^>]*)>(.*?)</\1>'%i,s,re.S); assert m,i; return m.group(0)
def li(ids): return '<ul>'+''.join(t(i,'li') for i in ids)+'</ul>'
def card(inner,cls=''): return '<div class="vk-card%s">%s</div>'%((' '+cls) if cls else '',inner)
def n(k): return '<span class="vk-n">%s</span>'%k
def tag(i): return '<div class="vk-tag">%s</div>'%t(i)
def tip(i): return '<div class="vk-tip">%s</div>'%t(i,'span')
def gold(k,p): return '<div class="gold"><span class="gold-k" data-t="%s">%s</span><p><strong data-t="%s">%s</strong></p></div>'%(k,NT[k][0],p,NT[p][0])
def steps(items):
    out=[]
    for j,(h,p) in enumerate(items,1):
        wide=' vk-wide' if (j==len(items) and len(items)%2) else ''
        out.append('<div class="vk-step%s">%s%s%s</div>'%(wide,n(j),t(h,'h4'),t(p,'p') if p else ''))
    return '<div class="vk-steps">'+''.join(out)+'</div>'
def repl(a_marker,b_marker,new,start_after=True):
    global s
    a=s.find(a_marker); assert a>0,a_marker
    a2=a+len(a_marker) if start_after else a
    b=s.find(b_marker,a2); assert b>0,b_marker
    s=s[:a2]+new+s[b:]
# L4 s1
new=(t('3001','p')+'<div class="vk-two">'+card(tag('3002')+t('3003','h4')+t('3004','p'))+card(tag('3005')+t('3006','h4')+t('3007','p'),'vk-yes')+'</div>'
 +tip('3008')+t('3009','h4')
 +'<div class="vk-two">'+card(n(1)+t('3010','h4')+t('3011','p')+li(['3012','3013']))+card(n(2)+t('3014','h4')+t('3015','p')+li(['3016','3017','3018','3019']))+'</div>'
 +'<div class="vk-stat"><b data-t="3020">%s</b>%s</div>'%(NT['3020'][0],t('3021'))
 +t('3022','h4')+steps([(k,None) for k in ['3023','3024','3025','3026','3027']])
 +tip('3028')+gold('3029','3030')+'\n')
a=s.find('<p class="sub" data-t="629">'); a=s.find('</p>',a)+5; b=s.find('</section>',a); s=s[:a]+new+s[b:]
# L4 s4
h661=orig('661')
new=(t('3031','p')+h661+steps([('3032','3033'),('3034','3035'),('3036','3037'),('3038','3039'),('3040','3041'),('3042','3043'),('3044','3045')])
 +'<h4 data-t="688">What to look for</h4><div class="vk-g3">'+card(t('3046','h4')+t('3047','p'),'vk-yes')+card(t('3048','h4')+t('3049','p'),'vk-no')+card(t('3050','h4')+t('3051','p'))+'</div>\n')
a=s.find('<h2 data-t="679">'); a=s.find('</h2>',a)+5; b=s.find('<p class="tip" data-t="692">',a); s=s[:a]+new+s[b:]
# L5 s1
plat=''.join(orig(i) for i in ['709','710','711','712','713','714'])
new=(t('3052','p')+tip('3053')+'<div class="vk-two">'+card(n(1)+t('3054','h4')+t('3055','p')+t('3056','p'))+card(n(2)+t('3057','h4')+'<ul>'+plat+'</ul>')+'</div>\n')
a=s.find('<h2 data-t="702">'); a=s.find('</h2>',a)+5; b=s.find('<div class="checklist">',a); s=s[:a]+'\n'+new+s[b:]
# L5 s3
costs=''.join(orig(i) for i in ['746','747','748','749','750'])
new=(t('3058','p')+'<div class="vk-two">'+card(t('3059','h4')+t('3060','p'))+card(t('3061','h4')+t('3062','p'),'vk-yes')+'</div>'
 +orig('745')+'<ul class="hd-ticks">'+costs+'</ul>'
 +'<div class="vk-two">'+card(tag('3063')+t('3064','h4')+li(['3065','3066','3067']),'vk-yes')+card(tag('3068')+t('3069','h4')+li(['3070','3071','3072','3073']))+'</div>'
 +gold('3074','3075')+'\n')
a=s.find('<h3 data-t="742">'); a=s.find('</h3>',a)+5; b=s.find('<div class="card">',a); s=s[:a]+'\n'+new+s[b:]
# L6 s1 top
offer=''.join(orig(i) for i in ['800','801','802','803'])
new=(t('3076','p')+'<p><em><strong data-t="797">%s</strong></em></p>'%re.search(r'data-t="797">(.*?)</strong>',s).group(1)
 +t('3077','h4')+'<div class="trio3">'+''.join('<div><b data-t="%s">%s</b><span data-t="%s">%s</span></div>'%(b_,NT[b_][0],c_,NT[c_][0]) for b_,c_ in [('3078','3079'),('3080','3081'),('3082','3083')])+'</div>'
 +t('3084','p')+card(tag('3085')+orig('799')+'<ul>'+offer+'</ul>','vk-yes')+tip('3086')
 +'<div class="vk-grid3">'+card(n(1)+t('3087','h4')+t('3088','p'))+card(n(2)+t('3089','h4')+t('3090','p'))+card(n(3)+t('3091','h4')+t('3092','p'))+card(n(4)+t('3093','h4')+t('3094','p'))+'</div>\n')
a=s.find('<p class="sub" data-t="795">'); a=s.find('</p>',a)+5; b=s.find('<p class="hd-open">',a); s=s[:a]+'\n'+new+s[b:]
# L6 coliving
new='<div class="vk-two">'+card(t('3095','h4')+t('3096','p'),'vk-no')+card(t('3097','h4')+t('3098','p'),'vk-yes')+'</div>'+tip('3100')+'\n'
a=s.find('<h4 class="tc" data-t="823">'); a=s.find('</h4>',a)+5; b=s.find('<h4 class="tc" data-t="826">',a); s=s[:a]+'\n'+new+s[b:]
# L6 s2 intro
a=s.find('<p data-t="867">'); b=s.find('<h3 data-t="869">',a); s=s[:a]+t('3101','p')+tip('3102')+'\n'+s[b:]
# translations
k0=s.find('var I18N=')+len('var I18N='); d,end=json.JSONDecoder().raw_decode(s[k0:])
for i,v in NT.items():
    for L,x in zip(('nl','es','pt'),v[1:]): d[L]['u'][i]=x
s=s[:k0]+json.dumps(d,ensure_ascii=False).replace('</','<\\/')+s[k0+end:]
s=s[:s.rfind('</style>')]+'\n.vk-g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:14px 0 20px}.vk-g3 .vk-card h4{font-size:15.5px}@media (max-width:760px){.vk-g3{grid-template-columns:1fr}}\n.vk-steps .vk-step h4:only-of-type:last-child{margin-bottom:0!important}\n'+s[s.rfind('</style>'):]
open(P,'w').write(s); print('rewrites ok')

# --- finish v2: gradients right-to-left, softer navbar, boxes depth, tables, cherry, third shadow ---
s=open(P).read()
fx2="""
/* finish v2 */
:root{--grad-t:linear-gradient(to left,#A86555 0%,#97594B 55%,#82473A 100%);--grad-th:linear-gradient(to left,#93574A 0%,#80493D 55%,#6C3B30 100%);--grad-g:linear-gradient(to left,#3B463D 0%,#313A33 55%,#262D27 100%);--grad-b:linear-gradient(to left,#4C4743 0%,#383330 55%,#2A2624 100%)}
.top{background-image:url(img/tex-terra-soft.webp),linear-gradient(to right,#AA6757 0%,#9C5C4D 55%,#8A4E41 100%)!important}
.donebtn,.donebox .donebtn,.donebox .donebtn:hover,.savebox,.copy.tog:not(.open),.ba-b,.navsw-side,.srch-x{background-image:var(--grad-b)!important;background-size:100% 100%!important;background-repeat:no-repeat!important}
.card,.vk-card:not(.vk-yes),.vk-step,.jour-c,.rf,.tips4 div,.donebox,.tool,details.obj,.platbox,.flow-step>div,.tiles>div,.pn a,.cel-card,.pbox,.mk,.tex-c,.decide,.opt,.notes,.rev-card,.chartcard,.hd-box,.brochure,.res,.map a,.choice:not(.sel),.mbadge{background-image:linear-gradient(to left,rgba(255,255,255,.55) 0%,rgba(255,255,255,.18) 45%,rgba(0,0,0,.02) 100%)}
.cmp{border:1px solid #CFCAC2}
.cmp tbody th{border-right:1px solid #D3CEC7}
.cmp thead th{border-bottom:1px solid #CFCAC2}
.cherry{background:var(--paper)!important;border-color:#E2CE9C}
.cherry .bubble,.cherry .bubble:after{background:var(--stone)}
.side a.aff .t{flex:none;text-align:center}
.vk-card:not(.vk-yes):not(.vk-no) .vk-tag{background:rgba(160,95,80,.12);color:#A05F50}
.lesson.on{position:relative}
.lesson.on::after{content:"";position:absolute;pointer-events:none;z-index:3;top:42%;width:620px;height:820px;background:var(--shade-mid,url(img/shade-2.webp)) no-repeat top left/contain;opacity:.1;left:-300px}
#main.sh-m .lesson.on::after{left:auto;right:-300px;background-position:top right;transform:scaleX(-1)}
@media (max-width:860px){.lesson.on::after{width:420px;height:560px;left:-160px;opacity:.08}#main.sh-m .lesson.on::after{right:-160px}}
@media print{.lesson.on::after{display:none}}
"""
s=s[:s.rfind('</style>')]+fx2+s[s.rfind('</style>'):]
o="m.classList.toggle('sh-l',SIDE[a]==='l');m.classList.toggle('sh-r',SIDE[b]==='l');"
assert o in s
s=s.replace(o,o+"var c=((i+3)%5)+1;if(c===a||c===b)c=((i+4)%5)+1;m.style.setProperty('--shade-mid','url(img/shade-'+c+'.webp)');m.classList.toggle('sh-m',i%2===1);")
open(P,'w').write(s); print('finish v2 ok')

# --- finish v3: shadows behind content, cement background, navbar dark-left ---
s=open(P).read()
fx3="""
/* finish v3 */
.top{background-image:url(img/tex-terra-soft.webp),linear-gradient(to right,#7E4639 0%,#93564A 50%,#AE6B5B 100%)!important}
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background:url(img/micro-cement.webp) center/cover no-repeat}
#main,.lesson.on{isolation:isolate}
#main::before,#main::after,.lesson.on::after{z-index:-1!important}
.pills button{background-color:var(--stone)}
@media print{body::before{display:none}}
"""
s=s[:s.rfind('</style>')]+fx3+s[s.rfind('</style>'):]
open(P,'w').write(s); print('finish v3 ok')

# --- perf v4: scrolling cement on body (opaque baked tile), lighter shadows, lazy images ---
s=open(P).read()
fx4="""
/* perf v4 */
body::before{content:none!important;display:none!important}
body{background:var(--stone) url(img/micro-cement.webp) 0 0/1800px auto repeat}
"""
s=s[:s.rfind('</style>')]+fx4+s[s.rfind('</style>'):]
import re as _re
def _lz(m):
    t=m.group(0)
    if 'loading=' in t or 'id="lbimg"' in t or 'img/cover.' in t: return t
    return t.replace('<img ','<img loading="lazy" ',1)
s=_re.sub(r'<img [^>]*>',_lz,s)
open(P,'w').write(s); print('perf v4 ok')
# photo tone is now baked into the image files (see orig-photos/), so no runtime CSS filter
s=open(P).read()
s=s[:s.rfind('</style>')]+"\n.lesson img,.hero img,.lb img{filter:none!important}\n"+s[s.rfind('</style>'):]
open(P,'w').write(s); print('nofilter ok')
# prev/next links at the bottom of lessons: plain, no box gradient
s=open(P).read()
s=s[:s.rfind('</style>')]+"\n.pn a,.pn a:hover{background:none!important;background-image:none!important;box-shadow:none!important;border:0!important}\n"+s[s.rfind('</style>'):]
open(P,'w').write(s); print('pn ok')

# --- progress sync for the team dashboard: a short summary only (lessons done, ticked-task count, last page, language) ---
s=open(P).read()
sync="""<script>
(function(){var KEY='sixfig-course-v1',L=['start','story','roadmap','ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8','ch9','ch10','ch11','ch12','ch13'],last='',t0=0,tm;
if(!/^https?:$/.test(location.protocol)||!/(^|\\.)6figurehost\\.com$|pages\\.dev$|^localhost$|^127\\.0\\.0\\.1$/.test(location.hostname))return;
function snap(){var S={};try{S=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){}var d=S.done||{},t=S.tasks||{},f=S.fields||{};
return JSON.stringify({done:L.filter(function(k){return !!d[k]}),tasks:Object.keys(t).filter(function(k){return !!t[k]}).length,last:String(f.last_pos||location.hash.slice(1)||'').slice(0,40),lang:f.lang||'en'})}
function send(force){var b=snap(),now=Date.now();if(!force&&b===last&&now-t0<15*60e3)return;if(!force&&now-t0<60e3){clearTimeout(tm);tm=setTimeout(function(){send(true)},60e3-(now-t0));return}
last=b;t0=now;try{fetch('/api/progress',{method:'POST',headers:{'Content-Type':'application/json'},body:b,keepalive:true,credentials:'same-origin'}).catch(function(){})}catch(e){}}
setTimeout(function(){send(true)},4000);setInterval(send,60e3);
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden')send()});})();
</script>
"""
i=s.rfind('</body>'); s=s[:i]+sync+s[i:]
open(P,'w').write(s); print('sync ok')

# --- lesson 8: platforms row: no arrows/asterisk, only Airbnb, Booking.com, Vrbo; Airbnb highlighted ---
s=open(P).read()
import re as _re
a=s.index('<div class="plats"><span data-t="1071">'); b=s.index('</div>',a)+6
s=s[:a]+'<div class="plats"><span data-t="1071">Platforms:</span><a class="pl-main" data-t="1072" href="https://www.airbnb.com/rp/6figurehost" rel="noopener" target="_blank">Airbnb</a><a data-t="1073" href="https://join.booking.com/" rel="noopener" target="_blank">Booking.com</a><a data-t="1074" href="https://www.vrbo.com/list-your-property" rel="noopener" target="_blank">Vrbo</a></div>'+s[b:]
s=s[:s.rfind('</style>')]+"\n.plats a.pl-main{background:var(--grad-t,#A05F50);background-color:#A05F50;border-color:#A05F50;color:#F4F2EF}.plats a.pl-main:hover{background:#8A4E41;border-color:#8A4E41;color:#F4F2EF}\n"+s[s.rfind('</style>'):]
open(P,'w').write(s); print('plats ok')

# --- lesson 8 "Your description = your story": icons instead of a. b. c. d. e. ---
s=open(P).read()
import re as _re, urllib.parse as _up
ICONS={
 '1107':('house','<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9v11h14V9"/><path d="M10 20v-6h4v6"/>'),
 '1108':('run','<circle cx="14" cy="4.5" r="2"/><path d="M8 21l3-6 3 3v3"/><path d="M6 12l3-4 5 1 3 4h3"/><path d="M11 15l1.5-5.5"/>'),
 '1109':('pin','<path d="M12 21s-7-6.3-7-12a7 7 0 0 1 14 0c0 5.7-7 12-7 12z"/><circle cx="12" cy="9" r="2.6"/>'),
 '1110':('wifi','<path d="M2.5 9a14 14 0 0 1 19 0"/><path d="M5.5 12.5a9.5 9.5 0 0 1 13 0"/><path d="M8.7 15.8a4.8 4.8 0 0 1 6.6 0"/><circle cx="12" cy="19" r="1.2" fill="#000"/>'),
 '1111':('spark','<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>'),
}
css=['\n.desc-ic{position:relative;padding-left:40px}',
 '.desc-ic::before{content:"";position:absolute;left:0;top:0;width:28px;height:28px;border-radius:8px;background:rgba(160,95,80,.12)}',
 '.desc-ic::after{content:"";position:absolute;left:5px;top:5px;width:18px;height:18px;background:#A05F50;-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}']
for tid,(name,paths) in ICONS.items():
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+paths+'</svg>'
    css.append('.desc-ic.ic-%s{--ic:url("data:image/svg+xml,%s")}'%(name,_up.quote(svg,safe='')))
    o='<p data-t="%s">'%tid; assert o in s, tid
    s=s.replace(o,'<p class="desc-ic ic-%s" data-t="%s">'%(name,tid),1)
    n0=len(s)
    s=_re.sub(r'((?:data-t="%s">|"%s": ")<strong>)[a-e]\. '%(tid,tid),r'\1',s)
s=s[:s.rfind('</style>')]+'\n'.join(css)+'\n'+s[s.rfind('</style>'):]
open(P,'w').write(s); print('desc icons ok')

# --- numbered headings as rounded number badges (lesson 8 first; extend NUM_LESSONS after approval) ---
NUM_LESSONS=None  # None = every lesson
s=open(P).read()
import re as _re
def _numify(s, lid):
    a=s.find('<article class="lesson" id="%s"'%lid); assert a>0, lid
    b=s.find('<article class="lesson"',a+10); b=b if b>0 else s.find('</main>',a)
    part=s[a:b]; ids=[]
    def rep(m):
        ids.append(m.group(3))
        return '<h4 class="num-h" data-n="%s" data-t="%s">%s'%(m.group(2),m.group(3),m.group(4))
    part=_re.sub(r'<h4( )data-t="(?P<x>\d+)">(\d+)\.\s','',part) if False else part
    part=_re.sub(r'<h4 data-t="(\d+)">(\d+)\.\s',lambda m:(ids.append(m.group(1)),'<h4 class="num-h" data-n="%s" data-t="%s">'%(m.group(2),m.group(1)))[1],part)
    s=s[:a]+part+s[b:]
    for t in ids:
        s=_re.sub(r'("%s": ")\d+\.\s'%t,r'\1',s)
    return s, ids
for _l in (NUM_LESSONS or _re.findall(r'<article class="lesson" id="([^"]+)"',s)):
    s,_ids=_numify(s,_l); print('num',_l,len(_ids))
s=s[:s.rfind('</style>')]+"""
h4.num-h{display:flex;align-items:center;gap:10px}
h4.num-h::before{content:attr(data-n);flex:none;display:inline-grid;place-items:center;width:26px;height:26px;border-radius:8px;background:#A05F50;background-image:var(--grad-t);color:#F4F2EF;font:700 13px/1 var(--body,Arial),Arial,sans-serif;letter-spacing:0}
"""+s[s.rfind('</style>'):]
open(P,'w').write(s); print('num-h ok')

# --- Bonus lesson "Difficult guests"; sidebar: old "Bonus" group becomes "Tools", new "Bonus" group ---
import importlib, guests as _g; importlib.reload(_g)
G=dict(_g.T)
import overrides as _o; importlib.reload(_o); G.update(_o.O)
s=open(P).read()
def gt(i,tag='span',cls=''):
    c=' class="%s"'%cls if cls else ''
    return '<%s%s data-t="%s">%s</%s>'%(tag,c,i,G[i][0],tag)
def gn(k): return '<span class="vk-n">%s</span>'%k
def gcard(inner,cls=''): return '<div class="vk-card%s">%s</div>'%((' '+cls) if cls else '',inner)
def chat(title,msgs,why,extra=''):
    out=('<details class="gx"><summary class="gx-h"><span class="gx-k" data-t="3297">'+G['3297'][0]+'</span>'+gt(title,'h4')
         +'<span aria-hidden="true" class="gx-chev"></span></summary><div class="gx-body"><div class="chat">')
    for who,i in msgs:
        out+='<div class="msg %s">%s%s</div>'%(who, gt('3259' if who=='g' else '3260','small'), gt(i,'p'))
    out+='</div><p class="gx-why"><b data-t="3261">%s</b> <span data-t="%s">%s</span></p>'%(G['3261'][0],why,G[why][0])
    if extra: out+='<p class="gx-link"><a data-t="%s" href="#ch9-p4">%s</a></p>'%(extra,G[extra][0])
    return out+'</div></details>'
def ext(href,i): return '<a class="gx-ext" data-t="%s" href="%s" rel="noopener" target="_blank">%s ↗</a>'%(i,href,G[i][0])
FOOT=s[s.find('<div class="foot">',s.find('<article class="lesson" id="bonus-mistakes"')):]
FOOT=FOOT[:FOOT.find('</div>\n</article>')+6]
art=('<article class="lesson" id="bonus-guests">\n'
 '<header class="lhead"><div class="lh-main">'+gt('3203','span','eyebrow')+'<h1 data-t="3204">'+G['3204'][0]+'</h1>'+gt('3205','p','sub')+'</div>'
 '<div class="lh-side"><span aria-hidden="true" class="mbadge sym"><small data-t="3201">Bonus</small><b>★</b></span><button class="backlink" hidden="" type="button"><span aria-hidden="true">←</span> <span class="bl-t" data-t="119">Back</span></button></div>\n</header>\n'
 +gt('3207','p')+'\n'
 +'<h3 data-t="3208">'+G['3208'][0]+'</h3>'+gt('3209','p')+gt('3210','p')
 +'<div class="vk-two">'+gcard(gt('3211','h4')+gt('3212','p'),'vk-no')+gcard(gt('3213','h4')+gt('3214','p'),'vk-yes')+'</div>\n'
 +'<h3 data-t="3215">'+G['3215'][0]+'</h3>'+gt('3216','p')
 +'<div class="vk-steps">'+''.join('<div class="vk-step%s">%s%s%s</div>'%(' vk-wide' if j==5 else '',gn(j),gt(h,'h4'),gt(q,'p')) for j,(h,q) in enumerate([('3217','3218'),('3219','3220'),('3221','3222'),('3223','3224'),('3225','3226')],1))+'</div>\n'
 +'<h3 data-t="3227">'+G['3227'][0]+'</h3>'+gt('3228','p')
 +'<div class="vk-g3">'+gcard(gn(1)+gt('3229','h4')+gt('3230','p'))+gcard(gn(2)+gt('3231','h4')+gt('3232','p'))+gcard(gn(3)+gt('3233','h4')+gt('3234','p'))+'</div>'
 +'<div class="gx-line">'+gt('3235','span','vk-tag')+gt('3236','p')+'</div>'
 +'<div class="gold"><span class="gold-k" data-t="3237">'+G['3237'][0]+'</span><p data-t="3238">'+G['3238'][0]+'</p></div>\n'
 +'<h3 data-t="3239">'+G['3239'][0]+'</h3>'+gt('3240','p')
 +chat('3241',[('g','3242'),('h','3243'),('g','3244'),('h','3245')],'3246','3361')
 +chat('3247',[('g','3248'),('h','3249'),('g','3250'),('h','3251')],'3252')
 +chat('3253',[('g','3254'),('h','3255'),('g','3256'),('h','3257')],'3258','3362')+'\n'
 +'<h3 data-t="3262">'+G['3262'][0]+'</h3>'
 +'<div class="vk-two">'+gcard(gt('3263','h4')+gt('3264','p')+ext('https://www.airbnb.com/help/article/2673','3265'))+gcard(gt('3266','h4')+gt('3267','p')+ext('https://www.airbnb.com/help/article/2799','3268'))+'</div>\n'
 +'<h3 data-t="3269">'+G['3269'][0]+'</h3>'
 +gcard('<ul>'+''.join(gt(i,'li') for i in ['3270','3271','3272','3273'])+'</ul>','vk-no')
 +'<div class="vk-tip">'+gt('3274')+'</div>\n'
 +'<h3 data-t="3275">'+G['3275'][0]+'</h3>'
 +'<div class="vk-g3">'+gcard(gt('3276','h4')+gt('3277','p'))+gcard(gt('3278','h4')+gt('3279','p'))+gcard(gt('3280','h4')+gt('3281','p'))+'</div>'
 +'<div class="copy"><header><span data-t="3282">'+G['3282'][0]+'</span><span><button class="btn-s cp" data-t="477" type="button">Copy</button></span></header><div class="src" data-t="3283">'+G['3283'][0]+'</div>'
 +'<div class="ai-links"><span data-t="479">Copy and open in:</span><a data-t="480" href="https://chatgpt.com/" rel="noopener" target="_blank">ChatGPT</a><a data-t="481" href="https://gemini.google.com/" rel="noopener" target="_blank">Gemini</a><a data-t="482" href="https://claude.ai/" rel="noopener" target="_blank">Claude</a></div></div>\n'
 +'<div class="checklist"><div class="label"><span data-t="322">Your tasks</span></div>'
 +''.join('<label class="task"><input data-task="bg-t%d" type="checkbox"/><span data-t="%s">%s</span></label>'%(j,i,G[i][0]) for j,i in enumerate(['3284','3285','3286'],1))+'</div>\n'
 +'<div class="gold"><span class="gold-k" data-t="3287">'+G['3287'][0]+'</span><p data-t="3288">'+G['3288'][0]+'</p></div>\n'
 +'<div class="pn"><a data-t="3292" href="#bonus-declutter">'+G['3292'][0]+'</a><a class="next" data-t="3293" href="#bonus-mistakes">'+G['3293'][0]+'</a></div>\n'
 +FOOT+'\n</article>\n')
a=s.find('<article class="lesson" id="bonus-mistakes"'); assert a>0
s=s[:a]+art+s[a:]
# prev/next chain: declutter -> guests -> mistakes
import re as _re2
s=_re2.sub(r'<a class="next" data-t="2437" href="#bonus-mistakes">.*?</a>','<a class="next" data-t="3294" href="#bonus-guests">'+G['3294'][0]+'</a>',s,1,flags=_re2.S)
s=_re2.sub(r'<a data-t="2475" href="#bonus-declutter">.*?</a>','<a data-t="3295" href="#bonus-guests">'+G['3295'][0]+'</a>',s,1,flags=_re2.S)
# mistakes badge says Bonus (24 now means Tools)
m0=s.find('<article class="lesson" id="bonus-mistakes"'); m1=s.find('</header>',m0)
s=s[:m0]+s[m0:m1].replace('<small data-t="24">Bonus</small>','<small data-t="3201">Bonus</small>')+s[m1:]
# sidebar
old='<a href="#bonus-mistakes"><span class="n">★</span><span class="t" data-t="38">Common mistakes</span></a></div></details>'
assert old in s
s=s.replace(old,'</div></details>\n<h6 data-t="3201">Bonus</h6>\n<a href="#bonus-guests"><span class="n">★</span><span class="t" data-t="3296">'+G['3296'][0]+'</span></a>\n<a href="#bonus-mistakes"><span class="n">★</span><span class="t" data-t="38">Common mistakes</span></a>',1)
s=s.replace('<h6 data-t="24">Bonus</h6>','<h6 data-t="24">Tools</h6>',1)
s=_re2.sub(r'(data-t="24"[^>]*>)Bonus<',r'\1Tools<',s)
# cross-links
for after in ['<p data-t="1278">','<p data-t="97">']:
    i=s.find(after); assert i>0, after; j=s.find('</p>',i)+4
    s=s[:j]+'<p class="xref" data-t="3290">'+G['3290'][0]+'</p>'+s[j:]
i=s.find('<span data-t="2449">Taking it personally</span>'); j=s.find('</p>',i)+4
s=s[:j]+'<a data-t="3291" href="#bonus-guests">'+G['3291'][0]+'</a>'+s[j:]
# translations
k0=s.find('var I18N=')+len('var I18N='); d,end=json.JSONDecoder().raw_decode(s[k0:])
for i,v in G.items():
    for L,x in zip(('nl','es','pt'),v[1:]): d[L]['u'][i]=x
for L,x in zip(('nl','es','pt'),G['3202'][1:]): d[L]['u']['24']=x
s=s[:k0]+json.dumps(d,ensure_ascii=False).replace('</','<\\/')+s[k0+end:]
css="""
/* bonus: difficult guests */
.gx{background:var(--paper);border:1.5px solid var(--ink);border-radius:16px;margin:12px 0}
details.gx{padding:0}details.gx>summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:1fr auto;align-items:center;column-gap:14px;padding:16px 20px}details.gx>summary::-webkit-details-marker{display:none}.gx-k{grid-column:1;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#A05F50}.gx-h h4{grid-column:1;margin:2px 0 0}.gx-chev{grid-column:2;grid-row:1/span 2;width:30px;height:30px;border-radius:99px;border:1.5px solid var(--ink);position:relative}.gx-chev::after{content:'';position:absolute;left:10px;top:8px;width:7px;height:7px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg);transition:transform .2s}details.gx[open] .gx-chev::after{transform:rotate(-135deg);top:12px}.gx-body{padding:0 20px 18px}p.gx-link{margin:10px 0 0;font-size:14px}p.gx-link a{color:#A05F50;font-weight:700}
.chat{display:flex;flex-direction:column;gap:8px}
.chat .msg{max-width:78%;padding:9px 14px 10px;border-radius:16px;font-size:15px;line-height:1.45}
.chat .msg small{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.6;margin-bottom:2px}
.chat .msg p{margin:0}
.chat .msg.g{align-self:flex-start;background:var(--stone);border-bottom-left-radius:4px}
.chat .msg.h{align-self:flex-end;background:#313A33;background-image:var(--grad-g);color:#F4F2EF;border-bottom-right-radius:4px}
.gx-why{margin:12px 0 0;font-size:14px;color:var(--ink-soft,#4A4541)}.gx-why b{color:#A05F50}
.gx-line{background:#313A33;background-image:var(--grad-g);color:#F4F2EF;border-radius:16px;padding:26px 30px 28px;margin:18px 0}
.gx-line p{margin:16px 0 0;max-width:62ch;font:italic 400 21px/1.35 var(--serif,'Instrument Serif'),Georgia,serif}
.gx-line .vk-tag{background:rgba(244,242,239,.14);color:#F4F2EF}
a.gx-ext{display:inline-block;margin-top:6px;font-size:13px;font-weight:700;color:#A05F50}
p.xref{font-size:14px;background:rgba(160,95,80,.08);border-left:3px solid #A05F50;border-radius:0 10px 10px 0;padding:8px 12px}
p.xref a{color:#A05F50;font-weight:700}
@media (max-width:640px){.chat .msg{max-width:92%}}
.copy+.checklist{margin-top:22px}
.vk-g3 .vk-card>.vk-n{margin-bottom:10px}
/* all numbered markers in the course: small terracotta rounded square, white number */
.vk-n{width:26px!important;height:26px!important;border-radius:8px!important;background:#A05F50!important;background-image:var(--grad-t)!important;color:#F4F2EF!important;font-size:13px!important}
.vk-step .vk-n{top:18px}
"""
s=s[:s.rfind('</style>')]+css+s[s.rfind('</style>'):]
open(P,'w').write(s); print('guests lesson ok')

# --- Difficult guests additions (real coliving case, escalation line, reviews) + bonus lesson "Big damage & AirCover" ---
import case as _c; importlib.reload(_c)
C=dict(_c.T); C.update(_o.O)
s=open(P).read()
def ct(i,tag='span',cls=''):
    c=' class="%s"'%cls if cls else ''
    return '<%s%s data-t="%s">%s</%s>'%(tag,c,i,C[i][0],tag)
def bubble(who,label,i): return '<div class="msg %s"><small data-t="%s">%s</small>%s</div>'%(who,label,(G.get(label) or C.get(label))[0],ct(i,'p'))
def cext(href,i): return '<a class="gx-ext" data-t="%s" href="%s" rel="noopener" target="_blank">%s ↗</a>'%(i,href,C[i][0])
def fig(src,cap,alt,w,h): return '<figure><img alt="%s" decoding="async" height="%d" loading="lazy" src="img/%s" width="%d"/><figcaption data-t="%s">%s</figcaption></figure>'%(alt,h,src,w,cap,C[cap][0])
# 1) escalation line, after "Keep your word"
esc=('<h3 data-t="3300">'+C['3300'][0]+'</h3>'+ct('3301','p')
 +'<div class="gx-line">'+gt('3235','span','vk-tag')+ct('3302','p')+'</div>'
 +'<div class="vk-tip">'+ct('3303')+'</div>\n')
a=s.find('<span class="gold-k" data-t="3237">'); a=s.find('</div>',a)+6
s=s[:a]+'\n'+esc+s[a:]
# 2) real case, after the example conversations (before "Airbnb's rules are on your side")
case=('<div class="case">'+'<h3 data-t="3304">'+C['3304'][0]+'</h3>'+ct('3305','p','case-sub')+ct('3306','p')
 +'<ol class="case-steps">'+''.join(ct(i,'li') for i in ['3307','3308','3309','3310','3311','3312'])+'</ol>'
 +ct('3313','h4')+'<div class="chat">'+bubble('h','3260','3314')+bubble('g','3318','3315')+bubble('h','3260','3316')+bubble('g','3319','3317')+'</div>'
 +'<div class="vk-card vk-yes case-learn">'+ct('3320','h4')+'<ul>'+''.join(ct(i,'li') for i in ['3321','3322','3323','3324','3325'])+'</ul></div>'
 +'</div>\n')
a=s.find('<h3 data-t="3262">'); s=s[:a]+case+s[a:]
# 3) reviews, before "Spot it before they book"
rev=('<h3 data-t="3327">'+C['3327'][0]+'</h3>'+ct('3328','p')
 +'<div class="vk-g3">'+gcard(gn(1)+ct('3329','h4')+ct('3330','p'))+gcard(gn(2)+ct('3331','h4')+ct('3332','p'))+gcard(gn(3)+ct('3333','h4')+ct('3334','p'),'vk-no')+'</div>'
 +cext('https://www.airbnb.com/help/article/3582','3335')+'\n')
a=s.find('<h3 data-t="3269">'); s=s[:a]+rev+s[a:]
# extra task
a=s.find('<input data-task="bg-t3"'); a=s.find('</label>',a)+8
s=s[:a]+'<label class="task"><input data-task="bg-t4" type="checkbox"/><span data-t="3336">%s</span></label>'%C['3336'][0]+s[a:]
# 4) damage lesson
st=lambda items:'<div class="vk-steps">'+''.join('<div class="vk-step%s">%s%s%s</div>'%(' vk-wide' if (j==len(items) and len(items)%2) else '',gn(j),ct(h,'h4'),ct(q,'p')) for j,(h,q) in enumerate(items,1))+'</div>'
FOOT2=s[s.find('<div class="foot">',s.find('<article class="lesson" id="bonus-guests"')):]
FOOT2=FOOT2[:FOOT2.find('</div>\n</article>')+6]
dmg=('<article class="lesson" id="bonus-damage">\n'
 '<header class="lhead"><div class="lh-main">'+ct('3400','span','eyebrow')+'<h1 data-t="3401">'+C['3401'][0]+'</h1>'+ct('3402','p','sub')+'</div>'
 '<div class="lh-side"><span aria-hidden="true" class="mbadge sym"><small data-t="3201">Bonus</small><b>★</b></span><button class="backlink" hidden="" type="button"><span aria-hidden="true">←</span> <span class="bl-t" data-t="119">Back</span></button></div>\n</header>\n'
 +ct('3403','p')+'\n'
 +'<h3 data-t="3404">'+C['3404'][0]+'</h3>'+st([('3405','3406'),('3407','3408'),('3409','3410'),('3411','3412'),('3413','3414')])+'\n'
 +'<h3 data-t="3415">'+C['3415'][0]+'</h3>'+ct('3416','p')+'<div class="vk-tip">'+ct('3417')+'</div>'+cext('https://www.airbnb.com/help/article/3215','3418')+'\n'
 +'<h3 data-t="3419">'+C['3419'][0]+'</h3>'+ct('3420','p')
 +'<div class="vk-two">'+gcard(ct('3421','h4')+'<ul>'+''.join(ct(i,'li') for i in ['3422','3423','3424'])+'</ul>','vk-yes')+gcard(ct('3425','h4')+'<ul>'+''.join(ct(i,'li') for i in ['3426','3427','3428'])+'</ul>','vk-no')+'</div>'
 +cext('https://www.airbnb.com/help/article/542','3445')
 +'<h4 data-t="3429">'+C['3429'][0]+'</h4>'+st([('3430','3431'),('3432','3433'),('3434','3435'),('3436','3437'),('3438','3439')])
 +'<div class="vk-tip">'+ct('3444')+'</div>\n'
 +'<h3 data-t="3440">'+C['3440'][0]+'</h3>'+ct('3441','p')
 +'<figure class="shot">'+'<img alt="Airbnb Resolution Center with reimbursement requests" decoding="async" height="768" loading="lazy" src="img/resolution-center.webp" width="1400"/><figcaption data-t="3442">'+C['3442'][0]+'</figcaption></figure>'
 +'<a class="btn" data-t="3443" href="https://www.airbnb.com/resolutions" rel="noopener" target="_blank">'+C['3443'][0]+'</a>\n'
 +'<div class="case">'+'<h3 data-t="3446">'+C['3446'][0]+'</h3>'+ct('3447','p','case-sub')+ct('3448','p')
 +'<div class="trio3 case-nums"><div><b>5</b><span data-t="3454">'+C['3454'][0]+'</span></div><div><b>4–5</b><span data-t="3455">'+C['3455'][0]+'</span></div><div><b>€2,500</b><span data-t="3456">'+C['3456'][0]+'</span></div><div><b>~95%</b><span data-t="3457">'+C['3457'][0]+'</span></div></div>'
 +'<div class="case-grid">'+fig('case-sewage-message.webp','3458','Guest message: the bathroom is full of sewage',800,788)+fig('case-sewage-bathroom.webp','3459','Flooded bathroom floor',900,1200)+fig('case-sewage-shower.webp','3460','Shower tray full of sewage water',900,1600)+'</div>'
 +ct('3449','h4')+'<ol class="case-steps">'+''.join(ct(i,'li') for i in ['3450','3451','3452','3453'])+'</ol>'
 +'<div class="case-grid">'+fig('case-sewage-van.webp','3461','Drain company van in Barcelona',900,1200)+fig('case-sewage-tech.webp','3462','Technician unblocking the pipe',900,1200)+fig('case-sewage-shower2.webp','3460','Shower after the water drained',900,1549)+'</div>'
 +'<figure class="shot">'+'<img alt="Email from Airbnb approving a reimbursement under Host damage protection" decoding="async" height="241" loading="lazy" src="img/case-sewage-airbnb.webp" width="1100"/><figcaption data-t="3463">'+C['3463'][0]+'</figcaption></figure>'
 +'</div>\n'
 +'<div class="checklist"><div class="label"><span data-t="322">Your tasks</span></div>'
 +''.join('<label class="task"><input data-task="bd-t%d" type="checkbox"/><span data-t="%s">%s</span></label>'%(j,i,C[i][0]) for j,i in enumerate(['3466','3467','3468','3469'],1))+'</div>\n'
 +'<div class="gold"><span class="gold-k" data-t="3464">'+C['3464'][0]+'</span><p data-t="3465">'+C['3465'][0]+'</p></div>\n'
 +'<div class="pn"><a data-t="3345" href="#bonus-guests">'+C['3345'][0]+'</a><a class="next" data-t="3346" href="#bonus-mistakes">'+C['3346'][0]+'</a></div>\n'
 +FOOT2+'\n</article>\n')
a=s.find('<article class="lesson" id="bonus-mistakes"'); s=s[:a]+dmg+s[a:]
# chain: guests -> damage -> mistakes
s=s.replace('<a class="next" data-t="3293" href="#bonus-mistakes">'+G['3293'][0]+'</a>','<a class="next" data-t="3340" href="#bonus-damage">'+C['3340'][0]+'</a>',1)
s=s.replace('<a data-t="3295" href="#bonus-guests">'+G['3295'][0]+'</a>','<a data-t="3341" href="#bonus-damage">'+C['3341'][0]+'</a>',1)
assert 'href="#bonus-damage"><small>Next' in s and 'data-t="3341"' in s
# sidebar
o='<a href="#bonus-guests"><span class="n">★</span><span class="t" data-t="3296">'+G['3296'][0]+'</span></a>'
assert o in s
s=s.replace(o,o+'\n<a href="#bonus-damage"><span class="n">★</span><span class="t" data-t="3342">'+C['3342'][0].replace('&','&amp;')+'</span></a>',1)
# cross-links
i=s.find('<p class="xref" data-t="3290">',s.find('<p data-t="1278">')); j=s.find('</p>',i)+4
s=s[:j]+'<p class="xref" data-t="3343">'+C['3343'][0]+'</p>'+s[j:]
i=s.find('<p data-t="2454">'); j=s.find('</p>',i)+4
s=s[:j]+'<a data-t="3344" href="#bonus-damage">'+C['3344'][0]+'</a>'+s[j:]
# every prompt / template box folds (except the ones already inside a dropdown)
o="if(!inLib&&AI.indexOf(t.getAttribute('data-t'))<0)return;"
assert o in s
s=s.replace(o,"if(!inLib&&c.closest('details'))return;")
i=s.find('<span data-t="1326">'); i=s.find('</div></div>',i)+12
_ta=_o.TA[0].replace('&','&amp;').replace('<','&lt;')
s=s[:i]+'<div class="copy"><header><span data-t="3360">%s</span><span><button class="btn-s ghost reset" data-t="1117" type="button">Reset</button><button class="btn-s cp" data-t="477" type="button">Copy</button></span></header><textarea aria-label="%s" data-edit="qr-disc-value" id="ed-qr-disc-value" rows="10">%s</textarea><div class="hint"><span data-t="1320">Quick reply. Edit the [brackets], then copy it into Airbnb › Quick replies.</span></div></div>'%(C['3360'][0],C['3360'][0],_ta)+s[i:]
# translations
k0=s.find('var I18N=')+len('var I18N='); d,end=json.JSONDecoder().raw_decode(s[k0:])
for L,x in zip(('nl','es','pt'),_o.TA[1:]): d[L]['ta']['qr-disc-value']=x
for i,v in C.items():
    for L,x in zip(('nl','es','pt'),v[1:]): d[L]['u'][i]=x
s=s[:k0]+json.dumps(d,ensure_ascii=False).replace('</','<\\/')+s[k0+end:]
css="""
/* real cases + damage lesson */
.case{background:var(--paper);border:1.5px solid var(--ink);border-radius:18px;padding:20px 22px;margin:22px 0}
.case>h3{margin-top:8px}.case .case-sub{margin:-4px 0 10px;color:#A05F50;font-weight:700;font-size:13px;letter-spacing:.06em;text-transform:uppercase}
.case-steps{counter-reset:cs;list-style:none;padding:0;margin:14px 0}
.case-steps li{counter-increment:cs;position:relative;padding:0 0 12px 38px;margin:0}
.case-steps li::before{content:counter(cs);position:absolute;left:0;top:1px;width:26px;height:26px;border-radius:8px;background:#A05F50;background-image:var(--grad-t);color:#F4F2EF;font:700 13px/26px var(--body,Arial),Arial,sans-serif;text-align:center}
.case .chat{margin:8px 0 16px}
.case-learn{margin-top:8px}
.case-nums{grid-template-columns:repeat(4,minmax(0,1fr))!important;margin:14px 0}
.case-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:14px 0}
.case-grid figure,figure.shot{margin:0}
.case-grid img{width:100%;height:240px;object-fit:cover;border-radius:12px;display:block;border:1px solid #DAD6D0}
figure.shot{margin:14px 0}figure.shot img{width:100%;max-width:none!important;height:auto;border-radius:12px;display:block;border:1px solid #DAD6D0;background:#fff}
.case-grid figcaption,figure.shot figcaption{font-size:13px;color:var(--ink-soft,#4A4541);margin-top:6px;line-height:1.4}
@media (max-width:760px){.case-grid{grid-template-columns:1fr 1fr}.case-nums{grid-template-columns:1fr 1fr!important}}
"""
s=s[:s.rfind('</style>')]+css+s[s.rfind('</style>'):]
open(P,'w').write(s); print('case + damage ok')
