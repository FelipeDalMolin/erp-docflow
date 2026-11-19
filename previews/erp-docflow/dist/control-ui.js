import {controlContext} from './control-context.js?v=24';
import {controlItems,taskControl,obligationControl,ensureControlTask} from './control-model.js?v=23';
import {validDate} from './range-model.js?v=17';

const groups={all:'Precisam de ação',overdue:'Atrasadas / vencidas',deviation:'Fora do previsto',due:'Hoje e próximos 7 dias',verify:'A conferir',planned:'Programadas',resolved:'Concluídas / revisadas'};
const tone=group=>({overdue:'red',deviation:'amber',due:'amber',verify:'blue',planned:'neutral',resolved:'green'}[group]);
export function createControl(a){
  const {esc,money,fullDate,icon,btn}=a;
  const filters=new Map();
  const items=()=>controlItems(a.state,a.company,a.NOW);
  const current=id=>items().find(item=>item.id===id);
  const taskFor=item=>a.state.tasks.find(t=>t.company===a.company&&t.controlSource===item.id);
  const pill=item=>`<span class="control-status ${tone(item.group)}">${esc(item.label)}</span>`;
  const alertCount=()=>items().filter(item=>!['planned','resolved'].includes(item.group)).length;
  function badge(kind,id){
    const record=a.scope(kind==='task'?'tasks':'obligations').find(x=>x.id===id);
    const item=record&&(kind==='task'?taskControl(record,a.NOW):obligationControl(a.state,record,a.NOW));
    return item?pill(item):'';
  }
  function summary(){
    const all=items(),count=alertCount(),late=all.filter(x=>x.group==='overdue').length;
    return `<section class="control-summary ${late?'has-overdue':''}" aria-label="Pendências e próximos passos"><div>${icon(late?'clock':'task')}<span><b>${count?count+' item(ns) precisam de ação':'Seu painel de obrigações e tarefas'}</b><small>${late?late+' prazo(s) ultrapassado(s). ':''}Vencimentos, desvios e verificações da empresa · ${fullDate(a.NOW)}</small></span></div>${btn('Abrir painel de controle','data-control-home="1"','','task')}</section>`;
  }
  const monthLabel=value=>new Intl.DateTimeFormat('pt-BR',{month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(value+'-01T12:00:00Z'));
  function chip(label,attrs='',kind=''){return `<${attrs?'button':'span'} ${attrs?'type="button" '+attrs:''} class="control-tag ${kind}">${label}</${attrs?'button':'span'}>`;}
  function references(refs){return refs.map(r=>chip(`<span>${esc(r.type)}</span> ${esc(r.label)}`,`data-open="${esc(r.kind)}" data-id="${esc(r.id)}"`,'linked')).join('');}
  function row(item,all){
    const task=item.kind==='task'?null:taskFor(item),context=controlContext(a.state,item,all),isForecast=item.kind==='forecast';
    const reference=context.direct.length?`<div class="control-reference"><span class="control-meta-label">Relacionado a</span><div class="control-tags">${references(context.direct)}</div></div>`:isForecast?'<p class="control-reference-missing"><b>Referência a identificar</b> · obrigação, contrato ou ativo ainda não vinculados a esta previsão.</p>':'';
    const history=isForecast?`<div class="control-evidence-summary"><b>Base da previsão:</b> ${context.sourceCount} movimentos em ${context.sourceMonths.map(monthLabel).map(esc).join(', ')}${context.documentCount?' · '+context.documentCount+' extrato(s) de origem':''}.</div>${context.histories.length?`<p class="control-bank-history"><b>Descrição do banco:</b> ${context.histories.map(esc).join(' / ')}</p>`:''}${context.historical.length?`<details class="control-historical"><summary>Vínculos nas ocorrências anteriores (${context.historical.length})</summary><p>Estes vínculos pertencem ao histórico. Ainda não foram atribuídos a esta previsão.</p><div class="control-tags">${references(context.historical)}</div></details>`:''}`:'';
    const facts=[{label:isForecast?'Data esperada':item.kind==='coverage'?'Sem cobertura desde':'Prazo informado',value:item.date?fullDate(item.date):'A definir'}];
    if(isForecast)facts.push({label:context.direction,value:money(item.amount)},{label:'Última ocorrência',value:context.lastDate?fullDate(context.lastDate):'Fonte indisponível'});
    else if(item.expected!==undefined)facts.push({label:context.direction||'Valor previsto',value:money(item.expected)},{label:'Saldo a conferir',value:money(item.remaining)});
    else if(item.kind==='task')facts.push({label:'Responsável',value:esc(item.owner||'A definir')});
    return `<article class="control-row control-row-context ${tone(item.group)}"><div class="control-row-main"><div class="control-row-heading">${pill(item)}<span class="control-origin">${esc(context.origin)}</span></div><h3><button class="control-title-link" data-open="control-item" data-id="${esc(item.id)}">${esc(context.title)}</button></h3><div class="control-tags" aria-label="Contexto deste item">${chip(`<span>Empresa</span> ${esc(context.companyName)}`,'data-go="companies"','company')}${context.banks.map(b=>chip(`<span>${isForecast?'Conta de origem':'Conta'}</span> ${esc(b.name)}`,`data-open="bank-account" data-id="${esc(b.id)}"`,'bank')).join('')}</div><dl class="control-card-facts">${facts.map(f=>`<div><dt>${esc(f.label)}</dt><dd>${f.value}</dd></div>`).join('')}</dl>${reference}${history}${context.note?`<p class="control-personal-note"><b>Sua observação:</b> ${esc(context.note)}</p>`:''}<p class="control-item-reason">${esc(item.detail)}</p><span class="control-next">Próxima ação: ${esc(item.next)}</span></div><div class="control-row-actions">${btn(isForecast?'Ver previsão e fontes':'Abrir contexto',`data-open="control-item" data-id="${esc(item.id)}"`)}${item.kind==='task'?btn(item.group==='resolved'?'Reabrir':'Concluir',`data-toggle-task="${esc(item.target)}"`,'','check'):item.group==='resolved'?'':btn(task&&!task.done?'Abrir tarefa':task?'Reabrir tarefa':'Criar tarefa',task&&!task.done?`data-open="task" data-id="${esc(task.id)}"`:`data-open="control-task" data-id="${esc(item.id)}"`,'','plus')}</div></article>`;
  }
  function panel(){
    const all=items(),filter=filters.get(a.company)||'all',counts=Object.fromEntries(Object.keys(groups).map(key=>[key,all.filter(item=>key==='all'?!['planned','resolved'].includes(item.group):item.group===key).length]));
    const visible=all.filter(item=>filter==='all'?!['planned','resolved'].includes(item.group):item.group===filter);
    return `<section class="control-panel" aria-label="Painel de controle de obrigações e tarefas"><div class="control-heading"><div><span class="eyebrow">O que precisa acontecer</span><h2>Pendências e próximos passos</h2><p>Referência: ${fullDate(a.NOW)} · pendências de todos os meses, da empresa selecionada.</p></div><div class="control-create">${btn('Ver previsões no calendário','data-forecast-calendar="1"','','calendar')}${btn('Nova obrigação','data-control-add="obligation"','primary','plus')}${btn('Criar tarefa','data-open="newtask"','','plus')}</div></div><div class="control-counters">${['overdue','deviation','due','verify'].map(group=>`<button class="${tone(group)} ${filter===group?'selected':''}" data-control-filter="${group}" aria-pressed="${filter===group}"><strong>${counts[group]}</strong><span>${groups[group]}</span></button>`).join('')}</div><div class="control-filterbar"><label>Exibir<select data-control-filter-select>${Object.entries(groups).map(([key,label])=>`<option value="${key}" ${filter===key?'selected':''}>${label} (${counts[key]})</option>`).join('')}</select></label><p role="status">${visible.length} item(ns) · prioridades primeiro</p></div><div class="control-list">${visible.map(row).join('')||'<div class="control-empty"><h3>Nenhum item nesta seleção</h3><p>Cadastre uma obrigação ou tarefa para acompanhar seus prazos, ou altere o filtro.</p></div>'}</div>${!a.scope('obligations').length?'<div class="control-start"><b>Comece pelos compromissos que você quer acompanhar.</b><p>O histórico bancário está disponível. As sugestões do histórico já podem ser vistas no calendário. Cadastre os compromissos conhecidos para acompanhar também seus vencimentos.</p></div>':''}<details class="control-explainer"><summary>Como interpretar os avisos</summary><p><b>Vencida:</b> o prazo informado passou e ainda existe valor sem vínculo confirmado. Confira a realização antes de repetir um pagamento ou cobrar.</p><p><b>Fora do previsto:</b> diferença de valor, realização após a data esperada ou valor ainda não localizado na data acompanhada.</p><p><b>A conferir:</b> falta de extrato, vínculo pendente ou previsão ainda não confirmada. Isso não prova inadimplência. Previsões do histórico permanecem identificadas como sugestões, mesmo quando sua data passa.</p><p>Concluir uma tarefa registra uma ação. A obrigação, o vínculo financeiro e o documento mantêm seus próprios estados. Avisos são internos e calculados ao abrir/atualizar a aplicação; alterações ficam neste navegador.</p></details></section>`;
  }
  function origin(item){return item.kind==='coverage'?btn('Ver conta e cobertura',`data-open="bank-account" data-id="${esc(item.target)}"`,'','wallet'):btn(item.kind==='task'?'Abrir tarefa':'Abrir obrigação',`data-open="${item.kind}" data-id="${esc(item.target)}"`,'','link');}
  function dialog(kind,id){
    if(!kind.startsWith('control-'))return null;
    const item=current(id);if(!item)return {heading:'Acompanhamento',body:'Este aviso não está mais ativo. Volte ao painel para consultar a situação atual.'};
    if(kind==='control-item'&&item.kind==='forecast')return a.forecastDialog('forecast',item.target);
    if(kind==='control-item'){
      const task=taskFor(item),record=item.kind==='task'?a.scope('tasks').find(t=>t.id===item.target):a.scope('obligations').find(o=>o.id===item.target);
      return {heading:'Pendência e próxima ação',body:`<h2>${esc(item.title)}</h2><p class="description">${pill(item)}</p><div class="control-context"><p>${esc(item.detail)}</p><strong>Próxima ação: ${esc(item.next)}</strong></div><dl class="info-grid"><div><dt>${item.kind==='coverage'?'Primeiro dia sem cobertura':'Prazo original / informado'}</dt><dd>${item.date?fullDate(record?.originalDue||item.date):'A definir'}</dd></div><div><dt>Responsável</dt><dd>${esc(item.owner||'A definir')}</dd></div>${item.expected!==undefined?`<div><dt>Valor previsto</dt><dd>${money(item.expected)}</dd></div><div><dt>Vínculos confirmados</dt><dd>${money(item.paid)}</dd></div><div><dt>Saldo a conferir</dt><dd>${money(item.remaining)}</dd></div><div><dt>Data de acompanhamento</dt><dd>${item.expectedDate?fullDate(item.expectedDate):'A definir'}</dd></div>`:''}</dl><div class="drawer-actions">${origin(item)}${item.date?btn('Ver na agenda',`data-control-agenda="${esc(item.id)}"`,'','calendar'):''}${item.kind==='task'?btn(item.group==='resolved'?'Reabrir tarefa':'Concluir tarefa',`data-toggle-task="${esc(item.target)}"`,'primary','check'):item.group==='resolved'?'':btn(task&&!task.done?'Abrir tarefa vinculada':task?'Reabrir tarefa vinculada':'Criar tarefa vinculada',task&&!task.done?`data-open="task" data-id="${esc(task.id)}"`:`data-open="control-task" data-id="${esc(item.id)}"`,'primary','plus')}</div>${item.kind!=='coverage'?btn('Ajustar acompanhamento',`data-open="control-schedule" data-id="${esc(item.id)}"`,'','calendar'):''}${item.group==='deviation'?btn('Registrar análise do desvio',`data-open="control-review" data-id="${esc(item.id)}"`,'','check'):''}${item.review?`<p class="control-review">Análise registrada em ${fullDate(item.review.date)}: ${esc(item.review.note)}</p>`:''}${record?.monitoringHistory?.length?`<details class="control-explainer"><summary>Histórico do acompanhamento</summary>${record.monitoringHistory.map(entry=>`<p>${fullDate(entry.at)} · ${fullDate(entry.from)} para ${fullDate(entry.to)} · ${esc(entry.reason)}</p>`).join('')}</details>`:''}<p class="audit-note">O alerta descreve os dados disponíveis. Nenhuma cobrança, pagamento ou mensagem é enviada por esta tela.</p>`};
    }
    if(kind==='control-task'){
      const existing=taskFor(item);
      return {heading:'Próxima ação vinculada',body:a.formShell('Definir a próxima ação',item.title,`<label>Ação<input name="title" value="${esc(existing?.title||item.next+' · '+item.title)}" required maxlength="180"></label><div class="formrow"><label>Prazo<input type="date" name="due" value="${a.NOW}" required></label><label>Responsável<input name="owner" value="${esc(existing?.owner||'Você')}" required maxlength="80"></label></div><p>Esta tarefa fica vinculada ao aviso. Repetir a ação abre a mesma tarefa, sem duplicá-la.</p><p class="form-error" role="alert"></p>`,kind,id,existing?'Reabrir tarefa':'Criar tarefa')};
    }
    if(kind==='control-review')return {heading:'Analisar desvio',body:a.formShell('Registrar análise',item.title,`<label>O que foi verificado?<textarea name="note" required maxlength="1000" placeholder="Registre a causa e a decisão tomada."></textarea></label><p>Esta análise reconhece o desvio. Valores, vencimento e movimentos permanecem no histórico. Um novo desvio reabre o aviso.</p><p class="form-error" role="alert"></p>`,kind,id,'Registrar análise')};
    if(kind==='control-schedule')return {heading:'Ajustar acompanhamento',body:a.formShell('Organizar a próxima data',item.title,`<label>${item.kind==='task'?'Novo prazo da tarefa':'Data esperada para execução'}<input type="date" name="date" value="${item.expectedDate||item.date||a.NOW}" required></label><label>Responsável<input name="owner" value="${esc(item.owner==='A definir'?'Você':item.owner)}" required maxlength="80"></label><label>Motivo<textarea name="reason" required maxlength="1000"></textarea></label><p>${item.kind==='task'?'O prazo anterior fica registrado no histórico.':'O vencimento original continua registrado. Reprogramar a expectativa não elimina um vencimento ultrapassado.'}</p><p class="form-error" role="alert"></p>`,kind,id,'Salvar acompanhamento')};
    return null;
  }
  function refresh(){const top=window.scrollY;a.render();window.scrollTo({top,behavior:'instant'});}
  function click(d){
    if(d.controlAdd){a.setMonth(a.NOW.slice(0,7));a.open('newobligation');return true;}
    if(d.controlHome){a.navigate('home/control');return true;}
    if(d.controlFilter&&groups[d.controlFilter]){filters.set(a.company,d.controlFilter);refresh();return true;}
    if(d.controlAgenda){const item=current(d.controlAgenda);if(item?.date){a.setMonth(item.date.slice(0,7));a.selectDate(item.date);a.navigate('home/calendar');}return true;}
    return false;
  }
  function change(e){if(e.target.hasAttribute('data-control-filter-select')){filters.set(a.company,groups[e.target.value]?e.target.value:'all');refresh();return true;}return false;}
  function submit(form,data){
    const kind=form.dataset.form;if(!['control-task','control-review','control-schedule'].includes(kind))return false;
    const item=current(form.dataset.id),v=key=>String(data.get(key)||'').trim(),fail=message=>{const box=form.querySelector('.form-error');if(box)box.textContent=message;else a.toast(message);return true;};
    if(!item)return fail('Este item mudou. Feche o painel e confira sua situação atual.');
    if(kind==='control-task'){
      let task;try{task=ensureControlTask(a.state,item,{title:v('title'),due:v('due'),owner:v('owner')},a.NOW);}catch(error){return fail(error.message);}
      a.save();a.closeAll();a.render();a.open('task',task.id);a.toast('Próxima ação vinculada ao contexto.');return true;
    }
    if(kind==='control-review'){
      if(item.group!=='deviation'||!v('note'))return fail('Registre o que foi verificado neste desvio.');
      a.state.controlReviews??={};a.state.controlReviews[a.company+':'+item.id]={signature:item.signature,date:a.NOW,note:v('note')};
    }else{
      if(!validDate(v('date'))||!v('reason')||!v('owner'))return fail('Informe uma data válida, o responsável e o motivo.');
      const record=a.scope(item.kind==='task'?'tasks':'obligations').find(x=>x.id===item.target);
      if(!record)return fail('Registro indisponível.');
      const from=item.kind==='task'?record.due:record.expectedDate||record.due;
      record.monitoringHistory??=[];record.monitoringHistory.push({at:a.NOW,from,to:v('date'),reason:v('reason')});record.owner=v('owner');
      if(item.kind==='task'){record.originalDue??=record.due;record.due=v('date');}else record.expectedDate=v('date');
    }
    a.save();a.closeAll();a.render();a.toast('Acompanhamento atualizado com histórico preservado.');return true;
  }
  return {panel,summary,badge,alertCount,dialog,click,change,submit};
}
