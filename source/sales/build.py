"""Builds the public sales pages and the home page into the site's public/ folder.

  python3 source/sales/build.py   (edit the texts in this file, then run it)

Pages: /  /course/  /course/start/  /course/owner/  /course/nomad/  /barcelona/  /bali/  /calculator/
The course pages come from base_body.html (the landing page designed in Claude Design).
"""
import os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'public')
BASE = open(os.path.join(HERE, 'base_body.html'), encoding='utf-8').read()
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Arimo:ital,wght@0,400;0,700;1,400&amp;family=Libre+Baskerville:ital,wght@0,400;1,400&amp;family=Pinyon+Script&amp;display=swap" rel="stylesheet">'

NAV = '''<nav class="nav" aria-label="Main">
<div class="in">
<a class="logo" href="/" aria-label="6 Figure Host home"><span class="sc">6 Figure</span><span class="dp">Host</span></a>
<ul>
<li><a href="/#start">Start here</a></li>
<li><a href="/#story">Our story</a></li>
<li><a href="/course/"{c}>Online course</a></li>
<li class="dd"><details><summary>Add-ons</summary>
<ul class="dd-menu">
<li><a href="/barcelona/"{b}>Barcelona guide</a></li>
<li><a href="/bali/"{i}>Bali guide</a></li>
<li><a href="/calculator/"{k}>Profit Calculator</a></li>
</ul></details></li>
</ul>
<script>document.addEventListener('click',function(e){{var d=document.querySelector('.nav .dd details');if(d&&d.open&&!d.contains(e.target))d.open=false}});document.addEventListener('keydown',function(e){{var d=document.querySelector('.nav .dd details');if(e.key==='Escape'&&d&&d.open){{d.open=false;d.querySelector('summary').focus()}}}});</script>
<a class="login" href="/hostcourse/login">Access your course</a>
</div>
</nav>'''

FOOT = '''<footer class="foot">
<div class="in">
<span>© 2026 Farah &amp; Daniel · Passion to profit LLC. All rights reserved.</span>
<span class="flinks"><a href="/course/">Course</a><a href="/barcelona/">Barcelona guide</a><a href="/bali/">Bali guide</a><a href="/calculator/">Profit Calculator</a><a href="/privacy">Privacy policy</a><a href="mailto:contact@6figurehost.com">contact@6figurehost.com</a><a href="https://www.instagram.com/6figurehost/" target="_blank" rel="noopener">Instagram @6figurehost</a></span>
</div>
</footer>'''


def page(path, title, desc, body, active=''):
    nav = NAV.format(c=' aria-current="page"' if active == 'course' else '', b=' aria-current="page"' if active == 'barcelona' else '',
                     i=' aria-current="page"' if active == 'bali' else '', k=' aria-current="page"' if active == 'calculator' else '')
    if path.strip('/'):
        nav = ''  # landing pages: no menu, so nothing pulls visitors away from the offer
    doc = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="https://6figurehost.com/assets/course-mockup.webp">
