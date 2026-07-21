# Ambientes

- **Classe:** runbook e baseline operacional de ambientes
- **Estado:** vigente, com itens planejados explicitamente qualificados
- **Atualizar quando:** host, WSL, CI, runtime ou estratégia on-prem mudar

Este projeto seguirá uma estratégia **on-prem first**, com evolução **cloud-like**.

O objetivo é permitir desenvolvimento local simples, validação em CI, execução futura em ambiente on-prem e possibilidade de expansão híbrida.

## 1. Visão geral

Ambientes previstos:

```text
local
ci
onprem-lab
prod-onprem
```

O projeto começa pelo ambiente local e pelo ambiente CI. O `onprem-lab` é o alvo do candidato R1 Golden Month com dataset sintético/anonimizado; `prod-onprem` e dados reais exigem gates posteriores.

Ambientes de produção e laboratório on-prem serão documentados antes de serem automatizados.

## 2. Ambiente local

O ambiente `local` é a máquina de desenvolvimento.

Uso:

- escrita de código;
- escrita de documentação;
- execução de testes locais;
- execução futura com Docker Compose;
- uso de VS Code;
- uso de Git;
- uso de GitHub CLI;
- uso de Codex;
- criação de branches e PRs.

Ferramentas previstas:

- VS Code;
- Git;
- GitHub CLI (`gh`);
- Docker;
- Docker Compose;
- Python;
- Node.js;
- pnpm;
- uv;
- Codex extension ou Codex CLI.

## 3. Diretriz WSL para múltiplos projetos

A máquina pode ter mais de um projeto usando WSL.

A diretriz inicial é **não criar uma distribuição WSL para cada projeto**.

O padrão será usar uma distribuição Ubuntu principal como ambiente técnico compartilhado e isolar os projetos por pasta, ambiente virtual, versão Node, Docker Compose, variáveis de ambiente e diretórios de dados.

Distribuição principal atual, conforme ADR-0004 e o runbook detalhado:

```text
Ubuntu-20.04
```

Alvo possível, somente mediante migração controlada em Issue própria:

```text
Ubuntu-24.04
```

A distribuição `docker-desktop` pertence ao Docker Desktop e não deve ser usada como shell principal de desenvolvimento.

### 3.1 Diretórios padrão

Código do projeto:

```text
~/projetos/erp-docflow          # WSL pessoal/genérica
/srv/apps/erp-docflow           # host operacional app-host
```

O path não é uma decisão arquitetural do produto. Quando existir inventário do host, como `/srv/ops/projects.yml`, ele é a fonte operacional para o checkout daquela máquina. Os exemplos com `~/projetos` continuam sendo o padrão portátil para uma WSL pessoal.

Logs brutos de execução Codex:

```text
~/codex-runs/erp-docflow
```

Dados operacionais e documentos fora do Git:

```text
E:\erp-docflow-data
```

No WSL:

```text
/mnt/e/erp-docflow-data
```

### 3.2 Regra de separação

```text
Código e execução técnica: WSL
Documentos, exports e backups: disco Windows dedicado
Versionamento: GitHub
Containers: Docker Desktop com integração WSL2
```

### 3.3 Quando criar uma WSL dedicada

Criar uma distribuição WSL dedicada apenas quando houver motivo real, como:

- dependências incompatíveis entre projetos;
- necessidade de simular ambiente on-prem-lab isolado;
- stack muito diferente;
- requisito forte de segurança ou separação;
- experimentos destrutivos;
- necessidade de export/import independente;
- operação contínua separada do ambiente de desenvolvimento.

Enquanto o projeto estiver no bootstrap R0 e antes de um `onprem-lab` isolado ser exigido pelo R1, a WSL principal compartilhada é suficiente.

Documento detalhado: [WSL multi-projetos](WSL_MULTI_PROJETOS.md).

## 4. Ambiente CI

O ambiente `ci` será executado no GitHub Actions.

Uso:

- validar estrutura do repositório;
- validar documentação obrigatória;
- rodar lint;
- rodar testes;
- validar build;
- validar configuração de Docker Compose;
- futuramente validar migrações.

O CI estrutural nasceu na Phase 0 e deve evoluir junto das fontes canônicas.

Validações iniciais:

