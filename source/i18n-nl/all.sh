set -e
cd /home/claude/deploy && git checkout -q public/hostcourse/index.html
cd /home/claude/nl
python3 build_nl.py >/dev/null
python3 lang_ui.py >/dev/null
sed -i 's/\.lang \.flag{width:22px;height:15px}\.prog \.bar{width:70px}}/.lang .flag{width:22px;height:15px}}/' /home/claude/deploy/public/hostcourse/index.html
python3 patch2.py
