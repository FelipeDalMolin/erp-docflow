import {remaining,total} from './data.js?v=17';
import {monthDays} from './workbook-model.js?v=17';
import {obligationControl,taskControl} from './control-model.js?v=23';
import {forecastItems} from './forecast-model.js?v=23';

export function calendarCells(month) {
  const days=monthDays(month),first=new Date(days[0]+'T12:00:00Z');
  const offset=(first.getUTCDay()+6)%7;
  first.setUTCDate(first.getUTCDate()-offset);
  const count=Math.ceil((offset+days.length)/7)*7;
  return Array.from({length:count},(_,i)=>{
    const d=new Date(first);d.setUTCDate(d.getUTCDate()+i);
    const date=d.toISOString().slice(0,10);
    return {date,inMonth:date.startsWith(month),day:d.getUTCDate()};
  });
}

export function calendarEvents(state,company,month,filters={}) {
  return collectCalendarEvents(state,company,date=>date.startsWith(month),filters);
}
export function calendarRangeEvents(state,company,range,filters={}) {
  return collectCalendarEvents(state,company,date=>date>=range.start&&date<=range.end,filters);
}
function collectCalendarEvents(state,company,matches,filters) {
  const enabled={realized:true,obligation:true,task:true,forecast:true,completed:false,...filters};
  const events=[];
  if(enabled.realized)for(const t of state.transactions.filter(t=>t.company===company&&matches(t.date))) {
    const o=state.obligations.find(o=>o.id===t.obligation&&o.company===company);
    events.push({id:'movement:'+t.id,date:t.date,type:'realized',title:o?.party||t.description,
      detail:o?.title||t.description,amount:t.amount,kind:t.imported?'transaction':'obligation',target:t.imported?t.id:t.obligation,sequence:t.sourceSequence||0,account:t.account,
      label:t.amount>=0?'Recebido':'Pago',done:true});
  }
  if(enabled.obligation)for(const o of state.obligations.filter(o=>o.company===company&&matches(o.due))) {
    const monitoring=filters.asOf?obligationControl(state,o,filters.asOf):null;
    if(filters.asOf&&!monitoring)continue;
    const balance=monitoring?monitoring.remaining:remaining(state,o),done=monitoring?monitoring.group==='resolved':balance===0;
    if(!enabled.completed&&done)continue;
    events.push({id:'due:'+o.id,date:o.due,type:'obligation',title:o.title,detail:o.party,
      amount:balance||total(o),kind:'obligation',target:o.id,done,urgency:monitoring?.group,
      label:monitoring?.label||(balance===0?'Liquidada':o.kind==='in'?'A receber':'A pagar')});
  }
  if(enabled.task)for(const t of state.tasks.filter(t=>t.company===company&&matches(t.due))) {
    if(!enabled.completed&&t.done)continue;
    events.push({id:'task:'+t.id,date:t.due,type:'task',title:t.title,detail:t.owner,
      kind:'task',target:t.id,done:t.done,urgency:filters.asOf?taskControl(t,filters.asOf).group:undefined,label:t.done?'Concluída':'Tarefa'});
  }
  if(enabled.forecast&&filters.asOf)for(const f of forecastItems(state,company,filters.asOf).filter(f=>matches(f.date)&&!f.hidden&&(enabled.completed||f.group!=='resolved'))){
    events.push({id:f.id,date:f.date,type:'forecast',title:f.title,detail:f.months+' meses de histórico · sem classificação',amount:f.amount*f.direction,kind:'forecast',target:f.id,done:f.group==='resolved',urgency:f.group,label:f.label});
  }
  const order={realized:0,obligation:1,task:2,forecast:3};
  return events.sort((x,y)=>x.date.localeCompare(y.date)||order[x.type]-order[y.type]||(x.account||'').localeCompare(y.account||'')||(x.sequence||0)-(y.sequence||0)||x.title.localeCompare(y.title,'pt-BR'));
}

const PROFILE_DEFAULTS={
  aurora:{purpose:'Administrar os imóveis, acompanhar locações e organizar a prestação de contas.',
    organization:'Gestão patrimonial',responsible:'Você',accounting:'Contabilidade Exemplo',taxStatus:'A confirmar',
    conditions:[
      {id:'aurora-rent',title:'Separar aluguel e valores recuperáveis',area:'Contratos',description:'Discriminar o valor base, o rateio e os encargos de cada cobrança. Manter a regra e o documento de origem acessíveis.',owner:'Você'},
      {id:'aurora-asset',title:'Relacionar despesas ao bem',area:'Documentos',description:'Identificar o imóvel ou veículo a que se refere cada manutenção, tributo ou pagamento.',owner:'Você'},
      {id:'aurora-review',title:'Conferir antes da entrega contábil',area:'Contabilidade',description:'Revisar a composição e os documentos do período. O pagamento e a conferência documental têm estados independentes.',owner:'Contabilidade'}]},
  horizonte:{purpose:'Acompanhar contratos de serviços, despesas operacionais e documentos da empresa.',
    organization:'Prestação de serviços',responsible:'Você',accounting:'A definir',taxStatus:'A confirmar',
    conditions:[{id:'horizonte-period',title:'Identificar o período dos serviços',area:'Contratos',description:'Indicar o contrato e a competência em cada cobrança de serviços.',owner:'Você'}]}
};
const PROFILE_DOCS=[
  {id:'profile-aurora-cadastro',company:'aurora',name:'Cadastro institucional · Aurora',type:'Cadastro institucional',status:'A revisar',pages:[{title:'Ficha da empresa',subtitle:'Aurora Participações · documento fictício',lines:['Atividade: locação e gestão patrimonial.','Localização: Campinas / SP.','Cadastro fiscal e societário: a complementar pelo responsável.','Esta ficha é um exemplo de organização, sem valor oficial.']}]},
  {id:'profile-aurora-documentos',company:'aurora',name:'Orientações de documentação · Aurora',type:'Orientações internas',status:'Revisado',pages:[{title:'Documentos e prestação de contas',subtitle:'Rotina ilustrativa da empresa',lines:['Preservar cada documento original.','Relacionar cobranças e comprovantes aos contratos, bens e obrigações.','Conferir separadamente pagamento, documento e composição.','Preparar um índice mensal revisável antes do compartilhamento.']}]},
  {id:'profile-horizonte-cadastro',company:'horizonte',name:'Cadastro institucional · Horizonte',type:'Cadastro institucional',status:'A revisar',pages:[{title:'Ficha da empresa',subtitle:'Horizonte Serviços · documento fictício',lines:['Atividade: serviços e consultoria.','Localização: São Paulo / SP.','Cadastro e condições operacionais: a confirmar.','Esta ficha é um exemplo de organização, sem valor oficial.']}]}
];

// Only missing profile fields are added; existing records and edits are preserved.
export function ensureProfiles(state) {
  for(const c of state.companies){
    const defaults=PROFILE_DEFAULTS[c.id]||{purpose:'',organization:'A definir',responsible:'Você',accounting:'A definir',taxStatus:'A confirmar',conditions:[]};
    c.profile??=structuredClone(defaults);
  }
  for(const doc of PROFILE_DOCS){
    if(state.companies.some(c=>c.id===doc.company)&&!state.documents.some(d=>d.id===doc.id)){
      state.documents.push({...structuredClone(doc),profileCompany:doc.company,source:'Exemplo institucional',date:'2026-07-01'});
    }
  }
  return state;
}