%s
<link rel="stylesheet" href="/assets/sales.css?v=20261123d">
<script src="/assets/offer.js?v=5" defer></script>
</head>
<body>
<div class="pg">
%s
%s
%s
</div>
</body>
</html>
''' % (html.escape(title), html.escape(desc), html.escape(title), html.escape(desc), FONTS, nav, body, FOOT)
    d = os.path.join(OUT, path.strip('/'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
    return len(doc)


def sub(s, old, new, count=1):
    assert old in s, 'not found: ' + old[:80]
    return s.replace(old, new, count)


# ---------------------------------------------------------------- course pages
OFFERBAR_HTML = """<div class="bar obar">
<div class="in">
<p data-o="bar"><b>Black Friday</b> opens 27 November: the course for $197 instead of $297.</p>
<span class="cd sm" data-o="countdown"></span>
<a href="#pricing">See the offer</a>
</div>
</div>
"""
VALUE_STACK = """<div class="buy vstack">
<p class="vs-h">What it’s worth</p>
<ul class="vs">
<li><span>6-Figure Host Course, 13 lessons</span><b data-o="vs" data-v="297">$297</b></li>
<li><span>Profit &amp; ROI Calculator</span><b data-o="vs" data-v="97">$97</b></li>
<li><span>Host starter kit: contracts, checklists, templates</span><b data-o="vs" data-v="150">$150</b></li>
<li><span>Landlord scripts, pitch brochure and AI prompts</span><b>included</b></li>
</ul>
<p class="vs-tot"><span>Total value</span><b data-o="vs" data-v="544">$544</b></p>
<p class="vs-you">Your price: <b data-o="price">$297</b></p>
<a class="cta" href="#pricing">Choose how you pay</a>
</div>"""
PRICING = """<div class="pricing" id="pricing">
<p class="pr-head" data-o="headline">Black Friday opens 27 November</p>
<div class="cd" data-o="countdown"></div>
<div class="curt"><span>Choose your currency</span><div class="cur" data-o="cur" role="radiogroup" aria-label="Currency"><button type="button" role="radio" data-cur="eur">€ EUR</button><button type="button" role="radio" data-cur="usd">$ USD</button></div></div>
<div class="pr-cards">
<div class="pr-card best"><span class="pr-badge">Best value</span>
<h3>One-time payment</h3>
<p class="pr-was" data-o="was1"></p>
<p class="pr-now" data-o="now1">$297</p>
<p class="pr-sub">The lowest total price.</p>
<p class="pr-save" data-o="save">Lifetime access, no subscription</p>
<ul class="ticks"><li><span>Lifetime access to the course</span></li><li><span>Profit Calculator + host starter kit included (value <span data-o="vs" data-v="247">$247</span>)</span></li><li><span>All future updates</span></li></ul>
<a class="cta" href="/checkout" data-buy="One-time payment">One-time payment</a>
</div>
<div class="pr-card">
<h3>Split pay</h3>
<p class="pr-was" data-o="was2"></p>
<p class="pr-now" data-o="now2">4 × $79</p>
<p class="pr-sub" data-o="tot2">$316 total, paid monthly</p>
<p class="pr-save pr-save2" data-o="split-note">Start today, pay in 4 months</p>
<ul class="ticks"><li><span>Lifetime access to the course</span></li><li><span>Profit Calculator + host starter kit included (value <span data-o="vs" data-v="247">$247</span>)</span></li><li><span>All future updates</span></li></ul>
<a class="cta ghost" href="/checkout?plan=split" data-buy="Split pay">Split pay</a>
</div>
</div>
<p class="pr-note">Secure payment by Stripe. Digital product, no refunds after purchase.</p>
<p class="pr-old"><b>Bought our guide before?</b> You get the new course for free. <a href="/hostcourse/login">Log in with your access code</a>, or write to <a href="mailto:contact@6figurehost.com">contact@6figurehost.com</a> if you can’t find it.</p>
</div>"""
OLD_BUYERS_FAQ = '<details><summary>I bought your guide before. Do I have to pay again?</summary><p>No. Everyone who bought our guide gets the new course for free. Log in with the access code you already have, or write to <a href="mailto:contact@6figurehost.com">contact@6figurehost.com</a> and we’ll send it to you.</p></details>\n'
def course_base():
    s = BASE
    s = re.sub(r'<div class="bar">.*?</div>\n</div>\n', lambda m: OFFERBAR_HTML, s, count=1, flags=re.S)
    s = sub(s, '<span class="pill">Now an interactive guide + host starter kit</span>', '<span class="pill">Interactive course + host starter kit</span>')
    s = sub(s, '<span class="dp">Host Guide</span>', '<span class="dp">Host Course</span>')
    s = sub(s, '<p class="lead">The step-by-step system to build a profitable, legal rental business, even without owning property.</p>', '<p class="lead">The step-by-step system to build a profitable, legal rental business (with or without owning property).</p>')
    s = s.replace('href="#offer"', 'href="/checkout"')
    s = s.replace('Get instant access for $149', '<span data-o="cta">Get instant access for $297</span>')
    s = re.sub(r'<div class="buy">.*?</div>\n</div>\n</div>', lambda m: VALUE_STACK + '\n</div>\n' + PRICING + '\n</div>', s, count=1, flags=re.S)
    s = s.replace('<details open><summary>When do I get access?</summary>', OLD_BUYERS_FAQ + '<details open><summary>When do I get access?</summary>', 1)
    s = re.sub(r'<img class="photo" src="/assets/sales/c9292e2a0b9965c2ce6ed45ed6d0dd7b.webp"[^>]*>\n', '', s, count=1)
    s = s.replace('<div class="stage">', '<div class="stage mk">', 1)
    s = s.replace('<div class="base"></div>\n</div>\n</div>\n</div>\n</header>', '<div class="base"></div>\n</div>\n<figure class="tabk"><div class="ipad"><img src="/assets/sales/kit-ipad.webp" width="1024" height="768" alt="The host starter kit inside the course on an iPad: launch roadmap, must-have tools, decision-making matrix and the profit calculator"></div></figure>\n</div>\n</div>\n</header>', 1)
    s = sub(s, '<video src="/assets/sales/0c82ae4341b1f2fc221c4fe50e96a4f3.mp4" poster="/assets/sales/52df027710a89acb2f932c71a4329f54.webp"', '<video src="/assets/sales/course-tour.mp4" poster="/assets/sales/course-tour.webp"')
    s = sub(s, 'aria-label="A scroll through the guide: the start page, a chapter, the launch roadmap, the setup checklist and the profit calculator"', 'aria-label="A scroll through the course: the start page, a lesson, the launch roadmap, the profit calculator and the host starter kit"')
    # the welcome video is not recorded yet: show Farah and Daniel instead of a placeholder
    s = re.sub(r'<div class="video">.*?</div>\n', '<img src="/assets/sales/us.webp" alt="Farah and Daniel together" style="width:100%;aspect-ratio:4/5;object-fit:cover">\n', s, count=1, flags=re.S)
    s = sub(s, 'This guide is built from that kind of knowledge.', 'This course is built from that kind of knowledge.')
    s = sub(s, '<span class="sc b">Not an ebook</span><span class="dp">A guide you work inside</span>', '<span class="sc b">Not an ebook</span><span class="dp">A course you work inside</span>')
    s = s.replace('inside the guide', 'inside the course').replace('Inside the guide', 'Inside the course')
    s = sub(s, '<h3 class="dp3">The interactive 6Figure Host Guide</h3>', '<h3 class="dp3">The interactive 6-Figure Host Course</h3>')
    s = sub(s, '<li><span>Profit and ROI calculators for arbitrage, ownership and leasehold</span></li>\n</ul></div>',
            '<li><span>Profit and ROI calculators for arbitrage, ownership and leasehold</span></li>\n</ul></div>\n<div><h3 class="dp3">Coming soon</h3>\n<ul class="ticks">\n<li><span>Barcelona and Bali Host Guides, to add to your course</span></li>\n</ul></div>')
    s = re.sub(r'<details><summary>Can I get an invoice\?</summary>.*?</details>\n', '', s, count=1, flags=re.S)
    s = re.sub(r'<details><summary>Do you offer refunds\?</summary>.*?</details>', '<details><summary>Do you offer refunds?</summary><p>As this is a digital product, no refunds can be given after purchase. By making a purchase you accept this.</p><p>An exception can be made when you accidentally purchase it twice with the same email address. Write to <a href="mailto:contact@6figurehost.com">contact@6figurehost.com</a> and tell us which email you used.</p></details>', s, count=1, flags=re.S)
    s = sub(s, '<details open><summary>When do I get access?</summary><p>Right after checkout. You can start the first lesson the same minute.</p></details>',
            '<details open><summary>When do I get access?</summary><p>Right after checkout. You see your personal access code on the screen, you are logged in, and we email you the code too. You can start the first lesson the same minute, on up to 5 devices.</p></details>')
    s = re.sub(r'<footer class="foot">.*?</footer>\n?', '', s, count=1, flags=re.S)
    return s


VARIANTS = {
    'course': dict(
        title='6-Figure Host Course · Build a profitable rental business', desc='The step-by-step course by Farah & Daniel to build a profitable, legal rental business, even without owning property.'),
    'course/start': dict(
        title='Start a rental business without owning property · 6-Figure Host Course',
        desc='Rental arbitrage and co-hosting, step by step: start a profitable rental business without buying property, even on a small budget.',
        pill='For beginners · no property needed',
        lead='Start a profitable rental business <b>without buying property</b>, with rental arbitrage or co-hosting, even on a small budget.',
        ticks=['<b>Pick the model that fits your budget.</b> Co-hosting needs almost no money; rental arbitrage needs a deposit, the first rent and furniture.',
               '<b>Get a landlord to say yes</b> with our exact scripts, pitch and follow-up messages.',
               '<b>Know if a place makes money before you sign</b> with the built-in profit and ROI calculator.'],
        sound=['You would love to start a rental business, but <b>buying property is not an option</b> for you right now.',
               'You keep hearing about rental arbitrage and co-hosting, but <b>you don’t know where to start</b> or if it is legal.',
               'You are afraid of <b>signing a lease that doesn’t pay off.</b>',
               'You want a <b>clear, step-by-step plan</b>, not a hundred tips from social media.'],
        first_qa='“I don&#x27;t own any property.”'),
    'course/owner': dict(
        title='Turn your property into a 5-star rental · 6-Figure Host Course',
        desc='Already own an apartment, a house or a spare room? Turn it into a profitable short- or mid-term rental that runs with systems, not with your evenings.',
        pill='For property owners',
        lead='Turn the property you already own into a <b>5-star rental that earns more</b>, and runs with systems instead of your evenings and weekends.',
        ticks=['<b>Run the numbers</b> on short-term, mid-term and long-term before you decide, with the ownership calculator.',
               '<b>Set it up and list it so it books itself:</b> what to buy, what to skip, and a listing that sells.',
               '<b>Hand off the day-to-day</b> to a cleaner, a manager and automated messages you set up once.'],
        sound=['You own an apartment, a house or a spare room, and <b>you know it could earn more</b> than it does now.',
               'You worry about <b>guests damaging the place</b> or about the local rules.',
               'You don’t want a second job: you want the property to <b>run without you being there.</b>',
               'You want to do it <b>properly and legally</b>, with contracts, checklists and a team you trust.'],
        first_qa='“What if guests damage the place?”',
        good="<p>Here is the good part: <b>you already have the hardest piece, the property.</b> What you need is the right rental model for it, a listing that sells, and systems that keep working while you get on with your life.</p>"),
    'course/nomad': dict(
        title='Rental income you can run from anywhere · 6-Figure Host Course',
        desc='Build a rental business that funds a life of travel: self check-in, automated messages and a local team, so you can manage it from anywhere.',
        pill='For digital nomads and expats',
        lead='Build a rental income that lets you <b>live, travel and work from anywhere</b>, run by systems and a local team.',
        ticks=['<b>Automate check-in and guest messages</b> so nobody waits for you to wake up in another time zone.',
               '<b>Build a local team you trust:</b> cleaner, manager and handyman, with agreements and checklists ready.',
               '<b>Scale to more homes in more countries</b>, the way we did in Barcelona and Bali.'],
        sound=['You want income that <b>doesn’t depend on where you are</b>, your clients or your next post.',
               'You love the idea of <b>homes in different places</b> you can rent out and stay in.',
               'You need a business that <b>runs from your phone</b>, with self check-in and automated messages.',
               'You are ready to <b>put in the work now</b> to enjoy the freedom later.'],
        first_qa=None,
        good="<p>Here is the good part: <b>you don't need to live next to your rentals.</b> You need a model that fits your budget, a local team you trust, and systems that keep working while you are on the other side of the world.</p>"),
}


def course_page(key):
    v = VARIANTS[key]
    s = course_base()
    if 'pill' in v:
        s = re.sub(r'<span class="pill">.*?</span>', '<span class="pill">%s</span>' % v['pill'], s, count=1)
        s = re.sub(r'(<header class="hero">.*?)<p class="lead">.*?</p>', lambda m: m.group(1) + '<p class="lead">%s</p>' % v['lead'], s, count=1, flags=re.S)
        s = re.sub(r'(<header class="hero">.*?)<ul class="ticks">.*?</ul>', lambda m: m.group(1) + '<ul class="ticks">\n%s\n</ul>' % '\n'.join('<li><span>%s</span></li>' % t for t in v['ticks']), s, count=1, flags=re.S)
        s = re.sub(r'(<span class="sc b">Does this</span>.*?)<ul class="ticks">.*?</ul>', lambda m: m.group(1) + '<ul class="ticks">\n%s\n</ul>' % '\n'.join('<li><span>%s</span></li>' % t for t in v['sound']), s, count=1, flags=re.S)
    if v.get('good'):
        s = re.sub(r'<p>Here is the good part:.*?</p>', lambda m: v['good'], s, count=1)
    if v.get('first_qa'):
        items = re.findall(r'<li><p class="q">.*?</li>', s, flags=re.S)
        first = [i for i in items if v['first_qa'].replace('&#x27;', "'") in html.unescape(i)]
        if first:
            rest = [i for i in items if i is not first[0]]
            block = '\n'.join([first[0]] + rest)
            s = re.sub(r'(<ul class="qa">\n).*?(\n</ul>)', lambda m: m.group(1) + block + m.group(2), s, count=1, flags=re.S)
    return page(key + '/', v['title'], v['desc'], s, 'course')


# ---------------------------------------------------------------- guide pages
def offer(name, items, was, now, href, note):
    return '''<section class="sec taupe" id="offer">
