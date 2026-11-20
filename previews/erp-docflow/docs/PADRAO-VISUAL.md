# Padrão visual e conciliação — v34

A cor financeira mantém o significado em calendário, agenda, listas, planilha,
obrigações e gráfico: entradas em verde, saídas em vermelho/terracota e saldo
em azul acinzentado. Tarefas usam azul, previsões usam rótulo violeta e borda
tracejada, vencimentos usam rótulo âmbar. O tipo não muda o sentido financeiro.
A seleção de navegação é azul; hoje tem preenchimento próprio e rótulo Hoje.

Na v35, a borda esquerda dos cards de pendências segue o sentido financeiro,
com o tom do banco quando há uma única conta identificada. Tarefas e conferências
de cobertura bancária usam azul. A urgência permanece no rótulo de status, sem
substituir a cor do assunto na borda.

`dist/visual-theme.js` centraliza a paleta compartilhada com amCharts;
`dist/visual-theme.css` aplica a mesma linguagem às demais visualizações.
Os tons de cada banco dependem da identidade da conta, nunca da posição no
filtro. O gráfico conserva barras positivas/negativas, saldo ao fundo e sliders.

## Título riscado e triângulo

O título riscado significa **conciliação financeira**. Valor e data continuam
legíveis. O triângulo âmbar indica documentação ou conferência pendente, com
descrição acessível e explicação nos detalhes. As duas indicações podem coexistir.
O usuário não precisa interpretar a cor sozinha: há rótulos e legenda.

- Um movimento só é conciliado quando tem vínculo confirmado com uma obrigação
  ativa da mesma empresa, conta e sentido compatíveis, data realizada válida e
  valor dentro do compromisso. Importação ou mera semelhança não confirmam vínculo.
- Um pagamento parcial pode estar conciliado como movimento; a obrigação só
  recebe o risco quando os vínculos compatíveis cobrem exatamente seu total.
  Excedentes e vínculos incompatíveis continuam a conferir.
- Documento ausente, bloqueado ou não revisado e classificação não revisada
  permanecem sinalizados. O extrato de origem não substitui um comprovante.
- A presença de um documento revisado não garante a suficiência documental da
  operação: a prévia ainda não possui requisitos documentais configuráveis.
- A tarefa concluída continua com seu próprio estado; reconhecer uma previsão
  não significa conciliar. Nada é confirmado ou alterado ao renderizar.
- No calendário, obrigações resolvidas com alertas continuam visíveis. Sem
  alertas, podem ser ocultadas pelo filtro de concluídos. Movimentos do extrato
  seguem visíveis para preservar a leitura cronológica e os totais do período.

O módulo `record-presentation.js` apenas interpreta vínculos e revisões já
existentes. Esta etapa não implementa a conversão previsão → obrigação nem um
novo procedimento de conciliação. Não cria tarefas, revisa documentos, altera
classificações ou efetua baixas automaticamente.

## Verificação

`checks/record-presentation.mjs` cobre conciliação, parcial/excedente, empresa,
conta, sinal, datas, documentação, escape HTML, ausência de mutações, estabilidade
dos tons e contraste do texto. As verificações existentes cobrem calendário,
hierarquia financeira, controle, obrigações, importação, classificação e gráfico.
