'use strict';
// Run the actual plan script against a small DOM fixture. No browser is used.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, 'template_72h_js.html'), 'utf8')
  .replace(/^<script>/, '').replace(/<\/script>\s*$/, '');

function run(stored, blocked, expected) {
  const classes = () => ({values:new Set(), toggle(k,on){on?this.values.add(k):this.values.delete(k);},
    add(k){this.values.add(k);}, contains(k){return this.values.has(k);}});
  const views = ['home','h1','h2'].map(id => ({id,dataset:id==='home'?{}:{n:id.slice(1)},classList:classes(),querySelector(){return null;}}));
  const controls = {prog:{},bar:{style:{}},cont:{},dark:{addEventListener(){}}};
  const nav = ['h1','h2'].map(id => ({dataset:{v:id},classList:classes()}));
  const buttons = [1,2].map(n => ({dataset:{done:String(n)},classList:classes()}));
  const errors = [], listeners = {}, events = {};
  const document = {
    title:'', documentElement:{setAttribute(){}},
    getElementById(id){return views.find(v=>v.id===id)||controls[id]||null;},
    querySelector(s){return s.startsWith('#')?this.getElementById(s.slice(1)):null;},
    querySelectorAll(s){return s==='.view'?views:s==='.side a[data-v]'?nav:s==='[data-done]'?buttons:[];},
    addEventListener(type,fn){events[type]=fn;}
  };
  const localStorage = {
    getItem(key){if(blocked)throw new Error('SecurityError');return key==='polgov72-done'?stored:null;},
    setItem(){if(blocked)throw new Error('SecurityError');}
  };
  const window = {addEventListener(type,fn){listeners[type]=fn;},scrollTo(){},matchMedia(){return {matches:false};}};
  vm.runInNewContext(code,{document,localStorage,window,location:{hash:'#h2'},console:{error(...args){errors.push(args);}}});
  assert.equal(errors.length,0,'Storage must not prevent plan initialization');
  assert.equal(typeof listeners.hashchange,'function','Hash navigation must initialize');
  assert.equal(views[2].classList.contains('on'),true,'Requested hour must open');
  assert.equal(controls.prog.textContent,expected+' of 72 hours done');
  // Completion remains usable even when persistent storage is blocked.
  const before = buttons[0].classList.contains('is');
  events.click({target:{closest(s){return s==='[data-done]'?buttons[0]:null;}}});
  assert.notEqual(buttons[0].classList.contains('is'),before);
  locationHashCheck(listeners,views);
}
function locationHashCheck(listeners,views){listeners.hashchange();assert.equal(views[2].classList.contains('on'),true);}
for(const [stored,blocked,expected] of [['[1,2]',false,2],['null',false,0],['{}',false,0],['bad json',false,0],
  ['[1,1,2,"3",0,73,1.5]',false,2],[null,true,0]])run(stored,blocked,expected);
console.log('PASS: Polity plan navigation/progress with valid, malformed, duplicate and blocked storage.');
