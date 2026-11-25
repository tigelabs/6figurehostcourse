F='file:///home/claude/mock/node_modules/@fontsource/'
css=f'''@font-face{{font-family:Anton;src:url({F}anton/files/anton-latin-400-normal.woff2)}}
@font-face{{font-family:Arimo;font-weight:400;src:url({F}arimo/files/arimo-latin-400-normal.woff2)}}
@font-face{{font-family:Arimo;font-weight:700;src:url({F}arimo/files/arimo-latin-700-normal.woff2)}}
@font-face{{font-family:Arimo;font-style:italic;src:url({F}arimo/files/arimo-latin-400-italic.woff2)}}
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0}}
.pg{{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background:#E1DED9;font-family:Arimo,Arial,sans-serif;color:#1d1d1f}}
.cover{{background:url(cover-1.png) center/100% 100% no-repeat}}
.cover .patch{{position:absolute;left:{200/1655*100}%;width:{(1452-200)/1655*100}%;top:{1125/2340*100}%;height:{(1500-1125)/2340*100}%;background:rgb(241,238,233);display:flex;align-items:flex-start;justify-content:center;text-align:center}}
.cover .patch h1{{font-family:Anton;font-weight:400;font-size:17pt;line-height:1.45;margin:3mm 6mm 0;letter-spacing:.01em}}
.in{{position:absolute;left:{356/1655*210}mm;right:{(1655-1560)/1655*210}mm;top:20mm}}
h2{{font-family:Anton;font-weight:400;font-size:20pt;line-height:1.55;margin:0 0 6mm;text-transform:uppercase}}
p{{font-size:9.6pt;line-height:1.45;margin:0 0 4mm}}
ul{{margin:0 0 4mm;padding-left:6mm;font-size:9.6pt;line-height:1.45}}
.ft{{position:absolute;left:{356/1655*210}mm;right:{(1655-1560)/1655*210}mm;top:{2243/2340*297}mm;border-top:1px solid #2b2c30;padding-top:2mm;text-align:right;font-style:italic;font-size:8.5pt}}
h3{{font-family:Arimo;font-weight:700;font-size:10pt;margin:6mm 0 2mm}}'''
FT='<div class="ft">door Farah Cuyvers &amp; Daniel Martí</div>'
pages=[]
pages.append('<div class="pg cover"><div class="patch"><h1>SCRIPTS, E-MAILTEMPLATES, PERSOONLIJKE PITCH<br>&amp; SPIEKBRIEFJE VOOR BEZWAREN</h1></div></div>')
pages.append('''<div class="pg"><div class="in"><h2>1. Koude e-mail aan een verhuurder (eerste contact)</h2>
<p><b>Onderwerp:</b> Korte vraag over uw huurwoning</p>
<p>Beste [naam verhuurder],<br>Ik zag uw advertentie voor [adres of omschrijving] en wilde vragen of de woning nog beschikbaar is. Ik zoek een woning voor de lange termijn, maar niet op de traditionele manier. Ik heb een klein bedrijf in woningbeheer, gericht op verblijven van korte tot middellange duur voor gescreende gasten, zoals remote workers, digital nomads en zakenreizigers.</p>
<p>We zorgen voor de woning alsof het onze eigen woning is: professionele schoonmaak, regelmatig onderhoud en de huur altijd op tijd. Ik vertel u er graag meer over als u openstaat voor een andere verhuurvorm die stabiele inkomsten oplevert met minder gedoe.</p>
<p>Staat u open voor een kort telefoongesprek of een afspraak deze week?</p>
<p>Hartelijk dank,<br>[Je naam]<br>[Je contactgegevens]</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>2. Opzet voor een persoonlijke pitch (afspraak met de verhuurder)</h2>
<p><b>Begin met een klik maken:</b> "Nogmaals bedankt dat u de tijd neemt om af te spreken. Dat waardeer ik echt. Ik wil u graag een ander soort huurovereenkomst laten zien die voor ons allebei goed kan werken."</p>
<p><b>Breng het aanbod:</b> "Ik heb een klein bedrijf in de gastvrijheid. Ik huur woningen en ontvang professionals voor verblijven van korte tot middellange duur, denk aan zakenreizigers, digital nomads en consultants. Het zijn rustige, respectvolle gasten die de woning behandelen als een hotel."</p>
<p><b>Neem bezwaren weg voordat ze komen:</b> "We betalen de huur als een klok, maken de woning na elk verblijf professioneel schoon en regelen het onderhoud. Geen late betalingen, geen risico op blijvende schade en u hoeft nooit achter huurders aan. Ik kan u laten zien hoe alles georganiseerd is: we hebben schoonmaakschema’s, communicatietemplates en volledige transparantie."</p>
<p><b>Ga in op zorgen over de buren:</b> "We nemen de impact op de omgeving serieus. Geen feestjes, geen luidruchtige gasten. We hebben strenge huisregels en screenen elke gast. Mijn doel is de makkelijkste huurder te zijn met wie u ooit hebt gewerkt."</p>
<p><b>Sluit vol vertrouwen af:</b> "Als u ervoor openstaat, stuur ik u graag een voorstel met hoe het er financieel en praktisch uit zou zien. Ik geloof echt dat dit voor ons allebei een winst kan zijn."</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>3. Opvolgmail na een gesprek</h2>
<p><b>Onderwerp:</b> Opvolging van het huurvoorstel</p>
<p>Beste [naam verhuurder],</p>
<p>Nogmaals bedankt dat u de tijd nam voor ons gesprek. Ik weet dat deze aanpak anders is dan een gewone verhuur voor de lange termijn, maar ik zet de belangrijkste voordelen voor u graag op een rij, vooral vergeleken met de gebruikelijke risico’s voor verhuurders.</p>
<p>Bij een gewone verhuur komt het vaak voor dat:</p>
<ul><li>Huurders de huur niet op tijd betalen of helemaal stoppen met betalen</li><li>Woningen na vertrek in slechte staat worden achtergelaten</li><li>Het lastig is om de woning in te komen voor inspecties of onderhoud</li><li>Er discussies ontstaan over schade, de borg of wie verantwoordelijk is voor onderhoud</li></ul>
<p>Wat wij bieden, is een zorgeloze, professionele constructie die uw woning beschermt en u gemoedsrust geeft:</p>
<p><b>Maandhuur:</b> [bedrag invullen], gegarandeerd en op tijd, elke maand<br><b>Gasten:</b> geverifieerde professionals (remote workers, digital nomads, verantwoordelijke reizigers)<br><b>Schoonmaak:</b> professioneel schoongemaakt na elk verblijf, veel vaker dan bij een gewone huur<br><b>Onderhoud:</b> regelmatig geïnspecteerd en onderhouden door ons team, zonder kosten voor u</p>
<p>Ik voeg een voorbeeld van onze gastengids, schoonmaakchecklist en huisregels toe, zodat u precies kunt zien hoe we werken en voor de woning zorgen.</p>
<p>Laat het me gerust weten als u vragen heeft of het verder wilt bespreken. Ik pas het voorstel graag aan of licht details toe.</p>
<p>Ik hoor graag wat u ervan vindt,<br>[Je naam]</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>Spiekbriefje voor bezwaren</h2>
<h3>“Ik wil geen willekeurige mensen in mijn woning.”</h3><p>Heel begrijpelijk. Al onze gasten worden gescreend en geverifieerd via Airbnb. Het zijn geen feestgangers: vaak zijn het professionals die voor hun werk of een langer bezoek komen. We hebben ook strenge huisregels en bieden direct ondersteuning als er iets is.</p>
<h3>“Wat als de woning beschadigd raakt?”</h3><p>Airbnb biedt bescherming en een verzekering voor hosts, maar we doen ook inspecties en professionele schoonmaak tussen de verblijven. Het is in ons eigen belang om de woning in perfecte staat te houden.</p>
<h3>“Ik heb liever een huurder voor de lange termijn.”</h3><p>We bieden dezelfde stabiele inkomsten, maar met meer zorg voor de woning. Onze huur is op tijd en gegarandeerd. En als u ooit terug wilt naar een gewone huurder, regelen wij de overgang.</p>
<h3>“Gaat dit de buren niet storen?”</h3><p>We screenen alle gasten zorgvuldig en zien toe op rusttijden en respectvol gedrag. We hebben ook een lokaal contactpersoon voor noodgevallen en een directe lijn voor communicatie.</p></div>'''+FT+'</div>')
open('scripts_nl.html','w').write('<!doctype html><html lang="nl"><meta charset="utf-8"><style>'+css+'</style><body>'+''.join(pages)+'</body></html>')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page();pg.goto('file:///home/claude/nlfiles/scripts/scripts_nl.html');pg.wait_for_timeout(800)
    pg.pdf(path='/home/claude/nlfiles/final/scripts-verhuurders.pdf',format='A4',print_background=True)
    b.close()
