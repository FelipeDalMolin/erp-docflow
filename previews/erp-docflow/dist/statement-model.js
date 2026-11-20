export function statementCoverage(state,company,selection='all'){
  const ids=Array.isArray(selection)?selection:selection==='all'?null:[selection];
  const periods=state.accounts.filter(a=>a.company===company&&a.statement&&(!ids||ids.includes(a.id))).map(a=>a.statement.period);
  return periods.length?{start:periods.map(p=>p.start).sort().at(-1),end:periods.map(p=>p.end).sort()[0]}:null;
}
export function statementCovers(state,company,start,end=start,selection='all'){const r=statementCoverage(state,company,selection);return !r||(start>=r.start&&end<=r.end);}
export function fitStatementRange(state,company,range,selection='all'){const r=statementCoverage(state,company,selection);if(!r)return {...range};const start=range.start>r.start?range.start:r.start,end=range.end<r.end?range.end:r.end;return start<=end?{start,end}:null;}
export function statementOrder(a,b){return a.date.localeCompare(b.date)||(a.account||'').localeCompare(b.account||'')||((a.sourceSequence??0)-(b.sourceSequence??0))||a.id.localeCompare(b.id);}
export function validateImportedStatements(state){
  return state.accounts.filter(a=>a.statement).map(a=>{
    const tx=state.transactions.filter(t=>t.account===a.id&&t.company===a.company&&t.imported).sort((a,b)=>a.sourceSequence-b.sourceSequence);
    let balance=a.opening,incoming=0,outgoing=0,printed=0;const errors=[];
    tx.forEach((t,i)=>{balance+=t.amount;if(t.amount>0)incoming+=t.amount;else outgoing-=t.amount;
      if(!Number.isSafeInteger(t.amount)||t.sourceSequence!==i+1||balance!==t.balance)errors.push(t.id);
      if(t.reportedBalance!==null){printed++;if(balance!==t.reportedBalance)errors.push(t.id);}
    });
    if(balance!==a.statement.closing||incoming!==a.statement.incoming||outgoing!==a.statement.outgoing||tx.length!==a.statement.transactionCount)errors.push('totals');
    return {account:a.id,count:tx.length,opening:a.opening,closing:balance,incoming,outgoing,printed,errors};
  });
}
