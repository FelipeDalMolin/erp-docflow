import assert from 'node:assert/strict';
import fs from 'node:fs';
import {financialPresentation,presentationHTML} from '../dist/record-presentation.js';
import {calendarRangeEvents} from '../dist/workspace-model.js';
import {createCalendar} from '../dist/calendar-ui.js';
import {financeSeries} from '../dist/amchart-runtime.js';
import {VISUAL_THEME,installVisualTheme,financeColor} from '../dist/visual-theme.js';

const today='2026-11-20';
const state={companies:[{id:'co',name:'Teste'}],accounts:[{id:'bradesco',company:'co',name:'Bradesco'},{id:'bb',company:'co',name:'Banco do Brasil'}],
  obligations:[{id:'o',company:'co',kind:'out',title:'Compromisso de teste',party:'Teste',due:today,account:'bradesco',items:[{amount:10000}],docs:[]}],
  transactions:[{id:'t',company:'co',account:'bradesco',amount:-10000,date:today,description:'Movimento de teste',imported:true,sourceDocument:'statement',confirmed:false}],
  documents:[{id:'statement',company:'co',name:'Extrato',type:'Extrato bancário',status:'Revisado'}],tasks:[],assets:[],contracts:[],classification:{records:{}}};
const o=state.obligations[0],t=state.transactions[0];
const tx=()=>financialPresentation(state,'transaction',t,today),ob=()=>financialPresentation(state,'obligation',o,today);
assert.equal(tx().complete,false,'Imported does not mean reconciled');
t.confirmed=true;assert.equal(tx().complete,false,'A bare confirmed flag is not a correspondence');
t.obligation='o';assert.equal(tx().complete,true);assert.equal(ob().complete,true);
assert.ok(tx().warnings.includes('Documento da operação não vinculado'));
assert.ok(tx().warnings.includes('Classificação a conferir'));
o.docs=['statement'];assert.ok(tx().warnings.includes('Documento da operação não vinculado'),'The statement is not a supporting receipt');
o.docs=['receipt'];state.documents.push({id:'receipt',company:'co',name:'Comprovante',status:'A revisar'});
assert.ok(tx().warnings.includes('Documentação a conferir'));assert.equal(tx().complete,true,'Docs cannot undo reconciliation');
state.documents[1].locked=true;assert.ok(tx().warnings.includes('Documento aguardando senha'));
state.documents[1].locked=false;state.documents[1].status='Revisado';
state.classification.records.t={company:'co',status:'reviewed',bankAmount:t.amount,bankDate:t.date,lines:[]};
assert.equal(tx().warnings.length,0);
t.amount=-4000;assert.equal(tx().complete,true,'A confirmed partial payment is itself a reconciled movement');
assert.equal(ob().complete,false,'The obligation remains partial');assert.equal(ob().label,'Conciliação parcial');
t.amount=-12000;assert.equal(tx().complete,false);assert.equal(ob().complete,false);assert.ok(tx().warnings.includes('Valor conciliado acima do compromisso'));
t.amount=-10000;t.confirmed=false;assert.equal(ob().complete,false);assert.equal(tx().complete,false);
t.confirmed=true;t.account='bb';assert.equal(tx().complete,false,'Wrong account must not be treated as reconciled');t.account='bradesco';
t.company='other';assert.equal(tx().complete,false);assert.equal(ob().complete,false);t.company='co';
t.amount=10000;assert.equal(tx().complete,false,'Wrong direction');t.amount=-10000;
t.archiveReason='superseded';assert.equal(tx().complete,false);delete t.archiveReason;
t.date='2026-11-21';assert.equal(tx().complete,false,'Future registration cannot resolve today');t.date=today;
o.cancelled=true;assert.equal(tx().complete,false);delete o.cancelled;
o.monitoringKind='estimate';assert.equal(tx().complete,false);delete o.monitoringKind;
o.due='2026-11-19';assert.equal(ob().complete,true);assert.ok(ob().warnings.includes('Realização após a data prevista'),'A late reconciled record retains its alert');o.due=today;
assert.ok(!calendarRangeEvents(state,'co',{start:today,end:today},{asOf:today}).some(e=>e.type==='obligation'),'Fully reconciled and reviewed obligation is hidden by default');
assert.ok(calendarRangeEvents(state,'co',{start:today,end:today},{asOf:today,completed:true}).some(e=>e.type==='obligation'),'Completed filter restores the reviewed obligation');
o.missing='Recibo';const before=JSON.stringify(state);
let ev=calendarRangeEvents(state,'co',{start:today,end:today},{asOf:today});
assert.ok(ev.find(e=>e.type==='realized').presentation.complete);
assert.ok(ev.find(e=>e.type==='obligation'),'Reconciled with outstanding documents stays visible');
assert.equal(ev.find(e=>e.type==='obligation').amount,-10000);
assert.equal(JSON.stringify(state),before,'Rendering cannot mutate financial or review state');
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const a={state,company:'co',NOW:today,esc,money:v=>'R$ '+v/100,fullDate:d=>d,icon:()=>'',btn:(l,p)=>'<button '+p+'>'+l+'</button>',empty:()=>'',titleBlock:()=>'',get:(col,id)=>state[col].find(x=>x.id===id),scope:col=>state[col].filter(x=>x.company==='co'),setMonth(){}};
const ui=createCalendar(a),html=ui.render('');
assert.match(html,/cal-event realized is-reconciled/);assert.match(html,/data-flow="outgoing"/);assert.match(html,/record-warning/);assert.match(html,/Conciliação e pendências: como ler/);
assert.ok(html.includes('Financeiro conciliado'));assert.ok(html.includes('Documentação pendente: Recibo'));
assert.equal(JSON.stringify(state),before);
assert.ok(!presentationHTML(a,{complete:true,label:'Conciliado',warnings:['<script>alert(1)</script>']}).includes('<script>'));
for(const direction of ['incoming','outgoing']){
  const both=financeSeries(state.accounts,'bank').find(s=>s.group===direction&&s.bankIndex===1).color;
  const only=financeSeries([state.accounts[1]],'bank').find(s=>s.group===direction).color;
  const reversed=financeSeries([...state.accounts].reverse(),'bank').find(s=>s.group===direction&&s.bankIndex===0).color;
  assert.equal(both,only);assert.equal(both,reversed);assert.equal(only,financeColor(direction,state.accounts[1]));
}
const vars={};installVisualTheme({documentElement:{style:{setProperty:(k,v)=>vars[k]=v}}});
const css=fs.readFileSync(new URL('../dist/visual-theme.css',import.meta.url),'utf8');
for(const [,variable] of css.matchAll(/var\((--df-[\w-]+)\)/g))assert.ok(vars[variable],variable+' must exist in the shared palette');
const luminance=hex=>{const rgb=hex.slice(1).match(/../g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;};
for(const [fg,bg] of [['incomeText','incomeSoft'],['expenseText','expenseSoft'],['task','taskSoft'],['forecast','forecastSoft'],['warning','warningSoft'],['balanceText','balanceSoft']])assert.ok((luminance(VISUAL_THEME[bg])+.05)/(luminance(VISUAL_THEME[fg])+.05)>=4.5,fg+' has readable contrast');
console.log('PASS semantic presentation: real reconciliation vs import, partial/overpayments, scope/account/sign/date checks, independent doc/classification alerts, source is not receipt, read-only calendar, stable bank colors and text contrast.');
