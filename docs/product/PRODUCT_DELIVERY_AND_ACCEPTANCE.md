# Entrega e aceite do produto

- **Classe:** baseline planejado de entrega e aceite de produto
- **Estado:** planejado, não implementado
- **Issue de origem:** #73
- **Atualizar quando:** destinatário, unidade de entrega, nível de maturidade ou resultado observável de aceite mudar

## 1. Finalidade

Este documento define **o que** deverá ser entregue e observado para que o `erp-docflow` deixe de ser apenas código executável no ambiente de desenvolvimento. Ele não cria deploy, imagens, Compose de piloto, secrets, backup ou autorização para produção.

O contrato técnico de `PeriodClose`, package, bundle, topologia, upgrade/rollback e observabilidade pertence a [Fechamento, pacote contábil e entrega do produto](../architecture/ACCOUNTING_CLOSE_AND_DELIVERY.md). Este documento é autoridade para destinatário, resultado de produto, níveis de maturidade e aceite observável; o documento de arquitetura é autoridade para objetos, invariantes e mecanismo técnico. ADRs aceitos prevalecem sobre ambos.

A direção on-prem vem do [ADR-0001](../adr/0001-on-prem-first-cloud-like.md), o uso inicial de Compose do [ADR-0008](../adr/0008-docker-compose-for-local-and-onprem-lab.md) e a exigência de recuperação do [ADR-0014](../adr/0014-backup-and-restore-required.md).

## 2. Duas entregas diferentes

| Unidade | Destinatário | Finalidade |
| --- | --- | --- |
| pacote de fechamento contábil/gerencial | contador ou responsável autorizado | transportar uma versão fechada, relatórios, evidências e protocolo |
| bundle de release do produto | administrador operacional | instalar, verificar, atualizar, recuperar e diagnosticar o software |

Gerar um PDF ou exportar uma planilha não constitui release instalável. Publicar containers também não constitui pacote de fechamento.

## 3. Pacote de fechamento

Conteúdo mínimo planejado:

- identificação da entidade, período e versão do fechamento;
- manifest de arquivos com hashes;
- livro e relatórios definidos para o piloto;
- previsto e realizado distinguidos;
- lista de pendências, ressalvas e exceções autorizadas;
- índice de ocorrências e evidências referenciadas;
- decisões e ajustes relevantes por referência, sem expor auditoria além da autorização;
- data, responsável e política de fechamento;
- protocolo de geração e, quando aplicável, entrega/retorno;
- formato e versão do schema de cada exportação estruturada.

O pacote deve ser determinístico para a mesma versão fechada. Regenerá-lo não cria novo fechamento; alterar conteúdo exige nova versão ou reabertura autorizada.

### Verificações do pacote

- hashes conferem;
- arquivos declarados existem e nenhum arquivo extra está oculto;
- totais correspondem ao snapshot;
- filtros, moeda, competência e regime de cada relatório estão identificados;
- referências chegam à origem conforme permissão;
- conteúdo sensível segue classificação e canal permitido;
- versão e protocolo são legíveis sem depender do nome da pasta.

## 4. Bundle de release do produto

Conteúdo mínimo planejado:

- manifest da release, versão e compatibilidade;
- imagens ou artefatos imutáveis, identificados por digest;
- orquestração específica do ambiente suportado;
- exemplo de configuração sem credenciais;
- migrations e verificação de compatibilidade;
- healthchecks e smoke test;
- runbook de instalação;
- runbook de atualização e rollback;
- runbook de backup e restore;
- diagnóstico e coleta segura de logs;
- release notes;
- inventário de componentes/SBOM quando o processo de build for materializado;
- dataset sintético ou anonimizado autorizado para o E2E Golden Month.

Secrets não entram em imagem, repositório, manifest, exemplo ou log. O mecanismo concreto depende da decisão de segurança ainda proposta no [ADR-0015](../adr/0015-auth-authorization-security-strategy.md).

## 5. Topologia mínima planejada

O bundle do piloto poderá materializar, conforme as capabilities já implementadas:

```text
web
  -> API
      -> banco relacional
      -> object storage
      -> worker/processamento assíncrono
      -> adapters internos habilitados pelo ambiente
```

PostgreSQL e storage S3-compatible permanecem direções arquiteturais condicionadas aos ADRs e gates correspondentes. Probe, OCR ou provider só entram no bundle quando o perfil que os utiliza estiver aprovado e implementado.

O Compose de desenvolvimento da Phase 1, limitado ao bootstrap de API e web, não é automaticamente o Compose do piloto. Bind mounts, hot reload e defaults locais não devem migrar silenciosamente para a unidade instalável.

## 6. Ambientes e níveis de evidência

| Ambiente | Finalidade | Dados permitidos | Declaração possível |
| --- | --- | --- | --- |
| desenvolvimento | implementação e testes rápidos | sintéticos | componente executa localmente |
| CI | validação reproduzível e isolada | fixtures sintéticas | build/testes passaram naquele commit |
| `onprem-lab` | instalação, integração, upgrade e recuperação | sintéticos ou anonimizados autorizados | release candidata é instalável e operável no laboratório |
| operação on-prem real | uso contínuo autorizado | reais classificados | produto atende gates operacionais e de segurança aprovados |

