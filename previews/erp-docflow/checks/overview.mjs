import assert from 'node:assert/strict';
import {SEED,figures} from './fixtures/demo.js';
import {overviewData} from '../dist/overview-model.js';
import {createOverview} from '../dist/overview-ui.js';
const range={start:'2026-07-01',end:'2026-07-31'},ids=['bradesco','bb'];
const d=overviewData(SEED,'aurora',range,ids),f=figures(SEED,'aurora','2026-07');
assert.equal(d.summary.opening,f.opening);assert.equal(d.summary.closing,f.balance);
assert.equal(d.summary.incoming,f.incoming);assert.equal(d.summary.outgoing,f.outgoing);
assert.equal(d.projected,f.projected);assert.equal(d.points.at(-1).projected,f.projected);
for(const p of d.points)assert.equal(p.total,p.balances.reduce((n,x)=>n+x,0));
assert.equal(d.transactions.length,5);assert.equal(d.points.length,32);
const brad=overviewData(SEED,'aurora',range,['bradesco']);
assert.equal(brad.summary.closing,1275000);assert.equal(brad.transactions.length,3);
const none=overviewData(SEED,'aurora',range,[]);
assert.equal(none.summary.closing,0);assert.equal(none.obligations.length,0);
assert.equal(overviewData(SEED,'horizonte',range,ids).summary.closing,0,'Company must constrain supplied account IDs');
const partial=overviewData(SEED,'aurora',{start:'2026-07-10',end:'2026-07-15'},ids);
assert.equal(partial.summary.opening,2175000);assert.equal(partial.summary.closing,2187000);
assert.equal(partial.transactions.length,3);
assert.equal(overviewData(SEED,'aurora',{start:'2026-01-01',end:'2026-12-31'},ids).summary.closing,f.balance);
const negative=structuredClone(SEED);negative.accounts.find(a=>a.id==='bradesco').opening=-500000;
const neg=overviewData(negative,'aurora',range,ids);assert.equal(neg.points.at(-1).balances[0],-475000);
assert.equal(neg.points.at(-1).total,402000);

// Controls exercised without a browser. Visual layout remains unverified.
globalThis.document={addEventListener(){},querySelector:()=>null,querySelectorAll:()=>[]};
globalThis.window={scrollY:0,scrollTo(){}};globalThis.CSS={escape:v=>v};
let html,exported,opened;
const a={state:structuredClone(SEED),company:'aurora',month:'2026-07',NOW:'2026-07-18',
  esc:v=>String(v??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;'),money:v=>'R$ '+(v/100).toFixed(2),
  fullDate:v=>v.split('-').reverse().join('/'),date:v=>v.slice(8)+'/'+v.slice(5,7),icon:()=>'',
  btn:(label,attrs)=>`<button ${attrs}>${label}</button>`,titleBlock:(t,s,actions)=>`<h1>${t}</h1>${actions}`,
  get:(type,id)=>a.state[type].find(x=>x.id===id),scope:type=>a.state[type].filter(x=>x.company===a.company),
  toast(){},render:()=>{html=ui.render()},openCashbook:(range,account)=>{opened={range,account}},download:(name,content)=>{exported={name,content}}};
const ui=createOverview(a);a.render();assert.doesNotMatch(html,/NaN|Infinity/);
ui.change({target:{hasAttribute:k=>k==='data-ov-account',dataset:{ovAccount:'bb'},checked:false}});
ui.click({ovSheet:'1'});assert.equal(opened.account,'bradesco');assert.deepEqual(opened.range,range);
ui.click({ovExport:'1'});assert.match(exported.content,/Bradesco/);assert.doesNotMatch(exported.content,/Banco do Brasil/);
ui.click({ovPreset:'day'});ui.click({ovSheet:'1'});assert.deepEqual(opened.range,{start:'2026-07-18',end:'2026-07-18'});
ui.click({ovShift:'1'});ui.click({ovSheet:'1'});assert.equal(opened.range.start,'2026-07-19');
const change=(attr,value)=>ui.change({target:{hasAttribute:k=>k===attr,value}});
change('data-ov-start','2026-07-10');change('data-ov-end','2026-08-05');ui.click({ovApply:'1'});ui.click({ovSheet:'1'});
assert.deepEqual(opened.range,{start:'2026-07-10',end:'2026-08-05'});
change('data-ov-start','2026-09-10');ui.click({ovApply:'1'});ui.click({ovSheet:'1'});assert.equal(opened.range.start,'2026-07-10');
a.company='horizonte';a.render();ui.click({ovSheet:'1'});assert.equal(opened.account,'hs');assert.doesNotMatch(html,/data-ov-account="bb"/);
a.company='aurora';a.render();ui.click({ovSheet:'1'});assert.equal(opened.account,'bradesco');
a.state=negative;a.render();assert.doesNotMatch(html,/NaN|Infinity/);
console.log('Verified chart balances, stacked totals, projections, partial ranges, negative balances, company/bank isolation, shared period controls, export and handoff to the sheet. Visual QA unavailable.');
