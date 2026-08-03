# ERP DocFlow experiment harness

Package isolado e offline para validar manifests, executar candidates explicitamente
registrados e produzir bundles de evidência verificáveis. A documentação canônica de uso e
limites está em `docs/architecture/EXPERIMENT_HARNESS.md`.

O único candidate desta slice é `integrity_probe/v1`. Ele recalcula hashes e tamanhos dos
bytes reais do dataset sintético; não extrai texto, não executa OCR e não é promovível.