Os ambientes e limitações vigentes estão em [Ambientes](../operations/AMBIENTES.md). Aprovação em desenvolvimento ou CI não autoriza dados reais.

## 7. Gates de aceitação da release

### 7.1 Construção e proveniência

- commit e versão identificados;
- build reproduzível ou diferenças justificadas;
- dependências travadas conforme política;
- imagens referenciadas por digest;
- Structural CI e testes da aplicação aprovados;
- artefatos e checksums publicados pela pipeline autorizada.

### 7.2 Instalação limpa

- requisitos de CPU, memória, disco, portas e runtime documentados;
- configuração validada antes de iniciar;
- instalação em host limpo segue o runbook;
- serviços atingem health/readiness;
- smoke test confirma web, API e dependências implantadas;
- falha retorna diagnóstico acionável e seguro.

### 7.3 Persistência e recuperação

- volumes e ownership documentados;
- migration parte de estado conhecido;
- backup cobre banco, objetos e configuração necessária;
- restore é executado em ambiente isolado e verificado por dados e hashes;
- RPO/RTO do piloto são definidos na Issue operacional;
- perda parcial ou incompatibilidade bloqueia a inicialização com erro explícito e diagnóstico acionável; não produz inicialização enganosa.

### 7.4 Atualização e rollback

- matriz de compatibilidade identifica origem e destino suportados;
- preflight verifica espaço, backup e versão;
- migration e aplicação são coordenadas;
- rollback tem limite explícito quando migration não for reversível;
- atualização preserva dados, audit trail e objetos;
- release anterior permanece identificável e recuperável.

### 7.5 Segurança e privacidade

- autenticação e autorização aplicáveis ratificadas;
- secrets externos ao bundle e rotacionáveis;
- TLS e exposição de rede definidos;
- serviço roda com menor privilégio viável;
- logs não contêm documento integral, token ou dado sensível por padrão;
- retenção, temporários e descarte verificados;
- providers externos bloqueados por padrão até elegibilidade explícita.

### 7.6 Observabilidade e suporte

- versão e estado dos serviços consultáveis;
- logs estruturados com correlation ID;
- métricas mínimas de erro, latência, fila, armazenamento e processamento;
- alertas do piloto possuem responsável e ação;
- runbook cobre indisponibilidade, fila presa, falta de espaço e falha de dependência;
- coleta de diagnóstico preserva classificação de dados.

### 7.7 Aceite funcional

- E2E do [piloto Golden Month](PILOT_VERTICAL_SLICE.md) aprovado;
- totais de controle e reconciliação conferem;
- pacote de fechamento passa suas verificações;
- estados e acessibilidade mínima de [Jornadas e UX](USER_JOURNEYS_AND_UX.md) foram testados;
- indisponibilidade de capability opcional não bloqueia o caminho estruturado/manual;
- limitações conhecidas constam das release notes.

## 8. Critérios de passagem por maturidade

### Demonstração

- dados sintéticos;
- percurso principal executável;
- limitações visíveis;
- sem declaração de operação contínua.

### Piloto em laboratório

- bundle instalável;
- dataset anonimizado autorizado;
- E2E, upgrade e restore aprovados;
- monitoramento e runbooks mínimos;
- aceite humano registrado.

### Operação com dados reais

- gates de segurança e autorização ratificados;
- backup/restore recorrentes;
- retenção e acesso auditáveis;
- capacidade, suporte e recuperação aprovados;
- release e ambiente explicitamente autorizados.

Nenhuma maturidade é inferida pela existência de uma tag, imagem ou PR. A evidência precisa estar ligada à versão testada.

## 9. Responsabilidades planejadas

| Responsabilidade | Evidência esperada |
| --- | --- |
| engenharia | build, testes, migrations e limitações |
| operação | instalação, configuração, backup, restore e diagnóstico |
| produto | aceite do Golden Month e adequação das jornadas |
| segurança/privacidade | classificação, exposição, acesso, retenção e provider eligibility |
| responsável pelo fechamento | validação dos totais, pendências, pacote e protocolo |

Uma mesma pessoa pode exercer mais de uma responsabilidade no piloto, mas cada aceite precisa registrar qual responsabilidade foi exercida.

## 10. Fora de escopo

- executar deploy nesta documentação;
- escolher registry, plataforma de secrets ou ferramenta de observabilidade;
- declarar Kubernetes necessário;
- prometer alta disponibilidade ou disaster recovery de produção;
- definir SLA sem capacidade medida;
- autorizar provider externo;
- substituir runbooks especializados futuros;
- tratar Compose de desenvolvimento como release de produto.

## 11. Relações

- [North Star do produto](PRODUCT_NORTH_STAR.md)
- [Piloto vertical Golden Month](PILOT_VERTICAL_SLICE.md)
- [Jornadas e UX](USER_JOURNEYS_AND_UX.md)
- [Roadmap](../project/ROADMAP.md)
- [Arquitetura](../architecture/ARCHITECTURE.md)
- [ADR-0008 — Docker Compose para local e onprem-lab](../adr/0008-docker-compose-for-local-and-onprem-lab.md)
- [ADR-0014 — Backup e restore obrigatórios](../adr/0014-backup-and-restore-required.md)
