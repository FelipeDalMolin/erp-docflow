# Arquitetura do frontend

Status: baseline executável da Phase 1, slice S1.03.

Este documento descreve o frontend mínimo do ERP DocFlow. Código, testes e o
lockfile são a evidência do que existe; o roadmap em `/system` é apenas
informativo e não representa capacidades entregues.

## Escopo atual

O R0 oferece um shell responsivo com três resultados de rota:

- `/`: apresentação da fundação técnica;
- `/system`: configuração pública visível e roadmap não interativo;
- `*`: estado de rota não encontrada.

A navegação principal contém somente Início e Sistema. Não existem nesta fase
Inbox, Documentos, Revisão, autenticação, dados reais, cliente GED ou chamadas
remotas. `VITE_API_BASE_URL` possui fallback para `http://localhost:8000`, mas é
somente configuração pública exibida em `/system`.

## Organização e ownership

```text
src/
├── app/                 composição da aplicação, router e shell
├── features/            páginas e comportamento por capacidade
├── shared/              estilos, tokens e utilidades sem regra de produto
└── test/                preparação compartilhada do ambiente de testes
```

### `app`

É responsável pela inicialização, composição do router, layout persistente,
landmarks e navegação de primeiro nível. O arquivo `app/router.tsx` é o registro
único de ownership de rotas. O shell não conhece regras documentais nem estado
remoto.

### `features`

Cada diretório representa uma capacidade visível e possui sua página de rota.
Uma feature pode compor elementos de `shared`, mas não deve importar detalhes
internos de outra feature. Nesta baseline existem `home`, `system` e
`not-found`; os nomes de capacidades futuras mostrados no roadmap não criam
features implícitas.

### `shared`

Contém recursos reutilizáveis sem regra de produto. Os tokens CSS semânticos
definem superfícies, texto, bordas, foco, feedback, tipografia, espaçamento,
raios e sombras. Componentes futuros só devem entrar aqui quando houver uso
real em mais de uma feature; esta slice não tenta antecipar um design system.

## Estados de interface

As features devem distinguir estados por significado e não apenas por cor:

| Estado | Representação esperada |
| --- | --- |
| loading | região identificada, texto de progresso e, quando aplicável, `aria-live`; nunca conteúdo falso |
| empty | contexto da coleção vazia e próxima ação válida, sem tratar ausência como erro |
| error | mensagem útil, correlação segura e recuperação proporcional; nenhum dado sensível |
| not found | página real para rota desconhecida e retorno para Início; implementada no R0 |
| permission denied | explicação do limite de acesso sem revelar o recurso; depende de auth futura |

Loading, empty, error e permission denied são padrões aprovados para evolução,
não telas ou fluxos implementados agora. Uma feature deve materializar apenas
os estados que seu contrato e sua fonte de dados tornam possíveis.

## Estado e fluxo de dados

- **Estado local:** interação efêmera pertencente ao componente ou à feature.
  No R0, a interface é essencialmente estática e não adota biblioteca global.
- **Estado de URL:** rota, parâmetros e filtros compartilháveis pertencem ao
  React Router. Estado que precise sobreviver a refresh ou link direto não deve
  ficar escondido somente em memória local.
- **Estado remoto futuro:** cache, revalidação e mutações serão escolhidos numa
  slice que possua API e critérios concretos. TanStack Query, cliente GED, MSW e
  abstrações genéricas não fazem parte desta baseline.

Não deve haver duplicação automática de estado entre componente, URL e cache
remoto. A fonte é escolhida conforme duração, compartilhamento e autoridade.

## Contratos com o backend

FastAPI e Pydantic são a fonte inicial dos contratos HTTP. Quando houver
integração remota, uma especificação OpenAPI versionada e governada deverá ser
publicada como artefato de contrato; somente então tipos e cliente poderão ser
gerados de forma reproduzível.

O frontend não pode:

- importar ou espelhar modelos de persistência;
- criar tipos TypeScript ou schemas Zod concorrentes como segunda fonte de
  verdade do mesmo contrato;
- inferir saúde da API pela presença de `VITE_API_BASE_URL`;
- transformar falhas de rede em afirmações sobre estado de negócio.

