#!/usr/bin/env python3
"""Optional browser checks. Requires Selenium and Firefox; never submits the form."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading
import tomllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('SE_CACHE_PATH','/tmp/jddance-selenium-cache')
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def end_headers(self):
        for key,value in tomllib.loads((ROOT/'netlify.toml').read_text())['headers'][0]['values'].items():
            self.send_header(key,value)
        super().end_headers()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT/'public')))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
options=Options();options.add_argument('-headless')
d=webdriver.Firefox(options=options,service=Service(service_args=['--allow-system-access']))
wait=WebDriverWait(d,10)
shots=Path('/tmp/jddance-browser-checks');shots.mkdir(exist_ok=True)
results=[]
try:
    d.set_context('chrome');d.execute_script('document.documentElement.style.minWidth="0px"');d.set_context('content')
    for width in [320,390,768,901,1440]:
        d.set_window_size(width,1000)
        for page in json.loads((ROOT/'data/pages.json').read_text()):
            d.get(base+page+'.html')
            wait.until(lambda _:d.execute_script('return document.fonts.status==="loaded"'))
            assert d.execute_script('return innerWidth')==width
            assert d.execute_script('return document.documentElement.scrollWidth <= innerWidth'),(page,width,'overflow')
            assert not d.find_element(By.ID,'mobileMenu').is_displayed()
            assert d.find_element(By.ID,'menuToggle').is_displayed()==(width<=900)
            for img in d.find_elements(By.TAG_NAME,'img'):
                d.execute_script('arguments[0].scrollIntoView({block:"center"})',img)
                wait.until(lambda _,img=img:d.execute_script('return arguments[0].complete && arguments[0].naturalWidth>0',img))
            if page not in ['thanks','privacy','404']:
                assert d.find_element(By.CSS_SELECTOR,'.nav-desktop [aria-current="page"]').get_attribute('href').endswith(page+'.html')
            if page=='studiohire':
                assert d.execute_script('return getComputedStyle(document.querySelector(".hero .g-text")).color')=='rgb(140, 229, 118)'
            if page in ['Wedding-first-dance','dance-hen-party']:
                assert d.execute_script('return getComputedStyle(document.querySelector(".hero .g-text")).color')=='rgb(255, 119, 196)'
            if width in [390,1440] and page in ['index','classes','studiohire','contact','Wedding-first-dance']:
                d.execute_script('window.scrollTo(0,0)')
                d.get_full_page_screenshot_as_file(str(shots/f'{page}-{width}.png'))
        results.append(f'{width}px: all 10 pages have no horizontal overflow; images load; menu and hero colours correct.')
        print(results[-1],flush=True)
    d.set_window_size(390,844);d.get(base+'classes.html')
    d.execute_script('window.scrollTo(0,500)');before=d.execute_script('return scrollY')
    d.find_element(By.ID,'menuToggle').click()
    assert d.execute_script('return document.activeElement.id')=='closeMenu'
    d.switch_to.active_element.send_keys(Keys.SHIFT,Keys.TAB)
    assert d.execute_script('return !!document.activeElement.closest("dialog")')
    d.switch_to.active_element.send_keys(Keys.ESCAPE)
    wait.until(lambda _:not d.find_element(By.ID,'mobileMenu').is_displayed())
    assert d.execute_script('return document.activeElement.id')=='menuToggle'
    assert abs(d.execute_script('return scrollY')-before)<2
    d.find_element(By.ID,'menuToggle').click();d.set_window_size(1440,1000)
    wait.until(lambda _:not d.find_element(By.ID,'mobileMenu').is_displayed())
    assert not d.execute_script('return document.body.classList.contains("menu-open")')
    d.get(base+'classes.html');d.find_element(By.CSS_SELECTOR,'.schedule-action .cta').click()
    assert d.find_element(By.ID,'interest').get_attribute('value')=='Classes'
    for interest in ['Classes','Studio Hire','Wedding First Dance','Hen Party']:
        from urllib.parse import quote
        d.get(base+'contact.html?interest='+quote(interest))
        assert d.find_element(By.ID,'interest').get_attribute('value')==interest
    assert not d.execute_script('return document.getElementById("enquiry-form").checkValidity()')
    for field,value in [('name','Test Visitor'),('email','visitor@example.com'),('message','Browser validation only; never submitted.')]:
        d.find_element(By.ID,field).send_keys(value)
    assert d.execute_script('return document.getElementById("enquiry-form").checkValidity()')
    # Mock both outcomes; never send a real enquiry.
    d.execute_script('window.fetch=async()=>({ok:false})')
    d.find_element(By.CSS_SELECTOR,'[type="submit"]').click()
    wait.until(lambda _:'couldn’t confirm' in d.find_element(By.ID,'form-status').text)
    assert d.find_element(By.ID,'message').get_attribute('value')=='Browser validation only; never submitted.'
    assert d.find_element(By.CSS_SELECTOR,'[type="submit"]').is_enabled()
    d.execute_script('window.fetch=async()=>({ok:true})')
    d.find_element(By.CSS_SELECTOR,'[type="submit"]').click()
    wait.until(lambda _:d.current_url.endswith('/thanks.html'))
    d.get(base+'index.html')
    wait.until(lambda _:d.execute_script('return !document.getElementById("hero-video").paused'))
    d.find_element(By.CSS_SELECTOR,'.video-toggle').click()
    assert d.execute_script('return document.getElementById("hero-video").paused')
    assert d.find_element(By.CSS_SELECTOR,'.video-toggle').get_attribute('aria-label')=='Play video'
    d.find_element(By.CSS_SELECTOR,'.video-toggle').click()
    wait.until(lambda _:d.execute_script('return !document.getElementById("hero-video").paused'))
    results.append('PASS: menu focus/scroll/Escape/resize, form preselection/validation, mocked submission error/success, and video pause/play under production CSP. No live submission made.')
    print(results[-1],flush=True)
    (shots/'results.json').write_text(json.dumps(results,indent=2))
finally:
    d.quit()
# Reduced motion: poster remains visible and no video source is downloaded.
options.set_preference('ui.prefersReducedMotion',1)
d=webdriver.Firefox(options=options)
try:
    d.get(base+'index.html')
    assert d.execute_script('return matchMedia("(prefers-reduced-motion: reduce)").matches')
    assert d.execute_script('return document.getElementById("hero-video").paused && !document.querySelector("video source").hasAttribute("src")')
finally:d.quit()
# Without JavaScript the navigation and native Netlify form are still usable.
options.set_preference('javascript.enabled',False)
d=webdriver.Firefox(options=options)
try:
    d.set_window_size(390,844);d.get(base+'contact.html')
    assert d.find_element(By.CSS_SELECTOR,'.nav-desktop').is_displayed()
    assert not d.find_element(By.ID,'menuToggle').is_displayed()
    assert d.find_element(By.ID,'enquiry-form').get_attribute('method')=='post'
    print('PASS: reduced-motion video loading and no-JavaScript navigation/form fallback.',flush=True)
finally:
    d.quit();server.shutdown()
