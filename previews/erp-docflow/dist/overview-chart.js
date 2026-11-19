import {dailySignedFlows,summarizeSignedFlows,signedScale} from './signed-flow-model.js?v=17';
import {reportedBankPositions} from './bank-position-model.js?v=17';
import {balancePointX} from './balance-events.js?v=17';
import {moveDate,validDate} from './range-model.js?v=17';
import {balanceSegments,balanceTrendPoints,TREND_COLORS} from './balance-trend-model.js?v=17';

// The period keeps actual dates. Only a focused day uses record order, never invented times.
export function balanceChartView(data,range,day){
  if(!day)return {points:data.points,width:910,day:null};
  const opening=[...data.points].reverse().find(p=>p.date<day)||data.points[0];
  const events=data.points.filter(p=>p.date===day&&p.transaction);
  const closing=data.points.findLast(p=>p.date===day&&!p.opening)||opening;
  const points=[{...opening,date:day,opening:true,transaction:undefined},...events,{...closing,date:day,opening:false,transaction:undefined}];
  return {points,width:Math.max(910,(points.length-1)*60+112),day};
}

export function createBalanceChart(a,hooks){
  const {esc,money,fullDate,icon}=a;
  const fills=['#699775','#7c99b6','#b6a269','#a282a5'];
  const strokes=['#38684d','#42688f','#79642e','#79577a'];
  let current,reported=[];
  const color=(id,palette=strokes)=>palette[Math.max(0,a.scope('accounts').findIndex(x=>x.id===id))%palette.length];
  const events=()=>current?.points.filter(p=>p.transaction)||[];

  function trendReadout(date){
    const points=current?.points||[],point=points.findLast(p=>!p.opening&&p.date<=date)||points[0];
    if(!point)return '';
    const index=points.indexOf(point),before=points[index-1],delta=before?point.total-before.total:null;
    const direction=delta>0?'up':delta<0?'down':'flat';
    return `<span class="bc-trend-date">${point.opening?'Abertura':'Saldo em '+fullDate(point.date)}${point.partial?' · parcial':''}</span><strong>${money(point.total)}</strong><span class="bc-trend-change" style="--trend-color:${TREND_COLORS[direction]}">${delta===null?'Primeira posição disponível':`${delta>0?'↑ Subiu':delta<0?'↓ Caiu':'= Sem variação'} ${money(Math.abs(delta))}<small>Desde ${before.opening?'a abertura':fullDate(before.date)}</small>`}</span><span class="bc-trend-banks">${hooks.data().accounts.map((account,i)=>`<span><i style="background:${color(account.id)}"></i>${esc(account.name)} <b>${money(point.balances[i])}</b></span>`).join('')}</span>`;
  }
  function showTrendDate(date){
    if(!current?.trend||current.day)return;
    const box=document.querySelector('[data-bc-trend-readout]');if(box)box.innerHTML=trendReadout(date);
    const index=current.points.findLastIndex(p=>!p.opening&&p.date<=date);if(index<0)return;
    const point=current.points[index],delta=index?point.total-current.points[index-1].total:0;
    const line=document.querySelector('[data-bc-hover-line]'),dot=document.querySelector('[data-bc-hover-dot]');
    const cx=current.geometry.x(index),cy=current.geometry.y(point.total);
    if(line){line.setAttribute('x1',cx);line.setAttribute('x2',cx);line.setAttribute('visibility','visible');}
    if(dot){dot.setAttribute('cx',cx);dot.setAttribute('cy',cy);dot.setAttribute('stroke',TREND_COLORS[delta>0?'up':delta<0?'down':'flat']);dot.setAttribute('visibility','visible');}
  }

  function detail(){
    const s=hooks.settings(),d=hooks.data(),list=events();
    const index=list.findIndex(p=>p.transaction.id===s.chartMovement),p=list[index];
    if(!p){
      const last=current?.points.at(-1)||d.points.at(-1);
      if(!current?.day&&s.chartBasis==='reported'&&!current?.reported)return `<div class="bc-balance"><span>Conta + aplicações</span><strong>Total não informado</strong></div><span class="bc-detail-note">Falta o saldo aplicado para compor a posição desse banco.</span>`;
      if(current?.reported)return `<div class="bc-balance"><span>${last.partial?'Total identificado · parcial':'Saldo identificado nos extratos'} · ${fullDate(last.date)}</span><strong>${money(last.total)}</strong></div><span class="bc-detail-note">${last.partial?'Falta o saldo aplicado de '+d.accounts.filter((account,i)=>!last.positions[i].complete).map(account=>esc(account.name)).join(', ')+'.':'Soma dos saldos informados no mesmo dia.'}</span>`;
      return `<div class="bc-balance"><span>Saldo dos extratos · fechamento de ${fullDate(last.date)}</span><strong>${money(last.total)}</strong></div><div class="bc-bank-values">${d.accounts.map((account,i)=>`<span><i style="background:${color(account.id)}"></i>${esc(account.name)} <b>${money(last.balances[i])}</b></span>`).join('')}</div>`;
    }
    const t=p.transaction,account=d.accounts.find(x=>x.id===t.account),ai=d.accounts.indexOf(account);
    return `<div class="bc-selected-value"><span>${t.amount<0?'Saída':'Entrada'} · ${esc(account.name)}</span><strong class="${t.amount<0?'bc-out':'bc-in'}">${t.amount>0?'+ ':''}${money(t.amount)}</strong><small>${fullDate(t.date)} · registro ${index+1} de ${list.length}</small></div><div class="bc-selected-description"><b>${esc(t.description)}</b><div class="bc-balance-equation"><span>Saldo do extrato antes <b>${money(p.balances[ai]-t.amount)}</b></span><span class="bc-equation-delta ${t.amount<0?'bc-out':'bc-in'}">${t.amount<0?'↓':'↑'} ${money(t.amount)}</span><span>Depois <b>${money(p.balances[ai])}</b></span></div>${t.movementType==='investment-transfer'?'<p class="bc-internal-note">Transferência entre conta e aplicação: altera a conta corrente, sem nova entrada ou saída do conjunto.</p>':''}<div class="bc-detail-actions"><button class="textbtn" data-ov-transaction="${esc(t.id)}">Abrir lançamento ${icon('chevron')}</button>${t.sourceDocument?`<button class="textbtn" data-statement-source="${esc(t.id)}">${icon('file')} ${t.sourceFormat==='ofx'?'Ver registro no OFX':'Ver página '+t.sourcePage+' do extrato'}</button>`:''}</div></div><div class="bc-step"><button data-ov-movement-step="-1" aria-label="Lançamento anterior" ${index===0?'disabled':''}>${icon('back')}</button><span>${index+1} / ${list.length}</span><button data-ov-movement-step="1" aria-label="Próximo lançamento" ${index===list.length-1?'disabled':''}>${icon('chevron')}</button></div>`;
  }

  function selectMovement(id){
    const p=events().find(p=>p.transaction.id===id);if(!p)return;
    hooks.settings().chartMovement=id;
    const box=document.querySelector('[data-bc-detail]');if(box)box.innerHTML=detail();
    document.querySelectorAll('[data-ov-chart-movement]').forEach(el=>{
      const selected=el.dataset.ovChartMovement===id;
      el.setAttribute('aria-pressed',String(selected));el.tabIndex=selected?0:-1;
    });
    const cursor=document.querySelector('[data-bc-cursor]'),index=current.points.indexOf(p);
    const arrow=document.querySelector('[data-bc-impact]');if(arrow)arrow.innerHTML=impact(index);
    if(cursor){const x=82+index/(current.points.length-1)*(current.width-112);cursor.setAttribute('x1',x);cursor.setAttribute('x2',x);}
  }

  function render(data,s){
    if(s.chartDay&&(s.chartDay<s.range.start||s.chartDay>s.range.end)){s.chartDay=null;s.chartMovement=null;}
    reported=reportedBankPositions(data,s.range);
    current=balanceChartView(data,s.range,s.chartDay);
    const wantsReported=s.chartBasis==='reported'&&!s.chartDay;
    const missingPosition=wantsReported&&!reported.length;
    if(wantsReported&&reported.length)current={points:reported,width:910,day:null,reported:true};
    const trend=s.chartStyle==='trend'&&!missingPosition;
    if(trend)current={...current,points:balanceTrendPoints(data,current),trend:true};
    const list=events();
    if(!list.some(p=>p.transaction.id===s.chartMovement))s.chartMovement=current.day?list[0]?.transaction.id:null;
    if(!data.accounts.length)return `<div class="ov-no-selection">${icon('wallet')}<strong>Escolha as contas para visualizar o caixa.</strong><button class="btn" data-ov-all="1">Selecionar todas</button></div>`;
    const {points,width:W,day}=current,H=420,top=28,bottom=348,right=W-30;
    const x=i=>day?82+i/(points.length-1)*(W-112):balancePointX(points[i],s.range);
    const excludeTransfers=wantsReported;
    const daily=dailySignedFlows(data,s.range,excludeTransfers),byDate=new Map(daily.map(p=>[p.date,p]));
    const dayTransactions=day?list.map(p=>p.transaction):data.transactions;
    const summary=summarizeSignedFlows(dayTransactions,excludeTransfers);
    const flow=day?points.map((p,i)=>({x:x(i),incoming:Math.max(0,p.transaction?.amount||0),outgoing:Math.min(0,p.transaction?.amount||0)})):[{x:82,incoming:0,outgoing:0},...daily.map(p=>({...p,x:balancePointX(p,s.range)}))];
    const showBackground=s.chartBackground!==false&&!missingPosition;
    const positive=points.map(()=>0),negative=points.map(()=>0);
    const layers=data.accounts.map((account,ai)=>{
      const base=[],edge=[];
      points.forEach((p,i)=>{const v=p.balances[ai],stack=v>=0?positive:negative;base.push(stack[i]);stack[i]+=v;edge.push(stack[i]);});
      return {account,base,edge,fill:color(account.id,fills),stroke:color(account.id)};
    });
    const projection=showBackground&&!current.reported&&s.projection&&points.some(p=>p.projected!==p.total);
    const values=[...(trend?points.map(p=>p.total):flow.flatMap(p=>[p.incoming,p.outgoing])),...(showBackground?[...positive,...negative]:[]),...(projection?points.map(p=>p.projected):[])];
    const {y,ticks}=signedScale(values,top,bottom);
    current.geometry={x,y,showBackground};
    const pts=values=>values.map((v,i)=>`${x(i).toFixed(2)},${y(v).toFixed(2)}`).join(' ');
    const flowPts=key=>flow.map(p=>`${p.x.toFixed(2)},${y(p[key]).toFixed(2)}`).join(' ');
    const compact=v=>new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(v/100);
    const dates=[...new Set(points.filter(p=>!p.opening).map(p=>p.date))];
    const labelDates=[...new Set([0,Math.round((dates.length-1)/4),Math.round((dates.length-1)/2),Math.round((dates.length-1)*.75),dates.length-1])].map(i=>dates[i]);
    const labels=day?points.map((p,i)=>({x:x(i),text:p.opening?'Abertura':p.transaction?String(i):'Fechamento',last:i===points.length-1})):labelDates.map(date=>({x:balancePointX({date},s.range),text:a.date(date)+(s.range.start.slice(0,4)!==s.range.end.slice(0,4)?'/'+date.slice(0,4):''),last:date===labelDates.at(-1)}));
    const markers=day?points.flatMap((p,i)=>p.transaction?[{p,i,x:x(i),y:y(trend?p.total:p.transaction.amount)}]:[]):data.points.filter(p=>p.transaction).map(p=>{
      const dailyValue=byDate.get(p.date),internal=excludeTransfers&&p.transaction.movementType==='investment-transfer';
      const closing=trend?points.findLast(point=>!point.opening&&point.date<=p.date):null;
      return {p,x:balancePointX(p,s.range),y:y(trend?(closing?.total??points[0].total):internal?0:p.transaction.amount<0?dailyValue.outgoing:dailyValue.incoming)};
    });
    const title=trend?'Evolução do saldo: subidas em verde e quedas em vermelho'+(day?' · '+fullDate(day):''):day?'Entradas e saídas de '+fullDate(day)+', com saldos ao fundo':current.reported?'Saldos informados por banco, com entradas positivas e saídas negativas':'Saldo bancário realizado e composição por conta, com entradas positivas e saídas negativas';
    const allDays=daily.filter(p=>p.count).map(p=>p.date);
    const balanceLabel=current.reported?current.points.some(p=>p.partial)?'Total identificado · parcial':'Saldo identificado':missingPosition?'Aplicações não informadas':'Saldo dos extratos';
    const legend=`<div class="bc-legend" aria-label="Contas incluídas no gráfico">${a.scope('accounts').map(account=>`<label><input type="checkbox" data-ov-account="${esc(account.id)}" ${s.ids.includes(account.id)?'checked':''}><i style="background:${color(account.id)}"></i>${esc(account.name)}</label>`).join('')}<span class="bc-total-key"><i></i>${balanceLabel}</span>${!current.reported&&!missingPosition&&data.obligations.length?`<label class="bc-projection"><input type="checkbox" data-ov-projection ${s.projection?'checked':''}>Com pendências</label>`:''}</div>`;
    const toolbar=day?`<div class="bc-focus-toolbar"><button class="btn" data-ov-chart-back="1">${icon('back')} Voltar ao período</button><div class="bc-day-navigation"><button data-ov-day-step="-1" aria-label="Dia anterior" ${day===s.range.start?'disabled':''}>${icon('back')}</button><label><span>Dia em detalhe</span><input type="date" data-ov-chart-date value="${day}" min="${s.range.start}" max="${s.range.end}" aria-label="Dia em detalhe no gráfico"></label><button data-ov-day-step="1" aria-label="Dia seguinte" ${day===s.range.end?'disabled':''}>${icon('chevron')}</button></div><span>${list.length} lançamento${list.length===1?'':'s'}</span></div>`:`<div class="bc-period-heading"><span>${fullDate(s.range.start)} — ${fullDate(s.range.end)}</span><b>${data.transactions.length} lançamentos · ${allDays.length} dias com movimento</b></div>`;
    const dateBands=day?'':`<div class="bc-date-targets" style="left:${82/W*100}%;right:${30/W*100}%;top:${top/H*100}%;bottom:${(H-bottom)/H*100}%">${daily.map((p,i)=>{
      const center=(balancePointX(p,s.range)-82)/798*100,previous=i?(balancePointX(daily[i-1],s.range)-82)/798*100:0,next=i<daily.length-1?(balancePointX(daily[i+1],s.range)-82)/798*100:100;
      const left=i?(previous+center)/2:0,end=i<daily.length-1?(center+next)/2:100;
      return `<button data-ov-chart-day="${p.date}" data-bc-trend-date="${p.date}" style="left:${left}%;width:${end-left}%" tabindex="${trend&&i===0?0:-1}" aria-label="${trend?'Consultar saldo e lançamentos de '+fullDate(p.date):'Ver '+fullDate(p.date)+', '+p.count+' lançamentos, movimento líquido '+money(p.net)}" title="${trend?'Consultar saldo e lançamentos de '+fullDate(p.date):fullDate(p.date)+' · entradas '+money(p.incoming)+' / saídas '+money(p.outgoing)+' · clique para ampliar'}"></button>`;
    }).join('')}</div>`;
    current.hoverDates=daily.map(p=>p.date);
    const selected=points.findIndex(p=>p.transaction?.id===s.chartMovement);
    const basis=a.state.dataset?`<div class="bc-basis segments" aria-label="Base dos saldos">${[['reported','Saldo + aplicações informadas'],['cash','Movimentos do extrato']].map(([key,label])=>`<button data-ov-chart-basis="${key}" aria-pressed="${(s.chartDay?'cash':s.chartBasis)===key}" class="${(s.chartDay?'cash':s.chartBasis)===key?'active':''}">${label}</button>`).join('')}</div>`:'';
    const positions=positionCards(data,s);
    const background=showBackground?`<g data-bank-background>${layers.map(l=>`<polygon data-bank-area="${esc(l.account.id)}" points="${pts(l.edge)} ${l.base.map((v,i)=>`${x(i)},${y(v)}`).reverse().join(' ')}" fill="${l.fill}" fill-opacity=".16"/><polyline points="${pts(l.edge)}" fill="none" stroke="${l.stroke}" stroke-opacity=".35" stroke-width="1.2"/>`).join('')}<polyline points="${pts(points.map(p=>p.total))}" fill="none" stroke="#526c59" stroke-opacity=".65" stroke-width="1.5"/>${projection?`<polyline points="${pts(points.map(p=>p.projected))}" fill="none" stroke="#936f32" stroke-width="1.5" stroke-dasharray="6 4"/>`:''}</g>`:'';
    const flowForeground=[['incoming','#247d52'],['outgoing','#bd5144']].map(([key,stroke])=>`<polygon points="${flow[0].x},${y(0)} ${flowPts(key)} ${flow.at(-1).x},${y(0)}" fill="${stroke}" fill-opacity=".045"/><polyline data-signed-flow="${key}" points="${flowPts(key)}" fill="none" stroke="${stroke}" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>${day?'':flow.filter(p=>p[key]).map(p=>`<circle cx="${p.x}" cy="${y(p[key])}" r="4.5" fill="white" stroke="${stroke}" stroke-width="2"/>`).join('')}`).join('');
    const styleControl=`<div class="bc-style-control"><span>Leitura do gráfico</span><div class="segments" aria-label="Leitura do gráfico">${[['trend','Subidas e quedas'],['flows','Entradas e saídas']].map(([mode,label])=>`<button data-bc-style="${mode}" aria-pressed="${mode===(trend?'trend':'flows')}" class="${mode===(trend?'trend':'flows')?'active':''}" ${mode==='trend'&&missingPosition?'disabled title="Falta o saldo de aplicações; selecione Movimentos do extrato para ver a conta corrente"':''}>${label}</button>`).join('')}</div></div>`;
    const foreground=trend?`<g data-balance-trend>${balanceSegments(points).map(segment=>`<path data-balance-segment="${segment.direction}" data-balance-delta="${segment.delta}" d="M${x(segment.from)} ${y(segment.previous.total)}L${x(segment.to)} ${y(segment.point.total)}" fill="none" stroke="${segment.color}" stroke-width="3.2" stroke-linecap="round" ${segment.direction==='flat'?'stroke-dasharray="3 4"':''}><title>${fullDate(segment.point.date)} · saldo ${money(segment.point.total)} · ${segment.delta>0?'subiu':segment.delta<0?'caiu':'sem variação'} ${money(Math.abs(segment.delta))}</title></path>`).join('')}${points.length===1?`<circle cx="${x(0)}" cy="${y(points[0].total)}" r="4" fill="#677b70"/>`:''}</g>`:flowForeground;
    const key=`<div class="bc-flow-legend">${trend?'<span class="bc-flow-in">↑ Saldo subiu</span><span class="bc-flow-out">↓ Saldo caiu</span><span class="bc-trend-flat">= Sem variação</span>':`<span class="bc-flow-in">＋ Entradas ${day?'por lançamento':'por dia'}</span><span class="bc-flow-out">− Saídas ${day?'por lançamento':'por dia'}</span>`}<label><input type="checkbox" data-bc-background ${s.chartBackground!==false?'checked':''}> Saldos dos bancos ao fundo</label></div>`;
    const scope=trend?'A cor compara o saldo com a posição anterior. Passe sobre uma data para conferir o valor; selecione o dia para abrir os lançamentos.':excludeTransfers?'Aplicações e resgates automáticos ficam fora das linhas de entradas e saídas.':day?'Detalhe do extrato: o Bradesco já incorpora a aplicação automática; no BB, os resgates alteram a conta corrente.':'Movimentos conforme cada extrato, incluindo as transferências internas informadas.';
    const totals=`<div class="bc-flow-summary" aria-label="Movimento ${day?'do dia':'do período'}"><div><span>Entradas ${day?'do dia':'do período'}</span><strong class="bc-in">+ ${money(summary.incoming)}</strong></div><div><span>Saídas ${day?'do dia':'do período'}</span><strong class="bc-out">${money(summary.outgoing)}</strong></div><div><span>Movimento líquido</span><strong class="${summary.net<0?'bc-out':'bc-in'}">${summary.net>0?'+ ':''}${money(summary.net)}</strong></div></div>`;
    const caption=trend?(day?'Cada ponto mostra o saldo após um lançamento. A cor indica a subida ou queda; a seta mostra seu efeito. Ordem dos registros por banco; horários não informados.':'A linha liga os saldos de fechamento informados: verde quando sobe, vermelho quando cai, tracejado quando não varia. As áreas ao fundo distinguem os bancos. Variação de saldo não é apuração de lucro ou prejuízo.'):day?'Linhas: valor de cada lançamento. Fundo: saldo do extrato após o lançamento. A seta indica seu efeito no saldo. Ordem dos registros por banco; horários não informados.':'Linhas: entradas acima de zero e saídas abaixo de zero, somadas por dia. Fundo: saldos observados dos bancos. Escolha um dia para ver cada lançamento e seu efeito no saldo.';
    return `<div class="bc-options">${legend}${basis}</div>${toolbar}${styleControl}${key}<p class="bc-flow-scope">${scope}</p>${trend&&!day?`<div class="bc-trend-readout" data-bc-trend-readout role="status" aria-live="polite">${trendReadout(points.at(-1).date)}</div>`:''}<div class="bc-scroll" role="region" aria-label="Entradas, saídas e saldos; role horizontalmente quando necessário" tabindex="0"><div class="bc-canvas" style="--chart-min:${Math.max(700,W*.8)}px"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${title}"><title>${title}</title><desc>${caption} ${current.reported?'A posição inclui apenas aplicações informadas; o total permanece parcial quando faltam saldos.':''}</desc><rect x="82" y="${y(0)}" width="${W-112}" height="${bottom-y(0)}" fill="#fbf6f3"/>${ticks.map(v=>`<path d="M82 ${y(v)}H${right}" class="bc-grid"/><text x="70" y="${y(v)+4}" text-anchor="end" class="bc-axis ${v===0?'bc-zero-label':''}">${v===0?'R$ 0':'R$ '+compact(v)}</text>`).join('')}${background}${foreground}${trend&&!day?`<line data-bc-hover-line x1="82" x2="82" y1="${top}" y2="${bottom}" visibility="hidden" stroke="#607469" stroke-dasharray="3 4"/><circle data-bc-hover-dot r="5" fill="white" stroke-width="2.5" visibility="hidden"/>`:''}<path data-zero-line d="M82 ${y(0)}H${right}" stroke="#778d7e" stroke-width="1.5" stroke-dasharray="5 3"/>${day?`<line data-bc-cursor x1="${x(Math.max(0,selected))}" x2="${x(Math.max(0,selected))}" y1="${top}" y2="${bottom}" stroke="#667c6c" stroke-dasharray="3 4"/><g data-bc-impact>${impact(selected)}</g>`:markers.map(({p,x,y})=>`<circle data-movement-id="${esc(p.transaction.id)}" cx="${x}" cy="${y}" r="2" fill="${excludeTransfers&&p.transaction.movementType==='investment-transfer'?'#87958c':color(p.transaction.account)}"/>`).join('')}${labels.map(l=>`<text x="${l.x}" y="390" text-anchor="${l.last?'end':'middle'}" class="bc-axis">${l.text}</text>`).join('')}</svg>${dateBands}${day?`<div class="bc-markers">${markers.map(({p,i,x,y})=>`<button class="bc-marker" data-ov-chart-movement="${esc(p.transaction.id)}" style="left:${x/W*100}%;top:${y/H*100}%;--bank-color:${color(p.transaction.account)};--movement-color:${p.transaction.movementType==='investment-transfer'?'#68796f':p.transaction.amount<0?'#a94639':'#247d52'}" aria-pressed="${s.chartMovement===p.transaction.id}" tabindex="${s.chartMovement===p.transaction.id?0:-1}" aria-label="Registro ${i}: ${esc(p.transaction.description)}, ${esc(a.get('accounts',p.transaction.account)?.name)}, ${money(p.transaction.amount)}" title="${esc(p.transaction.description)} · ${money(p.transaction.amount)}">${p.transaction.amount<0?'−':'+'}</button>`).join('')}</div>`:''}</div></div><p class="bc-caption">${caption}</p>${totals}${day?'':`<div class="bc-day-strip" aria-label="Dias com lançamentos"><span>Explorar<br>por dia</span><div class="bc-day-list">${allDays.map(date=>{const p=byDate.get(date);return `<button data-ov-chart-day="${date}" data-bc-trend-date="${date}" aria-label="${fullDate(date)}: ${p.count} lançamentos; movimento líquido ${money(p.net)}"><b>${a.date(date)}</b><strong class="${p.net<0?'bc-out':'bc-in'}">${p.net>0?'+ ':''}${money(p.net)}</strong><span>${p.count} ${p.count===1?'lançamento':'lançamentos'}</span></button>`;}).join('')||'<p>Nenhum lançamento neste período.</p>'}</div></div>`}<div class="bc-detail ${day&&list.length?'bc-has-selection':''}" data-bc-detail role="status" aria-live="polite" aria-atomic="true">${detail()}</div>${positions}${missingPosition?'<p class="bc-missing">O saldo das aplicações não consta neste período. As linhas de movimento continuam disponíveis; a área de saldo consolidado fica pendente.</p>':''}${day&&!list.length?'<p class="bc-caption">Nenhum lançamento neste dia. O gráfico mantém o saldo disponível no extrato.</p>':''}${summary.internalCount?`<p class="bc-source-note">${summary.internalCount} aplicações/resgates preservados nos lançamentos. Na visão Saldo + aplicações informadas, são transferências internas, sem nova entrada ou saída do conjunto. Rendimentos e saldos de aplicações ausentes não são estimados.</p>`:''}`;
  }

  function impact(index){
    if(!current?.day||(!current.geometry?.showBackground&&!current.trend)||index<1||!current.points[index]?.transaction)return '';
    const {x,y}=current.geometry,p=current.points[index],before=current.points[index-1].total,after=p.total;
    const cx=x(index),start=y(before),end=y(after),stroke=p.transaction.amount<0?'#bd5144':'#247d52',direction=end<start?1:-1;
    return `<path data-impact-before="${before}" data-impact-after="${after}" d="M${cx} ${start}V${end}M${cx-5} ${end+direction*7}L${cx} ${end}L${cx+5} ${end+direction*7}" fill="none" stroke="${stroke}" stroke-width="2.5"/><circle cx="${cx}" cy="${start}" r="3.5" fill="white" stroke="${stroke}" stroke-width="1.8"/>`;
  }

  function positionCards(data,s){
    if(!a.state.dataset)return '';
    const cutoff=s.chartDay||s.range.end,last=reported.findLast(p=>p.date<=cutoff);
    const day=last?.date||cutoff;
    const cash=data.points.findLast(p=>!p.opening&&!p.transaction&&p.date<=day)||data.points[0];
    return `<div class="bc-position-heading"><span>Posição informada · ${fullDate(day)}</span>${last&&last.partial?'<b>Aplicações incompletas</b>':''}</div><div class="bc-positions">${data.accounts.map((account,i)=>{
      const position=last?.positions[i],investment=position?.investment??null;
      const cashAmount=position?.cash??cash.balances[i];
      if(account.statement?.balanceBasis==='consolidated')return `<div class="bc-position" style="--bank-color:${color(account.id)}"><h3>${esc(account.name)}</h3><strong>${money(position?.identified??cashAmount)}</strong><p>Saldo do extrato, com aplicação automática incorporada. O Invest Fácil não é somado novamente; outras aplicações ficam no resumo da emissão.</p><button class="textbtn" data-ov-position-source="${esc(account.id)}" data-source-document="${esc(position?.sourceDocument||account.statement.document)}" data-source-page="${position?.sourcePage||1}">Conferir saldo no extrato ${icon('chevron')}</button></div>`;
      return `<div class="bc-position" style="--bank-color:${color(account.id)}"><h3>${esc(account.name)}</h3><strong>${investment===null?'Total não informado':money(cashAmount+investment)}</strong><dl><div><dt>Conta corrente</dt><dd>${money(cashAmount)}</dd></div><div><dt>Aplicações</dt><dd>${investment===null?'<span class="bc-unknown">Saldo não informado</span>':money(investment)}</dd></div></dl>${investment===null?'<p>É necessário o extrato de investimentos para completar este banco.</p>':`<button class="textbtn" data-ov-position-source="${esc(account.id)}" data-source-document="${esc(position.sourceDocument||account.statement.document)}" data-source-page="${position.sourcePage}">Conferir saldo no extrato ${icon('chevron')}</button>`}</div>`;
    }).join('')}</div>`;
  }

  function chooseDay(date,focus){
    const s=hooks.settings();
    if(!validDate(date)||date<s.range.start||date>s.range.end){a.toast('Escolha um dia dentro do período exibido.');hooks.refresh('[data-ov-chart-date]');return;}
    s.chartDay=date;s.chartMovement=null;hooks.refresh(focus||'[data-ov-chart-back]');
  }
  function click(d){
    if(d.bcStyle){if(['trend','flows'].includes(d.bcStyle))hooks.settings().chartStyle=d.bcStyle;hooks.refresh(`[data-bc-style="${d.bcStyle}"]`);return true;}
    if(d.ovChartBasis){const s=hooks.settings();s.chartBasis=d.ovChartBasis;s.chartDay=null;s.chartMovement=null;hooks.refresh(`[data-ov-chart-basis="${d.ovChartBasis}"]`);return true;}
    if(d.ovPositionSource){const account=hooks.data().accounts.find(x=>x.id===d.ovPositionSource);if(account?.statement){a.open('document',d.sourceDocument||account.statement.document);a.current.page=Number(d.sourcePage)-1;a.draw();}return true;}
    if(d.ovChartDay){chooseDay(d.ovChartDay);return true;}
    if(d.ovChartBack){const s=hooks.settings(),day=s.chartDay;s.chartDay=null;s.chartMovement=null;hooks.refresh(`.bc-day-list [data-ov-chart-day="${day}"]`);return true;}
    if(d.ovDayStep){chooseDay(moveDate(hooks.settings().chartDay,Number(d.ovDayStep)),`[data-ov-day-step="${d.ovDayStep}"]`);return true;}
    if(d.ovChartMovement){selectMovement(d.ovChartMovement);return true;}
    if(d.ovMovementStep){const list=events(),index=list.findIndex(p=>p.transaction.id===hooks.settings().chartMovement),next=list[index+Number(d.ovMovementStep)];if(next){selectMovement(next.transaction.id);focusMovement(next.transaction.id);}return true;}
    return false;
  }
  function change(e){if(e.target.hasAttribute('data-bc-background')){hooks.settings().chartBackground=e.target.checked;hooks.refresh('[data-bc-background]');return true;}if(!e.target.hasAttribute('data-ov-chart-date'))return false;chooseDay(e.target.value,'[data-ov-chart-date]');return true;}
  function focusMovement(id){const el=document.querySelector(`[data-ov-chart-movement="${CSS.escape(id)}"]`);el?.focus({preventScroll:true});el?.scrollIntoView({block:'nearest',inline:'nearest'});}
  document.addEventListener('focusin',e=>{if(e.target.hasAttribute('data-ov-chart-movement'))selectMovement(e.target.dataset.ovChartMovement);});
  for(const event of ['pointerover','focusin'])document.addEventListener(event,e=>{const target=e.target.closest?.('[data-bc-trend-date]');if(target)showTrendDate(target.dataset.bcTrendDate);});
  document.addEventListener('keydown',e=>{
    if(current?.trend&&!current.day&&e.target.hasAttribute('data-bc-trend-date')&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){
      e.preventDefault();const dates=current.hoverDates,index=dates.indexOf(e.target.dataset.bcTrendDate),next=e.key==='Home'?0:e.key==='End'?dates.length-1:Math.max(0,Math.min(dates.length-1,index+(e.key==='ArrowLeft'?-1:1))),date=dates[next];
      const target=document.querySelector(`.bc-date-targets [data-bc-trend-date="${date}"]`);if(target){e.target.tabIndex=-1;target.tabIndex=0;target.focus({preventScroll:true});}showTrendDate(date);return;
    }
    if(!e.target.hasAttribute('data-ov-chart-movement')||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
    e.preventDefault();const list=events(),index=list.findIndex(p=>p.transaction.id===e.target.dataset.ovChartMovement);
    const next=e.key==='Home'?0:e.key==='End'?list.length-1:Math.max(0,Math.min(list.length-1,index+(e.key==='ArrowLeft'?-1:1)));
    if(list[next]){selectMovement(list[next].transaction.id);focusMovement(list[next].transaction.id);}
  });
  return {render,click,change};
}
