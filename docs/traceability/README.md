# Rastreabilidade

- **Classe:** índice derivado
- **Estado:** vigente
- **Fonte de classificação:** [portal documental](../README.md)

Esta pasta conecta decisões, documentação, módulos, entidades, rotas, diagramas, Issues e Pull Requests.

## 1. Hierarquia de fontes

Quando houver divergência:

```text
ADR aceito
  -> documento canônico vigente
  -> mapa de rastreabilidade
  -> diagrama
  -> review/registro de descoberta
```

- ADR `Proposto` representa decisão pendente.
- Documento `planejado` orienta descoberta, não contrato implementado.
- Código/testes descrevem comportamento real quando existirem, mas não substituem decisão arquitetural necessária.
- Chat não deve permanecer como única fonte de decisão.

## 2. Perguntas que os mapas respondem

- qual ADR justifica esta direção?
- o status permite implementação?
- qual documento define o conceito?
- qual módulo/entidade será afetado?
- qual UML representa o fluxo?
- que outros artefatos precisam mudar?
- qual Issue/PR introduziu a mudança?

## 3. Mapas

| Arquivo | Finalidade |
| --- | --- |
| [ADR index](adr-index.md) | ADRs, status, relações e condição de revisão |
| [Decision map](decision-map.md) | dependências entre decisões |
| [Document map](document-map.md) | documentos, classes, autoridade e relações |
| [Module map](module-map.md) | boundaries planejados/implementados |
| [Entity map](entity-map.md) | conceitos/entidades, estados e ADRs |
| [Route map](route-map.md) | rotas reais quando existirem |
| [Impact matrix](impact-matrix.md) | checklist de artefatos afetados por tema |

## 4. Status de produto

Usar de forma explícita:

| Status | Significado |
| --- | --- |
| planejado | desenho para decisão/implementação futura |
| não implementado | não existe em código/infra |
| parcial | existe apenas no slice indicado |
| implementado | existe, tem validação e referência de PR |
| substituído | artefato/decisão sucedido, preservado no histórico |

Não registrar módulo, entidade ou rota como implementado sem evidência no repositório.

## 5. Quando atualizar

Atualizar os mapas quando houver mudança em:

- ADR ou status;
- documento canônico;
- módulo/boundary;
- entidade/estado;
- rota/contrato;
- workflow;
- diagrama UML;
- infraestrutura;
- segurança/LGPD;
- provider/modelo com impacto estrutural;
- integração;
- Issue/PR que materialize conceito planejado.

## 6. Procedimento mínimo

1. identificar decisão e status;
2. abrir Issue com escopo e critérios;
3. atualizar fonte canônica;
4. atualizar mapas afetados;
5. atualizar/renderizar UML quando aplicável;
6. validar links, nomes e guardrails;
7. relacionar PR e ADR.

## 7. Diretriz final

A rastreabilidade deve ser leve, mas suficiente para impedir decisões invisíveis e para explicar o impacto de mudar o `DocumentEnvelope`, o fluxo de review, um provider ou um efeito financeiro.
