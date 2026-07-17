# Modelo Operacional do Projeto

- **Classe:** normativo operacional
- **Estado:** vigente
- **Autoridade:** princípios de governança; detalhes especializados pertencem às fontes indicadas no [portal documental](../README.md)
- **Atualizar quando:** o modelo de trabalho, responsabilidades ou fontes de verdade mudarem

Este projeto tem como objetivo construir uma plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, focada em materialização documental, versionamento, revisão humana, aceite, auditoria e evolução futura para fluxos financeiros, contábeis, geração documental e integrações.

A proposta do projeto não é começar criando um ERP completo de uma vez. O objetivo inicial é construir uma base confiável para que documentos, arquivos, decisões, revisões, aceite humano, vínculos financeiros e histórico possam evoluir de forma rastreável.

## 1. Visão geral

O projeto será conduzido como um sistema de trabalho controlado, baseado em:

- GitHub Repository;
- GitHub Project;
- Issues;
- branches curtas;
- Pull Requests;
- CI/CD;
- ADRs;
- rastreabilidade;
- UMLs;
- revisão humana;
- uso controlado do Codex.

O fluxo padrão será:

```text
Issue → branch → commits → Pull Request → CI → review → squash merge
```

## 2. Fonte da verdade

A fonte da verdade do projeto será o repositório GitHub.

O repositório deve armazenar:

- código;
- documentação;
- ADRs;
- UMLs;
- mapas de rastreabilidade;
- templates;
- configuração de CI/CD;
- instruções para Codex;
- histórico de evolução via commits e Pull Requests.

O GitHub Project será usado como painel de acompanhamento, mas não substitui o repositório.

A fonte correta dentro do repositório depende da pergunta. O [portal documental](../README.md) mantém a matriz de autoridade; o [status do projeto](PROJECT_STATUS.md) mantém o snapshot de fase e gate. Este modelo não deve duplicar enums, comandos ou critérios que pertençam a uma fonte especializada.

## 3. Organização do trabalho

O trabalho será dividido em fases e slices.

Uma fase representa uma etapa maior do projeto.

Um slice representa uma unidade pequena, revisável e executável.

Exemplo:

```text
Phase 0 — Sistema do Projeto
├── [S0.01] Criar documentação operacional inicial
├── [S0.02] Definir fluxo do GitHub Project
├── [S0.03] Definir fluxo VS Code, Git e GitHub CLI
├── [S0.04] Criar AGENTS.md e configuração Codex
└── ...
```

Cada slice deve preferencialmente gerar:

```text
1 Issue
1 branch
N commits
1 Pull Request
1 squash merge
```

## 4. Papel das Issues

Issues representam unidades de trabalho.

Uma Issue deve conter, sempre que possível:

- objetivo;
- contexto;
- escopo;
- fora de escopo;
- critérios de aceite;
- validação esperada;
- relação com ADRs;
- relação com documentação;
- impacto em módulos, rotas, entidades ou infraestrutura, quando aplicável.

Issues vagas devem permanecer em descoberta ou especificação. Elas não devem ser executadas diretamente.

## 5. Papel dos Pull Requests

Pull Requests representam propostas de mudança.

Um PR deve:

- referenciar a Issue correspondente;
- ter escopo pequeno;
- explicar o que foi alterado;
- informar o que ficou fora de escopo;
- indicar documentação afetada;
- indicar validações realizadas;
- passar por revisão antes do merge.

O padrão de merge será:

```text
squash merge
```

Isso permite que a branch possua vários commits durante o trabalho, mas que a `main` receba apenas um commit consolidado por slice.

## 6. Papel dos ADRs

ADRs são Architecture Decision Records.

Eles registram decisões arquiteturais importantes.

Exemplos de decisões que devem virar ADR:

- escolha de arquitetura on-prem first;
- uso de modular monolith;
- uso de MinIO como object storage;
- uso de PostgreSQL;
- uso de DocumentEnvelope como núcleo GED;
- estratégia de revisão humana e aceite;
- uso do Codex no fluxo de desenvolvimento;
- estratégia de CI/CD;
- estratégia de autenticação e permissões.

Regra geral:

- se a decisão mudar de forma relevante, criar novo ADR;
- não apagar o ADR antigo;
- marcar o ADR antigo como substituído, complementado ou obsoleto;
- manter rastreabilidade entre ADRs e artefatos afetados.