Mudanças incompatíveis devem passar pelo versionamento do contrato e por testes
de compatibilidade, em vez de ajustes independentes nas duas aplicações.

## Acessibilidade

O shell usa landmarks `nav`, `main` e `footer`, um `h1` por página, link de
salto para o conteúdo e `aria-current="page"` na navegação ativa. Todo fluxo
implementado deve funcionar por teclado e manter foco visível. Ordem de tab,
nome acessível e destino do foco são parte do contrato dos componentes.

Contraste, seleção e feedback não dependem somente de cor. Textos devem
continuar legíveis com zoom e reflow; ícones decorativos permanecem ocultos da
árvore acessível; movimentos respeitam `prefers-reduced-motion`. O roadmap é
conteúdo editorial em `article`, sem aparência ou semântica de controle.

## Responsividade

O layout parte de uma largura mínima de 320 px. Em viewport largo, a navegação
fica numa sidebar persistente e o conteúdo respeita largura máxima. Em
viewports intermediário e estreito, a navegação vira uma faixa superior, grids
passam para duas ou uma coluna e nenhuma região exige rolagem horizontal.

A verificação mínima inclui 320 px, 768 px e 1440 px, zoom a 200%, reflow,
ordem de leitura e alvos de navegação. Breakpoints respondem ao espaço do
conteúdo, não a modelos específicos de dispositivo.

## Estratégia de testes

- **Unidade:** transformação ou utilidade isolada com resultado observável.
- **Componente:** conteúdo, nome acessível, estados e interação com Testing
  Library, priorizando consultas por role.
- **Rotas:** render de `/`, `/system` e caminho desconhecido em memory router,
  incluindo navegação por teclado e ausência de capacidades futuras no menu.
- **Gates locais:** ESLint 10, TypeScript 7 em modo strict, Vitest 4 e build do
  Vite 8 devem passar com o lockfile congelado.

O ESLint 10 analisa o subconjunto ECMAScript/JSX utilizado pelos arquivos
TypeScript desta baseline por meio do parser nativo Espree. O TypeScript 7 é o
gate responsável por sintaxe e semântica de tipos. Essa separação é deliberada
porque, na data desta baseline, o parser TypeScript normalmente adotado ainda
não declarava compatibilidade com TypeScript 7; sintaxe exclusiva de tipos que
o Espree não compreenda exige reavaliar o parser antes de ser introduzida.

Testes de integração remota e contrato serão adicionados apenas quando houver
um cliente gerado e um serviço integrado. Testes não devem simular capacidades
que o produto ainda não possui.

## Fontes e autoridade

A Issue #35 e a documentação canônica versionada no repositório definem o
contrato desta implementação. A base local de conhecimento foi consultada como
contexto de produto e proveniência. Os identificadores abaixo são abreviados,
mas preservam prefixo e sufixo suficientes para busca no índice local.

| Origem | Fonte selecionada | Identificador | Uso nesta baseline |
| --- | --- | --- | --- |
| ChatGPT | `Análise de Repositórios e Lógica` | `6a567502…e43d` | limites do shell e distinção entre direção de produto e capacidade real |
| ChatGPT | `Gestão Documental Inteligente` | `6a4e98e1…7280` | proveniência, evidência e evolução documental por fases |
| ChatGPT | `Alinhamento de foco ERP` | `69f10309…b901` | direção on-prem first, rastreabilidade e revisão humana |
| ChatGPT | `Modo Plan do Codex` | `6a27ebf3…7e3a` | slices verificáveis, ownership e checkpoints por PR |
| Codex | plano do relatório para a UI da Phase 1 | rollout `019f4d83…769e` | rotas `/` e `/system`, navegação mínima e ausência de Inbox no R0 |
| Codex | envelope governado e workspace da Phase 1 | rollout `019f6b1d…523f` | sequência #33–#37, contratos e fronteiras #34/#35 |

Chats selecionados orientaram linguagem e evolução por capacidades; não
constituem contrato nem prova de implementação. Em divergência, prevalecem a
Issue aprovada, ADRs aceitos, documentação canônica e evidência executável.

## Critério de evolução

Uma nova capability entra na navegação somente quando possuir Issue aprovada,
ownership, contrato, estados, acessibilidade e testes verificáveis. Roadmap não
reserva rota nem autoriza antecipação de dependências.
