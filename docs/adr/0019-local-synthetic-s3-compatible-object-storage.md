# ADR-0019 — Object storage S3-compatible no protótipo local sintético

Status: Aceito com revisão
Data: 2026-08-04
Decisores: FelipeDalMolin
Tags: storage, s3, minio, protótipo, supply-chain

## Contexto

O ADR-0011 definiu a fronteira S3-compatible e manteve MinIO como candidato
on-prem. A Issue #40 precisa de uma decisão mais estreita antes de materializar
bytes reais: qual uso é aceitável no protótipo local sintético, quais controles
de build e runtime são obrigatórios e quais ambientes ou classes de dados
continuam proibidos.

Na verificação de 2026-08-04, o repositório oficial `minio/minio` estava
arquivado e o próprio upstream o declarava sem manutenção. A distribuição
comunitária passou a ser source-only, sob AGPLv3, enquanto binários históricos
deixaram de receber atualizações. A última release pública marcada como `latest`
era de 2025-10-15, anterior a advisories High publicados em 2026. Esses fatos
impedem tratar o MinIO comunitário como baseline mantido ou seguro por padrão.

O checkpoint #104 aceita um uso temporário e estritamente contido para que a
#40 possa avaliar o round-trip S3-compatible de originais sintéticos. A decisão
não ratifica release, commit, patchset, imagem ou licença para distribuição.

## Evidências primárias consultadas

