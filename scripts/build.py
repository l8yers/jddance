#!/usr/bin/env python3
"""Build the current site from src/ and data/. Uses Python standard library only."""
from pathlib import Path
from html import escape
from datetime import date
import json
import os
import re
import shutil
from schedule_pdf import schedule_pdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public'
DOMAIN = 'https://jddance.info'
NAV = [('index', 'Home'), ('about', 'About'), ('classes', 'Classes'), ('studiohire', 'Studio Hire'), ('Wedding-first-dance', 'First Dance'), ('dance-hen-party', 'Hen Parties'), ('contact', 'Contact')]

def read(path):
    return (ROOT / path).read_text()

def load(path):
    return json.loads(read(path))

def image_tag(match):
    filename, alt, css, loading, sizes = match.group(1).strip().split('|')
    variants = load('data/media.json')[filename]
    preferred = 256 if filename == 'logo.png' and not css else 640
    default = next((v for v in variants if v['width'] >= preferred), variants[-1])
    sources = ', '.join(f"{v['src']} {v['width']}w" for v in variants)
    priority = ' fetchpriority="high"' if css == 'hero-photo' else ''
    return (f'<img src="{default["src"]}" srcset="{sources}" sizes="{escape(sizes)}" '
            f'width="{default["width"]}" height="{default["height"]}" alt="{escape(alt)}" '
            f'class="{escape(css)}" loading="{loading}" decoding="async"{priority}>')

def timetable(days):
    result = ['<div class="timetable">']
    for day in days:
        result.append(f'<div class="day" id="day-{escape(day["day"].lower())}"><h3 class="day-head">{escape(day["day"])}</h3><ul class="slots">')
        for slot in day['classes']:
            age = f'<span class="age-label">Age {escape(slot["age"])}</span>' if slot.get('age') else ''
            result.append(f'<li class="slot"><div><div class="name">{escape(slot["name"])}</div><div class="meta">{escape(slot["details"])} {age}</div></div><span class="price-pill">{escape(slot["price"])}</span></li>')
        result.append('</ul></div>')
    return '\n'.join(result) + '</div>'

def build():
    # Publish only generated pages and referenced assets, never source directories.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    pages = load('data/pages.json')
    days = load('data/schedule.json')
    for slug, info in pages.items():
        navigation = '\n'.join(f'<li><a href="{key}.html"'+(' aria-current="page"' if key == slug else '')+f'>{label}</a></li>' for key, label in NAV)
        footer_navigation = '\n'.join(f'<li><a href="{key}.html"'+(' aria-current="page"' if key == slug else '')+f'>{label}</a></li>' for key, label in NAV if key not in {'index', 'about', 'classes'})
        url = DOMAIN + ('/' if slug == 'index' else '/' + slug + '.html')
        private = slug in {'thanks', '404'} or os.getenv('CONTEXT') in {'deploy-preview', 'branch-deploy'}
        metadata = ('<meta name="robots" content="noindex, follow">\n' if private else '')
        metadata += f'<link rel="canonical" href="{url}">\n'
        for prop, value in {'og:type':'website', 'og:locale':'en_GB', 'og:site_name':'JD Dance', 'og:title':info['title'], 'og:description':info['description'], 'og:url':url, 'og:image':DOMAIN+'/assets/social-card.jpg', 'og:image:width':'1200', 'og:image:height':'630', 'og:image:alt':'JD Dance — dance classes, studio hire and private dance bookings'}.items():
            metadata += f'<meta property="{prop}" content="{escape(value)}">\n'
        metadata += '<meta name="twitter:card" content="summary_large_image">'
        if slug == 'index':
            schema = {'@context':'https://schema.org', '@type':'LocalBusiness', 'name':'JD Dance', 'url':DOMAIN+'/', 'image':DOMAIN+'/assets/social-card.jpg', 'telephone':'+447587107317', 'email':'jddanceex@gmail.com', 'address':{'@type':'PostalAddress','streetAddress':'Lockett St','addressLocality':'Manchester','postalCode':'M8 8EF','addressCountry':'GB'}, 'sameAs':['https://www.facebook.com/jddance7','https://www.instagram.com/jddancee/']}
            metadata += '\n<script type="application/ld+json">'+json.dumps(schema)+'</script>'
        values = {**info, 'metadata':metadata, 'content':read(f'src/pages/{slug}.html'), 'header':read('src/partials/header.html'), 'footer':read('src/partials/footer.html'), 'navigation':navigation, 'footer_navigation':footer_navigation, 'year':str(date.today().year), 'timetable':timetable(days)}
        values['title'] = escape(info['title'])
        values['description'] = escape(info['description'])
        html = read('src/layout.html')
        for _ in range(4):
            for key, value in values.items():
                html = html.replace('{{ '+key+' }}', value)
        html = re.sub(r'\{\{ image (.*?) \}\}', image_tag, html)
        assert '{{' not in html, slug
        if slug == '404':
            # A 404 can be served at any nested path; links must remain rooted.
            html = re.sub(r'((?:href|src)=")(?!(?:https?:|mailto:|tel:|/|#))', r'\1/', html)
            html = re.sub(r'(srcset=")([^\"]+)', lambda m:m[1]+', '.join('/'+part.strip() for part in m[2].split(',')), html)
        html = '<!-- Generated by scripts/build.py. Edit src/ and data/ instead. -->\n' + html
        (ROOT / f'{slug}.html').write_text(html)
        (OUT / f'{slug}.html').write_text(html)
    for name in ['style.css', 'site.js']:
        shutil.copy2(ROOT / name, OUT / name)
    (ROOT / 'assets/jd-schedule.pdf').write_bytes(schedule_pdf(days))
    texts = '\n'.join(p.read_text() for p in OUT.glob('*.html')) + read('style.css') + read('site.js')
    referenced = set(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:webp|png|jpg|jpeg|mp4|webm|woff2|pdf)\b', texts))
    referenced.add('assets/fonts/OFL.txt')
    for relative in referenced:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(relative)
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    urls = [DOMAIN + ('/' if slug == 'index' else '/'+slug+'.html') for slug in pages if slug not in {'thanks','404'}]
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>\n')
    robots = 'User-agent: *\nDisallow: /\n' if os.getenv('CONTEXT') in {'deploy-preview','branch-deploy'} else 'User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n'
    (OUT / 'robots.txt').write_text(robots)
    print(f'Built {len(pages)} pages with {len(referenced)} referenced assets into public/.')

if __name__ == '__main__':
    build()
