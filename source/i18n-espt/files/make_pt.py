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
pages.append('<div class="pg cover"><div class="patch"><h1>ROTEIROS, MODELOS DE E-MAIL, APRESENTAÇÃO PESSOAL<br>&amp; COLA DE OBJEÇÕES</h1></div></div>')
pages.append('''<div class="pg"><div class="in"><h2>1. E-mail frio para um proprietário (primeiro contato)</h2>
<p><b>Assunto:</b> Pergunta rápida sobre seu imóvel para alugar</p>
<p>Prezado(a) [nome do proprietário],<br>Vi seu anúncio de [endereço ou descrição] e queria saber se o imóvel ainda está disponível. Estou procurando um imóvel de longo prazo, mas não do jeito tradicional. Tenho uma pequena empresa de gestão de imóveis focada em estadias de curta e média duração para hóspedes verificados, como profissionais remotos, nômades digitais e viajantes a negócios.</p>
<p>Cuidamos do imóvel como se fosse nosso: limpeza profissional, manutenção regular e o aluguel sempre em dia. Adoraria contar mais se o senhor/a senhora estiver aberto(a) a outro formato de aluguel, que gera renda estável com menos dor de cabeça.</p>
<p>Teria disponibilidade para uma ligação rápida ou uma reunião esta semana?</p>
<p>Muito obrigado,<br>[Seu nome]<br>[Seu contato]</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>2. Estrutura de apresentação pessoal (reunião com o proprietário)</h2>
<p><b>Comece criando conexão:</b> "Obrigado mais uma vez por tirar um tempo para conversar. Valorizo muito isso. Quero te mostrar um formato de aluguel diferente, que pode funcionar muito bem para nós dois."</p>
<p><b>Apresente a proposta:</b> "Tenho um pequeno negócio de hospitalidade. Alugo imóveis e recebo profissionais em estadias de curta e média duração: viajantes a negócios, nômades digitais e consultores. São hóspedes tranquilos e respeitosos, que tratam o imóvel como um hotel."</p>
<p><b>Antecipe as objeções:</b> "Pagamos o aluguel sempre em dia, fazemos limpeza profissional depois de cada estadia e cuidamos da manutenção. Sem atrasos, sem risco de danos permanentes e sem precisar correr atrás de inquilino. Posso te mostrar como tudo é organizado: temos cronogramas de limpeza, modelos de comunicação e total transparência."</p>
<p><b>Responda à preocupação com os vizinhos:</b> "Levamos muito a sério o impacto no prédio e na vizinhança. Nada de festas nem hóspedes barulhentos. Temos regras da casa rígidas e verificamos cada hóspede. Meu objetivo é ser o inquilino mais fácil com quem você já trabalhou."</p>
<p><b>Feche com confiança:</b> "Se você topar, te mando uma proposta mostrando como tudo ficaria, nos números e na prática. Acredito de verdade que isso pode ser bom para nós dois."</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>3. E-mail de acompanhamento depois de uma conversa</h2>
<p><b>Assunto:</b> Sobre a proposta de aluguel</p>
<p>Prezado(a) [nome do proprietário],</p>
<p>Obrigado mais uma vez pela conversa. Sei que essa proposta é diferente de um aluguel tradicional de longo prazo, então quero resumir os principais benefícios, principalmente em comparação com os riscos comuns que os proprietários enfrentam.</p>
<p>Num aluguel tradicional, é comum que:</p>
<ul><li>Os inquilinos atrasem o aluguel ou parem de pagar</li><li>O imóvel fique em mau estado na mudança</li><li>Seja difícil entrar no imóvel para inspeções ou manutenção</li><li>Surjam discussões sobre danos, caução ou quem é responsável pela manutenção</li></ul>
<p>O que oferecemos é um formato profissional e sem preocupação, que protege seu imóvel e te dá tranquilidade:</p>
<p><b>Aluguel mensal:</b> [valor], garantido e em dia, todo mês<br><b>Hóspedes:</b> profissionais verificados (profissionais remotos, nômades digitais, viajantes responsáveis)<br><b>Limpeza:</b> limpeza profissional depois de cada estadia, com muito mais frequência do que num aluguel comum<br><b>Manutenção:</b> inspeções e manutenção regulares feitas pelo nosso time, sem custo para você</p>
<p>Envio em anexo um exemplo do nosso guia para hóspedes, do checklist de limpeza e das regras da casa, para você ver exatamente como trabalhamos e cuidamos do imóvel.</p>
<p>Qualquer dúvida, ou se quiser conversar com mais calma, é só me falar. Fico feliz em ajustar a proposta ou explicar qualquer detalhe.</p>
<p>Aguardo seu retorno,<br>[Seu nome]</p></div>'''+FT+'</div>')
pages.append('''<div class="pg"><div class="in"><h2>Cola de objeções</h2>
<h3>“Não quero gente desconhecida no meu imóvel.”</h3><p>Totalmente compreensível. Todos os nossos hóspedes são verificados pelo Airbnb. Não são pessoas querendo festa: muitas vezes são profissionais que vêm a trabalho ou para estadias mais longas. Também temos regras da casa rígidas e damos suporte imediato se acontecer alguma coisa.</p>
<h3>“E se o imóvel for danificado?”</h3><p>O Airbnb oferece proteção e seguro para anfitriões, mas também fazemos inspeções e limpeza profissional entre as estadias. Manter o imóvel em perfeito estado é do nosso próprio interesse.</p>
<h3>“Prefiro um inquilino de longo prazo.”</h3><p>Oferecemos a mesma renda estável, mas com mais cuidado com o imóvel. Nosso aluguel é em dia e garantido. E se um dia você quiser voltar para um inquilino tradicional, nós cuidamos da transição.</p>
<h3>“Isso não vai incomodar os vizinhos?”</h3><p>Verificamos todos os hóspedes com cuidado e fazemos cumprir os horários de silêncio e um comportamento respeitoso. Também temos um contato local para emergências e um canal direto de comunicação.</p></div>'''+FT+'</div>')
open('scripts_pt.html','w').write('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>'+css+'</style><body>'+''.join(pages)+'</body></html>')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page();pg.goto('file:///home/claude/nlfiles/scripts/scripts_pt.html');pg.wait_for_timeout(800)
    pg.pdf(path='/home/claude/nlfiles/final_pt/roteiros-proprietarios.pdf',format='A4',print_background=True)
    b.close()
