# Impact Matrix

Guia de revisão de impacto. Não substitui ADRs.

| Tema de mudança | ADRs afetados | Docs afetados | Mapas/UMLs a atualizar | Novo ADR? |
| --- | --- | --- | --- | --- |
| estratégia on-prem/cloud-like | ADR-0001, 0014, 0016 | arquitetura, ambientes, roadmap | decision/document/impact + deployment | sim, se mudar direção |
| iniciar código antes da Phase 0 | ADR-0002 | roadmap, modelo operacional, AGENTS | decision/impact | sim |
| Git/PR/revisão do projeto | ADR-0003, 0007, 0017 | estratégia Git, modelo operacional, fluxo Project | decision/document/impact + loop operacional | sim, se mudar regra |
| ambiente WSL/local | ADR-0004, 0008 | ambientes, WSL | document/impact + deployment | sim, se mudar ambiente oficial |
| Codex/configuração/continuidade | ADR-0005, 0017 | AGENTS, .codex, modelo operacional, fluxo Project, templates | decision/document/impact + loop operacional | sim, se mudar política ou revisão humana |
| CI/branch protection | ADR-0003, 0007 | estratégia Git, ambientes, roadmap | decision/impact | sim, se mudar ordem/regra |
| Docker Compose/processos | ADR-0008, 0009 | arquitetura, ambientes, roadmap | module/impact + deployment | sim, se mudar direção |
| modular monolith/microservices | ADR-0009, 0016 | arquitetura, provider strategy | decision/module/impact + componentes | sim |
| PostgreSQL/schema | ADR-0010, 0012, 0014 | data baseline, arquitetura, ambientes | entity/module/impact + domínio | sim antes de trocar banco |
| object storage/MinIO | ADR-0011, 0012, 0014 | data baseline, arquitetura, ambientes | entity/module/impact + deployment | sim antes de storage definitivo |
| DocumentEnvelope/versionamento | ADR-0012 | arquitetura, pipeline, data baseline, glossário | entity/module/impact + domínio/estado/sequência | sim se mudar núcleo |
| materialização vs efetivação | ADR-0012, 0013 | arquitetura, pipeline, glossário | entity/module/impact + atividade/sequências | sim se mudar responsabilidade |
| review/aceite/override | ADR-0013, 0015, 0016 | pipeline, data baseline, roadmap | entity/module/impact + review sequence/estado | sim se mudar fluxo |
| provider/capability/router | ADR-0016 (proposto) | provider strategy, arquitetura, pipeline | adr/decision/document/module/entity/impact + componentes | aprovar/substituir ADR-0016 antes de implementar |
| PaddleOCR/Tesseract padrão | ADR-0016 (proposto) | provider strategy, benchmark futuro | impact + policy/profile | decisão baseada em benchmark; novo ADR se estrutural |
| Stirling/OCRmyPDF | ADR-0008, 0011, 0016 | provider strategy, pipeline, deployment | module/impact + componentes | revisar ADR-0016; novo ADR se virar infra obrigatória |
| Google Document AI/OpenAI | ADR-0001, 0015, 0016 | provider strategy, segurança futura, ambientes | decision/module/impact + contexto/deployment | sim se autorizar dados/providers externos |
| thresholds/confidence | ADR-0013, 0016 | provider strategy, pipeline | entity/impact + estados | policy version; ADR se mudar gate estrutural |
| RAG/indexação | ADR-0012, 0015, 0016 | arquitetura, pipeline, data baseline | module/entity/impact | ADR quando store/acesso virarem decisão |
| vínculo/efeito financeiro | ADR-0012, 0013, 0015 | pipeline, roadmap, data baseline | module/entity/route/impact + atividade | sim antes de fluxo sensível |
| backup/restore | ADR-0010, 0011, 0014 | ambientes, arquitetura, roadmap | impact/decision + deployment | sim antes de operação real |
| auth/security/LGPD | ADR-0015 | AGENTS, arquitetura, pipeline, provider strategy | module/entity/route/impact + contexto | sim; ADR-0015 é gate |

## Checklist de análise

Para qualquer linha afetada:

1. consultar status do ADR;
2. identificar se a mudança complementa ou altera decisão;
3. revisar documentos canônicos, não apenas o diagrama;
4. atualizar mapas e UMLs correspondentes;
5. verificar segurança, dados reais, retenção e operação;
6. especificar testes/benchmark;
7. registrar Issue e PR.

Uma mudança de modelo/processor pode ser apenas nova versão de policy quando mantém a decisão arquitetural. Se alterar residência, responsabilidade, gate humano, storage, domínio ou implantação, exige análise de ADR.

