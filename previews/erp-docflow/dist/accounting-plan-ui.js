import {accountingPlanStore,parseAccountingPlanCSV,importAccountingPlan,saveAccountingMapping,resolveAccountingMapping} from './accounting-plan-model.js?v=29';
import {classificationCatalog,getClassification,PURPOSES} from './classification-model.js?v=29';

export function createAccountingPlan(a){
  const {esc,btn}=a;let company='',draft={csv:'',label:'',system:'',validFrom:''},preview=null,error='';
  const sync=()=>{if(company!==a.company){company=a.company;draft={csv:'',label:'',system:'',validFrom:''};preview=null;error='';}};
  const options=rows=>'<option value="">Selecione</option>'+rows.map(([id,label])=>'<option value="'+esc(id)+'">'+esc(label)+'</option>').join('');
  const field=(label,name,value,type='text')=>'<label>'+label+'<input type="'+type+'" name="'+name+'" value="'+esc(value)+'"></label>';
  function page(){
    sync();const store=accountingPlanStore(a.state,a.company),p=store.plan,cats=classificationCatalog(a.state,a.company),tx=a.state.transactions.filter(t=>a.state.accounts.some(b=>b.id===t.account&&b.company===a.company));
    let ready=0,pending=0;
    for(const t of tx){const r=getClassification(a.state,a.company,t.id);if(!r){pending++;continue;}for(const l of r.lines){if(resolveAccountingMapping(a.state,a.company,t,l).ready)ready++;else pending++;}}
    return '<section class="panel accounting-plan"><div class="panel-head"><div><h2>Plano do contador</h2><p>Seu Indexador permanece. A correspondência adapta cada item ao plano da empresa.</p></div>'+btn('Baixar modelo CSV','data-plan-template="1"','','download')+'</div><div class="classification-explainer"><p><b>Classificação → natureza → conta contábil.</b> Uma mesma categoria pode ter contas diferentes para despesa própria e rateio. Divida o lançamento quando houver mais de uma finalidade.</p><p>Esta tela prepara uma exportação para conferência. Não gera partidas de débito/crédito nem envia lançamentos ao software do contador. '+ready+' item(ns) com composição e correspondência revisadas; '+pending+' item(ns)/movimento(s) pendentes em todo o histórico.</p></div>'+
      (p?'<div class="classification-source"><b>'+esc(p.label)+'</b><p>'+p.accounts.length+' contas · '+esc(p.system||'Sistema a informar')+' · Vigência: '+esc(p.validFrom||'não informada')+'</p><p>Códigos preservados como texto. Importar uma nova versão exige revisar novamente as correspondências.</p></div>':'<p class="classification-help">Nenhum plano atual foi importado. Os códigos do contador continuam em branco.</p>')+
      '<details class="plan-import" '+(!p?'open':'')+'><summary>'+ (p?'Importar outra versão do plano':'Importar plano recebido do contador')+'</summary><form class="form" data-form="accounting-plan"><div class="formrow">'+field('Nome / versão do plano','label',draft.label)+field('Sistema do contador (opcional)','system',draft.system)+'</div>'+field('Vigente a partir de (opcional)','validFrom',draft.validFrom,'date')+'<label>Carregar CSV<input type="file" accept=".csv,text/csv" data-plan-file></label><label>Conteúdo CSV<textarea name="csv" rows="7" spellcheck="false" placeholder="codigo;nome;tipo;conta_pai;ativo">'+esc(draft.csv)+'</textarea></label><p class="annotation">Colunas obrigatórias: codigo, nome, tipo (analitica ou sintetica). Opcionais: conta_pai, ativo (sim/nao). Use o plano real da empresa; o modelo contém apenas cabeçalhos.</p><p class="form-error" role="alert">'+esc(error)+'</p><button class="btn" type="submit">Conferir importação</button>'+
      (preview?'<div class="plan-preview"><b>'+preview.accounts.length+' contas válidas para '+esc(preview.input.label)+'</b><ul>'+preview.accounts.slice(0,8).map(c=>'<li>'+esc(c.code)+' · '+esc(c.name)+' · '+(c.type==='analytic'?'Analítica':'Sintética')+'</li>').join('')+'</ul>'+btn('Usar este plano','data-plan-confirm="1"','primary')+'</div>':'')+'</form></details>'+
      (p?'<section class="plan-mapping"><h3>Nova correspondência / substituir existente</h3><form class="form" data-form="accounting-mapping"><div class="formrow"><label>Classificação do Indexador<select name="category">'+options(cats.filter(c=>c.active).map(c=>[c.id,c.label]))+'</select></label><label>Natureza do item<select name="purpose">'+options(Object.entries(PURPOSES))+'</select></label></div><div class="formrow"><label>Sentido bancário<select name="direction"><option value="both">Entradas e saídas</option><option value="incoming">Somente entradas</option><option value="outgoing">Somente saídas</option></select></label><label>Conta analítica do contador<select name="accountCode">'+options(p.accounts.filter(c=>c.active&&c.type==='analytic').map(c=>[c.code,c.code+' · '+c.name]))+'</select></label></div><label>Observação<textarea name="note" maxlength="1000"></textarea></label><label class="classification-check"><input type="checkbox" name="reviewed">Correspondência revisada com a contabilidade</label><p class="form-error" role="alert"></p><button class="btn primary" type="submit">Salvar correspondência</button></form><div class="table-wrap"><table><thead><tr><th>Classificação / natureza</th><th>Sentido</th><th>Conta do contador</th><th>Situação</th></tr></thead><tbody>'+store.mappings.map(m=>'<tr><td>'+esc(cats.find(c=>c.id===m.category)?.label)+'<small>'+esc(PURPOSES[m.purpose])+'</small></td><td>'+({both:'Ambos',incoming:'Entrada',outgoing:'Saída'}[m.direction])+'</td><td>'+esc(m.accountCode)+' · '+esc(m.accountLabel)+'</td><td>'+(m.planId!==p.id?'Versão anterior · revisar':m.reviewed?'Correspondência revisada':'A revisar')+'</td></tr>').join('')+'</tbody></table></div></section>':'')+'</section>';
  }
  const read=form=>Object.fromEntries(new FormData(form));
  function submit(form,data){
    if(!['accounting-plan','accounting-mapping'].includes(form.dataset.form))return false;
    sync();
    try{
      if(form.dataset.form==='accounting-plan'){
        draft=Object.fromEntries(data);if(!draft.label.trim())throw Error('Informe o nome/versão do plano.');
        preview={input:{...draft},accounts:parseAccountingPlanCSV(draft.csv)};error='';a.render();
      }else{saveAccountingMapping(a.state,a.company,{...Object.fromEntries(data),reviewed:data.has('reviewed')},a.NOW);a.save();a.render();a.toast('Correspondência salva para esta empresa.');}
    }catch(e){preview=null;error=e.message;form.querySelector('.form-error').textContent=e.message;}
    return true;
  }
  function click(d){
    if(d.planTemplate){a.download('Modelo-plano-do-contador.csv','\ufeffcodigo;nome;tipo;conta_pai;ativo\r\n','text/csv;charset=utf-8');return true;}
    if(!d.planConfirm)return false;
    const form=document.querySelector('form[data-form="accounting-plan"]');
    try{const current=read(form);if(!preview||JSON.stringify(current)!==JSON.stringify(preview.input))throw Error('O conteúdo mudou. Confira novamente antes de usar o plano.');importAccountingPlan(a.state,a.company,current,a.NOW);a.save();draft={csv:'',label:'',system:'',validFrom:''};preview=null;error='';a.render();a.toast('Plano importado. Defina as correspondências abaixo.');}
    catch(e){form.querySelector('.form-error').textContent=e.message;}
    return true;
  }
  function change(e){
    if(e.target.dataset.planFile===undefined)return false;
    const file=e.target.files?.[0],owner=a.company;if(!file)return true;
    if(file.size>2000000){a.toast('Use um CSV com até 2 MB.');return true;}
    draft=read(e.target.closest('form'));preview=null;
    file.arrayBuffer().then(buffer=>{if(a.company!==owner)return;let text=new TextDecoder('utf-8').decode(buffer);if(text.includes('\ufffd'))text=new TextDecoder('windows-1252').decode(buffer);draft.csv=text;if(!draft.label)draft.label=file.name;error='';a.render();}).catch(()=>a.toast('Não foi possível ler o CSV.'));
    return true;
  }
  return {page,submit,click,change};
}
