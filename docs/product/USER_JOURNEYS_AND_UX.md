# Jornadas de usuário e UX

- **Classe:** baseline planejado de experiência do produto
- **Estado:** planejado, não implementado
- **Issue de origem:** #73
- **Atualizar quando:** arquitetura de informação, jornada, estado, requisito de acessibilidade ou limite do piloto mudar

## 1. Finalidade

Este documento define a experiência mínima necessária para tornar o [piloto Golden Month](PILOT_VERTICAL_SLICE.md) compreensível e operável. Ele não define rotas, componentes, framework frontend, design system nem permissões implementadas.

As regras de domínio e processamento permanecem na [Arquitetura](../architecture/ARCHITECTURE.md), no [Pipeline documental](../architecture/DOCUMENT_PIPELINE.md) e no [Baseline de dados](../architecture/DATA_MODEL_BASELINE.md).

## 2. Princípios de experiência

1. **Contexto persistente:** entidade, período, visão e filtros ativos permanecem visíveis.
2. **Proveniência próxima:** origem e decisões ficam acessíveis a partir do valor, não em relatório técnico separado.
3. **Exceção acionável:** erro explica impacto, motivo e ação possível.
4. **Autoridade visível:** candidato, gerencial, revisado e fechado não usam a mesma aparência sem qualificação.
5. **Progressive disclosure:** a pessoa vê primeiro a ação e o risco; detalhes de provider, regra e tentativa ficam em painel técnico expansível.
6. **Teclado e densidade:** fluxos de revisão e matriz devem suportar trabalho repetitivo sem depender apenas de mouse.
7. **Estado recuperável:** atualizar a página ou retornar à tarefa não deve apagar filtros, mapping ou rascunho já persistido.
8. **Sem falso sucesso:** processamento parcial, warning e pendência não aparecem como concluídos.

## 3. Arquitetura de informação conceitual

Os nomes são áreas de experiência; não cristalizam URLs ou boundaries técnicos.

| Área planejada | Pergunta que responde | Conteúdo mínimo |
| --- | --- | --- |
| Visão geral | como está a entidade no período? | previsto, realizado, pendências, cobertura, diferenças e acesso ao fechamento |
| Importações e Inbox | o que entrou e em qual estado? | fontes, lotes, documentos, progresso, preview, mapping e erros |
| Revisão | o que exige decisão? | fila priorizada, evidência, proposta, validações e ações permitidas |
| Livro e agenda | o que ocorreu ou precisa ocorrer? | fatos, obrigações, liquidações, vencimentos, estados e conciliação |
| Matriz e relatórios | como analisar e explicar os números? | filtros, visões salvas, agregações e drill-through |
| Dossiês | o que está relacionado a uma entidade de negócio? | timeline, documentos, contratos, fatos, vínculos e pendências |
| Fechamento | o período pode ser encerrado e entregue? | checklist, cobertura, bloqueios, snapshot, pacote e protocolo |
| Sistema | a instalação está saudável? | versão, serviços, jobs, limites e diagnóstico autorizado |

A navegação deve destacar o trabalho pendente e o contexto atual, não a tecnologia usada para processá-lo.

## 4. Jornada de importação estruturada

```text
selecionar fonte
  -> confirmar entidade e período
  -> visualizar amostra
  -> mapear colunas
  -> validar
  -> confirmar lote
  -> acompanhar processamento
  -> revisar resumo e exceções
```

Requisitos:

- mostrar arquivo, hash, versão e origem;
- detectar cabeçalho e tipos sem gravar silenciosamente;
- permitir corrigir mapping antes de confirmar;
- apresentar valores bruto e interpretado;
- identificar erro por célula/linha e erro do lote;
- separar warning de bloqueio;
- informar importadas, aceitas, pendentes, rejeitadas e duplicadas;
- permitir baixar ou copiar relatório de erros;
- preservar mapping versionado para replay controlado;
- nunca esconder linhas descartadas por filtro ou parser.

## 5. Jornada de revisão

```text
abrir fila
  -> escolher item
  -> comparar origem e proposta
  -> examinar validações e conflitos
  -> aceitar, corrigir, rejeitar ou reprocessar
  -> justificar quando exigido
  -> avançar ao próximo item elegível
```

### Layout funcional

- evidência ou origem em uma região;
- campos, valores e vínculos propostos em outra;
- valor bruto, normalizado e aceito distinguíveis;
- página, linha ou região realçada quando existir coordenada;
- mensagens de validação junto ao campo afetado;
- alternativas e conflitos visíveis;
- histórico e painel técnico acessíveis sem dominar a tela;
- ação principal e consequência claramente nomeadas.

Bounding boxes só aparecem quando o artefato realmente possuir coordenadas. Texto nativo sem posição não deve produzir destaque inventado.

Ações de aceite e override seguem o [ADR-0013](../adr/0013-human-review-acceptance-and-override.md). A interface não concede autoridade que a política de acesso não concedeu.

## 6. Jornada de análise e drill-through

