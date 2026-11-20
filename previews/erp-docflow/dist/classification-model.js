import {INDEXADOR_CATEGORIES} from './classification-reference.js?v=28';
import {validDate} from './range-model.js?v=17';

export const PURPOSES={revenue:'Receita própria',expense:'Despesa própria',passThrough:'Rateio / repasse / reembolso',transfer:'Transferência',capital:'Aporte / empréstimo / retirada',asset:'Investimento / ativo',other:'Outra natureza'};
const text=(v,max=300)=>String(v??'').trim().slice(0,max);
export function classificationStore(state){
  state.classification??={version:1,catalogs:{},records:{}};
  return state.classification;
}
export function classificationCatalog(state,company){
  if(!state.companies.some(c=>c.id===company))return [];
  const store=classificationStore(state);
  store.catalogs[company]??=INDEXADOR_CATEGORIES.map(c=>({...structuredClone(c),active:true,accountCode:'',accountLabel:'',pendingCode:'',pendingLabel:'',mappingReviewed:false}));
  return store.catalogs[company];
}
export function classificationTransaction(state,company,id){
  return state.transactions.find(t=>t.id===id&&state.accounts.some(a=>a.id===t.account&&a.company===company));
}
export function getClassification(state,company,id){
  const r=state.classification?.records?.[id];
  return r?.company===company&&classificationTransaction(state,company,id)?r:null;
}
export function classificationStatus(state,company,t){
  const r=getClassification(state,company,t.id);
  if(!r)return 'unclassified';
  if(r.status==='initial'&&r.bankAmount===t.amount&&r.bankDate===t.date&&r.bankAccount===t.account&&r.provenance?.bankDescription===t.description)return 'initial';
  if(r.status==='reviewed'&&r.bankAmount===t.amount&&r.bankDate===t.date)return 'reviewed';
  return 'draft';
}
export function centsInput(value){
  const s=String(value??'').trim().replace(/\s|R\$/g,'');
  if(!s)return null;
  if(!/^(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,2})?$/.test(s))return NaN;
  const [whole,fraction='']=s.replaceAll('.','').split(',');
  const cents=Number(whole)*100+Number(fraction.padEnd(2,'0'));
  return Number.isSafeInteger(cents)?cents:NaN;
}
export function saveClassification(state,company,id,input,status,now){
  const t=classificationTransaction(state,company,id);
  if(!t)throw Error('Lançamento indisponível nesta empresa.');
  if(!['draft','reviewed'].includes(status))throw Error('Situação de revisão inválida.');
  if(!Array.isArray(input.lines)||!input.lines.length||input.lines.length>50)throw Error('Informe de 1 a 50 itens na composição.');
  const catalog=classificationCatalog(state,company),prior=getClassification(state,company,id);
  const lines=input.lines.map((raw,index)=>{
    const line={id:raw.id||crypto.randomUUID(),amount:raw.amount,category:text(raw.category),purpose:text(raw.purpose),belongsTo:text(raw.belongsTo),competence:text(raw.competence),costCenter:text(raw.costCenter),asset:text(raw.asset),contract:text(raw.contract),obligation:text(raw.obligation),parcel:text(raw.parcel),note:text(raw.note,1000),documents:[...new Set(raw.documents||[])]};
    const prefix='Item '+(index+1)+': ';
    if(line.amount!==null&&(!Number.isSafeInteger(line.amount)||line.amount<=0))throw Error(prefix+'informe um valor positivo em reais e centavos.');
    if(line.category&&!catalog.some(c=>c.id===line.category&&(c.active||prior?.lines.some(l=>l.category===c.id))))throw Error(prefix+'classificação indisponível.');
    if(line.purpose&&!PURPOSES[line.purpose])throw Error(prefix+'natureza inválida.');
    if(!state.companies.some(c=>c.id===line.belongsTo))throw Error(prefix+'indique a empresa à qual pertence.');
    if(line.competence&&!validDate(line.competence+'-01'))throw Error(prefix+'competência inválida.');
    for(const [key,collection] of [['asset','assets'],['contract','contracts'],['obligation','obligations']]){
      if(line[key]&&!state[collection].some(x=>x.id===line[key]&&x.company===line.belongsTo))throw Error(prefix+'a referência deve pertencer à empresa indicada.');
    }
    const contract=state.contracts.find(c=>c.id===line.contract),obligation=state.obligations.find(o=>o.id===line.obligation);
    if(contract?.asset&&line.asset&&contract.asset!==line.asset)throw Error(prefix+'o contrato e o ativo indicados não correspondem.');
    if(obligation?.contract&&line.contract&&obligation.contract!==line.contract)throw Error(prefix+'a obrigação e o contrato indicados não correspondem.');
    if(obligation?.asset&&line.asset&&obligation.asset!==line.asset)throw Error(prefix+'a obrigação e o ativo indicados não correspondem.');
    for(const doc of line.documents)if(!state.documents.some(d=>d.id===doc&&d.company===line.belongsTo))throw Error(prefix+'documento de outra empresa ou indisponível.');
    if(status==='reviewed'&&(!line.category||!line.purpose||!line.competence||line.amount===null))throw Error(prefix+'preencha classificação, natureza, competência e valor antes de revisar.');
    return line;
  });
  if(new Set(lines.map(l=>l.id)).size!==lines.length)throw Error('Há itens duplicados na composição.');
  const allocated=lines.reduce((n,l)=>n+(l.amount||0),0);
  if(!Number.isSafeInteger(allocated)||allocated>Math.abs(t.amount))throw Error('A composição ultrapassa o valor do lançamento.');
  if(status==='reviewed'&&allocated!==Math.abs(t.amount))throw Error('Distribua o valor integral do lançamento antes de concluir a revisão.');
  const record={company,transaction:id,bankAmount:t.amount,bankDate:t.date,party:text(input.party),complement:text(input.complement,1000),status,lines,updatedAt:now,revision:(prior?.revision||0)+1,history:[...(prior?.history||[])]};
  if(prior?.provenance)record.provenance=structuredClone(prior.provenance);
  if(prior){const {history,...snapshot}=prior;record.history.push(structuredClone(snapshot));}
  classificationStore(state).records[id]=record;
  return record;
}
export function saveCategory(state,company,id,input,now){
  const list=classificationCatalog(state,company),old=list.find(c=>c.id===id);
  if(id&&!old)throw Error('Classificação indisponível nesta empresa.');
  const label=text(input.label),group=text(input.group);
  if(!label||!group)throw Error('Preencha o grupo e o nome da classificação.');
  if(list.some(c=>c.id!==id&&c.label.toLocaleLowerCase('pt-BR')===label.toLocaleLowerCase('pt-BR')&&c.group.toLocaleLowerCase('pt-BR')===group.toLocaleLowerCase('pt-BR')))throw Error('Já existe uma classificação com esse nome neste grupo.');
  const next={...old,id:old?.id||'category-'+crypto.randomUUID(),label,group,active:input.active!==false,accountCode:text(input.accountCode,80),accountLabel:text(input.accountLabel),pendingCode:text(input.pendingCode,80),pendingLabel:text(input.pendingLabel),mappingReviewed:input.mappingReviewed===true,updatedAt:now,history:[...(old?.history||[])]};
  if(next.mappingReviewed&&(!next.accountCode||!next.accountLabel))throw Error('Informe código e nome da conta para registrar a correspondência como revisada.');
  if(old){const {history,...snapshot}=old;next.history.push(structuredClone(snapshot));Object.assign(old,next);}else list.push(next);
  return next;
}
export function classificationSummary(state,company,transactions,{includeInitial=false}={}){
  const categories=classificationCatalog(state,company),groups=new Map();let unallocated=0,draft=0,initial=0;
  for(const t of transactions){
    const r=getClassification(state,company,t.id);
    const status=classificationStatus(state,company,t);
    if(status!=='reviewed'&&!(includeInitial&&status==='initial')){unallocated+=Math.abs(t.amount);if(r)draft++;continue;}
    if(status==='initial')initial++;
    for(const line of r.lines){
      const category=categories.find(c=>c.id===line.category),key=[line.category,line.purpose,line.belongsTo].join('|');
      if(!groups.has(key))groups.set(key,{category:category?.label||'Classificação indisponível',group:category?.group||'',purpose:line.purpose,company:line.belongsTo,incoming:0,outgoing:0,transactions:new Set()});
      const item=groups.get(key);item[t.amount>0?'incoming':'outgoing']+=line.amount;item.transactions.add(t.id);
    }
  }
  return {groups:[...groups.values()].map(g=>({...g,count:g.transactions.size,transactions:[...g.transactions]})),unallocated,draft,initial};
}
