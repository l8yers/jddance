#!/usr/bin/env python3
"""Check generated page structure, local links, assets and production boundaries."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.tags=[]; self.h1=0
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs);self.tags.append((tag,attrs))
        if tag=='h1': self.h1+=1
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ['href','src','poster','data-src']:
            if key in attrs:self.refs.append(attrs[key])
        if 'srcset' in attrs:self.refs.extend(v.strip().split()[0] for v in attrs['srcset'].split(','))
        if tag=='img':
            assert all(k in attrs for k in ['alt','width','height']),attrs

def main():
    pages={}
    for file in OUT.glob('*.html'):
        p=Page();p.feed(file.read_text());pages[file.name]=p
        assert p.h1==1,(file,p.h1)
        assert len(p.ids)==len(set(p.ids)),file
        assert {'main-content','mobileMenu','menuToggle','year'}<=set(p.ids),file
        assert '{{' not in file.read_text(),file
    for name,p in pages.items():
        for ref in p.refs:
            url=urlsplit(ref)
            if url.scheme or url.netloc:continue
            target=unquote(url.path).lstrip('/') or (name if url.fragment else 'index.html')
            assert (OUT/target).is_file(),(name,ref)
            if url.fragment and target in pages:
                assert url.fragment in pages[target].ids,(name,ref)
    contact=pages['contact.html']
    form=next(a for t,a in contact.tags if t=='form')
    assert form['data-netlify']=='true' and form['method']=='POST' and form['action']=='/thanks.html'
    assert form['netlify-honeypot']=='bot-field'
    inputs={a.get('name'):a for t,a in contact.tags if t in {'input','select','textarea'}}
    assert inputs['form-name']['value']==form['name']=='contact'
    assert all('required' in inputs[n] for n in ['name','email','message'])
    assert inputs['name']['autocomplete']=='name' and inputs['email']['autocomplete']=='email'
    assert 'privacy.html' in contact.refs
    days=json.loads((ROOT/'data/schedule.json').read_text())
    assert sum(len(d['classes']) for d in days)==15
    tue=next(d['classes'] for d in days if d['day']=='Tue')
    assert tue[0]=={'name':'Empire','details':'4:30–6:00pm','price':'£7'}
    assert tue[2]['price']=='£8'
    karate=next(c for d in days for c in d['classes'] if c['name']=='Karate')
    assert karate['price']=='£5'
    academy=[c for d in days if d['day']=='Sat' for c in d['classes'] if c['name']=='Dance academy']
    assert len(academy)==2 and all(c['price']=='£10' for c in academy)
    classes=(OUT/'classes.html').read_text()
    assert classes.index('id="full-schedule"')<classes.index('Class enquiries')<classes.index('Popular classes')
    for blocked in ['New','src','scripts','api','.git','data']:
        assert not (OUT/blocked).exists(),blocked
    for page in ['thanks','404']:
        assert 'noindex, follow' in (OUT/f'{page}.html').read_text()
    assert 'fonts.googleapis.com' not in '\n'.join(p.read_text() for p in OUT.glob('*.html'))
    print(f'PASS: {len(pages)} pages; local links, responsive assets, form wiring, schedule data, SEO and publish boundaries.')

if __name__=='__main__':main()