| Fonte oficial | Fato observado | Consequência para esta decisão |
| --- | --- | --- |
| [repositório `minio/minio`](https://github.com/minio/minio) e [README no último commit público observado](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/README.md) | repositório arquivado, sem manutenção, source-only e S3-compatible | uso limitado a exceção local; não presumir manutenção ou correções futuras |
| [licença AGPLv3](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/LICENSE) e [compliance upstream](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/COMPLIANCE.md) | obrigações de licença precisam ser avaliadas para a aplicação e distribuição concretas | SBOM e análise de licença são gates; esta ADR não constitui parecer jurídico |
| [release comunitária mais recente](https://github.com/minio/minio/releases/tag/RELEASE.2025-10-15T17-29-55Z) | artefato público anterior aos advisories de 2026 | binários legados e referências flutuantes não são fontes admissíveis para a #40 |
| [GHSA-hv4r-mvr4-25vw](https://github.com/minio/minio/security/advisories/GHSA-hv4r-mvr4-25vw), [GHSA-9c4q-hq6p-c237](https://github.com/minio/minio/security/advisories/GHSA-9c4q-hq6p-c237), [GHSA-h749-fxx7-pwpg](https://github.com/minio/minio/security/advisories/GHSA-h749-fxx7-pwpg) e [GHSA-3rh2-v3gr-35p9](https://github.com/minio/minio/security/advisories/GHSA-3rh2-v3gr-35p9) | advisories High afetam releases OSS e apontam correções posteriores ou AIStor | a #40 deve registrar disposition por advisory; isolamento reduz exposição, mas não equivale a correção |
| [`go.mod` do source observado](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/go.mod) e [documentação oficial de toolchains Go](https://go.dev/doc/toolchain) | source declara Go 1.24 e toolchain 1.24.8; toolchain pode ser obtida automaticamente | commit, toolchain e modo de obtenção devem ser pinados; o build não pode depender de atualização implícita |
| [`Dockerfile`](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/Dockerfile) e [`Dockerfile.release`](https://github.com/minio/minio/blob/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/Dockerfile.release) upstream | usam imagens ou downloads mutáveis, incluindo `latest` | a #40 deve manter receita própria, com bases, ferramentas e downloads pinados por versão e digest |

As referências registram o snapshot que sustentou a decisão. A #40 deve
capturá-las novamente, pois advisories e opções de distribuição podem mudar
mesmo com o repositório comunitário arquivado.

## Decisão

### Escopo autorizado

MinIO OSS é autorizado como exceção temporária de risco somente para comprovar,
em execução standalone/single-node local e isolada, o round-trip S3-compatible
de originais sintéticos da #40.

Esta autorização não se estende a dados reais, `onprem-lab`, produção,
exposição remota, distribuição do produto ou uso como serviço compartilhado.
Outro backend ou ampliação desse limite exige revisão arquitetural antes da
mudança.

### Fronteira e isolamento

- domínio e aplicação dependem do contrato S3-compatible, nunca de tipos ou
  semântica proprietária do MinIO;
- o endpoint do storage existe somente em rede interna dedicada do ambiente
  descartável ou de desenvolvimento autorizado;
- nenhuma porta do storage ou console é publicada no host;
- o runtime não possui egress;
- o processo roda sem root, com capabilities removidas e filesystem raiz
  somente leitura, exceto pelo volume sintético explicitamente gravável;
- a credencial da aplicação é local, aleatória e limitada ao bucket
  necessário; a credencial administrativa é segregada e nunca reutilizada
  pelo adapter; nenhuma delas entra em Git, logs ou artifacts;
- somente fixtures exclusivamente sintéticas e explicitamente autorizadas
  podem ser persistidas.

### Admissão de supply chain

A implementação da #40 deve:

- selecionar source por SHA completo e registrar eventual patchset/fork;
- pinar versão/build; módulos por versão ou pseudo-versão e `go.sum`;
  toolchain Go por versão exata e checksum/digest do artefato ou imagem;
  imagens-base por digest; sem `latest`, binários legados ou atualização
  automática;
- construir uma imagem controlada pelo ERP-DocFlow, sem reutilizar
  Dockerfiles upstream com referências mutáveis;
- produzir digest do binário e da imagem, SBOM de ambos, análise de licença e
  scans de source, dependências e imagem;
- registrar a disposition de cada advisory aplicável, distinguindo correção,
  mitigação testada e risco residual;
- retornar `CHECKPOINT` se um achado Critical/High aplicável não tiver correção
  verificável, mitigação testada e aceite humano explícito do risco residual.

Sem essas evidências, a autorização desta ADR não torna o candidato elegível.
Isolamento e dados sintéticos são controles compensatórios, não prova de
correção de vulnerabilidade.

### Política versus evidência de implementação

Esta ADR governa limites e critérios. A #40 deve registrar os fatos concretos:

- commit e patchset escolhidos;
- toolchain, módulos e imagens-base;
- digests do binário e da imagem;
- SBOM, licença, scans e disposition dos advisories;
- Compose final e prova de ausência de host ports e egress;
- contrato do subconjunto S3 utilizado;
- round-trip, hash/integridade, restart e reconciliação.

Digest ou commit concreto não pertence ao ADR porque pode mudar sem alterar a
política arquitetural.

## Alternativas consideradas

### MinIO OSS local com contenção e evidência reforçadas

Aceita somente nos limites desta ADR. Preserva a fronteira S3-compatible e
permite uma prova sintética sem apresentar o upstream arquivado como solução
operacional definitiva.

### Binário legado ou imagem pronta com tag flutuante

Rejeitada. Os artefatos comunitários históricos não recebem atualizações e não
fornecem a proveniência exigida pelo checkpoint.

### Filesystem local como implementação direta do domínio

Rejeitada para a #40 porque eliminaria a prova da fronteira S3-compatible e
criaria outro contrato de persistência.

### AIStor ou outro backend S3-compatible

Não avaliada por esta decisão. Licença, manutenção, distribuição e operação
exigem Issue e revisão próprias antes de substituir o candidato.

## Consequências positivas

- mantém a aplicação portátil atrás do contrato S3-compatible;
- permite comprovar o ciclo mínimo com dados sem valor real;
- torna provenance, licença, vulnerabilidades e isolamento parte do aceite;
- impede que evidência de protótipo seja promovida silenciosamente a produção.

## Consequências negativas / trade-offs

- o upstream comunitário arquivado mantém risco residual elevado;
- build, SBOM, scans e análise por advisory aumentam o custo da #40;
- controles compensatórios não transformam código sem manutenção em baseline
  seguro;
- uma conclusão negativa na #40 pode exigir novo backend e novo checkpoint;
- obrigações AGPLv3 dependem de análise jurídica do uso e da distribuição
  concretos.

## Impacto técnico

### Documentação afetada

- ADR catalog e mapas de rastreabilidade;
- contrato de intake/storage e runbooks serão atualizados pela #40 quando
  existirem evidências concretas.

### Código, módulos, entidades e rotas

Nenhum nesta decisão. A futura implementação fica atrás de adapter
S3-compatible e não cria dependência MinIO no domínio.

### Infraestrutura

Nenhuma é criada por esta ADR. A #40 será responsável pelo build controlado,
rede interna, runtime single-node e volume sintético.

### Testes necessários na #40

- contrato do subconjunto S3 efetivamente usado;
- ausência de host ports, console exposto e egress;
- execução non-root e filesystem/capabilities esperados;
- round-trip com hash, falhas, restart e reconciliação;
- controles que sustentem cada disposition de advisory.

## Relações

Substitui: nenhum.
Substituído por: —
Complementa: ADR-0011.
Complementado por: —
Relacionado a: ADR-0001, ADR-0008, ADR-0010, ADR-0012 e ADR-0014.

## Revisão futura obrigatória

### Motivo da revisão futura

O upstream comunitário está arquivado, a distribuição é source-only, existem
advisories sem correção OSS pública verificável e o impacto da AGPLv3 depende
do uso e da distribuição concretos.

### Fase ou condição de revisão

- durante a #40, antes de admitir commit, patchset ou imagem concretos;
- novamente antes de `onprem-lab`, dado real, produção, exposição remota ou
  distribuição do produto.

### Gatilhos que podem mudar a decisão

- novo advisory ou mudança de severidade/disposition;
- indisponibilidade de source corrigido e auditável;
- alternativa S3-compatible mantida com licença mais adequada;
- necessidade de suporte, escala, alta disponibilidade ou operação contínua;
- mudança de licença, distribuição, classe de dados ou boundary de rede.

### Impactos previstos

Pode substituir o backend, exigir novo ADR, alterar build/Compose, backup,
restore, credenciais e operação. Não altera o contrato S3-compatible sem nova
decisão explícita.
