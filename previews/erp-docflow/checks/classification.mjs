import assert from 'node:assert/strict';
import {SEED} from '../dist/data.js';
import {groupMovements,movementCategoryLabel} from '../dist/movement-group-model.js';
import {INDEXADOR_CATEGORIES} from '../dist/classification-reference.js';
import {classificationCatalog,classificationStatus,getClassification,saveClassification,saveCategory,centsInput,classificationSummary} from '../dist/classification-model.js';
import {createClassification} from '../dist/classification-ui.js';
import {mergeImportedState} from '../dist/import-migration.js';

const state=structuredClone(SEED),company=state.companies[0].id,now='2026-11-20';
// Constructed test records; independent of private bank history.
state.accounts.push({id:'test-bank',company,name:'Conta fictícia',opening:0});
state.transactions.push({id:'synthetic-credit',company,account:'test-bank',date:'2026-10-10',amount:200000,description:'Recebimento fictício',imported:true},{id:'synthetic-debit',company,account:'test-bank',date:'2026-10-11',amount:-5000,description:'Pagamento fictício',imported:true});
const financial=JSON.stringify([state.transactions,state.accounts,state.obligations,state.documents]);
const catalog=classificationCatalog(state,company),cat=label=>catalog.find(c=>c.label===label).id;
assert.equal(catalog.length,68);assert.equal(new Set(catalog.map(c=>c.group)).size,9);
assert.deepEqual(catalog.map(c=>c.label),INDEXADOR_CATEGORIES.map(c=>c.label));
assert.ok(catalog.every(c=>!c.accountCode&&!c.mappingReviewed),'Old mappings never become confirmed accounting mappings');
assert.equal(catalog.find(c=>c.label==='IOF').source.sheet,'Modelo público');
for(const [input,result] of [['1.234,56',123456],['0,01',1],['1234',123400],['',null],['0',0]])assert.equal(centsInput(input),result);
for(const value of ['1,234','1.2','-1','NaN','1e4','1.234,567'])assert.ok(Number.isNaN(centsInput(value)),value);
const t=state.transactions.find(t=>t.amount>100000),amount=Math.abs(t.amount);
const line=(value,category,purpose='revenue')=>({id:crypto.randomUUID(),amount:value,category,purpose,belongsTo:company,competence:'2026-10',costCenter:'',asset:'',contract:'',obligation:'',documents:[],note:'',parcel:''});
const input={party:'Inquilino informado',complement:'Aluguel e rateio de energia',lines:[line(amount-12345,cat('Receitas')),line(12345,cat('Despesas Com Energia'),'passThrough')]};
saveClassification(state,company,t.id,input,'draft',now);
assert.equal(classificationStatus(state,company,t),'draft');
assert.equal(classificationSummary(state,company,[t]).groups.length,0,'Drafts are excluded from reviewed totals');
const reviewed=saveClassification(state,company,t.id,input,'reviewed',now);
assert.equal(classificationStatus(state,company,t),'reviewed');assert.equal(reviewed.history.length,1);
assert.equal(movementCategoryLabel(t,state),'Composição mista · 2 classificações');
assert.equal(groupMovements([t],state,'category').reduce((n,g)=>n+g.net,0),t.amount);
const sums=classificationSummary(state,company,[t]);
assert.equal(sums.groups.reduce((n,g)=>n+g.incoming,0),amount);assert.equal(sums.groups.reduce((n,g)=>n+g.outgoing,0),0);
assert.equal(sums.groups.find(g=>g.purpose==='passThrough').incoming,12345);
const snapshot=JSON.stringify(getClassification(state,company,t.id));
for(const invalid of [
 {...input,lines:[line(amount+1,cat('Receitas'))]},
 {...input,lines:[line(amount-1,cat('Receitas'))]},
 {...input,lines:[line(amount,'missing')]},
 {...input,lines:[{...line(amount,cat('Receitas')),competence:''}]},
 {...input,lines:[{...line(amount,cat('Receitas')),amount:1.5}]},
 {...input,lines:[{...line(amount,cat('Receitas')),asset:'foreign'}]}
]){assert.throws(()=>saveClassification(state,company,t.id,invalid,'reviewed',now));assert.equal(JSON.stringify(getClassification(state,company,t.id)),snapshot);}
assert.throws(()=>saveClassification(state,'other',t.id,input,'reviewed',now));
state.companies.push({id:'other',name:'Outra empresa'});state.assets.push({id:'foreign',name:'Ativo da outra empresa',company:'other'});
const cross={...input,lines:[{...line(amount,cat('Receitas')),belongsTo:'other',asset:'foreign'}]};
saveClassification(state,company,t.id,cross,'reviewed',now);
assert.equal(getClassification(state,company,t.id).lines[0].belongsTo,'other');assert.equal(getClassification(state,'other',t.id),null);
assert.equal(classificationSummary(state,company,[t]).groups[0].company,'other');
assert.ok(classificationCatalog(state,'other').every(c=>!c.mappingReviewed));
const originalCategory=catalog.find(c=>c.id===cat('Receitas'));
saveCategory(state,company,originalCategory.id,{...originalCategory,accountCode:'100',accountLabel:'Conta informada',mappingReviewed:true},now);
assert.equal(classificationCatalog(state,'other').find(c=>c.id===originalCategory.id).accountCode,'');
assert.equal(originalCategory.source.realized,'Receitas');assert.equal(originalCategory.history.length,1);
assert.throws(()=>saveCategory(state,company,originalCategory.id,{...originalCategory,accountCode:'',mappingReviewed:true},now));
assert.equal(JSON.stringify([state.transactions,state.accounts,state.obligations,state.documents]),financial,'Classification must not settle, reconcile or rewrite source values');
assert.equal(movementCategoryLabel(t,state),'Receitas');
const migrated=mergeImportedState({...state,dataset:{...state.dataset,id:'prior-import'}},SEED);
assert.deepEqual(migrated.classification,state.classification);
const changed={...t,amount:t.amount+1};assert.equal(classificationStatus(state,company,changed),'draft','Changed bank values require review again');