<div class="in">
<div class="head"><h2 class="lock"><span class="sc">Everything</span><span class="dp">You get inside</span></h2></div>
<div class="offer">
<div class="list"><div><h3 class="dp3">%s</h3><ul class="ticks">%s</ul></div></div>
<div class="buy">
<p class="was">Normally <s>$%d</s></p>
<p class="price">$%d</p>
<small>One payment, lifetime access. No subscription.</small>
<a class="cta" href="%s">Get instant access</a>
<small>%s</small>
</div>
</div>
</div>
</section>''' % (name, ''.join('<li><span>%s</span></li>' % i for i in items), was, now, href, note)


def faq(items):
    return '<section class="sec"><div class="in two flip top"><h2 class="lock"><span class="sc">Questions</span><span class="dp">Before you buy</span></h2><div class="faq">%s</div></div></section>' % ''.join(
        '<details%s><summary>%s</summary><p>%s</p></details>' % (' open' if n == 0 else '', q, a) for n, (q, a) in enumerate(items))


def crosssell():
    return '''<section class="sec night">
<div class="in two">
<div class="copy">
<h2 class="lock"><span class="sc">New to hosting?</span><span class="dp">Start with the course</span></h2>
<p class="lead">The city guide shows you the local rules and numbers. The 6-Figure Host Course shows you how to launch, run and scale the business itself, with the host starter kit and the profit calculator included.</p>
<div class="ctawrap"><a class="cta" href="/course/">See the course</a><small>Already includes the Profit Calculator.</small></div>
</div>
<img src="/assets/course-mockup.webp" width="1400" height="957" alt="The 6-Figure Host Course on a laptop, tablet and phone" loading="lazy">
</div>
</section>'''


GUIDES = {
    'barcelona': dict(
        title='Barcelona Host Guide · Legal mid-term rentals in Barcelona', active='barcelona',
        desc='How to run a legal, profitable rental business in Barcelona with mid-term stays, and copy the model to any city in Europe.',
        script='Barcelona', price=59, img='/assets/sales/bcn-cover.webp', imgw=675, imgh=1200, imgalt='Rooftops of Barcelona at sunset with the Sagrada Família in the distance',
        pill='Interactive guide + mid-term rental toolkit',
        lead='How to run a <b>legal, profitable rental business</b> in Barcelona with mid-term stays, and copy the model to any city in Europe.',
        ticks=['<b>Understand the rules</b>: the 32-day rule, tourist licences and the 2028 deadline, and the 2026 Catalan law.',
               '<b>Rent by rooms within the new cap</b> and add real services the right way.',
               '<b>Choose individual or company</b> with the taxes explained, and a worked example.'],
        sound_h=('Barcelona is', 'one of the best markets in Europe'),
        sound='<p>It is also one of the strictest. New tourist licences are not issued, the ones that exist end in November 2028, and since January 2026 mid-term rentals are regulated too. Operating an illegal tourist flat can cost up to €600,000.</p><p><b>Does that mean you should not invest? No.</b> It means you need to understand the rules better than everyone else. Every time the rules get stricter, the people who do it right get less competition.</p><p>We run five apartments in Barcelona without a single tourist licence. This guide is how.</p>',
        quote='“In Barcelona, the legal model is not the safe option. It is the only option.”',
        side='/assets/sales/bcn-room.webp', sidealt='A light bedroom in one of our Barcelona apartments',
        parts=[('Part 1', 'Understanding Barcelona', 'The numbers, the three ways to rent, what really happens with tourist licences, and the neighbourhoods.', ['Barcelona by the numbers', 'The three ways to rent (and the 32-day rule)', 'Tourist licences and the 2028 deadline', 'Choose your neighbourhood']),
               ('Part 2', 'The legal mid-term model', 'Seasonal rentals of 32 days or more under the 2026 Catalan law, renting by rooms, the platforms, and individual or company.', ['Seasonal rentals done right', 'Renting by rooms and the rent cap', 'Platforms, registration and enforcement', 'Individual or company? (taxes explained)']),
               ('Part 3', 'Running &amp; scaling', 'How we run a mid-term apartment day to day, the real numbers of a flat, and taking the model to other European cities.', ['Run it day to day', 'The numbers of a Barcelona apartment', 'Take the model to other European cities', 'Mistakes to avoid in Barcelona'])],
        feats=[('Rent cap checker', 'Put in the cap, the rooms and your planned rent. It tells you if you are within the law, or how far over.'),
               ('Flat profit calculator', 'Income, costs and a vacancy reserve, per month and per year, for any flat on your shortlist.'),
               ('Company tax estimate', 'See what a micro-company pays in corporate tax and dividends on your profit.'),
               ('Neighbourhood scorecard', 'Score up to three areas on eight criteria and see which one fits your guest best.'),
               ('Contract and document checklists', 'Seasonal contract essentials, guest documents, legal and tax, ready to tick off.'),
               ('AI prompts and the PDF', 'Prompts to compare areas and prepare your lawyer meeting, plus the full guide as a PDF.')],
        items=['12 interactive lessons in 3 parts', 'Rent cap checker, flat profit and company tax calculators', 'Neighbourhood scorecard', 'Checklists for contracts, guest documents, legal and tax, and new cities', 'Your Barcelona roadmap', 'The full guide as a PDF'],
        faq=[('When do I get access?', 'Right after checkout. You get your personal access code on the screen and by email, and you open the guide straight away.'),
             ('Is this legal advice?', 'No. The guide shares our experience and public information as of October 2026. Catalan and Spanish rules change fast, so always confirm your case with a lawyer and a tax advisor.'),
             ('Do I need the course too?', 'No, the guide works on its own. If you are new to hosting, the 6-Figure Host Course covers how to launch, run and scale the business itself.'),
             ('Does it only work in Barcelona?', 'The rules are specific to Barcelona and Catalonia, but lesson 11 shows you how to take the mid-term model to other European cities.'),
             ('Do you offer refunds?', 'As this is a digital product, no refunds can be given after purchase. If you bought it twice by accident, write to <a href="mailto:contact@6figurehost.com">contact@6figurehost.com</a>.')]),
    'bali': dict(
        title='Bali Host Guide · Invest in a villa rental in Bali, legally', active='bali',
        desc='How to legally invest, build and run a profitable villa rental in Bali, even as a foreigner.',
        script='Bali', price=49, img='/assets/sales/bali-cover.webp', imgw=673, imgh=1200, imgalt='A modern villa with a pool deck at sunset',
        pill='Interactive guide + Bali investor toolkit',
        lead='How to <b>legally invest, build and run</b> a profitable villa rental in Bali, even as a foreigner.',
        ticks=['<b>Know what you can own</b>: freehold, leasehold, Hak Pakai and HGB, and why the colour of the land decides everything.',
               '<b>Set up legally</b>: your PT PMA, the investor KITAS and the licences to rent short-term.',
               '<b>Buy, build and run</b> a villa that lasts, through the rain, the water and the waste.'],
        sound_h=('Bali can give you', 'a villa that pays for itself'),
        sound='<p>But Bali also eats unprepared investors for breakfast. You cannot own land as a foreigner. The zone of a plot matters more than the view. Many villas are built to be sold, not to last. And unlicensed rentals are being delisted from the platforms.</p><p><b>Does that mean you should not invest? No.</b> It means the bar is higher, and that is exactly your opportunity. When the rules get tighter, the hosts who did it right get less competition, better rankings and higher prices.</p><p>We walked away from more deals than we signed. This guide is everything we learned on the ground.</p>',
        quote='“In Bali, the cheapest deal is usually the most expensive one.”',
        side='/assets/sales/bali-bath.webp', sidealt='A guest reading in a sculptural bathtub in a Bali villa',
        parts=[('Part 1', 'Understanding the island', 'The numbers, the areas, how land ownership works for foreigners, and zoning.', ['Bali by the numbers', 'Choose your area', 'Who can own what (freehold vs leasehold)', 'Zoning: the colour that decides everything']),
               ('Part 2', 'Setting up legally', 'Your PT PMA, the investor visa, and the licences to rent short-term without risking a closure notice.', ['Your PT PMA', 'The investor visa', 'Licences to rent short-term (the 2026 crackdown)']),
               ('Part 3', 'Buying, building &amp; running', 'How to spot a badly built villa, how to build one that lasts, the aesthetic that gets booked, and the day-to-day reality.', ['Buying a finished villa', 'Building your own villa', 'The Bali aesthetic that gets booked', 'Running a villa day to day', 'Mistakes to avoid in Bali'])],
        feats=[('Lease comparison', 'Compare two villas by price per remaining year, the number that really matters with leasehold.'),
               ('Revenue check', 'Your nightly rate and occupancy against the Bali average listing, with the 10% local tax.'),
               ('Zoning tool', 'Pick the colour of a plot and see what you can build and rent there.'),
               ('Leasehold and land checklists', 'Every clause and check to tick off before you pay the balance.'),
               ('Villa inspection checklist', 'Twenty checks for cracks, water, pool, systems and drainage before you sign.'),
               ('AI prompts and the PDF', 'Prompts to compare areas, review a lease and prepare your zoning questions, plus the full guide as a PDF.')],
        items=['12 interactive lessons in 3 parts', 'Lease comparison, revenue check and zoning tools', 'Checklists for leasehold, land due diligence, villa inspection and KITAS documents', 'Licensing roadmap and your Bali investor roadmap', 'The full guide as a PDF'],
        faq=[('When do I get access?', 'Right after checkout. You get your personal access code on the screen and by email, and you open the guide straight away.'),
             ('Is this legal advice?', 'No. The guide shares our experience and public information as of October 2026. Indonesian rules change often and differ per regency, so always confirm your case with a licensed notary, lawyer or consultant.'),
             ('Do I need the course too?', 'No, the guide works on its own. If you are new to hosting, the 6-Figure Host Course covers how to launch, run and scale the business itself.'),
             ('Can a foreigner really do this?', 'Yes, through leasehold or a company, never through a nominee. The guide explains each legal route.'),
             ('Do you offer refunds?', 'As this is a digital product, no refunds can be given after purchase. If you bought it twice by accident, write to <a href="mailto:contact@6figurehost.com">contact@6figurehost.com</a>.')]),
}


def guide_page(key):
    g = GUIDES[key]
    href = '/checkout?item=%s' % key
    hero = '''<div class="bar"><div class="in"><p><b>Launch offer.</b> The new interactive %s guide is live. Get it for $%d instead of $79.</p><a href="%s">Start today</a></div></div>
