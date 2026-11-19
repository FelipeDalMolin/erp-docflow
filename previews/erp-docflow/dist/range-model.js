import {total,remaining} from './data.js?v=17';

const iso=d=>d.toISOString().slice(0,10);
const parse=d=>new Date(d+'T12:00:00Z');
export const validDate=d=>/^\d{4}-\d{2}-\d{2}$/.test(d)&&d>='1900-01-01'&&d<='9999-12-31'&&!Number.isNaN(parse(d).getTime())&&iso(parse(d))===d;
export const rangeDays=r=>Math.round((parse(r.end)-parse(r.start))/86400000)+1;
export function moveDate(value,days=0,months=0){
  const d=parse(value),day=d.getUTCDate();
  if(months){d.setUTCDate(1);d.setUTCMonth(d.getUTCMonth()+months);const last=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+1,0)).getUTCDate();d.setUTCDate(Math.min(day,last));}
  d.setUTCDate(d.getUTCDate()+days);return iso(d);
}
export function presetRange(preset,anchor,dates=[]){
  const year=anchor.slice(0,4),month=Number(anchor.slice(5,7)),monthStart=anchor.slice(0,7)+'-01';
  const fullMonths=(start,n)=>({start,end:moveDate(moveDate(start,0,n),-1)});
  if(preset==='day')return {start:anchor,end:anchor};
  if(preset==='week'){const start=moveDate(anchor,-((parse(anchor).getUTCDay()+6)%7));return {start,end:moveDate(start,6)};}
  if(preset==='month')return fullMonths(monthStart,1);
  if(preset==='quarter')return fullMonths(year+'-'+String(Math.floor((month-1)/3)*3+1).padStart(2,'0')+'-01',3);
  if(preset==='semester')return fullMonths(year+(month<=6?'-01-01':'-07-01'),6);
  if(preset==='year')return {start:year+'-01-01',end:year+'-12-31'};
  if(preset==='twelve')return fullMonths(moveDate(monthStart,0,-11),12);
  const sorted=dates.filter(validDate).sort();return {start:sorted[0]||anchor,end:sorted.at(-1)||anchor};
}
export function bucketCount(range,period){
  if(period==='daily')return rangeDays(range);
  if(period==='yearly')return Number(range.end.slice(0,4))-Number(range.start.slice(0,4))+1;
  return (Number(range.end.slice(0,4))-Number(range.start.slice(0,4)))*12+Number(range.end.slice(5,7))-Number(range.start.slice(5,7))+1;
}
// Each group uses exact inclusive boundaries. Partial months/years never expand the filter.
export function rangeBook(state,company,range,period='daily',account='all'){
  if(!validDate(range.start)||!validDate(range.end)||range.start>range.end)throw new Error('Período inválido.');
  const accounts=state.accounts.filter(a=>a.company===company&&(account==='all'||a.id===account)),ids=new Set(accounts.map(a=>a.id));
  const allTx=state.transactions.filter(t=>ids.has(t.account)),allObs=state.obligations.filter(o=>o.company===company&&ids.has(o.account));
  const result=[];
  for(let start=range.start;start<=range.end;){
    const key=start.slice(0,period==='daily'?10:period==='monthly'?7:4);
    const naturalEnd=period==='daily'?start:period==='monthly'?iso(new Date(Date.UTC(Number(start.slice(0,4)),Number(start.slice(5,7)),0,12))):key+'-12-31';
    const end=naturalEnd<range.end?naturalEnd:range.end;
    const transactions=allTx.filter(t=>t.date>=start&&t.date<=end),obligations=allObs.filter(o=>o.due>=start&&o.due<=end),tasks=state.tasks.filter(t=>t.company===company&&t.due>=start&&t.due<=end);
    const opening=accounts.reduce((n,a)=>n+a.opening,0)+allTx.filter(t=>t.date<start).reduce((n,t)=>n+t.amount,0);
    const incoming=transactions.filter(t=>t.amount>0).reduce((n,t)=>n+t.amount,0),outgoing=transactions.filter(t=>t.amount<0).reduce((n,t)=>n-t.amount,0);
    const sum=(kind,fn)=>obligations.filter(o=>o.kind===kind).reduce((n,o)=>n+fn(o),0);
    result.push({key,start,end,opening,incoming,outgoing,movement:incoming-outgoing,closing:opening+incoming-outgoing,transactions,obligations,tasks,dueIn:sum('in',total),dueOut:sum('out',total),pendingIn:sum('in',o=>remaining(state,o)),pendingOut:sum('out',o=>remaining(state,o))});
    if(end===range.end)break;start=moveDate(end,1);
  }
  return result;
}
