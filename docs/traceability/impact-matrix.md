# Impact Matrix

Guia de revisão de impacto. Não substitui ADRs.

| Tema de mudança | ADRs afetados | Docs afetados | Mapas/UMLs a atualizar | Novo ADR? |
| --- | --- | --- | --- | --- |
| estratégia on-prem/cloud-like | ADR-0001, 0014; 0016 (proposto) | arquitetura, ambientes, roadmap | decision/document/impact + deployment | sim, se mudar direção |
| iniciar código antes da Phase 0 | ADR-0002 | roadmap, modelo operacional, AGENTS | decision/impact | sim |
| Git/PR/revisão do projeto | ADR-0003, 0007, 0017, 0018 | estratégia Git, modelo operacional, fluxo Project | decision/document/impact + loop operacional | sim, se mudar regra |
| ambiente WSL/local | ADR-0004, 0008 | ambientes, WSL | document/impact + deployment | sim, se mudar ambiente oficial |
| Codex/configuração/continuidade | ADR-0005, 0017, 0018 | AGENTS, .codex, modelo operacional, fluxo Project, templates | decision/document/impact + loop operacional | sim, se mudar política, lifecycle, outcomes ou revisão humana |
| CI/branch protection | ADR-0003, 0007 | estratégia Git, ambientes, roadmap | decision/impact | sim, se mudar ordem/regra |
| Docker Compose/processos | ADR-0008, 0009 | arquitetura, ambientes, roadmap | module/impact + deployment | sim, se mudar direção |
| direção de produto/fato gerencial sustentado por evidência | ADR-0012, 0013; decisão complementar pendente | north star, piloto, arquitetura, domínio gerencial | document/module/entity/impact + contexto/atividade | sim antes de promover a contrato de implementação |
| piloto R1 Golden Month | ADR-0001, 0008, 0014; demais conforme capability | piloto vertical, UX, entrega, roadmap | document/module/entity/impact + contexto/deployment | ADR apenas quando introduzir decisão estrutural ainda não coberta |
| importação XLSX/CSV/OFX | ADR-0010, 0013; 0015 (proposto/gate) | structured import, domínio gerencial, lineage | module/entity/impact + atividade | sim se contrato, autorização ou persistência se tornarem estruturais |
| modular monolith/microservices | ADR-0009; 0016 (proposto) | arquitetura, provider strategy | decision/module/impact + componentes | sim |
| PostgreSQL/schema | ADR-0010, 0012, 0014 | data baseline, arquitetura, ambientes | entity/module/impact + domínio | sim antes de trocar banco |
| object storage/MinIO | ADR-0011, 0012, 0014 | data baseline, arquitetura, ambientes | entity/module/impact + deployment | sim antes de storage definitivo |
| DocumentEnvelope/versionamento | ADR-0012 | arquitetura, pipeline, data baseline, glossário | entity/module/impact + domínio/estado/sequência | sim se mudar núcleo |
| materialização vs efetivação | ADR-0012, 0013 | arquitetura, pipeline, glossário | entity/module/impact + atividade/sequências | sim se mudar responsabilidade |
| review/aceite/override | ADR-0013; 0015 (proposto/gate); 0016 (proposto) | pipeline, data baseline, roadmap | entity/module/impact + review sequence/estado | sim se mudar fluxo |
| provider/capability/router | ADR-0016 (proposto) | provider strategy, arquitetura, pipeline | adr/decision/document/module/entity/impact + componentes | aprovar/substituir ADR-0016 antes de implementar |
| Tika/probe/texto nativo | ADR-0016 (proposto) | pipeline, processing profile, provider strategy, data baseline | module/entity/impact + atividade/componentes/deployment | spike e benchmark antes de ratificar baseline; ADR se virar dependência estrutural |
| OpenCV/preprocessamento | ADR-0016 (proposto) | processing profile, pipeline, benchmark | module/entity/impact + policy/profile | decisão por perfil e benchmark; ADR se alterar infra ou boundary |
| PaddleOCR/Tesseract padrão | ADR-0016 (proposto) | provider strategy, benchmark futuro | impact + policy/profile | decisão baseada em benchmark; novo ADR se estrutural |
| regex/parsers/validators | ADR-0013; 0016 (proposto) | processing profile, structured import, pipeline | module/entity/impact | rule pack versionado; ADR apenas se mudar boundary/gate |
| Stirling/OCRmyPDF | ADR-0008, 0011; 0016 (proposto) | provider strategy, pipeline, deployment | module/impact + componentes | revisar ADR-0016; novo ADR se virar infra obrigatória |
| Google Document AI/OpenAI | ADR-0001; 0015 (proposto/gate); 0016 (proposto) | provider strategy, segurança futura, ambientes | decision/module/impact + contexto/deployment | sim se autorizar dados/providers externos |
| thresholds/confidence | ADR-0013; 0016 (proposto) | provider strategy, pipeline | entity/impact + estados | policy version; ADR se mudar gate estrutural |
| RAG/indexação | ADR-0012; 0015 (proposto/gate); 0016 (proposto) | arquitetura, pipeline, data baseline | module/entity/impact | ADR quando store/acesso virarem decisão |
| vínculo/efeito financeiro | ADR-0012, 0013; 0015 (proposto/gate) | pipeline, roadmap, data baseline | module/entity/route/impact + atividade | sim antes de fluxo sensível |
| obrigação/recebível/liquidação/conciliação/rateio | ADR-0013; 0015 (proposto/gate); decisão de domínio pendente | managerial domain, lineage, roadmap | document/module/entity/impact + atividade | sim antes de schema ou efeito sensível |
| relatório/saved view/drill-through | ADR-0012, 0013; 0015 (proposto/gate) | UX, lineage, domínio gerencial | module/entity/impact + contexto/atividade | ADR se mudar autoridade ou fonte canônica |
| fechamento/pacote contábil | ADR-0013, 0014; 0015 (proposto/gate) | close/delivery, UX, lineage, roadmap | module/entity/impact + atividade/deployment | sim antes de bloquear período ou enviar dados reais |
| UX mínima do produto | ADR-0013; 0015 (proposto/gate) | jornadas/UX, piloto, frontend architecture futura | document/module/impact + contexto | não para layout; sim se mudar autorização ou gate humano |
| ProductReleaseBundle/on-prem piloto | ADR-0001, 0008, 0014; 0015 (proposto/gate) | entrega/aceite, ambientes, arquitetura | module/impact + deployment | revisar ADR-0008; novo ADR se mudar direção de implantação |
| backup/restore | ADR-0010, 0011, 0014 | ambientes, arquitetura, roadmap | impact/decision + deployment | sim antes de operação real |
| auth/security/LGPD | ADR-0015 (proposto/gate) | AGENTS, arquitetura, pipeline, provider strategy | module/entity/route/impact + contexto | sim; ADR-0015 é gate |

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
