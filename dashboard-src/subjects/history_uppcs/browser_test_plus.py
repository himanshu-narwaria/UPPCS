"""Headless-Chrome test of History-UPPCS-Plus.html: python -I browser_test_plus.py"""
import subprocess, os, urllib.parse, re, html, tempfile
W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(W, '..', '..', '..', 'Indian_History_Part_2', 'History-UPPCS-Plus.html'))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
T = tempfile.mkdtemp(prefix='history-plus-')
base = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + os.path.join(T, 'prof'), '--allow-file-access-from-files']
url = lambda p, h='': 'file:///' + urllib.parse.quote(p.replace('\\', '/')) + h
src = open(OUT, encoding='utf-8').read()
probe = '''<script>window.__e=[];onerror=function(m,u,l){__e.push(m+' @'+l)};addEventListener('load',function(){setTimeout(function(){
var $=function(s){return document.querySelector(s)},$$=function(s){return [].slice.call(document.querySelectorAll(s))},R={err:__e,over:[]},ids=$$('.view').map(function(v){return v.id}),i=0,vis=function(e){return e.offsetParent!==null};
(function step(){if(i<ids.length){location.hash=ids[i++];setTimeout(function(){var sw=document.documentElement.scrollWidth;if(sw>innerWidth)R.over.push(location.hash+':'+sw);step()},15);return}
 location.hash='c9';setTimeout(function(){
  R.all=$$('#c9 .f').filter(vis).length;
  $('#tRep').click();R.rep=$$('#c9 .f').filter(vis).length;$('#tRep').click();
  var f=$('#c9 .f');f.querySelector('.tk').click();R.known=$('#sKnown').textContent;R.ring=$('#c9 .ring').textContent;
  $('#tWeak').click();R.weak=$$('#c9 .f').filter(vis).length;$('#tWeak').click();
  $('#tRecall').click();var b=$('#c9 .f b');R.hidden=getComputedStyle(b).color;b.click();R.shown=b.classList.contains('shown');$('#tRecall').click();
  $('#tFocus').click();R.focusTopics=$$('#c9 .topic').filter(vis).length;R.fpos=$('#fPos').textContent;$('#fNext').click();R.fpos2=$('#fPos').textContent;$('#tFocus').click();
  var tb=$('.tlb');tb.click();R.tl=tb.closest('.topic').querySelectorAll('.tl li').length;R.tlHides=!vis(tb.closest('.topic').querySelector('.fl'));tb.click();
  $('#q').value='ashoka';$('#q').dispatchEvent(new Event('input'));R.search=$('#rt').textContent;
  location.hash='cards';setTimeout(function(){
   R.card=$('#fcFact').textContent.slice(0,60);R.cpos=$('#fcPos').textContent;R.cardHidden=$('#fc').classList.contains('hide');$('#fcShow').click();R.cardShown=!$('#fc').classList.contains('hide');
   $('#fcKnow').click();R.cpos2=$('#fcPos').textContent;R.known2=$('#sKnown').textContent;
   $('[data-quiz="9"]').click();location.hash='quiz';setTimeout(function(){
    R.qn=$$('#qzList li').length;R.qch=$('#qzCh').value;var D=JSON.parse($('#quizd').textContent);
    var li=$('#qzList li');li.querySelector('.qo button').click();R.qscore=$('#qzScore').textContent;R.qfb=li.querySelector('.qf').textContent.slice(0,50);
    R.badLinks=$$('a[href^="#"]').filter(function(a){var h=a.getAttribute('href').slice(1);return h&&!document.getElementById(h)}).length;
    R.dup=$$('[id]').length-new Set($$('[id]').map(function(e){return e.id})).size;R.ext=$$('script[src],link[href],img').length;R.iw=innerWidth;
    var o='RESULT'+JSON.stringify(R)+'ENDRESULT';parent.postMessage(o,'*');document.body.insertAdjacentHTML('beforeend','<pre>'+o.replace(/</g,'&lt;')+'</pre>')},60)},60)},80)})()},400)})</script>'''
t = os.path.join(T, 'p.html'); open(t, 'w', encoding='utf-8').write(src.replace('<head>', '<head>' + probe, 1))
o = subprocess.run(base + ['--window-size=1280,900', '--virtual-time-budget=20000', '--dump-dom', url(t)], capture_output=True, timeout=240).stdout.decode('utf-8', 'replace')
m = re.search(r'RESULT(\{.*?\})ENDRESULT', o, re.S); print('desktop', html.unescape(m.group(1)) if m else 'NO RESULT')
wp = os.path.join(T, 'w.html')
open(wp, 'w', encoding='utf-8').write('<!doctype html><body><iframe src="p.html" width="360" height="800"></iframe><pre id="r"></pre><script>addEventListener("message",function(e){document.getElementById("r").textContent=e.data})</script>')
o = subprocess.run(base + ['--window-size=800,900', '--virtual-time-budget=25000', '--dump-dom', url(wp)], capture_output=True, timeout=240).stdout.decode('utf-8', 'replace')
m = re.search(r'RESULT(\{.*?\})ENDRESULT', o, re.S); print('phone', re.findall(r'"over":[[^]]*]', html.unescape(m.group(1))) if m else 'NO RESULT')
for name, frag in [('home', '#home'), ('c9', '#c9'), ('cards', '#cards')]:
    subprocess.run(base + ['--window-size=1280,1150', '--screenshot=' + os.path.join(T, name + '.png'), '--virtual-time-budget=3000', url(OUT, frag)], capture_output=True, timeout=120)
print('shots', T)
