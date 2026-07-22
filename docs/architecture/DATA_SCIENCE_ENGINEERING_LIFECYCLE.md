# Engenharia de software para experimentos e componentes de dados

Status documental: contrato planejado, não implementado
Atualizado em: 2026-07-21
Issue de origem: #73
Issues relacionadas: #43, #48, #83, #88 e #89
ADRs relacionados: ADR-0003, ADR-0005, ADR-0007, ADR-0009, ADR-0015 e ADR-0016 (propostos quando indicado)

## 1. Finalidade e autoridade

Este documento traduz práticas de engenharia de software para o ciclo de descoberta, benchmark, integração e operação de componentes orientados por dados no `erp-docflow`.

Ele se aplica a:

- notebooks e scripts de exploração;
- regras, classificadores, OCR, layout e modelos;
- adapters/providers e seus experimentos;
- datasets, ground truth e benchmarks;
- componentes probabilísticos ou cujo comportamento dependa de dados.

O objetivo não é transformar toda análise em produto nem exigir MLOps complexo no início. O objetivo é impedir que um resultado exploratório seja tratado como código de produção sem contrato, reprodução, testes, versionamento, medição e decisão.

O [contrato de processing profile](PROCESSING_PROFILE_CONTRACT.md) define o comportamento de cada caso documental. A [estratégia de providers](PROVIDER_STRATEGY.md) define seleção e limites dos adapters. Este documento é autoridade para a passagem **experimento → componente promovível**.

## 2. Princípio central

```text
notebook = ambiente de descoberta e evidência
script/runner = reprodução automatizável
pacote/componente = unidade testável e integrável
adapter/provider = fronteira operacional versionada
profile/policy = autorização de uso em um caso concreto
```

Um notebook pode demonstrar que uma hipótese funciona. Ele não é, por si só:

- unidade de deploy;
- fonte canônica de regra ou schema;
- worker ou endpoint;
- benchmark reproduzível;
- autorização para provider/dado real;
- evidência de que o comportamento cabe no host on-prem.

Estado de célula, ordem manual de execução e dependência implícita de arquivo local não podem participar do runtime do produto.

## 3. Práticas incorporadas

Os temas de *Engenharia de Software para Cientistas de Dados: de notebooks a sistemas escaláveis* entram como requisitos observáveis, não como resumo bibliográfico.

| Tema | Aplicação no projeto |
| --- | --- |
| simplicidade, modularidade e baixo acoplamento | funções pequenas, contratos por capability e domínio sem SDK de provider |
| robustez, erros e logs | falhas tipadas, reason codes, correlation ID e ausência de “sucesso vazio” |
| profiling de tempo e memória | cold/warm start, tempo por página/lote, CPU, peak RSS, disco e impacto nos serviços principais |
| formatação, lint e tipos | gates automatizados definidos pelo workspace Python; nenhum notebook substitui esses gates |
| testes e validação de dados | unit, schema/data, contract, golden/regressão e E2E, com casos inválidos e ambíguos |
| design e refatoração | código exploratório é extraído para módulo/CLI antes da integração |
| documentação de experimentos | manifest, dataset, configuração, hardware, métricas, limitações e decisão |
| Git, dependências e empacotamento | commit identificado, lockfile, `pyproject.toml`, versões/digests e build reproduzível |
| APIs, containers e automação | processamento assíncrono atrás de adapter; CI e bundle provam execução fora do notebook |
| segurança | dados autorizados, secrets externos, dependências/modelos inventariados e serviços remotos bloqueados por padrão |
| ciclo de vida de software | promoção, observação, rollback, depreciação e retirada explícitos |

As ferramentas concretas de format, lint e type checking pertencem ao workspace aprovado. Este contrato define o resultado; não cria uma segunda configuração concorrente.

## 4. Fluxo de maturidade

```text
explorar
  -> reproduzir fora do estado interativo
  -> extrair e empacotar
  -> validar contratos e dados
  -> benchmarkar no perfil/host alvo
  -> decidir promoção
  -> integrar por adapter
  -> liberar em ambiente autorizado
  -> observar e comparar
  -> substituir ou retirar
```

