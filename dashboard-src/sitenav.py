"""Add site-wide navigation to every HTML page in the project.

Each page gets, at run time:
  * a global menu ("Subjects" dropdown + Home) inside its existing sticky header,
  * breadcrumbs: Home › Subject › Notes type › current chapter or hour,
  * a "Related topics" box with Previous/Next links at the end of every chapter or hour,
    linking the same chapter in the subject's other note types and in its 72-hour plan.

Run through build_dashboard.py (it calls inject_all()). The injected block sits between
<!--sx:start--> and <!--sx:end--> markers plus <style id="sx-style">, and is replaced on
every run, so running again never duplicates it. A file is rewritten only when its block
changes. Standard library only.
"""
import html
import json
import os
import re
import sys
from urllib.parse import quote

import build_dashboard as bd

ROOT = bd.ROOT
HOME = "study-dashboard.html"
SKIP_DIRS = {".git", "dashboard-src", "node_modules", ".vercel"}
FORMAT_LABEL = {"full": "Full notes", "quick": "Quick notes", "plan": "72-hour plan"}


def rootrel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def enc(p):
    return "/".join(quote(part) for part in p.split("/"))


def all_pages():
    out = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        out += [os.path.join(dirpath, f) for f in sorted(files) if f.endswith(".html")]
    return out


def page_title(path):
    with open(path, encoding="utf-8") as f:
        head = f.read(20000)
    m = re.search(r"<title>(.*?)</title>", head, re.S)
    return html.unescape(m.group(1)).strip() if m else os.path.basename(path)


def site_map():
    """Subjects with their files, chapters and hours, plus every other page as 'Other notes'."""
    subjects, assigned = [], {HOME}
    for sub in bd.SUBJECTS:
        folder = sub["folder"]
        full = bd.find_one(folder, ["*-uppsc-notes.html", "*-full-notes.html"])
        quick = bd.find_one(folder, ["*quick-notes.html"], required=False)
        plan = bd.find_one(folder, ["*-in-72h.html"])
        F, P = bd.parse_full(full), bd.parse_72h(plan)
        ch_hours = bd.chapter_hours(F["chapters"], P, os.path.basename(plan))
        hour_ch = {}
        for n, hrs in ch_hours.items():
            for h in hrs:
                hour_ch.setdefault(h, []).append(n)
        files = {"full": rootrel(full), "plan": rootrel(plan)}
        quick_ok = set()
        if quick:
            files["quick"] = rootrel(quick)
            Q = bd.parse_quick(quick)
            for n, c in F["chapters"].items():
                if n in Q["chapters"] and bd.norm(Q["chapters"][n]["title"]) == bd.norm(c["title"]):
                    quick_ok.add(n)
                else:
                    print(f"sitenav warning: {sub['name']} chapter {n} differs between full and quick notes; no cross-link made")
        folder_html = {rootrel(x) for x in all_pages() if rootrel(x).startswith(folder + "/") and rootrel(x).count("/") == folder.count("/") + 1}
        for extra in sorted(folder_html - set(files.values())):
            print(f"sitenav warning: {extra} is in the {sub['name']} folder but is not its full notes, quick notes or 72h plan; it is listed under Other notes")
        assigned.update(files.values())
        subjects.append({
            "key": sub["key"], "name": sub["name"], "hindi": sub["hindi"], "files": files,
            "fullLayout": F["layout"], "repeated": "repeated" if F["layout"] == "views" else "dash-repeats",
            "chapters": [{"n": n, "t": c["title"], "h": ch_hours[n], "q": n in quick_ok} for n, c in F["chapters"].items()],
            "lastHour": P["hours"][-1][0],
            "hourCh": {str(h): v for h, v in sorted(hour_ch.items())},
            "phases": [[p, v[0][0], v[-1][0]] for p, v in P["phases"].items()],
        })
    others = [p for p in all_pages() if rootrel(p) not in assigned]
    titles = [page_title(p) for p in others]
    archive = []
    for p, t in zip(others, titles):
        label = t
        if titles.count(t) > 1:
            label = f"{t} ({os.path.splitext(os.path.basename(p))[0]})"
        archive.append({"path": rootrel(p), "t": label, "dir": os.path.dirname(rootrel(p)) or "project folder"})
    return {"home": HOME, "subjects": subjects, "archive": archive}


def context_for(path, smap):
    rp = rootrel(path)
    if rp == HOME:
        return {"kind": "home", "subject": None}
    for s in smap["subjects"]:
        for kind, fp in s["files"].items():
            if fp == rp:
                return {"kind": kind, "subject": s["key"]}
    return {"kind": "archive", "subject": None}


