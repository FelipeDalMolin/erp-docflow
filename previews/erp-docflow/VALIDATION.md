# Verificação da cópia pública — 20/11/2026

- Referência de interface: v35, commit local `c6818ea22439e382870f4f83f8878e3af703c77a`.
- Node 24.22.1: 15 arquivos de testes públicos, com base vazia e dados sintéticos.
- Cobertura: 12 rotas, bootstrap/restauração, isolamento do armazenamento, classificação
  e composição, calendário, períodos, gráficos, documentos, bancos, tarefas e
  estados de conciliação/documentação. `node checks/run.mjs` executa o conjunto.
- Sintaxe JavaScript, imports estáticos, manifesto e hashes amCharts 5.22.0 conferidos.
- Lote inicial de classificações vazio; catálogo público sem origem ou mapeamentos
  da planilha privada. A auditoria local compara identificadores, fontes, hashes,
  nomes e referências privadas sem publicar os marcadores utilizados.
- Documentos originais, contas/movimentos reais, evidências de classificação,
  relatórios de importação, configurações de hosting e histórico privado excluídos.
- Mudanças restritas à prévia e à nota factual em `docs/project/PROJECT_STATUS.md`.

A evidência desta cópia usa testes sintéticos e DOM controlado. Os testes privados
que dependem dos extratos não foram copiados. Não houve homologação mobile, bancária,
integração com backend, merge ou novo deploy do Site nesta entrega.