### 4.1 Explorar

Permitido:

- compreender formato e qualidade dos dados;
- testar algoritmos, providers e transformações;
- produzir visualizações e análise de erro;
- reduzir uma hipótese a um experimento pequeno.

Obrigatório:

- Issue/spike identificada;
- dados sintéticos, anonimizados ou explicitamente autorizados;
- objetivo e hipótese claros;
- nenhuma credencial ou dado real no notebook/Git.

### 4.2 Reproduzir

Antes de comparar ou promover, o experimento precisa executar do zero por comando não interativo, com:

- inputs e outputs explícitos;
- dependências travadas;
- seed quando houver aleatoriedade;
- parâmetros/configuração versionados;
- ambiente e hardware registrados;
- falha com exit code e diagnóstico acionável;
- saída em formato comparável por máquina.

Executar todas as células do notebook não substitui esse runner.

### 4.3 Extrair e empacotar

Lógica reutilizável deve sair do notebook e entrar em módulo importável e testável. O notebook pode chamar esse módulo para exploração; o módulo de produção nunca importa ou executa o notebook.

O componente promovível declara:

- interface e tipos de entrada/saída;
- versão e compatibilidade;
- configuração externa;
- errors/reason codes;
- limites de recurso e cancelamento;
- dependências mínimas;
- licença do código, modelos e artifacts usados.

### 4.4 Verificar e benchmarkar

Testes comprovam correção contratual. Benchmark compara qualidade e custo operacional. Um não substitui o outro.

O benchmark precisa usar o mesmo `DatasetManifest`, ground truth e splits para todos os candidatos comparáveis. Mudança de dataset, regra, modelo ou target cria nova execução/versionamento; não se ajusta ground truth para fazer o candidato passar.

### 4.5 Promover e operar

Promoção exige decisão humana registrada e vínculo com um processing profile. O fato de um pacote existir, uma imagem iniciar ou uma métrica isolada melhorar não o torna provider padrão.

Troca de versão que pode alterar output exige regressão e política versionada. Reprocessamento histórico é decisão explícita.

A identidade promovida é rastreável, não uma suposição de que todos os digests de build serão iguais:

- commit/source, dependency lock, configuração e digests de dataset/modelos permanecem correlacionados;
- o package artifact avaliado deve ser reutilizado quando viável;
- se package ou imagem forem reconstruídos, o build registra source/inputs e produz novos digests;
- a imagem final executa a regressão aplicável antes da release;
- qualquer mudança funcional ou de dependência que possa afetar output exige novo benchmark/decisão.

Configuração comportamental — parâmetros, modelo, idioma, preprocessing, schema e thresholds — participa dessa identidade. Configuração de deployment — endpoint interno, secret ref, limites do container e observabilidade — pode variar por ambiente dentro do envelope aprovado; permanece externa aos dados do experimento e exige nova regressão quando puder alterar output ou disponibilidade.

## 5. Evidências mínimas do experimento

### 5.1 ExperimentManifest

Todo experimento comparável registra, em formato versionado:

- `experiment_id`, Issue, objetivo e hipótese;
- commit e estado do workspace;
- dataset/ground-truth/splits por referência e hash;
- classificação, licença e finalidade dos dados;
- adapter, engine/modelo/subengine e versões;
- parâmetros, transformações e seed;
- SO, arquitetura, CPU/GPU, RAM disponível e runtime;
- comando de reprodução;
- métricas, artifacts e amostras de erro;
- limitações, resultado e decisão posterior.

O manifest pode ir ao Git. Dataset/documento real permanece fora do Git e é referenciado conforme política.

### 5.2 BenchmarkRun

Uma execução de benchmark registra:

- manifest e política de aceitação usados;
- timestamps, status e versão do runner;
- resultado por documento/página/campo/tabela, quando aplicável;
- agregações com distribuição, não apenas média;
- cold e warm start separados;
- CPU, memória, disco/model cache, latência e throughput;
- abstention, review, erro, timeout e limite excedido;
- artifact bruto e normalizado por referência;
- diferenças contra baseline e limites de regressão.

