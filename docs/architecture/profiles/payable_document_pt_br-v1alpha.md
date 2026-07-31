# Profile `payable_document_pt_br/v1alpha`

Status: candidato, não implementado nem promovido
Envelope: Issue #92
Slice de origem: Issue #43

## Resultado pretendido

O profile governa o primeiro percurso documental PDF-first do produto. Ele
descreve como documentos sintéticos de contas a pagar serão observados,
reconhecidos, extraídos, validados e enviados para revisão. Ele não autoriza
dados reais, autoaceite, efeito financeiro ou escolha de provider.

## Entradas e limites

- PDF born-digital, PDF somente imagem e PDF híbrido;
- PNG e JPEG documentais;
- idioma `pt-BR`;
- até 20 MiB e 20 páginas;
- um job pesado em execução no host `small-cpu-lab`.

DOCX, TXT, TIFF, planilhas, e-mail, layout e tabelas não pertencem ao
`v1alpha`. Um arquivo fora do profile termina com `UNSUPPORTED_FORMAT`, nunca
com interpretação vazia.

## Campos e regras de aplicabilidade

O schema versionado em
[`extraction.schema.json`](../../../profiles/payable_document_pt_br/v1alpha/extraction.schema.json)
preserva valor bruto, valor normalizado, aplicabilidade e evidências para o
tipo e os campos:

- tipo, número e emissor do documento;
- CNPJ do emissor ou beneficiário;
- emissão e vencimento;
- valor total e moeda.

Invoice exige emissor, CNPJ, número, emissão, vencimento e valor. Payment slip
permite emissão não aplicável. Receipt permite CNPJ, número e vencimento não
aplicáveis, desde que a ausência seja explícita. `OTHER` sempre segue para
revisão. Essas condições são executáveis no rule pack
[`validation-rules.json`](../../../profiles/payable_document_pt_br/v1alpha/validation-rules.json),
separadas do contrato estrutural de extração.

## CNPJ numérico e alfanumérico

As fixtures cobrem os CNPJs numéricos existentes e o formato alfanumérico
adotado em 2026. As 12 primeiras posições podem conter letras e números, e os
dois dígitos verificadores permanecem numéricos. O valor normalizado continua
string; nunca é convertido para inteiro nem perde letras ou zeros.

Fonte primária: [Receita Federal — CNPJ
Alfanumérico](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/cnpj-alfanumerico).

## Fronteira entre capability e decisão

O task graph declara candidates, não vencedores:

1. #82 avalia probe e texto nativo;
2. uma policy versionada produz `NativeTextAssessment`;
3. #83 compara candidatos de OCR somente quando `OCR_REQUIRED`;
4. regras determinísticas extraem e validam os campos;
5. routing envia todos os documentos do `v1alpha` para revisão.

Docling e estrutura de tabelas não entram enquanto layout, reading order e
tables forem `false`. Nenhum resultado de benchmark vira integração sem uma
`PromotionDecision` humana e a revisão aplicável do ADR-0016.

## Evidência e falha

Cada campo deve apontar o documento, a versão, o artefato e a página/trecho ou
região realmente disponível. Texto nativo sem coordenadas não recebe bounding
box inventada. Original e derivados permanecem distintos.

Corrompido, criptografado, MIME divergente, limite excedido, campo ausente e
conflito possuem reason codes próprios. Output vazio ou parcial não constitui
sucesso.

O PDF protegido usa Standard Security Handler Revision 2 e senha sintética
`erp-docflow`, registrada também no manifest. O PDF corrompido possui catálogo
e xref deliberadamente inválidos. A confirmação dos reason codes contra o
probe candidato continua pertencendo ao spike #82.

## Dataset e reprodução

O dataset em `datasets/payable_document_pt_br/v1alpha` é inteiramente
sintético, usa seed `20260731` e separa famílias antes de gerar variantes para
impedir leakage entre development, validation e test.

São 28 fixtures em 20 famílias: 6 born-digital válidas, 6 scans, 4 imagens, 2
híbridas e 10 cenários de falha/limite. `scenario_group` representa esse
recorte de aceitação; `modality` descreve a mídia física, inclusive quando um
PDF born-digital foi mutado para um cenário de falha.

```bash
python3 tools/document_fixtures/generate.py --check
python3 tools/document_fixtures/validate.py \
  --dataset payable_document_pt_br/v1alpha
python3 -m unittest discover -s tools/document_fixtures/tests
```

Cada ground truth contém um `expected_output` que valida diretamente contra o
schema de extração; casos bloqueados antes da interpretação usam
`expected_output: null`. O manifest registra SHA-256 e tamanho tanto do
documento quanto do ground truth.

Os comandos não acessam rede. A política de aceitação está em
`benchmarks/payable_document_pt_br/v1alpha/acceptance.json`; não alcançar um
target produz rejeição ou `INCONCLUSIVE`, nunca relaxamento silencioso. O
conjunto de teste possui somente quatro famílias; portanto macro-F1 permanece
explicitamente `INCONCLUSIVE` até existir a amostra mínima declarada, sem
transformar um corpus pequeno em alegação estatística.

O fixture de resource limit viola simultaneamente 20 MiB e 20 páginas. Ele
prova o bloqueio agregado deste profile, não as duas fronteiras isoladamente;
os contract tests de intake da #84 devem cobrir `max`, `max+1` e cada limite
independente.
