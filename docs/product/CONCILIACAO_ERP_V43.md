# Da prévia v43 ao ERP DocFlow

**Referência funcional de 23/11/2026 · Issue #119 · proposta para revisão de produto e engenharia.** A v43 é a referência do comportamento privado. A comparação do núcleo usa a revisão `1739ffb` da main. A v35 saneada da [PR #118](https://github.com/FelipeDalMolin/erp-docflow/pull/118) é uma referência pública anterior. Os arquivos deste guia descrevem funcionamentos. Os exemplos são fictícios.

## O que muda no plano

O trabalho do site fornece a primeira especificação concreta de um ERP multiempresa. Quem usa o Caixa quer explicar um valor do gráfico até o lançamento e a fonte. Quem usa o Inbox precisa acompanhar o que chegou e por que um documento produziu, ou ainda aguarda, uma decisão. O DocFlow traz identidade do original, versões, evidência e decisões auditáveis para sustentar essas duas jornadas.

**Proposta de arquitetura:** manter a prévia utilizável e introduzir uma interface de leitura para o Caixa. Um adaptador lê o estado local, outro passará a ler dados persistentes. Executar a mesma consulta sobre ambos com um mês fictício. Começar a escrita persistente por entrada estruturada ou manual rastreável. Acrescentar os originais e o Inbox por etapas. A escolha da solução de OCR pode esperar a definição da tarefa e a medição de qualidade. O primeiro resultado entregável é poder reproduzir e explicar um mês em outro ambiente.

**Como ler a matriz:** a segunda coluna registra comportamento identificado por inspeção da v43. A terceira descreve o alcance da main nas fontes citadas. A última é proposta de desenvolvimento. “Local” significa estado do navegador. “Conceitual” significa que existe contrato documental. As evidências desta conciliação são estáticas. Aceites abaixo são ensaios a executar.

## Mapa funcional do ERP

| Área da interface | O que preservar da v43 | Encaixe no DocFlow hoje | Ajuste e prova de conclusão |
|---|---|---|---|
| Home, calendário e pendências | Obrigações, tarefas e desvios levam ao objeto de origem com próxima ação e contexto. | Jornadas de operador e gestor planejadas em #76. | Dar identidade e origem a cada pendência. Abrir da Home e voltar conserva empresa, período e seleção. |
| Perfil da empresa | O usuário trabalha no contexto de uma empresa. Um item pode pertencer economicamente a empresa diferente da titular da conta. | O código de recepção usa tenant. A política de acesso da aplicação depende de decisão própria. | Definir titularidade da conta, empresa econômica, tenant e papéis separadamente. Antes de uso compartilhado, comprovar autorização de leitura, escrita e download por escopo. |
| Contas e bancos | Contas identificadas e cobertura por extrato. Configuração de consulta e ambiente pode existir sem chamada ao banco. | Origem bancária e conciliação constam do domínio planejado. | Manter identidade da transação, referência ao extrato, data de cobertura e saldo desconhecido. Reimportar um extrato conserva o movimento e as decisões de revisão válidas. |
| Fluxo de caixa e planilha | Entradas e saídas separadas, saldo ao fundo, intervalo móvel, seleção distinta do zoom, hierarquia por classificação e fonte de cada contribuição. | A main prevê linhagem de evidência e relatórios. Falta consulta persistente em paridade com a tela. | Criar leitura por empresa, contas, período, data de corte e inclusão de classificações iniciais. Gráfico, grade e exportação devolvem os mesmos IDs e centavos. #78. |
| Planejamento, previsões e controle | Previsto × realizado, recorrência sugerida, ocorrência reconhecida e revisão de desvio. | Obrigações e liquidações aparecem no contrato conceitual. | Manter previsão, obrigação e alocação explícitas. Reconhecer uma ocorrência de previsão não altera a baixa. Exercitar data futura, ausência de extrato e pagamento parcial. |
| Obrigações e tarefas | Acompanhamento de vencimento, atividade e pagamento. A conclusão de uma tarefa preserva a pendência financeira. | Parcela, liquidação e alocação estão descritas. O banco atual materializa documentos. | Unificar elegibilidade de baixa entre detalhe, planejamento e controle. Ter um evento distinto para concluir tarefa e outro para confirmar alocação. |
| Ativos e contratos | O contrato contextualiza o ativo, os documentos e a cobrança da competência. Repetir a geração evita duplicar a cobrança. | O piloto #75 já prevê veículo e imóvel com aditivo e recebível. | Preservar identidade do ativo, versão/vigência contratual e chave de geração da cobrança. Repetir competência mantém uma cobrança; aditivo só muda a vigência aplicável. |
| Documentos e futuro Inbox | Recepção local, associação ao contexto, plano de leitura, tarefas e revisão local. A captura da navegação apresenta **Documentos**. | #39 oferece ocorrência idempotente e materialização SQL. #40–42 separam storage, upload HTTP e leitura/download. | Evoluir Documentos para fila/detalhe com etapa, razão, versão original e decisão. O recebimento pode avançar sem executar OCR. |
| Classificação, Contabilidade e fechamento | Composição por item/empresa, rascunho/inicial/revisado, plano CSV por empresa e versão. Exportação para conferência. | A main define fato gerencial e entrega ao contador. Política de autoridade e fechamento estão em #80 e #79. | Preservar natureza e versão do mapa de contas. A classificação do item não confirma conciliação, baixa, partida ou fechamento. Exigir autorização e trilha distintas para estes efeitos. |

