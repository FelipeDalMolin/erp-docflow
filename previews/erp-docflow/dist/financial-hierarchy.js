import {classificationStatus,getClassification} from './classification-model.js?v=29';
import {INDEXADOR_CATEGORIES} from './classification-reference.js?v=28';
import {statementOrder} from './statement-model.js?v=17';

export const CLASSIFICATION_STATES={initial:'Inicial · a revisar',reviewed:'Composição revisada',draft:'Rascunho · a classificar',unclassified:'A classificar',excluded:'Inicial não incluída'};
const pending={id:'unclassified',label:'A classificar'};
const unique=entries=>new Set(entries.map(e=>e.transaction.id)).size;
export function financialHierarchy(state,company,transactions,{includeInitial=true}={}){
  const accounts=new Set(state.accounts.filter(a=>a.company===company).map(a=>a.id));
  const catalog=state.classification?.catalogs?.[company]||INDEXADOR_CATEGORIES;
  const map=new Map(catalog.map(c=>[c.id,c]));
  const directions=[{id:'incoming',label:'Entradas',sign:1},{id:'outgoing',label:'Saídas',sign:-1}].map(d=>({...d,groups:[],entries:[],total:0,count:0}));
  // A bank ID appears once in this input; each valid allocation contributes only its own cents.
  for(const t of [...new Map(transactions.filter(t=>accounts.has(t.account)&&!t.archiveReason).map(t=>[t.id,t])).values()].sort(statementOrder)){
    if(!Number.isSafeInteger(t.amount)||t.amount===0)continue;
    const direction=directions[t.amount>0?0:1],status=classificationStatus(state,company,t),record=getClassification(state,company,t.id);
    const usable=(status==='reviewed'||includeInitial&&status==='initial')&&record?.lines?.length&&record.lines.every(l=>Number.isSafeInteger(l.amount)&&l.amount>0&&map.has(l.category))&&record.lines.reduce((n,l)=>n+l.amount,0)===Math.abs(t.amount);
    const lines=usable?record.lines:[{id:'pending',amount:Math.abs(t.amount),category:pending.id}];
    for(const [index,line] of lines.entries()){
      const category=usable?map.get(line.category):pending;
      direction.entries.push({id:t.id+':'+line.id,transaction:t,amount:line.amount,category:category.id,label:category.label,status:status==='initial'&&!includeInitial?'excluded':usable?status:status==='draft'?'draft':'unclassified',line:usable?line:null,part:usable&&lines.length>1,index:index+1,parts:lines.length});
    }
  }
  for(const d of directions){
    const groups=new Map();
    for(const e of d.entries){if(!groups.has(e.category))groups.set(e.category,{id:e.category,label:e.label,entries:[],total:0});const g=groups.get(e.category);g.entries.push(e);g.total+=e.amount;}
    d.groups=[...groups.values()].map(g=>({...g,count:unique(g.entries),initial:unique(g.entries.filter(e=>e.status==='initial')),reviewed:unique(g.entries.filter(e=>e.status==='reviewed'))})).sort((a,b)=>a.id===pending.id?1:b.id===pending.id?-1:a.label.localeCompare(b.label,'pt-BR'));
    d.total=d.entries.reduce((n,e)=>n+e.amount,0);d.count=unique(d.entries);
  }
  return directions;
}

// A partially paid obligation has no allocation of payments to items yet. Do not prorate it.
export function obligationCategory(state,company,obligation){
  const catalog=state.classification?.catalogs?.[company]||INDEXADOR_CATEGORIES;
  const ids=new Set((obligation.items||[]).map(item=>item.category||''));
  if(!ids.size||ids.has(''))return pending;
  if(ids.size>1)return {id:'mixed-pending',label:'Composição a distribuir'};
  return catalog.find(c=>c.id===[...ids][0])||pending;
}