CSS = r"""
.sx-nav{display:inline-flex;align-items:center;gap:6px;flex:0 0 auto}
.sx-nav a,.sx-nav button{font:600 13.5px/1 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:#1d2b45;background:#fff;border:1.5px solid #cfd6e3;border-radius:8px;height:34px;padding:0 10px;display:inline-flex;align-items:center;gap:5px;cursor:pointer;text-decoration:none;white-space:nowrap}
.sx-nav a:hover,.sx-nav button:hover,.sx-nav button[aria-expanded="true"]{background:#eef3fb;border-color:#1f5f8b}
.sx-nav a:focus-visible,.sx-nav button:focus-visible,.sx-panel a:focus-visible,.sx-crumbs a:focus-visible,.sx-rel a:focus-visible{outline:2px solid #1f5f8b;outline-offset:2px}
.sx-panel{position:fixed;right:12px;z-index:1000;width:min(760px,calc(100vw - 24px));max-height:calc(100vh - 90px);overflow:auto;background:#fff;color:#16202e;border:1.5px solid #cfd6e3;border-radius:12px;box-shadow:0 16px 44px rgba(20,30,50,.22);padding:14px 16px;font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.sx-panel[hidden]{display:none}
.sx-panel .sx-top{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:0 0 10px;padding-bottom:10px;border-bottom:1px solid #e3e7ee}
.sx-panel .sx-top a{font-weight:700;color:#1f5f8b;text-decoration:none}
.sx-panel .sx-top small{color:#5b6577}
.sx-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px 18px}
.sx-col h4{margin:0 0 4px;font:700 15px/1.3 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.sx-col h4 a{color:#1f5f8b;text-decoration:none}
.sx-col h4 small{display:block;font-weight:400;color:#5b6577;font-size:12.5px}
.sx-col ul{list-style:none;margin:0;padding:0}
.sx-col li{margin:0}
.sx-col li a,.sx-col li span{display:block;padding:5px 8px;border-radius:6px;color:#16202e;text-decoration:none}
.sx-col li a:hover{background:#eef3fb}
.sx-col li a[aria-current="page"]{background:#fff3c4;font-weight:700}
.sx-col li span{color:#8a93a3}
.sx-col.sx-arch{grid-column:1/-1;border-top:1px solid #e3e7ee;padding-top:10px}
.sx-col.sx-arch ul{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0 18px}
.sx-col.sx-arch small{color:#5b6577;font-size:12px}
.sx-crumbs{font:13px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:#5b6577;margin:0 0 14px;display:flex;flex-wrap:wrap;gap:2px 0;align-items:center}
.sx-crumbs a{color:#1f5f8b;text-decoration:none}
.sx-crumbs a:hover{text-decoration:underline}
.sx-crumbs .sx-sep,.sx-pre .sx-sep{margin:0 6px;color:#9aa3b3}
.sx-crumbs [aria-current]{color:#16202e;font-weight:600}
.sx-pre a{text-decoration:none}
.sx-rel{margin:26px 0 8px;padding:14px 16px;border:1.5px solid #dbe1ea;border-radius:10px;background:#f7f9fc;font:14.5px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:#16202e}
.sx-rel h3{margin:0 0 8px;font:700 13px/1.2 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#5b6577}
.sx-rel ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px 8px}
.sx-rel li a{display:inline-block;padding:4px 10px;border:1px solid #cfd6e3;border-radius:999px;background:#fff;color:#1f5f8b;text-decoration:none}
.sx-rel li a:hover{background:#eef3fb}
.sx-pn{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:12px;padding-top:10px;border-top:1px solid #dbe1ea}
.sx-pn a{color:#1f5f8b;text-decoration:none;font-weight:600;max-width:48%}
.sx-pn a:hover{text-decoration:underline}
.sx-pn .sx-nx{margin-left:auto;text-align:right}
.sx-bar{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px max(16px,env(safe-area-inset-left,0px));background:#fff;border-bottom:1.5px solid #e3e7ee}
.sx-bar .sx-brand{font:700 16px/1.2 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:#16202e;text-decoration:none}
@media (max-width:600px){.sx-nav .sx-lbl{display:none}.sx-nav a,.sx-nav button{padding:0 8px;font-size:13px}.top .brand{display:none}header .sx-nav a{display:none}}
@media print{.sx-nav,.sx-panel,.sx-rel,.sx-bar,.sx-crumbs,.sx-pre{display:none!important}}
"""

