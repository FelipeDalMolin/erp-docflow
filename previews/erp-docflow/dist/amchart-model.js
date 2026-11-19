import {moveDate} from './range-model.js?v=18';
import {reportedBankPositions} from './bank-position-model.js?v=18';
import {summarizeSignedFlows} from './signed-flow-model.js?v=18';
export const DAY_MS=86400000;
export const dateStamp=date=>Date.parse(date+'T00:00:00Z');

// The bar, its count and its drill-down share the same inclusion rule.
export function chartBarTransactions(data,selection,basis='reported'){
  if(!selection||!['incoming','outgoing'].includes(selection.direction))return [];
  return data.transactions.filter(t=>t.date===selection.date&&(!selection.account||t.account===selection.account)
    &&(basis!=='reported'||t.movementType!=='investment-transfer')
    &&(selection.direction==='incoming'?t.amount>0:t.amount<0));
}
function movementCounts(transactions,basis){
  const included=transactions.filter(t=>basis!=='reported'||t.movementType!=='investment-transfer');
  return {incomingCount:included.filter(t=>t.amount>0).length,outgoingCount:included.filter(t=>t.amount<0).length};
}

export function chartDays(data,range,basis='reported'){
  const reported=new Map(reportedBankPositions(data,range).map(p=>[p.date,p]));
  const closePoints=data.points.filter(p=>!p.opening&&!p.transaction);
  const automaticIncluded=data.accounts.some(a=>a.statement?.balanceBasis==='consolidated');
  const days=[];let cash=data.points[0],index=0;
  for(let date=range.start;date<=range.end;date=moveDate(date,1)){
    const ledgerOpening=cash.total;
    while(index<closePoints.length&&closePoints[index].date<=date)cash=closePoints[index++];
    const tx=data.transactions.filter(t=>t.date===date),flow=summarizeSignedFlows(tx,basis==='reported');
    let position=reported.get(date);
    // The consolidated ledger covers quiet days too; separate investment snapshots
    // are never carried across dates without an observed position.
    if(basis==='reported'&&!position&&automaticIncluded){
      const values=data.accounts.map((a,i)=>({account:a.id,identified:cash.balances[i],complete:a.statement?.balanceBasis==='consolidated'}));
      position={total:cash.total,balances:cash.balances,partial:values.some(p=>!p.complete),positions:values};
    }
    const balance=basis==='reported'?position?.total??null:cash.total;
    const bankFlows=data.accounts.map(account=>{const movements=tx.filter(t=>t.account===account.id);return {account:account.id,...summarizeSignedFlows(movements,basis==='reported'),...movementCounts(movements,basis)};});
    days.push({date,timestamp:dateStamp(date),incoming:flow.incoming,outgoing:flow.outgoing,...movementCounts(tx,basis),net:flow.net,balance,partial:basis==='reported'&&(!position||position.partial),banks:basis==='reported'?position?.balances??null:cash.balances,bankFlows,count:tx.length,internalCount:flow.internalCount,ledgerOpening,ledgerBalance:cash.total,excludedTransfers:basis==='reported'?flow.internalIn+flow.internalOut:0});
  }
  return days;
}

export function chartRangeResult(rows,range){
  const selected=rows.filter(row=>row.date>=range.start&&row.date<=range.end);
  return {incoming:selected.reduce((n,r)=>n+r.incoming,0),outgoing:selected.reduce((n,r)=>n+r.outgoing,0),net:selected.reduce((n,r)=>n+r.net,0),opening:selected[0]?.ledgerOpening??null,closing:selected.at(-1)?.ledgerBalance??null,balance:selected.at(-1)?.balance??null,partial:selected.at(-1)?.partial??true,excludedTransfers:selected.reduce((n,r)=>n+r.excludedTransfers,0),count:selected.reduce((n,r)=>n+r.count,0)};
}

// amCharts reports zoom endpoints in milliseconds. Include touched calendar days,
// with an exclusive right endpoint, and clamp to statement coverage.
export function zoomDateRange(min,max,range){
  if(!Number.isFinite(min)||!Number.isFinite(max)||max<=min)return null;
  const lower=dateStamp(range.start),upper=dateStamp(range.end)+DAY_MS;
  if(max<=lower||min>=upper)return null;
  const start=Math.max(lower,Math.floor(min/DAY_MS)*DAY_MS),end=Math.min(upper-DAY_MS,Math.ceil(max/DAY_MS)*DAY_MS-DAY_MS);
  return {start:new Date(start).toISOString().slice(0,10),end:new Date(Math.max(start,end)).toISOString().slice(0,10)};
}