<header class="hero">
<div class="in">
<div class="txt">
<span class="pill">%s</span>
<h1><span class="sc">%s</span><span class="dp">Host Guide</span></h1>
<p class="lead">%s</p>
<ul class="ticks">%s</ul>
<div class="ctawrap"><a class="cta" href="%s">Get instant access for $%d</a><small>Secure checkout. Lifetime access. Works on phone and laptop.</small></div>
</div>
<div class="stage"><img class="photo" src="%s" width="%d" height="%d" alt="%s"></div>
</div>
</header>''' % (g['script'], g['price'], href, g['pill'], g['script'], g['lead'], ''.join('<li><span>%s</span></li>' % t for t in g['ticks']), href, g['price'], g['img'], g['imgw'], g['imgh'], g['imgalt'])
    truth = '''<section class="sec sand"><div class="in two">
<div><div class="head"><h2 class="lock"><span class="sc b">%s</span><span class="dp">%s</span></h2></div><div class="copy">%s</div><p class="lead" style="margin-top:24px">%s</p></div>
<img src="%s" alt="%s" style="width:100%%;aspect-ratio:4/5;object-fit:cover" loading="lazy">
</div></section>''' % (g['sound_h'][0], g['sound_h'][1], g['sound'], g['quote'], g['side'], g['sidealt'])
    parts = '''<section class="sec night"><div class="in">
