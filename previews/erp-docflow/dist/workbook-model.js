import {figures, total, remaining} from './data.js?v=17';

export function monthDays(month) {
  const [year, number] = month.split('-').map(Number);
  const count = new Date(Date.UTC(year, number, 0)).getUTCDate();
  return Array.from({length:count}, (_,i)=>`${month}-${String(i+1).padStart(2,'0')}`);
}

// Realized balances only use bank movements. Outstanding commitments are separate.
export function dailyBook(state, company, month, account='all') {
  const f = figures(state,company,month,account);
  let balance = f.opening;
  return monthDays(month).map(date=>{
    const transactions = f.current.filter(t=>t.date===date);
    const obligations = f.obs.filter(o=>o.due===date);
    const tasks = state.tasks.filter(t=>t.company===company&&t.due===date);
    const incoming = transactions.filter(t=>t.amount>0).reduce((n,t)=>n+t.amount,0);
    const outgoing = transactions.filter(t=>t.amount<0).reduce((n,t)=>n-t.amount,0);
    const opening = balance;
    balance += incoming-outgoing;
    return {date,opening,incoming,outgoing,movement:incoming-outgoing,closing:balance,
      dueIn:obligations.filter(o=>o.kind==='in').reduce((n,o)=>n+total(o),0),
      dueOut:obligations.filter(o=>o.kind==='out').reduce((n,o)=>n+total(o),0),
      pendingIn:obligations.filter(o=>o.kind==='in').reduce((n,o)=>n+remaining(state,o),0),
      pendingOut:obligations.filter(o=>o.kind==='out').reduce((n,o)=>n+remaining(state,o),0),
      transactions,obligations,tasks};
  });
}

// Balances are snapshots; only movements and commitments are additive.
export function summarizePeriods(periods) {
  const summary={opening:periods[0]?.opening||0,closing:periods.at(-1)?.closing||0};
  for(const key of ['incoming','outgoing','movement','dueIn','dueOut','pendingIn','pendingOut'])
    summary[key]=periods.reduce((sum,p)=>sum+p[key],0);
  for(const key of ['transactions','obligations','tasks'])summary[key]=periods.flatMap(p=>p[key]);
  return summary;
}

export function workbookPeriods(state,company,month,period='daily',account='all') {
  if(period==='daily')return dailyBook(state,company,month,account).map(d=>({...d,key:d.date,start:d.date,end:d.date}));
  const monthly=year=>Array.from({length:12},(_,i)=>{
    const key=year+'-'+String(i+1).padStart(2,'0'),days=dailyBook(state,company,key,account);
    return {...summarizePeriods(days),key,start:days[0].date,end:days.at(-1).date};
  });
  if(period==='monthly')return monthly(month.slice(0,4));
  const ids=new Set(state.accounts.filter(a=>a.company===company&&(account==='all'||a.id===account)).map(a=>a.id));
  const years=[...new Set([month.slice(0,4),
    ...state.transactions.filter(t=>ids.has(t.account)).map(t=>t.date.slice(0,4)),
    ...state.obligations.filter(o=>o.company===company&&ids.has(o.account)).map(o=>o.due.slice(0,4))])].sort();
  return years.map(key=>({...summarizePeriods(monthly(key)),key,start:key+'-01-01',end:key+'-12-31'}));
}

export function contractTemplate(state, contractId, competence) {
  const c=state.contracts.find(c=>c.id===contractId);
  if(!c) throw new Error('Contrato indisponível.');
  const [year,month]=competence.split('-').map(Number);
  if(!year||!month||month>12)throw new Error('Informe uma competência válida.');
  const end=monthDays(competence).at(-1);
  const due=competence+'-'+String(Math.min(c.due,Number(end.slice(8)))).padStart(2,'0');
  const previous=state.obligations.filter(o=>o.contract===c.id).sort((a,b)=>a.competence.localeCompare(b.competence))[0];
  return {company:c.company,contract:c.id,asset:c.asset,party:c.party,kind:'in',due,competence,
    title:`${c.title} · ${String(month).padStart(2,'0')}/${year}`,
    account:previous?.account||state.accounts.find(a=>a.company===c.company)?.id,
    items:[{name:`Valor base · ${String(month).padStart(2,'0')}/${year}`,amount:c.base,nature:previous?.items[0]?.nature||'A classificar',rule:`${c.number} · ${c.revision}`,doc:c.doc}],
    rule:c.rule,number:c.number,valid:due>=c.start&&due<=c.end};
}

export const receiveTools = [
  {id:'direct',label:'Leitura direta',description:'PDF com texto selecionável: aproveitar o conteúdo nativo.',icon:'file'},
  {id:'ocr',label:'OCR',description:'Foto ou digitalização: reconhecer o texto e revisar o resultado.',icon:'eye'},
  {id:'password',label:'Documento com senha',description:'Liberar a leitura com uma senha informada por você.',icon:'lock'},
  {id:'pages',label:'Selecionar páginas',description:'Separar a parte útil e manter o original completo.',icon:'file'},
  {id:'bundle',label:'Organizar conjunto',description:'Relacionar cobrança, obrigação, recibo e comprovante.',icon:'link'}
];