```text
selecionar entidade/período
  -> aplicar visão e filtros
  -> examinar total ou célula
  -> abrir ocorrências componentes
  -> abrir decisão e origem
  -> retornar sem perder contexto
```

Requisitos:

- filtros ativos e unidade monetária visíveis;
- cabeçalhos, totais e congelamento visual adequados a matriz densa;
- comportamento previsível de ordenação e seleção;
- estado da visão preservado;
- total identifica quantidade de ocorrências e cobertura de evidência;
- valor provisório ou incompleto é qualificado;
- exportação, quando existir, registra visão, filtros, período e versão.

Uma planilha é referência de familiaridade para densidade e navegação; não é o modelo permanente da interface nem a fonte canônica do produto.

## 7. Jornada de fechamento

```text
abrir checklist
  -> revisar cobertura e bloqueios
  -> resolver ou justificar pendências permitidas
  -> confirmar autoridade e período
  -> gerar snapshot
  -> gerar pacote e protocolo
  -> acompanhar entrega ou retorno
```

Requisitos:

- distinguir bloqueio de recomendação;
- mostrar diferença, cobertura e itens sem evidência;
- impedir confirmação acidental ou duplicada;
- exibir consequências antes do fechamento;
- registrar versão, responsável, horário e justificativas;
- tornar correção posterior um fluxo explícito de nova versão/reabertura;
- permitir verificar integridade do pacote gerado.

## 8. Vocabulário visual de estado

| Estado de produto | Comunicação mínima |
| --- | --- |
| recebido | origem registrada; processamento ainda não iniciado |
| em processamento | etapa atual e progresso determinado ou indeterminado |
| candidato | resultado automático ou importado ainda não aceito |
| pendente | ação necessária, responsável quando conhecido e motivo |
| conflito | sinais incompatíveis que impedem decisão automática |
| revisado | decisão humana registrada, sem implicar fechamento |
| aceito | interpretação válida para uma finalidade definida |
| fechado | pertence a snapshot versionado do período |
| falhou | etapa, reason code, possibilidade de retry e próximo passo |
| quarentena | acesso/uso bloqueado e orientação segura, sem expor conteúdo indevido |

Cor nunca deve ser o único meio de comunicar estado. Labels técnicas e de produto não devem usar a mesma palavra com semânticas diferentes.

## 9. Estados obrigatórios por experiência

Toda área interativa deve especificar e testar:

- carregando;
- vazia com orientação útil;
- sucesso;
- sucesso parcial;
- warning;
- erro recuperável;
- erro não recuperável;
- sem permissão;
- bloqueada por dependência;
- dado desatualizado ou versão sucedida;
- ação em andamento e prevenção de duplo envio.

Falhas devem apresentar correlation ID seguro quando útil ao suporte, sem revelar stack trace, path interno, secret ou conteúdo sensível.

## 10. Acessibilidade e responsividade

Mínimo planejado:

- HTML semântico e nomes acessíveis;
- ordem de foco coerente e foco visível;
- navegação e ações principais por teclado;
- associação entre erro, instrução e campo;
- contraste e estado independentes apenas de cor;
- anúncios adequados de progresso e erro;
- tabelas com cabeçalhos e leitura compreensível;
- zoom e reflow sem perda de ação essencial;
- alvos de toque adequados para consultas em tela menor.

O produto é desktop-first para importação, revisão e matriz. Telas menores devem permitir consulta e ações essenciais, sem prometer paridade de densidade antes de teste de uso.

## 11. Painel técnico expansível

Quando autorizado, pode mostrar:

- origem, hash e versão;
- job, attempt e correlation ID;
- perfil/política e versões;
- capability, adapter/modelo e configuração;
- regra/validator e reason codes;
- latência, retry e artefatos relacionados.

Apache Tika, OCR ou modelo não devem aparecer como estado principal. A pessoa vê “texto original aproveitado”, “OCR necessário”, “revisão necessária” ou “falha de inspeção”; detalhes técnicos permanecem disponíveis para diagnóstico.

## 12. Critérios de aceite de UX do piloto

- a pessoa sempre identifica entidade, período e autoridade da visão;
- nenhuma ação destrutiva ou de fechamento ocorre sem consequência explícita;
- importação apresenta preview e erros por linha;
- revisão permite chegar à evidência e registrar decisão;
- drill-through retorna ao relatório sem perder contexto;
- estados obrigatórios foram projetados e testados;
- fluxo principal funciona por teclado em desktop;
- testes automatizados e revisão manual de acessibilidade cobrem as experiências entregues;
- nenhuma tela afirma capacidade que o backend e a política não implementaram.

Targets, ferramentas de teste e comandos pertencem às Issues de implementação.

## 13. Fora de escopo

- definir URLs ou nomes de endpoints;
- selecionar biblioteca de componentes;
- criar design system completo ou Storybook;
- fechar identidade visual;
- desenhar todas as modalidades futuras;
- implementar colaboração em tempo real;
- substituir decisão de RBAC/ABAC;
- tratar mock ou wireframe como produto implementado.