## 7. Papel da rastreabilidade

A rastreabilidade conecta decisões, documentos, módulos, rotas, entidades, diagramas e Issues.

A pasta `docs/traceability/` deve apoiar perguntas como:

- qual ADR justifica esta decisão?
- qual módulo implementa este conceito?
- quais rotas afetam esta entidade?
- quais diagramas representam este fluxo?
- qual documentação precisa ser atualizada se uma decisão mudar?
- qual o impacto de alterar o DocumentEnvelope?
- qual Issue ou PR introduziu determinado comportamento?

A rastreabilidade evita que o projeto se transforme em código e documentação soltos.

## 8. Papel das UMLs

A pasta `docs/uml/` armazenará diagramas estruturais e comportamentais.

Tipos previstos:

- contexto;
- deployment;
- casos de uso;
- atividades;
- componentes;
- classes de domínio;
- sequência;
- estados.

Os diagramas devem apoiar o entendimento do sistema e devem ser atualizados quando houver mudança relevante em fluxos, entidades, estados, módulos ou integrações.

## 9. Papel do Codex

O Codex será usado como apoio para execução e revisão.

O Codex poderá atuar em:

- criação de arquivos;
- implementação de slices;
- refatorações pequenas;
- revisão de PRs;
- atualização de documentação;
- geração de testes;
- apoio em CI/CD.

O Codex deve ter autonomia para selecionar e executar slices prontos dentro de um envelope aprovado.

O Codex não deve decidir sozinho mudanças de direção. Deve solicitar orientação e aprovação em:

- mudança de arquitetura;
- troca de banco;
- troca de storage;
- mudança em fluxo de aceite;
- mudança em segurança;
- mudança em deploy;
- alteração de ADR aceito;
- implementação fora do escopo da Issue.

O uso do Codex deve respeitar:

- Issue clara;
- escopo definido;
- critérios de aceite;
- condição de execução verificada;
- modo de execução definido;
- revisão humana.

A aprovação humana pode abranger um lote de slices. O fim de um slice não exige nova aprovação quando o próximo item já está pronto, pertence ao mesmo envelope e não introduz decisão, risco ou conflito novo.

## 10. Condição de Execução

O campo `Condição de Execução` no GitHub Project indica se uma Issue está pronta para ser trabalhada. A lista canônica e os critérios completos pertencem ao [Fluxo do GitHub Project](../operations/FLUXO_GITHUB_PROJECT.md).

Valores previstos:

```text
Não Verificado
Condições Verificadas
Precisa Especificação
Precisa ADR
Precisa Decisão Humana
Bloqueado
```

Uma Issue só deve ser executada quando:

```text
Condição de Execução = Condições Verificadas
```

Quando várias Issues com condições verificadas pertencem a um envelope aprovado, elas formam uma fila de pull. O Codex pode escolher a próxima por prioridade e dependência sem pedir autorização a cada transição.

## 11. Modo de Execução

O campo `Modo de Execução` indica como a Issue será trabalhada. Ele descreve colaboração e não substitui permissões técnicas de Read, Plan ou Workspace-write da sessão Codex.

Valores previstos:

```text
Não Definido
Manual
Assistido por Codex
Somente Revisão Codex
Pareamento / Chat + Humano
```

O modo de execução não substitui a revisão humana. Mesmo tarefas assistidas por Codex devem passar por PR e revisão.

No modo `Assistido por Codex`, a Issue pode participar do loop contínuo quando estiver no envelope aprovado. `Pareamento / Chat + Humano` deve ser usado quando os checkpoints esperados fizerem parte do próprio trabalho.

## 11.1 Loop de continuidade

O fluxo operacional completo é:

```text
Plan Mode
→ aprovação do envelope
→ puxar slice pronto
→ executar
→ validar
→ preparar PR
→ avaliar continuidade
   ├── CONTINUE
   ├── AWAIT_DEPENDENCY
   ├── CHECKPOINT
   └── STOP
```

O envelope deve registrar apenas o necessário:

- estado `Rascunho`, `Aprovado`, `Pausado` ou `Encerrado`;
- responsável, data e referência da aprovação;
- objetivo;
- conjunto ou critério de seleção dos slices;
- áreas autorizadas e excluídas;
- paths e ownership quando houver paralelismo;
- dependências;
- validações;
- checkpoints;
- condição de encerramento.

