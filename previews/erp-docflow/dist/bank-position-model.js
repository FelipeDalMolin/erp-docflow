// Combine only same-date statement observations. Missing investment balances stay null.
// An application/rescue is a transfer: it is never added again to investment snapshots.
export function reportedBankPositions(data,range){
  const consolidated=data.accounts.some(a=>a.statement?.balanceBasis==='consolidated');
  const dates=[...new Set(consolidated?data.points.filter(p=>!p.opening&&!p.transaction).map(p=>p.date):data.accounts.flatMap(a=>(a.statement?.investments||[]).map(p=>p.date)))].filter(date=>date>=range.start&&date<=range.end).sort();
  return dates.map(date=>{
    const cash=data.points.findLast(p=>!p.opening&&!p.transaction&&p.date<=date)||data.points[0];
    const positions=data.accounts.map((account,i)=>{
      const investment=account.statement?.investments.find(p=>p.date===date);
      if(account.statement?.balanceBasis==='consolidated'){
        const source=data.points.findLast(p=>p.date<=date&&p.transaction?.account===account.id)?.transaction||data.openingSources?.[i];
        return {account:account.id,cash:null,investment:investment?.amount??null,consolidated:true,complete:true,sourcePage:source?.sourcePage||1,sourceDocument:source?.sourceDocument||account.statement.document,identified:cash.balances[i]};
      }
      return {account:account.id,cash:cash.balances[i],investment:investment?.amount??null,complete:investment!==undefined,sourcePage:investment?.sourcePage??null,sourceDocument:investment?.sourceDocument||account.statement?.document,identified:cash.balances[i]+(investment?.amount??0)};
    });
    const balances=positions.map(p=>p.identified),total=balances.reduce((n,v)=>n+v,0);
    return {date,positions,balances,total,projected:total,partial:positions.some(p=>!p.complete)};
  });
}