### 5.3 PromotionDecision

A decisão informa:

- `experiment_manifest_ref` e um ou mais `benchmark_run_ref` que a fundamentam;
- capability e perfil autorizados;
- versão/configuração aprovada;
- host/ambiente elegível;
- targets atingidos e exceções;
- fallback e rollback;
- dados permitidos;
- owner e data de revisão;
- motivo de rejeição ou promoção.

`ExperimentManifest` e `BenchmarkRun` são evidências; não recebem status de “aprovado”. A autorização de runtime pertence somente à `PromotionDecision` humana.

## 6. Pirâmide de verificação

| Camada | Prova esperada |
| --- | --- |
| unitária | normalizadores, parsers, regras, métricas e transformações determinísticas |
| schema/dados | tipos, ranges, nulidade, categorias, unicidade, totais e casos inválidos |
| contrato de adapter | request/response, erro, timeout, cancelamento, retry e versão por fake/fixture |
| golden/regressão | outputs esperados por profile sem alterar fixture silenciosamente |
| integração | adapter real isolado com artifacts sintéticos/autorizados |
| E2E | task graph, lineage, routing, review e efeito permitido no ambiente elegível |

Para modelos treinados, testar separadamente preparação, treinamento e inferência. Splits impedem leakage; seed não torna determinístico o que a engine não garante, portanto a tolerância precisa ser declarada.

## 7. Performance e capacidade on-prem

O host de referência pequeno do laboratório possui a seguinte classe observada:

```text
small-cpu-lab
CPU: 4 processadores lógicos
RAM: aproximadamente 12 GB
Disco: SSD/NVMe
GPU: não presumida
Uso: rede local e poucos usuários
```

Essa é a classe-alvo para validar o R1 `core` e medir processamento assíncrono de baixa concorrência. A aptidão de cada provider CPU ainda precisa ser comprovada; a classe não demonstra capacidade de ML pesado nem de múltiplos providers concorrentes.

Regras para qualquer experimento no host:

1. API, banco, storage e UI mantêm prioridade de responsividade.
2. Execução pesada ocorre em worker/fila, nunca no request síncrono.
3. Concorrência, threads, batch, páginas e timeout são explícitos; default de biblioteca não é aceito sem medição.
4. Começar com um job pesado agregado no host; `deployment_profile/resource_envelope` e admission control compartilhado limitam todos os workers, enquanto o processing profile limita apenas paralelismo interno.
5. Medir peak RSS e pressão conjunta dos serviços, não apenas memória do processo isolado.
6. Separar cold start, warm start, download/cache de modelo e tempo por página.
7. Falta de memória, disco ou timeout produz reason code e não derruba o núcleo transacional.
8. VLM/GPU não pertence ao baseline desta classe de host.

Targets definitivos só podem ser fixados pela Issue do profile e pelo benchmark no host ou classe equivalente.

### 7.1 Escala progressiva sem antecipar microservices

Escalabilidade aqui significa preservar contrato, idempotência e observabilidade quando o volume crescer; não significa distribuir o sistema antes de haver necessidade.

| Estágio | Topologia | Mudança permitida sem alterar o domínio |
| --- | --- | --- |
| laboratório/poucos usuários | single-node, fila assíncrona e um job pesado | ajustar profile, batch e limites após benchmark |
| rede local com maior fila | worker CPU dedicado na LAN | mover adapter/provider mantendo job, artifact e `ProviderExecution` |
| workload acelerado | worker/host GPU opcional | promover outro candidato por capability e host class |
| volume maior | múltiplos workers com backpressure | particionar consumo preservando idempotência e estado durável fora da fila |

O núcleo permanece modular monolith. Provider não grava diretamente no banco canônico, fila não vira fonte da verdade e mover um worker não autoriza mudar output/schema silenciosamente. Queue age, tempo de espera, throughput, saturação e taxa de retry entram no capacity benchmark antes de aumentar concorrência.