// UI behavior with controlled state. This is not browser visual verification.
let html='',downloaded,opened,stored=0;
const a={state,company,month:t.date.slice(0,7),NOW:now,current:{},
 esc:v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;'),money:v=>v==null?'—':'R$ '+(v/100).toFixed(2),fullDate:d=>d?.split('-').reverse().join('/')||'—',
 btn:(label,attrs)=>'<button '+attrs+'>'+label+'</button>',pill:(label,tone)=>'<span class="'+tone+'">'+label+'</span>',
 titleBlock:(title,sub,actions)=>'<h1>'+title+'</h1>'+actions,monthSelect:()=>'',empty:(title)=>title,link:(label,kind,id)=>'<button data-open="'+kind+'" data-id="'+id+'">'+label+'</button>',
 get:(type,id)=>state[type].find(x=>x.id===id),scope:type=>state[type].filter(x=>x.company===a.company),
 render:()=>{html=ui.page()},open:(kind,id)=>{opened={kind,id}},draw(){},closeAll(){},save(){stored++},toast(){},download:(name,content)=>{downloaded={name,content}},
 formShell:(title,sub,body,kind,id)=>'<form data-form="'+kind+'" data-id="'+id+'">'+body+'</form>'};
const ui=createClassification(a,()=>'<div>Entrega anterior preservada</div>');a.render();
assert.match(html,/Classificação e contexto/);assert.match(html,/Composição revisada/);assert.doesNotMatch(html,/NaN|Infinity/);
ui.click({classificationTab:'catalog'});assert.match(html,/IOF/);assert.match(html,/Referência do modelo/);
ui.click({classificationTab:'summary'});assert.match(html,/Resumo das classificações/);
ui.click({classificationTab:'legacy'});assert.match(html,/Entrega anterior preservada/);
ui.click({classificationTab:'entries'});
const drawer=ui.dialog('classify',t.id);assert.match(drawer.body,/name="competence-0"/);assert.match(drawer.body,/data-classification-review/);assert.match(drawer.body,/ORIGEM BANCÁRIA PRESERVADA/);
assert.match(ui.summaryCard(t),/data-open="asset"/);
assert.match(ui.dialog('classification-category',originalCategory.id).body,/Plano do contador/);
ui.click({classificationFilterButton:'reviewed'});ui.click({classificationExport:'1'});
assert.match(downloaded.content,/Valor bancário \(somar uma vez por ID\)/);assert.match(downloaded.content,/Conta informada/);assert.match(downloaded.content,/Outra empresa/);
const exportedRows=downloaded.content.split('\r\n').slice(1);assert.equal(exportedRows.length,1);
// Export a split credit: its bank amount appears only once; each item remains signed.
saveClassification(state,company,t.id,input,'reviewed',now);ui.click({classificationExport:'1'});
let csvRows=downloaded.content.split('\r\n').slice(1).map(row=>row.slice(1,-1).split('";"'));
assert.equal(csvRows.length,2);assert.equal(csvRows.filter(row=>row[7]!=='').length,1);
assert.equal(csvRows.reduce((n,row)=>n+centsInput(row[10]),0),amount);
const debit=state.transactions.find(x=>x.amount<0&&x.date.startsWith(a.month));
saveClassification(state,company,debit.id,{party:'=HYPERLINK(test)',complement:'',lines:[line(-debit.amount,cat('Tarifas e Despesas Bancarias'),'expense')]},'reviewed',now);
ui.click({classificationExport:'1'});
assert.match(downloaded.content,/'=HYPERLINK/);
assert.ok(downloaded.content.includes('"'+(debit.amount/100).toFixed(2).replace('.',',')+'"'));
saveClassification(state,company,t.id,cross,'reviewed',now);
const badForm={dataset:{form:'classification',id:t.id},querySelector:()=>({textContent:'',scrollIntoView(){}})};
const formData=new Map([['party','Pessoa'],['complement',''],...Object.entries(a.current.classificationDraft.lines[0]).filter(([key])=>!['id','documents'].includes(key)).map(([key,value])=>[key+'-0',value])]);formData.getAll=()=>[];
formData.set('amount-0','0,01');ui.submit(badForm,formData);assert.equal(stored,1,'Partial drafts can be saved explicitly');
assert.equal(classificationStatus(state,company,t),'draft');assert.equal(classificationSummary(state,company,[t]).groups.length,0);
a.company='other';a.render();assert.doesNotMatch(html,new RegExp(t.id));
assert.equal(JSON.stringify([state.transactions,state.accounts,state.obligations,state.documents]),financial);
console.log('Verified original names, cent rounding, split totals, partial drafts, atomic validation, explicit cross-company ownership, reference isolation, mapping review, revision history, migration, routes, filters, CSV and immutable bank data. Visual QA unavailable.');
