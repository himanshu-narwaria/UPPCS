import os

HERE = os.path.dirname(os.path.abspath(__file__))
POLITY_DIR = os.path.abspath(os.path.join(HERE, "..", "polity"))

with open(os.path.join(HERE, "fonts_embedded.css"), "r", encoding="utf-8") as f:
    fonts_css = f.read()

MOBILE_CSS_EXTRA = """
html, body {
  overflow-x: hidden;
  max-width: 100vw;
}
.top {
  max-width: 100%;
  box-sizing: border-box;
}
@media (max-width:860px){
  .top { gap: 8px; padding: 0 10px; }
  #menu { width: 36px; height: 36px; flex: none; }
  #q { min-width: 50px; height: 36px; font-size: 13.5px; }
  .tog { font-size: 12.5px; gap: 4px; min-height: 36px; }
  main { max-width: 100%; box-sizing: border-box; overflow-x: hidden; }
}
@media (max-width:400px){
  .top { gap: 6px; padding: 0 6px; }
  #menu { width: 32px; height: 32px; }
  #q { min-width: 40px; font-size: 12px; padding: 0 6px; }
  .tog { font-size: 11.5px; gap: 3px; }
}
"""

H72_CSS_EXTRA = """
.prog-box{margin:16px 0 20px;padding:14px 16px;background:var(--soft);border:1px solid var(--line);border-radius:10px}
.pb-lbl{display:flex;justify-content:space-between;font-weight:600;font-size:14px;margin-bottom:8px}
.pbar{height:10px;background:var(--line);border-radius:5px;overflow:hidden}
.pbf{height:100%;width:0;background:var(--acc);border-radius:5px;transition:width .2s}
.btn.is, .btn.done, .btn-tick.is, .btn-tick.done {
  background: var(--acc) !important;
  color: #fff !important;
  border-color: var(--acc) !important;
}
"""

# 1. Full Notes Style
with open(os.path.join(POLITY_DIR, "template_full_style.css"), "r", encoding="utf-8") as f:
    polity_full_css = f.read()

current_full_css = polity_full_css.replace(
    'font:16.5px/1.55 system-ui,-apple-system,"Segoe UI","Nirmala UI",Roboto,Arial,sans-serif',
    'font:16.5px/1.55 "Atkinson Hyperlegible Next","Segoe UI",system-ui,Arial,"Nirmala UI",sans-serif'
).replace(
    'h1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}',
    'h1,h2,.brand{font-family:"Lexend","Segoe UI",system-ui,sans-serif}\nh1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}'
)
full_css = fonts_css + "\n" + current_full_css + "\n" + MOBILE_CSS_EXTRA
with open(os.path.join(HERE, "template_full_style.css"), "w", encoding="utf-8") as f:
    f.write(full_css)

# 2. Quick Notes Style
with open(os.path.join(POLITY_DIR, "template_quick_style.css"), "r", encoding="utf-8") as f:
    polity_quick_css = f.read()

current_quick_css = polity_quick_css.replace(
    'font:16.5px/1.55 system-ui,-apple-system,"Segoe UI","Nirmala UI",Roboto,Arial,sans-serif',
    'font:16.5px/1.55 "Atkinson Hyperlegible Next","Segoe UI",system-ui,Arial,"Nirmala UI",sans-serif'
).replace(
    'h1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}',
    'h1,h2,.brand{font-family:"Lexend","Segoe UI",system-ui,sans-serif}\nh1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}'
)
quick_css = fonts_css + "\n" + current_quick_css + "\n" + MOBILE_CSS_EXTRA
with open(os.path.join(HERE, "template_quick_style.css"), "w", encoding="utf-8") as f:
    f.write(quick_css)

# 3. 72h Plan Style
with open(os.path.join(POLITY_DIR, "template_72h_style.css"), "r", encoding="utf-8") as f:
    polity_72h_css = f.read()

