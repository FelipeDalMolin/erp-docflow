// Configuration only. No browser-to-bank requests or credential storage.
export const RESEARCH_DATE='2026-11-12';
const bradDocs='https://developers.bradesco.com.br/productDetails/8a2e88539549335b01954cccc83e136d/version/2377491905f04d2592cc863bccd38ca1/docs';
export const BANKS={
  '237':{name:'Bradesco',short:'BR',product:'Saldo e extrato',version:'Manual 2.2.2 · API v1',source:bradDocs+'/viewer/b8117d2f94f24a94adf018d7a9940854/0',authSource:bradDocs+'/viewer/245ebea1aacb45e885851c914c5b08f9/0',types:['checking','savings'],maxRecords:5000,historyYears:10,credentials:['clientIdRef','clientSecretRef','certificateRef'],bases:{sandbox:'https://openapisandbox.prebanco.com.br',production:'https://openapi.bradesco.com.br'},tokenPath:'/auth/server-mtls/v2/token',statementPath:'/v1/fornecimento-extratos-contas/extratos',balancePath:'/v1/fornecimento-saldos-contas/saldos',scope:''},
  '001':{name:'Banco do Brasil',short:'BB',product:'API Extratos v2',version:'OpenAPI 2.0.1',source:'https://apoio.developers.bb.com.br/apis/80?topico=19587365&versaoApi=2',authSource:'https://apoio.developers.bb.com.br/apis/80?topico=19587364&versaoApi=2',types:['checking'],maxRecords:120,historyYears:5,credentials:['clientIdRef','clientSecretRef','appKeyRef','certificateRef'],bases:{sandbox:'https://extratos.mtls.api.hm.bb.com.br/v2',production:'https://extratos.mtls.api.bb.com.br/v2'},tokenUrls:{sandbox:'https://oauth.hm.bb.com.br/oauth/token',production:'https://oauth.bb.com.br/oauth/token'},statementPath:'/conta-corrente/agencia/{agencia}/conta/{conta}',scope:'extrato-info'}
};
export const MODES={file:'Arquivo do banco',api:'API do banco',openfinance:'Open Finance'};
export const CREDENTIAL_LABELS={clientIdRef:'Identificador da aplicação (Client ID)',clientSecretRef:'Segredo da aplicação (Client Secret)',appKeyRef:'Chave da aplicação (gw-dev-app-key)',certificateRef:'Certificado e chave privada (mTLS)'};
export const TYPES={checking:'Conta corrente',savings:'Poupança',payment:'Conta de pagamento'};
const environment=()=>({application:'',approval:'not-requested',clientIdRef:'',clientSecretRef:'',appKeyRef:'',certificateRef:'',certificateExpires:'',testMci:''});
export function newBanking(code=''){
  return {schema:1,bankCode:code,branch:'',branchDigit:'',number:'',digit:'',type:'checking',holderType:'PJ',holderName:'',taxId:'',currency:'BRL',mode:'file',environment:'sandbox',environments:{sandbox:environment(),production:environment()},bradesco:{operation:'1'},bb:{pageSize:120},file:{format:'OFX',encoding:'auto',separator:'auto',dateFormat:'DD/MM/AAAA',decimal:','},openfinance:{provider:'',recipient:'',consentReference:'',consentExpires:'',permissions:['accounts','balances','transactions']},sync:{frequency:'daily',time:'08:00',timezone:'America/Sao_Paulo',startDate:'',overlapDays:7,matchDays:3},documents:[]};
}
export function ensureBanking(state){
  for(const account of state.accounts){
    if(!account.banking){const n=account.name.toLowerCase();account.banking=newBanking(n.includes('bradesco')?'237':n.includes('banco do brasil')?'001':'');if(account.statement){const x=account.statement;Object.assign(account.banking,{bankCode:x.bankCode,branch:x.branch,branchDigit:x.branchDigit,number:x.number,digit:x.digit,holderName:state.companies.find(c=>c.id===account.company)?.name||'',mode:'file'});account.banking.sync.startDate=x.period.start;account.banking.documents=[x.document];}}
  }
}
export const normalizeTaxId=value=>String(value).replace(/[.\/\-\s]/g,'').toUpperCase();
export function validTaxFormat(type,value){return (type==='PJ'?/^[A-Z0-9]{12}\d{2}$/:/^\d{11}$/).test(normalizeTaxId(value))}
export const aliasValid=value=>!value||/^ref:[a-z][a-z0-9_-]{2,50}$/.test(value);
export function validateDraft(config,label){
  const c=config,errors=[];
  if(!label.trim())errors.push('Dê um nome para identificar esta conta.');
  if(!BANKS[c.bankCode])errors.push('Selecione Bradesco ou Banco do Brasil.');
  if(c.branch&&!/^\d{1,6}$/.test(c.branch))errors.push('Informe a agência sem o dígito, usando apenas números.');
  if(c.number&&!/^\d{1,20}$/.test(c.number))errors.push('Informe o número da conta sem o dígito.');
  if(!/^[A-Z0-9]{0,2}$/.test(c.digit)||!/^[A-Z0-9]{0,2}$/.test(c.branchDigit))errors.push('Confira os dígitos da agência e da conta.');
  if(c.taxId&&!validTaxFormat(c.holderType,c.taxId))errors.push('Confira o formato do CPF/CNPJ. CNPJ aceita letras nas primeiras 12 posições.');
  for(const env of Object.values(c.environments))for(const key of Object.keys(CREDENTIAL_LABELS))if(!aliasValid(env[key]))errors.push('Use somente nomes de referência, como ref:bb-teste-cliente. Não cole credenciais.');
  if(!Number.isInteger(c.bb.pageSize)||c.bb.pageSize<30||c.bb.pageSize>120)errors.push('No BB, a página deve ter entre 30 e 120 registros.');
  if(!Number.isInteger(c.sync.overlapDays)||c.sync.overlapDays<1||c.sync.overlapDays>30)errors.push('A releitura deve abranger de 1 a 30 dias.');
  if(!Number.isInteger(c.sync.matchDays)||c.sync.matchDays<0||c.sync.matchDays>30)errors.push('A janela de sugestão deve ser de 0 a 30 dias.');
  return [...new Set(errors)];
}
export function preparation(c,today=RESEARCH_DATE){
  const bank=BANKS[c.bankCode],env=c.environments[c.environment];
  const rows=[{label:'Identificação da conta e titular',ready:!!(bank&&c.branch&&c.number&&c.digit&&c.holderName&&validTaxFormat(c.holderType,c.taxId))}];
  if(c.mode==='api'){
    rows.push({label:'Modalidade atendida pela API (conta própria PJ)',ready:c.holderType==='PJ'&&!!bank?.types.includes(c.type)});
    rows.push({label:'Habilitação declarada neste ambiente',ready:env.approval==='declared'});
    rows.push({label:'Referências de credenciais preenchidas',ready:!!bank?.credentials.every(k=>env[k]&&aliasValid(env[k]))});
    rows.push({label:'Validade do certificado informada e vigente',ready:!!env.certificateExpires&&env.certificateExpires>today});
    if(c.bankCode==='001'&&c.environment==='sandbox')rows.push({label:'MCI de teste informado',ready:/^\d+$/.test(env.testMci)});
    rows.push({label:'Conector seguro e teste com o banco',ready:false,external:true});
  }else if(c.mode==='openfinance'){
    rows.push({label:'Parceiro e instituição receptora definidos',ready:!!(c.openfinance.provider&&c.openfinance.recipient)});
    rows.push({label:'Referência e prazo do consentimento informados',ready:!!c.openfinance.consentReference&&c.openfinance.consentExpires>today});
    rows.push({label:'Autorização validada pelo parceiro',ready:false,external:true});
  }else rows.push({label:'Leitor de arquivo e amostra homologados',ready:false,external:true});
  return rows;
}
export function publicConfiguration(account){
  return {notice:'Rascunho da prévia. Não conectado. Referências não são credenciais. Nenhuma rotina executada.',schemaVersion:1,researchDate:RESEARCH_DATE,company:account.company,accountId:account.id,label:account.label,configuration:structuredClone(account.banking),adapter:BANKS[account.banking.bankCode],reconciliation:{bankStatus:'pending | booked | reversed',linkStatus:'unmatched | suggested | reviewed',documentStatus:'missing | received | reviewed',amountUnit:'integer_centavos',identity:['bank','account','bankTransactionId_when_available'],fallback:'Preservar ocorrências e submeter duplicatas ambíguas à revisão; nunca deduplicar apenas por data/valor.',rawEvidence:'Preservar resposta ou arquivo original no servidor; não tratar saldo como lançamento.',paymentInitiation:false}};
}
// Executable adapter contract for a future backend. Deliberately returns no tokens.
export function statementPlan(c,start,end,page=1){
  const bank=BANKS[c.bankCode];if(!bank)throw Error('Banco não configurado.');
  if(c.holderType!=='PJ'||!bank.types.includes(c.type))throw Error('Esta modalidade não é atendida pela API pesquisada.');
  if(!/^\d+$/.test(c.branch)||!/^\d+$/.test(c.number))throw Error('Agência e conta são obrigatórias.');
  const validDate=s=>/^\d{4}-\d{2}-\d{2}$/.test(s)&&!Number.isNaN(Date.parse(s))&&new Date(s).toISOString().slice(0,10)===s;
  if(!validDate(start)||!validDate(end)||end<start)throw Error('Período inválido.');
  const days=(Date.parse(end)-Date.parse(start))/86400000+1;
  const dmy=s=>s.slice(8)+s.slice(5,7)+s.slice(0,4);
  const clean=s=>s.replace(/^0+(?=\d)/,'');
  if(c.bankCode==='001'){
    if(days>31)throw Error('Divida a consulta BB em janelas de até 31 dias.');
    if(!Number.isInteger(page)||page<1)throw Error('Página inválida.');
    if(!Number.isInteger(c.bb.pageSize)||c.bb.pageSize<30||c.bb.pageSize>120)throw Error('Tamanho de página BB inválido.');
    return {method:'GET',url:bank.bases[c.environment]+bank.statementPath.replace('{agencia}',clean(c.branch)).replace('{conta}',clean(c.number)),query:{dataInicioSolicitacao:Number(dmy(start)),dataFimSolicitacao:Number(dmy(end)),numeroPaginaSolicitacao:page,quantidadeRegistroPaginaSolicitacao:c.bb.pageSize},requiredQuerySecrets:['gw-dev-app-key'],requiredHeaders:['Authorization',...(c.environment==='sandbox'?['x-br-com-bb-ipa-mciteste']:[])],scope:bank.scope,mutualTLS:true};
  }
  if(c.branch.length>4||c.number.length>7)throw Error('Confira agência (até 4) e conta (até 7 dígitos) no Bradesco.');
  if(days>366)throw Error('Divida a consulta Bradesco em períodos de até um ano.');
  return {method:'GET',url:bank.bases[c.environment]+bank.statementPath,query:{agencia:c.branch,conta:c.number,dataInicio:dmy(start),dataFim:dmy(end),tipo:c.type==='savings'?'cp':'cc',tipoOperacao:Number(c.bradesco.operation)},requiredHeaders:['Authorization'],mutualTLS:true,maxRecords:5000,onRecordLimit:'Interromper e subdividir o período; nunca considerar 5.000 registros como extrato completo.'};
}
