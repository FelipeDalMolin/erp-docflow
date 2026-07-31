import { Link } from "react-router-dom";

const principles = [
  {
    eyebrow: "01 · Origem",
    title: "Evidência preservada",
    description:
      "A direção do produto mantém fonte, versão e contexto antes de qualquer interpretação.",
  },
  {
    eyebrow: "02 · Decisão",
    title: "Revisão proporcional ao risco",
    description:
      "Automação futura sugere; regras validam; pessoas mantêm a autoridade sobre decisões sensíveis.",
  },
  {
    eyebrow: "03 · Operação",
    title: "On-prem first",
    description:
      "A fundação prioriza controle local sem abandonar contratos, containers e execução reproduzível.",
  },
];

export function HomePage() {
  return (
    <div className="page home-page">
      <section className="hero" aria-labelledby="home-title">
        <div className="hero-copy">
          <p className="eyebrow eyebrow-accent">R0 · Bootstrap técnico</p>
          <h1 id="home-title">Fundação técnica para decisões rastreáveis.</h1>
          <p className="hero-lead">
            O primeiro passo do ERP DocFlow estabelece uma interface clara e
            reproduzível para evoluir fontes heterogêneas em informação
            gerencial revisável — sem antecipar capacidades ainda planejadas.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" to="/system">
              Ver estado do sistema
              <span aria-hidden="true">→</span>
            </Link>
            <span className="scope-note">Sem dados reais · sem integrações remotas</span>
          </div>
        </div>

        <div className="hero-visual" aria-label="Fluxo conceitual planejado">
          <p className="visual-label">Direção do produto</p>
          <ol className="flow-list">
            <li>
              <span className="flow-index">01</span>
              <span><strong>Fontes</strong><small>documentais, estruturadas e manuais</small></span>
            </li>
            <li>
              <span className="flow-index">02</span>
              <span><strong>Evidências</strong><small>origem e contexto preservados</small></span>
            </li>
            <li>
              <span className="flow-index">03</span>
              <span><strong>Decisões</strong><small>validadas, revisáveis e auditáveis</small></span>
            </li>
          </ol>
          <p className="visual-disclaimer">Fluxo planejado; não implementado no R0.</p>
        </div>
      </section>

      <section className="release-strip" aria-labelledby="release-title">
        <div>
          <p className="eyebrow">Disponível nesta entrega</p>
          <h2 id="release-title">Um shell preparado para crescer por capacidades.</h2>
        </div>
        <div className="release-facts">
          <span><strong>02</strong> rotas principais</span>
          <span><strong>01</strong> linguagem visual</span>
          <span><strong>0</strong> capacidades simuladas</span>
        </div>
      </section>

      <section className="principles-section" aria-labelledby="principles-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Princípios de construção</p>
            <h2 id="principles-title">O futuro começa com limites explícitos.</h2>
          </div>
          <p>
            Estes princípios orientam a evolução do produto. Código, testes e
            contratos executáveis continuarão sendo a prova do que existe.
          </p>
        </div>

        <div className="principles-grid">
          {principles.map((principle) => (
            <article className="principle-card" key={principle.eyebrow}>
              <p className="card-index">{principle.eyebrow}</p>
              <h3>{principle.title}</h3>
              <p>{principle.description}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