## Dados que atravessam a interface

| O que existe na prévia | Conceito a reutilizar ou definir | Decisão para persistir |
|---|---|---|
| Movimento, conta e referência ao extrato | `BankMovement`, evidência de origem bancária | Um movimento mantém um ID mesmo quando aparece em várias classificações. Abertura do total deve indicar o valor que cada item contribuiu. |
| Composição e plano contábil da empresa | `ManagerialFact`, dimensões e mapeamento versionado | Registrar empresa econômica por item, natureza e centavos. Revisão exige soma exata da composição. Preservar a evidência e o histórico de mudanças. |
| Obrigação, sugestão de vínculo e pagamento | `Obligation`, `Charge`, `Settlement`, `SettlementAllocation` | A alocação terá valor explícito por parcela/item. Um pagamento pode cobrir várias cobranças e uma cobrança pode ter vários pagamentos. Estornar cria registro compensatório. |
| Competência informada no item | Reconhecimento econômico por item e período, proposto em complemento a `competence_date` | Admitir um ou vários reconhecimentos com valor, precisão temporal, método e versão. Mês informado continua mês. A distribuição diária requer política definida. |
| Documento e blob do navegador | `IntakeOccurrence`, `DocumentEnvelope`, `DocumentVersion`, `FileObject` | Manter ID de origem e hash. Tratar repetição de requisição, repetição de bytes e duplicidade de negócio como três decisões. |
| Planilha, extrato, entrada manual, revisão | Referência de evidência e origem tipada | Em CSV/XLSX guardar arquivo, aba, linha/célula e versão de mapeamento. Na entrada manual, autoria e justificativa. No documento, versão e localização quando aplicável. |
| Período, filtros, foco e exportação | Contexto de consulta e execução de relatório propostos | Fixar base temporal, data de corte, critérios, cobertura e conjunto de contribuições. Uma conta selecionada precisa explicitar o tratamento de fatos sem pagamento ou conta. |

O schema relacional auditado implementa `document_intake_occurrences`, `document_intake_occurrence_reasons`, `document_envelopes`, `document_versions`, `file_objects` e `audit_events`. O objeto de arquivo guarda localizador e metadados. Os bytes exigem armazenamento próprio. As entidades financeiras da tabela acima são alvos conceituais. A inspeção de código não substitui o inventário do banco instalado em um host.

## Decisões que afetam o que o usuário vê

**Baixa e corte.** Na v43, o detalhe pode somar o valor absoluto de movimentos vinculados. O planejamento verifica confirmação, sentido e conta. O acompanhamento também filtra por empresa e corte até a data corrente, com critério diferente para conta. Propomos uma regra explícita de elegibilidade, versionada e comum às três telas, com motivo e data de corte. O movimento aparecerá no caixa pela data bancária. A baixa dependerá do valor efetivamente alocado, da confirmação e do escopo da obrigação. Divergências entre visões só são aceitáveis quando o critério for exposto.

**Caixa, resultado por caixa e competência.** A escolha funcional “Caixa | Competência | Comparar” está registrada na v43. Construir o motor ainda exige três conjuntos de contribuições. O fluxo bancário soma movimentos. O resultado por caixa considera a parcela liquidada com natureza econômica aplicável. O resultado por competência considera os reconhecimentos do período. A comparação deve explicar as diferenças por contribuição e data. A UI já dá os filtros e o caminho até a fonte.

**Preservação e moeda.** Para reproduzir a prévia fora do navegador original, reunir revisão da aplicação, recursos e fontes embarcados, estado local e blobs de upload do IndexedDB. Restaurar primeiro em ambiente isolado. Um JSON de estado sozinho perde originais. Manter IDs e vínculos, verificar tamanho e SHA-256 e sinalizar ausências. Na fronteira front/API, a proposta é transmitir BRL em centavos inteiros e converter exatamente para o tipo decimal do domínio. Definir escala/moeda antes de admitir outras moedas.

