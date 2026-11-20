import {financialHierarchyHTML} from './financial-hierarchy-ui.js?v=34';
import {INDEXADOR_SOURCE} from './classification-reference.js?v=28';
import {PURPOSES,classificationCatalog,classificationTransaction,getClassification,classificationStatus,classificationSummary,centsInput,saveClassification,saveCategory} from './classification-model.js?v=29';
import {INITIAL_BATCH,initialDecision,initialBatchSummary} from './classification-initial.js?v=29';
import {createAccountingPlan} from './accounting-plan-ui.js?v=29';
import {resolveAccountingMapping} from './accounting-plan-model.js?v=29';
import {statementOrder} from './statement-model.js?v=17';

export function createClassification(a,legacy){
  const {esc,money,fullDate,btn,pill}=a;
  let tab='entries',filter='all',bank='all',query='',listPage=0,lastCompany='',period='month',includeInitial=true;
  const plan=createAccountingPlan(a);
  const states={unclassified:'A classificar',initial:'Classificação inicial',draft:'Rascunho',reviewed:'Composição revisada'};
  const catalog=()=>classificationCatalog(a.state,a.company);
  const record=t=>getClassification(a.state,a.company,t.id);
  const status=t=>classificationStatus(a.state,a.company,t);
  const options=(rows,value,blank='Ainda não informado')=>'<option value="">'+blank+'</option>'+rows.map(x=>'<option value="'+esc(x.id)+'" '+(x.id===value?'selected':'')+'>'+esc(x.name||x.title||x.label)+'</option>').join('');
  const select=(label,name,rows,value)=>'<label>'+label+'<select name="'+name+'">'+options(rows,value)+'</select></label>';
  const input=(label,name,value='',type='text')=>'<label>'+label+'<input name="'+name+'" type="'+type+'" value="'+esc(value)+'" '+(type==='text'?'maxlength="300"':'')+'></label>';
  const badge=t=>pill(states[status(t)],status(t)==='reviewed'?'green':'amber');
  const categoryLabel=id=>catalog().find(c=>c.id===id)?.label||'A classificar';
  const labelCompany=id=>a.state.companies.find(c=>c.id===id)?.name||'Empresa indisponível';
  const refName=(collection,id)=>a.state[collection].find(x=>x.id===id)?.name||a.state[collection].find(x=>x.id===id)?.title||'';
  const scoped=(collection,company)=>a.state[collection].filter(x=>x.company===company);
  function rows(){
    if(lastCompany!==a.company){lastCompany=a.company;bank='all';listPage=0;query='';}
    const ids=new Set(a.scope('accounts').filter(b=>bank==='all'||b.id===bank).map(b=>b.id));
    return a.state.transactions.filter(t=>ids.has(t.account)&&(period==='all'||t.date.startsWith(a.month))).sort(statementOrder);
  }
  function composition(t){
    const r=record(t);
    return r?r.lines.map(l=>esc(categoryLabel(l.category))+' · '+money(l.amount)).join('<br>'):'<span class="muted">Definir classificação e contexto</span>';
  }
  function evidence(t){
    const d=initialDecision(t),r=record(t),source=r?.provenance;
    if(!d&&!source)return '';
    const rule=d||INITIAL_BATCH.rules[source.rule];
    if(!rule)return '';
    const confidence={supported:'Correspondência bem sustentada',probable:'Correspondência provável',pending:'Contexto insuficiente'}[rule.confidence];
    return '<details class="classification-evidence" '+(!r?'open':'')+'><summary>'+esc(confidence)+(r?.provenance?' · fundamento inicial':' · motivo da pendência')+'</summary><p>'+esc(rule.reason)+'</p><p><b>Conferir:</b> '+esc(rule.review)+'</p>'+(rule.candidates.length?'<p>Possibilidades a verificar: '+rule.candidates.map(id=>esc(categoryLabel(id))).join(' · ')+'</p>':'')+(rule.evidence.length?'<p>Referência: '+esc(INITIAL_BATCH.source.source)+' · '+esc(INITIAL_BATCH.source.sheet)+'. O arquivo contém registros de 2018 a 2020.</p><ul>'+rule.evidence.map(e=>'<li>Linha '+e.row+' · '+esc(e.history)+' → '+esc(e.category)+' · '+money(e.amount)+'</li>').join('')+'</ul>':'<p>Referência: descrição do extrato e categorias do Indexador. Sem contraparte histórica equivalente.</p>')+'</details>';
  }
  function summaryCard(t){
    const r=record(t);
    const refs=(r?.lines||[]).map(l=>'<div class="classification-ref"><b>'+esc(categoryLabel(l.category))+' · '+money(l.amount)+'</b><p>'+esc([PURPOSES[l.purpose],labelCompany(l.belongsTo),l.competence,l.costCenter,l.parcel].filter(Boolean).join(' · '))+'</p>'+[['assets','asset',l.asset],['contracts','contract',l.contract],['obligations','obligation',l.obligation],...l.documents.map(id=>['documents','document',id])].filter(([, ,id])=>id).map(([collection,kind,id])=>a.link(refName(collection,id),kind,id)).join('')+(l.note?'<p>'+esc(l.note)+'</p>':'')+'</div>').join('');
    return '<section class="drawer-section classification-context"><h3>Classificação e composição</h3>'+badge(t)+evidence(t)+(r?refs:'<p>Definir classificação e contexto.</p>')+btn(record(t)?'Revisar composição':'Classificar lançamento','data-open="classify" data-id="'+esc(t.id)+'"','primary')+'<p class="annotation">Classificação gerencial, conciliação e conferência documental são controles separados.</p></section>';
  }
  function indexador(){
    const cats=catalog(),groups=[...new Set(cats.map(c=>c.group))];
    return '<section class="panel classification-index"><div class="panel-head"><div><h2>Indexador da empresa</h2><p>Grupo e classificação do fluxo, com correspondência contábil revisável.</p></div>'+btn('Nova classificação','data-open="classification-category"','primary','plus')+'</div><div class="classification-explainer"><p>Referência: '+esc(INDEXADOR_SOURCE.file)+' · classificações editáveis, sem dados da planilha privada.</p><p>O catálogo é uma referência inicial revisável. Use a aba Plano do contador para importar as contas reais e definir correspondências por natureza. Referências manuais anteriores, se houver, ficam preservadas abaixo.</p></div>'+groups.map(group=>'<details class="classification-group" '+(group==='CAIXA'?'open':'')+'><summary>'+esc(group)+' <span>'+cats.filter(c=>c.group===group).length+' classificações</span></summary><div class="table-wrap"><table><thead><tr><th>Classificação do fluxo</th><th>Referência do modelo<br><small>Realizado / em aberto</small></th><th>Referência manual anterior</th><th></th></tr></thead><tbody>'+cats.filter(c=>c.group===group).map(c=>'<tr><td><strong>'+esc(c.label)+'</strong><small>'+(c.source?esc(c.source.sheet):'Criada nesta aplicação')+(c.active?'':' · Inativa')+'</small></td><td>'+esc(c.source?.realized||'Não informada')+'<small>'+esc(c.source?.pending||'Não informada')+'</small></td><td>'+esc([c.accountCode,c.accountLabel].filter(Boolean).join(' · ')||'Nenhuma')+'<small>Plano atual: use a aba Plano do contador</small><small>'+(c.mappingReviewed?'Referência manual registrada':'')+'</small></td><td>'+btn('Editar','data-open="classification-category" data-id="'+esc(c.id)+'"')+'</td></tr>').join('')+'</tbody></table></div></details>').join('')+'</section>';
  }
  function totals(transactions){
    return '<section class="panel"><div class="panel-head"><div><h2>Resumo das classificações</h2><p>Entradas / Saídas · Classificação · Lançamentos. Cada parcela contribui somente com seu próprio valor.</p></div></div><label class="fh-option"><input type="checkbox" data-classification-initial-summary '+(includeInitial?'checked':'')+'> Incluir classificações iniciais, ainda sujeitas a revisão</label>'+financialHierarchyHTML(a,transactions,{includeInitial})+'</section>';
  }
  function page(){
    const tx=rows(),matched=tx.filter(t=>(filter==='all'||status(t)===filter)&&(!query||[t.description,record(t)?.party,record(t)?.complement,...(record(t)?.lines||[]).map(l=>categoryLabel(l.category))].join(' ').toLocaleLowerCase('pt-BR').includes(query.toLocaleLowerCase('pt-BR'))));
    listPage=Math.min(listPage,Math.max(0,Math.ceil(matched.length/30)-1));
    const tabs='<div class="classification-tabs" role="group" aria-label="Área de classificação">'+[['entries','Classificar'],['catalog','Indexador'],['plan','Plano do contador'],['summary','Resumo por classificação'],['legacy','Obrigações e documentos']].map(([key,label])=>'<button data-classification-tab="'+key+'" class="'+(tab===key?'active':'')+'" aria-pressed="'+(tab===key)+'">'+label+'</button>').join('')+'</div>';
    if(tab==='legacy')return tabs+legacy();
    const header=a.titleBlock('Classificação e contexto','Do lançamento bancário à composição que explica o movimento.',['catalog','plan'].includes(tab)?'':a.monthSelect()+btn('Exportar classificação CSV','data-classification-export="1"','','download'),'Contabilidade');
    if(tab==='catalog')return header+tabs+indexador();
    if(tab==='plan')return header+tabs+plan.page();
    const controls='<div class="classification-filters"><label>Período<select data-classification-period><option value="month" '+(period==='month'?'selected':'')+'>Mês selecionado</option><option value="all" '+(period==='all'?'selected':'')+'>Todo o histórico importado</option></select></label><label>Conta<select data-classification-bank><option value="all">Todas as contas</option>'+a.scope('accounts').map(b=>'<option value="'+esc(b.id)+'" '+(bank===b.id?'selected':'')+'>'+esc(b.name)+'</option>').join('')+'</select></label>'+(tab==='entries'?'<label>Situação<select data-classification-filter><option value="all">Todas</option>'+Object.entries(states).map(([k,v])=>'<option value="'+k+'" '+(filter===k?'selected':'')+'>'+v+'</option>').join('')+'</select></label><label class="classification-search">Buscar histórico ou classificação<input type="search" data-classification-query value="'+esc(query)+'" placeholder="Digite e pressione Enter"></label>':'')+'</div>';
    if(tab==='summary')return header+tabs+controls+totals(tx);
    const batch=initialBatchSummary(a.state,a.company);
    const batchNotice=batch.total?'<div class="classification-batch"><div><b>Livro Caixa aplicado ao histórico de 2026</b><p>'+batch.initial+' classificações iniciais · '+batch.pending+' pendentes · '+batch.edited+' composições já editadas. Total: '+batch.total+' movimentos.</p><p>Os valores bancários foram preservados. Revise competências, rateios, contratos e documentos antes de concluir a composição.</p></div>'+btn('Ver todo o histórico','data-classification-all-history="1"')+'</div>':'';
    return header+tabs+batchNotice+'<div class="classification-stats">'+Object.entries(states).map(([key,label])=>'<button data-classification-filter-button="'+key+'" aria-pressed="'+(filter===key)+'"><strong>'+tx.filter(t=>status(t)===key).length+'</strong><span>'+label+'</span></button>').join('')+'</div><p class="classification-help">Escolha um movimento para informar o que ele representa e a quem pertence. Divida em itens quando houver aluguel, rateio, parcelas ou destinos diferentes.</p><section class="panel">'+controls+'<div class="table-wrap"><table class="classification-table"><thead><tr><th>Data / banco</th><th>Histórico / complemento</th><th>Classificação e composição</th><th>Valor do extrato</th><th>Situação</th><th></th></tr></thead><tbody>'+matched.slice(listPage*30,(listPage+1)*30).map(t=>'<tr><td>'+fullDate(t.date)+'<small>'+esc(a.get('accounts',t.account)?.name)+'</small></td><td><button class="textbtn" data-open="transaction" data-id="'+esc(t.id)+'">'+esc(t.description)+'</button><small>'+esc(record(t)?.complement||initialDecision(t)?.reason||'')+'</small></td><td>'+composition(t)+'</td><td class="money '+(t.amount<0?'outgoing':'incoming')+'">'+money(t.amount)+'</td><td>'+badge(t)+'</td><td>'+btn(record(t)?'Revisar':'Classificar','data-open="classify" data-id="'+esc(t.id)+'"')+'</td></tr>').join('')+'</tbody></table></div>'+(!matched.length?a.empty('Nenhum lançamento nesta seleção','Altere o mês, a conta ou o filtro.'):'')+'<div class="classification-pagination"><span>'+matched.length+' movimentos · página '+(listPage+1)+' de '+Math.max(1,Math.ceil(matched.length/30))+'</span>'+btn('Anterior','data-classification-page="-1" '+(listPage===0?'disabled':''))+btn('Próxima','data-classification-page="1" '+((listPage+1)*30>=matched.length?'disabled':''))+'</div></section><p class="classification-help">Alterações guardadas neste navegador. O CSV exporta o recorte e os filtros atuais; não envia documentos ao contador.</p>';
  }
  function categoryDialog(id){
    const c=catalog().find(c=>c.id===id)||{active:true};
    return {heading:'Indexador da empresa',body:a.formShell(id?'Editar classificação':'Nova classificação','A alteração vale para esta empresa. A referência original é preservada.',input('Nome da classificação','label',c.label)+input('Grupo','group',c.group)+'<p class="classification-help">Defina as contas atuais na aba Plano do contador. Ali cada correspondência usa uma conta do plano importado e a natureza do item.</p><label class="classification-check"><input type="checkbox" name="active" '+(c.active?'checked':'')+'>Disponível para novas classificações</label>'+(c.source?'<div class="classification-source"><b>Referência original de 2018 · DM!'+esc(c.source.range)+'</b><p>'+esc(c.source.realized||'Realizado não informado')+'<br>'+esc(c.source.pending||'Em aberto não informado')+'</p><p>Não aplicada automaticamente às contas atuais.</p></div>':'')+'<p class="form-error" role="alert"></p>','classification-category',id||'','Salvar classificação')};
  }
  const blankLine=(t,amount='')=>({id:crypto.randomUUID(),amount,category:'',purpose:'',belongsTo:a.company,competence:'',costCenter:'',asset:'',contract:'',obligation:'',parcel:'',note:'',documents:[]});
  const amountText=v=>v==null?'':(v/100).toFixed(2).replace('.',',');
  function draftFor(t){
    if(!a.current.classificationDraft){const r=record(t);a.current.classificationDraft=r?{party:r.party,complement:r.complement,lines:r.lines.map(l=>({...structuredClone(l),amount:amountText(l.amount)}))}:{party:'',complement:'',lines:[blankLine(t,amountText(Math.abs(t.amount)))]};}
    return a.current.classificationDraft;
  }
  function capture(form,data=new FormData(form)){
    const draft=a.current?.classificationDraft;if(!draft)return;
    draft.party=String(data.get('party')||'');draft.complement=String(data.get('complement')||'');
    draft.lines.forEach((line,i)=>{for(const key of ['amount','category','purpose','belongsTo','competence','costCenter','asset','contract','obligation','parcel','note'])line[key]=String(data.get(key+'-'+i)||'');line.documents=data.getAll('documents-'+i).map(String);line.contextOpen=Boolean(form.querySelector('[data-line-context="'+i+'"]')?.open);});
    return draft;
  }
  function lineForm(line,i){
    const cats=catalog(),groups=[...new Set(cats.filter(c=>c.active||c.id===line.category).map(c=>c.group))],suffix='-'+i;
    const categoryOptions='<option value="">Escolha uma classificação</option>'+groups.map(g=>'<optgroup label="'+esc(g)+'">'+cats.filter(c=>c.group===g&&(c.active||c.id===line.category)).map(c=>'<option value="'+esc(c.id)+'" '+(line.category===c.id?'selected':'')+'>'+esc(c.label)+(c.active?'':' · inativa')+'</option>').join('')+'</optgroup>').join('');
    const context=[refName('assets',line.asset),refName('contracts',line.contract),line.competence,line.costCenter].filter(Boolean).join(' · ');
    return '<fieldset class="classification-item"><legend>Item '+(i+1)+'</legend><div class="classification-item-top"><label>Classificação<select name="category'+suffix+'">'+categoryOptions+'</select></label><label>Valor deste item (R$)<input name="amount'+suffix+'" inputmode="decimal" value="'+esc(line.amount)+'" placeholder="0,00"></label>'+btn('Remover','data-classification-remove="'+i+'" aria-label="Remover item '+(i+1)+'"')+'</div><div class="formrow">'+select('Natureza deste valor','purpose'+suffix,Object.entries(PURPOSES).map(([id,label])=>({id,label})),line.purpose)+select('Pertence à empresa','belongsTo'+suffix,a.state.companies,line.belongsTo)+'</div>'+input('Competência','competence'+suffix,line.competence,'month')+'<details data-line-context="'+i+'" '+(line.contextOpen?'open':'')+'><summary>Competência, referência e documentos'+(context?' · '+esc(context):'')+'</summary><div class="classification-item-context"><div class="formrow">'+input('Centro de custo','costCenter'+suffix,line.costCenter)+'</div><div class="formrow">'+select('Ativo','asset'+suffix,scoped('assets',line.belongsTo),line.asset)+select('Contrato','contract'+suffix,scoped('contracts',line.belongsTo),line.contract)+'</div><div class="formrow">'+select('Obrigação relacionada','obligation'+suffix,scoped('obligations',line.belongsTo),line.obligation)+input('Parcela / referência','parcel'+suffix,line.parcel)+'</div><label>Contexto deste item<textarea name="note'+suffix+'" maxlength="1000" placeholder="Ex.: aluguel base do contrato ou rateio de energia.">'+esc(line.note)+'</textarea></label><div class="classification-docs"><b>Documentos relacionados</b>'+scoped('documents',line.belongsTo).filter(d=>!d.originalUrl||line.documents.includes(d.id)).map(d=>'<label class="classification-check"><input type="checkbox" name="documents'+suffix+'" value="'+esc(d.id)+'" '+(line.documents.includes(d.id)?'checked':'')+'>'+esc(d.name)+'</label>').join('')+'<small>O extrato de origem já acompanha o lançamento. Adicione recibos e documentos em Documentos para relacioná-los aqui.</small></div></div></details></fieldset>';
  }
  function dialog(kind,id){
    if(kind==='classification-category')return categoryDialog(id);
    if(kind!=='classify')return null;
    const t=classificationTransaction(a.state,a.company,id);if(!t)return {heading:'Classificação',body:'Lançamento indisponível nesta empresa.'};
    const draft=draftFor(t),r=record(t),bankName=a.get('accounts',t.account)?.name;
    return {heading:'Classificar lançamento',wide:true,body:'<div class="classification-bank"><div><span>ORIGEM BANCÁRIA PRESERVADA</span><h2>'+esc(t.description)+'</h2><p>'+fullDate(t.date)+' · '+esc(bankName)+' · '+esc(labelCompany(a.company))+'</p></div><strong class="'+(t.amount<0?'outgoing':'incoming')+'">'+money(t.amount)+'</strong>'+btn('Abrir extrato','data-statement-source="'+esc(t.id)+'"')+'</div><p class="classification-help">'+(t.amount<0?'Pagamento realizado pela conta de ':'Recebimento na conta de ')+esc(labelCompany(a.company))+'. Em cada item, indique a empresa à qual o valor pertence. Nenhum empréstimo, aporte ou conciliação é criado automaticamente.</p>'+evidence(t)+'<form class="form classification-form" data-form="classification" data-id="'+esc(t.id)+'">'+input('Contraparte identificada','party',draft.party)+'<label>Complemento do histórico<textarea name="complement" maxlength="1000" placeholder="Explique o movimento para a contabilidade.">'+esc(draft.complement)+'</textarea></label>'+draft.lines.map(lineForm).join('')+'<div class="drawer-actions">'+btn('Adicionar item à composição','data-classification-add="1"','','plus')+'</div><div class="classification-allocation" data-classification-allocation role="status">'+allocation(t,draft)+'</div><p class="form-error" role="alert"></p><div class="drawer-actions"><button class="btn" type="submit">Salvar rascunho</button>'+btn('Concluir revisão da composição','data-classification-review="1"','primary')+'</div><p class="classification-help">A revisão exige classificação, natureza, competência e a soma integral. Documentos e correspondência contábil mantêm sua revisão própria. Alterações ficam neste navegador.</p></form>'+(r?.history?.length?'<details class="classification-history"><summary>Histórico · '+r.history.length+' versão(ões) anterior(es)</summary>'+r.history.map(h=>'<p>Versão '+h.revision+' · '+fullDate(h.updatedAt)+' · '+esc(states[h.status])+' · '+h.lines.map(l=>esc(categoryLabel(l.category))+' '+money(l.amount)).join('; ')+'</p>').join('')+'</details>':'')};
  }
  function allocation(t,draft){
    const values=draft.lines.map(l=>centsInput(l.amount));
    if(values.some(v=>Number.isNaN(v)))return 'Confira os valores: use reais e centavos, como 1.234,56.';
    const sum=values.reduce((n,v)=>n+(v||0),0),remaining=Math.abs(t.amount)-sum;
    return '<span>Distribuído <b>'+money(sum)+'</b></span><span>'+(remaining<0?'Excede o lançamento':'A distribuir')+' <b>'+money(Math.abs(remaining))+'</b></span><span>'+(remaining===0?'Soma corresponde ao extrato':'Ajuste os itens antes de concluir')+'</span>';
  }
  function save(form,data,reviewed){
    try{const draft=capture(form,data);saveClassification(a.state,a.company,form.dataset.id,{...draft,lines:draft.lines.map(l=>({...l,amount:centsInput(l.amount)}))},reviewed?'reviewed':'draft',a.NOW);a.save();a.closeAll();a.render();a.toast(reviewed?'Composição revisada. Conciliação e documentos permanecem independentes.':'Rascunho salvo neste navegador.');}
    catch(error){form.querySelector('.form-error').textContent=error.message;form.querySelector('.form-error').scrollIntoView?.({block:'nearest'});}
    return true;
  }
  function exportCSV(){
    const tx=rows().filter(t=>(tab==='summary'||filter==='all'||status(t)===filter)&&(!query||tab==='summary'||[t.description,record(t)?.party,record(t)?.complement,...(record(t)?.lines||[]).map(l=>categoryLabel(l.category))].join(' ').toLocaleLowerCase('pt-BR').includes(query.toLocaleLowerCase('pt-BR'))));
    const headers=['ID lançamento','Data do extrato','Conta bancária','Empresa da conta','Histórico original','Contraparte','Complemento','Valor bancário (somar uma vez por ID)','Situação composição','Item','Valor do item com sinal','Grupo','Classificação','Natureza','Pertence à empresa','Competência','Centro de custo','Ativo','Contrato','Obrigação','Parcela / referência','Contexto','Documentos','Referência manual anterior (não validada no plano)','Revisão da referência manual','Fonte bancária','Registro / página','Fundamento inicial','Confiança inicial','Revisão necessária','Plano do contador','Código no plano importado','Conta no plano importado','Situação para contabilidade'];
    const data=tx.flatMap(t=>{const r=record(t),items=r?.lines.length?r.lines:[null];return items.map((l,i)=>{const c=catalog().find(c=>c.id===l?.category),mapping=l?resolveAccountingMapping(a.state,a.company,t,l):{reason:'Composição pendente'},initial=initialDecision(t),value=v=>(v/100).toFixed(2).replace('.',',');return [t.id,t.date,a.get('accounts',t.account)?.name,labelCompany(a.company),t.description,r?.party,r?.complement,i===0?value(t.amount):'',states[status(t)],l?i+1:'',l?.amount!=null?value(l.amount*(t.amount<0?-1:1)):'',c?.group,c?.label,PURPOSES[l?.purpose],l?labelCompany(l.belongsTo):'',l?.competence,l?.costCenter,refName('assets',l?.asset),refName('contracts',l?.contract),refName('obligations',l?.obligation),l?.parcel,l?.note,l?.documents.map(id=>refName('documents',id)).join('; '),c?[c.accountCode,c.accountLabel].filter(Boolean).join(' · '):'',c?.mappingReviewed?'Revisada por você':'A revisar',refName('documents',t.sourceDocument),t.sourceRecord||t.sourcePage||'',initial?.reason,initial?.confidence,initial?.review,mapping.plan,mapping.code,mapping.name,mapping.reason];});});
    const safe=v=>'"'+String(v??'').replace(/^[=+@-]/,"'$&").replaceAll('"','""')+'"';
    a.download('Classificacao-'+(period==='all'?'historico':a.month)+'.csv','\ufeff'+[headers,...data].map(row=>row.map((v,i)=>[7,10].includes(i)&&typeof v==='string'&&/^-?\d+,\d{2}$/.test(v)?'"'+v+'"':safe(v)).join(';')).join('\r\n'),'text/csv;charset=utf-8');
    a.toast('Classificação exportada com situação, composição e origem. Nenhum documento foi enviado.');
  }
  function click(d){
    if(plan.click(d))return true;
    if(d.classificationAllHistory){period='all';filter='all';query='';bank='all';listPage=0;tab='entries';a.render();return true;}
    if(d.classificationTab){tab=d.classificationTab;listPage=0;a.render();return true;}
    if(d.classificationFilterButton){filter=d.classificationFilterButton;listPage=0;a.render();return true;}
    if(d.classificationPage){listPage=Math.max(0,listPage+Number(d.classificationPage));a.render();return true;}
    if(d.classificationExport){exportCSV();return true;}
    if(d.classificationAdd||d.classificationRemove!==undefined||d.classificationReview){
      const form=document.querySelector('form[data-form="classification"]');if(!form)return true;
      const draft=capture(form),t=classificationTransaction(a.state,a.company,form.dataset.id);
      if(d.classificationReview)return save(form,new FormData(form),true);
      if(d.classificationAdd){if(draft.lines.length>=50){a.toast('Limite de 50 itens por lançamento.');return true;}draft.lines.push(blankLine(t));}
      else if(draft.lines.length>1)draft.lines.splice(Number(d.classificationRemove),1);else{a.toast('Mantenha ao menos um item na composição.');return true;}
      a.draw();return true;
    }
    return false;
  }
  function change(e){
    const d=e.target.dataset;
    if(plan.change(e))return true;
    if(d.classificationInitialSummary!==undefined){includeInitial=e.target.checked;a.render();return true;}
    if(d.classificationPeriod!==undefined){period=e.target.value;listPage=0;a.render();return true;}
    if(d.classificationBank!==undefined||d.classificationFilter!==undefined||d.classificationQuery!==undefined){if(d.classificationBank!==undefined)bank=e.target.value;if(d.classificationFilter!==undefined)filter=e.target.value;if(d.classificationQuery!==undefined)query=e.target.value.trim();listPage=0;a.render();return true;}
    const form=e.target.closest?.('form[data-form="classification"]');if(!form)return false;
    const draft=capture(form),match=e.target.name.match(/^belongsTo-(\d+)$/);
    if(match){Object.assign(draft.lines[Number(match[1])],{asset:'',contract:'',obligation:'',documents:[]});a.draw();}
    else{const t=classificationTransaction(a.state,a.company,form.dataset.id);form.querySelector('[data-classification-allocation]').innerHTML=allocation(t,draft);}
    return true;
  }
  function submit(form,data){
    if(plan.submit(form,data))return true;
    if(form.dataset.form==='classification')return save(form,data,false);
    if(form.dataset.form!=='classification-category')return false;
    try{saveCategory(a.state,a.company,form.dataset.id,{...catalog().find(c=>c.id===form.dataset.id),...Object.fromEntries([...data.entries(),['active',data.has('active')]])},a.NOW);a.save();a.closeAll();a.render();a.toast('Indexador atualizado nesta empresa.');}
    catch(error){form.querySelector('.form-error').textContent=error.message;}
    return true;
  }
  return {page,dialog,click,change,submit,summaryCard};
}
