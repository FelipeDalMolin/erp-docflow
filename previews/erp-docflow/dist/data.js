// Public bootstrap: no imported records or account identifiers.
export const MONTHS = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
export const SEED = {
  "dataset": {
    "id": "public-preview-empty-v1",
    "kind": "empty",
    "defaultMonth": "2026-11",
    "defaultDate": "2026-11-19",
    "notice": "Prévia de código · sem dados financeiros",
    "transactionCount": 0
  },
  "companies": [
    {
      "id": "example",
      "name": "Empresa de exemplo",
      "short": "EX",
      "activity": "A preencher",
      "city": "",
      "color": "green"
    }
  ],
  "accounts": [],
  "transactions": [],
  "archivedTransactions": [],
  "assets": [],
  "contracts": [],
  "obligations": [],
  "documents": [],
  "tasks": [],
  "reviewed": []
};
export const total = o => o.items.reduce((n,i)=>n+i.amount,0);
export const paid = (state,o) => state.transactions.filter(t=>t.obligation===o.id).reduce((n,t)=>n+Math.abs(t.amount),0);
export const remaining = (state,o) => Math.max(0,total(o)-paid(state,o));
export function figures(state,company,month,account='all') {
  const accounts=state.accounts.filter(a=>a.company===company&&(account==='all'||a.id===account));
  const ids=new Set(accounts.map(a=>a.id));
  const tx=state.transactions.filter(t=>ids.has(t.account));
  const current=tx.filter(t=>t.date.slice(0,7)===month);
  const opening=accounts.reduce((n,a)=>n+a.opening,0)+tx.filter(t=>t.date.slice(0,7)<month).reduce((n,t)=>n+t.amount,0);
  const incoming=current.filter(t=>t.amount>0).reduce((n,t)=>n+t.amount,0),outgoing=-current.filter(t=>t.amount<0).reduce((n,t)=>n+t.amount,0);
  const obs=state.obligations.filter(o=>o.company===company&&o.due.slice(0,7)===month&&ids.has(o.account));
  const toReceive=obs.filter(o=>o.kind==='in').reduce((n,o)=>n+remaining(state,o),0),toPay=obs.filter(o=>o.kind==='out').reduce((n,o)=>n+remaining(state,o),0);
  return {opening,incoming,outgoing,balance:opening+incoming-outgoing,toReceive,toPay,projected:opening+incoming-outgoing+toReceive-toPay,current,obs};
}