JS = r"""
(function(){
var D=JSON.parse(document.getElementById("sx-data").textContent),C=D.ctx,B=D.base;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function enc(p){return p.split("/").map(encodeURIComponent).join("/")}
function L(path,anchor){if(path===C.file)return "#"+(anchor||"");return B+enc(path)+(anchor?"#"+anchor:"")}
var S=D.subjects,sub=null;S.forEach(function(s){if(s.key===C.subject)sub=s});
var FL={full:"Full notes",quick:"Quick notes",plan:"72-hour plan"};
var SEP='<span class="sx-sep" aria-hidden="true">›</span>';

/* 1. global menu */
var panel=document.createElement("nav");panel.className="sx-panel";panel.id="sx-panel";panel.hidden=true;panel.setAttribute("aria-label","All subjects and notes");
var cols=S.map(function(s){
 var li=["full","quick","plan"].map(function(k){var p=s.files[k];
  if(!p)return '<li><span>'+FL[k]+' (not made yet)</span></li>';
  return '<li><a href="'+L(p)+'"'+(p===C.file?' aria-current="page"':"")+'>'+FL[k]+'</a></li>'}).join("");
 return '<div class="sx-col"><h4><a href="'+L(D.home,s.key)+'">'+esc(s.name)+'<small>'+esc(s.hindi)+'</small></a></h4><ul>'+li+'</ul></div>'}).join("");
var arch=D.archive.length?'<div class="sx-col sx-arch"><h4>Other notes</h4><ul>'+D.archive.map(function(a){return '<li><a href="'+L(a.path)+'"'+(a.path===C.file?' aria-current="page"':"")+'>'+esc(a.t)+' <small>· '+esc(a.dir)+'</small></a></li>'}).join("")+'</ul></div>':"";
panel.innerHTML='<div class="sx-top"><a href="'+L(D.home)+'">⌂ Study dashboard</a><small>Esc to close</small></div><div class="sx-cols">'+cols+arch+'</div>';
document.body.appendChild(panel);
var bar=document.createElement("span");bar.className="sx-nav";
bar.innerHTML=(C.kind==="home"?"":'<a href="'+L(D.home)+'" title="Study dashboard" aria-label="Study dashboard home">⌂<span class="sx-lbl">Home</span></a>')+
 '<button type="button" aria-expanded="false" aria-controls="sx-panel">Subjects ▾</button>';
var header=document.querySelector("header.topbar, header.top");
if(C.kind==="home"||!header){var hb=document.createElement("div");hb.className="sx-bar";hb.innerHTML='<a class="sx-brand" href="'+L(D.home)+'">UPPSC Study</a>';hb.appendChild(bar);document.body.insertBefore(hb,document.body.firstChild);header=hb}
else{var anchor=header.querySelector("#menu, #menuBtn");if(anchor&&anchor.nextSibling)header.insertBefore(bar,anchor.nextSibling);else header.insertBefore(bar,header.firstChild)}
var btn=bar.querySelector("button");
function place(){var r=header.getBoundingClientRect();panel.style.top=Math.max(8,r.bottom+6)+"px";panel.style.maxHeight="calc(100vh - "+(Math.max(8,r.bottom+6)+12)+"px)"}
function openP(o){panel.hidden=!o;btn.setAttribute("aria-expanded",o?"true":"false");if(o){place();var a=panel.querySelector("a");if(a)a.focus()}}
btn.addEventListener("click",function(e){e.stopPropagation();openP(panel.hidden)});
document.addEventListener("click",function(e){if(!panel.hidden&&!panel.contains(e.target)&&!bar.contains(e.target))openP(false)});
document.addEventListener("keydown",function(e){if(e.key==="Escape"&&!panel.hidden){openP(false);btn.focus()}});
panel.addEventListener("click",function(e){if(e.target.closest("a"))openP(false)});
/* keep keyboard users inside the open menu: leaving it closes it */
panel.addEventListener("focusout",function(e){var t=e.relatedTarget;if(!panel.hidden&&t&&!panel.contains(t)&&!bar.contains(t))openP(false)});
panel.addEventListener("keydown",function(e){if(e.key!=="Tab")return;var a=panel.querySelectorAll("a");if(!a.length)return;
 if(e.shiftKey&&document.activeElement===a[0]){e.preventDefault();btn.focus()}})
window.addEventListener("resize",function(){if(!panel.hidden)place()});

/* 2. breadcrumbs */
var pageName=document.title;D.archive.forEach(function(a){if(a.path===C.file)pageName=a.t});
var head=C.kind==="archive"?'<a href="'+L(D.home)+'">Home</a>'+SEP+'<a href="'+L(D.home,"others")+'">Other notes</a>'+SEP:
 sub?'<a href="'+L(D.home)+'">Home</a>'+SEP+'<a href="'+L(D.home,sub.key)+'">'+esc(sub.name)+'</a>'+SEP:"";
var shellCrumbs=document.getElementById("crumbs");
if(C.kind!=="home"&&shellCrumbs&&shellCrumbs.classList.contains("crumbs")){
 var pre=head+'<a href="#top">'+esc(sub?FL[C.kind]:pageName)+'</a>'+SEP;
 var mo=new MutationObserver(fix);
 function drop(test){var n=shellCrumbs.firstChild&&shellCrumbs.firstChild.nextSibling;if(n&&n.nodeType===1&&n.tagName==="A"&&test(n.textContent.trim())){var s=n.nextSibling;n.remove();if(s&&s.nodeType===1&&s.classList.contains("sep"))s.remove();return true}return false}
 function fix(){if(shellCrumbs.firstChild&&shellCrumbs.firstChild.className==="sx-pre")return;mo.disconnect();var sp=document.createElement("span");sp.className="sx-pre";sp.innerHTML=pre;shellCrumbs.insertBefore(sp,shellCrumbs.firstChild);
  /* the page's own trail starts "Contents › Subject"; the prefix already says both */
  drop(function(t){return t==="Contents"});if(sub)drop(function(t){return t.replace(/&/g,"and")===sub.name.replace(/&/g,"and")});
  var last=shellCrumbs.lastChild;if(last&&last.nodeType===1&&last.classList&&last.classList.contains("sep"))last.remove();
  if(!sp.nextSibling&&sp.lastChild&&sp.lastChild.nodeType===1&&sp.lastChild.classList.contains("sx-sep"))sp.lastChild.remove();
  mo.observe(shellCrumbs,{childList:true})}
 fix();
}else if(C.kind!=="home"){
 var main=document.querySelector("main");
 if(main){var cr=document.createElement("nav");cr.className="sx-crumbs";cr.setAttribute("aria-label","Breadcrumb");main.insertBefore(cr,main.firstChild);
  var homeView=document.getElementById("home");
  function upd(){var v=document.querySelector(".view.on"),name=sub?FL[C.kind]:pageName,last="";
   if(v&&v.id!=="home"){
    if(C.kind==="plan"){var n=v.getAttribute("data-n"),h2=v.querySelector("h2");last=n?"Hour "+n+(h2?" · "+h2.textContent:""):(v.getAttribute("data-title")||"")}
    else{var h=v.querySelector("h2,h1");last=v.getAttribute("data-title")||(h?h.textContent:"")}}
   cr.innerHTML=head+(last?'<a href="#home">'+esc(name)+'</a>'+SEP+'<span aria-current="page">'+esc(last)+'</span>':'<span aria-current="page">'+esc(name)+'</span>')}
  upd();window.addEventListener("hashchange",function(){setTimeout(upd,0)});
  var lastV=null;new MutationObserver(function(){var v=document.querySelector(".view.on");if(v!==lastV){lastV=v;upd()}}).observe(main,{subtree:true,attributes:true,attributeFilter:["class"]});
 }
}

/* 3. related topics + previous/next */
function block(rel,prev,next){var a=document.createElement("aside");a.className="sx-rel";a.setAttribute("aria-label","Related topics");
 var h="";if(rel.length)h+='<h3>Related topics</h3><ul>'+rel.map(function(r){return '<li><a href="'+r[1]+'">'+esc(r[0])+'</a></li>'}).join("")+'</ul>';
 if(prev||next)h+='<nav class="sx-pn" aria-label="Previous and next">'+(prev?'<a rel="prev" href="'+prev[1]+'">← '+esc(prev[0])+'</a>':"")+(next?'<a rel="next" class="sx-nx" href="'+next[1]+'">'+esc(next[0])+' →</a>':"")+'</nav>';
 a.innerHTML=h;return a}
function chapterRel(n,except){var c=null;sub.chapters.forEach(function(x){if(x.n===n)c=x});if(!c)return [];var r=[];
 if(except!=="full")r.push(["Ch "+n+" in full notes",L(sub.files.full,"c"+n)]);
 if(sub.files.quick&&c.q&&except!=="quick")r.push(["Ch "+n+" in quick notes",L(sub.files.quick,"c"+n)]);
 if(except!=="plan"&&c.h.length)r.push(["72-hour plan: "+(c.h.length===1?"hour "+c.h[0]:"hours "+c.h[0]+"–"+c.h[c.h.length-1]),L(sub.files.plan,"h"+c.h[0])]);
 return r}
function common(){var r=[];if(sub){r.push(["Most repeated facts in "+sub.name,L(sub.files.full,sub.repeated)]);r.push([sub.name+" on the dashboard",L(D.home,sub.key)])}else r.push(["Study dashboard",L(D.home)]);return r}
if(C.kind==="full"||C.kind==="quick"||C.kind==="archive"){
 var secs=[].slice.call(document.querySelectorAll("section.chapter[id]"));
 if(secs.length){secs.forEach(function(sec,i){var m=/^c(\d+)$/.exec(sec.id),rel=(m&&sub)?chapterRel(+m[1],C.kind):[];
  if(m||i===secs.length-1)rel=rel.concat(common());
  var t=function(x){return x.getAttribute("data-title")||x.id};
  var prev=i>0?[t(secs[i-1]),"#"+secs[i-1].id]:["Start of notes","#top"],next=i<secs.length-1?[t(secs[i+1]),"#"+secs[i+1].id]:null;
  var tgt=sec.querySelector(":scope>.body")||sec;tgt.appendChild(block(rel,prev,next))})}
 else{[].slice.call(document.querySelectorAll("section.view[id]")).forEach(function(v){if(v.id==="results")return;
  var m=/^c(\d+)$/.exec(v.id),rel=(m&&sub)?chapterRel(+m[1],C.kind):[];rel=rel.concat(common());
  var hasPn=!!v.querySelector("nav.pn");v.appendChild(block(rel,hasPn?null:(v.id==="home"?null:["Start of notes","#home"]),null))})}
}
if(C.kind==="plan"&&sub){
 [].slice.call(document.querySelectorAll("section.view[id]")).forEach(function(v){
  var m=/^h(\d+)$/.exec(v.id),rel=[];
  if(m){var n=+m[1];(sub.hourCh[String(n)]||[]).forEach(function(c){rel=rel.concat(chapterRel(c,"plan"))});
   rel=rel.concat(common());
   var ownNext=!!v.querySelector(".done a.nx");
   v.appendChild(block(rel,n>1?["Hour "+(n-1),"#h"+(n-1)]:["Plan overview","#home"],ownNext?null:(n<sub.lastHour?["Hour "+(n+1),"#h"+(n+1)]:["Plan overview","#home"])))}
  else if(v.id==="home"){rel=[["Full notes",L(sub.files.full)]];if(sub.files.quick)rel.push(["Quick notes",L(sub.files.quick)]);rel=rel.concat(common());v.appendChild(block(rel,null,["Hour 1","#h1"]))}})
}
})();
"""

