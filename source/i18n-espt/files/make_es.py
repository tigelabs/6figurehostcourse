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
FT='<div class="ft">por Farah Cuyvers &amp; Daniel Martí</div>'
pages=[]
pages.append('<div class="pg cover"><div class="patch"><h1>GUIONES, PLANTILLAS DE EMAIL, PRESENTACIÓN EN PERSONA<br>&amp; CHULETA DE OBJECIONES</h1></div></div>')
pages.append('''<div class="pg"><div class="in"><h2>1. Email en frío a un propietario (primer contacto)</h2>
<p><b>Asunto:</b> Consulta rápida sobre su vivienda en alquiler</p>
<p>Estimado/a [nombre del propietario]:<br>He visto su anuncio de [dirección o descripción] y quería preguntarle si la vivienda sigue disponible. Busco una vivienda a largo plazo, pero no de la forma tradicional. Tengo una pequeña empresa de gestión de viviendas centrada en estancias de corta y media duración para huéspedes verificados, como teletrabajadores, nómadas digitales y viajeros de negocios.</p>
<p>Cuidamos la vivienda como si fuera nuestra: limpieza profesional, mantenimiento periódico y el alquiler siempre puntual. Me encantaría contarle más si está abierto a otro tipo de alquiler que le dé ingresos estables con menos complicaciones.</p>
<p>¿Tendría disponibilidad para una llamada breve o una reunión esta semana?</p>
<p>Muchas gracias,<br>[Tu nombre]<br>[Tus datos de contacto]</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>2. Esquema de presentación en persona (reunión con el propietario)</h2>
<p><b>Empieza creando confianza:</b> "Gracias de nuevo por dedicarme su tiempo. De verdad que lo valoro. Me gustaría enseñarle un tipo de acuerdo de alquiler diferente que puede funcionar muy bien para los dos."</p>
<p><b>Plantea la oferta:</b> "Tengo un pequeño negocio de hospitalidad. Alquilo viviendas y alojo a profesionales en estancias de corta y media duración: viajeros de negocios, nómadas digitales y consultores. Son huéspedes tranquilos y respetuosos que tratan la vivienda como un hotel."</p>
<p><b>Adelántate a las objeciones:</b> "Pagamos el alquiler como un reloj, limpiamos la vivienda de forma profesional después de cada estancia y nos encargamos del mantenimiento. Sin retrasos en los pagos, sin riesgo de daños permanentes y sin tener que perseguir a ningún inquilino. Puedo enseñarle cómo está todo organizado: tenemos calendarios de limpieza, plantillas de comunicación y total transparencia."</p>
<p><b>Responde a la preocupación por los vecinos:</b> "Nos tomamos muy en serio el impacto en la comunidad. Nada de fiestas ni de huéspedes ruidosos. Tenemos normas de la casa estrictas y verificamos a cada huésped. Mi objetivo es ser el inquilino más fácil con el que haya trabajado nunca."</p>
<p><b>Cierra con seguridad:</b> "Si le parece bien, le envío una propuesta con cómo quedaría todo, en números y en la práctica. Creo de verdad que esto puede ser beneficioso para los dos."</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>3. Email de seguimiento tras una conversación</h2>
<p><b>Asunto:</b> Seguimiento de la propuesta de alquiler</p>
<p>Estimado/a [nombre del propietario]:</p>
<p>Gracias de nuevo por dedicarme su tiempo. Sé que este enfoque es distinto de un alquiler tradicional de larga duración, así que me gustaría resumirle las principales ventajas, sobre todo comparadas con los riesgos habituales a los que se enfrentan los propietarios.</p>
<p>Con un alquiler tradicional es habitual que:</p>
<ul><li>Los inquilinos no paguen a tiempo o dejen de pagar</li><li>La vivienda quede en mal estado cuando se van</li><li>Sea difícil acceder a la vivienda para inspecciones o mantenimiento</li><li>Surjan conflictos por daños, la fianza o quién se encarga del mantenimiento</li></ul>
<p>Lo que ofrecemos es un acuerdo profesional y sin preocupaciones que protege su vivienda y le da tranquilidad:</p>
<p><b>Alquiler mensual:</b> [importe], garantizado y puntual, todos los meses<br><b>Huéspedes:</b> profesionales verificados (teletrabajadores, nómadas digitales, viajeros responsables)<br><b>Limpieza:</b> limpieza profesional después de cada estancia, con mucha más frecuencia que con un alquiler normal<br><b>Mantenimiento:</b> inspecciones y mantenimiento periódicos a cargo de nuestro equipo, sin coste para usted</p>
<p>Le adjunto un ejemplo de nuestra guía para huéspedes, nuestra checklist de limpieza y nuestras normas de la casa, para que vea exactamente cómo trabajamos y cuidamos la vivienda.</p>
<p>Si tiene cualquier pregunta o quiere hablarlo con más calma, dígamelo. Estaré encantado de ajustar la propuesta o aclararle cualquier detalle.</p>
<p>Quedo a la espera de su opinión,<br>[Tu nombre]</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>Chuleta de objeciones</h2>
<h3>“No quiero desconocidos en mi vivienda.”</h3><p>Es totalmente comprensible. Todos nuestros huéspedes están verificados a través de Airbnb. No son gente de fiesta: a menudo son profesionales que vienen por trabajo o para estancias largas. Además, tenemos normas de la casa estrictas y ofrecemos asistencia inmediata si surge algo.</p>
<h3>“¿Y si la vivienda sufre daños?”</h3><p>Airbnb ofrece protección y un seguro para anfitriones, pero además hacemos inspecciones y limpiezas profesionales entre estancias. Mantener la vivienda en perfecto estado nos interesa a nosotros mismos.</p>
<h3>“Prefiero un inquilino de larga duración.”</h3><p>Le ofrecemos los mismos ingresos estables, pero con más cuidado de la vivienda. Nuestro alquiler llega puntual y está garantizado. Y si algún día quiere volver a un inquilino tradicional, nos encargamos de la transición.</p>
<h3>“¿No molestará esto a los vecinos?”</h3><p>Verificamos con cuidado a todos los huéspedes y hacemos cumplir los horarios de silencio y un comportamiento respetuoso. También tenemos un contacto local para emergencias y una línea directa de comunicación.</p></div>'''+FT+'</div>')
open('scripts_es.html','w').write('<!doctype html><html lang="es"><meta charset="utf-8"><style>'+css+'</style><body>'+''.join(pages)+'</body></html>')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page();pg.goto('file:///home/claude/nlfiles/scripts/scripts_es.html');pg.wait_for_timeout(800)
    pg.pdf(path='/home/claude/nlfiles/final_es/guiones-propietarios.pdf',format='A4',print_background=True)
    b.close()
