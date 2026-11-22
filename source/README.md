# Course source (not published)

The course page `public/index.html` is generated from these files. Cloudflare only publishes `public/`, so nothing here is online.

- `content.txt` – all lesson text and blocks
- `template.html` – layout, styles and scripts
- `build.py`, `proof.py`, `i18n_extract.py`, `setup.tsv`, `blocks.json`, `pt.json`, `tr/` – build helpers

Rebuild (the script uses fixed paths):

```
mkdir -p /home/claude/build /home/claude/work /home/claude/site
cp -r source/. /home/claude/build/ && cp source/blocks.json /home/claude/work/
cp -r public/hostcourse/. /home/claude/site/
cd /home/claude/build && python3 -I build.py
cp /home/claude/site/index.html public/hostcourse/index.html
```
Then check `grep -c 'id="cel-stay"' public/hostcourse/index.html` prints 1, commit and push to `main`.