current_72h_css = polity_72h_css.replace(
    'font:16.5px/1.55 system-ui,-apple-system,"Segoe UI","Nirmala UI",Roboto,Arial,sans-serif',
    'font:16.5px/1.55 "Atkinson Hyperlegible Next","Segoe UI",system-ui,Arial,"Nirmala UI",sans-serif'
).replace(
    'h1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}',
    'h1,h2,.brand{font-family:"Lexend","Segoe UI",system-ui,sans-serif}\nh1,h2{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}'
)
h72_css = fonts_css + "\n" + current_72h_css + "\n" + MOBILE_CSS_EXTRA + "\n" + H72_CSS_EXTRA
with open(os.path.join(HERE, "template_72h_style.css"), "w", encoding="utf-8") as f:
    f.write(h72_css)

# 4. Full Notes JS
with open(os.path.join(POLITY_DIR, "template_full_js.html"), "r", encoding="utf-8") as f:
    polity_full_js = f.read()

current_full_js = polity_full_js.replace(
    'Indian Polity Full Notes', 'Current Affairs Full Notes'
).replace(
    'polgovup-imp', 'caup-imp'
).replace(
    'polgov-theme', 'ca-theme'
).replace(
    'polgov-practice', 'ca-practice'
)
with open(os.path.join(HERE, "template_full_js.html"), "w", encoding="utf-8") as f:
    f.write(current_full_js)

# 5. Quick Notes JS
with open(os.path.join(POLITY_DIR, "template_quick_js.html"), "r", encoding="utf-8") as f:
    polity_quick_js = f.read()

current_quick_js = polity_quick_js.replace(
    'Indian Polity Quick Revision', 'Current Affairs Quick Revision'
).replace(
    'polgovup-imp', 'caup-imp'
).replace(
    'polgov-theme', 'ca-theme'
)
with open(os.path.join(HERE, "template_quick_js.html"), "w", encoding="utf-8") as f:
    f.write(current_quick_js)

