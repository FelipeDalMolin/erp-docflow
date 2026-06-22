# WSL Multi-Projetos

Este documento define como o projeto `erp-docflow` deve usar WSL quando a mesma máquina também hospedar outros projetos de desenvolvimento.

A decisão operacional inicial é: **usar uma única distribuição WSL principal para desenvolvimento**, mantendo isolamento por projeto dentro da própria distribuição.

## 1. Decisão inicial

Para a máquina atual, com recursos limitados, o padrão será:

```text
Windows = host operacional
WSL Ubuntu = ambiente técnico principal compartilhado
Docker Desktop = backend WSL2 e containers Linux
GitHub = fonte da verdade
Projetos = isolados por pasta, virtualenv, Node version, Docker Compose e variáveis de ambiente
```

Não criaremos uma distribuição WSL separada para cada projeto no início.

## 2. Por que não criar uma WSL por projeto agora

O WSL permite múltiplas distribuições lado a lado, mas isso não significa que devamos criar uma distribuição para cada projeto.

Para o estado atual da máquina e do projeto, múltiplas distribuições aumentariam:

- manutenção;
- duplicação de pacotes;
- consumo de disco;
- risco de diferença entre ambientes;
- trabalho de backup;
- confusão entre shells, paths e integrações Docker.

A separação correta, neste momento, deve ocorrer por:

```text
~/projetos/<nome-do-projeto>
~/codex-runs/<nome-do-projeto>
/mnt/e/<nome-do-projeto>-data
ambiente Python por projeto
versão Node controlada por projeto
Docker Compose por projeto
.env por projeto, fora do Git
```

## 3. Quando criar uma WSL dedicada

Criar uma distribuição WSL dedicada apenas quando houver motivo real de isolamento.

Exemplos:

- projeto com dependências incompatíveis;
- stack muito diferente;
- necessidade de simular servidor dedicado;
- uso de serviços pesados e persistentes;
- requisitos fortes de segurança ou separação de dados;
- experimento que pode quebrar o ambiente comum;
- necessidade de snapshot/export independente;
- projeto que deve virar um ambiente on-prem-lab próprio.

Para o `erp-docflow`, a WSL dedicada pode ser considerada futuramente quando o projeto sair de desenvolvimento local e virar laboratório operacional contínuo.

## 4. Nomes recomendados

Distribuição WSL principal atual:

```text
Ubuntu-20.04
```

Distribuição futura recomendada para migração controlada, não obrigatória neste momento:

```text
Ubuntu-24.04
```

Diretórios:

```text
~/projetos/erp-docflow
~/codex-runs/erp-docflow
/mnt/e/erp-docflow-data
```

No Windows, a pasta de dados correspondente será:

```text
E:\erp-docflow-data
```

## 5. Regra de ouro para arquivos

Código deve ficar no filesystem Linux do WSL:

```text
~/projetos/erp-docflow
```

Evitar código em:

```text
/mnt/c/Users/Felipe/projetos/erp-docflow
/mnt/e/erp-docflow
```

Documentos operacionais, arquivos enviados, exports e backups podem ficar em disco Windows montado no WSL:

```text
/mnt/e/erp-docflow-data
```

Motivo: o código executado por Linux, Git, Python, Node, testes e Codex tende a funcionar melhor e com mais previsibilidade dentro do filesystem Linux. Já documentos e backups precisam ser facilmente visíveis e copiáveis pelo Windows.

## 6. Layout recomendado

```text
Windows
├── VS Code
├── navegador
├── Docker Desktop
├── E:\erp-docflow-data
│   ├── incoming
│   ├── storage
│   ├── backups
│   ├── exports
│   └── logs
└── C:\Users\Felipe\.wslconfig

WSL Ubuntu
├── ~/projetos
│   ├── erp-docflow
│   ├── projeto-jubileu
│   └── outros-projetos
├── ~/codex-runs
│   ├── erp-docflow
│   └── outros-projetos
└── ferramentas compartilhadas
    ├── git
    ├── gh
    ├── codex opcional
    ├── python
    ├── node/nvm
    └── docker cli
```

## 7. Isolamento por projeto dentro da mesma WSL

Mesmo usando uma única WSL, cada projeto deve ter isolamento próprio.

### Python

Cada projeto deve usar seu próprio ambiente virtual:

```bash
cd ~/projetos/erp-docflow
python3 -m venv .venv
source .venv/bin/activate
python --version
```

### Node

Cada projeto deve declarar sua versão esperada de Node:

```text
.nvmrc
```

Exemplo:

```text
22
```

Uso:

```bash
cd ~/projetos/erp-docflow
nvm install
nvm use
node -v
```

### Variáveis de ambiente

Cada projeto deve ter:

```text
.env.example
```

O arquivo real não deve ir para o Git:

```text
.env
```

### Docker Compose

Cada projeto deve ter seu próprio Compose e seu próprio nome de projeto:

```bash
docker compose -p erp-docflow up -d
```

Isso evita conflito de nomes entre containers, redes e volumes.

## 8. Passo a passo correto

### 8.1 Verificar WSL no PowerShell

```powershell
wsl --version
wsl --status
wsl -l -v
```

### 8.2 Definir WSL2 como padrão para novas instalações

```powershell
wsl --set-default-version 2
```

### 8.3 Definir a distribuição principal atual

