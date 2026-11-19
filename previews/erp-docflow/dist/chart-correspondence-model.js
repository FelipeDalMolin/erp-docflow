import {obligationDocuments} from './inventory-model.js?v=17';

// Resolve only existing relationships in the selected company, never similarities.
export function chartMovementReferences(state,transaction,company){
  const owned=(collection,id)=>id?(state[collection]?.find(x=>x.id===id&&x.company===company)||null):null;
  if(transaction.company!==company)return {source:null,obligation:null,contract:null,asset:null,documents:[]};
  const obligation=owned('obligations',transaction.obligation);
  const contract=owned('contracts',transaction.contract||obligation?.contract);
  const asset=owned('assets',transaction.asset||obligation?.asset||contract?.asset);
  const source=owned('documents',transaction.sourceDocument);
  const documents=obligation?obligationDocuments(state,obligation).filter(d=>d.id!==source?.id):[];
  return {source,obligation,contract,asset,documents};
}
