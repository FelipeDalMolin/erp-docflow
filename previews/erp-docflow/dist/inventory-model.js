// References are resolved from their original records, never from file names.
export const ENTITY_TYPES={company:'Empresa',asset:'Ativo',contract:'Contrato',obligation:'Obrigação / lançamento'};
export const COLLECTIONS={company:'companies',asset:'assets',contract:'contracts',obligation:'obligations'};
export const PURPOSES={documentation:'Documentação cadastral',support:'Documento da operação'};
export const ATTRIBUTE_MODELS={
  'Imóvel':['Endereço / localização','Matrícula / identificação','Área','Uso / destinação'],
  'Veículo':['Marca / modelo','Ano','Placa / identificação','Uso / destinação'],
  'Equipamento':['Fabricante / modelo','Número de série','Localização','Uso / destinação'],
  'Outro':['Identificação','Localização','Uso / destinação']
};
export function entity(state,kind,id,company){
  const item=state[COLLECTIONS[kind]]?.find(x=>x.id===id);
  return item&&(kind==='company'?item.id===company:item.company===company)?item:null;
}
export function obligationAsset(state,o){return o.asset||state.contracts.find(c=>c.id===o.contract&&c.company===o.company)?.asset;}
export function referenceKey(r){return [r.kind,r.id,r.purpose].join(':');}
export function addReference(state,doc,{kind,id,purpose='support',note=''}){
  if(!entity(state,kind,id,doc.company))throw Error('Escolha uma referência desta empresa.');
  if(kind==='obligation')purpose='support';
  if(!PURPOSES[purpose])throw Error('Escolha a finalidade do documento.');
  doc.references??=[];
  const reference={kind,id,purpose,note};
  const existing=doc.references.find(r=>referenceKey(r)===referenceKey(reference));
  if(existing){existing.note=note;return existing;}
  doc.references.push(reference);return reference;
}
export function documentReferences(state,doc){
  const company=doc.company,refs=new Map();
  const add=(kind,id,purpose,direct,via,note='')=>{
    const record=entity(state,kind,id,company);if(!record)return;
    const key=referenceKey({kind,id,purpose});
    const label=(record.name||record.title)+(kind==='obligation'&&record.competence?' · '+record.competence.slice(5)+'/'+record.competence.slice(0,4):'');
    if(!refs.has(key))refs.set(key,{kind,id,purpose,label,direct:false,via:[],notes:[]});
    const ref=refs.get(key);ref.direct ||= direct;
    if(via&&!ref.via.includes(via))ref.via.push(via);
    if(note&&!ref.notes.includes(note))ref.notes.push(note);
  };
  const docPurpose=doc.assetPurpose||(/contrato|cadastro|matrícula|registro|certidão|licença|apólice|institucional/i.test(doc.type)?'documentation':'support');
  if(doc.profileCompany)add('company',doc.profileCompany,'documentation',true,'Perfil da empresa');
  if(doc.asset)add('asset',doc.asset,docPurpose,true,'Vínculo registrado no documento');
  if(doc.contract)add('contract',doc.contract,/contrato/i.test(doc.type)?'documentation':'support',true,'Vínculo registrado no documento');
  for(const ref of doc.references||[])add(ref.kind,ref.id,ref.purpose,true,'Referência informada',ref.note);
  for(const c of state.contracts.filter(c=>c.company===company&&c.doc===doc.id))add('contract',c.id,'documentation',true,'Documento de origem do contrato');
  for(const asset of state.assets.filter(x=>x.company===company))for(const req of asset.dossier?.requirements||[]){
    if(req.doc===doc.id)add('asset',asset.id,'documentation',true,'Documentação esperada: '+req.title);
  }
  for(const o of state.obligations.filter(o=>o.company===company)){
    if(o.id===doc.obligation||(o.docs||[]).includes(doc.id))add('obligation',o.id,'support',true,'Documento de suporte da obrigação');
    for(const item of o.items||[])if(item.doc===doc.id)add('obligation',o.id,'support',true,'Origem do componente: '+item.name);
  }
  // Carry context through explicit relationships; a related asset is not its cadastral documentation.
  for(const ref of [...refs.values()].filter(r=>r.kind==='obligation')){
    const o=entity(state,'obligation',ref.id,company);if(!o)continue;
    if(o.contract)add('contract',o.contract,'support',false,'Via '+o.title+' · '+o.competence);
    if(obligationAsset(state,o))add('asset',obligationAsset(state,o),'support',false,'Via '+o.title+' · '+o.competence);
  }
  for(const ref of [...refs.values()].filter(r=>r.kind==='contract')){
    const c=entity(state,'contract',ref.id,company);if(c?.asset)add('asset',c.asset,ref.purpose,false,'Via '+c.title);
  }
  return [...refs.values()];
}
export function assetDocuments(state,asset,purpose){
  return state.documents.filter(d=>d.company===asset.company&&documentReferences(state,d).some(r=>r.kind==='asset'&&r.id===asset.id&&(!purpose||r.purpose===purpose)));
}
export function obligationDocuments(state,o){return state.documents.filter(d=>d.company===o.company&&documentReferences(state,d).some(r=>r.kind==='obligation'&&r.id===o.id));}
export function assetObligations(state,asset){return state.obligations.filter(o=>o.company===asset.company&&obligationAsset(state,o)===asset.id);}
export function assetTasks(state,asset){
  const obs=new Set(assetObligations(state,asset).map(o=>o.id)),docs=new Set(assetDocuments(state,asset).map(d=>d.id));
  return state.tasks.filter(t=>t.company===asset.company&&(t.asset===asset.id||obs.has(t.obligation)||docs.has(t.doc)||state.contracts.some(c=>c.company===asset.company&&c.asset===asset.id&&c.id===t.contract)));
}
export function requirementStatus(state,req,now){
  const d=state.documents.find(d=>d.id===req.doc);
  if(!d)return {label:'Falta documento',tone:'amber'};
  if(req.validUntil&&req.validUntil<now)return {label:'Prazo informado vencido',tone:'red'};
  if(d.locked)return {label:'Aguardando senha',tone:'amber'};
  if(d.status!=='Revisado')return {label:'A conferir',tone:'amber'};
  return {label:'Documento conferido',tone:'green'};
}
export function assetFields(kind,asset={}){
  return (ATTRIBUTE_MODELS[kind]||ATTRIBUTE_MODELS.Outro).map(label=>({label,value:label==='Área'?asset.area||'':label==='Uso / destinação'?asset.description||'':''}));
}
export function adaptAssetFields(fields,kind,previousKind){
  const suggested=assetFields(kind),old=ATTRIBUTE_MODELS[previousKind]||ATTRIBUTE_MODELS.Outro;
  const kept=fields.filter(f=>f.value.trim()||suggested.some(x=>x.label===f.label)||!old.includes(f.label));
  for(const f of suggested)if(!kept.some(x=>x.label===f.label))kept.push(f);
  return kept;
}
export function ensureInventory(state){
  for(const asset of state.assets){
    asset.dossier??={attributes:assetFields(asset.kind,asset),requirements:[]};
    asset.dossier.attributes??=[];asset.dossier.requirements??=[];
  }
  if(state.inventoryVersion>=1)return state;
  const examples=[
    {asset:'a204',id:'asset-a204-identification',name:'Identificação do imóvel · Sala 204',type:'Cadastro do imóvel',status:'Revisado',title:'Identificação do imóvel',lines:['Sala 204 · Edifício Aurora.','Área cadastrada no exemplo: 80 m².','Matrícula e inscrição: a informar.','Ficha fictícia, sem valor de certidão ou comprovação de propriedade.']},
    {asset:'acar',id:'asset-acar-identification',name:'Identificação do veículo · exemplo',type:'Cadastro do veículo',status:'A revisar',title:'Identificação do veículo',lines:['Veículo utilitário de apoio à operação.','Placa, registro e ano: a complementar.','Vínculo informado: propriedade financiada.','Ficha fictícia, sem valor de documento oficial.']}
  ];
  for(const x of examples){
    const asset=state.assets.find(a=>a.id===x.asset);if(!asset)continue;
    if(!state.documents.some(d=>d.id===x.id))state.documents.push({id:x.id,company:asset.company,name:x.name,type:x.type,status:x.status,date:'2026-07-01',source:'Exemplo de documentação do ativo',references:[{kind:'asset',id:asset.id,purpose:'documentation',note:'Ficha ilustrativa do cadastro.'}],pages:[{title:x.title,subtitle:'Documento fictício · prévia',lines:x.lines}]});
    if(!asset.dossier.requirements.length)asset.dossier.requirements=[{id:x.id+'-req',title:'Ficha de identificação',doc:x.id,validUntil:''},{id:x.id+'-ownership',title:'Comprovação do vínculo com a empresa',doc:'',validUntil:''}];
  }
  state.inventoryVersion=1;return state;
}