# 6. 72h Plan JS
CURRENT_72H_JS = """<script>(function(){
try {
  var $=function(s,r){return(r||document).querySelector(s)},$$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
  var pqdEl = $("#pqd");
  var D = pqdEl ? JSON.parse(pqdEl.textContent) : {},side=$("#side"),scrim=$("#scrim"),q=$("#q"),last="home",done=[];
  try{done=JSON.parse(localStorage.getItem("ca72-done")||"[]")}catch(e){}
  function save(){try{localStorage.setItem("ca72-done",JSON.stringify(done))}catch(e){}}
  function paint(){
    $$(".side a[data-v]").forEach(function(a){a.classList.toggle("ok",done.indexOf(+a.dataset.v.slice(1))>=0)});
    $$("[data-done],[data-h],.btn-tick").forEach(function(b){
      var n = +(b.dataset.done || b.dataset.h);
      if (!n) return;
      var on = done.indexOf(n) >= 0;
      b.classList.toggle("is", on);
      b.classList.toggle("done", on);
      b.textContent = on ? "Hour " + n + " done ✓" : "Mark hour " + n + " done";
    });
    var pct = Math.round(100 * done.length / 72);
    var prog = $("#prog"); if (prog) prog.textContent = done.length + " of 72 hours done";
    var progTxt = $("#prog-txt"); if (progTxt) progTxt.textContent = done.length + " / 72 hours (" + pct + "%)";
    var bar = $("#bar"); if (bar) bar.style.width = pct + "%";
    var pb = $("#pb"); if (pb) pb.style.width = pct + "%";
    var nx = 1; while(done.indexOf(nx) >= 0 && nx < 72) nx++;
    var c = $("#cont"); if (c) { c.href = "#h" + nx; c.textContent = (done.length ? "Continue with hour " : "Start with hour ") + nx + " →"; }
  }
  function drawer(o){if(side)side.classList.toggle("open",o);if(scrim)scrim.classList.toggle("on",o)}
  function fill(v){
    if(!v) return;
    var ol=$(".pq",v);if(!ol||ol.dataset.f)return;ol.dataset.f=1;var st={d:0,r:0,t:0};
    ol.innerHTML=ol.dataset.q.split(",").map(function(i){
      var x=D[i];if(!x)return"";st.t++;
      return'<li data-i="'+i+'"><div class="meta">'+x.e+'</div><div class="stem">'+x.s+'</div><div class="opts">'+x.o.map(function(o,j){return'<button type="button" class="o" data-j="'+j+'">('+"abcde"[j]+') '+o+'</button>'}).join("")+'</div><div class="fb" hidden></div></li>';
    }).join("");
    var sc=$(".score",v);
    function showScore(){if(sc)sc.textContent=st.t+" questions · answered "+st.d+" · correct "+st.r+(st.d?" ("+Math.round(100*st.r/st.d)+"%)":"")}
    showScore();
    ol.addEventListener("click",function(e){
      var b=e.target.closest(".o");if(!b||b.disabled)return;
      var li=b.closest("li"),x=D[li.dataset.i],j=+b.dataset.j,ok=x.k.indexOf(j)>=0;
      $$(".o",li).forEach(function(o,n){o.disabled=true;if(x.k.indexOf(n)>=0)o.classList.add("ok");else if(n===j)o.classList.add("no")});
      var fb=$(".fb",li);
      if(fb){
        fb.hidden=false;
        fb.innerHTML='<b class="'+(ok?"ok":"no")+'">'+(ok?"Correct.":"Not correct.")+"</b> "+x.f+(x.n>1?' <span class="p up">UPPSC ×'+x.n+"</span>":"")+"";
      }
      st.d++;if(ok)st.r++;showScore();
    });
  }
  function show(id){
    $$(".view").forEach(function(v){v.classList.toggle("on",v.id===id)});
    $$(".side a").forEach(function(a){a.classList.toggle("on",a.dataset.v===id)});
    if(id!=="results")last=id;
    var v=$("#"+id);if(v)fill(v);
    document.title=((v&&v.dataset.n)?"Hour "+v.dataset.n+" · ":"")+"Current Affairs in 72h";
    var a=$(".side a.on");if(a&&a.scrollIntoView)a.scrollIntoView({block:"nearest"});
  }
  function route(){
    var h=location.hash.slice(1)||"home";
    if(!document.getElementById(h))h="home";
    if(q)q.value="";
    show(h);drawer(false);window.scrollTo(0,0);
  }
  document.addEventListener("click",function(e){
    var b=e.target.closest("[data-done],[data-h],.btn-tick");if(!b)return;
    var n=+(b.dataset.done || b.dataset.h);
    if(!n) return;
    var i=done.indexOf(n);
    if(i>=0)done.splice(i,1);else done.push(n);
    save();paint();
  });
  var idx=null;
  if (q) {
    q.addEventListener("input",function(){
      var s=q.value.trim().toLowerCase();if(s.length<2){show(last);return}
      if(!idx){idx=[];$$(".view[data-n]").forEach(function(v){$$(".pt",v).forEach(function(p){var c=p.cloneNode(true);$$(".ps,.src",c).forEach(function(x){x.remove()});var t=c.textContent.replace(/\\s+/g," ").trim();idx.push({n:v.dataset.n,t:t,l:t.toLowerCase()})})})}
      var w=s.split(/\\s+/),hits=idx.filter(function(x){return w.every(function(k){return x.l.indexOf(k)>=0})}).slice(0,60);
      var rt=$("#rt");if(rt)rt.textContent=hits.length+" results";
      var rl=$("#rl");if(rl)rl.innerHTML=hits.map(function(x){return'<a href="#h'+x.n+'">'+String(x.t).replace(/[&<>]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;"}[c]})+" <small>Hour "+x.n+"</small></a>"}).join("")||"<p>Nothing found.</p>";
      show("results");
    });
  }
  var menu = $("#menu");
  if(menu&&side)menu.onclick=function(){drawer(!side.classList.contains("open"))};
  if(scrim)scrim.onclick=function(){drawer(false)};
  var dark = $('#dark');
  if (dark) {
    var isDark = localStorage.getItem('ca-theme') === 'dark' || (!localStorage.getItem('ca-theme') && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    dark.checked = isDark;
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    dark.addEventListener('change', function () {
      var theme = dark.checked ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', theme);
      try{localStorage.setItem('ca-theme', theme)}catch(e){}
    });
  }
  window.addEventListener("hashchange",route);
  paint();
  route();
} catch (err) {
  console.error("72h plan init error:", err);
  var hm = document.getElementById("home");
  if (hm) hm.classList.add("on");
}
})();</script>"""

with open(os.path.join(HERE, "template_72h_js.html"), "w", encoding="utf-8") as f:
    f.write(CURRENT_72H_JS)

print("Created all CSS and JS templates with offline fonts, keys, and mobile fixes for Current Affairs!")