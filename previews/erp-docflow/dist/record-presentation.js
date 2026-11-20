import {obligationDocuments} from './inventory-model.js?v=17';
import {classificationStatus,getClassification} from './classification-model.js?v=29';
import {validDate} from './range-model.js?v=17';

// Presentation only. Reading this status must never confirm a link, pay an obligation,
// review a document/classification, or create tasks. The source statement is not a receipt.
const expected=o=>(o.items||[]).reduce((n,i)=>n+i.amount,0);
const active=o=>o&&!o.cancelled&&o.status!=='cancelled'&&o.monitoringKind!=='estimate';
function compatible(state,t,o,today){
  return active(o)&&t.company===o.company&&!t.archiveReason&&t.confirmed===true&&
    validDate(t.date)&&(!today||t.date<=today)&&Number.isSafeInteger(t.amount)&&
    (o.kind==='in'?t.amount>0:t.amount<0)&&
    state.accounts.some(a=>a.id===t.account&&a.company===o.company)&&(!o.account||t.account===o.account);
}
function linked(state,o,today){
  return state.transactions.filter(t=>t.obligation===o.id&&t.company===o.company&&!t.archiveReason&&(!today||t.date<=today));
}
function documentWarnings(state,o,transactions){
  const sources=new Set(transactions.flatMap(t=>[t.sourceDocument,...(t.additionalSources||[]).map(s=>s.document)]));
  const docs=new Map();
  if(o)for(const d of obligationDocuments(state,o))if(!sources.has(d.id))docs.set(d.id,d);
  for(const t of transactions){
    const r=getClassification(state,t.company,t.id);
    for(const line of r?.lines||[])for(const id of line.documents||[]){
      const d=state.documents.find(d=>d.id===id&&d.company===line.belongsTo);
      if(d&&!sources.has(d.id))docs.set(id,d);
    }
  }
  const warnings=[];
  if(o?.missing)warnings.push('Documentação pendente: '+o.missing);
  if(!docs.size)warnings.push('Documento da operação não vinculado');
  if([...docs.values()].some(d=>d.locked))warnings.push('Documento aguardando senha');
  if([...docs.values()].some(d=>d.status!=='Revisado'))warnings.push('Documentação a conferir');
  return warnings;
}
export function financialPresentation(state,kind,record,today){
  if(!record)return {complete:false,label:'A conciliar',warnings:[]};
  const o=kind==='obligation'?record:state.obligations.find(o=>o.id===record.obligation&&o.company===record.company);
  const tx=kind==='obligation'?linked(state,record,today):[record];
  const all=o?linked(state,o,today):[],confirmed=all.filter(t=>compatible(state,t,o,today));
  const amount=o?expected(o):0,paid=confirmed.reduce((n,t)=>n+Math.abs(t.amount),0);
  const validAmount=Number.isSafeInteger(amount)&&amount>0;
  const complete=kind==='obligation'?!!(active(o)&&validAmount&&paid===amount&&all.every(t=>compatible(state,t,o,today))):
    !!(o&&validAmount&&compatible(state,record,o,today)&&paid<=amount);
  const warnings=documentWarnings(state,o,tx);
  if(tx.some(t=>classificationStatus(state,t.company,t)!=='reviewed'))warnings.push('Classificação a conferir');
  if(o&&paid>amount)warnings.push('Valor conciliado acima do compromisso');
  if(o&&all.some(t=>!compatible(state,t,o,today)))warnings.push('Há vínculo financeiro a conferir');
  if(o&&confirmed.some(t=>t.date>(o.expectedDate||o.due)))warnings.push('Realização após a data prevista');
  if(o&&paid>0&&paid<amount)warnings.push('Obrigação parcialmente conciliada');
  return {complete,label:complete?(kind==='obligation'?'Financeiro conciliado':'Conciliado'):paid>0&&kind==='obligation'?'Conciliação parcial':'A conciliar',warnings:[...new Set(warnings)]};
}
export const warningIcon='<svg class="record-warning-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 22 21H2Z"/><path d="M12 9v5m0 3v1"/></svg>';
export function presentationHTML(a,p,{compact=false}={}){
  if(!p)return '';
  return `<span class="record-status-line"><span class="record-reconciliation ${p.complete?'is-complete':''}">${p.complete?'✓ ':''}${a.esc(p.label)}</span>${p.warnings.length?`<span class="record-warning" title="${a.esc(p.warnings.join(' · '))}" aria-label="Atenção: ${a.esc(p.warnings.join(' · '))}">${warningIcon}<span>${compact?p.warnings.length+' pendência(s)':a.esc(p.warnings.join(' · '))}</span></span>`:''}</span>`;
}
