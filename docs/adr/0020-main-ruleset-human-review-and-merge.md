# ADR-0020 — Ruleset, revisão humana e método de merge da main

Status: Aceito
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: github, ruleset, review, ci, merge

## Contexto

O ADR-0007 determinou CI estrutural antes de branch protection. O repositório
já possui CI estrutural e CI da aplicação, mas a política documentada ainda não
é imposta pela plataforma. Reviews acionáveis foram registrados depois de
merges, rebase continua habilitado e a `main` não possui ruleset ou branch
protection.

No snapshot de 2026-08-04, existe somente um colaborador direto com permissão
Write ou superior: o próprio autor e administrador `FelipeDalMolin`. O GitHub
não permite que o autor aprove a própria Pull Request. Exigir uma aprovação
formal agora tornaria toda integração insatisfazível sem acrescentar um segundo
colaborador.

O checkpoint #104 reservou esta decisão para transformar o fluxo documentado em
proteção efetiva por dois cutovers, sem exigir checks que ainda não existem nem
apresentar a dependência organizacional como falha técnica.

## Evidências vivas da decisão

| Elemento observado | Estado em 2026-08-04 | Consequência |
| --- | --- | --- |
| `main` | `dc9f171f52759680b0de49a4758a2afc2fdc9ec1` | base da Issue #111 e deste ADR |
| rulesets e regras efetivas | nenhum ruleset; nenhuma regra para `main` | Cutover A precisa criar a proteção, não migrar configuração existente |
| métodos de merge | merge commit desabilitado; squash habilitado; rebase habilitado | Cutover A deve desabilitar rebase e manter somente squash |
| auto-merge | desabilitado | deve permanecer desabilitado |
| colaboradores Write+ | somente `FelipeDalMolin`, papel `admin`; nenhum convite pendente | Cutover A usa zero aprovações formais; Cutover B aguarda segundo revisor |
| checks atuais | cinco contextos verdes pelo GitHub Actions, App ID observado `15368` | podem entrar no Cutover A após revalidação da execução recente |

Os cinco contextos atuais são:

- `Backend / lint and tests`;
- `PostgreSQL / migrations and integration`;
- `Frontend / quality and build`;
- `Compose / configuration`;
- `Validate repository structure and documentation`.

## Decisão

### Regra comum aos dois cutovers

Um ruleset chamado `main-governance`, ativo e dirigido somente a
`refs/heads/main`, será a proteção canônica da branch. Seu estado normal terá
`bypass_actors=[]`.

O ruleset exigirá:

- Pull Request para integrar alterações;
- resolução das conversas de review;
- histórico linear;
- bloqueio de deleção da `main`;
- bloqueio de non-fast-forward/force-push;
- checks obrigatórios com política estrita, mantendo a branch atualizada;
- `allowed_merge_methods=["squash"]`.

As configurações do repositório permanecerão coerentes com o ruleset:

- squash merge habilitado;
- merge commit desabilitado;
- rebase merge desabilitado;
- auto-merge desabilitado.

`allow_update_branch` controla uma sugestão/botão adicional; não implementa o
gate de branch atualizada. A autoridade desse gate será
`strict_required_status_checks_policy=true` com pelo menos um required check.

Aceitar este ADR autoriza a futura Issue operacional do Cutover A na sequência
do checkpoint #104. Não altera agora settings, ruleset, CI ou branch
protection.

### Cutover A — proteção satisfazível

O Cutover A ocorrerá somente depois da aceitação dos ADRs 0019–0022 e da
integração das referências de implementação mínimas. A Issue operacional deve
revalidar o snapshot imediatamente antes da mutação.

Parâmetros da regra de Pull Request:

- `required_approving_review_count=0`;
- `required_review_thread_resolution=true`;
- `dismiss_stale_reviews_on_push=false`;
- `require_code_owner_review=false`;
- `require_last_push_approval=false`;
- `allowed_merge_methods=["squash"]`.

Required checks:

- os cinco contextos atuais listados acima;
- `strict_required_status_checks_policy=true`;
- cada contexto precisa ter concluído com sucesso no repositório nos sete dias
  anteriores ao cutover e possuir nome único/estável;
- workflows obrigatórios devem reportar o contexto em toda Pull Request dirigida
  à `main`; filtros de path, branch ou mensagem que deixem o contexto esperado
  ausente ou indefinidamente `pending` são proibidos;
- Pull Requests devem ter `main` como base desde a abertura; se uma PR for
  redirecionada posteriormente para `main`, ela não pode integrar até um evento
  elegível executar e concluir novamente todos os contextos obrigatórios;
- o produtor GitHub Actions deve ser associado quando a API o suportar e a
  identidade for revalidada; o App ID `15368` é evidência deste snapshot, não
  identificador arquitetural imutável.

Zero aprovações formais não elimina a revisão humana e o squash merge humano
exigidos pelos ADRs 0003, 0017 e 0018. Significa somente que o GitHub ainda não
impõe uma aprovação independente impossível no estado organizacional atual.

### Cutover B — checks novos e aprovação independente

Depois de cada contexto abaixo concluir com sucesso no repositório nos sete
dias anteriores ao cutover, o Cutover B os acrescentará aos required checks:

