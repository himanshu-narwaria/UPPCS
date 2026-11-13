(function(){
'use strict';
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const store={get(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v);}catch(_){return d;}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(_){}}};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const D=$('#pqd')?JSON.parse($('#pqd').textContent):{};
const FULL='current-uppsc-full-notes.html';
const side=$('#side'),scrim=$('#scrim'),menu=$('#menu'),search=$('#q'),test=$('#test');
let answers=store.get('ca3-answers',{}),boxes=store.get('ca3-leitner',{}),last='home',index=null;
if(!answers||typeof answers!=='object'||Array.isArray(answers))answers={};
if(!boxes||typeof boxes!=='object'||Array.isArray(boxes))boxes={};
const mocks=Object.create(null);

/* ---------- views, drawer, routing ---------- */
function drawer(o){if(!side)return;side.classList.toggle('open',o);if(scrim)scrim.classList.toggle('on',o);if(menu)menu.setAttribute('aria-expanded',String(o));}
function show(id){$$('.view').forEach(v=>v.classList.toggle('on',v.id===id));$$('.side a[data-v]').forEach(a=>a.classList.toggle('on',a.dataset.v===id));if(id!=='results')last=id;const v=document.getElementById(id);if(v){$$('ol.pq',v).forEach(fill);}}
function route(){let id;try{id=decodeURIComponent(location.hash.slice(1))||'home';}catch(_){id='home';}let el=document.getElementById(id);if(!el||!el.closest('.view'))el=$('#home');if(!el)return;const view=el.closest('.view');if(search)search.value='';show(view.id);drawer(false);if(el===view){window.scrollTo(0,0);}else{for(let p=el;p;p=p.parentElement){if(p.tagName==='DETAILS')p.open=true;}el.scrollIntoView({block:'start'});el.classList.add('flash');setTimeout(()=>el.classList.remove('flash'),1700);}}
if(menu)menu.addEventListener('click',()=>drawer(!side.classList.contains('open')));
if(scrim)scrim.addEventListener('click',()=>drawer(false));
window.addEventListener('hashchange',route);
document.addEventListener('keydown',e=>{if(e.key==='Escape')drawer(false);});

/* ---------- test mode: hide answers and bold key facts ---------- */
function applyTest(on){document.body.classList.toggle('test',on);if(test)test.checked=on;store.set('ca3-test',on);if(!on)$$('.shown').forEach(x=>x.classList.remove('shown'));}
if(test){test.addEventListener('change',()=>applyTest(test.checked));applyTest(!!store.get('ca3-test',false));}
document.addEventListener('click',e=>{if(!document.body.classList.contains('test'))return;const k=e.target.closest('b.k,.qa .a');if(k)k.classList.toggle('shown');});

/* ---------- search ---------- */
function build(){index=[];$$('.view.ch').forEach(v=>{$$('.pt',v).forEach(p=>{const t=p.textContent.replace(/\s+/g,' ').trim();const art=p.closest('.topic');index.push({el:p,id:(art&&art.id)||v.id,t,low:t.toLowerCase(),where:(v.dataset.title||'')+(art&&art.dataset.title?' › '+art.dataset.title:'')});});});}
function runSearch(){const s=search.value.trim().toLowerCase();if(s.length<2){show(last);return;}if(!index)build();const w=s.split(/\s+/),hits=index.filter(x=>w.every(t=>x.low.includes(t)));$('#rt').textContent=hits.length+(hits.length===1?' result':' results');const l=$('#rl');l._h=hits;l.innerHTML=hits.slice(0,80).map((x,i)=>'<li><a href="#'+esc(x.id)+'" data-hit="'+i+'">'+esc(x.t.slice(0,300))+'<small>'+esc(x.where)+'</small></a></li>').join('')||'<li>No match. Try a name, place or scheme.</li>';show('results');window.scrollTo(0,0);}
if(search){let t;search.addEventListener('input',()=>{clearTimeout(t);t=setTimeout(runSearch,150);});}
const rl=$('#rl');if(rl)rl.addEventListener('click',e=>{const a=e.target.closest('[data-hit]');if(!a)return;e.preventDefault();const x=rl._h[+a.dataset.hit];search.value='';show(x.el.closest('.view').id);for(let p=x.el;p;p=p.parentElement){if(p.tagName==='DETAILS')p.open=true;}x.el.scrollIntoView({block:'center'});x.el.classList.add('flash');setTimeout(()=>x.el.classList.remove('flash'),1700);});

