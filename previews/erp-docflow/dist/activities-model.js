import {controlItems} from './control-model.js?v=23';
import {controlContext} from './control-context.js?v=24';
import {planningRemaining} from './planning-book-model.js?v=31';
import {validDate} from './range-model.js?v=17';

// One shared record per activity: displaying it here does not create an obligation.
export function activityItems(state,company,today){
  const all=controlItems(state,company,today),tasks=state.tasks.filter(t=>t.company===company);
  return all.filter(item=>item.kind!=='coverage').map(item=>{
    const context=controlContext(state,item,all),record=context.record;
    const type=item.kind==='obligation'&&record?.monitoringKind==='estimate'?'forecast':item.kind;
    const parent=record?.obligation?state.obligations.find(o=>o.company===company&&o.id===record.obligation):null;
    const parentForecast=record?.forecast?all.find(f=>f.kind==='forecast'&&f.id===record.forecast):null;
    if(parentForecast)for(const id of parentForecast.accounts||[]){const bank=state.accounts.find(b=>b.company===company&&b.id===id);if(bank&&!context.banks.some(b=>b.id===id))context.banks.push({id:bank.id,name:bank.name,label:bank.label});}
    const direction=item.kind==='forecast'?item.direction:item.kind==='obligation'?(record.kind==='in'?1:-1):parent?(parent.kind==='in'?1:-1):parentForecast?.direction||0;
    const linkedTasks=item.kind==='task'?[]:tasks.filter(t=>t.controlSource===item.id||(item.kind==='obligation'&&t.obligation===item.target)||(item.kind==='forecast'&&t.forecast===item.target));
    return {...item,type,context,direction,linkedTasks,
      balance:item.kind==='obligation'?planningRemaining(state,record):null,
      origin:item.kind==='obligation'?(type==='forecast'?'Previsão cadastrada':'Compromisso cadastrado'):context.origin,
      date:validDate(item.date)?item.date:null};
  });
}
const normalize=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export function selectActivities(items,{start,end,type='all',direction='all',account='all',status='active',search=''}={}){
  const term=normalize(search);
  const scoped=items.filter(i=>{
    if(direction!=='all'&&i.direction!==(direction==='in'?1:-1))return false;
    if(account!=='all'&&!i.context.banks.some(b=>b.id===account))return false;
    if(status==='active'&&(i.group==='resolved'||i.hidden))return false;
    if(status==='resolved'&&i.group!=='resolved')return false;
    if(status==='attention'&&!['overdue','deviation','verify'].includes(i.group))return false;
    if(status==='overdue'&&i.group!=='overdue')return false;
    return !term||normalize([i.title,i.owner,i.label,i.context.record?.party,...i.context.direct.map(r=>r.label),...i.context.banks.map(b=>b.name)].join(' ')).includes(term);
  });
  const inRange=i=>i.date&&(!start||i.date>=start)&&(!end||i.date<=end);
  const counts={all:0,obligation:0,forecast:0,task:0};
  for(const i of scoped.filter(inRange)){counts.all++;counts[i.type]++;}
  const filtered=scoped.filter(i=>type==='all'||i.type===type);
  const sort=rows=>rows.sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999')||a.title.localeCompare(b.title,'pt-BR')||a.id.localeCompare(b.id));
  const rows=sort(filtered.filter(inRange)),prior=sort(filtered.filter(i=>start&&i.date&&i.date<start&&i.group!=='resolved'&&!i.hidden)),undated=sort(filtered.filter(i=>!i.date));
  const commitments=rows.filter(i=>i.type==='obligation');
  return {rows,prior,undated,counts,summary:{incoming:commitments.filter(i=>i.direction>0).reduce((n,i)=>n+i.balance,0),outgoing:commitments.filter(i=>i.direction<0).reduce((n,i)=>n+i.balance,0),forecasts:rows.filter(i=>i.type==='forecast').length,tasks:rows.filter(i=>i.type==='task').length}};
}
export function activityGroups(rows){
  const groups=new Map();for(const row of rows){const key=row.date||'undated';if(!groups.has(key))groups.set(key,{date:row.date,items:[]});groups.get(key).items.push(row);}return [...groups.values()];
}
