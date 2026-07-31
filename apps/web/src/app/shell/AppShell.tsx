import { NavLink, Outlet } from "react-router-dom";

const navigation = [
  { to: "/", label: "Início", end: true, icon: <HomeIcon /> },
  { to: "/system", label: "Sistema", end: true, icon: <SystemIcon /> },
];

function HomeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m3 10.6 9-7.1 9 7.1v9.1a.8.8 0 0 1-.8.8H15v-6H9v6H3.8a.8.8 0 0 1-.8-.8Z" />
    </svg>
  );
}

function SystemIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3.5a2 2 0 0 1 1.9 1.4l.3.8 1 .4.8-.4a2 2 0 0 1 2.4.4l.5.5a2 2 0 0 1 .4 2.4l-.4.8.4 1 .8.3a2 2 0 0 1 1.3 1.9v.7a2 2 0 0 1-1.3 1.9l-.8.3-.4 1 .4.8a2 2 0 0 1-.4 2.4l-.5.5a2 2 0 0 1-2.4.4l-.8-.4-1 .4-.3.8a2 2 0 0 1-1.9 1.3h-.7a2 2 0 0 1-1.9-1.3l-.3-.8-1-.4-.8.4a2 2 0 0 1-2.4-.4l-.5-.5a2 2 0 0 1-.4-2.4l.4-.8-.4-1-.8-.3A2 2 0 0 1 2.5 13v-.7a2 2 0 0 1 1.3-1.9l.8-.3.4-1-.4-.8A2 2 0 0 1 5 5.9l.5-.5A2 2 0 0 1 8 5l.8.4 1-.4.3-.8A2 2 0 0 1 12 3.5Zm0 6a3.2 3.2 0 1 0 0 6.4 3.2 3.2 0 0 0 0-6.4Z" />
    </svg>
  );
}

function MarkIcon() {
  return (
    <svg viewBox="0 0 40 40" aria-hidden="true">
      <path d="M8 6h18l6 6v22H8z" className="mark-page" />
      <path d="M26 6v7h6M13 18h14M13 23h14M13 28h9" className="mark-lines" />
    </svg>
  );
}

export function AppShell() {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#conteudo-principal">
        Ir para o conteúdo
      </a>

      <aside className="sidebar">
        <div className="brand-lockup">
          <span className="brand-mark">
            <MarkIcon />
          </span>
          <span>
            <strong>ERP DocFlow</strong>
            <small>Fundação R0</small>
          </span>
        </div>

        <nav className="primary-nav" aria-label="Navegação principal">
          <p className="nav-label">Workspace</p>
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-note" aria-label="Estado da entrega">
          <span className="signal-dot" aria-hidden="true" />
          <span>
            <strong>Bootstrap técnico</strong>
            <small>Capacidades de produto ainda planejadas</small>
          </span>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div className="mobile-brand">
            <span className="brand-mark"><MarkIcon /></span>
            <strong>ERP DocFlow</strong>
          </div>
          <p className="environment-label">
            <span>Ambiente local</span>
            <span className="divider" aria-hidden="true" />
            <strong>R0</strong>
          </p>
        </header>

        <main id="conteudo-principal" tabIndex={-1}>
          <Outlet />
        </main>

        <footer className="app-footer">
          <span>ERP DocFlow · on-prem first</span>
          <span>Fundação técnica — não representa produto final</span>
        </footer>
      </div>
    </div>
  );
}
