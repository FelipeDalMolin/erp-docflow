# Harness reproduzível de experimentos

- **Classe:** contrato executável de engenharia
- **Estado:** implementado para `integrity_probe/v1`
- **Issue:** [#88](https://github.com/FelipeDalMolin/erp-docflow/issues/88)
- **Envelope:** [#92](https://github.com/FelipeDalMolin/erp-docflow/issues/92)
- **Atualizar quando:** schema, candidate registry, formato do bundle ou controles mudarem

## Finalidade

O harness transforma um `ExperimentManifest` versionado em uma execução não interativa e
um bundle verificável. Ele registra os inputs, commit, dependency lock, ambiente, controles,
resultados e digests necessários para reproduzir e revisar uma evidência experimental.

Esta implementação não é o pipeline do aplicativo. Ela não recebe uploads, não extrai texto,
não executa OCR, não grava em PostgreSQL/MinIO e não promove provider. A única execução
disponível é `integrity_probe/v1`, que abre os bytes reais das 28 fixtures sintéticas e seus
ground truths para recalcular SHA-256 e tamanho.

## Contratos

Os schemas ficam em `experiments/schemas/v1alpha/`:

| Contrato | Responsabilidade |
| --- | --- |
| `ExperimentManifest` | inputs, candidate, classificação, limites e seleção de fixtures |
| `BenchmarkRun` | fatos observados, provenance, recursos, status e reason code |
| `ArtifactBundle` | inventário fechado de artifacts com SHA-256 e tamanho |
| `PromotionDecision` | forma de uma decisão humana posterior; nunca criada pelo runner |

O manifest não aceita comando shell, URL, import path ou plugin arbitrário. O campo
`candidate.id` precisa existir no registry fechado do código. Um candidate futuro entra por
Issue própria e testes contratuais antes de poder ser referenciado.

## Preparação

Requisitos:

- Python `3.13.14`;
- uv `0.11.16`;
- Linux com `renameat2(RENAME_NOREPLACE)` para publicação atômica do bundle;
- Git disponível para capturar commit e estado do worktree;
- execução a partir da raiz de um worktree Git do repositório;
- nenhum acesso de rede durante validação, smoke ou verificação.

Instale somente o ambiente travado do package:

```bash
uv sync --locked --project tools/experiment_harness
```

O package não possui dependência de runtime externa. Pytest, Ruff e mypy pertencem apenas ao
grupo de desenvolvimento. O backend Hatchling `1.29.0` está fixado no build-system e no grupo
`build`; ambos os grupos padrão são resolvidos no `uv.lock`, sem faixa flutuante. O próprio
`pyproject.toml` recusa versões de uv diferentes de `0.11.16`.

## Validar o manifest

```bash
uv run --project tools/experiment_harness erp-docflow-experiment validate-manifest \
  --manifest experiments/payable_document_pt_br/v1alpha/harness-smoke.json
```

A validação resolve apenas paths confinados ao repositório, confirma profile/dataset/policy,
classificação sintética, candidate, controles, o lock registrado para o candidate e a contagem
das fixtures. Manifest ausente, campo desconhecido, path traversal, dado real, egress,
concorrência diferente de um ou candidate desconhecido falham fechados.

## Executar o smoke real

Use sempre um diretório novo sob `.artifacts/experiments/`:

```bash
uv run --project tools/experiment_harness erp-docflow-experiment run \
  --manifest experiments/payable_document_pt_br/v1alpha/harness-smoke.json \
  --output .artifacts/experiments/harness-smoke
```

O output é ignorado pelo Git e contém:

```text
artifact-bundle.json
benchmark-run.json
events.jsonl
experiment-manifest.json
fixture-results.json
```

O runner lê cada arquivo e ground truth incrementalmente. Ele não grava cópia dos documentos,
texto, identificadores ou conteúdo em artifacts/log. Os eventos têm campos allowlisted. O
`BenchmarkRun` registra se o worktree estava limpo; executar com alterações locais é permitido
para diagnóstico, mas essa condição fica explícita na evidência.

Os JSONs governantes são parseados e digeridos a partir da mesma captura estável de bytes. As
aberturas percorrem componentes com `O_NOFOLLOW`; o subprocesso Git usa argumentos fixos,
ambiente mínimo e desativa `core.fsmonitor` e hooks do checkout.

`host_class` é derivado dos limites observados de CPU/RAM/GPU declarada. Uma execução arbitrária
não recebe o rótulo-alvo `small-cpu-lab`: por exemplo,
`observed-cpu-3-memory-5gib-gpu-not-declared`. O target permanece na acceptance policy e só pode
ser associado a uma classe elegível por decisão humana posterior.

O output nunca é sobrescrito. Para repetir, use outro ID/diretório ou mova o bundle anterior por
um procedimento consciente e rastreável. O harness não possui comando de limpeza.

Durante a execução, os artifacts ficam em um diretório privado
`.erp-docflow-staging-*`, irmão do destino. Somente depois de criar e verificar o descriptor esse
diretório é publicado atomicamente, sem substituir um destino concorrente. Uma falha de
filesystem/finalização não expõe o path final solicitado; o staging pode permanecer para
diagnóstico consciente.

## Verificar o bundle

```bash
uv run --project tools/experiment_harness erp-docflow-experiment verify-artifact \
  --bundle .artifacts/experiments/harness-smoke
```

A verificação exige nominalmente os quatro artifacts canônicos, recalcula SHA-256 e tamanho e
compara o conjunto completo de arquivos. Artifact obrigatório ausente, modificado, extra,
duplicado, symlink ou path inseguro encerra com código diferente de zero. O comando também
retorna o SHA-256 do próprio `artifact-bundle.json`; preserve esse digest junto da evidência
externa que referencia o bundle. O descriptor é lido como contrato; ele não inventaria evidência
ausente.

Quando o candidate falha depois de criar o staging, o harness persiste `BenchmarkRun` com
`FAILED` e reason code, inventaria os artifacts produzidos, publica o bundle factual e retorna
código diferente de zero. Retorno vazio, incompleto, duplicado, fora de ordem ou com facts não
allowlisted também vira falha; nunca aparece como sucesso vazio.

## Checks da slice

```bash
uv run --project tools/experiment_harness ruff check tools/experiment_harness
uv run --project tools/experiment_harness mypy --strict tools/experiment_harness/src
uv run --project tools/experiment_harness pytest tools/experiment_harness/tests
```

Além desses checks, a geração/validação original da #43 continua obrigatória para garantir que
o harness não mascarou mudança no dataset:

```bash
python3 tools/document_fixtures/generate.py --check
python3 tools/document_fixtures/validate.py --dataset payable_document_pt_br/v1alpha
python3 -m unittest discover -s tools/document_fixtures/tests
```

## Extensão por #82 e #83

Tika e candidatos OCR não devem ser adicionados por configuração local. Cada Issue precisa:

1. implementar um adapter importável, com request/response e erros tipados;
2. registrar o candidate em código, sem shell/import arbitrário vindo do manifest;
3. fixar package, engine/modelo, licença, configuração e digests;
4. adicionar testes unitários, contratuais, de timeout/limite e smoke isolado;
5. preservar raw e normalizado como artifacts distintos, sem conteúdo em log;
6. executar sobre o mesmo manifest/splits e registrar recursos do processo completo;
7. produzir evidência para revisão humana.

O `BenchmarkRun` de `integrity_probe/v1` nesta slice registra somente fatos com status
`SUCCEEDED`, `FAILED` ou `INCONCLUSIVE`; ele não recomenda promoção ou rejeição. Candidates
futuros seguem a policy da #43, mas somente uma `PromotionDecision` humana posterior e separada
autoriza candidate/capability/profile/host. Este runner não escreve nem referencia essa decisão,
e o ADR-0016 permanece sujeito ao checkpoint previsto no envelope.

## Limitações atuais

- o peak RSS cobre o processo do harness; providers futuros precisam medir toda a árvore do
  processo isolado em intervalo compatível com a policy;
- `integrity_probe/v1` prova integridade e reproducibilidade do harness, não qualidade de texto;
- não há notebook, worker, fila, API ou interface web nesta slice;
- bundles locais não são release artifacts nem evidência de backup/restore.
