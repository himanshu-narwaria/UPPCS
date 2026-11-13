"""Headless-Chrome smoke test of Polity-UPPCS.html: python -I browser_test.py"""
import subprocess, os, urllib.parse, re, html, tempfile
W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(W, '..', '..', '..', 'Indian_Polity_and_Governance', 'Polity-UPPCS.html'))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
T = tempfile.mkdtemp(prefix='polity-uppcs-')
base = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + os.path.join(T, 'prof'), '--allow-file-access-from-files']
url = lambda p, h='': 'file:///' + urllib.parse.quote(p.replace('\\', '/')) + h
src = open(OUT, encoding='utf-8').read()
probe = '''<script>window.__e=[];onerror=function(m,u,l){__e.push(m+' @'+l)};addEventListener('load',function(){setTimeout(function(){
var $$=function(s){return [].slice.call(document.querySelectorAll(s))},R={err:__e,over:[]},ids=$$('.view').map(function(v){return v.id}),i=0,vis=function(e){return e.offsetParent!==null};
(function step(){if(i<ids.length){location.hash=ids[i++];setTimeout(function(){var sw=document.documentElement.scrollWidth;if(sw>innerWidth)R.over.push(location.hash+':'+sw);step()},15);return}
 location.hash='c13';setTimeout(function(){
  R.all=$$('#c13 .f').filter(vis).length;var only=document.getElementById('only');only.click();R.rep=$$('#c13 .f').filter(vis).length;R.hot=$$('#c13 .f.hot').length;only.click();
  var q=document.getElementById('q');q.value='article 32';q.dispatchEvent(new Event('input'));R.search=document.getElementById('rt').textContent;
  var a=document.querySelector('#rl a');if(a)a.click();R.after=($$('.view.on')[0]||{}).id;
  R.views=ids.length;R.repRows=$$('#repeated .rows li').length;
  R.badLinks=$$('a[href^="#"]').filter(function(a){var h=a.getAttribute('href').slice(1);return h&&!document.getElementById(h)}).length;
  R.dup=$$('[id]').length-new Set($$('[id]').map(function(e){return e.id})).size;R.ext=$$('script[src],link[href],img').length;R.iw=innerWidth;
  var o='RESULT'+JSON.stringify(R)+'ENDRESULT';parent.postMessage(o,'*');document.body.insertAdjacentHTML('beforeend','<pre>'+o.replace(/</g,'&lt;')+'</pre>')},80)})()},400)})</script>'''
t = os.path.join(T, 'p.html'); open(t, 'w', encoding='utf-8').write(src.replace('<head>', '<head>' + probe, 1))
o = subprocess.run(base + ['--window-size=1280,900', '--virtual-time-budget=15000', '--dump-dom', url(t)], capture_output=True, timeout=200).stdout.decode('utf-8', 'replace')
m = re.search(r'RESULT(\{.*?\})ENDRESULT', o, re.S); print('desktop', html.unescape(m.group(1)) if m else 'NO RESULT')
wp = os.path.join(T, 'w.html')
open(wp, 'w', encoding='utf-8').write('<!doctype html><body><iframe src="p.html" width="360" height="800"></iframe><pre id="r"></pre><script>addEventListener("message",function(e){document.getElementById("r").textContent=e.data})</script>')
o = subprocess.run(base + ['--window-size=800,900', '--virtual-time-budget=20000', '--dump-dom', url(wp)], capture_output=True, timeout=200).stdout.decode('utf-8', 'replace')
m = re.search(r'RESULT(\{.*?\})ENDRESULT', o, re.S); print('phone', html.unescape(m.group(1))[:160] if m else 'NO RESULT')
shot = os.path.join(T, 'c13.png')
subprocess.run(base + ['--window-size=1280,1100', '--screenshot=' + shot, '--virtual-time-budget=3000', url(OUT, '#c13')], capture_output=True, timeout=120)
print('screenshot', shot)
