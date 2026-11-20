import {INITIAL_CLASSIFICATION as batch} from './classification-initial-data.js?v=29';
import {classificationStore,classificationCatalog,getClassification,classificationStatus} from './classification-model.js?v=29';

const decisions=new Map(batch.decisions.map(row=>[row[0],row]));
export const INITIAL_BATCH=batch;
export function initialDecision(t){
  const row=decisions.get(t.id);
  if(!row||row[1]!==t.date||row[2]!==t.amount||row[3]!==t.account||row[5]!==t.description||t.archiveReason)return null;
  return {...batch.rules[row[4]],rule:row[4],batch:batch.id};
}
export function applyInitialClassifications(state){
  const store=classificationStore(state);store.initialBatches??={};
  const log=store.initialBatches[batch.id]??={applied:[],preserved:[],skipped:[]};
  const handled=new Set([...log.applied,...log.preserved]);
  let applied=0;
  for(const t of state.transactions){
    const decision=initialDecision(t),account=state.accounts.find(a=>a.id===t.account);
    if(!decision?.category||account?.company!==batch.company||handled.has(t.id))continue;
    if(store.records[t.id]){log.preserved.push(t.id);continue;}
    const catalog=classificationCatalog(state,batch.company);
    if(!catalog.some(c=>c.id===decision.category&&c.active))continue;
    const provenance={batch:batch.id,rule:decision.rule,confidence:decision.confidence,reason:decision.reason,review:decision.review,source:batch.source,sourceDocument:t.sourceDocument,sourceRecord:t.sourceRecord||t.sourcePage,bankDescription:t.description};
    store.records[t.id]={company:batch.company,transaction:t.id,bankAmount:t.amount,bankDate:t.date,bankAccount:t.account,status:'initial',party:'',complement:'',updatedAt:batch.createdAt,revision:1,history:[],provenance,
      lines:[{id:'initial-'+t.id,amount:Math.abs(t.amount),category:decision.category,purpose:decision.purpose,belongsTo:batch.company,competence:'',costCenter:'',asset:'',contract:'',obligation:'',parcel:'',note:decision.review,documents:[]}]};
    log.applied.push(t.id);applied++;
  }
  return applied;
}
export function initialBatchSummary(state,company){
  const tx=state.transactions.filter(t=>state.accounts.some(a=>a.id===t.account&&a.company===company)&&initialDecision(t));
  return {total:tx.length,initial:tx.filter(t=>classificationStatus(state,company,t)==='initial').length,pending:tx.filter(t=>!getClassification(state,company,t.id)).length,edited:tx.filter(t=>getClassification(state,company,t.id)&&classificationStatus(state,company,t)!=='initial').length};
}
