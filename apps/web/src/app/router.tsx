import { createBrowserRouter } from "react-router-dom";

import { HomePage } from "../features/home/HomePage";
import { NotFoundPage } from "../features/not-found/NotFoundPage";
import { SystemPage } from "../features/system/SystemPage";
import { AppShell } from "./shell/AppShell";

export const routes = [
  {
    path: "/",
    element: <AppShell />,
    children: [
      { path: "", element: <HomePage /> },
      { path: "system", element: <SystemPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
];

export const router = createBrowserRouter(routes);