O corpo da Epic ou Issue governante mantém o estado corrente. `Rascunho` não autoriza execução; `Aprovado` limita a execução ao escopo registrado; `Pausado` impede iniciar nova slice; `Encerrado` exige novo envelope ou revisão aprovada para retomar. Mudança de limites, ownership ou exclusões exige revisão humana durável.

`CONTINUE` é permitido quando o próximo slice estiver pronto, dentro do envelope, sem dependência pendente, sem conflito e sem decisão nova.

`AWAIT_DEPENDENCY` é usado quando o próximo item depende de PR ou entrega conhecida e esperada, sem decisão nova.

`CHECKPOINT` é usado quando houver decisão/ação humana não prevista, mudança de direção, risco, ambiguidade, falha que amplie escopo ou área protegida não autorizada.

Uma dependência conhecida e esperada usa `AWAIT_DEPENDENCY`. Se a dependência revelar decisão, ação humana não prevista ou ambiguidade de escopo, usa-se `CHECKPOINT`.

`STOP` é usado quando o envelope terminar ou não houver candidato elegível.

Selecionar exatamente um outcome nesta ordem: `STOP` para envelope encerrado/sem candidato; `CHECKPOINT` para decisão, risco ou conflito não previsto; `AWAIT_DEPENDENCY` para espera conhecida; `CONTINUE` para próximo item elegível.

Registrar fato, referência ao envelope e condição de retomada na descrição do PR. Sem PR, registrar em comentário na Issue ou Epic correspondente.

Um slice fica tecnicamente concluído quando implementação, validações, documentação e PR draft estão preparados. Ele entra em `Review` somente com PR fora de draft e pronto para revisão humana. Só fica `Done` depois de revisão, squash merge, fechamento da Issue e reconciliação do Project.

O Codex pode iniciar outro slice independente enquanto um PR aguarda revisão, desde que parta da `main`, não dependa do PR pendente, não sobreponha mudanças relevantes e o envelope permita.

O Codex nunca faz merge automático.

## 12. Fases do projeto

O projeto será conduzido por fases:

```text
Phase 0 — Sistema do Projeto
Phase 1 — Bootstrap App
Phase 2 — Núcleo GED
Phase 3 — OCR Extract Classify
Phase 4 — Review Acceptance
Phase 5 — Núcleo Financeiro
Phase 6 — Geração Documental
Phase 7 — Integrações
```

A Phase 0 deve ser concluída antes do início do código de produto.

O baseline da Phase 0 está encerrado. A Epic da Phase 1 está aberta em refinamento, mas o código só começa quando o gate e a primeira slice estiverem aprovados conforme [Status do projeto](PROJECT_STATUS.md).

## 13. Critério de maturidade para iniciar código

O ADR-0002 define a decisão histórica de concluir um baseline operacional antes do código. O [Roadmap](ROADMAP.md) mantém os critérios permanentes da transição, e [Status do projeto](PROJECT_STATUS.md) registra evidências, pendências e aprovação do gate atual.

Uma Epic aberta ou uma lista de Issues não equivale a autorização de execução. Para iniciar código, a slice deve ter escopo verificável, dependências satisfeitas, condição `Condições Verificadas`, paths/validações conhecidos e vínculo com envelope aprovado.

## 14. O que evitar

Evitar:

- trabalhar direto na `main`;
- criar código antes da documentação mínima;
- executar tarefas grandes demais;
- misturar vários slices no mesmo PR;
- usar Codex sem Issue clara;
- alterar arquitetura sem ADR;
- deixar decisões importantes apenas no chat;
- criar documentação fora do repositório;
- tratar arquivos/documentos como anexos sem rastreabilidade;
- automatizar fluxos críticos sem revisão humana.

## 15. Diretriz final

O objetivo do projeto é construir uma solução ERP/GED confiável, auditável e evolutiva.

Para isso, o projeto deve evoluir com:

```text
clareza → rastreabilidade → revisão → versionamento → automação controlada
```

A agilidade desejada não virá de fazer tudo de uma vez, mas de criar um fluxo onde cada pequena entrega possa ser entendida, revisada, testada, rastreada e integrada com segurança.