MARK_RE = re.compile(r"\n?<!--sx:start-->.*?<!--sx:end-->\n?", re.S)
STYLE_RE = re.compile(r'\n?<style id="sx-style">.*?</style>\n?', re.S)


def inject(path, smap):
    with open(path, encoding="utf-8", newline="") as f:
        s = f.read()
    orig = s
    s = STYLE_RE.sub("\n", MARK_RE.sub("\n", s))
    ctx = context_for(path, smap)
    rp = rootrel(path)
    depth = rp.count("/")
    data = {"ctx": dict(ctx, file=rp), "base": "../" * depth, "home": smap["home"],
            "subjects": smap["subjects"], "archive": smap["archive"]}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    style = f'<style id="sx-style">{CSS.strip()}</style>\n'
    block = f'<!--sx:start-->\n<script type="application/json" id="sx-data">{payload}</script>\n<script>{JS.strip()}</script>\n<!--sx:end-->\n'
    if "</head>" not in s or "</body>" not in s:
        raise SystemExit(f"sitenav: {rp} has no </head> or </body>")
    i = s.rindex("</head>")
    s = s[:i].rstrip("\n") + "\n" + style + s[i:]
    j = s.rindex("</body>")
    s = s[:j].rstrip("\n") + "\n" + block + s[j:]
    if s != orig:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(s)
        return True
    return False


def _has_head_body(path):
    with open(path, encoding="utf-8", newline="") as f:
        t = f.read()
    return "</head>" in t and "</body>" in t


def inject_all(only=None):
    smap = site_map()
    bad = [rootrel(p) for p in all_pages() if not _has_head_body(p)]
    if bad:
        sys.exit(f"sitenav: these pages lack </head> or </body>, nothing was changed: {bad}")
    changed = []
    for p in all_pages():
        if only and rootrel(p) not in only:
            continue
        if inject(p, smap):
            changed.append(rootrel(p))
    print(f"sitenav: {len(changed)} page(s) updated" + (": " + ", ".join(changed) if changed else ""))
    return smap


if __name__ == "__main__":
    inject_all()
