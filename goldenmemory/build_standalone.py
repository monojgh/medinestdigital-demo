"""Build golden-memory-demo.html: index.html with all images embedded (one file to share)."""
import base64, re, pathlib, io
from PIL import Image
root = pathlib.Path(__file__).parent
html = (root / 'index.html').read_text(encoding='utf-8')
def uri(name):
    p = root / 'images' / name
    if p.suffix == '.png':
        data, mime = p.read_bytes(), 'image/png'
    else:
        im = Image.open(p).convert('RGB'); b = io.BytesIO()
        im.save(b, 'JPEG', quality=68, optimize=True, progressive=True); data, mime = b.getvalue(), 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(data).decode()
names = sorted(set(re.findall(r'images/([\w-]+\.(?:jpg|png))', html)))
js_names = sorted({f'{n}.jpg' for n in re.findall(r"img:'([\w-]+)'", html)})
table = {n: uri(n) for n in set(names) | set(js_names)}
for n in names:
    html = html.replace(f'images/{n}', table[n])
html = html.replace("`images/${p.img}.jpg`", "IMG[p.img]").replace('images/${p.img}.jpg', '${IMG[p.img]}')
html = html.replace('images/${g.img}.jpg', '${IMG[g.img]}').replace("'images/'+g.img+'.jpg'", "IMG[g.img]").replace("'images/'+p.img+'.jpg'", "IMG[p.img]")
img_js = 'const IMG={' + ','.join(f"'{n[:-4]}':'{table[n]}'" for n in js_names) + '};\n'
html = html.replace('<script>\nconst WA=', '<script>\n' + img_js + 'const WA=', 1)
assert 'images/' not in html, re.findall(r'.{30}images/.{30}', html)[:5]
(root / 'golden-memory-demo.html').write_text(html, encoding='utf-8')
print('ok', len(html) // 1024, 'KB')