- verificar existência de arquivos essenciais;
- verificar estrutura de `docs/`;
- verificar templates;
- verificar ADR index;
- verificar traceability baseline.

Validações futuras:

- backend lint;
- backend tests;
- frontend lint;
- frontend typecheck;
- frontend build;
- migration checks;
- Docker Compose config;
- testes de integração.

## 5. Ambiente onprem-lab

O ambiente `onprem-lab` será um ambiente local dedicado ou servidor pequeno para comprovar instalação e operação controlada do candidato R1. Ele não equivale a produção.

Uso:

- testar execução contínua;
- testar Docker Compose;
- testar banco;
- testar object storage;
- testar workers;
- testar backup;
- testar restore;
- executar o Golden Month com dataset sintético/anonimizado;
- validar TLS/lab, smoke, E2E, atualização, rollback e diagnóstico;
- validar comportamento fora da máquina de desenvolvimento.

O bundle do piloto é distinto do Compose de desenvolvimento. Tika e OCR só entram quando suas capabilities estiverem aprovadas e não podem bloquear o caminho XLSX/CSV + manual do Golden Month.

Exemplos possíveis:

- mini PC;
- notebook dedicado;
- workstation;
- servidor local;
- NAS com suporte a containers.

Requisitos estimados Atual/Futuros:

```text
CPU: 4 a 8 cores
RAM: 8 GB / 16 GB recomendado
Disco: SSD/NVMe
Sistema: WSL / Ubuntu Server LTS
Docker: sim
Backup: obrigatório
```

## 6. Ambiente prod-onprem

O ambiente `prod-onprem` será o ambiente futuro de produção on-prem.

Uso:

- execução real do ERP/GED;
- armazenamento oficial dos documentos;
- banco principal;
- storage principal;
- workers;
- logs;
- auditoria;
- backup;
- restore;
- acesso controlado.

Este ambiente não será criado no início.

Antes de existir produção ou envio externo real, devem existir:

- estratégia de backup;
- estratégia de restore;
- estratégia de secrets;
- estratégia de logs;
- estratégia de atualização;
- branch protection;
- CI mínimo;
- documentação operacional;
- plano de rollback;
- baseline de segurança.

Os critérios observáveis de maturidade estão em [Entrega e aceite do produto](../product/PRODUCT_DELIVERY_AND_ACCEPTANCE.md); o contrato técnico do bundle, fechamento e recuperação está em [Fechamento e entrega técnica](../architecture/ACCOUNTING_CLOSE_AND_DELIVERY.md).

## 7. Estratégia cloud-like

Mesmo sendo on-prem first, o sistema deve usar conceitos cloud-like:

- containers;
- serviços separados;
- object storage;
- variáveis de ambiente;
- logs;
- healthchecks;
- workers;
- filas;
- versionamento;
- CI/CD;
- backup automatizado;
- deploy reproduzível.

On-prem first não significa improvisado. Significa que a operação principal deve poder rodar sob controle local.

## 8. Regras de configuração

Nenhum segredo deve ser salvo no Git.

Usar:

```text
.env.example
```

para documentar variáveis esperadas.

Arquivos `.env` reais devem ficar fora do repositório.

Exemplos de dados que não devem ir para o Git:

- senhas;
- tokens;
- chaves privadas;
- chaves de API;
- credenciais bancárias;
- credenciais de storage;
- certificados privados;
- dados reais de clientes;
- documentos reais.

## 9. Deploy

No início, o deploy será manual.

Fluxo futuro previsto:

```text
main estável
tag/release
instalação manual do bundle candidato em onprem-lab
validação
deploy manual em prod-onprem somente após autorização própria
```

Automação de deploy só deve entrar depois que CI, branch protection e estratégia de backup estiverem maduros.

## 10. Backup e restore

Backup não é opcional para este projeto.

No futuro, devem ser cobertos:

- PostgreSQL;
- object storage;
- arquivos gerados;
- arquivos originais;
- logs relevantes;
- configurações;
- ADRs e documentação via Git.

Restore deve ser testado, não apenas documentado.

## 11. Diretriz final

A ordem de maturidade dos ambientes será:

```text
local funcional
→ CI validando
→ onprem-lab reproduzível
→ prod-onprem controlado
→ híbrido/cloud opcional
```

O projeto não deve saltar diretamente para produção.
