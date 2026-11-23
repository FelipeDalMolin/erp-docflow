# Dicionário entre a extração do DocFlow e o ERP Movimento Confiança

**#119 · referência funcional v43 · contrato de integração proposto em 23/11/2026.** O primeiro recorte é o perfil candidato `payable_document_pt_br/v1alpha`. A ligação começa na proposta de campo e termina numa decisão rastreável no ERP. A grade de revisão precisa mostrar, lado a lado, **o que o documento diz, o que já consta do ERP, a evidência e qual alteração a pessoa está autorizada a confirmar**.

## 1. O que efetivamente existe em cada lado

| Camada | Evidência atual | Mudança necessária |
|---|---|---|
| DocFlow: obtenção do texto | O perfil prevê inspeção do original, texto nativo, avaliação e OCR quando necessário. O único candidato executável registrado no harness é `integrity_probe/v1`; ele confere bytes e hashes de dados sintéticos. | Selecionar e testar adapters por capability. Registrar execução, versão, artefato produzido e tentativa. Uma verificação de integridade não comprova leitura do conteúdo. |
| DocFlow: interpretação | Existe um JSON Schema fechado, um pacote de regras por tipo e exemplos de saídas esperadas. O grafo do perfil atribui a extração dos campos a um pacote interno após obter texto. | Implementar ou adaptar a etapa que produz o resultado normalizado; validar formato, regras por tipo e evidência. Uma troca de motor de OCR deve preservar o significado dos campos. |
| Movimento Confiança: recepção | Documentos mantém catálogo e vínculos. O plano local escolhe método e abre tarefa. A v43 tem campos como `documents[].type`, `obligations[].party`, `obligations[].due` e `items[].amount`. | Expor no Inbox uma proposta por campo, com recurso para abrir o trecho, selecionar o objeto do ERP, corroborar um valor existente, corrigir a proposta ou deixá-la pendente. |
| Passagem entre ambos | A main planeja `EvidenceRef`, decisão e snapshot; a PR já descreve identidades e processos. Não foi identificada uma rotina integrada que traduza o resultado do perfil em alterações autorizadas nessas telas. | Fixar versão do mapa de campos e da decisão. Ligar o resultado à versão do original e à execução, comparar com a versão vigente do alvo e aplicar somente o efeito autorizado. |