Para o setup atual do projeto, usar `Ubuntu-20.04` como distribuição principal:

```powershell
wsl --set-version Ubuntu-20.04 2
wsl --set-default Ubuntu-20.04
```

Uma migração futura para `Ubuntu-24.04` pode ser considerada depois, em tarefa própria e com validação controlada:

```powershell
wsl --install -d Ubuntu-24.04
wsl --set-default Ubuntu-24.04
```

### 8.4 Não usar `docker-desktop` como ambiente de trabalho

A distribuição `docker-desktop` pertence ao Docker Desktop. Ela não deve ser usada como shell principal de desenvolvimento.

Ambiente de trabalho atual:

```text
Ubuntu-20.04
```

Ambiente futuro possível, mediante migração controlada:

```text
Ubuntu-24.04
```

### 8.5 Criar diretórios de trabalho no WSL

```bash
mkdir -p ~/projetos
mkdir -p ~/codex-runs/erp-docflow
cd ~/projetos
```

### 8.6 Clonar o projeto dentro do filesystem Linux

```bash
cd ~/projetos
git clone https://github.com/FelipeDalMolin/erp-docflow.git
cd erp-docflow
```

### 8.7 Criar diretórios de dados no Windows

No PowerShell:

```powershell
New-Item -ItemType Directory -Force E:\erp-docflow-data\incoming
New-Item -ItemType Directory -Force E:\erp-docflow-data\storage
New-Item -ItemType Directory -Force E:\erp-docflow-data\backups
New-Item -ItemType Directory -Force E:\erp-docflow-data\exports
New-Item -ItemType Directory -Force E:\erp-docflow-data\logs
```

No WSL, validar:

```bash
ls -la /mnt/e/erp-docflow-data
```

### 8.8 Configurar limite global do WSL

Criar ou editar no Windows:

```text
C:\Users\Felipe\.wslconfig
```

Conteúdo recomendado para máquina com 8 GB RAM:

```ini
[wsl2]
memory=4GB
processors=3
swap=4GB
localhostForwarding=true

[experimental]
autoMemoryReclaim=gradual
```

Depois aplicar:

```powershell
wsl --shutdown
```

Atenção: `.wslconfig` é configuração global do WSL2 no usuário Windows. Ela afeta o conjunto das distribuições WSL2, não apenas um projeto.

### 8.9 Preparar pacotes base na Ubuntu

```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
  git \
  curl \
  build-essential \
  ca-certificates \
  python3 \
  python3-venv \
  python3-pip \
  tesseract-ocr \
  tesseract-ocr-por \
  poppler-utils
```

Esses pacotes preparam o ambiente técnico, mas não autorizam início de código de produto fora dos gates da Phase 0.

### 8.10 Instalar Node via nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
corepack enable
```

### 8.11 Validar ferramentas

```bash
git --version
python3 --version
node -v
npm -v
tesseract --version
pdftotext -v
```

### 8.12 Docker Desktop e WSL

No Docker Desktop:

```text
Settings → General → Use WSL 2 based engine
Settings → Resources → WSL Integration → habilitar Ubuntu usada no projeto
```

Na Ubuntu:

```bash
docker version
docker compose version
```

## 9. Como abrir no VS Code

A partir do WSL:

```bash
cd ~/projetos/erp-docflow
code .
```

O VS Code deve abrir em modo remoto WSL.

Se abrir no Windows puro, conferir o canto inferior esquerdo do VS Code. O esperado no setup atual é:

```text
WSL: Ubuntu-20.04
```

Futuramente, após migração controlada, pode ser:

```text
WSL: Ubuntu-24.04
```

## 10. Como o Codex deve ser usado nesse modelo

Uso principal no setup atual:

```text
VS Code conectado ao WSL + Codex extension no workspace /home/felipe/projetos/erp-docflow
```

O Codex deve operar no projeto aberto em modo remoto WSL. O objetivo é que leitura de arquivos, comandos, Git, testes e edições ocorram no ambiente Linux do projeto, não em um workspace Windows.

Uso secundário/opcional, quando necessário:

```bash
cd ~/projetos/erp-docflow
codex
```

ou, em modo não interativo:

```bash
cd ~/projetos/erp-docflow
codex exec "Leia AGENTS.md e proponha um plano. Não implemente."
```

Logs brutos devem ficar fora do Git:

```text
~/codex-runs/erp-docflow
```

O repositório deve manter apenas resumos limpos, decisões, ADRs, rastreabilidade e documentação operacional.

## 11. Regra para outros projetos

Novos projetos devem seguir o mesmo padrão:

```text
~/projetos/<nome-do-projeto>
~/codex-runs/<nome-do-projeto>
/mnt/e/<nome-do-projeto>-data
```

Só criar uma nova distribuição WSL quando houver necessidade real de isolamento.

## 12. Diretriz final

Para esta máquina e este estágio do `erp-docflow`:

```text
Uma WSL principal compartilhada.
Ubuntu-20.04 como distro atual.
Ubuntu-24.04 como migração futura possível.
Isolamento por projeto.
Código no filesystem Linux.
Dados operacionais em disco Windows dedicado.
Docker integrado apenas à distribuição de trabalho.
Codex principalmente via VS Code em WSL.
Codex CLI apenas como opção complementar.
Docs e ADRs como fonte de decisão.
```