**Inbox e processamento.** A v43 aceita PDF, PNG, JPEG e WebP até 15 MiB. O perfil candidato de processamento aceita PDF, PNG e JPEG até 20 MiB/20 páginas. Preservar um WebP pode ser válido mesmo quando o perfil não o processa. Exibir elegibilidade e razão. A v43 cria plano/tarefa para o arquivo recebido. Resultado de demonstração é simulado. No produto, execução de provider gerará tentativa, artefato, versão e evidência por campo; a revisão humana decide sobre aquela versão. O efeito financeiro tem autoridade própria.

## Sequência de desenvolvimento

| Ordem e responsável proposto | Trabalho e dependência | Saída verificável |
|---|---|---|
| 0 · Produto + frontend | Congelar a referência funcional; documentar dados e contexto de UI e criar o mês sintético. Manter os documentos de operação no site privado. | Restaurar em perfil limpo estado + originais sintéticos. Comparar IDs, hashes e vínculos. Catalogar exceções e suas razões. |
| 1 · Financeiro + frontend | Em cópia de desenvolvimento, encapsular a leitura do Caixa. Provar a consulta local antes de substituir a fonte. Rodar o exemplo de baixa em detalhe/planejamento/controle; pactuar corte, confirmação e conta. #74, #76, #78. | Gráfico, grade, detalhe e exportação reconciliados. Paridade inclui saldo desconhecido, seleção e foco. As três visões explicam o mesmo saldo pendente. |
| 2 · Domínio + dados | Ratificar fato/evidência (#74), definir transporte monetário, chave de importação, alocações e reconhecimento. Começar por entrada manual ou CSV/XLSX (#77) com prévia de lote e decisão explícita para linhas inválidas. Rodar as duas leituras do mesmo mês. | Mesmas contribuições e centavos no Caixa. Importar outra vez preserva efeitos e rastreabilidade. Comparar dois períodos explica pagamento parcial e competência. |
| 3 · Documentos + backend | Planejar a fila já com o usuário. Para persistência de originais, seguir #104 e #40 → #41 → #42. Rever recuperação do localizador e paridade das restrições SQL. | Reinício entre gravação dos bytes e commit SQL é recuperável. Download retorna o original conferido. Revisão deixa autor, versão, decisão e efeito explícito. |
| 4 · Processamento | Com originais recuperáveis, avaliar primeiro a capability exigida pelo perfil. Definir limite de recursos, versões e dataset adequado. | Tentativa e artefato rastreáveis, custo/qualidade medidos e seleção humana. O piloto financeiro pode operar com entrada estruturada e revisão humana. |
| 5 · Operações + produto | Ensaiar o bundle (#81) em host distinto. Antes de uso compartilhado, decidir acesso, isolamento, armazenamento e restauração. Exercitar o mês Golden Month (#75) e a entrega para conferência (#79/#80). | Restaurar aplicação, banco e objetos em conjunto, verificar IDs/hashes, consultar o mesmo mês e ensaiar retorno. Prontidão inclui dependências. A rota de saúde sozinha cobre o processo. |

As etapas 0 e 1 e o desenho da fila podem avançar enquanto os controles de #104 são tratados. A PR #116 antecede a revisão da ADR-0022 e a liberação explícita de #40. A ADR-0019 trata storage local sintético. O host definitivo, o armazenamento operacional e a política de autoridade continuam decisões de implantação.

## Provas e referências

- [Cenários de aceite e primeira entrega](ACEITE_ERP_V43.md)
- [Catálogo UML](../uml/README.md), [jornadas do produto](USER_JOURNEYS_AND_UX.md) e [piloto Golden Month](PILOT_VERTICAL_SLICE.md)
- [Domínio financeiro-gerencial](../architecture/MANAGERIAL_FINANCIAL_DOMAIN.md), [linhagem](../architecture/EVIDENCE_TO_REPORT_LINEAGE.md) e [importação estruturada](../architecture/STRUCTURED_IMPORT_PIPELINE.md)
- [Contrato de recepção e storage](../architecture/INTAKE_PERSISTENCE_STORAGE_CONTRACT.md), [estratégia de providers](../architecture/PROVIDER_STRATEGY.md) e [migração que materializa as seis tabelas](../../apps/api/migrations/versions/20260803_0001_document_materialization.py)

O mapa deve ser revisado quando uma tela, uma regra de cálculo, uma fonte de dados ou uma fronteira de persistência mudar. Em cada revisão registrar versão observada, issue, cenário impactado e evidência do teste. A passagem de comportamento proposto para implementado exige revisão do código e resultado do cenário correspondente.

## Levantamento por estrutura e decisão

O [levantamento das 21 estruturas e 13 sobreposições](ESTRUTURAS_E_RESPONSABILIDADES_V43.md) identifica os consumidores e registra um ensaio sintético da baixa. O [plano de adaptação documental](ADAPTACAO_DOCUMENTAL_ERP.md) define responsabilidades, vínculos, tipos de evidência e critérios para a primeira fatia.
