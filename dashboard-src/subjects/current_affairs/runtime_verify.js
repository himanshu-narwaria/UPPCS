/* Focused checks of the actual runtime with a small UI adapter. No browser/layout claim. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const D=JSON.parse(fs.readFileSync(path.join(__dirname,'parsed_uppsc_questions.json'),'utf8'));
const source=fs.readFileSync(path.join(__dirname,'study_runtime.js'),'utf8').replace(
  '  pickChapter();paintProgress();route();',
  '  globalThis.__qa={paintAnswer,mockState,scoreQuestions,fillQuestions,get answers(){return answers},get done(){return done}};pickChapter();paintProgress();route();');
function boot(saved='{}',progress='[]',localAnchor=false){
  const handlers=[],lists=[],storage=new Map([['ca-source-practice-v2',saved],['ca72-done',progress]]);
  const document={querySelector:s=>s==='#pqd'?{textContent:JSON.stringify(D)}:null,
    querySelectorAll:s=>s.startsWith('[data-qi=')?lists.flatMap(x=>x.items).filter(li=>s.includes('"'+li.dataset.qi+'"')):s==='ol.pq[data-filled]'?lists:[],
    getElementById:id=>localAnchor&&id==='c1-t1'?{}:null,
    addEventListener:(type,fn)=>{if(type==='click')handlers.push(fn)},body:{classList:{toggle(){}}},documentElement:{dataset:{}}};
  const context={document,localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v)},
    window:{addEventListener(){},scrollTo(){}},location:{hash:''},history:{replaceState(){}},
    setTimeout,clearTimeout,setInterval,clearInterval};
  vm.runInNewContext(source,context,{filename:'study_runtime.js'});
  function click(target){for(const fn of handlers)fn({target})}
  function makeSet(mock){
    const feedback={hidden:true,innerHTML:''},score={textContent:''};
    const li={dataset:{qi:'q0001'},closest:()=>ol,querySelector:s=>s==='.pq-fb'?feedback:null,
      querySelectorAll:s=>s==='.pq-o'?buttons:[]};
    const buttons=D.q0001.o.map((_,i)=>{const classes=new Set();return {dataset:{answer:String(i)},disabled:false,
      classList:{toggle:(n,on)=>on?classes.add(n):classes.delete(n),contains:n=>classes.has(n)},
      setAttribute(){},closest:s=>s==='[data-qi]'?li:null}});
    const ol={dataset:{q:'q0001',filled:'1',...(mock?{mock}: {})},items:[li],parentElement:null,
      querySelectorAll:s=>s==='[data-qi]'?[li]:[],innerHTML:''};
    const view={querySelector:()=>null},box={querySelector:s=>s==='ol.pq'?ol:s==='.score'?score:null,closest:()=>view};
    ol.parentElement=box;lists.push(ol);
    return {ol,li,buttons,feedback,score,
      answer:i=>click({closest:s=>s==='[data-answer]'?buttons[i]:null}),
      submit:()=>click({closest:s=>s==='[data-submit-mock]'?{closest:()=>box}:null}),
      reset:()=>click({closest:s=>s==='[data-reset-mock]'?{closest:()=>box}:null})};
  }
  return {qa:context.__qa,storage,makeSet};
}
for(const bad of ['null','[]','"wrong"','broken JSON'])assert.equal(JSON.stringify(boot(bad).qa.answers),'{}');
const guarded=boot('{"q0001":null,"q0002":99,"q0003":"0","unknown":0,"q0004":1}','[1,1,0,73,"2",2]');
assert.equal(JSON.stringify(guarded.qa.answers),'{"q0004":1}');
assert.equal(JSON.stringify(guarded.qa.done),'[1,2]');
const app=boot(),regular=app.makeSet(),mock=app.makeSet('h69');
regular.answer(0);
assert.equal(app.qa.answers.q0001,0);
assert.equal(regular.feedback.hidden,false);
assert.match(regular.feedback.innerHTML,/href="current-uppsc-full-notes.html#c1-t1"/);
app.qa.paintAnswer(mock.li);
assert.equal(mock.feedback.hidden,true);
assert.equal(mock.buttons.every(b=>!b.disabled&&!b.classList.contains('ok')),true);
mock.answer(2);
assert.equal(app.qa.mockState(mock.ol).answers.q0001,2);
assert.equal(app.qa.answers.q0001,0);
assert.equal(mock.feedback.hidden,true);
assert.equal(mock.buttons[2].classList.contains('selected'),true);
assert.doesNotMatch(mock.score.textContent,/correct/);
mock.answer(1);
assert.equal(mock.buttons[1].classList.contains('selected'),true);
assert.equal(mock.buttons[2].classList.contains('selected'),false);
mock.submit();
assert.equal(mock.feedback.hidden,false);
assert.equal(mock.buttons.every(b=>b.disabled),true);
assert.equal(mock.buttons[2].classList.contains('ok'),true);
assert.equal(mock.buttons[1].classList.contains('no'),true);
assert.match(mock.score.textContent,/0 correct/);
assert.equal(JSON.parse(app.storage.get('ca-source-practice-v2')).q0001,0);
mock.reset();
assert.equal(Object.keys(app.qa.mockState(mock.ol).answers).length,0);
assert.equal(mock.feedback.hidden,true);
assert.equal(mock.buttons.every(b=>!b.disabled&&!b.classList.contains('ok')),true);
const local=boot('{}','[]',true),localSet=local.makeSet();
localSet.answer(2);
assert.match(localSet.feedback.innerHTML,/href="#c1-t1"/);
console.log('Runtime checks pass: malformed/null storage, valid progress, persisted learning answers, independent editable mock selections, deferred keys, scoring/reset and cross-file/local feedback links.');