- `Evaluation / fixtures and harness`;
- `Documentation / validate and build`.

Se existir segundo colaborador humano com Write ou superior:

- `required_approving_review_count=1`;
- `dismiss_stale_reviews_on_push=true`;
- `require_last_push_approval=false`;
- comprovação em PR real de bloqueio sem aprovação e liberação somente depois
  da aprovação e dos checks.

Se continuar existindo somente o autor:

- aprovações formais permanecem em zero;
- `governance_gate=AWAIT_DEPENDENCY`;
- a #40 permanece inelegível mesmo que todos os gates técnicos passem.

Code Owners, merge queue e last-push approval não são introduzidos por esta
decisão.

### Bypass e emergência

Não haverá bypass cotidiano. Uma emergência não cria ator permanente na bypass
list e não autoriza o Codex a desabilitar ou contornar o ruleset.

Qualquer exceção exige ação humana e registro com:

- Issue/incidente e justificativa;
- ator responsável;
- snapshots anterior e posterior;
- delta mínimo, duração e operação executada;
- restauração imediata da política;
- auditoria do resultado.

### Evidência e rollback dos cutovers

Cada cutover deve capturar, sem secrets:

- settings do repositório;
- rulesets brutos e regras efetivas agregadas para `main`;
- colaboradores elegíveis e convites;
- required checks, produtor, execução recente e nomes exatos;
- JSON anterior/posterior, delta e ID do ruleset;
- prova em PR real, incluindo thread quando aplicável.

O rollback restaura os métodos de merge e o ruleset ao snapshot anterior. Se o
Cutover A criar o primeiro ruleset, a Issue operacional deve registrar como
reverter ou remover exatamente esse ID sem afetar outra regra. Erro de
configuração não autoriza bypass silencioso.

## Alternativas consideradas

### Ruleset em dois cutovers

Aceita. Protege imediatamente com checks existentes e separa a dependência
organizacional e os checks ainda inexistentes.

### Proteção única somente ao final

Rejeitada. Manteria a `main` sem enforcement durante todo o checkpoint, apesar
de os cinco checks atuais já serem elegíveis.

### Exigir uma aprovação no Cutover A

Rejeitada no estado atual. O único usuário elegível é o autor, que não pode
aprovar a própria PR. A exigência será ativada no Cutover B quando satisfazível.

### Branch protection clássica

Não selecionada. O ruleset oferece uma política nomeada, alvo explícito,
composição verificável e API adequada aos snapshots/rollback deste checkpoint.

## Consequências positivas

- transforma Issue → PR → checks → conversas resolvidas → squash em enforcement;
- impede rebase, force-push e deleção da `main`;
- mantém Cutover A executável sem esconder a falta do segundo revisor;
- adiciona os checks novos somente depois de existirem e executarem com sucesso;
- torna bypass, evidência e rollback explicitamente auditáveis.

## Consequências negativas / trade-offs

- zero aprovações formais no Cutover A mantém a revisão independente como regra
  processual, não enforcement da plataforma;
- renomear ou omitir um contexto obrigatório pode bloquear merges;
- ruleset configurado incorretamente pode bloquear a `main` até rollback humano;
- administradores continuam tecnicamente capazes de editar a política; a
  governança depende de snapshots e registro de exceções;
- a #40 continuará em `AWAIT_DEPENDENCY` se não surgir segundo revisor até o
  Cutover B.

## Impacto técnico

### Nesta decisão

Somente ADR, catálogo, snapshot canônico e mapas são alterados nos seis paths
da Issue #111. Nenhum workflow, setting, colaborador, branch ou ruleset muda
nesta PR.

### Na futura aplicação

- Cutover A: Issue operacional própria, snapshots, mudança de settings/ruleset
  e prova na primeira PR real subsequente;
- Cutover B: adição dos checks Evaluation/Documentation e, quando satisfazível,
  uma aprovação formal;
- qualquer renomeação de contexto, mudança de método de merge ou política de
  bypass exige reavaliar este ADR.

## Fontes oficiais

- [regras disponíveis em rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets);
- [criação de rulesets e bypass](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository);
- [troubleshooting de required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks);
- [eventos que disparam workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows);
- [métodos de merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github);
- [aprovação de Pull Requests com reviews obrigatórios](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews);
- [API REST de rulesets](https://docs.github.com/en/rest/repos/rules).

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0007.
Complementado por: —
Relacionado a: ADR-0003, ADR-0017 e ADR-0018.

## Revisão futura obrigatória

Revisar esta decisão quando:

- surgir ou deixar de existir segundo colaborador Write+;
- um contexto obrigatório for criado, removido ou renomeado;
- o GitHub Actions deixar de ser o produtor esperado de um check;
- mudar método de merge, estratégia de branches ou necessidade de merge queue;
- ocorrer exceção emergencial ou necessidade recorrente de bypass;
- plano/capacidade do repositório alterar o suporte a rulesets.

Uma revisão pode ajustar parâmetros ou substituir este ADR, mas não reescreve
silenciosamente a evidência dos cutovers já executados.
