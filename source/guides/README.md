# City guides (Barcelona, Bali)

Each guide is built like the course: `content.txt` (lessons) + `template.html` (the course layout) -> `index.html`.

Edit `content.txt`, then from this folder:

```
GUIDE_DIR=barcelona python3 -I gbuild.py && cp barcelona/index.html ../../public/hostcourse/guides/barcelona/index.html
GUIDE_DIR=bali python3 -I gbuild.py && cp bali/index.html ../../public/hostcourse/guides/bali/index.html
```

Only re-run `mk_tpl.py` if the course template changed (it adds the guide title, brand, storage key and calculators):
`python3 mk_tpl.py barcelona "Barcelona Host Guide · 6-Figure Host" "Barcelona Guide" sixfig-bcn-v1 EUR`
`python3 mk_tpl.py bali "Bali Host Guide · 6-Figure Host" "Bali Guide" sixfig-bali-v1 USD`

Images live in `public/hostcourse/guides/<guide>/img/`. The PDFs are `public/hostcourse/guides/barcelona.pdf` and `bali.pdf`.
