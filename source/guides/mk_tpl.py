import os
import sys, re
g, title, brand, key, cur = sys.argv[1:6]
t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'template.html'), encoding='utf-8').read()
t = t.replace('<title>6-Figure Host Guide</title>', '<title>%s</title>' % title, 1)
t = t.replace('<span class="d">Host Course</span>', '<span class="d">%s</span>' % brand, 1)
t = t.replace("var KEY='sixfig-course-v1';", "var KEY='%s';" % key, 1)
for a, b in [('Loving the course?', 'Loving the guide?'), ('Back to the course', 'Back to the guide')]:
    t = t.replace(a, b)
css = '''
.verdict.ok{border-color:var(--green);background:#EEF1EC}.verdict.no{border-color:var(--blue);background:#F6ECE9}
.sc-card{overflow-x:auto}.sc{width:100%;border-collapse:separate;border-spacing:0;font-size:14px}
.sc th,.sc td{padding:9px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
.sc thead th{font-size:11px;letter-spacing:.1em;text-transform:uppercase}
.sc thead input{width:100%;min-width:90px;border:1.5px solid var(--ink);border-radius:8px;padding:7px 9px;font:inherit;font-size:13px;background:#fff}
.sc select{border:1.5px solid var(--ink);border-radius:8px;padding:6px 8px;background:#fff;font:inherit}
.sc tfoot td{font-weight:700;font-size:15px}.sc tfoot td.best{color:var(--green)}.sc tfoot td.best::after{content:"  ★ best fit";font-size:11px;letter-spacing:.08em;text-transform:uppercase}
.zone-pick select{border:1.5px solid var(--ink);border-radius:8px;padding:9px 11px;background:#fff;font:inherit;max-width:320px}
.zone-res{border-radius:12px;padding:16px 18px;background:#fff;border:1.5px solid var(--line)}.zone-res b{display:block;font-family:var(--display);font-weight:400;text-transform:uppercase;font-size:20px;margin-bottom:4px}
.zdot{display:inline-block;width:14px;height:14px;border-radius:50%;vertical-align:-2px;margin-right:8px;border:1px solid rgba(0,0,0,.2)}
.legal-note{font-size:13px;color:var(--ink-soft);border-left:3px solid var(--line);padding:6px 0 6px 12px;margin:18px 0}
.srcs{font-size:13px;color:var(--ink-soft)}.srcs li{margin-bottom:4px}
'''
t = t.replace('</style>\n</head>', css + '</style>\n</head>', 1)
t = t.replace('<body>', '<body data-cur="%s">' % cur, 1)
_i = t.rfind('</body>'); t = t[:_i] + open('calc.js', encoding='utf-8').read() + t[_i:]
open('%s/template.html' % g, 'w', encoding='utf-8').write(t)
print('ok', g, len(t))
