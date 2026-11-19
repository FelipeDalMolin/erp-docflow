import {fitStatementRange,statementCoverage,statementOrder} from './statement-model.js?v=17';
import {MONTHS,remaining,total} from './data.js?v=17';
import {summarizePeriods} from './workbook-model.js?v=17';
import {rangeBook,presetRange,validDate,bucketCount,moveDate,rangeDays} from './range-model.js?v=17';

export function createPeriodSheet(a,context){
  const {esc,money,fullDate,icon,btn}=a;
  let period='daily',preset=a.state.dataset?.defaultCashbookPreset||(a.state.dataset?'month':'week'),range=null,draft=null,error='',historyCompany=null,historyAccount=null;
  const presets=[['day','Dia selecionado'],['week','Semana'],['month','Mês'],['quarter','Trimestre'],['semester','Semestre'],['year','Ano'],['twelve','Últimos 12 meses'],['history','Todos os registros'],['custom','Personalizado']];
  const expanded=new Set();
  const labels={daily:'Dia',monthly:'Mês',yearly:'Ano'};
  const format=n=>money(n).replace('R$','').trim();
  const weekday=d=>new Intl.DateTimeFormat('pt-BR',{weekday:'short',timeZone:'UTC'}).format(new Date(d+'T12:00:00Z')).replace('.','');
  function currentRange(){
    if(!range||(preset==='history'&&(historyCompany!==a.company||historyAccount!==a.account))){
      const dates=a.scope('obligations').map(o=>o.due);
      // Movements may be scoped by account even when they have no company field.
      const ids=new Set(a.scope('accounts').map(x=>x.id));dates.push(...a.state.transactions.filter(t=>ids.has(t.account)).map(t=>t.date));
      range=(preset==='history'?statementCoverage(a.state,a.company,a.account):null)||fitStatementRange(a.state,a.company,presetRange(preset,context.selected,dates),a.account)||a.state.dataset?.period||presetRange(preset,context.selected,dates);historyCompany=a.company;historyAccount=a.account;
    }
    const fitted=fitStatementRange(a.state,a.company,range,a.account);range=fitted||statementCoverage(a.state,a.company,a.account)||range;
    return range;
  }
  function periods(account=a.account){return rangeBook(a.state,a.company,currentRange(),period,account);}
  function commit(next,nextPreset='custom'){
    if(!validDate(next.start)||!validDate(next.end)){error='Preencha as duas datas válidas (a partir de 1900).';return false;}
    if(next.start>next.end){error='A data final deve ser igual ou posterior à data inicial.';return false;}
    if(bucketCount(next,'yearly')>366){error='Reduza o intervalo para exibir até 366 anos.';return false;}
    const fitted=fitStatementRange(a.state,a.company,next,a.account);if(!fitted){error='Não há extrato no intervalo escolhido. Consulte a cobertura da conta em Sobre a importação.';return false;}if(fitted.start!==next.start||fitted.end!==next.end)a.toast('Período limitado às datas dos extratos carregados.');next=fitted;let adjusted=false;
    if(period==='daily'&&bucketCount(next,period)>366){period='monthly';adjusted=true;}
    if(period==='monthly'&&bucketCount(next,period)>366){period='yearly';adjusted=true;}
    range={...next};preset=nextPreset;draft=null;error='';historyCompany=a.company;historyAccount=a.account;context.pick(range.start);
    if(adjusted)a.toast('Agrupamento ajustado para manter a leitura do intervalo completo.');
    return true;
  }
  function applyDraft(){const ok=commit(draft||currentRange());refresh(ok?'[data-sheet-apply]':'[data-range-start]');return ok;}
  function rangeControls(){
    const applied=currentRange(),values=draft||applied;
    return `<div class="sheet-range-controls"><div class="range-fields"><label>Período<select data-range-preset aria-label="Atalho de período">${presets.map(([key,label])=>`<option value="${key}" ${preset===key?'selected':''}>${label}</option>`).join('')}</select></label><label>De<input type="date" min="1900-01-01" max="9999-12-31" value="${esc(values.start)}" data-range-start aria-label="Data inicial"></label><label>Até<input type="date" min="1900-01-01" max="9999-12-31" value="${esc(values.end)}" data-range-end aria-label="Data final"></label>${btn('Aplicar','data-sheet-apply="1"','primary')}</div><p class="range-error" role="alert">${esc(error)}</p><div class="range-options"><div class="range-group"><span>Agrupar por</span><div class="segments" aria-label="Agrupamento da planilha">${Object.entries(labels).map(([key,label])=>`<button data-sheet-period="${key}" class="${period===key?'active':''}" aria-pressed="${period===key}" ${bucketCount(applied,key)>366?'disabled title="Reduza o intervalo para usar este agrupamento"':''}>${label}</button>`).join('')}</div></div><div class="range-navigation"><button data-range-shift="-1" aria-label="Período anterior" title="Período anterior">${icon('back')}</button><span>${fullDate(applied.start)} — ${fullDate(applied.end)}</span><button data-range-shift="1" aria-label="Próximo período" title="Próximo período">${icon('chevron')}</button></div></div><div class="range-actions"><span>O período define os dados; o agrupamento muda as colunas.</span><div><select aria-label="Filtrar conta" data-account><option value="all">Todas as contas</option>${a.scope('accounts').map(x=>`<option value="${x.id}" ${a.account===x.id?'selected':''}>${esc(x.name)}</option>`).join('')}</select>${btn('Exportar grade','data-book-export="1"','','download')}</div></div></div>`;
  }
  const columnLabel=p=>period==='daily'?fullDate(p.key):period==='monthly'?MONTHS[Number(p.key.slice(5))-1]+' '+p.key.slice(0,4):p.key;
  function rows(columns){
    const result=[];
    const section=label=>result.push({label,section:true});
    const row=(label,key,cls='',roll='sum',source=columns,extra={})=>{
      const values=source.map(p=>p[key]);
      result.push({label,cls,values,total:roll==='first'?values[0]:roll==='last'?values.at(-1):values.reduce((s,v)=>s+v,0),...extra});
    };
    function movementRows(label,key,source,bank='all'){
      const incoming=key==='incoming',id=`real:${bank}:${key}`;
      const tx=source.flatMap(p=>p.transactions).filter(t=>incoming?t.amount>0:t.amount<0).sort(statementOrder);
      row(label,key,incoming?'entry-row':'exit-row','sum',source,{toggle:id,count:tx.length});
      if(!expanded.has(id))return;
      if(!tx.length){result.push({label:'Nenhum lançamento neste período.',notice:true});return;}
      for(const t of tx){
        const obligation=a.get('obligations',t.obligation),account=a.get('accounts',t.account);
        result.push({label:obligation?.party||t.description,sub:`${fullDate(t.date)} · ${account?.name||'Conta'} · ${obligation?.title||t.description}`,
          cls:'sheet-detail '+(incoming?'entry-row':'exit-row'),detail:true,target:t.imported?{kind:'transaction',id:t.id}:obligation?{kind:'obligation',id:obligation.id}:{kind:'day',id:t.date},
          values:columns.map(p=>t.date>=p.start&&t.date<=p.end?Math.abs(t.amount):0),total:Math.abs(t.amount)});
      }
    }
    function obligationRows(label,key,incoming,pending){
      const id='planned:'+key,obs=columns.flatMap(p=>p.obligations).filter(o=>o.kind===(incoming?'in':'out')&&(!pending||remaining(a.state,o)>0)).sort((x,y)=>x.due.localeCompare(y.due)||x.id.localeCompare(y.id));
      row(label,key,pending?(incoming?'entry-row':'exit-row'):'planned-row','sum',columns,{toggle:id,count:obs.length});
      if(!expanded.has(id))return;
      if(!obs.length){result.push({label:'Nenhuma obrigação neste período.',notice:true});return;}
      for(const o of obs){const amount=pending?remaining(a.state,o):total(o);result.push({label:o.title,sub:`${fullDate(o.due)} · ${o.party}`,cls:'sheet-detail planned-row',detail:true,target:{kind:'obligation',id:o.id},values:columns.map(p=>o.due>=p.start&&o.due<=p.end?amount:0),total:amount});}
    }
    const unit=period==='daily'?'dia':period==='monthly'?'mês':'ano';
    row('Saldo inicial','opening','balance-row','first');
    row('Movimento do '+unit,'movement','movement-row');
    row('Saldo final do '+unit,'closing','closing-row','last');
    section('REALIZADO · MOVIMENTOS BANCÁRIOS');
    movementRows('Total das entradas','incoming',columns);
    movementRows('Total das saídas','outgoing',columns);
    for(const account of a.scope('accounts').filter(x=>a.account==='all'||x.id===a.account)){
      const bankPeriods=periods(account.id);
      section(account.name);
      movementRows('Entradas','incoming',bankPeriods,account.id);
      movementRows('Saídas','outgoing',bankPeriods,account.id);
      row('Saldo da conta','closing','bank-balance','last',bankPeriods);
    }
    section('OBRIGAÇÕES · PELA DATA DE VENCIMENTO');
    obligationRows('Total previsto a receber','dueIn',true,false);
    obligationRows('Total previsto a pagar','dueOut',false,false);
    obligationRows('Ainda a receber','pendingIn',true,true);
    obligationRows('Ainda a pagar','pendingOut',false,true);
    return result;
  }
  function target(p){return period==='daily'?`data-open="day" data-id="${p.key}"`:`data-sheet-drill="${p.key}"`;}
  function render(){
    const columns=periods(),data=rows(columns),title=period==='daily'?'Fluxo por dia':period==='monthly'?'Fluxo por mês':'Fluxo por ano';
    const help=period==='daily'?'Dias nas colunas · clique para abrir o dia':period==='monthly'?'Meses nas colunas · clique para abrir os dias do mês':'Anos nas colunas · clique para abrir os meses do ano';
    const body=data.map(r=>{
      if(r.section)return `<tr class="sheet-section"><th scope="row">${esc(r.label)}</th><td colspan="${columns.length+1}"></td></tr>`;
      if(r.notice)return `<tr class="sheet-empty-detail"><td colspan="${columns.length+2}">${esc(r.label)}</td></tr>`;
      const attrs=r.target?`data-open="${r.target.kind}" data-id="${esc(r.target.id)}"`:'';
      const heading=r.toggle?`<button class="sheet-expand" data-sheet-toggle="${esc(r.toggle)}" aria-expanded="${expanded.has(r.toggle)}" aria-label="${expanded.has(r.toggle)?'Recolher':'Expandir'} ${esc(r.label)}${r.toggle.startsWith('real:all')?' · todas as contas':r.toggle.startsWith('real:')?' · '+esc(a.get('accounts',r.toggle.split(':')[1])?.name||''):''}">${icon(expanded.has(r.toggle)?'down':'chevron')}<span>${esc(r.label)}</span><small>${r.count}</small></button>`:r.detail?`<button class="sheet-detail-link" ${attrs} title="${esc(r.label+' · '+r.sub)}"><b>${esc(r.label)}</b><small>${esc(r.sub)}</small></button>`:esc(r.label);
      return `<tr class="${r.cls||''}"><th scope="row" ${r.detail?'class="sheet-detail-label"':''}>${heading}</th>${columns.map((p,i)=>`<td class="money ${period==='daily'&&p.key===context.selected?'selected-col':''}">${r.detail&&!r.values[i]?'<span class="zero">—</span>':`<button ${r.detail?attrs:target(p)} aria-label="${esc(r.label)} · ${esc(columnLabel(p))}: ${money(r.values[i])}">${r.values[i]===0?'<span class="zero">—</span>':format(r.values[i])}</button>`}</td>`).join('')}<td class="money period-total">${format(r.total)}</td></tr>`;
    }).join('');
    return `<section class="panel workbook-panel"><div class="sheet-caption"><div><span class="sheet-badge">LIVRO CAIXA</span><h2>${title}</h2><p>${help}</p></div><div class="sheet-legend"><span><i class="real-dot"></i>Realizado</span><span><i class="planned-dot"></i>Previsto</span><span>Valores em R$</span></div></div>${rangeControls()}<div class="sheet-detail-guide"><span>${icon('chevron')} Expanda entradas e saídas para ver seus lançamentos.</span>${expanded.size?btn('Recolher detalhes','data-sheet-collapse="1"'):''}</div><div class="sheet-scroll" tabindex="0" aria-label="Planilha agrupada por ${labels[period].toLowerCase()}, role horizontalmente para ver os períodos"><table class="cash-sheet"><thead><tr><th scope="col" class="sheet-label">Descrição / conta</th>${columns.map(p=>`<th scope="col" class="${period==='daily'&&p.key===context.selected?'selected-col':''}"><button ${target(p)} aria-label="Abrir ${esc(columnLabel(p))}"><b>${period==='daily'?p.key.slice(8):period==='monthly'?MONTHS[Number(p.key.slice(5))-1].slice(0,3):p.key}</b><small>${period==='daily'?weekday(p.key):period==='monthly'?p.key.slice(0,4):'Ver meses'}</small>${p.transactions.length||p.obligations.length?'<i class="day-dot"></i>':''}</button></th>`).join('')}<th scope="col" class="period-total">Período<br>exibido</th></tr></thead><tbody>${body}</tbody></table></div><div class="sheet-note"><span>${fullDate(columns[0].start)} a ${fullDate(columns.at(-1).end)} · apenas as datas deste intervalo entram nos totais, inclusive em meses ou anos parciais. Saldos mostram a abertura e o fechamento.</span><span>Previsto mantém o total da obrigação; “Ainda” mostra o saldo em aberto.</span></div></section>`;
  }
  function refresh(selector){
    const panel=document.querySelector('.workbook-panel'),top=panel?.getBoundingClientRect().top,scroll=panel?.querySelector('.sheet-scroll'),left=scroll?.scrollLeft||0,y=scroll?.scrollTop||0;
    a.render();
    const next=document.querySelector('.workbook-panel'),nextScroll=next?.querySelector('.sheet-scroll');
    if(nextScroll){nextScroll.scrollLeft=left;nextScroll.scrollTop=y;}
    if(next&&top!==undefined)window.scrollBy({top:next.getBoundingClientRect().top-top,behavior:'instant'});
    next?.querySelector(selector)?.focus({preventScroll:true});
  }
  function click(d){
    if(d.sheetApply){applyDraft();return true;}
    if(d.rangeShift){
      const r=currentRange(),direction=Number(d.rangeShift),months={month:1,quarter:3,semester:6,year:12,twelve:12}[preset];
      let next;if(months){const anchor=moveDate(preset==='twelve'?r.end:r.start,0,direction*months);next=presetRange(preset,anchor);}else{const delta=direction*rangeDays(r);next={start:moveDate(r.start,delta),end:moveDate(r.end,delta)};}
      commit(next,preset==='history'?'custom':preset);refresh(`[data-range-shift="${d.rangeShift}"]`);return true;
    }
    if(d.sheetPeriod){if(draft&&!commit(draft)){refresh('[data-range-start]');return true;}if(bucketCount(currentRange(),d.sheetPeriod)>366){a.toast('Reduza o intervalo para usar este agrupamento.');return true;}period=d.sheetPeriod;refresh(`[data-sheet-period="${period}"]`);return true;}
    if(d.sheetToggle){expanded.has(d.sheetToggle)?expanded.delete(d.sheetToggle):expanded.add(d.sheetToggle);refresh(`[data-sheet-toggle="${CSS.escape(d.sheetToggle)}"]`);return true;}
    if(d.sheetCollapse){expanded.clear();refresh(`[data-sheet-period="${period}"]`);return true;}
    if(d.sheetDrill){const chosen=periods().find(p=>p.key===d.sheetDrill);if(chosen){period=d.sheetDrill.length===4?'monthly':'daily';commit({start:chosen.start,end:chosen.end});refresh(`[data-sheet-period="${period}"]`);const scroll=document.querySelector('.sheet-scroll');if(scroll){scroll.scrollLeft=0;scroll.scrollTop=0;}}return true;}
    if(d.bookExport){
      const columns=periods(),data=rows(columns),safe=v=>'"'+String(v).replaceAll('"','""')+'"';
      const csv=[[a.state.dataset?'EXTRATOS IMPORTADOS · HISTÓRICO 2026':'DEMONSTRAÇÃO · DADOS FICTÍCIOS'],[a.get('companies',a.company).name,a.account==='all'?'Todas as contas':a.get('accounts',a.account).name],['Período',fullDate(currentRange().start),fullDate(currentRange().end)],['Descrição / conta',...columns.map(columnLabel),'Período exibido'],...data.filter(r=>!r.notice).map(r=>r.section?[r.label]:[r.label+(r.sub?' · '+r.sub:''),...r.values.map(v=>(v/100).toFixed(2).replace('.',',')),(r.total/100).toFixed(2).replace('.',',')])];
      a.download(`Livro-caixa-${period}-${columns[0].start}-${columns.at(-1).end}.csv`,'\ufeff'+csv.map(r=>r.map(safe).join(';')).join('\r\n'),'text/csv;charset=utf-8');a.toast('Grade exportada com o período, a conta e os detalhes exibidos.');return true;
    }
    return false;
  }
  function change(e){
    if(e.target.hasAttribute('data-range-start')||e.target.hasAttribute('data-range-end')){draft??={...currentRange()};draft[e.target.hasAttribute('data-range-start')?'start':'end']=e.target.value;error='';return true;}
    if(e.target.hasAttribute('data-range-preset')){const nextPreset=e.target.value;if(nextPreset==='custom'){preset='custom';draft={...currentRange()};refresh('[data-range-start]');return true;}const ids=new Set(a.scope('accounts').map(x=>x.id)),dates=[...a.state.transactions.filter(t=>ids.has(t.account)).map(t=>t.date),...a.scope('obligations').map(o=>o.due)];commit((nextPreset==='history'?statementCoverage(a.state,a.company,a.account):null)||presetRange(nextPreset,context.selected,dates),nextPreset);refresh('[data-range-preset]');return true;}
    return false;
  }
  document.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.matches('[data-range-start],[data-range-end]')){e.preventDefault();draft??={...currentRange()};draft[e.target.hasAttribute('data-range-start')?'start':'end']=e.target.value;applyDraft();}});
  return {render,click,change,setRange(next){period=rangeDays(next)<=93?'daily':'monthly';return commit(next)},summary:()=>summarizePeriods(periods()),daily(window='week'){period='daily';preset=window;range=null;draft=null;error='';}};
}
