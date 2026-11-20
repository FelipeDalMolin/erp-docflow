import assert from 'node:assert/strict';
import {SEED} from './fixtures/demo.js';
import {createPeriodSheet} from '../dist/period-ui.js';

// Component checks without a browser; these do not validate the visual layout.
globalThis.document={querySelector:()=>null,addEventListener:()=>{}};
globalThis.CSS={escape:v=>v};
let selected='2026-07-18',html='',download;
const a={state:structuredClone(SEED),company:'aurora',month:'2026-07',account:'all',
  esc:v=>String(v??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;'),
  money:v=>'R$ '+(v/100).toFixed(2),fullDate:v=>v.split('-').reverse().join('/'),icon:()=>'',
  btn:(label,attrs)=>`<button ${attrs}>${label}</button>`,
  get:(type,id)=>a.state[type].find(x=>x.id===id),scope:type=>a.state[type].filter(x=>x.company===a.company),
  render:()=>{html=sheet.render()},toast:()=>{},download:(name,content)=>{download={name,content}}};
const sheet=createPeriodSheet(a,{get selected(){return selected},pick:v=>{selected=v;a.month=v.slice(0,7)}});
const change=(attr,value)=>sheet.change({target:{value,hasAttribute:key=>key===attr}});
a.render();
assert.match(html,/data-range-start/);assert.match(html,/data-range-end/);
change('data-range-start','2026-07-10');change('data-range-end','2026-08-05');sheet.click({sheetApply:'1'});
const snapshot=()=>Object.fromEntries(Object.entries(sheet.summary()).map(([key,value])=>[key,Array.isArray(value)?value.map(x=>x.id).sort():value]));
const summary=snapshot();
for(const key of ['monthly','yearly','daily']){sheet.click({sheetPeriod:key});assert.deepEqual(snapshot(),summary);}
sheet.click({sheetToggle:'real:all:incoming:category:unclassified'});sheet.click({bookExport:'1'});
assert.match(download.content,/"Período";"10\/07\/2026";"05\/08\/2026"/);
assert.match(download.content,/Ateliê Luna/);assert.doesNotMatch(download.content,/Marina Studio/);
change('data-range-start','2026-09-01');sheet.click({sheetApply:'1'});
assert.deepEqual(snapshot(),summary,'Rejected dates must preserve the active query');
assert.match(html,/data final deve ser igual ou posterior/);
change('data-range-start','2026-07-10');sheet.click({sheetApply:'1'});
sheet.click({rangeShift:'1'});sheet.click({bookExport:'1'});
assert.match(download.content,/"Período";"06\/08\/2026";"01\/09\/2026"/);
change('data-range-preset','quarter');sheet.click({sheetPeriod:'monthly'});
assert.match(html,/value="2026-07-01"/);assert.match(html,/value="2026-09-30"/);
sheet.click({sheetDrill:'2026-08'});sheet.click({bookExport:'1'});
assert.match(download.content,/"Período";"01\/08\/2026";"31\/08\/2026"/);
console.log('Verified range controls, grouping preserves totals, rejected input is atomic, navigation, drill-down and matching export. Visual QA unavailable.');
