import {financialPresentation,presentationHTML} from './record-presentation.js?v=34';
import {bankTone,flowDirection} from './visual-theme.js?v=34';
import {financialHierarchyHTML} from './financial-hierarchy-ui.js?v=34';
import {groupMovements} from './movement-group-model.js?v=29';

export function createMovementList(a,hooks){
  const {esc,money,fullDate,icon}=a;
  let visibleGroups=[];
  function record(t){
    const obligation=a.get('obligations',t.obligation),presentation=financialPresentation(a.state,'transaction',t,a.NOW);
    return `<button class="ov-record" data-flow="${flowDirection(t.amount)}" data-bank-tone="${bankTone(a.get('accounts',t.account))}" data-ov-transaction="${esc(t.id)}"><span class="ov-record-icon ${t.amount<0?'out':''}">${icon(t.amount<0?'out':'in')}</span><span><b class="record-title ${presentation.complete?'is-reconciled':''}">${esc(obligation?.party||t.description)}</b><small>${fullDate(t.date)} · ${esc(a.get('accounts',t.account)?.name)}${t.bankDocument?' · Doc. '+esc(t.bankDocument):''}</small>${presentationHTML(a,presentation,{compact:true})}</span><strong class="${t.amount<0?'outgoing':'incoming'}">${money(t.amount)}</strong></button>`;
  }
  function render(data,s){
    const tx=data.transactions.filter(t=>(!s.chartDay||t.date===s.chartDay)&&(s.tx==='all'||(s.tx==='in'?t.amount>0:t.amount<0)));
    const mode=s.movementGroup||'category',expanded=new Set(s.expandedGroups||[]),complete=new Set(s.completeGroups||[]);
    const controls=`<div class="ov-movement-controls"><div class="ov-subtabs segments">${[['all','Todos'],['in','Entradas'],['out','Saídas']].map(([key,label])=>`<button data-ov-tx="${key}" aria-pressed="${s.tx===key}" class="${s.tx===key?'active':''}">${label}</button>`).join('')}</div><label>Agrupar por<select data-ov-group-by aria-label="Agrupar movimentação por"><option value="type" ${mode==='type'?'selected':''}>Tipo de movimento</option><option value="category" ${mode==='category'?'selected':''}>Classificação</option><option value="none" ${mode==='none'?'selected':''}>Sem agrupamento</option></select></label></div>`;
    if(mode==='category')return controls+`<label class="fh-option"><input type="checkbox" data-ov-initial ${s.includeInitial!==false?'checked':''}> Incluir classificações iniciais (a revisar)</label>`+financialHierarchyHTML(a,tx,{includeInitial:s.includeInitial!==false});
    if(mode==='none')return controls+`<div class="ov-records">${tx.slice(0,s.all||s.chartDay?tx.length:8).map(record).join('')||'<p class="ov-empty">Nenhum lançamento para esta seleção.</p>'}</div>${!s.chartDay&&tx.length>8?`<button class="textbtn ov-more" data-ov-more="1">${s.all?'Mostrar menos':'Ver os '+tx.length+' lançamentos'}</button>`:''}`;
    visibleGroups=groupMovements(tx,a.state,mode);
    const allExpanded=visibleGroups.length&&visibleGroups.every(g=>expanded.has(g.key));
    return controls+`<p class="ov-group-note">${mode==='type'?'Tipos conforme o histórico bancário. Não definem a classificação contábil.':'Classificações iniciais identificadas como inicial, composições revisadas e categorias já informadas. Cada movimento aparece uma vez; consulte o resumo em Contabilidade para os valores divididos por classificação.'}</p><div class="ov-group-actions"><span>${visibleGroups.length} grupos · ${tx.length} lançamentos</span>${visibleGroups.length?`<button class="textbtn" data-ov-groups-all="${allExpanded?'close':'open'}">${allExpanded?'Recolher grupos':'Expandir grupos'}</button>`:''}</div><div class="ov-movement-groups" data-ov-groups>${visibleGroups.map((group,index)=>{
      const open=expanded.has(group.key),showAll=complete.has(group.key),id='movement-group-'+index;
      return `<section class="ov-movement-group"><button class="ov-group-heading" data-ov-group="${esc(group.key)}" aria-expanded="${open}" aria-controls="${id}"><span class="ov-group-name"><span class="ov-group-sign" aria-hidden="true">${open?'−':'+'}</span><b>${esc(group.label)}</b><small>${group.transactions.length} ${group.transactions.length===1?'lançamento':'lançamentos'}</small></span><span class="ov-group-figures"><span>Entradas<strong class="incoming">${money(group.incoming)}</strong></span><span>Saídas<strong class="outgoing">${money(-group.outgoing)}</strong></span><span>Diferença<strong>${money(group.net)}</strong></span></span></button><div id="${id}" ${open?'':'hidden'}>${open?`<div class="ov-group-records">${group.transactions.slice(0,showAll?undefined:8).map(record).join('')}</div>${group.transactions.length>8?`<button class="textbtn ov-more" data-ov-group-more="${esc(group.key)}">${showAll?'Mostrar menos':'Ver todos os '+group.transactions.length+' lançamentos'}</button>`:''}`:''}</div></section>`;
    }).join('')||'<p class="ov-empty">Nenhum lançamento para esta seleção.</p>'}</div>`;
  }
  function click(d){
    const s=hooks.settings();
    if(d.ovGroup){const set=new Set(s.expandedGroups||[]);set.has(d.ovGroup)?set.delete(d.ovGroup):set.add(d.ovGroup);s.expandedGroups=[...set];hooks.refresh(`[data-ov-group="${CSS.escape(d.ovGroup)}"]`);return true;}
    if(d.ovGroupMore){const set=new Set(s.completeGroups||[]);set.has(d.ovGroupMore)?set.delete(d.ovGroupMore):set.add(d.ovGroupMore);s.completeGroups=[...set];hooks.refresh(`[data-ov-group-more="${CSS.escape(d.ovGroupMore)}"]`);return true;}
    if(d.ovGroupsAll){const set=new Set(s.expandedGroups||[]);for(const g of visibleGroups)d.ovGroupsAll==='open'?set.add(g.key):set.delete(g.key);s.expandedGroups=[...set];hooks.refresh('[data-ov-groups-all]');return true;}
    return false;
  }
  function change(e){if(e.target.hasAttribute('data-ov-initial')){hooks.settings().includeInitial=e.target.checked;hooks.refresh('[data-ov-initial]');return true;}if(!e.target.hasAttribute('data-ov-group-by'))return false;if(['type','category','none'].includes(e.target.value))hooks.settings().movementGroup=e.target.value;hooks.refresh('[data-ov-group-by]');return true;}
  return {render,click,change};
}
