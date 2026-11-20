import {bankTone} from './visual-theme.js?v=34';
import {presentationHTML,warningIcon} from './record-presentation.js?v=34';
import {calendarCells,calendarRangeEvents} from './workspace-model.js?v=34';
import {newCalendarSelection,setCalendarRange,pickCalendarDate,calendarPreset,shiftCalendarRange,insideSelection,calendarDayGroups,calendarDayPage} from './calendar-selection.js?v=26';
import {validDate,moveDate,rangeDays} from './range-model.js?v=17';
import {statementCovers} from './statement-model.js?v=17';
import {dailyBook} from './workbook-model.js?v=17';

const types=['realized','obligation','task','forecast'],labels={realized:'Realizados',obligation:'Vencimentos',task:'Tarefas',forecast:'Previsões'};
export function createCalendar(a){
  const {esc,money,fullDate,icon,btn,empty}=a,states=new Map();
  let view='month',drag=null,suppressUntil=0;
  const state=()=>{if(!states.has(a.company))states.set(a.company,newCalendarSelection(a.NOW));return states.get(a.company);};
  const filters=()=>{const s=state();return s.filters??={realized:true,obligation:true,task:true,forecast:true,completed:false};};
  const events=(range,all=false)=>calendarRangeEvents(a.state,a.company,range,{...(all?{completed:filters().completed}:filters()),asOf:a.NOW});
  const monthName=month=>new Intl.DateTimeFormat('pt-BR',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(month+'-01T12:00:00Z'));
  const weekday=date=>new Intl.DateTimeFormat('pt-BR',{weekday:'long',timeZone:'UTC'}).format(new Date(date+'T12:00:00Z'));
  const focusContext=()=>{const s=state();(a.setCalendarFocus||a.selectDate)(s.focus);};
  const refresh=selector=>{a.render();if(selector)document.querySelector(selector)?.focus({preventScroll:true});};
  const badge=e=>['task','obligation'].includes(e.type)?a.controlBadge?.(e.kind,e.target)||'':'';
  const interval=s=>s.start===s.end?fullDate(s.start):fullDate(s.start)+' — '+fullDate(s.end);
  function eventButton(e,compact=false){
    const account=a.state.accounts.find(b=>b.id===e.account&&b.company===a.company),reconciled=!!e.presentation?.complete;
    const doneTask=e.type==='task'&&e.done,flow=e.direction||'neutral';
    const typeLabel={realized:'Extrato',obligation:'Vencimento',task:'Tarefa',forecast:'Previsão'}[e.type];
    return `<button class="cal-event ${e.type} ${reconciled?'is-reconciled':''} ${doneTask?'is-done':''}" data-flow="${flow}" data-bank-tone="${bankTone(account)}" data-open="${e.kind}" data-id="${esc(e.target)}" data-cal-context="${e.date}" title="${esc([e.title,e.label,e.presentation?.label,...(e.presentation?.warnings||[])].filter(Boolean).join(' · '))}"><span class="event-dot"></span><span class="event-copy"><span class="event-meta"><span class="event-type">${typeLabel}</span>${account?`<span class="event-bank">${esc(account.name)}</span>`:''}</span><b>${esc(e.title)}</b><small>${esc(e.label)}${e.amount!==undefined?' · <span class="event-amount">'+money(e.amount)+'</span>':''}</small>${e.presentation?presentationHTML(a,e.presentation,{compact}):''}</span>${badge(e)}</button>`;
  }
  function semantics(){return `<div class="calendar-semantics" aria-label="Padrão visual dos registros"><span class="incoming"><i></i>Entradas / recebimentos</span><span class="outgoing"><i></i>Saídas / pagamentos</span><span><s class="semantic-strike">Título riscado</s> Financeiro conciliado</span><span class="record-warning">${warningIcon}Há conferências pendentes</span></div>`;}
  function completionGuide(){return `<details class="calendar-completion-guide"><summary>Conciliação e pendências: como ler</summary><p>O título riscado indica vínculo financeiro confirmado e compatível. Na obrigação, o valor deve estar integralmente conciliado. O valor e a data continuam legíveis.</p><p>O triângulo identifica documentação, classificação ou diferenças que ainda precisam de conferência. Um item conciliado pode continuar com alerta. Abra o item para consultar os vínculos e as pendências.</p><p>Um extrato importado não está automaticamente conciliado. Tarefas são riscadas quando concluídas; reconhecer uma previsão não confirma conciliação.</p></details>`;}
  function rangeControls(){
    const s=state(),draft=s.draft||s;
    return `<section class="calendar-selection" aria-label="Selecionar período do calendário"><div class="calendar-selection-head"><div><span class="eyebrow">Seu contexto de navegação</span><h3>${interval(s)}</h3><p role="status">${rangeDays(s)} dia(s) selecionado(s) · contadores, agenda e lista usam este período.</p></div><div class="segments" aria-label="Modo de seleção">${[['day','Dia'],['range','Intervalo']].map(([id,title])=>`<button data-cal-select-mode="${id}" aria-pressed="${s.mode===id}" class="${s.mode===id?'active':''}">${title}</button>`).join('')}</div></div><div class="calendar-range-presets">${[['today','Hoje'],['week','Semana'],['month','Mês'],['next7','Próximos 7 dias'],['year','Ano']].map(([id,title])=>btn(title,`data-cal-preset="${id}"`)).join('')}</div><div class="calendar-range-fields"><label>De<input type="date" data-cal-range-start value="${esc(draft.start)}" min="1900-01-01" max="9999-12-31"></label><label>Até<input type="date" data-cal-range-end value="${esc(draft.end)}" min="1900-01-01" max="9999-12-31"></label>${btn('Aplicar período','data-cal-range-apply="1"','primary')}<div class="calendar-range-shifts"><button data-cal-range-shift="-1" aria-label="Intervalo anterior">${icon('back')}</button><button data-cal-range-shift="1" aria-label="Próximo intervalo">${icon('chevron')}</button></div></div><p class="calendar-selection-help">${s.pending?'Escolha a data final. Você pode navegar para outro mês. Esc cancela.':s.mode==='range'?'Clique no início e no fim, ou arraste entre as células com o mouse. Shift + clique também amplia a seleção.':'Clique em uma célula para explorar o dia. Use Intervalo para selecionar várias datas.'}</p><p class="range-error" role="alert">${esc(s.error)}</p><div class="calendar-selection-legend"><span class="today-key">Hoje</span><span class="range-key">Período selecionado</span><span class="focus-key">Dia em detalhe</span></div></section>`;
  }
  function grid(items){
    const s=state(),cells=calendarCells(s.month),focusVisible=cells.some(c=>c.date===s.focus);return `<div class="calendar-grid ${s.mode==='range'?'range-selecting':''}" aria-label="Calendário mensal"><div class="calendar-weekdays">${['SEG','TER','QUA','QUI','SEX','SÁB','DOM'].map(d=>`<span>${d}</span>`).join('')}</div><div class="calendar-days">${cells.map(c=>{
      const es=items.filter(e=>e.date===c.date),alerts=es.filter(e=>['overdue','deviation'].includes(e.urgency)).length,selected=insideSelection(s,c.date),today=c.date===a.NOW,focused=c.date===s.focus;
      return `<article data-cal-cell="${c.date}" class="calendar-cell ${!c.inMonth?'outside':''} ${today?'reference is-today':''} ${selected?'in-range':''} ${c.date===s.start?'range-start':''} ${c.date===s.end?'range-end':''} ${focused?'focused-day':''} ${alerts?'has-control-alert':''}"><button class="calendar-cell-hit" data-cal-day="${c.date}" tabindex="${focused||(!focusVisible&&c.inMonth&&c.day===1)?0:-1}" aria-label="${fullDate(c.date)}${today?', hoje':''}${selected?', dentro da seleção':''}, ${es.length} itens${alerts?', '+alerts+' alerta(s)':''}" ${today?'aria-current="date"':''} aria-pressed="${selected}"></button><div class="calendar-day-number"><span>${c.day}</span>${today?'<small>Hoje</small>':''}${alerts?`<span class="calendar-alert-count">! ${alerts}</span>`:''}<span class="mobile-day-dots">${['incoming','outgoing'].filter(d=>es.some(e=>e.direction===d)).map(d=>`<i data-flow="${d}"></i>`).join('')}${['task','forecast'].filter(t=>es.some(e=>e.type===t)).map(t=>`<i class="${t}"></i>`).join('')}${es.some(e=>e.presentation?.warnings.length)?'<i class="has-warning"></i>':''}</span></div><div class="calendar-cell-events">${es.slice(0,3).map(e=>eventButton(e,true)).join('')}${es.length>3?`<button class="cal-more" data-cal-explore="${c.date}">+ ${es.length-3} itens neste dia</button>`:''}</div></article>`;
    }).join('')}</div></div>`;
  }
  function pagination(items){const p=calendarDayPage(items,state().page);state().page=p.page;return `<nav class="calendar-pagination" aria-label="Páginas dos itens selecionados"><span>${p.first}–${p.last} de ${p.total} dias com itens · ${p.totalItems} itens no período</span><div><button data-cal-page="${p.page-1}" ${p.page===1?'disabled':''} aria-label="Página anterior">${icon('back')}</button><span>Página ${p.page} de ${p.pages}</span><button data-cal-page="${p.page+1}" ${p.page===p.pages?'disabled':''} aria-label="Próxima página">${icon('chevron')}</button></div></nav>`;}
  function agenda(items){
    const p=calendarDayPage(items,state().page),dates=[...new Set(p.items.map(e=>e.date))];
    return `<div class="calendar-agenda" aria-label="Agenda do período selecionado"><p class="calendar-agenda-caption">Agenda · ${interval(state())}</p>${dates.map(date=>`<section class="agenda-date"><button class="agenda-day-button" data-cal-explore="${date}" aria-label="Explorar ${fullDate(date)}"><strong>${date.slice(8)}</strong><span>${weekday(date).replace('-feira','')}</span><small>${fullDate(date)}</small></button><div>${p.items.filter(e=>e.date===date).map(e=>eventButton(e)).join('')}</div></section>`).join('')||empty('Sem itens na seleção','Altere o período ou os filtros.')}${pagination(items)}</div>`;
  }
  function financialLink(){
    const s=state();
    return `<div class="calendar-flow-context"><label>Conta para abrir no fluxo<select data-cal-flow-account><option value="all" ${s.flowAccount==='all'?'selected':''}>Todas as contas</option>${a.scope('accounts').map(b=>`<option value="${esc(b.id)}" ${s.flowAccount===b.id?'selected':''}>${esc(b.name)}</option>`).join('')}</select></label>${btn('Abrir período no fluxo','data-cal-open-flow="1"','','flow')}<p>O fluxo receberá as mesmas datas selecionadas, inclusive futuras ou sem extrato. A cobertura bancária será informada sem cortar o período.</p></div>`;
  }

  const closedDays=()=>state().closedDays??=new Set();
  function dayGroup(group){
    const closed=closedDays().has(group.date),bodyId='calendar-period-day-'+group.date;
    const counts=types.filter(type=>group.counts[type]).map(type=>`${group.counts[type]} ${labels[type].toLowerCase()}`).join(' · ');
    return `<section class="calendar-day-group"><h3><button class="calendar-day-toggle" data-cal-toggle-day="${group.date}" aria-expanded="${!closed}" aria-controls="${bodyId}" aria-label="${closed?'Expandir':'Recolher'} itens de ${fullDate(group.date)}"><span class="calendar-day-toggle-heading"><strong>${fullDate(group.date)}</strong><span class="calendar-day-toggle-sign" aria-hidden="true">${closed?'+':'−'}</span></span><span class="calendar-day-weekday">${weekday(group.date)}</span><span class="calendar-day-count">${group.items.length} itens · ${counts}</span>${group.counts.realized?`<span class="calendar-day-money"><span class="incoming">Créditos <b>${money(group.incoming)}</b></span><span class="outgoing">Débitos <b>${money(group.outgoing)}</b></span></span>`:'<span class="calendar-day-no-realized">Sem movimentos realizados neste dia com os filtros atuais.</span>'}</button></h3><div id="${bodyId}" class="calendar-day-group-items" ${closed?'hidden':''}>${group.items.map(e=>eventButton(e)).join('')}${btn('Explorar este dia',`data-cal-explore="${group.date}"`,'','calendar')}</div></section>`;
  }
  function groupControls(items){return items.length?`<div class="calendar-group-controls" role="group" aria-label="Visibilidade dos dias">${btn('Recolher dias','data-cal-collapse-days="1"')}${btn('Expandir dias','data-cal-expand-days="1"')}</div>`:'';}
  function periodPanel(items){
    const s=state(),page=calendarDayPage(items,s.page),tx=items.filter(e=>e.type==='realized'),incoming=tx.filter(t=>t.amount>0).reduce((n,t)=>n+t.amount,0),outgoing=tx.filter(t=>t.amount<0).reduce((n,t)=>n-t.amount,0);
    const uncovered=a.scope('accounts').filter(b=>b.statement&&!(b.statement.period.start<=s.start&&b.statement.period.end>=s.end));
    return `<aside class="calendar-detail calendar-period-detail" id="calendar-detail" aria-label="Itens do período selecionado"><span class="eyebrow">Período selecionado</span><h2>${interval(s)}</h2><p class="calendar-period-caption">${items.length} itens com os filtros atuais</p><div class="calendar-period-totals"><div class="incoming"><span>Créditos exibidos</span><b>${money(incoming)}</b></div><div class="outgoing"><span>Débitos exibidos</span><b>${money(outgoing)}</b></div></div><p class="calendar-period-note">Somente movimentos do extrato nos filtros atuais. Previsões e obrigações não entram nestes totais.${uncovered.length?' Cobertura incompleta: '+uncovered.map(b=>esc(b.name)).join(', ')+'.':''}</p>${groupControls(items)}<div class="calendar-period-items">${page.groups.map(dayGroup).join('')||'<p>Nenhum item neste intervalo com os filtros atuais.</p>'}</div>${pagination(items)}${completionGuide()}${financialLink()}<p class="calendar-date-note">A seleção filtra a navegação; não altera vencimentos, tarefas nem lançamentos.</p></aside>`;
  }
  function dayPanel(items){
    const s=state(),date=s.focus,dayItems=items.filter(e=>e.date===date),range=s.start!==s.end,f=dailyBook(a.state,a.company,date.slice(0,7)).find(d=>d.date===date);
    return `<aside class="calendar-detail" id="calendar-detail" aria-label="Itens do dia selecionado">${range?btn('Voltar aos itens do período','data-cal-panel="range"','','back'):'<button class="calendar-back" data-calendar-back="1">Voltar ao calendário</button>'}<div class="calendar-detail-head"><span class="eyebrow">${range?'Dia dentro da seleção':'Dia selecionado'}</span><div class="calendar-day-navigation" role="group" aria-label="Navegação por dia"><button data-panel-day-shift="-1" ${range&&date===s.start?'disabled':''} aria-label="Dia anterior">${icon('back')}</button><input type="date" data-panel-day-date aria-label="Ir para uma data" value="${date}"><button data-panel-day-shift="1" ${range&&date===s.end?'disabled':''} aria-label="Próximo dia">${icon('chevron')}</button></div><div class="calendar-day-caption"><p>${weekday(date)}</p><span class="day-item-count">${dayItems.length} itens</span></div><span class="calendar-day-announcement" role="status">${fullDate(date)} · ${dayItems.length} itens</span></div><div class="day-balance-mini"><span>Saldo realizado ao fim do dia</span><strong>${statementCovers(a.state,a.company,date)?money(f?.closing||0):'Sem extrato'}</strong></div><div class="calendar-detail-items">${types.map(t=>{const group=dayItems.filter(e=>e.type===t);return group.length?`<section><h3><i class="event-dot ${t}"></i>${labels[t]} <span>${group.length}</span></h3>${group.map(e=>e.type==='task'?`<div class="day-item ${e.done?'completed':''}"><button class="check ${e.done?'done':''}" data-toggle-task="${esc(e.target)}" aria-label="${e.done?'Reabrir':'Concluir'} tarefa: ${esc(e.title)}">${e.done?icon('check'):''}</button>${eventButton(e)}</div>`:eventButton(e)).join('')}</section>`:''}).join('')||'<div class="quiet-day"><strong>Nenhum item neste dia.</strong><p>Confira os filtros ou navegue pela seleção.</p></div>'}</div><div class="calendar-detail-actions">${btn('Criar tarefa nesta data','data-calendar-add="task"','primary','plus')}${btn('Nova obrigação nesta data','data-calendar-add="obligation"','','wallet')}${btn('Abrir detalhe financeiro',`data-calendar-full="${date}"`,'','flow')}</div>${completionGuide()}${financialLink()}<p class="calendar-date-note">Prazos acompanhados em ${fullDate(a.NOW)}. Selecionar datas não altera vencimentos.</p></aside>`;
  }
  function render(tabs){
    const s=state();a.setMonth(s.month);const cells=calendarCells(s.month),gridItems=events({start:cells[0].date,end:cells.at(-1).date}),selected=events(s),all=events(s,true);
    return a.titleBlock('Home','Lançamentos, vencimentos, tarefas e previsões dentro da sua seleção.',tabs,'Seu dia a dia')+`<section class="calendar-shell">${rangeControls()}<div class="calendar-monthbar"><div class="calendar-month-title"><span class="eyebrow">${esc(a.get('companies',a.company).name)} · mês em exibição</span><h2>${monthName(s.month)}</h2></div><div class="calendar-month-actions"><div class="calendar-arrows"><button data-calendar-shift="-1" aria-label="Mês anterior">${icon('back')}</button><input aria-label="Mês do calendário" type="month" data-calendar-month value="${s.month}"><button data-calendar-shift="1" aria-label="Próximo mês">${icon('chevron')}</button></div>${btn('Mostrar seleção','data-cal-reveal="1"')}<div class="segments"><button data-calendar-mode="month" class="${view==='month'?'active':''}" aria-pressed="${view==='month'}">Mês</button><button data-calendar-mode="agenda" class="${view==='agenda'?'active':''}" aria-pressed="${view==='agenda'}">Agenda</button></div></div></div><div class="calendar-filterbar"><div class="calendar-filters" aria-label="Filtrar itens da seleção">${types.map(t=>`<button class="calendar-filter ${t} ${filters()[t]?'active':''}" data-calendar-filter="${t}" aria-pressed="${filters()[t]}"><i class="event-dot"></i>${labels[t]}<span>${all.filter(e=>e.type===t).length}</span></button>`).join('')}</div><label class="completed-filter"><input type="checkbox" data-calendar-completed ${filters().completed?'checked':''}>Mostrar concluídos / reconhecidos</label></div>${semantics()}<div class="calendar-workspace"><div class="calendar-main" id="calendar-month-content">${view==='month'?grid(gridItems):agenda(selected)}<div class="calendar-key">${icon('info')}<span>Hoje tem preenchimento próprio. A faixa destaca a seleção; a borda indica o dia em detalhe. Navegar pelos meses preserva o intervalo.</span></div></div>${s.panel==='day'?dayPanel(selected):periodPanel(selected)}</div>${a.forecastBanner?.()||''}</section>`;
  }
  function select(date,{extend=false,explore=false,focusSelector}={}){
    const s=state();if(!validDate(date))return;
    if(explore&&insideSelection(s,date)){s.focus=date;s.panel='day';s.month=date.slice(0,7);}
    else if(explore){setCalendarRange(s,date);s.mode='day';}
    else pickCalendarDate(s,date,extend);
    focusContext();refresh(focusSelector||`[data-cal-day="${date}"]`);
  }
  function click(d,event={}){
    const s=state();
    if(d.calDay){if(Date.now()<suppressUntil){suppressUntil=0;return true;}select(d.calDay,{extend:!!event.shiftKey});return true;}
    if(d.calExplore){select(d.calExplore,{explore:true});return true;}
    if(d.calContext){select(d.calContext,{explore:true});return false;}
    if(d.calSelectMode){s.mode=d.calSelectMode==='range'?'range':'day';s.pending=false;s.anchor=null;if(s.mode==='day')setCalendarRange(s,s.focus);refresh();return true;}
    if(d.calPreset){calendarPreset(s,d.calPreset,a.NOW);focusContext();refresh();return true;}
    if(d.calRangeApply){const draft=s.draft||s;if(setCalendarRange(s,draft.start,draft.end)){s.mode=s.start===s.end?'day':'range';focusContext();}refresh('[data-cal-range-apply]');return true;}
    if(d.calRangeShift){shiftCalendarRange(s,Number(d.calRangeShift));focusContext();refresh();return true;}
    if(d.calReveal){s.month=s.focus.slice(0,7);refresh();return true;}
    if(d.calToggleDay){if(calendarDayGroups(events(s)).some(group=>group.date===d.calToggleDay)){const closed=closedDays();closed.has(d.calToggleDay)?closed.delete(d.calToggleDay):closed.add(d.calToggleDay);refresh(`[data-cal-toggle-day="${d.calToggleDay}"]`);}return true;}
    if(d.calCollapseDays||d.calExpandDays){const closed=closedDays();for(const group of calendarDayGroups(events(s)))d.calCollapseDays?closed.add(group.date):closed.delete(group.date);refresh(d.calCollapseDays?'[data-cal-collapse-days]':'[data-cal-expand-days]');return true;}
    if(d.calPage){s.page=Number(d.calPage);refresh();return true;}
    if(d.calPanel){s.panel='range';refresh();return true;}
    if(d.calendarMode){view=d.calendarMode==='agenda'?'agenda':'month';refresh();return true;}
    if(d.calendarFilter){if(types.includes(d.calendarFilter))filters()[d.calendarFilter]=!filters()[d.calendarFilter];s.page=1;refresh();return true;}
    if(d.calendarShift){s.month=moveDate(s.month+'-01',0,Number(d.calendarShift)).slice(0,7);refresh();return true;}
    if(d.calendarReference){calendarPreset(s,'today',a.NOW);focusContext();refresh();return true;}
    if(d.panelDayShift){const next=moveDate(s.focus,Number(d.panelDayShift));if(s.start===s.end||insideSelection(s,next))select(next,{explore:true,focusSelector:`[data-panel-day-shift="${d.panelDayShift}"]`});return true;}
    if(d.calendarBack){document.getElementById('calendar-month-content')?.scrollIntoView({behavior:'smooth',block:'start'});return true;}
    if(d.calendarFull){focusContext();a.setAccount('all');a.open('day',s.focus);return true;}
    if(d.calendarAdd){focusContext();a.open(d.calendarAdd==='task'?'task-template':'obligation-template');a.current.fromCalendar=true;return true;}
    if(d.calOpenFlow){a.openCashbook({start:s.start,end:s.end},s.flowAccount);return true;}
    return false;
  }
  function change(e){
    const t=e.target,s=state();
    if(t.hasAttribute('data-cal-range-start')||t.hasAttribute('data-cal-range-end')){s.draft??={start:s.start,end:s.end};s.draft[t.hasAttribute('data-cal-range-start')?'start':'end']=t.value;s.error='';return true;}
    if(t.hasAttribute('data-cal-flow-account')){s.flowAccount=t.value==='all'||a.scope('accounts').some(b=>b.id===t.value)?t.value:'all';refresh();return true;}
    if(t.hasAttribute('data-calendar-month')){if(validDate(t.value+'-01')){s.month=t.value;refresh();}return true;}
    if(t.hasAttribute('data-calendar-completed')){filters().completed=t.checked;s.page=1;refresh();return true;}
    if(t.hasAttribute('data-panel-day-date')){if(validDate(t.value))select(t.value,{explore:true,focusSelector:'[data-panel-day-date]'});else a.toast('Escolha uma data válida.');return true;}
    return false;
  }
  function preview(start,end){if(start>end)[start,end]=[end,start];for(const cell of document.querySelectorAll('[data-cal-cell]'))cell.classList.toggle('range-preview',!!start&&cell.dataset.calCell>=start&&cell.dataset.calCell<=end);}
  function pointer(e){
    if(e.type==='pointerdown'){
      if(e.pointerType==='touch'||e.button!==0||state().mode!=='range'||!e.target.closest?.('[data-cal-day]'))return;
      const date=e.target.closest('[data-cal-cell]')?.dataset.calCell;if(date)drag={id:e.pointerId,company:a.company,start:date,last:date,moved:false};return;
    }
    if(!drag||e.pointerId!==drag.id)return;
    if(e.type==='pointercancel'||drag.company!==a.company){drag=null;preview(null,null);return;}
    if(e.type==='pointermove'){
      if(e.buttons===0){drag=null;preview(null,null);return;}
      const cell=document.elementFromPoint?.(e.clientX,e.clientY)?.closest('[data-cal-cell]');
      if(cell){drag.last=cell.dataset.calCell;drag.moved ||= drag.last!==drag.start;if(drag.moved){e.preventDefault();preview(drag.start,drag.last);}}return;
    }
    if(e.type==='pointerup'){
      const selected=drag;drag=null;preview(null,null);
      if(selected.moved){const s=state();setCalendarRange(s,selected.start,selected.last,selected.last);s.mode='range';s.month=selected.last.slice(0,7);suppressUntil=Date.now()+350;focusContext();refresh();}
    }
  }
  function keydown(e){
    const s=state();
    if(e.key==='Escape'&&(drag||s.pending)&&!e.target.closest?.('[role=dialog]')){drag=null;preview(null,null);if(s.pending&&s.previous){const p=s.previous;setCalendarRange(s,p.start,p.end,p.focus);s.month=p.month;}s.pending=false;s.anchor=null;focusContext();refresh();e.preventDefault();return true;}
    if(e.key==='Enter'&&e.target.matches?.('[data-cal-range-start],[data-cal-range-end]')){change(e);click({calRangeApply:'1'});e.preventDefault();return true;}
    const date=e.target.dataset?.calDay,step={ArrowLeft:-1,ArrowRight:1,ArrowUp:-7,ArrowDown:7}[e.key];
    if(date&&step){e.preventDefault();select(moveDate(date,step),{extend:e.shiftKey,explore:!e.shiftKey});return true;}
    return false;
  }
  return {render,click,change,pointer,keydown,externalDate(date){if(validDate(date)){const s=state();setCalendarRange(s,date);s.mode='day';}},get selection(){return {...state()};}};
}
