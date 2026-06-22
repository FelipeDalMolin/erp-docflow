# Ambientes

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

O projeto começa pelo ambiente local e pelo ambiente CI.

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

Diretório local padrão:

```text
C:\Users\Felipe\projetos\erp-docflow
```

## 3. Ambiente CI

O ambiente `ci` será executado no GitHub Actions.

Uso:

- validar estrutura do repositório;
- validar documentação obrigatória;
- rodar lint;
- rodar testes;
- validar build;
- validar configuração de Docker Compose;
- futuramente validar migrações.

Na Phase 0, o CI deve começar simples.

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

## 4. Ambiente onprem-lab

O ambiente `onprem-lab` será um ambiente local dedicado ou servidor pequeno para simular operação real.

Uso:

- testar execução contínua;
- testar Docker Compose;
- testar banco;
- testar object storage;
- testar workers;
- testar backup;
- testar restore;
- validar comportamento fora da máquina de desenvolvimento.

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

## 5. Ambiente prod-onprem

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

Antes de existir produção, devem existir:

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

## 6. Estratégia cloud-like

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

## 7. Regras de configuração

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

## 8. Deploy

No início, o deploy será manual.

Fluxo futuro previsto:

```text
main estável
tag/release
deploy manual em onprem-lab
validação
deploy manual em prod-onprem
```

Automação de deploy só deve entrar depois que CI, branch protection e estratégia de backup estiverem maduros.

## 9. Backup e restore

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

## 10. Diretriz final

A ordem de maturidade dos ambientes será:

```text
local funcional
→ CI validando
→ onprem-lab reproduzível
→ prod-onprem controlado
→ híbrido/cloud opcional
```

O projeto não deve saltar diretamente para produção.