<div class="head"><h2 class="lock"><span class="sc">The guide</span><span class="dp">Three parts, %d lessons</span></h2><p class="lead narrow">Read it in order: first you understand the rules, then you set up the legal model, then you run and scale it. Every lesson ends with a task.</p></div>
<div>%s</div>
<div class="ctawrap" style="margin-top:48px"><a class="cta" href="%s">Get instant access for $%d</a><small>Secure checkout. Lifetime access.</small></div>
</div></section>''' % (sum(len(p[3]) for p in g['parts']), ''.join(
        '<div class="part"><div><div class="sc">%s</div><h3 class="dp3">%s</h3></div><div><p>%s</p><ul class="chs">%s</ul></div></div>' % (a, b, c, ''.join('<li><span class="n">%02d</span><span>%s</span></li>' % (n, t) for n, t in d))
        for a, b, c, d in [(p[0], p[1], p[2], list(zip(range(1 + sum(len(q[3]) for q in g['parts'][:i]), 100), p[3]))) for i, p in enumerate(g['parts'])]), href, g['price'])
    feats = '''<section class="sec"><div class="in">
<div class="head"><h2 class="lock"><span class="sc b">Not a PDF</span><span class="dp">A guide you work inside</span></h2><p class="lead narrow">It opens in your browser, remembers where you stopped and does the maths for you. The PDF is included too.</p></div>
<ul class="feat">%s</ul>
</div></section>''' % ''.join('<li><h3 class="dp3">%s</h3><p>%s</p></li>' % f for f in g['feats'])
    body = '\n'.join([hero, truth, parts, feats, offer('The interactive %s Host Guide' % g['script'], g['items'], 79, g['price'], href, 'Secure payment by Stripe. Add the Profit &amp; ROI Calculator at checkout for $37.'), crosssell(), faq(g['faq'])])
    return page(key + '/', g['title'], g['desc'], body, g['active'])


# ---------------------------------------------------------------- calculator page
def calculator_page():
    href = '/checkout?item=calculator'
    body = '''<div class="bar"><div class="in"><p><b>Launch offer.</b> Get the Profit &amp; ROI Calculator for $37 instead of $97.</p><a href="%(h)s">Get it now</a></div></div>
