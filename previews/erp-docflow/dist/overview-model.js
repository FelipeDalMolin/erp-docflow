import {rangeBook,rangeDays,bucketCount} from './range-model.js?v=17';
import {summarizePeriods} from './workbook-model.js?v=17';

export function overviewData(state,company,range,selectedIds){
  const accounts=state.accounts.filter(a=>a.company===company&&selectedIds.includes(a.id));
  const grouping=rangeDays(range)<=93?'daily':bucketCount(range,'monthly')<=120?'monthly':'yearly';
  const series=accounts.map(account=>({account,periods:rangeBook(state,company,range,grouping,account.id)}));
  const empty=rangeBook({...state,accounts:[],transactions:[],obligations:[]},company,range,grouping);
  const columns=(series[0]?.periods||empty).map((base,i)=>{
    const p={key:base.key,start:base.start,end:base.end};
    for(const key of ['opening','closing','incoming','outgoing','movement','dueIn','dueOut','pendingIn','pendingOut'])p[key]=series.reduce((n,s)=>n+s.periods[i][key],0);
    for(const key of ['transactions','obligations','tasks'])p[key]=key==='tasks'?[]:series.flatMap(s=>s.periods[i][key]);
    return p;
  });
  let pending=0;
  const points=[{date:range.start,opening:true,total:columns[0].opening,projected:columns[0].opening,balances:series.map(s=>s.periods[0].opening)},...columns.map((p,i)=>{
    pending+=p.pendingIn-p.pendingOut;
    return {date:p.end,total:p.closing,projected:p.closing+pending,balances:series.map(s=>s.periods[i].closing)};
  })];
  const summary=summarizePeriods(columns);
  return {accounts,series,columns,grouping,points,summary,projected:summary.closing+summary.pendingIn-summary.pendingOut,
    transactions:[...summary.transactions].sort((a,b)=>b.date.localeCompare(a.date)||(a.account||'').localeCompare(b.account||'')||(a.sourceSequence??0)-(b.sourceSequence??0)||a.id.localeCompare(b.id)),
    obligations:[...summary.obligations].sort((a,b)=>a.due.localeCompare(b.due)||a.id.localeCompare(b.id))};
}
