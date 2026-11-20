import assert from 'node:assert/strict';
import {SEED} from '../dist/data.js';
import {INITIAL_CLASSIFICATION} from '../dist/classification-initial-data.js';
import {INDEXADOR_SOURCE,INDEXADOR_CATEGORIES} from '../dist/classification-reference.js';

assert.equal(SEED.dataset.kind,'empty');
assert.deepEqual(INITIAL_CLASSIFICATION.decisions,[]);
assert.deepEqual(INITIAL_CLASSIFICATION.rules,{});
assert.deepEqual(INITIAL_CLASSIFICATION.source,{});
assert.equal(INDEXADOR_SOURCE.file,'Catálogo de exemplo');
assert.ok(!INDEXADOR_SOURCE.sha256);
assert.ok(INDEXADOR_CATEGORIES.every(c=>c.source.sheet==='Modelo público'&&!c.source.range));
assert.equal(SEED.companies.length,1);
for(const key of ['accounts','transactions','archivedTransactions','assets','contracts','obligations','documents','tasks','reviewed'])assert.deepEqual(SEED[key],[],key);
const elements=new Map(),listeners=new Map(),windowEvents=new Map();
const oldState=JSON.stringify({sentinel:'previous preview is not read or modified'});
const storage=new Map([['docflow-statements-v1',oldState]]),reads=[];
const element=()=>({innerHTML:'',style:{},classList:{add(){},remove(){},contains(){return false}},focus(){},querySelector(){return null},querySelectorAll(){return []}});
globalThis.document={getElementById:id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id)},body:{style:{}},activeElement:element(),addEventListener:(k,fn)=>{if(!listeners.has(k))listeners.set(k,[]);listeners.get(k).push(fn)},querySelector:()=>null,querySelectorAll:()=>[]};
globalThis.window={scrollY:0,scrollTo(){},addEventListener:(k,fn)=>windowEvents.set(k,fn)};
globalThis.location={hash:'#home/control'};
globalThis.history={replaceState(_,__,hash){location.hash=hash}};
globalThis.localStorage={getItem:k=>{reads.push(k);return storage.get(k)||null},setItem:(k,v)=>storage.set(k,v)};
globalThis.CSS={escape:v=>v};globalThis.matchMedia=()=>({matches:false});
await import('../dist/app.js');
const app=elements.get('app'),modal=elements.get('modal');
for(const hash of ['#home/control','#home/calendar','#home/overview','#flow','#companies','#banks','#assets','#contracts','#documents','#obligations','#tasks','#accounting']){
  location.hash=hash;windowEvents.get('hashchange')();
  assert.ok(app.innerHTML.includes('Empresa de exemplo'),hash);
  assert.ok(app.innerHTML.includes('Base inicial vazia'),hash);
  assert.ok(!/NaN|Infinity|dados reais/.test(app.innerHTML),hash);
}
function click(dataset){const button={dataset,disabled:false};for(const fn of listeners.get('click')||[])fn({target:{closest:()=>button},preventDefault(){}});}
click({open:'statement-import'});assert.ok(modal.innerHTML.includes('Nenhum extrato incluído'));
assert.ok(!modal.innerHTML.includes('import-audit.json'));
click({action:'close'});click({open:'about'});assert.ok(modal.innerHTML.includes('sem contas, lançamentos ou documentos'));
click({open:'reset'});assert.ok(modal.innerHTML.includes('base inicial vazia'));
click({action:'reset-confirm'});
const saved=JSON.parse(storage.get('docflow-public-preview-v1'));
for(const key of ['accounts','transactions','documents','obligations','tasks'])assert.deepEqual(saved[key],[],key);
assert.deepEqual([...new Set(reads)],['docflow-public-preview-v1']);
assert.equal(storage.get('docflow-statements-v1'),oldState);
console.log('PASS public bootstrap: empty data, 12 routes, import/about/reset dialogs and storage isolation. Controlled DOM only.');
