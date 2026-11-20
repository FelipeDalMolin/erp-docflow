import {classificationStore,classificationCatalog,classificationStatus,PURPOSES} from './classification-model.js?v=29';
import {validDate} from './range-model.js?v=17';
const norm=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toLowerCase().replace(/[\s_-]+/g,'');
const clean=(s,max=300)=>String(s||'').trim().slice(0,max);
export function accountingPlanStore(state,company){
  if(!state.companies.some(c=>c.id===company))throw Error('Empresa indisponível.');
  const store=classificationStore(state);store.accountingPlans??={};
  return store.accountingPlans[company]??={plan:null,mappings:[],history:[]};
}
function parseRows(text){
  const source=String(text).replace(/^\ufeff/,'');
  if(source.length>2000000)throw Error('Use um CSV com até 2 MB.');
  const header=source.split(/\r?\n/,1)[0],separator=header.includes(';')?';':header.includes('\t')?'\t':',';
  const rows=[];let row=[],cell='',quoted=false;
  for(let i=0;i<source.length;i++){
    const c=source[i];
    if(c==='"'){if(quoted&&source[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}
    else if(c===separator&&!quoted){row.push(cell);cell='';}
    else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&source[i+1]==='\n')i++;row.push(cell);if(row.some(v=>v.trim()))rows.push(row);row=[];cell='';}
    else cell+=c;
  }
  if(quoted)throw Error('Aspas não fechadas no CSV.');
  row.push(cell);if(row.some(v=>v.trim()))rows.push(row);
  return rows;
}
export function parseAccountingPlanCSV(text){
  const rows=parseRows(text),headers=(rows.shift()||[]).map(norm);
  for(const name of ['codigo','nome','tipo'])if(!headers.includes(name))throw Error('O CSV precisa das colunas codigo;nome;tipo. O código é texto, inclusive zeros à esquerda.');
  if(new Set(headers).size!==headers.length)throw Error('Há cabeçalhos repetidos.');
  const accounts=rows.map((row,i)=>{
    if(row.length!==headers.length)throw Error('Linha '+(i+2)+': quantidade de colunas diferente do cabeçalho.');
    const values=Object.fromEntries(headers.map((h,j)=>[h,row[j].trim()])),code=values.codigo,name=values.nome;
    if(!code||!name||code.length>80||name.length>300||/[\u0000-\u001f]/.test(code+name))throw Error('Linha '+(i+2)+': código ou nome inválido.');
    const kind=norm(values.tipo),type=['analitica','a'].includes(kind)?'analytic':['sintetica','s'].includes(kind)?'synthetic':'';
    if(!type)throw Error('Linha '+(i+2)+': tipo deve ser analitica ou sintetica.');
    const active=norm(values.ativo||'sim');if(!['sim','nao','true','false','1','0'].includes(active))throw Error('Linha '+(i+2)+': ativo deve ser sim ou nao.');
    return {code,name,type,parent:values.contapai||'',active:['sim','true','1'].includes(active)};
  });
  if(!accounts.length||accounts.length>10000)throw Error('Informe de 1 a 10.000 contas.');
  const map=new Map(accounts.map(a=>[a.code,a]));
  if(map.size!==accounts.length)throw Error('Há códigos repetidos no plano.');
  for(const a of accounts){
    const seen=new Set([a.code]);let parent=a.parent;
    while(parent){const p=map.get(parent);if(!p||p.type!=='synthetic')throw Error('A conta pai de '+a.code+' deve existir como sintética no mesmo arquivo.');if(seen.has(parent))throw Error('Hierarquia circular em '+a.code+'.');seen.add(parent);parent=p.parent;}
  }
  return accounts;
}
export function importAccountingPlan(state,company,input,now){
  const accounts=parseAccountingPlanCSV(input.csv),label=clean(input.label),system=clean(input.system),validFrom=clean(input.validFrom,10);
  if(!label)throw Error('Informe o nome/versão do plano recebido.');
  if(validFrom&&!validDate(validFrom))throw Error('Data de vigência inválida.');
  const store=accountingPlanStore(state,company);
  if(store.plan)store.history.push(structuredClone(store.plan));
  store.plan={id:crypto.randomUUID(),label,system,validFrom,accounts,importedAt:now};
  // A new plan version intentionally invalidates prior mappings until rechecked.
  return store.plan;
}
export function saveAccountingMapping(state,company,input,now){
  const store=accountingPlanStore(state,company),plan=store.plan;
  if(!plan)throw Error('Importe primeiro o plano atual do contador.');
  const category=classificationCatalog(state,company).find(c=>c.id===input.category);
  if(!category||!PURPOSES[input.purpose])throw Error('Escolha a classificação e a natureza do item.');
  if(!['incoming','outgoing','both'].includes(input.direction))throw Error('Escolha o sentido do movimento.');
  const account=plan.accounts.find(c=>c.code===input.accountCode&&c.active&&c.type==='analytic');
  if(!account)throw Error('Escolha uma conta analítica ativa do plano importado.');
  const key=[category.id,input.purpose,input.direction].join('|'),prior=store.mappings.find(m=>m.key===key);
  const next={key,category:category.id,purpose:input.purpose,direction:input.direction,accountCode:account.code,accountLabel:account.name,planId:plan.id,reviewed:input.reviewed===true,note:clean(input.note,1000),updatedAt:now,history:prior?[...prior.history,structuredClone({...prior,history:undefined})]:[]};
  if(prior)Object.assign(prior,next);else store.mappings.push(next);
  return next;
}
export function resolveAccountingMapping(state,company,t,line){
  const store=accountingPlanStore(state,company),plan=store.plan,blocked=reason=>({ready:false,reason,code:'',name:''});
  if(!plan)return blocked('Plano do contador não importado');
  if(line.belongsTo!==company)return blocked('Item de outra empresa: definir sua correspondência contábil');
  if(!line.purpose)return blocked('Natureza do item pendente');
  const direction=t.amount>0?'incoming':'outgoing';
  const candidates=store.mappings.filter(m=>m.category===line.category&&m.purpose===line.purpose);
  const mapping=candidates.find(m=>m.direction===direction)||candidates.find(m=>m.direction==='both');
  if(!mapping)return blocked('Correspondência ainda não definida para esta natureza/sentido');
  if(mapping.planId!==plan.id)return blocked('Correspondência de versão anterior: revisar');
  if(plan.validFrom&&t.date<plan.validFrom)return blocked('Movimento anterior à vigência informada do plano');
  const account=plan.accounts.find(c=>c.code===mapping.accountCode&&c.active&&c.type==='analytic');
  if(!account)return blocked('Conta indisponível no plano atual');
  const info={code:account.code,name:account.name,plan:plan.label};
  if(!mapping.reviewed)return {...info,ready:false,reason:'Correspondência aguardando revisão'};
  if(classificationStatus(state,company,t)!=='reviewed')return {...info,ready:false,reason:'Composição do lançamento aguardando revisão'};
  return {...info,ready:true,reason:'Composição e correspondência revisadas'};
}
