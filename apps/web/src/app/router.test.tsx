import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { routes } from "./router";

afterEach(cleanup);

function renderRoute(initialPath = "/") {
  const memoryRouter = createMemoryRouter(routes, {
    initialEntries: [initialPath],
  });

  render(<RouterProvider router={memoryRouter} />);
}

describe("application routes", () => {
  it("renders the R0 home and exposes only current navigation", () => {
    renderRoute();

    expect(screen.getByRole("heading", { level: 1, name: /fundação técnica/i })).toBeInTheDocument();
    const navigation = screen.getByRole("navigation", { name: /navegação principal/i });
    expect(navigation).toHaveTextContent("Início");
    expect(navigation).toHaveTextContent("Sistema");
    expect(navigation).not.toHaveTextContent("Inbox");
    expect(screen.getByRole("link", { name: "Início" })).toHaveAttribute("aria-current", "page");
  });

  it("navigates by keyboard to the system page", async () => {
    const user = userEvent.setup();
    renderRoute();

    await user.tab();
    await user.tab();
    await user.tab();
    expect(screen.getByRole("link", { name: "Sistema" })).toHaveFocus();
    await user.keyboard("{Enter}");

    expect(screen.getByRole("heading", { level: 1, name: /estado desta fundação/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sistema" })).toHaveAttribute("aria-current", "page");
  });

  it("shows a non-interactive roadmap on system", () => {
    renderRoute("/system");

    const heading = screen.getByRole("heading", { name: /roadmap informativo/i });
    const section = heading.closest("section");

    if (!section) {
      throw new Error("A seção de roadmap não foi encontrada.");
    }

    expect(within(section).getAllByText("Planejado")).toHaveLength(4);
    expect(within(section).queryByRole("link")).not.toBeInTheDocument();
    expect(within(section).queryByRole("button")).not.toBeInTheDocument();
  });

  it("exposes landmarks and a skip link to the main content", () => {
    renderRoute();

    expect(screen.getByRole("navigation", { name: /navegação principal/i })).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "conteudo-principal");
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /ir para o conteúdo/i })).toHaveAttribute(
      "href",
      "#conteudo-principal",
    );
  });

  it("renders not found for an unknown route", () => {
    renderRoute("/rota-inexistente");

    expect(screen.getByRole("heading", { level: 1, name: /caminho ainda não faz parte/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sistema" })).not.toHaveAttribute("aria-current");
    expect(screen.getByRole("link", { name: /voltar ao início/i })).toHaveAttribute("href", "/");
  });
});
