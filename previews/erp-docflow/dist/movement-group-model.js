import {classificationStatus,getClassification} from './classification-model.js?v=29';

const clean=value=>typeof value==='string'?value.trim().replace(/\s+/g,' '):'';
const normal=value=>clean(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase();

// Bank-operation labels describe the statement; they do not classify its accounting nature.
export function movementTypeLabel(t){
  if(t.movementType==='investment-transfer')return t.amount<0?'Aplicação automática':'Resgate automático';
  const label=clean(t.history),key=normal(label);
  if(/TARIFA/.test(key))return 'Tarifas bancárias';
  if(/PIX.*ENVIADO/.test(key))return 'Pix enviado';
  if(/PIX.*RECEBIDO/.test(key))return 'Pix recebido';
  if(key==='PIX')return t.amount<0?'Pix enviado':'Pix recebido';
  if(/RENTAB.*INVEST|RENDIMENT/.test(key))return 'Rendimentos de aplicação';
  if(/PAGTO.*TRIBUTO/.test(key)||key==='IMPOSTOS')return 'Pagamento de tributos';
  if(/PAGTO.*COBRANCA/.test(key)||key==='PAGAMENTO DE BOLETO')return 'Pagamento de cobrança';
  if(/CONTA (DE )?LUZ/.test(key))return 'Conta de energia';
  if(/CONTA (DE )?AGUA/.test(key))return 'Conta de água e esgoto';
  return label||'Tipo não informado';
}

export function movementCategoryLabel(t,state){
  const company=t.company||(state.accounts||[]).find(a=>a.id===t.account)?.company;
  const composition=state.classification&&getClassification(state,company,t.id);
  if(composition){
    const status=classificationStatus(state,company,t);
    if(!['reviewed','initial'].includes(status))return 'Classificação em rascunho';
    const catalog=state.classification.catalogs[company]||[];
    const categories=new Set(composition.lines.map(l=>catalog.find(c=>c.id===l.category)?.label||'Classificação indisponível'));
    return (categories.size===1?[...categories][0]:'Composição mista · '+categories.size+' classificações')+(status==='initial'?' · inicial':'');
  }
  const direct=clean(t.category);if(direct)return direct;
  const obligation=t.confirmed&&(state.obligations||[]).find(o=>o.id===t.obligation&&o.company===t.company);
  const items=obligation?.items||[];
  if(!items.length||items.some(item=>!clean(item.nature)))return 'Sem categoria';
  const categories=new Map(items.map(item=>[normal(item.nature),clean(item.nature)]));
  return categories.size===1?[...categories.values()][0]:'Composição mista · a detalhar';
}

// The bank list keeps each transaction once. Split amounts are shown in the classification summary.
export function groupMovements(transactions,state,mode='type'){
  const groups=new Map();
  for(const t of transactions){
    const label=mode==='category'?movementCategoryLabel(t,state):movementTypeLabel(t),key=mode+':'+normal(label);
    if(!groups.has(key))groups.set(key,{key,label,transactions:[],incoming:0,outgoing:0,net:0,gross:0});
    const group=groups.get(key);group.transactions.push(t);group.net+=t.amount;group.gross+=Math.abs(t.amount);
    if(t.amount>0)group.incoming+=t.amount;else group.outgoing-=t.amount;
  }
  return [...groups.values()].sort((a,b)=>b.gross-a.gross||a.label.localeCompare(b.label,'pt-BR'));
}
