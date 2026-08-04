# ADR-0019 — Object storage S3-compatible no protótipo local sintético

Status: Proposto
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: storage, s3, minio, protótipo, supply-chain

## Contexto

O ADR-0011 definiu a fronteira S3-compatible e manteve MinIO como candidato
on-prem. A Issue #40, porém, precisa de uma decisão mais estreita antes de
materializar bytes reais: qual uso é aceitável no protótipo local sintético,
quais controles de build e runtime são obrigatórios e quais ambientes ou
classes de dados continuam proibidos.

O checkpoint governante #104 reservou este número para decidir esses limites.
Esta proposta não implementa storage nem ratifica um build específico.

## Pergunta decisória

Em quais limites MinIO, ou outro backend S3-compatible, pode ser usado para
comprovar storage local de originais sintéticos sem antecipar onprem-lab,
produção, dados reais ou uma decisão de distribuição?

## Decisão pendente

Nenhuma implementação passa a ser obrigatória por este documento enquanto o
status permanecer `Proposto`. A decisão será registrada em Issue e PR próprios,
com revisão humana, antes da #40.

## Alternativas a avaliar

- autorizar MinIO construído de source pinado somente no protótipo sintético;
- selecionar outro backend S3-compatible local após análise equivalente;
- adiar object storage até existir alternativa com manutenção e licença mais adequadas.

## Impactos a decidir

- fronteira S3-compatible e isolamento do domínio em relação ao SDK;
- commit, toolchain, digest, SBOM e análise de licença/segurança;
- egress, exposição de portas, credenciais locais e rede do Compose;
- round-trip, integridade, restart e reconciliação;
- gatilhos para nova revisão antes de onprem-lab, produção ou dado real.

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0011.
Complementado por: —
Relacionado a: ADR-0001, ADR-0008, ADR-0010, ADR-0012 e ADR-0014.

## Critérios para aceitação

- análise viva do upstream, licença, manutenção e advisories;
- limites de protótipo e proibições explicitamente registrados;
- responsabilidades do ADR separadas das evidências concretas da #40;
- revisão humana e atualização dos contratos/mapas afetados.
