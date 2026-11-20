import {validDate,moveDate} from './range-model.js?v=17';

const normal=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/^INTERNET\s*[- ]*/, '').replace(/[^A-Z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
const median=values=>{const v=[...values].sort((a,b)=>a-b),i=Math.floor(v.length/2);return Math.round(v.length%2?v[i]:(v[i-1]+v[i])/2);};
const monthShift=(month,n)=>{const d=new Date(month+'-01T12:00:00Z');d.setUTCMonth(d.getUTCMonth()+n);return d.toISOString().slice(0,7);};
const monthEnd=month=>moveDate(monthShift(month,1)+'-01',-1);
const monthCount=rows=>new Set(rows.map(t=>t.date.slice(0,7))).size;
const lastWeekday=month=>{let d=monthEnd(month);while([0,6].includes(new Date(d+'T12:00:00Z').getUTCDay()))d=moveDate(d,-1);return d;};
const dateAt=(month,day)=>month+'-'+String(Math.min(Number(monthEnd(month).slice(8)),Math.max(1,day))).padStart(2,'0');
const hash=value=>{let n=2166136261;for(const c of value){n^=c.charCodeAt(0);n=Math.imul(n,16777619);}return (n>>>0).toString(36);};
const key=(company,id)=>company+':'+id;
const eligible=t=>t.imported&&validDate(t.date)&&Number.isSafeInteger(t.amount)&&t.amount!==0&&t.movementType!=='investment-transfer'&&!/RENTAB|RENDIMENTO|RENDE FACIL|INVEST FACIL|APLICACAO|RESGATE/.test(normal(t.description));
function identity(t){
  const detail=(t.details||[]).filter(x=>/[A-Za-zÀ-ÿ]{3}/.test(x)&&!/^\d{2}[/.]\d{2}/.test(x.trim())).join(' ');
  const text=normal(detail||t.history||t.description);
  if(text.length<5||/^(PAGTO ELETRON COBRANCA|TRANSF PGTO PIX|TRANSFERENCIA PIX|PIX RECEBIDO|PIX ENVIADO|TRANSF CC PARA CC|PAGAMENTO|TRANSFERENCIA|DEBITO AUTOMATICO|ORDEM BANCARIA)$/.test(text))return null;
  return text;
}
const compatible=(a,b)=>a===b||(Math.min(a.length,b.length)>=24&&(a.startsWith(b+' ')||b.startsWith(a+' ')));
function regular(rows,previousMonth){return monthCount(rows)>=3&&rows.some(t=>t.date.slice(0,7)>=monthShift(previousMonth,-1))&&monthCount(rows)===rows.length;}

// Rules use only bank text, direction, dates and integer amounts. No accounting categories.
export function recurringPatterns(state,company,today){
  const current=today.slice(0,7),previous=monthShift(current,-1),start=monthShift(current,-6)+'-01';
  const rows=state.transactions.filter(t=>t.company===company&&eligible(t)&&t.date>=start&&t.date<current+'-01'&&identity(t));
  const names=[...new Set(rows.map(identity))].sort((a,b)=>a.length-b.length||a.localeCompare(b));
  const canonical=name=>names.find(n=>compatible(name,n))||name;
  const buckets=new Map();
  for(const t of rows){
    const account=state.accounts.find(a=>a.company===company&&a.id===t.account),period=account?.statement?.period,m=t.date.slice(0,7);
    if(!period||period.start>m+'-01'||period.end<monthEnd(m))continue;
    const name=canonical(identity(t)),id=Math.sign(t.amount)+'|'+name;
    if(!buckets.has(id))buckets.set(id,{name,rows:[]});buckets.get(id).rows.push(t);
  }
  const patterns=[];
  function add(name,series,suffix){
    if(!regular(series,previous))return;
    const sorted=[...series].sort((a,b)=>a.date.localeCompare(b.date)),amounts=sorted.map(t=>Math.abs(t.amount)),days=sorted.map(t=>Number(t.date.slice(8)));
    const endRule=sorted.filter(t=>t.date>=moveDate(monthEnd(t.date.slice(0,7)),-3)).length/sorted.length>=.8;
    const patternKey=hash(company+'|'+Math.sign(sorted[0].amount)+'|'+name+'|'+suffix);
    patterns.push({patternKey,identity:name,title:sorted.at(-1).details?.join(' ')||sorted.at(-1).history||name,company,direction:Math.sign(sorted[0].amount),amount:median(amounts),minAmount:Math.min(...amounts),maxAmount:Math.max(...amounts),
      day:median(days),minDay:Math.min(...days),maxDay:Math.max(...days),endRule,accounts:[...new Set(sorted.map(t=>t.account))],sourceIds:sorted.map(t=>t.id),months:monthCount(sorted),lastDate:sorted.at(-1).date,
      dateNote:endRule?'Perto do fim do mês; sugestão na última segunda a sexta. Feriados não considerados.':Math.max(...days)-Math.min(...days)>7?'Datas variáveis; a data central é apenas uma referência.':'Data central das ocorrências anteriores; pode variar.'});
  }
  for(const {name,rows:group} of buckets.values()){
    if(monthCount(group)===group.length){add(name,group,'monthly');continue;}
    const exact=new Map();for(const t of group){const value=Math.abs(t.amount);if(!exact.has(value))exact.set(value,[]);exact.get(value).push(t);}
    const used=new Set();for(const [amount,series] of exact){if(regular(series,previous)){add(name,series,'amount:'+amount);series.forEach(t=>used.add(t.id));}}
    const rest=group.filter(t=>!used.has(t.id));if(used.size)add(name,rest,'variable');
  }
  return patterns.sort((a,b)=>a.title.localeCompare(b.title,'pt-BR'));
}

function makeForecast(pattern,month){
  const date=pattern.endRule?lastWeekday(month):dateAt(month,pattern.day),windowStart=pattern.endRule?moveDate(monthEnd(month),-3):dateAt(month,pattern.minDay),windowEnd=pattern.endRule?monthEnd(month):dateAt(month,pattern.maxDay);
  return {...pattern,id:'forecast-'+pattern.patternKey+'-'+month,month,date,windowStart,windowEnd};
}
export function rememberForecasts(state,company,today){
  let changed=false;state.forecastOverrides??={};
  for(const pattern of recurringPatterns(state,company,today)){
    const snapshot=makeForecast(pattern,today.slice(0,7)),id=key(company,snapshot.id);
    if(!state.forecastOverrides[id]){state.forecastOverrides[id]={snapshot,generatedAt:today,history:[]};changed=true;}
  }
  return changed;
}
export function forecastItems(state,company,today){
  const byId=new Map(),patterns=recurringPatterns(state,company,today),current=today.slice(0,7);
  for(let i=0;i<3;i++)for(const pattern of patterns){const f=makeForecast(pattern,monthShift(current,i));byId.set(f.id,f);}
  for(const [id,record] of Object.entries(state.forecastOverrides||{}))if(id.startsWith(company+':')&&record.snapshot?.company===company)byId.set(record.snapshot.id,record.snapshot);
  return [...byId.values()].map(f=>forecastStatus(state,f,today)).sort((a,b)=>a.date.localeCompare(b.date)||a.title.localeCompare(b.title,'pt-BR'));
}
export function forecastStatus(state,base,today){
  const decision=state.forecastOverrides?.[key(base.company,base.id)]||{},date=decision.date||base.date,amount=decision.amount||base.amount;
  const windowStart=decision.date?date:base.windowStart,windowEnd=decision.date?date:base.windowEnd;
  const sampleMin=decision.amount?amount:base.minAmount,sampleMax=decision.amount?amount:base.maxAmount,tolerance=Math.max(100,Math.round(amount*.05));
  const assigned=new Set(Object.entries(state.forecastOverrides||{}).filter(([id,r])=>id!==key(base.company,base.id)&&id.startsWith(base.company+':')&&r.matchedTransactionId).map(([,r])=>r.matchedTransactionId));
  const searchStart=moveDate(windowStart,-3),searchEnd=moveDate(windowEnd,3),searchMonth=date.slice(0,7);
  const candidates=state.transactions.filter(t=>t.company===base.company&&t.date<=today&&t.date>=searchStart&&t.date<=searchEnd&&t.date.startsWith(searchMonth)&&Math.sign(t.amount)===base.direction&&Math.abs(t.amount)>=sampleMin-tolerance&&Math.abs(t.amount)<=sampleMax+tolerance&&!assigned.has(t.id)&&eligible(t)&&identity(t)&&compatible(identity(t),base.identity));
  const matched=state.transactions.find(t=>t.company===base.company&&t.id===decision.matchedTransactionId&&eligible(t)&&Math.sign(t.amount)===base.direction&&t.date<=today);
  const covered=base.accounts.every(id=>{const p=state.accounts.find(a=>a.company===base.company&&a.id===id)?.statement?.period;return p&&p.start<=windowStart&&p.end>=today;});
  const f={...base,date,amount,windowStart,windowEnd,kind:'forecast',target:base.id,expected:amount,owner:'A definir',decision,candidateIds:candidates.map(t=>t.id),matchedTransactionId:matched?.id,covered,group:'planned',label:decision.accepted?'Previsão acompanhada':'Previsão a confirmar',next:'Revisar data e valor sugeridos',detail:`Repetição em ${base.months} meses do histórico. Não confirma uma obrigação.`,snapshot:base};
  if(decision.dismissed)return {...f,group:'resolved',label:'Previsão descartada',detail:decision.reason||'Descartada neste mês.',next:'Reabrir previsão',hidden:true};
  if(matched)return {...f,group:'resolved',label:'Ocorrência reconhecida',detail:'Correspondência reconhecida por você. A conciliação contábil permanece independente.',next:'Consultar movimento e histórico'};
  if(decision.matchedTransactionId)return {...f,group:'verify',label:'Correspondência indisponível',detail:'O movimento reconhecido não está disponível nesta empresa. Revise a previsão.',next:'Rever correspondência'};
  if(candidates.length)return {...f,group:'verify',label:'Possível correspondência · conferir',detail:`${candidates.length} movimento(s) semelhante(s) no período. Nenhum vínculo foi confirmado automaticamente.`,next:'Conferir possível ocorrência'};
  if(date<today){
    if(!covered)return {...f,group:'verify',label:'Data prevista passou · falta extrato',detail:'A cobertura das contas do histórico não permite verificar o período. Não é atraso confirmado.',next:'Atualizar extrato e verificar previsão'};
    if(today<=windowEnd)return {...f,group:'verify',label:'Data prevista passou · dentro da faixa',detail:'A data central passou, mas ainda está na faixa observada no histórico. Confira se ocorreu.',next:'Conferir data e movimentos'};
    return {...f,group:'deviation',label:'Não localizada · previsão a revisar',detail:'Data e faixa esperadas passaram sem movimento semelhante nos extratos disponíveis. Isso não comprova dívida ou inadimplência.',next:'Revisar previsão e definir próxima ação'};
  }
  if(date<=moveDate(today,7))f.group='due';
  return f;
}

export function updateForecast(state,item,changes,today){
  state.forecastOverrides??={};const id=key(item.company,item.id),previous=state.forecastOverrides[id]||{};
  state.forecastOverrides[id]={...previous,...changes,snapshot:previous.snapshot||structuredClone(item.snapshot),history:[...(previous.history||[]),{date:today,action:changes.action||'Revisão',fromDate:item.date,fromAmount:item.amount,toDate:changes.date||item.date,toAmount:changes.amount||item.amount}]};
  return state.forecastOverrides[id];
}
