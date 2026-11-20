import {financialHierarchy,CLASSIFICATION_STATES} from './financial-hierarchy.js?v=30';
import {INDEXADOR_CATEGORIES} from './classification-reference.js?v=28';
import {statementOrder} from './statement-model.js?v=17';
import {planningRemaining} from './planning-book-model.js?v=31';

const unknown=amount=>({category:null,label:'A classificar',amount,status:'Classificação não informada'});
const noValue=note=>({heading:'Classificação e valor',valueLabel:'Valor financeiro',rows:[{label:'Não se aplica',amount:null,status:'Atividade sem valor financeiro próprio'}],note});
// Read-only presentation. Historical allocations never become a forecast's classification.
export function controlClassification(state,item,all=[]){
  const company=item.company,owned=(collection,id)=>state[collection]?.find(r=>r.id===id&&r.company===company);
  if(item.kind==='coverage')return noValue('Atualizar o extrato é uma ação de conferência, sem valor a classificar.');
  if(item.kind==='task'){
    const task=owned('tasks',item.target);if(!task)return noValue('Contexto da tarefa indisponível nesta empresa.');
    const obligation=owned('obligations',task.obligation),forecast=all.find(f=>f.kind==='forecast'&&f.company===company&&f.id===task.forecast);
    const parent=obligation?{kind:'obligation',target:obligation.id,company}:forecast;
    if(!parent)return noValue('Vincule um compromisso ou previsão para consultar sua classificação e seu valor.');
    const context=controlClassification(state,parent,all);
    return {...context,heading:'Classificação do contexto da tarefa',note:'Valor do compromisso relacionado; a tarefa não acrescenta outro valor. '+(context.note||'')};
  }
  if(item.kind==='obligation'){
    const o=owned('obligations',item.target);if(!o)return noValue('Obrigação indisponível nesta empresa.');
    const catalog=state.classification?.catalogs?.[company]||INDEXADOR_CATEGORIES;
    const valid=o.items?.length&&o.items.every(line=>Number.isSafeInteger(line.amount)&&line.amount>0)&&Number.isSafeInteger(o.items.reduce((n,line)=>n+line.amount,0));
    if(!valid)return {heading:'Classificação da obrigação',valueLabel:'Valor informado',rows:[unknown(null)],note:'Complete os valores da composição para exibir a classificação por item.'};
    const groups=new Map();
    for(const line of o.items){const category=catalog.find(c=>c.id===line.category),key=category?.id||'unclassified';if(!groups.has(key))groups.set(key,category?{category:key,label:category.label,amount:0,status:'Informada na obrigação'}:unknown(0));groups.get(key).amount+=line.amount;}
    const total=o.items.reduce((n,line)=>n+line.amount,0),left=planningRemaining(state,o);
    return {heading:'Classificação da obrigação',valueLabel:'Valor da composição',rows:[...groups.values()],target:{kind:'obligation',id:o.id,label:'Ver composição'},note:left!==total?'Valores da composição total. O saldo em aberto não é distribuído entre classificações sem conferir os pagamentos por item.':'Classificação própria da obrigação. A revisão contábil e a realização financeira são acompanhadas separadamente.'};
  }
  if(item.kind==='forecast'){
    const accounts=new Set(state.accounts.filter(a=>a.company===company).map(a=>a.id));
    const sources=new Set(item.sourceIds||[]);
    const allowed=state.transactions.filter(t=>t.company===company&&accounts.has(t.account)&&!t.archiveReason&&Math.sign(t.amount)===item.direction);
    const matched=allowed.find(t=>t.id===item.matchedTransactionId);
    const latest=matched||allowed.filter(t=>sources.has(t.id)).sort(statementOrder).at(-1);
    const history=latest?{date:latest.date,transaction:latest.id,matched:!!matched,rows:financialHierarchy(state,company,[latest]).flatMap(d=>d.entries).map(e=>({category:e.category==='unclassified'?null:e.category,label:e.label,amount:e.amount,status:CLASSIFICATION_STATES[e.status]||'A classificar'}))}:null;
    return {heading:'Classificação da previsão',valueLabel:'Valor previsto',rows:[unknown(Number.isSafeInteger(item.amount)?item.amount:null)],history,note:'A classificação das ocorrências anteriores é uma referência; ainda não foi atribuída a esta previsão.',target:{kind:'forecast',id:item.id,label:'Ver previsão e fontes'}};
  }
  return noValue('Nenhum valor financeiro relacionado.');
}

export function controlClassificationHTML(a,item,all=[]){
  const c=controlClassification(a.state,item,all),{esc,money,fullDate,btn}=a;
  const rows=values=>values.map(r=>`<div class="control-classification-line"><div><b>${esc(r.label)}</b><small>${esc(r.status)}</small></div><strong>${r.amount===null?'—':money(r.amount)}</strong></div>`).join('');
  return `<section class="control-classification" aria-label="Classificação e valor"><div class="control-classification-heading"><h4>${esc(c.heading)}</h4><span>${esc(c.valueLabel)}</span></div>${rows(c.rows)}${c.history?`<div class="control-classification-history"><div class="control-classification-heading"><b>${c.history.matched?'Ocorrência reconhecida':'Referência mais recente do histórico'} · ${fullDate(c.history.date)}</b><span>Valor do extrato</span></div>${rows(c.history.rows)}${btn('Conferir classificação do lançamento',`data-open="classify" data-id="${esc(c.history.transaction)}"`,'control-classification-source')}</div>`:''}<p>${esc(c.note)}</p>${c.target?btn(esc(c.target.label),`data-open="${c.target.kind}" data-id="${esc(c.target.id)}"`,'control-classification-source'):''}</section>`;
}
