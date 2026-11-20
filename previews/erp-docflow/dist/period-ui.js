import {financialHierarchy,obligationCategory,CLASSIFICATION_STATES} from './financial-hierarchy.js?v=30';
import {statementOrder} from './statement-model.js?v=17';
import {MONTHS,total} from './data.js?v=17';
import {planningBook,planningSummary,planningHistoryRange,planningRemaining} from './planning-book-model.js?v=31';
import {planningCoverageHTML,planningAgendaHTML} from './planning-book-ui.js?v=31';
import {presetRange,validDate,bucketCount,moveDate,rangeDays} from './range-model.js?v=17';

export function createPeriodSheet(a,context){
  const {esc,money,fullDate,icon,btn}=a;
  let period='daily',preset=a.state.dataset?.defaultCashbookPreset||(a.state.dataset?'month':'week'),range=null,draft=null,error='',historyCompany=null,historyAccount=null;
  const presets=[['today','Hoje'],['next30','Próximos 30 dias'],['day','Dia selecionado'],['week','Semana'],['month','Mês'],['quarter','Trimestre'],['semester','Semestre'],['year','Ano'],['twelve','Últimos 12 meses'],['history','Todos os registros'],['custom','Personalizado']];
  const expanded=new Set(['real:all:incoming','real:all:outgoing']);
  let includeInitial=true;
  const labels={daily:'Dia',monthly:'Mês',yearly:'Ano'};
  const format=n=>n==null?'—':money(n).replace('R$','').trim();
  const weekday=d=>new Intl.DateTimeFormat('pt-BR',{weekday:'short',timeZone:'UTC'}).format(new Date(d+'T12:00:00Z')).replace('.','');
  function currentRange(){
    if(!range||(preset==='history'&&(historyCompany!==a.company||historyAccount!==a.account))){
      const fallback=presetRange('month',context.selected);
      range=preset==='history'?planningHistoryRange(a.state,a.company,a.account,fallback):presetRange(preset,context.selected);
      historyCompany=a.company;historyAccount=a.account;
    }
    return range;
  }
  function periods(account=a.account){return planningBook(a.state,a.company,currentRange(),period,account,a.NOW);}
  function commit(next,nextPreset='custom'){
    if(!validDate(next.start)||!validDate(next.end)){error='Preencha as duas datas válidas (a partir de 1900).';return false;}
    if(next.start>next.end){error='A data final deve ser igual ou posterior à data inicial.';return false;}
    if(bucketCount(next,'yearly')>366){error='Reduza o intervalo para exibir até 366 anos.';return false;}
    let adjusted=false;
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
  const isTodayColumn=p=>Boolean(a.NOW&&p.start<=a.NOW&&a.NOW<=p.end);
  const columnClass=p=>[period==='daily'&&p.key===context.selected?'selected-col':'',isTodayColumn(p)?'today-col':''].filter(Boolean).join(' ');
  const todayLabel=()=>period==='daily'?'Hoje':period==='monthly'?'Mês atual':'Ano atual';
  function todayGuide(columns){
    if(!a.NOW)return '';
    const visible=columns.some(isTodayColumn);
    const note=visible?`${todayLabel()} em verde. O dia selecionado mantém a marca azul.`:'Hoje está fora do período exibido. Você pode ir para hoje mesmo sem extrato.';
    return `<div class="sheet-today-guide ${visible?'in-period':'outside-period'}"><div><span class="sheet-today-chip">Hoje · ${fullDate(a.NOW)}</span><span>${note}</span></div>${btn(visible?'Localizar hoje':'Ir para hoje','data-sheet-today="1"')}</div>`;
  }

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
      const direction=financialHierarchy(a.state,a.company,tx,{includeInitial}).find(d=>d.id===key);
      for(const group of direction.groups){
        const groupId=id+':category:'+group.id;
        result.push({label:group.label,cls:'sheet-category '+(incoming?'entry-row':'exit-row'),classification:true,toggle:groupId,count:group.count,
          sub:[group.initial?group.initial+' inicial(is)':'',group.reviewed?group.reviewed+' revisado(s)':''].filter(Boolean).join(' · '),
          values:columns.map(p=>group.entries.filter(e=>e.transaction.date>=p.start&&e.transaction.date<=p.end).reduce((n,e)=>n+e.amount,0)),total:group.total});
        if(!expanded.has(groupId))continue;
        for(const entry of group.entries){
          const t=entry.transaction,obligation=a.get('obligations',t.obligation),account=a.get('accounts',t.account);
          result.push({label:obligation?.party||t.description,sub:`${fullDate(t.date)} · ${account?.name||'Conta'} · ${CLASSIFICATION_STATES[entry.status]}${entry.part?' · Parcela '+entry.index+'/'+entry.parts+' de '+money(Math.abs(t.amount)):''}`,
            cls:'sheet-detail sheet-allocation '+(incoming?'entry-row':'exit-row'),detail:true,target:t.imported?{kind:'transaction',id:t.id}:obligation?{kind:'obligation',id:obligation.id}:{kind:'day',id:t.date},
            values:columns.map(p=>t.date>=p.start&&t.date<=p.end?entry.amount:0),total:entry.amount});
        }
      }
    }

    function obligationRows(label,key,incoming,pending){
      const id='planned:'+key,obs=columns.flatMap(p=>p.obligations).filter(o=>o.kind===(incoming?'in':'out')&&(!pending||planningRemaining(a.state,o)>0)).sort((x,y)=>x.due.localeCompare(y.due)||x.id.localeCompare(y.id));
      row(label,key,pending?(incoming?'entry-row':'exit-row'):'planned-row','sum',columns,{toggle:id,count:obs.length});
      if(!expanded.has(id))return;
      if(!obs.length){result.push({label:'Nenhuma obrigação neste período.',notice:true});return;}
      const groups=new Map();
      for(const o of obs){const category=obligationCategory(a.state,a.company,o);if(!groups.has(category.id))groups.set(category.id,{...category,items:[]});groups.get(category.id).items.push(o);}
      for(const group of groups.values()){
        const groupId=id+':category:'+group.id,amount=o=>pending?planningRemaining(a.state,o):total(o);
        result.push({label:group.label,cls:'sheet-category planned-row',classification:true,toggle:groupId,count:group.items.length,values:columns.map(p=>group.items.filter(o=>o.due>=p.start&&o.due<=p.end).reduce((n,o)=>n+amount(o),0)),total:group.items.reduce((n,o)=>n+amount(o),0)});
        if(expanded.has(groupId))for(const o of group.items)result.push({label:o.title,sub:`${fullDate(o.due)} · ${o.party}`,cls:'sheet-detail sheet-allocation planned-row',detail:true,target:{kind:'obligation',id:o.id},values:columns.map(p=>o.due>=p.start&&o.due<=p.end?amount(o):0),total:amount(o)});
      }
    }
    const unit=period==='daily'?'dia':period==='monthly'?'mês':'ano';
    row('Saldo realizado · abertura','opening','balance-row','first');
    row('Movimento registrado no '+unit,'movement','movement-row');
    row('Saldo realizado · fechamento','closing','closing-row','last');
    row('Saldo de referência','reference','reference-row','last');
    row('Projeção com obrigações','projected','projection-row','last');
    section('REGISTRADO · MOVIMENTOS BANCÁRIOS');
    movementRows('Entradas registradas','incoming',columns);
    movementRows('Saídas registradas','outgoing',columns);
    for(const account of a.scope('accounts').filter(x=>a.account==='all'||x.id===a.account)){
      const bankPeriods=periods(account.id);
      section(account.name);
      movementRows('Entradas','incoming',bankPeriods,account.id);
      movementRows('Saídas','outgoing',bankPeriods,account.id);
      row('Saldo realizado da conta','closing','bank-balance','last',bankPeriods);
    }
    section('OBRIGAÇÕES · PELA DATA DE VENCIMENTO');
    obligationRows('Total previsto a receber','dueIn',true,false);
    obligationRows('Total previsto a pagar','dueOut',false,false);
    obligationRows('Ainda a receber','pendingIn',true,true);
    obligationRows('Ainda a pagar','pendingOut',false,true);
    section('PREVISÕES DO HISTÓRICO · FORA DOS SALDOS');
    for(const [direction,key,label] of [[1,'forecastIn','Entradas a confirmar'],[-1,'forecastOut','Saídas a confirmar']]){
      const id='forecast:'+key,items=columns.flatMap(p=>p.forecasts).filter(f=>f.direction===direction);
      row(label,key,'forecast-row','sum',columns,{toggle:id,count:items.length});
      if(expanded.has(id))for(const f of items)result.push({label:f.title,sub:fullDate(f.date)+' · '+f.label,cls:'sheet-detail forecast-row',detail:true,target:{kind:'forecast',id:f.id},values:columns.map(p=>f.date>=p.start&&f.date<=p.end?f.amount:0),total:f.amount});
    }
    return result;
  }
  function target(p){return period==='daily'?`data-open="day" data-id="${p.key}"`:`data-sheet-drill="${p.key}"`;}
  function render(){
    const columns=periods(),data=rows(columns),title=period==='daily'?'Fluxo por dia':period==='monthly'?'Fluxo por mês':'Fluxo por ano';
    const help=period==='daily'?'Dias nas colunas · clique para abrir o dia':period==='monthly'?'Meses nas colunas · clique para abrir os dias do mês':'Anos nas colunas · clique para abrir os meses do ano';
    const body=data.map(r=>{
      if(r.section)return `<tr class="sheet-section"><th scope="row">${esc(r.label)}</th>${columns.map(p=>`<td class="${columnClass(p)}"></td>`).join('')}<td class="period-total"></td></tr>`;
      if(r.notice)return `<tr class="sheet-empty-detail"><td colspan="${columns.length+2}">${esc(r.label)}</td></tr>`;
      const attrs=r.target?`data-open="${r.target.kind}" data-id="${esc(r.target.id)}"`:'';
      const heading=r.toggle?`<button class="sheet-expand" data-sheet-toggle="${esc(r.toggle)}" aria-expanded="${expanded.has(r.toggle)}" aria-label="${expanded.has(r.toggle)?'Recolher':'Expandir'} ${esc(r.label)}${r.toggle.startsWith('real:all')?' · todas as contas':r.toggle.startsWith('real:')?' · '+esc(a.get('accounts',r.toggle.split(':')[1])?.name||''):''}">${icon(expanded.has(r.toggle)?'down':'chevron')}<span>${esc(r.label)}${r.sub?`<small class="sheet-category-status">${esc(r.sub)}</small>`:''}</span><small>${r.count}</small></button>`:r.detail?`<button class="sheet-detail-link" ${attrs} title="${esc(r.label+' · '+r.sub)}"><b>${esc(r.label)}</b><small>${esc(r.sub)}</small></button>`:esc(r.label);
      return `<tr class="${r.cls||''}"><th scope="row" ${r.detail?'class="sheet-detail-label"':''}>${heading}</th>${columns.map((p,i)=>`<td class="money ${columnClass(p)}">${r.detail&&!r.values[i]?'<span class="zero">—</span>':`<button ${r.detail?attrs:r.classification?`data-sheet-toggle="${esc(r.toggle)}"`:target(p)} aria-label="${esc(r.label)} · ${esc(columnLabel(p))}: ${r.values[i]==null?'Sem saldo confirmado':money(r.values[i])}">${r.values[i]==null?'<span class="unknown">—</span>':r.values[i]===0?'<span class="zero">—</span>':format(r.values[i])}</button>`}</td>`).join('')}<td class="money period-total">${format(r.total)}</td></tr>`;
    }).join('');
    return `<section class="panel workbook-panel"><div class="sheet-caption"><div><span class="sheet-badge">LIVRO CAIXA</span><h2>${title}</h2><p>${help}</p></div><div class="sheet-legend"><span><i class="real-dot"></i>Realizado</span><span><i class="planned-dot"></i>Previsto</span><span>Valores em R$</span></div></div>${rangeControls()}<label class="sheet-classification-option"><input type="checkbox" data-sheet-initial ${includeInitial?'checked':''}> Incluir classificações iniciais (a revisar)</label>${todayGuide(columns)}${planningCoverageHTML(a,currentRange())}<div class="sheet-detail-guide"><span>${icon('chevron')} Entradas / Saídas · Classificação · Lançamentos. Expanda cada nível.</span>${expanded.size?btn('Recolher detalhes','data-sheet-collapse="1"'):''}</div><div class="sheet-scroll" tabindex="0" aria-label="Planilha agrupada por ${labels[period].toLowerCase()}, role horizontalmente para ver os períodos"><table class="cash-sheet"><thead><tr><th scope="col" class="sheet-label">Descrição / conta</th>${columns.map(p=>`<th scope="col" class="${columnClass(p)}"><button ${target(p)} ${isTodayColumn(p)?`data-sheet-current="1" aria-current="${period==='daily'?'date':'true'}"`: ''} aria-label="Abrir ${esc(columnLabel(p))}${isTodayColumn(p)?' · '+todayLabel():''}"><b>${period==='daily'?p.key.slice(8):period==='monthly'?MONTHS[Number(p.key.slice(5))-1].slice(0,3):p.key}</b><small>${period==='daily'?weekday(p.key):period==='monthly'?p.key.slice(0,4):'Ver meses'}</small>${!p.complete?'<small class="sheet-missing-tag">'+(p.coverage.some(c=>c.status==='full'||c.status==='partial')?'Extrato parcial':'Sem extrato')+'</small>':''}${isTodayColumn(p)?`<small class="sheet-today-tag">${todayLabel()}</small>`:''}${p.transactions.length||p.obligations.length||p.forecasts.length||p.tasks.length?'<i class="day-dot"></i>':''}</button></th>`).join('')}<th scope="col" class="period-total">Período<br>exibido</th></tr></thead><tbody>${body}</tbody></table></div><div class="sheet-note"><span>${fullDate(columns[0].start)} a ${fullDate(columns.at(-1).end)} · apenas as datas deste intervalo entram nos totais, inclusive em meses ou anos parciais. Saldos realizados sem cobertura aparecem como —. Referência e projeção são valores separados.</span><span>Parcelas usam somente o valor classificado, sem duplicar o movimento. Obrigações sem classificação própria ficam em A classificar; pagamentos parciais não são rateados automaticamente.</span></div></section>${planningAgendaHTML(a,planningSummary(columns))}`;
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
    if(d.sheetToday){
      if(!periods().some(isTodayColumn)){period='daily';commit({start:a.NOW,end:a.NOW},'today');refresh('[data-sheet-current]');return true;}
      const scroll=document.querySelector('.workbook-panel .sheet-scroll'),button=scroll?.querySelector('[data-sheet-current]');
      if(scroll&&button){
        const box=scroll.getBoundingClientRect(),cell=button.getBoundingClientRect(),label=scroll.querySelector('.sheet-label')?.getBoundingClientRect().width||0,total=scroll.querySelector('thead .period-total');
        const end=total&&getComputedStyle(total).position==='sticky'?total.getBoundingClientRect().width:0;
        const center=box.left+label+(box.width-label-end)/2;
        scroll.scrollLeft+=cell.left+cell.width/2-center;
        button.focus({preventScroll:true});
      }
      return true;
    }
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
      const columns=periods(),data=rows(columns),safe=v=>{let value=String(v);if(!/^-?\d+,\d{2}$/.test(value))value=value.replace(/^[=+@-]/,"'$&");return '"'+value.replaceAll('"','""')+'"';};
      const csv=[[a.state.dataset?'FLUXO DE CAIXA · REGISTROS E PLANEJAMENTO':'DEMONSTRAÇÃO · DADOS FICTÍCIOS'],[a.get('companies',a.company).name,a.account==='all'?'Todas as contas':a.get('accounts',a.account).name],['Período',fullDate(currentRange().start),fullDate(currentRange().end)],['Tipo de linha','Descrição / conta',...columns.map(columnLabel),'Período exibido'],['Informação','Cobertura',...columns.map(p=>p.complete?'Completa':p.coverage.some(c=>c.status==='full'||c.status==='partial')?'Parcial':'Sem extrato'),'Saldos desconhecidos em branco'],...data.filter(r=>!r.notice).map(r=>r.section?['Seção',r.label]:[r.detail?'Lançamento / parcela':r.classification?'Subtotal da classificação':'Resumo / total',r.label+(r.sub?' · '+r.sub:''),...r.values.map(v=>v==null?'':(v/100).toFixed(2).replace('.',',')),r.total==null?'':(r.total/100).toFixed(2).replace('.',',')])];
      a.download(`Livro-caixa-${period}-${columns[0].start}-${columns.at(-1).end}.csv`,'\ufeff'+csv.map(r=>r.map(safe).join(';')).join('\r\n'),'text/csv;charset=utf-8');a.toast('Grade exportada com o período, a conta e os detalhes exibidos.');return true;
    }
    return false;
  }
  function change(e){
    if(e.target.hasAttribute('data-sheet-initial')){includeInitial=e.target.checked;refresh('[data-sheet-initial]');return true;}
    if(e.target.hasAttribute('data-range-start')||e.target.hasAttribute('data-range-end')){draft??={...currentRange()};draft[e.target.hasAttribute('data-range-start')?'start':'end']=e.target.value;error='';return true;}
    if(e.target.hasAttribute('data-range-preset')){const nextPreset=e.target.value;if(nextPreset==='custom'){preset='custom';draft={...currentRange()};refresh('[data-range-start]');return true;}const ids=new Set(a.scope('accounts').map(x=>x.id)),dates=[...a.state.transactions.filter(t=>ids.has(t.account)).map(t=>t.date),...a.scope('obligations').map(o=>o.due)];commit(nextPreset==='today'?{start:a.NOW,end:a.NOW}:nextPreset==='next30'?{start:a.NOW,end:moveDate(a.NOW,29)}:nextPreset==='history'?planningHistoryRange(a.state,a.company,a.account,presetRange('month',context.selected)):presetRange(nextPreset,context.selected,dates),nextPreset);refresh('[data-range-preset]');return true;}
    return false;
  }
  document.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.matches('[data-range-start],[data-range-end]')){e.preventDefault();draft??={...currentRange()};draft[e.target.hasAttribute('data-range-start')?'start':'end']=e.target.value;applyDraft();}});
  return {render,click,change,setRange(next){period=rangeDays(next)<=93?'daily':'monthly';return commit(next)},summary:()=>planningSummary(periods()),daily(window='week'){period='daily';preset=window;range=null;draft=null;error='';}};
}
