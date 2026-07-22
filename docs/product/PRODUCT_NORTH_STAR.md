# North Star do produto

- **Classe:** baseline planejado de produto
- **Estado:** planejado, não implementado
- **Issue de origem:** #73
- **Atualizar quando:** problema, público, resultado, limite ou medida principal de produto mudar

## 1. Finalidade

Este documento define o resultado que orienta o `erp-docflow`. Ele não cria entidades físicas, rotas, permissões, providers nem autorização para operar com dados reais.

A arquitetura de execução permanece em [Arquitetura](../architecture/ARCHITECTURE.md), o modelo documental em [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md) e a ordem de implementação no [Roadmap](../project/ROADMAP.md).

## 2. Resultado orientador

O produto deverá transformar fontes heterogêneas em informações gerenciais revisáveis e rastreáveis, permitindo acompanhar uma operação até sua evidência, decisão, relatório e fechamento.

Princípio orientador:

> Efeito e informação oficial exigem proveniência. Documento é evidência de primeira classe, mas não é a única origem possível.

Uma planilha, um movimento bancário, uma integração ou um lançamento manual auditado também podem originar informação gerencial. Cada origem precisa preservar identidade, autoria, horário, valor recebido, transformações e decisões aplicadas.

## 3. Problemas que o produto deverá resolver

- fontes documentais e estruturadas mantidas em silos;
- consolidações manuais sem linhagem reproduzível;
- previsto, realizado e evidência misturados em uma mesma célula ou arquivo;
- correções que apagam o valor anterior ou não registram justificativa;
- relatórios sem caminho de volta à origem;
- fechamento dependente de conhecimento tácito;
- automação opaca, sem mostrar regra, conflito ou necessidade de revisão;
- entrega técnica que funciona apenas no ambiente de desenvolvimento.

## 4. Atores e necessidades

Os nomes abaixo representam responsabilidades de produto, não papéis de autorização já definidos.

| Ator planejado | Necessidade principal |
| --- | --- |
| operador | importar, organizar, corrigir pendências e acompanhar progresso sem perder linhas ou documentos |
| revisor | comparar evidência e proposta, entender conflitos e registrar decisão justificada |
| gestor | acompanhar previsto, realizado, cobertura e exceções com acesso à origem |
| responsável pelo fechamento | verificar checklist, pendências e produzir uma versão fechada reproduzível |
| contador ou colaborador externo autorizado | receber pacote consistente, devolver ajustes e preservar protocolo |
| administrador operacional | instalar, atualizar, diagnosticar, proteger e recuperar o produto |
| auditor | reconstruir quem fez o quê, com qual fonte, regra, versão e decisão |

Autenticação, segregação e autoridade de cada ação continuam bloqueadas pela estratégia proposta no [ADR-0015](../adr/0015-auth-authorization-security-strategy.md).

## 5. Cadeia de valor planejada

```text
fonte identificada
  -> conteúdo bruto preservado
  -> interpretação candidata
  -> validações e conflitos
  -> decisão humana ou política autorizada
  -> informação gerencial aceita
  -> vínculo ou efeito operacional autorizado
  -> relatório com drill-through
  -> fechamento e pacote versionados
```

O [Pipeline documental](../architecture/DOCUMENT_PIPELINE.md) detalha o ramo de documentos. Fontes estruturadas deverão possuir parsing, mapeamento e validação próprios; não devem ser convertidas em texto livre para imitar OCR.

## 6. Conceitos de produto

| Conceito | Significado nesta baseline | Não significa |
| --- | --- | --- |
| fonte | ocorrência recebida com origem, ator/processo, horário e identificador | apenas um arquivo PDF |
| evidência | referência verificável ao dado bruto, documento, linha, região ou evento que sustenta uma interpretação | verdade automática |
| interpretação candidata | valor, classe, vínculo ou efeito ainda sujeito a validação e decisão | registro oficial |
| informação gerencial aceita | representação aprovada para uma finalidade, preservando versão e proveniência | escrituração contábil automática |
| fato gerencial | nome conceitual para uma ocorrência analisável de receita, despesa, obrigação, recebimento, pagamento, ajuste ou transferência | entidade ou tabela já definida |
| fechamento | snapshot versionado de um período, com cobertura, pendências, decisões e pacote | apagar ou sobrescrever o histórico anterior |

