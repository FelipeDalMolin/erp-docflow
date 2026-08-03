# erp-docflow

Plataforma ERP/GED **on-prem first**, com arquitetura **cloud-like**, para transformar fontes heterogêneas em informação gerencial auditável, preservando evidências, revisão, aceite, fechamento e operação documental.

Status atual: **Phases 0 e 1/R0 encerradas; primeira persistência PDF-first materializada pela #39**. A revisão atual acrescenta domínio puro, PostgreSQL, migrations, idempotência e auditoria transacional; storage de bytes, upload HTTP e telas continuam nas slices #40–#42.

Esse avanço **ainda não é o ERP funcional no navegador**. Os repositórios da #39 persistem somente metadados sintéticos fornecidos por um `VerifiedOriginalDescriptor`, mas ainda não são acionados por uma rota HTTP. A slice não armazena nem recupera o PDF, não expõe upload e não interpreta documentos. Essas provas dependem das slices posteriores e de seus próprios critérios de aceite.

Consulte o [status do projeto](docs/project/PROJECT_STATUS.md) para o gate ativo e o [portal da documentação](docs/README.md) para escolher a fonte correta.

## Visão do fluxo

```text
fonte documental, estruturada, manual ou integrada
  -> conteúdo bruto e origem preservados
  -> interpretação candidata + evidências
  -> validação e revisão proporcional ao risco
  -> fato gerencial ou vínculo autorizado
  -> relatório com drill-through
  -> fechamento, pacote e auditoria
```

## Documentação principal

| Entrada | Finalidade |
| --- | --- |
| [Portal da documentação](docs/README.md) | trilhas de leitura, matriz de autoridade, classes e manutenção |
| [Direção do produto](docs/product/README.md) | north star, piloto Golden Month, jornadas e critérios de entrega |
| [Status do projeto](docs/project/PROJECT_STATUS.md) | fase atual, evidências, gate e fila candidata |
| [Roadmap](docs/project/ROADMAP.md) | escopo permanente, dependências e resultados das fases |
| [Arquitetura](docs/architecture/ARCHITECTURE.md) | visão lógica planejada, boundaries e dados |
| [ADRs](docs/adr/README.md) | decisões arquiteturais e seus status |
| [Rastreabilidade](docs/traceability/README.md) | relações derivadas entre decisões e artefatos |

## Executar e validar o ambiente local

- [Validação local equivalente ao Application CI](docs/operations/VALIDACAO_LOCAL_CI.md): instala dependências travadas e executa os mesmos checks de backend, frontend e Compose usados pela CI.
- [Compose de desenvolvimento](docs/operations/DEVELOPMENT_COMPOSE.md): inicia PostgreSQL interno, API em `127.0.0.1:8100` e shell web em `127.0.0.1:5180`, sem publicar a porta `5432`.

O shell web ainda demonstra apenas que a fundação técnica executa. Ele não contém as telas e os fluxos de um ERP e não processa PDFs; a evidência desta revisão está na camada de domínio/persistência e nos testes PostgreSQL da #39, ainda sem integração com o runtime HTTP.

## Guardrails

- não trabalhar diretamente na `main`;
- seguir Issue → branch → PR → CI → revisão humana → squash merge;
- permitir que o Codex puxe o próximo slice pronto dentro de envelope aprovado, sem nova autorização mecânica;
- não iniciar uma slice apenas porque sua Phase, release ou Epic está aberta: a slice deve estar especificada, com condições verificadas e dentro de envelope aprovado;
- não transformar proposta ou diagrama planejado em contrato implementado;
- não alterar ADR aceito como documento vivo;
- não usar dados reais, secrets ou providers externos sem decisão e controles aplicáveis.

O fim de um slice não é, sozinho, um gate. Mudança de direção, risco, dependência ou área protegida exige checkpoint; merge permanece humano.

Consulte [AGENTS.md](AGENTS.md) antes de executar uma Issue com Codex. O `README` apresenta o projeto; ele não substitui a fonte especializada de cada regra.
