# Web

Interface mínima da Phase 1 do ERP DocFlow. Ela entrega o shell técnico R0,
responsivo e acessível, sem representar capacidades futuras como implementadas.

## Pré-requisitos

- Node.js 24.18.0;
- pnpm 11.13.1 via Corepack.

Na raiz do repositório:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @erp-docflow/web dev
```

A interface abre em `http://localhost:5173`. `VITE_API_BASE_URL` é uma
configuração pública opcional, com fallback para `http://localhost:8000`; esta
slice não executa chamadas remotas.

## Validar

```bash
pnpm --filter @erp-docflow/web lint
pnpm --filter @erp-docflow/web typecheck
pnpm --filter @erp-docflow/web test
pnpm --filter @erp-docflow/web build
```

Rotas implementadas:

- `/` — apresentação da fundação R0;
- `/system` — capacidades atuais e roadmap informativo;
- qualquer outra rota — página de não encontrado.