/* ---------- practice questions with spaced repetition (Leitner boxes) ---------- */
function learn(id,ok){const b=boxes[id]||{b:0,w:0};if(ok){b.b=Math.min(5,(b.b||0)+1);}else{b.b=1;b.w=(b.w||0)+1;}boxes[id]=b;store.set('ca3-leitner',boxes);}
function card(id,n){const q=D[id];if(!q)return'';return '<li data-qi="'+id+'"><div class="pq-meta">'+esc(q.e)+'</div><div class="pq-stem">'+esc(q.s)+'</div><div class="pq-opts">'+q.o.map((o,j)=>'<button type="button" class="pq-o" data-j="'+j+'">'+'ABCD'[j]+'. '+esc(o)+'</button>').join('')+'</div><div class="pq-fb" hidden></div></li>';}
function stateOf(ol){if(ol.dataset.mock)return mocks[ol.dataset.mock]||(mocks[ol.dataset.mock]={a:{},done:false});if(ol.dataset.review!==undefined)return ol._s||(ol._s={a:{},done:null});return null;}
function paint(li){const id=li.dataset.qi,q=D[id],ol=li.closest('ol.pq'),st=stateOf(ol),j=st?st.a[id]:answers[id];const finished=st?(st.done===null?j!==undefined:st.done):j!==undefined;
 $$('.pq-o',li).forEach((b,k)=>{b.disabled=finished;b.classList.toggle('sel',!finished&&k===j);b.classList.toggle('ok',finished&&q.k.includes(k));b.classList.toggle('no',finished&&k===j&&!q.k.includes(k));b.setAttribute('aria-pressed',String(k===j));});
 const f=$('.pq-fb',li);f.hidden=!finished;if(finished){const href=(document.getElementById(q.h)?'#':FULL+'#')+q.h;f.innerHTML='<b>'+(j===undefined?'Not answered. ':q.k.includes(j)?'Correct. ':'Not quite. ')+'</b>'+esc(q.f)+' <a href="'+esc(href)+'">Open the note</a>';}}
function score(ol){const ids=(ol._ids||[]),st=stateOf(ol),a=st?st.a:answers,fin=ids.filter(x=>a[x]!==undefined),ok=fin.filter(x=>D[x]&&D[x].k.includes(a[x]));const s=ol.parentElement.querySelector('.score');if(s)s.textContent=ids.length+' questions · '+fin.length+(st&&st.done===false?' chosen':' answered · '+ok.length+' correct');}
function render(ol,ids){ol._ids=ids.filter(x=>D[x]);ol.innerHTML=ol._ids.map(card).join('')||'<li>Nothing here yet.</li>';$$('[data-qi]',ol).forEach(paint);score(ol);}
function dueReview(n){return Object.keys(boxes).filter(id=>D[id]&&boxes[id].b<=2&&boxes[id].w>0).sort((x,y)=>(boxes[y].w-boxes[x].w)||(boxes[x].b-boxes[y].b)).slice(0,n);}
function fill(ol){if(ol.dataset.filled)return;ol.dataset.filled='1';if(ol.id==='pqList'){pick();return;}if(ol.dataset.review!==undefined){render(ol,dueReview(+ol.dataset.review||15));return;}render(ol,(ol.dataset.q||'').split(',').filter(Boolean));}
document.addEventListener('click',e=>{const b=e.target.closest('.pq-o');if(!b||b.disabled)return;const li=b.closest('[data-qi]'),ol=li.closest('ol.pq'),id=li.dataset.qi,j=+b.dataset.j,st=stateOf(ol);
 if(st&&st.done===false){st.a[id]=j;paint(li);score(ol);return;}
 if(st){st.a[id]=j;}else{answers[id]=j;store.set('ca3-answers',answers);}
 learn(id,D[id].k.includes(j));paint(li);score(ol);});
