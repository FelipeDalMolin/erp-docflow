import {rangeBook,moveDate,validDate} from './range-model.js?v=17';
import {total} from './data.js?v=17';
import {forecastItems} from './forecast-model.js?v=23';

const selectedAccounts=(state,company,account)=>state.accounts.filter(a=>a.company===company&&(account==='all'||a.id===account));
const active=o=>!o.cancelled&&o.status!=='cancelled';
const compatiblePayment=(state,o,t)=>Number.isSafeInteger(t.amount)&&state.accounts.some(a=>a.id===t.account&&a.company===o.company)&&(!t.company||t.company===o.company)&&Math.sign(t.amount)===(o.kind==='in'?1:-1);
export function planningPaid(state,o){
  return state.transactions.filter(t=>t.obligation===o.id&&t.confirmed&&compatiblePayment(state,o,t)).reduce((n,t)=>n+Math.abs(t.amount),0);
}
export const planningRemaining=(state,o)=>Math.max(0,total(o)-planningPaid(state,o));
export function planningCoverage(state,company,range,account='all'){
  return selectedAccounts(state,company,account).map(a=>{
    const p=a.statement?.period;
    return {id:a.id,name:a.name,period:p||null,status:p?(range.start>=p.start&&range.end<=p.end?'full':range.start<=p.end&&range.end>=p.start?'partial':'missing'):state.dataset?'missing':'manual'};
  });
}
export function planningHistoryRange(state,company,account='all',fallback){
  const accounts=selectedAccounts(state,company,account),ids=new Set(accounts.map(a=>a.id));
  const dates=accounts.flatMap(a=>a.statement?[a.statement.period.start,a.statement.period.end]:[]);
  dates.push(...state.transactions.filter(t=>ids.has(t.account)).map(t=>t.date));
  const sorted=dates.filter(validDate).sort();return sorted.length?{start:sorted[0],end:sorted.at(-1)}:{...fallback};
}
// A reference at the end of each account's available statement is not today's balance.
function referenceAt(state,company,accounts,date,rangeStart){
  const refs=accounts.map(a=>{
    const p=a.statement?.period,manual=!state.dataset&&!p;
    if(!p&&!manual||p&&date<p.start)return {account:a.id,date:null,amount:null,known:false};
    const anchor=p?(date<p.end?date:p.end):date;
    const amount=a.opening+state.transactions.filter(t=>t.account===a.id&&t.date<=anchor).reduce((n,t)=>n+t.amount,0);
    return {account:a.id,date:anchor,amount,known:true,manual};
  });
  const known=refs.length>0&&refs.every(r=>r.known);
  let delta=0,excluded=0;
  for(const o of state.obligations.filter(o=>active(o)&&o.company===company&&accounts.some(a=>a.id===o.account))){
    const left=planningRemaining(state,o);if(!left||o.due>date)continue;
    const ref=refs.find(r=>r.account===o.account);
    const afterBase=ref?.manual?o.due>=rangeStart:ref?.date&&o.due>ref.date;
    // An unconfirmed association may already be in the bank balance: require review first.
    const unresolvedLink=state.transactions.some(t=>t.obligation===o.id&&(!t.confirmed||!compatiblePayment(state,o,t)));
    if(!afterBase||unresolvedLink){excluded++;continue;}
    delta+=(o.kind==='in'?1:-1)*left;
  }
  return {references:refs,reference:known?refs.reduce((n,r)=>n+r.amount,0):null,projected:known?refs.reduce((n,r)=>n+r.amount,0)+delta:null,projectionDelta:delta,excluded};
}
export function planningBook(state,company,range,period='daily',account='all',today='2026-11-20'){
  const accounts=selectedAccounts(state,company,account),ids=new Set(accounts.map(a=>a.id));
  const forecasts=forecastItems(state,company,today).filter(f=>!f.hidden&&f.group!=='resolved'&&f.accounts.some(id=>ids.has(id)));
  return rangeBook(state,company,range,period,account).map(p=>{
    const coverage=planningCoverage(state,company,p,account),complete=coverage.length>0&&coverage.every(c=>c.status==='full'||c.status==='manual');
    const openingKnown=accounts.length>0&&accounts.every(a=>a.statement?p.start>=a.statement.period.start&&p.start<=moveDate(a.statement.period.end,1):!state.dataset);
    const closingKnown=accounts.length>0&&accounts.every(a=>a.statement?p.end>=a.statement.period.start&&p.end<=a.statement.period.end:!state.dataset);
    const reference=referenceAt(state,company,accounts,p.end,range.start);
    const selectedForecasts=forecasts.filter(f=>f.date>=p.start&&f.date<=p.end);
    const obligations=p.obligations.filter(active);
    return {...p,obligations,date:p.start,opening:openingKnown?p.opening:null,closing:closingKnown?p.closing:null,coverage,complete,...reference,
      dueIn:obligations.filter(o=>o.kind==='in').reduce((n,o)=>n+total(o),0),dueOut:obligations.filter(o=>o.kind==='out').reduce((n,o)=>n+total(o),0),
      pendingIn:obligations.filter(o=>o.kind==='in').reduce((n,o)=>n+planningRemaining(state,o),0),pendingOut:obligations.filter(o=>o.kind==='out').reduce((n,o)=>n+planningRemaining(state,o),0),
      forecasts:selectedForecasts,forecastIn:selectedForecasts.filter(f=>f.direction>0).reduce((n,f)=>n+f.amount,0),forecastOut:selectedForecasts.filter(f=>f.direction<0).reduce((n,f)=>n+f.amount,0)};
  });
}
export function planningSummary(periods){
  const first=periods[0],last=periods.at(-1),result={opening:first?.opening??null,closing:last?.closing??null,reference:last?.reference??null,projected:last?.projected??null,references:last?.references||[],projectionDelta:last?.projectionDelta||0,excluded:last?.excluded||0,complete:periods.length>0&&periods.every(p=>p.complete)};
  for(const key of ['incoming','outgoing','movement','dueIn','dueOut','pendingIn','pendingOut','forecastIn','forecastOut'])result[key]=periods.reduce((n,p)=>n+p[key],0);
  for(const key of ['transactions','obligations','tasks','forecasts'])result[key]=periods.flatMap(p=>p[key]);
  result.start=first?.start;result.end=last?.end;return result;
}
