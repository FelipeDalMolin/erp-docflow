# Mês fictício para conferir o ERP

**Issue #119 · critérios propostos para #74–78 e #104.** Os identificadores e os valores abaixo foram criados para este ensaio. O quadro fixa resultados esperados. A execução deverá registrar versão do código, data de corte, cobertura, seleção, IDs de contribuição e resultado obtido.

## Um caso que atravessa o ERP

A Empresa Exemplo tem uma obrigação de **10.000 centavos** relativa a novembro. O item A responde por 6.000 e o B por 4.000. Ambos são reconhecidos em novembro, com precisão mensal. Em dezembro o banco registra uma saída de 4.000. O operador primeiro sugere o vínculo; depois confirma alocação integral de 4.000 **somente ao item A**. O total abaixo usa sinais de saída nos resultados e saldo a pagar positivo. Para fins deste exemplo, todo o valor compõe despesa.

| Momento e corte | Fluxo bancário no período | Resultado por caixa | Resultado por competência | Pendente no corte |
|---|---:|---:|---:|---:|
| Novembro encerrado, ambos os itens reconhecidos | 0 | 0 | −10.000 | 10.000 |
| Dezembro, após extrato e antes da confirmação | −4.000 | 0 atribuído a esta obrigação; 4.000 aguardam alocação | 0 novo | 10.000 |
| Dezembro, após a alocação a A | −4.000 | −4.000 | 0 novo | 6.000 (A 2.000 + B 4.000) |
| Repetição da confirmação com mesma chave e conteúdo | −4.000 | −4.000 | 0 novo | 6.000 |
| Cancelamento apenas da alocação, sem estorno bancário | −4.000 | 0 atribuído a esta obrigação | 0 novo | 10.000 |

Os zeros desta tabela pressupõem cobertura conhecida e ausência de outras contribuições. Sem extrato suficiente, o saldo é desconhecido. O movimento continua visível quando a associação está sugerida ou cancelada. Um estorno bancário real teria outro movimento identificável.

## Roteiro de aceite

| ID | Ensaio | Resultado que o revisor consegue conferir |
|---|---|---|
| C01 | Selecionar empresa, conta e dezembro. Abrir a barra, grade, item e fonte; exportar e voltar. | O mesmo movimento e os mesmos 4.000 centavos compõem as quatro saídas visuais. A seleção, o intervalo, o agrupamento e o foco sobrevivem ao retorno. Aproximar pelo zoom difere de selecionar um período. |
| C02 | Abrir detalhe da obrigação, planejamento e controle nos três primeiros momentos do quadro. | Para os mesmos critérios e corte, as três telas exibem o pendente esperado e informam por que um vínculo foi excluído. Uma tarefa concluída deixa os saldos inalterados. |
| C03 | Dividir uma liquidação entre duas cobranças e usar dois pagamentos para uma cobrança; repetir o comando e cancelar uma alocação. | Cada alocação conserva seu valor e destino. A soma respeita o disponível nas duas pontas. Repetição não duplica; cancelamento preserva o rastro e os demais vínculos. Resíduo fica explícito. |
| C04 | Alternar Caixa, Competência e Comparar com uma competência mensal e um filtro de conta. | Novembro contém os dois reconhecimentos. Dezembro contém o movimento. A diferença abre por item. A visão mensal conserva precisão e explica o tratamento dos fatos sem conta ou pagamento. |
| C05 | Conferir ausência de extrato, transferência entre contas e divisão entre empresas econômicas. | Ausência não produz saldo zero. O consolidado identifica os dois lados da transferência sem receita/despesa fictícia. A consulta declara a empresa do item e a titular da conta. |
| C06 | Gerar a cobrança de contrato para uma competência duas vezes e concluir a atividade associada na Home. | Uma cobrança mantém vínculos com ativo, contrato, aditivo e demonstrativo aplicáveis. Repetição e conclusão da tarefa não criam pagamento nem envio ao contador. |
| C07 | Reimportar o mesmo arquivo estruturado com o mesmo mapeamento. Incluir uma linha inválida e rever o lote. | A prévia mostra erro e proveniência por linha. A política de confirmação do lote é explícita. A nova tentativa preserva IDs e efeitos já aceitos. Alteração de origem/valor requer reavaliação. |
| D01 | Receber o mesmo conteúdo, primeiro com a mesma chave e depois com nova chave. Reutilizar a chave original com conteúdo diferente. | O primeiro replay devolve a ocorrência original; a nova chave preserva outra ocorrência auditável; a chave conflitante retorna conflito. A política de reuso de bytes é independente. |
| D02 | Interromper após gravar bytes e antes do commit SQL; repetir e baixar o original. | Retomada tem razão e estado visíveis. Um resultado concluído corresponde a um original recuperável, mesma identidade e tamanho/SHA-256 conferidos por releitura. |
| D03 | Receber WebP e um PDF elegível. Reprocessar o PDF e revisar a versão certa. | A fila diferencia recepção, elegibilidade e resultado. A tentativa tem versão e artefato próprios. Aceitar documento não confirma baixa nem lançamento. |
| H01 | Restaurar dados sintéticos num perfil limpo e, na etapa de release, em outro host. | No perfil: revisão, JSON, arquivos e vínculos recuperados. No host: release, migration, banco, storage, permissões, consulta, download e hashes verificados. O procedimento também cobre falha de restauração e retorno à versão anterior compatível. |

## Primeira fatia para desenvolvimento

Começar por **C01, C02 e C05** com leitura local na cópia de desenvolvimento da prévia. Registrar entradas, esperado e obtido antes de alterar as regras. Implementar o adaptador de consulta somente após definir como o período e a cobertura chegam às quatro apresentações. Abrir uma decisão de domínio para as divergências de baixa encontradas em C02. Introduzir leitura persistente com a mesma fixture. A prova de paridade compara conjuntos de IDs, centavos, cobertura e origem por contribuição, inclusive quando os totais coincidem.

O cenário C04 ampliado depende do reconhecimento por período e da alocação: preservar a decisão de UX já permite avaliar a tela enquanto esses contratos passam por revisão. Os cenários D02 e H01 sobre storage operacional aguardam as etapas correspondentes de #104 e #81.

[Mapa da conciliação](CONCILIACAO_ERP_V43.md)