O nome e o schema físico desses conceitos exigem refinamento de domínio e, quando aplicável, ADR. `AcceptedSnapshot` e `EntityLink` continuam com o significado definido no [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md).

## 7. Princípios de produto

1. **Origem neutra:** a regra de negócio não pressupõe que todo fato nasceu de OCR.
2. **Evidência antes do efeito:** interpretação candidata não produz efeito sensível sem gate aplicável.
3. **Original preservado:** correção cria nova decisão ou versão; não reescreve silenciosamente a origem.
4. **Exceção visível:** falha, ausência, ambiguidade e conflito recebem estado e motivo.
5. **Autoridade explícita:** toda visão informa se é candidata, gerencial, revisada ou fechada.
6. **Drill-through:** total e célula agregada devem chegar aos fatos e evidências que os compõem.
7. **Automação mensurável:** regras e modelos são promovidos por evidência reproduzível, não por catálogo de tecnologia.
8. **On-prem first:** o primeiro produto utilizável deve poder operar sob controle local, conforme o [ADR-0001](../adr/0001-on-prem-first-cloud-like.md).
9. **Revisão proporcional ao risco:** revisão humana segue política, sensibilidade e conflito, conforme o [ADR-0013](../adr/0013-human-review-acceptance-and-override.md).

## 8. Primeiro limite utilizável

O primeiro produto utilizável é o [piloto vertical Golden Month](PILOT_VERTICAL_SLICE.md): uma entidade e um período completos, com importação estruturada, tratamento de exceções, informação gerencial, relatório rastreável, fechamento e entrega.

Processamento documental avançado agrega evidência e reduz trabalho manual, mas não bloqueia esse piloto. O produto começa import-first e manual-assisted, mantendo contratos para automatização posterior.

## 9. Fora do compromisso desta baseline

- substituir sistema contábil oficial ou banco;
- decidir automaticamente efeito financeiro sensível;
- tratar score de modelo como verdade;
- exigir OCR para toda fonte;
- definir todas as modalidades fiscais, contábeis e contratuais no primeiro piloto;
- habilitar provider externo ou dado real sem segurança e residência aprovadas;
- prometer produção, alta disponibilidade ou escala sem testes operacionais;
- declarar telas, APIs, schemas ou módulos como implementados.

## 10. Medidas orientadoras

| Medida | Direção esperada |
| --- | --- |
| cobertura de origem | toda informação aceita possui referência verificável à fonte e às transformações |
| descarte silencioso | nenhuma linha, documento ou falha desaparece sem estado e motivo |
| reconciliação | diferenças são zero ou explicitamente classificadas e justificadas |
| tempo de fechamento | redução mensurável frente ao processo de referência |
| retrabalho | correções recorrentes e causas ficam mensuráveis por perfil e origem |
| autonomia com controle | tarefas de rotina avançam sem esconder decisões que exigem revisão |
| reprodutibilidade | uma versão fechada e seu pacote podem ser reconstruídos a partir das referências registradas |

Targets numéricos, dataset e método de medição pertencem ao piloto ou à Issue de implementação, não a esta direção estável.

## 11. Relações

- [Piloto vertical Golden Month](PILOT_VERTICAL_SLICE.md)
- [Jornadas e UX](USER_JOURNEYS_AND_UX.md)
- [Entrega e aceite](PRODUCT_DELIVERY_AND_ACCEPTANCE.md)
- [Arquitetura](../architecture/ARCHITECTURE.md)
- [Roadmap](../project/ROADMAP.md)
- [Gestão Documental Inteligente](../reviews/GESTAO_DOCUMENTAL_INTELIGENTE.md), como evidência histórica e não fonte normativa
