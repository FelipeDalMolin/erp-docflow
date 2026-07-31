import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="page not-found-page">
      <div className="not-found-code" aria-hidden="true">404</div>
      <div>
        <p className="eyebrow eyebrow-accent">Rota não encontrada</p>
        <h1>Este caminho ainda não faz parte do workspace.</h1>
        <p>
          A fundação R0 expõe somente as áreas Início e Sistema. Capacidades
          futuras serão adicionadas quando seus contratos e gates existirem.
        </p>
        <Link className="button button-primary" to="/">
          Voltar ao início
          <span aria-hidden="true">→</span>
        </Link>
      </div>
    </div>
  );
}
