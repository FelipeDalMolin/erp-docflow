# Piloto vertical Golden Month

- **Classe:** baseline planejado de piloto
- **Estado:** planejado, não implementado
- **Issue de origem:** #73
- **Atualizar quando:** cenário, dataset, resultado, dependência ou critério de aceite do piloto mudar

## 1. Objetivo

Entregar um recorte pequeno, mas utilizável, que percorra uma entidade e um período representativo desde a entrada dos dados até o fechamento e a entrega. O piloto deve comprovar valor gerencial ponta a ponta antes de ampliar documentos, automação, integrações ou modalidades.

Ele aplica a direção do [North Star](PRODUCT_NORTH_STAR.md), mas não substitui as fases e gates do [Roadmap](../project/ROADMAP.md).

## 2. Hipótese do piloto

Se o produto conseguir importar um mês representativo, preservar cada origem, tratar exceções, produzir informações gerenciais reconciliadas e fechar uma versão rastreável, então a arquitetura poderá ser evoluída com automação documental sem depender dela para demonstrar valor inicial.

## 3. Recorte

| Dimensão | Recorte planejado |
| --- | --- |
| organização | uma entidade operacional representativa |
| período | um mês completo e já conhecido pelo responsável |
| dataset | cópia anonimizada, versionada e acompanhada de manifest |
| entrada obrigatória | uma planilha legada representativa em XLSX ou CSV |
| entradas auxiliares | lançamento manual auditado e documentos relacionados quando disponíveis |
| entradas opcionais | extrato estruturado ou OFX, somente se houver slice própria e contrato validado |
| dimensões/casos obrigatórios | classes/aliases/master data, ao menos um veículo e um imóvel com contrato/aditivo e recebível no dataset anonimizado |
| resultado | livro/agenda, visões gerenciais, pendências, fechamento e pacote versionado |
| ambiente-alvo | `onprem-lab`, depois que o bundle mínimo existir e seus gates forem atendidos |

O piloto não utiliza dados reais em ambiente não autorizado. Anonimização não dispensa classificação, controle de acesso e validação de que o conjunto não permite reidentificação indevida.

## 4. Contrato mínimo de entrada

Antes de importar, o dataset deve possuir:

- identificador e versão;
- hash dos arquivos;
- entidade e período de referência;
- origem e responsável pela preparação;
- abas, colunas e tipos esperados;
- regras conhecidas do legado;
- totalizadores de controle;
- valores ausentes ou ambíguos conhecidos;
- classificação de sensibilidade;
- resultado esperado usado como ground truth gerencial.

Cada linha recebida deve permanecer rastreável pelo arquivo, aba, linha ou identificador original. A normalização não pode descartar silenciosamente linhas inválidas.

## 5. Percurso ponta a ponta

### 5.1 Preparar

1. selecionar o mês representativo;
2. anonimizar e versionar o conjunto;
3. registrar manifest, hashes e totalizadores;
4. definir responsáveis por validação gerencial e técnica.

### 5.2 Importar

1. selecionar a fonte e a entidade/período;
2. visualizar amostra antes da gravação;
3. mapear colunas para conceitos do piloto;
4. validar tipo, obrigatoriedade, duplicidade e totais;
5. confirmar a importação;
6. registrar lote, configuração, linha bruta, linha normalizada e erro por linha.

Reexecutar o mesmo lote com a mesma chave de idempotência não pode duplicar fatos aceitos. Reprocessar com nova configuração cria nova tentativa/versionamento e preserva a anterior.

### 5.3 Normalizar e revisar

- normalizar datas, moeda, sinal, categoria, contraparte e dimensões aplicáveis;
- separar valor bruto de valor normalizado;
- mostrar erro, warning e conflito de forma distinta;
- permitir corrigir, aceitar, rejeitar ou deixar pendente conforme autoridade futura;
- registrar antes/depois, justificativa, ator, horário e regra/configuração usada.

O mínimo comum de uma ocorrência aceita deve permitir identificar entidade, período, data, direção, valor, origem e estado. O Golden Month deve ainda provar, no dataset anonimizado e nas slices refinadas:

- normalização de classes, aliases e master data;
- veículo como dimensão do mesmo ledger;
- imóvel relacionado a contrato e aditivo com vigência;
- ao menos um recebível relacionado e rastreável.

Centro de custo, contraparte e dimensões adicionais só entram quando explicitamente refinados.

### 5.4 Produzir informação gerencial

- representar previsto e realizado sem sobrescrever um pelo outro;
- distinguir obrigação, liquidação, ajuste e transferência quando o caso exigir;
- evitar duplicidade na efetivação;
- preservar vínculos com fonte, revisão e evidências relacionadas;
- manter itens incompletos fora dos totais oficiais ou identificá-los explicitamente conforme política.

Os nomes de entidades e relações físicas serão definidos em refinamento de domínio; este documento define somente o comportamento observável.

### 5.5 Reconciliar e analisar