/* practice view */
const pqCh=$('#pqCh'),pqPri=$('#pqPri'),pqMiss=$('#pqMiss'),pqList=$('#pqList');let pool=[],shown=0;
function pick(){if(!pqList)return;const ch=pqCh?pqCh.value:'',pri=pqPri&&pqPri.checked,miss=pqMiss&&pqMiss.checked;pool=Object.keys(D).filter(id=>(!ch||D[id].ch===ch)&&(!pri||D[id].p===1)&&(!miss||(boxes[id]&&boxes[id].b<=2&&boxes[id].w>0)));shown=0;pqList.innerHTML='';more();}
function more(){const part=pool.slice(shown,shown+15);shown+=part.length;pqList._ids=pool.slice(0,shown);pqList.insertAdjacentHTML('beforeend',part.map(card).join(''));$$('[data-qi]',pqList).slice(-part.length).forEach(paint);const m=$('#pqMore');if(m)m.hidden=shown>=pool.length;score(pqList);if(!pool.length)pqList.innerHTML='<li>No questions match. Clear a filter.</li>';}
if(pqList){[pqCh,pqPri,pqMiss].forEach(x=>x&&x.addEventListener('change',pick));const m=$('#pqMore');if(m)m.addEventListener('click',more);const sh=$('#pqShuf');if(sh)sh.addEventListener('click',()=>{for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}shown=0;pqList.innerHTML='';more();});
 const rs=$('#pqReset');if(rs)rs.addEventListener('click',()=>{answers={};store.set('ca3-answers',answers);pick();});}
/* chapter practice links */
document.addEventListener('click',e=>{const a=e.target.closest('[data-practice-ch]');if(a&&pqCh){pqCh.value=a.dataset.practiceCh;if(pqList.dataset.filled)pick();}});

/* ---------- timed mocks ---------- */
document.addEventListener('click',e=>{const b=e.target.closest('[data-mock-start],[data-mock-submit]');if(!b)return;const id=b.dataset.mockStart||b.dataset.mockSubmit,ol=$('ol.pq[data-mock="'+id+'"]'),st=stateOf(ol),box=b.closest('.mock');
 if(b.dataset.mockStart){if(st.timer)return;let left=(+box.dataset.min||20)*60;const t=$('.timer',box);b.disabled=true;st.timer=setInterval(()=>{left--;t.textContent=Math.floor(left/60)+':'+String(left%60).padStart(2,'0');if(left<=0){clearInterval(st.timer);submit(ol,st,box);}},1000);return;}
 submit(ol,st,box);});
function submit(ol,st,box){if(st.done)return;st.done=true;if(st.timer)clearInterval(st.timer);(ol._ids||[]).forEach(id=>{if(st.a[id]!==undefined)learn(id,D[id].k.includes(st.a[id]));else learn(id,false);});$$('[data-qi]',ol).forEach(paint);score(ol);const s=$('[data-mock-submit]',box);if(s)s.disabled=true;}

/* ---------- 72-hour plan progress ---------- */
let done=[];try{done=JSON.parse(localStorage.getItem("ca72-v3-done")||'[]');}catch(_){done=[];}
if(!Array.isArray(done))done=[];done=[...new Set(done)].filter(n=>Number.isInteger(n)&&n>=1&&n<=72);
function paintPlan(){const total=$$('section.view[data-n]').length;if(!total)return;$$('.side a[data-v^="h"]').forEach(a=>a.classList.toggle('ok',done.includes(+a.dataset.v.slice(1))));$$('[data-done]').forEach(b=>{const on=done.includes(+b.dataset.done);b.classList.toggle('is',on);b.textContent=on?'Hour '+b.dataset.done+' done ✓':'Mark hour '+b.dataset.done+' done';});const p=$('#prog');if(p)p.textContent=done.length+' of 72 hours done';const bar=$('#bar');if(bar)bar.style.width=(100*done.length/72)+'%';const c=$('#cont');if(c){let n=1;while(done.includes(n)&&n<72)n++;c.href='#h'+n;c.textContent=(done.length?'Continue with hour ':'Start with hour ')+n+' →';}}
document.addEventListener('click',e=>{const b=e.target.closest('[data-done]');if(!b)return;const n=+b.dataset.done,i=done.indexOf(n);if(i>=0)done.splice(i,1);else done.push(n);try{localStorage.setItem("ca72-v3-done",JSON.stringify(done));}catch(_){}paintPlan();});

paintPlan();route();
})();
