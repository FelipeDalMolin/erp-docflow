# ERP DocFlow — código da prévia

Cópia saneada da interface desenvolvida no Site, registrada pela Issue #117.
Inclui calendário e seleção de período, pendências, planilha de caixa, gráficos,
documentos e contexto, bens, contratos, obrigações, bancos e previsões.
A aplicação inicia com uma empresa genérica, sem contas, saldos, lançamentos,
documentos, obrigações ou tarefas. Cadastros posteriores ficam no navegador.

## Executar

Na raiz desta pasta, usando Python 3 já instalado:

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Abra http://127.0.0.1:8765. Sirva `dist` como raiz; não abra o HTML diretamente.
Não é necessário instalar pacotes ou compilar. Para verificar com Node 22+:

```sh
node checks/run.mjs
```

## Origem e limites

- Base GitHub: `1739ffbc4da7f3dbf9e55b5c66eabc091a4c0fef`.
- Código local de referência: `c6818ea22439e382870f4f83f8878e3af703c77a`, de 20/11/2026 (v35).
- O histórico privado não foi copiado. Um novo commit contém apenas arquivos revisados.
- `apps/web`, backend, persistência e gates do produto não foram integrados a esta prévia.
- Não há login de aplicação, sincronização entre dispositivos, OCR real, conector bancário
  ou publicação automática. O Site privado permanece independente desta branch.
- O código amCharts permanece em 5.22.0, com licença e marca preservadas.
- As referências bancárias são o retrato de pesquisa do código original, não uma nova
  homologação de API. Nenhuma credencial acompanha esta cópia.

## Dados excluídos

Não foram copiados `dist/sources`, a base financeira original `dist/data.js`,
`dist/import-audit.json`, a fixture real de outubro, testes que incorporavam valores
ou identificadores reais, o importador pontual dependente dos arquivos particulares,
README histórico com detalhes de importações, configurações locais ou metadados de hosting.
O `data.js` público contém somente a base vazia e os mesmos cálculos reutilizáveis.

Os testes conservados usam exemplos inteiramente fictícios. Novas verificações cobrem
base vazia, rotas e comportamento com dados sintéticos. Elas não certificam os antigos
extratos nem substituem validação visual em navegador ou aparelhos Android/iOS.
O armazenamento desta versão usa nomes próprios para não reutilizar dados de outra prévia.

Antes de um futuro envio, confira também o conteúdo de JS, JSON, testes e documentação:
ignorar PDFs/OFX não basta para excluir dados derivados. Não substitua a base pública
por uma exportação real. O `.gitignore` é uma proteção adicional, não uma auditoria.

## Requisitos preservados

Valores em centavos inteiros; fontes e identificadores preservados nas operações.
Entradas e saídas em grupos separados, saldo ao fundo, slider nativo de período,
seleção distinta do zoom e vínculos explícitos dos lançamentos às fontes.
Previsão não é dívida, sugestão não é conciliação e concluir tarefa não liquida obrigação.
Para gráficos, consulte a documentação compatível com amCharts 5.22.0 e os hashes em
`dist/vendor/amcharts5-5.22.0/manifest.json`; não remova a marca da biblioteca.

## Atualização de 20/11/2026 — v35

A mesma branch agora preserva classificação e divisão dos movimentos, cadastro e
correspondência do plano contábil, hierarquia Entradas/Saídas → Classificação →
Lançamentos, períodos futuros sem extrato e página de obrigações com atividades.
Inclui contexto e classificação nos cards, cores consistentes por direção/banco,
título riscado por conciliação financeira e alertas documentais independentes.

O lote de classificações aplicadas aos dados reais foi substituído por um lote
vazio. O catálogo público conserva classificações genéricas editáveis, sem hashes,
localizações ou correspondências da planilha privada; a referência a uma associação
específica foi generalizada. As decisões e o catálogo originais permanecem no Site.
O comportamento da interface foi preservado; os dados iniciais públicos continuam
vazios. A conversão previsão → obrigação e a Inbox continuam etapas futuras.

Regras visuais: [PADRAO-VISUAL.md](docs/PADRAO-VISUAL.md).
Consulta e projeção: [FLUXO-PLANEJAMENTO.md](docs/FLUXO-PLANEJAMENTO.md).
