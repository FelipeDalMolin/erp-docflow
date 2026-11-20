// Entirely fictional test data from the original concept; never loaded by the public app.
export const SEED = {
  companies:[
    {id:'aurora',name:'Aurora Participações',short:'AP',activity:'Locação e gestão patrimonial',city:'Campinas · SP',color:'green'},
    {id:'horizonte',name:'Horizonte Serviços',short:'HS',activity:'Serviços e consultoria',city:'São Paulo · SP',color:'blue'}
  ],
  accounts:[{id:'bradesco',company:'aurora',name:'Bradesco',label:'Conta principal',opening:1250000},{id:'bb',company:'aurora',name:'Banco do Brasil',label:'Recebimentos',opening:595000},{id:'hs',company:'horizonte',name:'Bradesco',label:'Conta operacional',opening:720000}],
  assets:[
    {id:'a204',company:'aurora',name:'Sala 204',kind:'Imóvel',description:'Edifício Aurora · 2º andar',area:'80 m²',relationship:'Propriedade',status:'Locado',contract:'c204',details:'Participação de 20% no consumo compartilhado de água.'},
    {id:'a105',company:'aurora',name:'Sala 105',kind:'Imóvel',description:'Edifício Aurora · 1º andar',area:'60 m²',relationship:'Propriedade',status:'Locado',contract:'c105',details:'Manutenção elétrica realizada em julho. A documentação está pendente.'},
    {id:'aloja',company:'aurora',name:'Loja 01',kind:'Imóvel',description:'Galeria Jardim · térreo',area:'120 m²',relationship:'Propriedade',status:'Locado',contract:'cloja',details:'Vencimento do aluguel no dia 25.'},
    {id:'acar',company:'aurora',name:'Veículo utilitário',kind:'Veículo',description:'Veículo de apoio à operação',area:'Parcela 17 de 48',relationship:'Propriedade financiada',status:'Em uso',details:'Prestação de exemplo: R$ 1.080 de principal e R$ 120 de juros.'},
    {id:'hdesk',company:'horizonte',name:'Escritório central',kind:'Imóvel',description:'Unidade administrativa',area:'45 m²',relationship:'Locação',status:'Em uso',details:'Espaço de trabalho da equipe de serviços.'}
  ],
  contracts:[
    {id:'c204',company:'aurora',title:'Locação · Sala 204',party:'Marina Studio',asset:'a204',start:'2026-01-01',end:'2027-12-31',base:300000,due:5,number:'LOC-024',rule:'Aluguel mensal + água por participação de 20% + encargo fixo de R$ 180.',revision:'Regra 1 · vigente desde 01/01/2026',doc:'dcontract'},
    {id:'c105',company:'aurora',title:'Locação · Sala 105',party:'Ateliê Luna',asset:'a105',start:'2026-03-01',end:'2028-02-29',base:240000,due:15,number:'LOC-025',rule:'Aluguel mensal fixo. Recebimentos parciais mantêm o saldo da parcela.',revision:'Regra 1 · vigente desde 01/03/2026'},
    {id:'cloja',company:'aurora',title:'Locação · Loja 01',party:'Livraria Vereda',asset:'aloja',start:'2026-02-01',end:'2027-01-31',base:420000,due:25,number:'LOC-026',rule:'Aluguel mensal, com revisão prevista ao fim da vigência.',revision:'Regra 1 · vigente desde 01/02/2026'},
    {id:'ch',company:'horizonte',title:'Consultoria mensal',party:'Estúdio Horizonte',asset:'hdesk',start:'2026-05-01',end:'2027-04-30',base:890000,due:10,number:'SER-008',rule:'Mensalidade pelos serviços do período.',revision:'Regra 1 · vigente desde 01/05/2026'}
  ],
  obligations:[
    {id:'o204',company:'aurora',title:'Aluguel e encargos · Sala 204',party:'Marina Studio',kind:'in',due:'2026-07-05',competence:'2026-07',contract:'c204',asset:'a204',account:'bb',docs:['dcharge','dreceipt'],items:[{name:'Aluguel · parcela 07/2026',amount:300000,nature:'Aluguel',rule:'Contrato LOC-024 · valor base vigente',doc:'dcontract'},{name:'Participação na água',amount:12000,nature:'Valor a recuperar · revisar',rule:'Fatura de R$ 600 × 20% = R$ 120',doc:'dwater'},{name:'Encargo contratual',amount:18000,nature:'Encargo · revisar',rule:'Valor fixo previsto no contrato',doc:'dcontract'}]},
    {id:'o105',company:'aurora',title:'Aluguel · Sala 105',party:'Ateliê Luna',kind:'in',due:'2026-07-15',competence:'2026-07',contract:'c105',asset:'a105',account:'bradesco',docs:['dpartial'],items:[{name:'Aluguel · parcela 07/2026',amount:240000,nature:'Aluguel',rule:'Valor base do contrato LOC-025'}]},
    {id:'oloja',company:'aurora',title:'Aluguel · Loja 01',party:'Livraria Vereda',kind:'in',due:'2026-07-25',competence:'2026-07',contract:'cloja',asset:'aloja',account:'bb',docs:[],items:[{name:'Aluguel · parcela 07/2026',amount:420000,nature:'Aluguel',rule:'Valor base do contrato LOC-026'}]},
    {id:'owater',company:'aurora',title:'Água · Edifício Aurora',party:'Águas da Cidade',kind:'out',due:'2026-07-22',competence:'2026-07',account:'bradesco',docs:['dwater'],items:[{name:'Consumo de água',amount:60000,nature:'Despesa compartilhada',rule:'Fatura integral; R$ 120 vinculados à Sala 204',doc:'dwater'}]},
    {id:'oenergy',company:'aurora',title:'Energia · Sala 105',party:'Energia Regional',kind:'out',due:'2026-07-20',competence:'2026-07',asset:'a105',account:'bb',docs:['dlocked'],items:[{name:'Consumo de energia',amount:25000,nature:'Energia elétrica',rule:'Valor informado; conferir após leitura',doc:'dlocked'}]},
    {id:'orepair',company:'aurora',title:'Manutenção elétrica · Sala 105',party:'Oficina Elétrica',kind:'out',due:'2026-07-10',competence:'2026-07',asset:'a105',account:'bb',docs:['dmaintenance'],missing:'Nota fiscal do serviço',items:[{name:'Serviço elétrico',amount:48000,nature:'Manutenção',rule:'Relacionado ao imóvel Sala 105'}]},
    {id:'ocar',company:'aurora',title:'Financiamento · veículo',party:'Banco financiador',kind:'out',due:'2026-07-15',competence:'2026-07',asset:'acar',account:'bradesco',docs:['dloan'],items:[{name:'Amortização · parcela 17/48',amount:108000,nature:'Principal do financiamento',rule:'Composição informada no demonstrativo',doc:'dloan'},{name:'Juros da parcela',amount:12000,nature:'Despesa financeira',rule:'Componente separado do principal',doc:'dloan'}]},
    {id:'oaccounting',company:'aurora',title:'Honorários contábeis',party:'Contabilidade Exemplo',kind:'out',due:'2026-07-16',competence:'2026-07',account:'bradesco',docs:[],items:[{name:'Serviços de contabilidade',amount:35000,nature:'Serviços profissionais',rule:'Mensalidade informada'}]},
    {id:'oh',company:'horizonte',title:'Consultoria · julho',party:'Estúdio Horizonte',kind:'in',due:'2026-07-10',competence:'2026-07',contract:'ch',account:'hs',docs:[],items:[{name:'Serviços do mês',amount:890000,nature:'Serviços',rule:'Contrato SER-008'}]},
    {id:'ohpay',company:'horizonte',title:'Aluguel do escritório',party:'Locador Exemplo',kind:'out',due:'2026-07-12',competence:'2026-07',asset:'hdesk',account:'hs',docs:[],items:[{name:'Locação de espaço',amount:245000,nature:'Ocupação',rule:'Obrigação cadastrada manualmente'}]},
    {id:'ohsoft',company:'horizonte',title:'Licença de software',party:'Software Exemplo',kind:'out',due:'2026-07-23',competence:'2026-07',account:'hs',docs:[],items:[{name:'Assinatura anual',amount:42000,nature:'Software',rule:'Renovação prevista; confirmar documento'}]}
  ],
  transactions:[
    {id:'m1',company:'aurora',date:'2026-07-05',description:'PIX recebido · Marina Studio',account:'bb',amount:330000,obligation:'o204',confirmed:true},
    {id:'m2',company:'aurora',date:'2026-07-10',description:'Pagamento · Oficina Elétrica',account:'bb',amount:-48000,obligation:'orepair',confirmed:true},
    {id:'m3',company:'aurora',date:'2026-07-12',description:'PIX recebido · Ateliê Luna',account:'bradesco',amount:180000,obligation:'o105',confirmed:false},
    {id:'m4',company:'aurora',date:'2026-07-15',description:'Débito · parcela veículo',account:'bradesco',amount:-120000,obligation:'ocar',confirmed:true},
    {id:'m5',company:'aurora',date:'2026-07-16',description:'Pagamento · contabilidade',account:'bradesco',amount:-35000,obligation:'oaccounting',confirmed:true},
    {id:'mh1',company:'horizonte',date:'2026-07-10',description:'Recebimento · consultoria',account:'hs',amount:890000,obligation:'oh',confirmed:true},
    {id:'mh2',company:'horizonte',date:'2026-07-12',description:'Pagamento · locação',account:'hs',amount:-245000,obligation:'ohpay',confirmed:true}
  ],
  documents:[
    {id:'dcontract',company:'aurora',name:'Contrato · Sala 204.pdf',type:'Contrato',source:'Arquivo enviado',date:'2026-07-01',status:'Revisado',contract:'c204',asset:'a204',pages:[{title:'Contrato de locação',subtitle:'LOC-024 · Aurora Participações / Marina Studio',lines:['Objeto: locação da Sala 204, Edifício Aurora.','Vigência: 01/01/2026 a 31/12/2027.','Aluguel base: R$ 3.000,00. Vencimento: dia 5.']},{title:'Encargos e participação',subtitle:'Cláusula ilustrativa · versão 1',lines:['Água: 20% sobre o valor da fatura compartilhada.','Encargo fixo: R$ 180,00 por competência.','Toda cobrança deve discriminar seus componentes.']},{title:'Assinaturas e anexos',subtitle:'Página de exemplo',lines:['Esta página representa um anexo contratual.','Documentos fictícios para avaliação da navegação.']}]},
    {id:'dcharge',company:'aurora',name:'Cobrança · Sala 204 · julho.pdf',type:'Cobrança',source:'Gerado pelo contrato',date:'2026-07-01',status:'Revisado',obligation:'o204',contract:'c204',pages:[{title:'Demonstrativo da cobrança',subtitle:'Marina Studio · competência julho/2026',lines:['Aluguel da Sala 204: R$ 3.000,00.','Água compartilhada: R$ 120,00.','Encargo contratual: R$ 180,00.','TOTAL: R$ 3.300,00. Vencimento: 05/07/2026.']},{title:'Memória do rateio',subtitle:'Regra vigente em julho/2026',lines:['Fatura de origem: R$ 600,00.','Participação da Sala 204: 20%.','R$ 600,00 × 20% = R$ 120,00.']}]},
    {id:'dwater',company:'aurora',name:'Fatura de água · julho.pdf',type:'Fatura',source:'E-mail · exemplo',date:'2026-07-02',status:'Revisado',obligation:'owater',pages:[{title:'Fatura de água',subtitle:'Águas da Cidade · Edifício Aurora',lines:['Competência: julho de 2026.','Valor da fatura: R$ 600,00.','Vencimento: 22/07/2026.','Vínculo: R$ 120,00 na cobrança da Sala 204.']},{title:'Informações de consumo',subtitle:'Complemento da fatura',lines:['Histórico ilustrativo de consumo do edifício.','Esta página pode ser excluída da seleção para envio.','O documento original permanece completo.']}]},
    {id:'dreceipt',company:'aurora',name:'Comprovante · Marina Studio.pdf',type:'Comprovante',source:'Celular · exemplo',date:'2026-07-05',status:'Revisado',obligation:'o204',pages:[{title:'Comprovante de recebimento',subtitle:'Banco do Brasil · exemplo fictício',lines:['Data: 05/07/2026.','Pagador: Marina Studio.','Recebedor: Aurora Participações.','Valor: R$ 3.300,00.']}]},
    {id:'dpartial',company:'aurora',name:'Recibo parcial · Ateliê Luna.jpg',type:'Recibo',source:'Foto · exemplo',date:'2026-07-12',status:'A revisar',obligation:'o105',pages:[{title:'Recibo de pagamento parcial',subtitle:'Exemplo de leitura de uma imagem',lines:['Recebido de Ateliê Luna: R$ 1.800,00.','Referente ao aluguel de julho/2026, Sala 105.','Saldo da cobrança: R$ 600,00.','Conferir relação com o movimento de 12/07.']}]},
    {id:'dlocked',company:'aurora',name:'Energia · Sala 105.pdf',type:'Fatura',source:'Arquivo enviado',date:'2026-07-14',status:'Senha necessária',locked:true,obligation:'oenergy',asset:'a105',pages:[{title:'Conta de energia',subtitle:'Energia Regional · Sala 105',lines:['Valor: R$ 250,00.','Vencimento: 20/07/2026.','Dados de exemplo liberados após simulação de senha.']}]},
    {id:'dmaintenance',company:'aurora',name:'Comprovante · manutenção.pdf',type:'Comprovante',source:'Celular · exemplo',date:'2026-07-10',status:'Revisado',obligation:'orepair',asset:'a105',pages:[{title:'Comprovante de pagamento',subtitle:'Oficina Elétrica · Sala 105',lines:['Valor pago: R$ 480,00.','Data: 10/07/2026.','A nota fiscal ainda precisa ser obtida.']}]},
    {id:'dloan',company:'aurora',name:'Demonstrativo · veículo.pdf',type:'Demonstrativo',source:'Arquivo enviado',date:'2026-07-15',status:'Revisado',obligation:'ocar',asset:'acar',pages:[{title:'Demonstrativo da prestação',subtitle:'Parcela 17 de 48 · veículo utilitário',lines:['Amortização: R$ 1.080,00.','Juros: R$ 120,00.','Total pago: R$ 1.200,00.','Classificação contábil sujeita à revisão.']}]}
  ],
  tasks:[
    {id:'tpassword',company:'aurora',title:'Informar senha da conta de energia',due:'2026-07-18',owner:'Você',kind:'Documento',doc:'dlocked',obligation:'oenergy',done:false},
    {id:'tmatch',company:'aurora',title:'Conferir recebimento parcial da Sala 105',due:'2026-07-18',owner:'Você',kind:'Conciliação',obligation:'o105',done:false},
    {id:'tnote',company:'aurora',title:'Obter nota da manutenção elétrica',due:'2026-07-19',owner:'Você',kind:'Documento',obligation:'orepair',asset:'a105',done:false},
    {id:'trateio',company:'aurora',title:'Revisar classificação dos encargos',due:'2026-07-20',owner:'Contabilidade',kind:'Classificação',obligation:'o204',done:false},
    {id:'trenew',company:'horizonte',title:'Confirmar renovação do software',due:'2026-07-21',owner:'Você',kind:'Obrigação',obligation:'ohsoft',done:false}
  ],
  reviewed:[],selections:{},notes:{}
};
for (const origin of SEED.obligations.filter(o=>o.contract)) {
  SEED.obligations.push({...structuredClone(origin),id:origin.id+'-aug',due:origin.due.replace('-07-','-08-'),competence:'2026-08',docs:[],items:origin.items.map(i=>({...i,name:i.name.replace('07/2026','08/2026')}))});
}

export {MONTHS,total,paid,remaining,figures} from '../../dist/data.js';
