# Roadmap

Este roadmap organiza a evolução do projeto ERP/GED em fases incrementais.

A proposta não é construir o sistema inteiro de uma vez. A proposta é evoluir de forma controlada, começando pelo sistema de trabalho do projeto e avançando até o núcleo GED, revisão humana, financeiro, geração documental e integrações.

## Visão de destino

O projeto busca construir uma plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, capaz de:

- receber documentos;
- materializar documentos em um núcleo GED;
- armazenar arquivos com versionamento e rastreabilidade;
- executar OCR;
- extrair campos;
- sugerir classificação;
- permitir revisão humana;
- registrar aceite ou override;
- vincular documentos a lançamentos financeiros;
- gerar documentos como recibos, contratos e cobranças;
- manter auditoria;
- evoluir para integrações com bancos, escritórios contábeis e fontes externas.

## Phase 0 — Sistema do Projeto

Objetivo: criar o sistema operacional do projeto antes de iniciar código de produto.

Inclui:

- GitHub Project;
- Issues e slices;
- modelo operacional;
- estratégia Git;
- fluxo VS Code, Git e GitHub CLI;
- fluxo Codex;
- ADR baseline;
- traceability baseline;
- UML baseline;
- templates de Issue;
- template de Pull Request;
- CI estrutural inicial;
- planejamento de branch protection.

Critério de saída:

```text
Issue → branch → commits → PR → CI → review → squash merge
```

deve estar documentado e operacional.

## Phase 1 — Bootstrap App

Objetivo: criar a estrutura mínima da aplicação.

Inclui:

- monorepo inicial;
- backend FastAPI com endpoint `/health`;
- frontend React/Vite;
- estrutura base de pastas;
- configuração inicial de ambiente local;
- README de execução;
- Docker Compose inicial de desenvolvimento.

Fora de escopo inicial:

- autenticação completa;
- OCR;
- financeiro;
- GED completo;
- integração bancária;
- deploy de produção.

Resultado esperado:

```text
frontend abre
backend responde /health
estrutura base do projeto existe
ambiente local é reproduzível
```

## Phase 2 — Núcleo GED

Objetivo: implementar a base documental do sistema.

Inclui:

- DocumentEnvelope;
- FileObject;
- DocumentVersion;
- upload de documentos;
- armazenamento em object storage;
- persistência de metadados;
- hash de arquivos;
- Inbox Documental inicial;
- vínculo entre arquivo, versão e documento.

Resultado esperado:

```text
arquivo enviado
documento materializado
arquivo armazenado
metadados persistidos
documento aparece na Inbox
```

## Phase 3 — OCR, Extract e Classify

Objetivo: iniciar a automação documental.

Inclui:

- worker de OCR;
- OCRResult;
- extração de texto;
- extração inicial de campos;
- classificação sugerida;
- fila de processamento;
- reprocessamento manual;
- registro de erros e tentativas.

Campos iniciais desejáveis:

- fornecedor;
- valor;
- data de emissão;
- vencimento;
- competência;
- linha digitável;
- CNPJ/CPF;
- tipo provável do documento.

Resultado esperado:

```text
documento processado
texto extraído
campos sugeridos
classificação sugerida
status atualizado
```

## Phase 4 — Review e Acceptance

Objetivo: implementar revisão humana, override e aceite formal.

Inclui:

- ReviewDecision;
- AcceptanceCheck;
- tela de revisão;
- correção de campos;
- aceite;
- rejeição;
- reprocessamento;
- timeline documental;
- audit trail;
- registro de decisão humana.

Resultado esperado:

```text
sistema sugere
pessoa revisa
pessoa aceita, corrige ou rejeita
decisão é auditada
documento fica pronto para vínculo operacional
```

## Phase 5 — Núcleo Financeiro

Objetivo: conectar o núcleo GED aos fluxos ERP financeiros.

Inclui:

- FinancialEntry;
- PaymentIntent inicial;
- CashMovement inicial;
- EntityLink;
- vínculo entre documento e lançamento;
- vínculo entre documento e pagamento;
- dashboard operacional de pendências.

Resultado esperado:

```text
documento aceito
lançamento financeiro criado
vínculo registrado
auditoria preservada
pendências aparecem no dashboard
```

## Phase 6 — Geração Documental

Objetivo: permitir geração de documentos a partir dos dados do sistema.

Inclui:

- templates;
- geração de recibos;
- geração de contratos simples;
- geração de cobranças;
- geração de PDFs;
- versionamento de documentos gerados;
- vínculo com DocumentEnvelope;
- armazenamento dos documentos gerados.

Resultado esperado:

```text
dados estruturados
template selecionado
documento gerado
PDF armazenado
versão registrada
vínculo criado
```

## Phase 7 — Integrações

Objetivo: conectar o sistema a fontes externas e fluxos operacionais mais amplos.

Inclui:

- Google Drive / OneDrive como entrada;
- e-mail ingestion;
- integração bancária futura;
- importação OFX/CNAB;
- plano de contas;
- exportação contábil;
- integrações com escritório contábil;
- webhooks;
- APIs externas.

Resultado esperado:

```text
fontes externas alimentam o GED
movimentações externas alimentam o ERP
documentos e lançamentos ficam sincronizados
rastreabilidade é mantida
```

## Evolução esperada por maturidade

A maturidade do projeto deve evoluir assim:

```text
Fase documental controlada
→ automação assistida
→ revisão humana auditável
→ vínculo financeiro
→ geração documental
→ integrações
→ operação on-prem confiável
```

## Princípio de execução

Cada fase deve ser quebrada em slices pequenos.

Cada slice deve seguir:

```text
Issue → branch → commits → Pull Request → CI → review → squash merge
```

## Observação

As fases não são blocos rígidos. Elas orientam a evolução.

Pode haver spikes técnicos, revisões de ADR e ajustes de escopo ao longo do caminho. O importante é que mudanças relevantes sejam registradas e rastreáveis.