A revisão de referência da main é `1739ffb`. As estruturas da v43 provêm do inventário de código da prévia. Dois detalhes de interface foram corroborados diretamente na v35 saneada: os rótulos disponíveis para tipo documental e a inicialização de `documents[].date` no recebimento. Validar o vocabulário final e a semântica de datas na v43 antes de implementar escrita. [Perfil](../../profiles/payable_document_pt_br/v1alpha/profile.json) · [Código dos candidatos](../../tools/experiment_harness/src/erp_docflow_experiment/candidates.py) · [Estruturas da v43](ESTRUTURAS_E_RESPONSABILIDADES_V43.md) · [Recepção da v35](https://github.com/FelipeDalMolin/erp-docflow/blob/4b25fcb318b602439db1ff814c047ffd369a4098/previews/erp-docflow/dist/intake-ui.js)

## 2. Dicionário campo a campo

`schema_id` e `schema_version` identificam o contrato. As outras oito observações são `document_type` e os sete atributos de `fields`. A coluna “Destino” explicita quando o ERP precisa de um atributo novo. As chaves semânticas propostas estão no [mapa JSON versionado](ensaios/mapa-payable-erp-v43.json). Elas não são nomes de colunas SQL existentes.

| Origem no resultado | Conceito do ERP | Destino existente ou lacuna | Conversão, decisão e proteção |
|---|---|---|---|
| `document_type` | Classe de negócio observada | Propor `documents[].type` com tradução de catálogo. | `INVOICE` sugere Fatura, mas pode exigir escolha de Nota fiscal. `PAYMENT_SLIP` sugere Cobrança com subtipo boleto. `RECEIPT` sugere Recibo. `OTHER` requer triagem; um contrato pode estar nesse grupo. MIME e categoria gerencial são independentes. |
| `fields.document_number` | Número atribuído ao documento pelo emissor | **Novo atributo documental.** Não há `documents[].number` no inventário. | Guardar como texto, inclusive zeros e série quando informados. Usar com emitente/escopo para localizar candidatos. Nunca substituir ID interno, número do contrato ou `transactions[].bankDocument`. |
| `fields.issuer_name` | Nome observado e papel de quem emitiu | Propor `obligations[].party` somente após resolver o papel. | Se a empresa emitiu a própria cobrança, a contraparte a receber é o cliente e pode estar ausente da extração. Em um boleto, distinguir instituição emissora/intermediária e beneficiário antes de sugerir o credor. Guardar texto observado e ID da contraparte confirmada separadamente. |
| `fields.issuer_tax_id` | Identificador fiscal observado do emitente | **Novo atributo de identificação** na referência ao emitente/contraparte. | Preservar texto inclusive letras e zeros. Validar formato e dígitos conforme o pacote do perfil. `companies[].profile.registration` pertence ao cadastro da empresa de contexto e não deve ser sobrescrito. |
| `fields.issued_on` | Data de emissão | **Novo atributo de emissão.** `documents[].date` não tem equivalência demonstrada. | Manter emissão, data de recepção, data bancária e competência distintas. Na rotina de upload v35, `documents[].date` recebe a data de trabalho ao receber o arquivo. |
| `fields.due_on` | Data de vencimento proposta | Candidata a `obligations[].due` em cobrança identificada. | Associar à parcela certa. Confrontar com vigência e vencimento do contrato. Não alimentar `expectedDate`, competência ou data do pagamento. A derivação atual de competência a partir de `due.slice(0,7)` em um formulário exige correção antes de reutilizá-lo aqui. |
| `fields.total_amount` | Total bruto declarado no documento | **Comparação** com a soma de `obligations[].items[].amount`. O ERP compõe o total pelos itens. | Decimal textual positivo com duas casas. Converter exatamente para centavos quando a moeda for BRL e o valor couber no intervalo inteiro usado no site. Não copiar o total para cada item, transação, valor do contrato, saldo pago ou competência. |
| `fields.currency` | Moeda da quantia observada | **Novo atributo/contexto monetário explícito** para a observação. | Perfil admite BRL quando presente. Se a moeda estiver ausente, sinalizar a pendência. A apresentação habitual em reais não autoriza completar o campo. |

Em resumo, há **quatro observações sem campo equivalente confirmado** (número, identificador do emitente, emissão e moeda). As outras quatro exigem tradução de catálogo, resolução de papel, proposta de vencimento ou comparação com uma composição. Nenhuma das oito autoriza gravação financeira direta.

**Campos que devem vir de outro lugar.** O contexto autorizado define tenant e empresa operadora. Titularidade da conta e movimento vêm do cadastro e do extrato. Empresa econômica por item, direção a pagar/receber, competência, natureza, categoria, centro de custo, contrato, ativo, parcela e alocação exigem evidência adicional, cadastro ou decisão com autoridade. Uma fatura genérica por si só não completa a composição revisada nem prova desembolso.

**Regra de comparação.** Mesmo alvo, mesmo campo, mesma versão e valor igual → pode corroborar com evidência adicional. Valor diferente → apresentar conflito com os dois valores e fontes. Alvo desconhecido → manter a observação no acervo e oferecer busca ou criação de rascunho. Duas parcelas igualmente plausíveis → solicitar seleção. Efeito em objeto já alterado → reabrir a comparação; a revisão antiga permanece consultável.

## 3. O que as palavras do perfil significam na tela

| Estado | O que salvar | Apresentação e efeito |
|---|---|---|
| `PRESENT` | Valor bruto, normalizado e ao menos uma referência de evidência. | Mostrar a proposta e validar. Um identificador fiscal pode estar legível e ainda ser inválido. |
| `MISSING` | Bruto e normalizado nulos; referências vazias. | Mostrar “Não encontrado”. Se for obrigatório para a classe, abrir pendência. |
| `NOT_APPLICABLE` | Bruto e normalizado nulos; referências vazias. | Mostrar “Não se aplica”. Aceitar esse estado segundo a classe documental. |
| `AMBIGUOUS` | Normalizado nulo, bruto presente ou nulo e pelo menos uma referência. | Mostrar “Exige conferência”, com o trecho. Um valor ilegível não vira zero. |

Cada observação mantém o mesmo envelope: `raw_value`, `normalized_value`, `applicability` e `evidence_refs[]`. Para esse perfil, cada evidência traz `artifact_ref`, página a partir de 1 e trecho, além de `bbox` e `coordinate_space`. Quatro coordenadas não negativas exigem `PIXEL`; quando a região é nula, o espaço também é nulo. Para banco, entrada manual e planilha, aplicar seus localizadores próprios. Um texto de OCR sem um número de página confiável não deve receber uma página inventada para passar na validação.

O envelope externo da aplicação deve associar tenant, empresa, documento/versão, original, job/tentativa, execução por capability, artefato, resultado e versão do mapa. A decisão aponta a finalidade e a versão do alvo. Scores opcionais de motores ficam com sua execução e método de cálculo; o schema fechado não aceita acrescentar `confidence` ao campo. Campo legível, candidato correto e autorização para alterar o ERP são três verificações distintas. [Schema](../../profiles/payable_document_pt_br/v1alpha/extraction.schema.json) · [Regras](../../profiles/payable_document_pt_br/v1alpha/validation-rules.json)

| Classe do perfil | Presença exigida pelo pacote | Ação a oferecer no ERP |
|---|---|---|
| `INVOICE` | Todos os sete campos. | Associar a uma cobrança existente ou preparar uma nova proposta com empresa, itens e competência por resolver. |
| `PAYMENT_SLIP` | Seis campos; emissão pode ser inaplicável. | Procurar a cobrança correspondente à fatura. Um segundo documento com o mesmo valor não cria segunda obrigação. |
| `RECEIPT` | Emitente, emissão, total e moeda. Número, identificador fiscal e vencimento podem ser inaplicáveis. | Associar comprovante e procurar movimento compatível. Confirmar a parcela e o montante é outra decisão. |
| `OTHER` | Nenhum dos sete precisa estar presente. Tipo classificado com evidência; revisão prevista. | Triagem e guarda, ou encaminhamento a perfil adequado. Um total lido em um contrato não gera obrigação por esse motivo. |

## 4. Correção bilateral em ordem de desenvolvimento

| Entrega | No erp-docflow | No Movimento Confiança | Prova de conclusão |
|---|---|---|---|
| 1 · Dicionário e teste de mesa | Revisar o mapa proposto com Produto. Manter schema de saída, regras por tipo e versão do mapa rastreáveis. | Validar rótulos, finalidade de cada data e papéis de emitente/beneficiário/contraparte em um caso privado conhecido. | Cada uma das oito observações tem destino, evidência e responsável. Cada campo exigido pela tela tem fonte ou motivo da pendência. |
| 2 · Inbox de revisão com fixture | Fornecer leitura de resultado esperado e contexto por versão. Começar com fixture sintética já existente; validar estrutura e regras antes de mostrar proposta. | Mostrar valor extraído versus cadastro atual, trecho da página, origem, alvo sugerido e efeito previsto. Registrar “corroborar”, “corrigir”, “buscar alvo” e “deixar pendente”. | A mesma fatura pode ser revisada contra uma obrigação existente. A data de emissão fica no documento; a competência continua pendente quando não há outra prova. |
| 3 · Decisão, vínculo e escrita | Implementar revisão/versionamento e autorização separados. Dar ao efeito uma identidade estável de origem, operação, alvo e finalidade. Vincular as revisões de decisão/mapa a essa identidade; uma reexecução retorna o efeito existente e uma correção cria sucessão ou estorno explícito. | Aplicar vinculação autorizada no acervo ou propor alteração individual no formulário de obrigação. Preservar a distribuição dos itens e o histórico da decisão. | Corrigir um vencimento cria registro de decisão e somente uma alteração. Um recibo reiterado conserva o pendente financeiro. Uma edição concorrente do alvo exige nova conferência. |
| 4 · Provider real e comparação | #82/#44 inspeção e texto nativo, #83/#46 OCR por necessidade, #84 validação/extração e #45 tentativas. #49–53 para revisão, snapshot e trilha. | Medir qualidade por campo e utilidade das propostas na operação privada, respeitando a política de dados do perfil/release. | Duas trajetórias de leitura do mesmo documento abastecem a mesma grade e mantêm fontes distintas. Degradação de um campo aparece com motivo. Dados reais precisam de uma decisão de perfil própria antes de processamento automático. |
| 5 · Outras famílias | Criar extensão ou perfil específico apenas quando houver caso real, contrato de saída e exemplos de aceitação. | Validar a trilha inversa do registro do ERP até cláusula, linha de origem ou decisão humana. | Exercitar o caso completo contrato/aditivo → cobrança/fatura → extrato → comprovante com um único efeito autorizado por alocação. |

**Prova operacional de revisão em uma linha.** Em um boleto de terceiro, o operador vê o CNPJ no trecho do original, confirma a identidade e o papel do emitente, escolhe a cobrança já existente e associa o documento. Uma diferença de vencimento fica destacada para decisão separada. Após salvar, a obrigação ganha a evidência, o saldo pago fica igual e o histórico permite saber quem aceitou cada mudança.

### Dados de outras famílias que o ERP precisa

| Origem | Campos a planejar e destino | Forma de entrada e limite |
|---|---|---|
| Contrato/aditivo | Número próprio, partes **com papéis**, ativo, cláusula, vigência, valor-base, periodicidade e regra de reajuste/rateio → versão do contrato e parâmetros de geração da cobrança. | Perfil específico ou revisão manual. Um aditivo só altera o período autorizado. Manter cláusula/página e antecessor. |
| Extrato | Conta/titular, período, ID de origem quando disponível, data, valor com sinal, moeda, saldo observado e cobertura → conta, movimento e referência de saldo. | Parser OFX quando disponível; para PDF, regra/extração específica para linhas e saldos. O perfil payable exige total positivo e não representa um extrato. |
| Planilha de controle | Aba, identidade de linha, data e semântica declarada, valor e sinal, categoria, empresa e competência quando informadas → lote, candidatos e fatos. | Mapeamento de colunas versionado, linha/célula e política para linhas rejeitadas. Ambiguidade de data exige decisão. |
| Dossiê de ativo | Ativo, requisito documental, emissor, validade e versão → atendimento do requisito e próxima ação. | Recepção simples e revisão podem bastar. Um prazo documental não é vencimento financeiro. |

Conta, parcela, contrato ou pessoa podem ser citados por vários perfis. Os perfis devem compartilhar um dicionário de identidade e resolução no ERP. Cada perfil conserva sua própria semântica de origem e seus próprios localizadores.

## 5. Verificação feita e próximos testes

O [verificador do mapa](ensaios/conferir-mapa-payable.mjs) confronta as chaves com o schema, as classes com o pacote de regras e as referências com os resultados **esperados** do [manifesto sintético](../../datasets/payable_document_pt_br/v1alpha/manifest.json). Verificamos 28 registros: 23 têm resultado esperado com oito observações (184 ao todo), cinco têm quarentena esperada sem resultado e quatro dos 23 têm falhas de validação previstas. Foram 165 observações presentes, 17 inaplicáveis, uma ausente e uma ambígua. Exercitamos também quatro mutações que o ensaio rejeitou: campo removido do mapa, escrita automática habilitada, ambiguidade convertida em zero e campo presente sem evidência. O ensaio confere coerência do mapa. A medição de precisão de um provider e a execução das telas ficam para as entregas 2 e 4.

| Caso do repositório ou contraprova proposta | Observação | Comportamento esperado na revisão |
|---|---|---|
| `dev-inv001-native` | R$ 1.234,56 → `1234.56` → 123456 centavos; emissão e vencimento diferentes. | Propor total e vencimento com fontes. Não preencher competência nem registrar pagamento. |
| `val-slip001-native` | Identificador fiscal sintético com letras; emissão inaplicável. | Preservar identificador como texto e manter emissão nula. Resolver papel antes de vincular. |
| `dev-rec001-native` | Recibo de R$ 245,90 sem vencimento aplicável. | Mostrar evidência de 24590 centavos, permitir anexar e conservar a baixa independente. |
| `dev-val-invalid-amount` / `dev-val-invalid-taxid` / `dev-val-date-conflict` | Total ilegível, identificador presente mas inválido, ou vencimento anterior à emissão. | Exibir o motivo específico e o trecho. Guardar as observações para correção e revisão. |
| `dev-inv001-native`, `dev-inv001-scan` e `dev-inv001-duplicate` | Mesma família, variantes de bytes e recepção. | Distinguir ocorrência, original e efeito econômico. Reprocessar ou receber novamente não duplica cobrança. |
| Caso funcional a executar na v43 | Empresa emitente de sua própria cobrança, já existente, mais recibo de mesmo valor. | Não criar a empresa como sua própria contraparte. Mostrar duas fontes de papéis distintos; manter uma cobrança e baixa dependente de alocação confirmada. |

Para repetir a conferência em um checkout com Node, a partir da raiz:

```sh
node docs/product/ensaios/conferir-mapa-payable.mjs
```

**Critério para considerar os dois projetos alinhados.** A mesma ocorrência de campo pode ser explicada no painel do ERP com a versão do original, o trecho lido, o valor normalizado, o objeto alvo, a decisão e seu eventual efeito. O caminho inverso parte de uma obrigação ou movimento e recupera esses mesmos elementos, inclusive conflitos e campos pendentes. O primeiro caso real deve ser conferido manualmente no ambiente privado. [Plano de adaptação por família](ADAPTACAO_DOCUMENTAL_ERP.md)
