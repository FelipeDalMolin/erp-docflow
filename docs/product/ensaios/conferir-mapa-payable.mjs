// Ensaio de documentação. Compara o mapa com resultados ESPERADOS já versionados.
// Uso: node docs/product/ensaios/conferir-mapa-payable.mjs [raiz-do-checkout]
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function conferirContrato(mapa, schema, regras, manifesto, carregarEsperado) {
  const exigir = (ok, msg) => { if (!ok) throw new Error(msg); };
  const chavesIguais = (a, b) =>
    a.length === b.length && new Set(a).size === a.length && a.every(k => b.includes(k));
  exigir(mapa.automatic_erp_writes === false, "O mapa de revisão permite escrita automática.");
  exigir(mapa.payload_schema_id === schema.properties.schema_id.const &&
    mapa.payload_schema_version === schema.properties.schema_version.const, "Versão de schema divergente.");
  const fontes = mapa.field_mapping.map(f => f.source_path);
  const campos = schema.properties.fields.required;
  exigir(chavesIguais(fontes, ["document_type", ...campos.map(k => "fields." + k)]), "Cobertura de campos divergente.");
  exigir(chavesIguais(Object.keys(mapa.route_by_document_type), Object.keys(regras.document_types)), "Rotas por tipo divergentes.");
  exigir(chavesIguais(Object.keys(mapa.applicability), schema.$defs.applicability.enum), "Estados de aplicabilidade divergentes.");
  const resumo = {casos: 0, com_saida_esperada: 0, sem_saida_esperada: 0, observacoes: 0,
    por_estado: {}, por_rota_esperada: {}, casos_com_validacao_negativa_esperada: 0, por_disposicao: {}};
  for (const f of mapa.field_mapping) {
    exigir(f.semantic_key && f.review_rule && f.do_not_assign.length > 0, "Regra incompleta: " + f.source_path);
    exigir(f.disposition === "new_attribute" ? f.v43_reference === null : typeof f.v43_reference === "string",
      "Correspondência ERP incoerente: " + f.source_path);
  }
  for (const fixture of manifesto.fixtures) {
    const gt = carregarEsperado(fixture);
    exigir(gt.fixture_id === fixture.id, "Identidade da fixture divergente.");
    resumo.casos++;
    const rota = fixture.expected.routing;
    resumo.por_rota_esperada[rota] = (resumo.por_rota_esperada[rota] || 0) + 1;
    const saida = gt.expected_output;
    if (saida === null) {
      exigir(rota === "QUARANTINE_INPUT", fixture.id + ": saída ausente fora da quarentena esperada.");
      resumo.sem_saida_esperada++;
      continue;
    }
    resumo.com_saida_esperada++;
    exigir(saida.schema_id === mapa.payload_schema_id && saida.schema_version === mapa.payload_schema_version, fixture.id + ": saída de outro perfil.");
    exigir(chavesIguais(Object.keys(saida.fields), campos), fixture.id + ": conjunto de campos inesperado.");
    const tipo = saida.document_type.normalized_value;
    const regra = regras.document_types[tipo];
    exigir(regra && saida.document_type.applicability === "PRESENT", fixture.id + ": tipo inválido.");
    const falhas = gt.expected_validations.filter(v => v.status === "FAIL").map(v => v.code);
    if (falhas.length) resumo.casos_com_validacao_negativa_esperada++;
    for (const spec of mapa.field_mapping) {
      const nome = spec.source_path.split(".").pop();
      const obs = spec.source_path === "document_type" ? saida.document_type : saida.fields[nome];
      const estado = obs.applicability;
      exigir(chavesIguais(Object.keys(obs), schema.$defs.baseField.required), fixture.id + ": envelope de campo divergente.");
      exigir(Object.hasOwn(mapa.applicability, estado) && Array.isArray(obs.evidence_refs), fixture.id + ": observação inválida.");
      if (estado === "PRESENT") {
        exigir(typeof obs.normalized_value === "string" && obs.normalized_value.length > 0 &&
          typeof obs.raw_value === "string" && obs.raw_value.length > 0 && obs.evidence_refs.length > 0, fixture.id + ": PRESENT sem fonte/valor.");
      } else if (estado === "AMBIGUOUS") {
        exigir(obs.normalized_value === null && obs.evidence_refs.length > 0, fixture.id + ": ambiguidade perdeu evidência.");
      } else {
        exigir(obs.raw_value === null && obs.normalized_value === null && obs.evidence_refs.length === 0, fixture.id + ": ausência com valor.");
      }
      for (const ref of obs.evidence_refs) {
        exigir(ref.artifact_ref && ref.excerpt && Number.isInteger(ref.page) && ref.page >= 1 && ref.page <= gt.page_count,
          fixture.id + ": localização de evidência inconsistente.");
        exigir(ref.bbox === null ? ref.coordinate_space === null :
          Array.isArray(ref.bbox) && ref.bbox.length === 4 && ref.bbox.every(n => Number.isFinite(n) && n >= 0) &&
          ref.coordinate_space === "PIXEL", fixture.id + ": coordenadas inconsistentes.");
      }
      if (nome !== "document_type" && estado !== "PRESENT" && regra.required_present.includes(nome)) {
        exigir(falhas.includes("REQUIRED_FIELD_MISSING"), fixture.id + ": obrigatório ausente sem falha esperada.");
      }
      if (nome === "due_on" && estado === "PRESENT" && saida.fields.issued_on.applicability === "PRESENT" &&
        saida.fields.issued_on.normalized_value > obs.normalized_value) {
        exigir(falhas.includes("VALIDATION_CONFLICT"), fixture.id + ": datas conflitantes sem falha esperada.");
      }
      if (nome === "total_amount" && estado === "PRESENT" && saida.fields.currency.normalized_value === "BRL") {
        const v = obs.normalized_value;
        exigir(/^[0-9]+\.[0-9]{2}$/.test(v), fixture.id + ": decimal inválido.");
        const cents = BigInt(v.replace(".", ""));
        exigir(cents > 0n && cents <= BigInt(Number.MAX_SAFE_INTEGER), fixture.id + ": fora da faixa do site.");
      }
      resumo.observacoes++;
      resumo.por_estado[estado] = (resumo.por_estado[estado] || 0) + 1;
      resumo.por_disposicao[spec.disposition] = (resumo.por_disposicao[spec.disposition] || 0) + 1;
    }
  }
  return resumo;
}

const raiz = resolve(process.argv[2] || ".");
const ler = caminho => JSON.parse(readFileSync(caminho, "utf8"));
const pastaPerfil = resolve(raiz, "profiles/payable_document_pt_br/v1alpha");
const pastaDados = resolve(raiz, "datasets/payable_document_pt_br/v1alpha");
const resumo = conferirContrato(
  ler(new URL("./mapa-payable-erp-v43.json", import.meta.url)),
  ler(resolve(pastaPerfil, "extraction.schema.json")),
  ler(resolve(pastaPerfil, "validation-rules.json")),
  ler(resolve(pastaDados, "manifest.json")),
  fixture => ler(resolve(pastaDados, fixture.ground_truth))
);
console.log(JSON.stringify(resumo, null, 2));
