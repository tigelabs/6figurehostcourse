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