- comparar totais importados, aceitos, pendentes e rejeitados;
- identificar diferenças e motivo;
- filtrar por entidade, período, estado e dimensões disponíveis;
- salvar uma visão quando essa capacidade for implementada;
- navegar de um total para ocorrências e respectivas origens.

### 5.6 Fechar

1. executar checklist de cobertura e pendências;
2. impedir fechamento silencioso com conflito crítico não tratado;
3. registrar responsável, horário, regras e versão dos dados;
4. congelar um snapshot lógico do período;
5. gerar pacote e protocolo;
6. tratar correção posterior por nova versão ou reabertura autorizada, nunca por sobrescrita invisível.

O conteúdo do pacote e os gates operacionais estão em [Entrega e aceite](PRODUCT_DELIVERY_AND_ACCEPTANCE.md).

## 6. Dependências de capacidades

| Capacidade | Necessária para o piloto | Observação |
| --- | --- | --- |
| bootstrap reproduzível | sim | base técnica da Phase 1 |
| persistência e auditoria mínimas | sim | sujeitas aos ADRs e gates aplicáveis |
| importação XLSX/CSV | sim | caminho principal do piloto |
| correção manual auditada | sim | evita depender de automação prematura |
| classes, aliases e master data | sim | normalização mínima antes dos vínculos gerenciais |
| veículo, imóvel, contrato/aditivo e recebível | sim | casos representativos obrigatórios do Golden Month, sem pretender cobrir todas as modalidades |
| visão e drill-through | sim | demonstra valor gerencial e proveniência |
| fechamento e pacote | sim | define o final verificável do percurso |
| materialização documental | parcial | necessária somente para documentos usados como evidência no recorte |
| Tika, OCR ou extração automática | não bloqueante | entram depois por perfil e benchmark |
| OFX/CNAB e integração bancária | não bloqueante | só entram com contrato próprio |
| RAG, busca híbrida e aprendizado | não | evolução posterior |

Quando documentos entrarem no recorte, devem respeitar o [Pipeline documental](../architecture/DOCUMENT_PIPELINE.md), o [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md) e a estratégia proposta no [ADR-0016](../adr/0016-capability-based-document-processing-providers.md).

## 7. Experiência mínima

O piloto deve oferecer as experiências planejadas em [Jornadas e UX](USER_JOURNEYS_AND_UX.md):

- contexto visível de entidade e período;
- importação com preview, mapping e erros por linha;
- fila de exceções;
- visão gerencial com drill-through;
- checklist de fechamento;
- pacote, versão e protocolo acessíveis;
- estados de loading, vazio, erro, bloqueio e falta de permissão.

Isso não define URLs, framework de estado, componentes ou design system.

## 8. Critérios de aceite funcional

| Critério | Evidência esperada |
| --- | --- |
| nenhuma entrada some | todas as linhas possuem estado final ou pendente e reason code quando não aceitas |
| linhagem completa | 100% das ocorrências aceitas chegam à linha/fonte e às decisões aplicadas |
| idempotência | replay do mesmo lote não cria duplicidade |
| totais controlados | totais de entrada, aceitos, pendentes e rejeitados fecham entre si |
| diferença explicável | não existe diferença não classificada no fechamento |
| correção auditável | antes/depois, autor, horário e justificativa são preservados |
| dimensões representativas | veículo e imóvel são localizáveis no mesmo ledger e preservam seus vínculos/evidências |
| contrato e recebível | contrato/aditivo preserva vigência e o recebível relacionado chega à fonte e ao fato |
| drill-through | total selecionado chega às ocorrências que o compõem |
| fechamento reproduzível | snapshot, manifest e pacote podem ser regenerados pelas referências persistidas |
| isolamento de automação | indisponibilidade de OCR/provider não impede o caminho estruturado/manual |
| operação verificável | smoke e E2E do percurso passam no ambiente-alvo aprovado |

Critérios de desempenho, volume e tempo devem ser quantificados pela Issue de implementação com base no dataset real do benchmark.

## 9. Gates antes de dados reais

O piloto só pode avançar de dataset sintético/anonimizado para operação real quando cumprir o nível correspondente em [Entrega e aceite](PRODUCT_DELIVERY_AND_ACCEPTANCE.md). Este documento não mantém uma segunda lista de controles.

O [ADR-0015](../adr/0015-auth-authorization-security-strategy.md) permanece bloqueante para autenticação, autorização e segurança, e o [ADR-0014](../adr/0014-backup-and-restore-required.md) exige restore testado antes de operação on-prem real. A autorização do dataset, dos responsáveis pelo fechamento e do ambiente também precisa estar registrada na Issue operacional.

## 10. Fora de escopo

- cobrir todas as entidades e exercícios históricos;
- reproduzir toda planilha como interface permanente;
- definir escrituração fiscal ou contábil oficial;
- automação irrestrita ou autoaceite geral;
- treinamento de modelo;
- providers externos com dados reais;
- alta disponibilidade ou produção definitiva;
- rotas, endpoints, tabelas e schemas físicos.
