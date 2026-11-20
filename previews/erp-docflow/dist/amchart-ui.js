import {chartDays,chartRangeResult,chartBarTransactions} from './amchart-model.js?v=21';
import {chartMovementReferences} from './chart-correspondence-model.js?v=21';
import {loadAmCharts,createFinanceChart,financeSeries} from './amchart-runtime.js?v=34';
import {moveDate,validDate} from './range-model.js?v=19';
import {CHART_MODES,navigateChartRange} from './chart-navigation-model.js?v=19';

export function createAmChartPanel(a,hooks){
  const {esc,money,fullDate}=a;
  let rows=[],runtime=null,epoch=0,lastDate=null;
  function barDetails(){
    const s=hooks.settings(),selection=s.chartBar;
    if(!selection)return '<p class="am-bar-placeholder">Selecione uma barra ou a quantidade de entradas/saídas de um dia para ver os lançamentos e suas correspondências.</p>';
    const transactions=chartBarTransactions(hooks.data(),selection,s.chartBasis);
    const bank=hooks.data().accounts.find(x=>x.id===selection.account),incoming=selection.direction==='incoming';
    const total=transactions.reduce((n,t)=>n+t.amount,0);
    return `<div class="am-bar-heading"><div><span class="eyebrow">Correspondências da barra</span><h3 tabindex="-1" data-am-bar-title>${incoming?'Entradas':'Saídas'} · ${fullDate(selection.date)}</h3><p>${esc(bank?.name||'Todas as contas selecionadas')} · ${transactions.length} lançamento${transactions.length===1?'':'s'} · <b>${money(total)}</b></p></div><button class="textbtn" data-am-bar-clear="1">Fechar detalhes</button></div>${bank?'<button class="textbtn" data-am-bar-all="1">Ver também os outros bancos neste dia</button>':''}<div class="am-bar-records">${transactions.map(t=>{
      const refs=chartMovementReferences(a.state,t,a.company),account=hooks.data().accounts.find(x=>x.id===t.account);
      const related=[refs.obligation&&{kind:'obligation',item:refs.obligation,label:'Obrigação'},refs.contract&&{kind:'contract',item:refs.contract,label:'Contrato'},refs.asset&&{kind:'asset',item:refs.asset,label:'Ativo'},...refs.documents.map(item=>({kind:'document',item,label:'Documento relacionado'}))].filter(Boolean);
      return `<article class="am-bar-record"><div class="am-bar-record-main"><button class="am-bar-description" data-am-transaction="${esc(t.id)}">${esc(t.description||t.history||'Lançamento')}<small>${esc(account?.name||'Conta')} · ${t.sourceSequence?'Ordem '+t.sourceSequence+' no extrato':'Registro do sistema'}</small></button><strong class="${incoming?'incoming':'outgoing'}">${money(t.amount)}</strong></div><div class="am-bar-links">${refs.source?`<button class="textbtn" data-statement-source="${esc(t.id)}">${a.icon('file')}Ver origem no extrato${t.sourceRecord?' · registro '+t.sourceRecord:t.sourcePage?' · p. '+t.sourcePage:''}</button>`:''}${related.map(ref=>`<button class="textbtn" ${ref.kind==='asset'?`data-asset-page="${esc(ref.item.id)}"`:`data-open="${ref.kind}" data-id="${esc(ref.item.id)}"`}>${ref.label}: ${esc(ref.item.title||ref.item.name)}</button>`).join('')}${!related.length?'<span class="am-unlinked">Sem correspondência cadastrada</span>':''}</div></article>`;
    }).join('')||'<p class="am-note">Nenhum movimento compõe esta barra na base selecionada.</p>'}</div><p class="am-note">A origem no extrato identifica o registro bancário. Os vínculos acima são os já cadastrados; não indicam conciliação automática. A seleção desta barra não altera o intervalo do gráfico.</p>`;
  }
  function showBar(selection){
    const s=hooks.settings();
    if(!chartBarTransactions(hooks.data(),selection,s.chartBasis).length)return;
    s.chartBar=selection;
    const row=rows.find(row=>row.date===selection.date),read=document.querySelector('[data-am-readout]');
    if(read)read.innerHTML=readout(row);
    const box=document.querySelector('[data-am-bar-detail]');
    if(box){box.innerHTML=barDetails();box.querySelector('[data-am-bar-title]')?.focus({preventScroll:true});box.scrollIntoView?.({block:'nearest',behavior:'instant'});}
  }
  function readout(row){
    if(!row)return '';
    lastDate=row.date;
    const accounts=hooks.data().accounts;
    return `<div class="am-day-title"><b>${fullDate(row.date)}</b><span>${row.count} lançamentos no extrato</span><button class="textbtn" data-ov-chart-day="${row.date}">Ver lançamentos deste dia</button></div><div class="am-values"><span>Entradas<strong class="incoming">${money(row.incoming)}</strong><button class="am-count incoming" data-am-bar="incoming" data-am-bar-day="${row.date}" ${!row.incomingCount?'disabled':''}>${row.incomingCount} lançamento${row.incomingCount===1?'':'s'}</button></span><span>Saídas<strong class="outgoing">${money(row.outgoing)}</strong><button class="am-count outgoing" data-am-bar="outgoing" data-am-bar-day="${row.date}" ${!row.outgoingCount?'disabled':''}>${row.outgoingCount} lançamento${row.outgoingCount===1?'':'s'}</button></span><span>Resultado do dia<strong class="${row.net<0?'outgoing':'incoming'}">${money(row.net)}</strong></span><span>Saldo${row.partial?' · parcial':''}<strong>${row.balance===null?'Não informado':money(row.balance)}</strong></span></div><p class="am-bank-values">${accounts.map((account,i)=>`${esc(account.name)}${hooks.settings().chartBasis==='reported'&&account.statement?.balanceBasis!=='consolidated'?' (corrente; aplicações não informadas)':''}: <b>${row.banks?.[i]===undefined?'não informado':money(row.banks[i])}</b>`).join(' · ')}${row.internalCount&&hooks.settings().chartBasis==='reported'?' · '+row.internalCount+' aplicações/resgates automáticos fora das barras de entradas e saídas.':''}</p>`;
  }
  function activeRange(s){return s.chartDay?{start:s.chartDay,end:s.chartDay}:s.chartSelectionRange||s.chartZoomRange||s.range;}
  function windowRange(s){return s.chartDay?{start:s.chartDay,end:s.chartDay}:s.chartZoomRange||s.range;}
  function result(s){
    const totals=chartRangeResult(rows,activeRange(s));
    return `<div class="am-result-heading"><b>Resultado do intervalo analisado</b><span>${totals.count} lançamentos</span></div><div class="am-values"><span>Entradas<strong class="incoming">${money(totals.incoming)}</strong></span><span>Saídas<strong class="outgoing">${money(totals.outgoing)}</strong></span><span>Resultado líquido<strong class="${totals.net<0?'outgoing':'incoming'}">${money(totals.net)}</strong></span><span>Saldo identificado${totals.partial?' · parcial':''}<strong>${totals.balance===null?'Não informado':money(totals.balance)}</strong></span></div><details class="am-reconciliation"><summary>Como o resultado chega ao saldo</summary><p>Na base dos extratos: saldo inicial <b>${money(totals.opening??0)}</b> + resultado <b>${money(totals.net)}</b>${totals.excludedTransfers?' + aplicações/resgates automáticos <b>'+money(totals.excludedTransfers)+'</b>':''} = saldo final <b>${money(totals.closing??0)}</b>.</p><p>${s.chartBasis==='reported'?'Aplicações e resgates automáticos não compõem as barras de entradas e saídas. No Bradesco, a aplicação automática já faz parte do saldo do extrato. No BB, o saldo investido não foi informado.':'Esta consulta usa os valores de cada extrato, incluindo os movimentos automáticos da conta corrente.'} O resultado líquido representa movimentação de caixa; a classificação contábil exige os vínculos e a composição de cada lançamento.</p></details>`;
  }
  function selectionTools(s){return s.chartSelectionRange?`<span>Seleção: <b>${fullDate(s.chartSelectionRange.start)} — ${fullDate(s.chartSelectionRange.end)}</b></span><button class="btn" data-am-fit-selection="1">Ampliar seleção</button><button class="textbtn" data-am-clear-selection="1">Limpar seleção</button>`:'<span>Use Selecionar para marcar um intervalo e analisar os itens abaixo sem ampliar o gráfico.</span>';}
  function render(data,s){
    rows=chartDays(data,s.range,s.chartBasis);
    if(s.chartBar&&!chartBarTransactions(data,s.chartBar,s.chartBasis).length)s.chartBar=null;
    const selected=s.chartBar?.date||s.chartDay||activeRange(s).end,row=rows.find(x=>x.date===selected)||rows.at(-1),view=windowRange(s);
    const mode=CHART_MODES[s.chartMode]?s.chartMode:'zoom',hidden=s.chartHidden||[];
    return `<div class="bc-controls"><div class="ov-accounts">${a.scope('accounts').map(account=>`<label><input type="checkbox" data-ov-account="${esc(account.id)}" ${s.ids.includes(account.id)?'checked':''}>${esc(account.name)}</label>`).join('')}</div><div class="segments">${[['reported','Conta + aplicações'],['cash','Base do extrato']].map(([value,label])=>`<button data-ov-chart-basis="${value}" class="${s.chartBasis===value?'active':''}" aria-pressed="${s.chartBasis===value}">${label}</button>`).join('')}</div></div>${data.accounts.length?`
      <div class="am-legend" aria-label="Entradas, saídas e saldo">${[['incoming','am-in','Entradas / receitas'],['outgoing','am-out','Despesas / saídas'],['balance','am-balance','Saldo ao fundo'+(rows.some(r=>r.partial)?' · parcial':'')]].map(([group,key,label])=>`<button type="button" data-am-layer="${group}" aria-pressed="${!hidden.includes(group)}" title="Mostrar ou ocultar ${label}"><i class="am-key ${key}"></i>${label}</button>`).join('')}<label class="am-composition">Barras<select data-am-composition aria-label="Composição das barras"><option value="total" ${s.chartComposition!=='bank'?'selected':''}>Totais</option><option value="bank" ${s.chartComposition==='bank'?'selected':''}>Por banco</option></select></label></div>
      ${s.chartComposition==='bank'?`<div class="am-bank-legend">${financeSeries(data.accounts,'bank').filter(spec=>spec.bankIndex!==undefined).map(spec=>`<span><i style="background:#${spec.color.toString(16).padStart(6,'0')}"></i>${esc(spec.label)}</span>`).join('')}</div>`:''}
      <p class="am-note">Barras diárias: entradas acima de zero e saídas abaixo. ${s.chartComposition==='bank'?'Os segmentos de cada banco se somam em cada barra. ':''}O saldo acompanha os fechamentos disponíveis, em linha e área ao fundo. Passe sobre uma barra para ver valor e quantidade; clique para abrir seus lançamentos e vínculos. A legenda controla apenas as camadas visíveis.</p>
      <div class="am-toolbar"><div class="segments am-modes" role="group" aria-label="Interação com o gráfico">${Object.entries(CHART_MODES).map(([key,value])=>`<button data-am-mode="${key}" class="${mode===key?'active':''}" aria-pressed="${mode===key}">${value.label}</button>`).join('')}</div><div class="am-zoom-buttons" role="group" aria-label="Zoom e navegação"><button class="btn" data-am-navigate="back" aria-label="Mover intervalo para trás">${a.icon('back')}</button><button class="btn" data-am-navigate="out" aria-label="Reduzir zoom">−</button><button class="btn" data-am-navigate="in" aria-label="Ampliar zoom">+</button><button class="btn" data-am-navigate="forward" aria-label="Mover intervalo para frente">${a.icon('chevron')}</button><button class="btn" data-am-reset="1">Restaurar</button></div></div>
      <p class="am-interaction-hint" data-am-mode-hint role="status">${CHART_MODES[mode].hint}</p>
      <div class="am-stage"><div id="docflow-amchart" class="am-chart" aria-label="Evolução diária: entradas e saídas em barras, saldo em linha e área. Selecione ou amplie uma área; sliders controlam datas e valores."></div><p class="am-loading" data-am-loading role="status">Carregando o gráfico amCharts…</p></div>
      <div class="am-wheel-tools"><label><input type="checkbox" data-am-wheel ${s.chartWheel?'checked':''}>Zoom com a roda</label><span>Ctrl/⌘ + roda: ampliar · Shift + roda: mover · Dois dedos: zoom no celular</span><button class="textbtn" data-am-scale-reset="1">Restaurar escala de valores</button></div>
      <div class="am-range-tools"><div><strong data-am-range-label>${rangeLabel(s)}</strong><p>Alças: ajustar datas. Centro do slider: mover o intervalo. Controle lateral: ampliar valores.</p></div><div class="am-range-fields"><label>De<input type="date" data-am-range-start value="${view.start}" min="${s.range.start}" max="${s.range.end}" aria-label="Início do recorte do gráfico"></label><label>Até<input type="date" data-am-range-end value="${view.end}" min="${s.range.start}" max="${s.range.end}" aria-label="Fim do recorte do gráfico"></label><button class="btn" data-am-range-apply="1">Ampliar intervalo</button></div></div>
      <div class="am-selection-tools" data-am-selection-tools>${selectionTools(s)}</div>
      <div class="am-result" data-am-result>${result(s)}</div>
      <div class="am-readout" data-am-readout>${readout(row)}</div><section class="am-bar-detail" data-am-bar-detail aria-label="Lançamentos e correspondências da barra">${barDetails()}</section><div class="am-day-tools"><button class="btn" data-am-day-step="-1" aria-label="Dia anterior">${a.icon('back')}</button><label>Explorar dia<input type="date" data-am-day value="${selected}" min="${s.range.start}" max="${s.range.end}"></label><button class="btn" data-am-day-step="1" aria-label="Dia seguinte">${a.icon('chevron')}</button>${s.chartDay?'<button class="textbtn" data-ov-chart-back="1">Voltar ao intervalo do slider</button>':''}</div>${s.chartBasis==='reported'&&rows.every(r=>r.balance===null)?'<p class="ov-scope-note">Aplicações não informadas: falta o saldo investido para traçar o saldo total desta conta. Os lançamentos continuam disponíveis.</p>':''}`:'<p class="ov-empty">Escolha as contas para visualizar o gráfico.</p><button class="btn" data-ov-all="1">Selecionar todas</button>'}`;
  }
  function rangeLabel(s){const range=windowRange(s);return `Janela visível: ${fullDate(range.start)} — ${fullDate(range.end)}`;}
  async function mount(){
    const element=document.querySelector('#docflow-amchart');
    if(!element||typeof document.createElement!=='function')return;
    const generation=++epoch;
    try{
      const library=await loadAmCharts();
      if(generation!==epoch||!element.isConnected)return;
      const s=hooks.settings();
      runtime=createFinanceChart(element,{rows,range:s.range,zoomRange:s.chartDay?{start:s.chartDay,end:s.chartDay}:s.chartZoomRange,
        accounts:hooks.data().accounts,composition:s.chartComposition||'total',mode:s.chartMode||'zoom',hidden:s.chartHidden||[],wheelZoom:s.chartWheel,yRange:s.chartYRange,selectionRange:s.chartDay?null:s.chartSelectionRange,
        onZoom(range){hooks.zoom(range);sync();},onSelect(range){hooks.select(range);sync();},onScale(range){s.chartYRange=range;},
        onBar:showBar,
        onHover(row){if(s.chartBar)return;const box=document.querySelector('[data-am-readout]');if(box)box.innerHTML=readout(row);}
      },library);
      document.querySelector('[data-am-loading]')?.remove();
    }catch(error){
      if(generation!==epoch)return;
      runtime?.dispose();runtime=null;
      const message=document.querySelector('[data-am-loading]');
      if(message)message.innerHTML='O gráfico não carregou. Seus dados continuam disponíveis abaixo. <button class="btn" data-am-retry="1">Tentar novamente</button>';
      console.error('amCharts:',error);
    }
  }
  function sync(){
    const s=hooks.settings(),view=windowRange(s);
    const label=document.querySelector('[data-am-range-label]');if(label)label.textContent=rangeLabel(s);
    for(const [selector,html] of [['[data-am-bar-detail]',barDetails()],['[data-am-selection-tools]',selectionTools(s)],['[data-am-result]',result(s)],['[data-am-readout]',readout(rows.find(row=>row.date===activeRange(s).end))]]){const box=document.querySelector(selector);if(box)box.innerHTML=html;}
    for(const [selector,value] of [['[data-am-range-start]',view.start],['[data-am-range-end]',view.end]]){const input=document.querySelector(selector);if(input)input.value=value;}
    s.chartRangeDraft=null;
  }
  function navigate(range){hooks.zoom(range);runtime?.highlight(null);runtime?.zoom(range);sync();}
  function dispose(){epoch++;runtime?.dispose();runtime=null;}
  function selectDay(date){const s=hooks.settings();if(validDate(date)&&date>=s.range.start&&date<=s.range.end){s.chartBar=null;s.chartDay=date;hooks.refresh('[data-am-day]');}}
  function click(d){
    const s=hooks.settings();
    if(d.amBar){showBar({date:d.amBarDay,direction:d.amBar,account:null});return true;}
    if(d.amBarAll){if(s.chartBar)showBar({...s.chartBar,account:null});return true;}
    if(d.amBarClear){s.chartBar=null;const box=document.querySelector('[data-am-bar-detail]');if(box)box.innerHTML=barDetails();document.querySelector('[data-am-bar]')?.focus({preventScroll:true});return true;}
    if(d.amTransaction){const t=hooks.data().transactions.find(t=>t.id===d.amTransaction);if(t){const refs=chartMovementReferences(a.state,t,a.company);a.open(t.imported?'transaction':refs.obligation?'obligation':'day',t.imported?t.id:refs.obligation?.id||t.date);}return true;}
    if(d.amRetry){hooks.refresh();return true;}
    if(d.amMode&&CHART_MODES[d.amMode]){s.chartMode=d.amMode;runtime?.setMode(d.amMode);for(const button of document.querySelectorAll('[data-am-mode]')){const active=button.dataset.amMode===d.amMode;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}const hint=document.querySelector('[data-am-mode-hint]');if(hint)hint.textContent=CHART_MODES[d.amMode].hint;return true;}
    if(d.amLayer&&['balance','incoming','outgoing'].includes(d.amLayer)){const hidden=new Set(s.chartHidden||[]);if(hidden.has(d.amLayer))hidden.delete(d.amLayer);else if(hidden.size<2)hidden.add(d.amLayer);else{a.toast('Mantenha pelo menos uma camada visível.');return true;}s.chartHidden=[...hidden];const visible=!hidden.has(d.amLayer);runtime?.setVisible(d.amLayer,visible);document.querySelector(`[data-am-layer="${d.amLayer}"]`)?.setAttribute('aria-pressed',String(visible));return true;}
    if(d.amNavigate){const action={back:{shift:-.5},forward:{shift:.5},in:{factor:.5},out:{factor:2}}[d.amNavigate];if(action)navigate(navigateChartRange(windowRange(s),s.range,action));return true;}
    if(d.amRangeApply){const range=s.chartRangeDraft||windowRange(s);if(!validDate(range.start)||!validDate(range.end)||range.start>range.end||range.start<s.range.start||range.end>s.range.end){a.toast('Informe datas dentro do período carregado, com início anterior ou igual ao fim.');return true;}navigate({...range});return true;}
    if(d.amClearSelection){hooks.select(null);runtime?.highlight(null);sync();return true;}
    if(d.amFitSelection){if(s.chartSelectionRange)navigate({...s.chartSelectionRange});return true;}
    if(d.amScaleReset){s.chartYRange=null;runtime?.resetScale();return true;}
    if(d.ovChartBasis){s.chartBasis=d.ovChartBasis==='cash'?'cash':'reported';hooks.refresh();return true;}
    if(d.ovChartDay){selectDay(d.ovChartDay);return true;}
    if(d.ovChartBack){s.chartDay=null;hooks.refresh();return true;}
    if(d.amDayStep){selectDay(moveDate(s.chartDay||lastDate||s.range.start,Number(d.amDayStep)));return true;}
    if(d.amReset){s.chartZoomRange=null;s.chartSelectionRange=null;s.chartYRange=null;s.chartDay=null;runtime?.resetScale();navigate({...s.range});return true;}
    return false;
  }
  function change(e){
    const el=e.target,s=hooks.settings();
    if(el.hasAttribute('data-am-day')){selectDay(el.value);return true;}
    if(el.hasAttribute('data-am-composition')){if(['total','bank'].includes(el.value)){s.chartComposition=el.value;hooks.refresh('[data-am-composition]');}return true;}
    if(el.hasAttribute('data-am-wheel')){s.chartWheel=el.checked;runtime?.setWheelZoom(el.checked);return true;}
    if(el.hasAttribute('data-am-range-start')||el.hasAttribute('data-am-range-end')){s.chartRangeDraft??={...windowRange(s)};s.chartRangeDraft[el.hasAttribute('data-am-range-start')?'start':'end']=el.value;return true;}
    return false;
  }
  return {render,mount,dispose,click,change};
}
