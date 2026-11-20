// Refresh imported data while retaining browser-local work and stable references.
export function mergeImportedState(previous,seed){
  if(!previous?.companies)return structuredClone(seed);
  if(previous.dataset?.id===seed.dataset?.id)return previous;
  const state=structuredClone(previous);
  const mergeList=(type,merge=(fresh,old)=>({...fresh,...old}))=>{
    const old=new Map((previous[type]||[]).map(x=>[x.id,x]));
    return [...seed[type].map(fresh=>merge(structuredClone(fresh),old.get(fresh.id)||{})),...(previous[type]||[]).filter(x=>!seed[type].some(n=>n.id===x.id))];
  };
  state.companies=mergeList('companies');
  state.accounts=mergeList('accounts',(fresh,old)=>({...fresh,...old,opening:fresh.opening,statement:fresh.statement}));
  state.documents=mergeList('documents',(fresh,old)=>({...fresh,...old,originalUrl:fresh.originalUrl,sha256:fresh.sha256,pages:fresh.pages,period:fresh.period,format:fresh.format}));
  const prior=new Map([...(previous.transactions||[]),...(previous.archivedTransactions||[])].map(t=>[t.id,t]));
  const retainWork=t=>{const old=prior.get(t.id)||{};return {...old,...structuredClone(t),confirmed:old.confirmed??t.confirmed,...(old.obligation?{obligation:old.obligation}:{}),...(old.category?{category:old.category}:{})};};
  const canonicalIds=new Set([...seed.transactions,...(seed.archivedTransactions||[])].map(t=>t.id));
  state.transactions=[...seed.transactions.map(retainWork),...(previous.transactions||[]).filter(t=>!canonicalIds.has(t.id))];
  state.archivedTransactions=[...(seed.archivedTransactions||[]).map(retainWork),...(previous.archivedTransactions||[]).filter(t=>!canonicalIds.has(t.id))];
  state.dataset=structuredClone(seed.dataset);
  return state;
}
