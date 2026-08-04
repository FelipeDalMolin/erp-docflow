# ADR-0022 — Documentação viva e rastreabilidade da implementação

Status: Proposto
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: documentação, rastreabilidade, conceitos, uml, evidência

## Contexto

O ADR-0006 exige ADRs e mapas, mas a evolução recente mostrou que documentos
preparados durante um PR podem permanecer descrevendo `em revisão` depois do
merge. Também faltam referências de implementação que expliquem como, onde e
por que conceitos, classes, estados, falhas e testes colaboram na `main`.

O checkpoint #104 reservou esta decisão para formalizar fontes, derivados,
registries e evidência pré/pós-merge sem criar uma segunda fonte operacional.

## Pergunta decisória

Como o projeto liga significado, decisão, implementação, testes, diagramas e
histórico de entrega, e quais validações impedem drift sem versionar renders ou
snapshots temporários como autoridade?

## Decisão pendente

Esta proposta não cria MkDocs, registries, UML, grafo ou novo check. Enquanto
`Proposto`, ela apenas reserva a pergunta e sua relação com a governança atual.

## Alternativas a avaliar

- referências de implementação e registries versionados com site derivado;
- somente Markdown e mapas manuais, sem registry verificável;
- portal externo como autoridade documental.

## Impactos a decidir

- precedência entre ADR, contrato, glossário, registry, código, teste e PR;
- schemas de work/concept registry e campos estáveis versus operacionais;
- formato das referências de implementação e regra de atualização por slice;
- MkDocs, PlantUML, grafo, pins, determinismo e retenção de artifacts;
- registros separados de execução pré-merge e integração pós-merge.

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0006.
Complementado por: —
Relacionado a: ADR-0003, ADR-0005, ADR-0017 e ADR-0018.

## Critérios para aceitação

- matriz de autoridade e gatilhos de atualização inequívocos;
- fontes editáveis separadas de outputs derivados;
- evidência pós-merge e pós-cutover obrigatória;
- validações e build reproduzível definidos;
- revisão humana antes de tornar a documentação CI obrigatória.
