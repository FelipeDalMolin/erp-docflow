import assert from 'node:assert/strict';
import {SEED} from './fixtures/demo.js';
import {overviewData} from '../dist/overview-model.js';
import {withBalanceEvents,balancePointX} from '../dist/balance-events.js';
import {createOverview} from '../dist/overview-ui.js';
const range={start:'2026-07-01',end:'2026-07-31'},ids=['bradesco','bb'];
const state=structuredClone(SEED),before=JSON.stringify(state);
const model=(r=range,accounts=ids)=>withBalanceEvents(overviewData(state,'aurora',r,accounts),state,'aurora',r);
const d=model(),events=d.points.filter(p=>p.transaction);
assert.equal(events.length,5);assert.equal(events[0].transaction.id,'m1');
assert.deepEqual(events[0].balances,[1250000,925000]);assert.equal(events[0].total,2175000);
assert.equal(events.find(p=>p.transaction.id==='m3').transaction.amount,180000);
assert.deepEqual(d.points.at(-1).balances,[1275000,877000]);assert.equal(d.points.at(-1).total,2152000);
assert.equal(d.points.at(-1).projected,d.projected);
assert.equal(balancePointX(events[0],range),82+5/31*798,'July 5 is placed on its own day');
assert.equal(model(range,['bradesco']).points.filter(p=>p.transaction).length,3);
assert.equal(model(range,[]).points.filter(p=>p.transaction).length,0);
const annual={start:'2026-01-01',end:'2026-12-31'},year=model(annual);
const july5=year.points.find(p=>p.transaction?.id==='m1');assert.equal(july5.date,'2026-07-05');
assert.ok(balancePointX(july5,annual)<balancePointX({date:'2026-07-31'},annual),'Annual chart must keep the actual day, not move it to month-end');
assert.equal(JSON.stringify(state),before);
state.transactions.push({id:'same-day',company:'aurora',account:'bb',date:'2026-07-05',amount:-10000});
const same=model().points.filter(p=>p.transaction&&p.date==='2026-07-05');
assert.equal(same.length,2);assert.equal(balancePointX(same[0],range),balancePointX(same[1],range));
assert.equal(same[1].balances[1],915000);
state.transactions.pop();
state.accounts[0].opening=-500000;assert.equal(model().points.at(-1).balances[0],-475000);state.accounts[0].opening=1250000;

globalThis.document={addEventListener(){},querySelector:()=>null,querySelectorAll:()=>[]};
globalThis.window={scrollY:0,scrollTo(){}};globalThis.CSS={escape:v=>v};
let html,opened,exported;
const a={state,company:'aurora',month:'2026-07',NOW:'2026-07-18',
  esc:v=>String(v??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;'),money:v=>'R$ '+(v/100).toFixed(2),
  fullDate:v=>v.split('-').reverse().join('/'),date:v=>v.slice(8)+'/'+v.slice(5,7),icon:()=>'',
  btn:(label,attrs)=>`<button ${attrs}>${label}</button>`,titleBlock:(t,s,actions)=>`<h1>${t}</h1>${actions}`,
  get:(type,id)=>a.state[type].find(x=>x.id===id),scope:type=>a.state[type].filter(x=>x.company===a.company),
  toast(){},render:()=>{html=ui.render()},openCashbook(){},open:(kind,id)=>{opened={kind,id}},download:(name,content)=>{exported={name,content}}};
const ui=createOverview(a);a.render();
assert.match(html,/docflow-amchart/);
assert.match(html,/Bradesco/);assert.match(html,/Banco do Brasil/);
assert.doesNotMatch(html,/cf-view|cf-filter|cf-detail|Entradas × saídas/);
assert.match(html,/5 lançamentos/);
ui.click({ovTransaction:'m1'});assert.deepEqual(opened,{kind:'obligation',id:'o204'});
ui.click({ovTransaction:'m3'});assert.deepEqual(opened,{kind:'obligation',id:'o105'});
ui.click({ovExport:'1'});assert.match(exported.content,/PIX recebido · Marina Studio/);assert.match(exported.content,/Saldo total/);
ui.change({target:{hasAttribute:k=>k==='data-ov-account',dataset:{ovAccount:'bb'},checked:false}});
assert.match(html,/3 lançamentos/);
a.company='horizonte';a.render();assert.match(html,/2 lançamentos/);assert.doesNotMatch(html,/Marina Studio/);
assert.doesNotMatch(html,/NaN|Infinity/);
console.log('Verified amCharts container and dated transaction data, within-day balances, long intervals, negative balances, company/account filters, context navigation and export. Browser visual QA unavailable.');