## 8. Dependências, artifacts e segurança

- dependências Python ficam em pacote/extra mínimo e lockfile; não instalar todo stack de pesquisa no backend principal;
- provider pesado roda em processo/container dedicado;
- modelos são baixados no build/preflight autorizado, fixados por versão/digest e disponíveis offline antes da operação;
- download automático em runtime não é aceito no bundle on-prem;
- serviço remoto, plugin externo e telemetria são bloqueados por padrão;
- entrada vem por bytes/objeto interno controlado; URL arbitrária não é repassada ao provider;
- temporários têm quota, owner, retenção e deleção;
- resposta bruta fica em artifact store conforme retenção, não em log comum;
- inventário/SBOM inclui biblioteca, engine, subengine, modelo e licença aplicável;
- formatos inseguros e desserialização arbitrária são tratados pelo gate de segurança.

Código aberto sob licença permissiva não implica que todos os modelos/dependências usem a mesma licença.

## 9. Integração com providers compostos

Uma única chamada física pode produzir texto, layout e tabelas. Isso não autoriza a capability genérica `process_document`.

Quando um provider orquestra subengines:

- registrar uma `ProviderInvocation` para a chamada e um `ProviderExecution` por capability;
- registrar provider, backend, engine/subengine, modelo, versão e configuração;
- preservar um raw artifact comum e outputs normalizados tipados;
- medir qualidade e custo por capability sempre que possível;
- definir unidade de retry para não repetir silenciosamente etapa cara;
- impedir que confidence do provider vire confiança de negócio sem calibração;
- manter invocation/executions, `derived_from`, `EvidenceRef` e decisão do profile.

O modelo de dados do SDK permanece na borda. Ele não vira o modelo canônico do domínio.

## 10. Definition of Ready para Codex

Uma slice experimental ou probabilística só pode ficar `Condições Verificadas` quando informar:

- hipótese e decisão que o resultado poderá sustentar;
- manifest/dataset/ground truth permitidos;
- runner não interativo e comando de reprodução;
- paths de notebook, pacote, testes e artifacts;
- candidatos e baseline comparáveis;
- métricas/targets de qualidade e recursos;
- ambiente/hardware e budgets;
- política para falha, abstention, fallback e review;
- gate de segurança/licença/dados;
- critério explícito de promoção, rejeição e rollback.

O Codex pode criar ou usar notebook quando a Issue autorizar exploração. Ele não deve copiar células diretamente para produção, escolher o candidato vencedor nem promover output sem evidência e decisão registradas.

## 11. Aplicação inicial ao roadmap

O primeiro ciclo de processamento deve seguir esta ordem lógica:

1. #43 define processing profile, dataset, ground truth e targets.
2. #88 materializa manifest, runner, pacote, testes e relatório reproduzíveis.
3. #82 valida o Tika isolado para probe/texto nativo.
4. #83 (`recognize_text`) e #89 (`extract_layout`/`extract_table_structure`) executam como trilhas paralelas no mesmo dataset/host class; #83 usa o resultado Tika da #82 quando aplicável.
5. Decisão/ADR aprova capability, adapter e configuração.
6. #45–#47/#84–#86 implementam task graph e políticas separadas.
7. #48 executa regressão E2E do conjunto integrado.

O R1 Golden Month continua import-first. Nenhum notebook, Tika, Docling ou OCR bloqueia o caminho XLSX/CSV + correção manual auditada.

## 12. Referências

- [Catherine Nelson — *Software Engineering for Data Scientists*](https://www.oreilly.com/library/view/software-engineering-for/9781098136192/)
- [Sumário da edição brasileira — Novatec](https://s3.novatec.com.br/sumarios/sumario-9788575229170.pdf)
- [Contrato de processing profile](PROCESSING_PROFILE_CONTRACT.md)
- [Estratégia de providers](PROVIDER_STRATEGY.md)
- [Pipeline documental](DOCUMENT_PIPELINE.md)
- [Ambientes](../operations/AMBIENTES.md)