<header class="hero calc">
<div class="in">
<div class="txt">
<span class="pill">Interactive calculator · works in your browser</span>
<h1><span class="sc">Profit &amp; ROI</span><span class="dp">Calculator</span></h1>
<p class="lead">See in seconds if a property is <b>profitable before you rent or buy it.</b> No maths, no formulas, no guessing.</p>
<ul class="ticks">
<li><span><b>Profit, ROI and break-even</b> calculated for you, at three occupancy rates.</span></li>
<li><span><b>Works for rental arbitrage, leasehold and ownership</b>, so the numbers match your model.</span></li>
<li><span><b>Test prices, rooms and costs</b> and see right away what changes.</span></li>
</ul>
<div class="ctawrap"><a class="cta" href="%(h)s">Get instant access for $37</a><small>Secure checkout. Lifetime access. Already included in the course.</small></div>
</div>
<figure class="tab"><div class="ipad"><video autoplay muted loop playsinline preload="metadata" poster="/assets/sales/calculator-demo.webp" src="/assets/sales/calculator-demo.mp4" aria-label="A walk through the Profit Calculator: entering rent and rooms, then the profit table, the 5-year view and the break-even chart" style="display:block;width:100%%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;background:#fff"></video></div><figcaption>The calculator in action.</figcaption></figure>
</div>
</header>
<section class="sec night"><div class="in">
<div class="head"><h2 class="lock"><span class="sc">Before you sign</span><span class="dp">Decide with numbers, not hope</span></h2></div>
<div class="fit">
<div class="no"><h3 class="dp3">Without the calculator</h3><ul>
<li><i aria-hidden="true">✕</i><span>“I think this deal might work…”</span></li>
<li><i aria-hidden="true">✕</i><span>Hours trying to calculate the numbers</span></li>
<li><i aria-hidden="true">✕</i><span>Constant doubt before signing a lease</span></li>
<li><i aria-hidden="true">✕</i><span>Overthinking every decision</span></li></ul></div>
<div class="yes"><h3 class="dp3">With the calculator</h3><ul>
<li><i aria-hidden="true">✓</i><span>Know right away if a deal is good or bad</span></li>
<li><i aria-hidden="true">✓</i><span>Initial investment, profit, ROI and break-even calculated for you</span></li>
<li><i aria-hidden="true">✓</i><span>Make confident decisions</span></li>
<li><i aria-hidden="true">✓</i><span>Decisions based on data, not stress</span></li></ul></div>
</div>
</div></section>
<section class="sec"><div class="in">
<div class="head"><h2 class="lock"><span class="sc b">What it does</span><span class="dp">Everything you need to judge a property</span></h2></div>
<ul class="feat">
<li><h3 class="dp3">Your business costs</h3><p>Utilities, team and other monthly costs, plus one-time setup costs room by room, with an AI prompt to estimate them for your city.</p></li>
<li><h3 class="dp3">Three business models</h3><p>Renting, buying or leasing a property, each with its own fields and results.</p></li>
<li><h3 class="dp3">Three scenarios</h3><p>Worst, average and best case occupancy, each with monthly income, costs, profit, ROI and break-even.</p></li>
<li><h3 class="dp3">Break-even chart</h3><p>See month by month when your profit covers your initial investment.</p></li>
<li><h3 class="dp3">5-year view</h3><p>Your estimated profit after five years with one, two or four similar properties.</p></li>
<li><h3 class="dp3">Any currency</h3><p>Switch currency in one click. Your numbers are saved on your device.</p></li>
</ul>
<div class="chips-row"><span>New hosts</span><span>Arbitrage hosts</span><span>Property investors</span><span>Leasehold investors</span><span>Anyone running the numbers on a deal</span></div>
</div></section>
%(offer)s
%(cross)s
%(faq)s''' % dict(h=href, offer=offer('The Profit &amp; ROI Calculator', ['Calculators for rental arbitrage, ownership and leasehold', 'Business cost overview with an AI prompt for your city', 'Three occupancy scenarios, break-even chart and 5-year view', 'Multi-currency, saved on your device'], 97, 37, href, 'Secure payment by Stripe. Included in the 6-Figure Host Course.'),
                      cross='''<section class="sec night"><div class="in two"><div class="copy"><h2 class="lock"><span class="sc">Want the full system?</span><span class="dp">The calculator is in the course</span></h2><p class="lead">The 6-Figure Host Course includes this calculator, the host starter kit and 13 lessons to launch, run and scale your rental business.</p><div class="ctawrap"><a class="cta" href="/course/">See the course</a></div></div><img src="/assets/course-mockup.webp" width="1400" height="957" alt="The 6-Figure Host Course on a laptop, tablet and phone" loading="lazy"></div></section>''',
                      faq=faq([('Do I need Excel?', 'No. The calculator works in your browser, on your phone or laptop. Nothing to download.'),
                               ('I am bad at maths. Will I understand it?', 'Yes. You only type in the basics, like rent, rooms and nightly price. Every field has a short “What is this?” explanation.'),
                               ('What currencies does it support?', 'EUR, USD, CAD, BRL, IDR, THB, AUD, MXN, JPY, CHF and AED.'),
                               ('Is this a one-time payment?', 'Yes. You pay once and keep lifetime access.'),
                               ('Is it included in the course?', 'Yes. If you buy the 6-Figure Host Course, the calculator is already inside.')]))
    return page('calculator/', 'Profit & ROI Calculator · Know if a property is profitable', 'See in seconds if a property is profitable before you rent or buy it: profit, ROI and break-even for arbitrage, leasehold and ownership.', body, 'calculator')


# ---------------------------------------------------------------- home page
def home_page():
    body = open(os.path.join(HERE, 'home_body.html'), encoding='utf-8').read()
    return page('', '6-Figure Host · Farah & Daniel', 'Ten years of hosting in Barcelona and Bali, turned into a course, city guides and a calculator to build a profitable, legal rental business.', body)


# ---------------------------------------------------------------- masterclass video
def masterclass_page():
    body = """OFFERBAR
<section class="mcv" aria-label="Free masterclass video">
<div class="mcv-in">
<p class="mcv-k"><span class="sc">Free masterclass</span></p>
<div class="mcv-frame"><iframe src="https://www.youtube-nocookie.com/embed/0Bfym8N8JJA?rel=0&amp;modestbranding=1&amp;playsinline=1" title="6-Figure Host masterclass with Farah and Daniel" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>
<p class="mcv-note" data-o="mc-note">*In the video we talk about our old guide and its price. That guide is now the full 6-Figure Host Course: <b>$297</b>.</p>
<h1 class="mcv-h">From sleeping on the couch to homes around the world</h1>
<p class="mcv-lead">Everything we learned in ten years of hosting, in one free class.</p>
<div class="mcv-cta"><a class="cta" href="/course/#pricing"><span data-o="cta">Get instant access for $297</span></a><a class="mcv-more" href="/course/">See what’s inside the course</a></div>
</div>
</section>
<section class="sec">
<div class="in two flip mc-us">
<img src="/assets/sales/us-mc.webp" width="675" height="844" alt="Farah and Daniel together" loading="lazy">
<div class="copy">
<h2 class="lock"><span class="sc b">Our story</span><span class="dp">From a couch to homes around the world</span></h2>
<p>We met in 2017 as housemates in a shared flat in Barcelona. Farah sublet her bedroom and slept on the couch. One apartment turned into five, then came multiple properties in Bali, and we still don’t own a single one of them.</p>
</div>
</div>
</section>
<section class="sec sand">
<div class="in two">
<div class="copy">
<h2 class="lock"><span class="sc b">After watching</span><span class="dp">Take the next step</span></h2>
<p>The masterclass shows you how the model works. The 6-Figure Host Course gives you everything to do it yourself: the launch roadmap, landlord scripts, the profit calculator, contracts and checklists, and our real case studies from Barcelona and Bali.</p>
<div class="ctawrap"><a class="cta" href="/course/#pricing"><span data-o="cta">Get instant access for $297</span></a><small>One payment or split pay. Lifetime access.</small></div>
</div>
<img src="/assets/course-mockup.webp" width="1400" height="957" alt="The 6-Figure Host Course on a laptop, tablet and phone" loading="lazy">
</div>
</section>"""
    body = body.replace('OFFERBAR', OFFERBAR_HTML.replace('href="#pricing"', 'href="/course/#pricing"'))
    return page('masterclassvideo/', 'Free masterclass · 6-Figure Host', 'Watch the free masterclass by Farah & Daniel: how to build a profitable rental business in Barcelona, Bali or anywhere, with or without owning property.', body)


if __name__ == '__main__':
    open(os.path.join(OUT, 'assets/sales.css'), 'w').write(open(os.path.join(HERE, 'base.css')).read() + '\n' + open(os.path.join(HERE, 'extra.css')).read() + '\n' + open(os.path.join(HERE, 'home.css')).read())
    for k in VARIANTS: print(k, course_page(k))
    for k in GUIDES: print(k, guide_page(k))
    print('calculator', calculator_page())
    print('home', home_page())
    print('masterclass', masterclass_page())
