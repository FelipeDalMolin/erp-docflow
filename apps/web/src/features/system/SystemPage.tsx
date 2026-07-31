const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const currentCapabilities = [
  {
    label: "Interface web",
    value: "Disponível nesta entrega",
    detail: "Shell React/Vite com navegação e estados básicos.",
    tone: "current",
  },
  {
    label: "Configuração pública",
    value: apiBaseUrl,
    detail: "Endereço configurado; nenhuma chamada é realizada nesta fase.",
    tone: "neutral",
  },
  {
    label: "Integração da API",
    value: "Não verificada pela interface",
    detail: "O contrato de health pertence à slice S1.02 do backend.",
    tone: "neutral",
  },
];

const roadmap = [
  { phase: "Phase 2", title: "Núcleo GED e intake", description: "Materialização, integridade e estado documental." },
  { phase: "Phase 3", title: "Processamento", description: "Perfis, evidências, providers e lineage." },
  { phase: "Phase 4", title: "Revisão e aceite", description: "Decisões humanas, correções e trilha auditável." },
  { phase: "R1", title: "Golden Month", description: "Piloto gerencial import-first sujeito a novo envelope." },
];

export function SystemPage() {
  return (
    <div className="page system-page">
      <header className="page-heading">
        <div>
          <p className="eyebrow eyebrow-accent">Sistema</p>
          <h1>Estado desta fundação</h1>
        </div>
        <p>
          Esta página descreve apenas a configuração visível do frontend R0.
          Ela não substitui healthchecks, observabilidade ou evidência de CI.
        </p>
      </header>

      <section className="capabilities-panel" aria-labelledby="current-title">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Agora</p>
            <h2 id="current-title">Capacidades técnicas atuais</h2>
          </div>
          <span className="status-key"><span className="signal-dot" aria-hidden="true" /> Implementado nesta UI</span>
        </div>

        <div className="capability-list">
          {currentCapabilities.map((capability) => (
            <article className="capability-row" key={capability.label}>
              <div>
                <p className="capability-label">{capability.label}</p>
                <strong className={capability.tone === "current" ? "value-current" : ""}>
                  {capability.value}
                </strong>
              </div>
              <p>{capability.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="roadmap-section" aria-labelledby="roadmap-title">
        <div className="section-heading roadmap-heading">
          <div>
            <p className="eyebrow">Depois</p>
            <h2 id="roadmap-title">Roadmap informativo</h2>
          </div>
          <p>
            Itens abaixo são direção planejada, não controles disponíveis,
            rotas do sistema ou compromissos desta entrega.
          </p>
        </div>

        <div className="roadmap-grid">
          {roadmap.map((item) => (
            <article className="roadmap-card" key={item.phase}>
              <span className="planned-badge">Planejado</span>
              <p>{item.phase}</p>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
