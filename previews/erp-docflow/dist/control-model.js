import {validDate,moveDate} from './range-model.js?v=17';
import {forecastItems,updateForecast} from './forecast-model.js?v=23';

export const controlToday=(date=new Date())=>new Intl.DateTimeFormat('sv-SE',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(date);
const daysBetween=(from,to)=>Math.round((Date.parse(to+'T12:00:00Z')-Date.parse(from+'T12:00:00Z'))/86400000);
const priority={overdue:0,deviation:1,verify:2,due:3,planned:4,resolved:5};
const closed=o=>o.cancelled||o.status==='cancelled';

export function taskControl(task,today){
  const days=validDate(task.due)?daysBetween(today,task.due):null;
  const doneLate=task.done&&validDate(task.doneAt)&&task.doneAt>task.due;
  const group=task.done?'resolved':days===null?'verify':days<0?'overdue':days<=7?'due':'planned';
  return {id:'task:'+task.id,kind:'task',target:task.id,company:task.company,title:task.title,date:task.due,owner:task.owner||'A definir',group,
    label:task.done?(doneLate?'Concluída com atraso':'Concluída'):days===null?'Sem prazo':days<0?'Tarefa atrasada':days===0?'Para hoje':days<=7?'Próximos 7 dias':'Programada',
    detail:task.done?'A ação foi concluída; o compromisso financeiro é acompanhado separadamente.':days<0?`Prazo ultrapassado há ${-days} dia(s).`:days===null?'Defina uma data para acompanhar esta ação.':`Prazo em ${days} dia(s).`,
    next:task.done?'Consultar contexto':'Executar ou reprogramar a tarefa',daysLate:Math.max(0,-(days||0))};
}

export function obligationControl(state,o,today){
  if(closed(o))return null;
  const expected=(o.items||[]).reduce((n,i)=>n+i.amount,0),due=validDate(o.due)?o.due:null;
  const expectedDate=validDate(o.expectedDate)?o.expectedDate:due;
  const linked=(state.transactions||[]).filter(t=>t.company===o.company&&t.obligation===o.id&&validDate(t.date)&&t.date<=today);
  const correct=t=>Number.isSafeInteger(t.amount)&&(o.kind==='in'?t.amount>0:t.amount<0);
  const confirmed=linked.filter(t=>t.confirmed&&correct(t)).sort((a,b)=>a.date.localeCompare(b.date));
  const paid=confirmed.reduce((n,t)=>n+Math.abs(t.amount),0),remaining=Math.max(0,expected-paid);
  const account=state.accounts.find(a=>a.company===o.company&&a.id===o.account),coverage=account?.statement?.period;
  const verificationStart=expectedDate&&expectedDate<due?expectedDate:due;
  const covered=!!(due&&coverage&&coverage.start<=verificationStart&&coverage.end>=today);
  let cumulative=0,completedAt=null;
  for(const t of confirmed){cumulative+=Math.abs(t.amount);if(completedAt===null&&cumulative>=expected)completedAt=t.date;}
  const item={id:'obligation:'+o.id,kind:'obligation',target:o.id,company:o.company,title:o.title,date:due,expectedDate,owner:o.owner||'A definir',account:o.account,expected,paid,remaining,covered,coverageEnd:coverage?.end||null,
    daysLate:due?Math.max(0,daysBetween(due,today)):0,group:'planned',label:'Programada',detail:'Compromisso acompanhado pelo prazo informado.',next:'Abrir obrigação'};
  const set=(group,label,detail,next)=>Object.assign(item,{group,label,detail,next});
  if(!due||!Number.isSafeInteger(expected)||expected<=0)set('verify','Cadastro a completar','Confira o prazo e o valor antes de acompanhar este compromisso.','Completar acompanhamento');
  else if(linked.some(t=>!t.confirmed||!correct(t)))set('verify','Vínculo a conferir','Há movimento associado ainda não confirmado ou com direção incompatível. A baixa depende da conferência.','Conferir movimentos vinculados');
  else if(paid>expected)set('deviation','Valor acima do previsto','A soma dos movimentos confirmados ultrapassa o valor deste compromisso.','Conferir diferença de valor');
  else if(remaining===0){
    if(completedAt>due||completedAt>(expectedDate||due))set('deviation','Realização após o previsto','O compromisso foi integralmente realizado depois do vencimento ou da data esperada. O vencimento original permanece no histórico.','Revisar o desvio de data');
    else set('resolved','Realizada','O valor está integralmente vinculado a movimentos confirmados.','Consultar obrigação');
  }
  else if(o.monitoringKind==='estimate'){
    if(expectedDate<today)set('verify','Previsão não confirmada','A data estimada passou. Uma sugestão não confirma dívida, atraso ou inadimplência.','Revisar ou confirmar a previsão');
    else if(expectedDate<=moveDate(today,7))set('due','Previsão próxima','Data e valor ainda são estimados.','Revisar previsão');
    else set('planned','Previsão futura','Data e valor ainda são estimados.','Revisar previsão');
  }
  else if((due<today||expectedDate<today)&&!covered)set('verify','Verificação pendente','O prazo acompanhado passou, mas falta cobertura bancária para verificar a realização. Ausência de extrato não confirma atraso.','Atualizar extrato e conferir');
  else if(due<today)set('overdue',paid?'Vencida · saldo a conferir':'Vencida · realização a conferir',`Vencimento há ${item.daysLate} dia(s). ${paid?'Há realização parcial confirmada.':'Não há realização confirmada vinculada.'} Confira antes de cobrar ou pagar novamente.`,'Conferir realização e definir próxima ação');
  else if(expectedDate<today)set('deviation','Não localizada na data prevista','A data esperada passou e ainda há valor sem realização confirmada. O vencimento original é mantido.','Conferir e reprogramar acompanhamento');
  else if(due===today)set('due',paid?'Vence hoje · parcial':'Vence hoje','Confira o valor pendente e a próxima ação para hoje.','Executar e registrar a realização');
  else if(due<=moveDate(today,7))set('due','Próximos 7 dias','Organize o documento e a ação antes do vencimento.','Preparar execução');
  item.signature=JSON.stringify([o.due,o.expectedDate,o.monitoringKind,expected,confirmed.map(t=>[t.id,t.amount,t.date]),item.label]);
  const review=state.controlReviews?.[o.company+':'+item.id];
  if(item.group==='deviation'&&review?.signature===item.signature){
    item.review=review;
    if(remaining>0){
      item.group=due<=moveDate(today,7)?'due':'planned';
      item.label='Desvio revisado · compromisso pendente';
      item.detail='A análise foi registrada. O valor pendente e o vencimento continuam acompanhados.';
      item.next='Acompanhar a realização até o vencimento';
    }else{item.group='resolved';item.label='Desvio revisado';}
  }
  if(item.group==='resolved'&&o.missing)set('verify','Documentação pendente','A realização financeira está registrada. Falta: '+o.missing,'Providenciar e conferir a documentação');
  return item;
}

export function controlItems(state,company,today){
  const items=[...(state.obligations||[]).filter(o=>o.company===company).map(o=>obligationControl(state,o,today)).filter(Boolean),
    ...(state.tasks||[]).filter(t=>t.company===company).map(t=>taskControl(t,today)),...forecastItems(state,company,today)];
  for(const account of state.accounts.filter(a=>a.company===company)){
    const end=account.statement?.period?.end;
    if(!end||end<today)items.push({id:'coverage:'+account.id,kind:'coverage',target:account.id,company,account:account.id,title:'Atualizar extrato · '+account.name,date:end?moveDate(end,1):today,group:'verify',label:'Cobertura bancária pendente',
      detail:end?`Último extrato até ${end.split('-').reverse().join('/')}. Os dias seguintes não estão verificados.`:'Esta conta ainda não tem período de extrato informado.',next:'Providenciar extrato e conferir movimentos',daysLate:0});
  }
  return items.sort((a,b)=>priority[a.group]-priority[b.group]||(a.date||'9999').localeCompare(b.date||'9999')||a.title.localeCompare(b.title,'pt-BR'));
}

export function ensureControlTask(state,item,{title,due,owner},today){
  if(!validDate(due)||!title.trim()||!owner.trim())throw Error('Informe a ação, o responsável e um prazo válido.');
  const existing=state.tasks.find(t=>t.company===item.company&&t.controlSource===item.id);
  if(existing){
    if(existing.done){existing.originalDue??=existing.due;existing.monitoringHistory??=[];existing.monitoringHistory.push({at:today,from:existing.due,to:due,reason:'Reabertura do acompanhamento'});existing.done=false;existing.due=due;existing.owner=owner;existing.title=title;existing.doneAt=null;}
    return existing;
  }
  const task={id:'control-task-'+crypto.randomUUID(),company:item.company,title:title.trim(),due,owner:owner.trim(),kind:'Acompanhamento',done:false,createdAt:today,controlSource:item.id};
  if(item.kind==='obligation')task.obligation=item.target;
  if(item.kind==='coverage')task.bankAccount=item.target;
  if(item.kind==='forecast'){task.forecast=item.target;updateForecast(state,item,{action:'Tarefa de acompanhamento criada'},today);}
  state.tasks.push(task);return task;
}
