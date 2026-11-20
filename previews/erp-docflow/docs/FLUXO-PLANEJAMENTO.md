# Fluxo livre para consulta e planejamento — v31

O período do Fluxo de caixa não depende mais da presença de extrato. A planilha
aceita datas anteriores ou posteriores ao histórico, pelos campos De/Até,
atalhos Hoje/Próximos 30 dias e navegação do período. Meses futuros do resumo
anual são clicáveis. Abrir o fluxo pelo calendário preserva o intervalo completo.
Trocar a conta conserva um período personalizado; Todos os registros acompanha
a união dos históricos das contas selecionadas, sem cortar pelo banco mais curto.

## Leitura dos valores

- **Entradas/saídas registradas:** apenas movimentos existentes no sistema no
  intervalo. Sem extrato, a ausência de registros não comprova movimento zero.
- **Saldo realizado:** conhecido apenas com cobertura da data nas contas
  selecionadas. Sem base, `null` é apresentado como — e exportado em branco.
  O fechamento conhecido continua válido como abertura do dia seguinte.
- **Referência:** última posição disponível de cada conta até o fim consultado.
  A explicação lista conta, valor e data. Posições podem ter datas diferentes;
  a soma é uma referência parcial, sujeita também aos limites das aplicações.
- **Projeção com obrigações:** referência mais recebimentos pendentes, menos
  pagamentos pendentes, com vencimento após a base de sua conta e até o fim
  selecionado. Inclui compromissos entre a base e o início da janela. Se uma
  conta não tem base conhecida, a projeção conjunta também permanece desconhecida.

Pendências usam vínculos confirmados, da empresa correta e com sentido compatível,
descontando pagamentos parciais em centavos inteiros. Obrigações canceladas não
participam. Compromissos vencidos antes da base bancária e aqueles com vínculos
não confirmados/incompatíveis ficam fora da projeção e são indicados para revisão;
não se presume uma nova data de pagamento. A projeção usa o estado atual dos
vínculos: não é uma reconstrução de como as pendências eram conhecidas no passado.
O cenário usa vencimentos; não altera nem reprograma compromissos.

As previsões por recorrência têm seção própria na planilha e no detalhe diário,
com acesso ao contexto original. Permanecem fora do realizado e da projeção para
não duplicar obrigações semelhantes. O algoritmo existente gera o mês corrente
e os dois seguintes, preservando decisões anteriores. Navegar além desse horizonte
é permitido e mostra obrigações/tarefas cadastradas; não inventa recorrências.

## Preservação e validação

Não há migração financeira: extratos, contas, documentos, classificações, IDs e
decisões locais permanecem intactos. A hierarquia Entradas/Saídas → Classificação
→ Lançamentos é mantida. O gráfico amCharts conserva o modelo de histórico existente.

Na cópia pública, execute `node checks/run.mjs`: base vazia, componentes de
período e fixtures fictícias são verificados sem extratos reais. A suíte privada
de planejamento não acompanha esta exportação. As regras de cálculo acima foram
preservadas no código, sem reaplicar dados privados aos testes.
