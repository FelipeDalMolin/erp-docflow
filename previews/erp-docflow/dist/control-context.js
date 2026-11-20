import {chartMovementReferences} from './chart-correspondence-model.js?v=21';
import {obligationDocuments} from './inventory-model.js?v=17';

const collections={obligation:'obligations',contract:'contracts',asset:'assets',document:'documents',account:'accounts',task:'tasks'};
const labels={obligation:'Obrigação',contract:'Contrato',asset:'Ativo',document:'Documento',forecast:'Previsão'};

// A relationship in the historical evidence is not inherited by the new forecast.
export function controlContext(state,item,forecasts=[]){
  const company=item.company,owned=(kind,id)=>state[collections[kind]]?.find(r=>r.id===id&&r.company===company);
  const record=owned(item.kind,item.target),direct=new Map(),historical=new Map(),banks=new Map();
  const companyName=state.companies.find(c=>c.id===company)?.name||'Empresa atual';
  function add(kind,id,target=direct){const r=owned(kind,id);if(r)target.set(kind+':'+id,{kind,id,label:r.name||r.title||labels[kind],type:labels[kind]});return r;}
  function bank(id){const r=owned('account',id);if(r)banks.set(id,{id,name:r.name,label:r.label});}
  function related(r,target=direct){
    if(!r)return;
    const o=r.obligation?add('obligation',r.obligation,target):null;
    const contract=add('contract',r.contract||o?.contract,target);
    add('asset',r.asset||o?.asset||contract?.asset,target);
    if(r.doc)add('document',r.doc,target);
    for(const id of r.docs||[])add('document',id,target);
    if(target===direct){bank(r.account||r.bankAccount||o?.account);}
  }
  related(record);
  if(item.kind==='obligation'&&record)for(const d of obligationDocuments(state,record))add('document',d.id);
  if(item.kind==='coverage')bank(item.target);
  if(record?.forecast){
    const forecast=forecasts.find(f=>f.kind==='forecast'&&f.company===company&&f.id===record.forecast);
    const snapshot=state.forecastOverrides?.[company+':'+record.forecast]?.snapshot;
    const f=forecast||(snapshot?.company===company?snapshot:null);
    if(f)direct.set('forecast:'+f.id,{kind:'forecast',id:f.id,label:f.title,type:'Previsão'});
  }
  const sources=item.kind==='forecast'?(item.sourceIds||[]).map(id=>state.transactions.find(t=>t.id===id&&t.company===company)).filter(Boolean):[];
  const documents=new Set(),histories=new Set();
  for(const id of item.accounts||[])bank(id);
  for(const tx of sources){
    bank(tx.account);if(tx.history)histories.add(tx.history);
    const refs=chartMovementReferences(state,tx,company);
    if(refs.source)documents.add(refs.source.id);
    for(const kind of ['obligation','contract','asset'])if(refs[kind])add(kind,refs[kind].id,historical);
  }
  return {company,companyName,record,banks:[...banks.values()],direct:[...direct.values()],historical:[...historical.values()],sources,sourceCount:sources.length,documentCount:documents.size,
    sourceMonths:[...new Set(sources.map(t=>t.date.slice(0,7)))].sort(),lastDate:sources.map(t=>t.date).sort().at(-1),histories:[...histories],note:item.kind==='forecast'?item.decision?.note:'',
    title:item.kind==='forecast'?item.title.replace(/^INTERNET\s*--\s*/i,''):item.title,
    direction:item.kind==='forecast'?(item.direction>0?'Entrada prevista':'Saída prevista'):item.kind==='obligation'?(record?.kind==='in'?'A receber':'A pagar'):null,
    origin:({forecast:'Previsão do histórico',obligation:'Obrigação registrada',task:'Tarefa',coverage:'Cobertura bancária'})[item.kind]||'Acompanhamento'};
}
