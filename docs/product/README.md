# Produto

- **Classe:** índice canônico de produto
- **Estado:** planejado, não implementado
- **Issue de origem:** #73
- **Atualizar quando:** um baseline de produto for criado, substituído, movido ou mudar de responsabilidade

Este diretório organiza a direção de produto do `erp-docflow`: qual problema resolver, qual primeiro resultado utilizável entregar, como a pessoa interage com esse resultado e o que significa entregá-lo. Ele não substitui arquitetura, ADRs, roadmap, status ou evidência de implementação.

O estado corrente continua em [Status do projeto](../project/PROJECT_STATUS.md). Código, testes e contratos executáveis são a evidência do que realmente existe.

## Documentos

| Pergunta | Fonte primária | Responsabilidade primária |
| --- | --- | --- |
| Qual resultado o produto busca e quais são seus limites? | [North Star do produto](PRODUCT_NORTH_STAR.md) | problema, atores, fluxo de valor, princípios e medidas de resultado |
| Qual é o primeiro recorte utilizável ponta a ponta? | [Piloto vertical Golden Month](PILOT_VERTICAL_SLICE.md) | cenário, entradas, sequência, dependências e aceite funcional do piloto |
| Como as pessoas percorrem o produto? | [Jornadas e UX](USER_JOURNEYS_AND_UX.md) | arquitetura de informação conceitual, jornadas, estados e requisitos de uso |
| O que o usuário/operador deve receber e que resultado observável comprova o aceite? | [Entrega e aceite](PRODUCT_DELIVERY_AND_ACCEPTANCE.md) | destinatários, unidades de entrega, níveis de maturidade e critérios observáveis de aceite |

## Relação com as demais fontes

| Tema | Fonte de autoridade |
| --- | --- |
| ordem, fases e gates | [Roadmap](../project/ROADMAP.md) |
| estado atual e próxima condição | [Status do projeto](../project/PROJECT_STATUS.md) |
| boundaries e componentes planejados | [Arquitetura](../architecture/ARCHITECTURE.md) |
| etapas e artefatos do processamento | [Pipeline documental](../architecture/DOCUMENT_PIPELINE.md) |
| conceitos e invariantes documentais | [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md) |
| capabilities e adapters candidatos | [Estratégia de providers](../architecture/PROVIDER_STRATEGY.md) |
| contrato técnico de fechamento, package, bundle, topologia e operação | [Fechamento e entrega técnica](../architecture/ACCOUNTING_CLOSE_AND_DELIVERY.md) |
| motivo e status de uma decisão | [Catálogo de ADRs](../adr/README.md) |
| execução de Issues e uso do Codex | [Fluxo do GitHub Project](../operations/FLUXO_GITHUB_PROJECT.md) |

Se houver divergência, não combinar regras silenciosamente. Usar a fonte primária da pergunta, verificar o ADR aplicável e registrar a correção em Issue.

## Trilhas de leitura

### Entender o produto

1. [North Star do produto](PRODUCT_NORTH_STAR.md)
2. [Piloto vertical Golden Month](PILOT_VERTICAL_SLICE.md)
3. [Jornadas e UX](USER_JOURNEYS_AND_UX.md)
4. [Entrega e aceite](PRODUCT_DELIVERY_AND_ACCEPTANCE.md)
5. [Roadmap](../project/ROADMAP.md)

### Refinar uma slice

1. localizar o resultado do usuário neste diretório;
2. verificar fase e gate no [Roadmap](../project/ROADMAP.md) e no [Status](../project/PROJECT_STATUS.md);
3. usar a fonte arquitetural especializada para entradas, saídas e invariantes;
4. verificar ADRs aplicáveis;
5. tornar o escopo verificável conforme o [Fluxo do GitHub Project](../operations/FLUXO_GITHUB_PROJECT.md).

## Estrutura

```text
docs/product/
├── README.md
├── PRODUCT_NORTH_STAR.md
├── PILOT_VERTICAL_SLICE.md
├── USER_JOURNEYS_AND_UX.md
└── PRODUCT_DELIVERY_AND_ACCEPTANCE.md
```

## Regra de manutenção

- manter aqui somente resultado, jornada, piloto e entrega;
- referenciar arquitetura e ADRs em vez de copiar suas decisões;
- não declarar rota, endpoint, tabela, biblioteca ou provider como implementado;
- marcar hipóteses, capacidades e telas futuras como planejadas;
- não transportar fatos de uma planilha ou exemplo histórico para o contrato do produto sem validação;
- atualizar links e a matriz de autoridade no mesmo PR que alterar a estrutura.
