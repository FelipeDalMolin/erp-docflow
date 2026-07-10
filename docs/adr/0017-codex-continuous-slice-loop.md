# ADR-0017 — Loop contínuo de slices pelo Codex

Status: Aceito  
Data: 2026-07-10  
Decisores: FelipeDalMolin  
Tags: codex, autonomia, loop, slices, plan-mode, github-project

## Contexto

ADR-0003 define Issue, branch, Pull Request, CI, revisão humana e squash merge como fluxo rastreável. ADR-0005 define uso do Codex com autonomia alta controlada.

Os documentos operacionais, porém, descrevem principalmente a prontidão e os motivos de parada. Sem uma regra de continuidade, isso pode ser interpretado como necessidade de nova aprovação humana ao terminar cada slice, mesmo quando o próximo item já está pronto, pertence ao mesmo contexto aprovado e não introduz decisão nova.

O projeto precisa preservar Issues e PRs pequenos sem transformar cada transição entre slices em um gate mecânico.

## Decisão

Adotar um loop contínuo baseado em **envelope de execução**:

1. Plan Mode propõe um lote delimitado de slices, dependências, áreas permitidas, exclusões, validações e checkpoints;
2. a aprovação humana do plano autoriza o envelope, não apenas o primeiro slice;
3. o Codex puxa o slice elegível de maior prioridade;
4. executa, valida, documenta e prepara o PR correspondente;
5. ao encerrar o trabalho técnico do slice, avalia a fila e escolhe uma das saídas:
   - `CONTINUE`: puxar o próximo slice elegível;
   - `AWAIT_DEPENDENCY`: aguardar PR, decisão ou dependência;
   - `CHECKPOINT`: solicitar orientação humana com evidência e opções;
   - `STOP`: encerrar porque o envelope terminou ou não há item elegível;
6. o fim de um slice, isoladamente, não exige nova aprovação.

O Codex decide **se pode continuar**. Ele não decide sozinho nova direção de produto, arquitetura, segurança, infraestrutura ou negócio.

## Envelope de execução

O envelope é registrado na Epic, na Issue que abre o lote ou no plano aprovado. Deve ser curto e conter:

- objetivo do lote;
- slices ou critérios de seleção;
- áreas e tipos de mudança autorizados;
- exclusões;
- dependências conhecidas;
- validações mínimas;
- checkpoints humanos;
- condição de encerramento.

Não é obrigatório criar novo campo no GitHub Project. `codex:eligible`, prioridade, condição de execução, Epic e dependências formam a fila de pull.

## Elegibilidade para continuar

O próximo slice pode ser puxado quando:

- está `Ready for execution`;
- pertence ao envelope aprovado;
- tem escopo e aceite verificáveis;
- dependências estão concluídas ou o item é independente;
- não depende de conteúdo ainda não mergeado;
- não conflita com branch/PR em andamento;
- não toca área excluída ou protegida sem autorização explícita;
- não exige decisão nova;
- o slice anterior atingiu seu critério técnico de saída.

`codex:eligible` indica entrada possível na fila. Não concede autorização ilimitada fora do envelope.

## Slice tecnicamente concluído versus Done

Para o loop:

- **tecnicamente concluído**: implementação, validações, documentação e PR draft estão preparados;
- **Done no Project**: PR revisado e mergeado, Issue fechada e critérios confirmados.

O Codex pode iniciar outro slice independente enquanto um PR aguarda revisão, desde que:

- a nova branch parta da `main`;
- o novo slice não dependa do PR pendente;
- não haja sobreposição relevante de arquivos ou decisões;
- o envelope permita continuidade paralela.

Slice dependente deve aguardar o merge. Branch/PR empilhado só pode ser usado se estiver explicitamente previsto no envelope.

## Checkpoints obrigatórios

Solicitar orientação quando houver:

- mudança de objetivo, escopo ou critério de aceite;
- decisão arquitetural ou alteração de ADR aceito;
- banco, storage, segurança, permissão, dados sensíveis ou fluxo de aceite;
- deploy, secrets, branch protection ou automerge;
- CI ou área protegida não autorizada no envelope;
- conflito entre candidatos/prioridades;
- dependência não satisfeita;
- falha de validação que exija ampliar escopo;
- necessidade de dado real, credencial ou coordenação externa;
- fim do envelope ou gate de Phase.

O checkpoint deve ser curto: fato observado, impacto, opções e recomendação.

## Pull Requests e merge

Mantém-se como padrão preferencial:

```text
1 Issue -> 1 branch -> 1 PR -> 1 squash merge
```

O loop coordena a seleção de trabalho; ele não agrupa silenciosamente várias Issues no mesmo PR.

O Codex não faz merge automático. A revisão humana e os checks permanecem gates de integração na `main`.

## Alternativas consideradas

### Aprovação humana após todo slice

Rejeitada como regra geral porque cria espera mesmo quando o próximo trabalho já foi planejado e está pronto.

### Um único PR por lote

Rejeitada como padrão porque reduz rastreabilidade e aumenta o diff. Pode existir apenas quando o lote for explicitamente modelado como uma única Issue.

### Autonomia sem envelope

Rejeitada porque permite expansão silenciosa de escopo e decisões sem contexto aprovado.

### Loop por envelope e fila de pull

Escolhida por combinar continuidade, PRs pequenos e checkpoints baseados em risco real.

## Consequências positivas

- reduz aprovações mecânicas;
- mantém Codex produtivo entre slices;
- preserva rastreabilidade por Issue e PR;
- torna motivos de parada explicáveis;
- permite trabalho independente enquanto PR aguarda review;
- concentra participação humana em fronteiras de decisão.

## Consequências negativas / trade-offs

- requer backlog priorizado e dependências minimamente corretas;
- o Codex precisa avaliar conflito entre branches;
- pode haver mais de um PR aberto;
- envelopes vagos podem gerar interpretação divergente;
- revisão humana continua necessária para merge.

## Impacto técnico

### Documentação afetada

- `AGENTS.md`;
- `docs/MODELO_OPERACIONAL_DO_PROJETO.md`;
- `docs/FLUXO_GITHUB_PROJECT.md`;
- `docs/ESTRATEGIA_GIT.md`;
- `docs/ROADMAP.md`;
- `docs/templates/`;
- `docs/traceability/`;
- `docs/uml/`.

### Código, módulos, entidades e rotas

Nenhum código de produto, módulo, entidade ou rota é criado por esta decisão.

### Infraestrutura

Nenhuma automação persistente, runner, fila, CI, deploy ou branch protection é criada por esta decisão.

### Validação

- consistência documental;
- rastreabilidade entre ADRs, fluxo e templates;
- representação UML do loop;
- Structural CI existente.

## Relações

Substitui: nenhum.  
Substituído por: —  
Complementa: ADR-0003 e ADR-0005.  
Complementado por: —  
Relacionado a: ADR-0006 e ADR-0007.

## Critérios para revisão futura

Revisar quando:

- o volume de PRs paralelos gerar conflitos frequentes;
- houver automação real de pull no GitHub Project;
- o Codex passar a operar de forma persistente sem sessão humana;
- a política de merge ou revisão humana mudar;
- métricas mostrarem que envelopes estão amplos ou restritivos demais.

