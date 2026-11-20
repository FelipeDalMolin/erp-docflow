import {remaining} from './data.js?v=17';

// Retain the bank balance series, adding exact transaction dates even in long ranges.
export function withBalanceEvents(data,state,company,range){
  const ids=new Map(data.accounts.map((a,i)=>[a.id,i]));
  const transactions=state.transactions.filter(t=>t.company===company&&ids.has(t.account)&&t.date>=range.start&&t.date<=range.end)
    .map((t,index)=>({...t,index})).sort((a,b)=>a.date.localeCompare(b.date)||a.index-b.index);
  const obligations=data.obligations.filter(o=>remaining(state,o)>0);
  const dates=[...new Set([...data.points.slice(1).map(p=>p.date),...transactions.map(t=>t.date),...obligations.map(o=>o.due)])].sort();
  const balances=[...data.points[0].balances],points=[{...data.points[0]}];let pending=0;
  const snapshot=(date,transaction)=>{const total=balances.reduce((n,v)=>n+v,0);points.push({date,total,balances:[...balances],projected:total+pending,...(transaction?{transaction}:{})});};
  for(const date of dates){
    for(const t of transactions.filter(t=>t.date===date)){balances[ids.get(t.account)]+=t.amount;snapshot(date,t);}
    pending+=obligations.filter(o=>o.due===date).reduce((n,o)=>n+(o.kind==='in'?1:-1)*remaining(state,o),0);
    snapshot(date);
  }
  const openingSources=data.accounts.map(account=>state.transactions.filter(t=>t.account===account.id&&t.date<range.start).sort((a,b)=>a.date.localeCompare(b.date)||(a.sourceSequence||0)-(b.sourceSequence||0)).at(-1));
  return {...data,points,openingSources};
}
export function balancePointX(point,range){
  if(point.opening)return 82;
  const start=Date.parse(range.start+'T00:00:00Z'),end=Date.parse(range.end+'T00:00:00Z');
  return 82+(Date.parse(point.date+'T00:00:00Z')-start+86400000)/(end-start+86400000)*798;
}
