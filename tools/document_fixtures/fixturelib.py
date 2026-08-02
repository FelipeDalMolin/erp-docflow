from __future__ import annotations

import hashlib
import json
import math
import random
import re
import struct
import zlib
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable


DATASET_ID = "payable_document_pt_br"
DATASET_VERSION = "v1alpha"
SEED = 20260731
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_PAGES = 20
PDF_PASSWORD_PADDING = bytes.fromhex(
    "28BF4E5E4E758A4164004E56FFFA0108"
    "2E2E00B6D0683E802F0CA9FE6453697A"
)
DATASET_GIT_ATTRIBUTES = (
    b"files/*.pdf binary\n"
    b"files/*.png binary\n"
    b"files/*.jpg binary\n"
    b"files/*.tiff binary\n"
)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _rc4(key: bytes, payload: bytes) -> bytes:
    state = list(range(256))
    cursor = 0
    for index in range(256):
        cursor = (cursor + state[index] + key[index % len(key)]) % 256
        state[index], state[cursor] = state[cursor], state[index]
    output = bytearray()
    left = right = 0
    for byte in payload:
        left = (left + 1) % 256
        right = (right + state[left]) % 256
        state[left], state[right] = state[right], state[left]
        output.append(byte ^ state[(state[left] + state[right]) % 256])
    return bytes(output)


def _pad_pdf_password(password: str) -> bytes:
    encoded = password.encode("latin-1")[:32]
    return (encoded + PDF_PASSWORD_PADDING)[:32]


def _pdf_revision_2_security(
    user_password: str,
    owner_password: str,
    permissions: int,
    file_id: bytes,
) -> tuple[bytes, bytes, bytes]:
    owner_key = hashlib.md5(_pad_pdf_password(owner_password)).digest()[:5]
    owner_entry = _rc4(owner_key, _pad_pdf_password(user_password))
    encryption_key = hashlib.md5(
        _pad_pdf_password(user_password)
        + owner_entry
        + struct.pack("<i", permissions)
        + file_id
    ).digest()[:5]
    user_entry = _rc4(encryption_key, PDF_PASSWORD_PADDING)
    return owner_entry, user_entry, encryption_key


def _pdf_object_key(encryption_key: bytes, object_id: int) -> bytes:
    material = (
        encryption_key
        + object_id.to_bytes(3, "little")
        + (0).to_bytes(2, "little")
    )
    return hashlib.md5(material).digest()[: min(len(encryption_key) + 5, 16)]


def _cnpj_digit(base: str, weights: list[int]) -> str:
    total = sum((ord(char) - 48) * weight for char, weight in zip(base, weights))
    remainder = total % 11
    return str(0 if remainder < 2 else 11 - remainder)


def make_cnpj(base: str) -> str:
    normalized = base.upper()
    if re.fullmatch(r"[A-Z0-9]{12}", normalized) is None:
        raise ValueError("CNPJ base must contain exactly 12 ASCII letters/digits")
    first = _cnpj_digit(normalized, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = _cnpj_digit(
        normalized + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    )
    return normalized + first + second


def normalize_cnpj(raw: str) -> str:
    return "".join(
        char
        for char in raw.upper()
        if "0" <= char <= "9" or "A" <= char <= "Z"
    )


def valid_cnpj(raw: str) -> bool:
    normalized = normalize_cnpj(raw)
    if re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", normalized) is None:
        return False
    if normalized.isdigit() and len(set(normalized)) == 1:
        return False
    return make_cnpj(normalized[:12]) == normalized


def format_numeric_cnpj(value: str) -> str:
    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"


NUMERIC_CNPJS = [
    make_cnpj("123456780001"),
    make_cnpj("234567890001"),
    make_cnpj("345678900001"),
    make_cnpj("456789010001"),
    make_cnpj("567890120001"),
    make_cnpj("678901230001"),
]
ALPHANUMERIC_CNPJS = [
    make_cnpj("12ABC34501DE"),
    make_cnpj("23BCD45602EF"),
    make_cnpj("34CDE56703FG"),
    make_cnpj("45DEF67804GH"),
    make_cnpj("56EFG78905HJ"),
    make_cnpj("67FGH89006JK"),
    make_cnpj("78GHJ90107KL"),
    make_cnpj("89HJK01208LM"),
]


def field(raw: str | None, normalized: str | None, applicability: str = "PRESENT") -> dict[str, Any]:
    return {
        "raw_value": raw,
        "normalized_value": normalized,
        "applicability": applicability,
    }


def document_fields(
    document_type: str,
    number: str | None,
    issuer: str,
    tax_id: str | None,
    issued_on: tuple[str, str] | None,
    due_on: tuple[str, str] | None,
    amount: tuple[str, str] | None,
) -> dict[str, dict[str, Any]]:
    tax_raw = None
    tax_normalized = None
    if tax_id:
        tax_normalized = normalize_cnpj(tax_id)
        tax_raw = (
            format_numeric_cnpj(tax_normalized)
            if tax_normalized.isdigit()
            else tax_normalized
        )
    return {
        "document_type": field(document_type, document_type),
        "document_number": field(
            number,
            number,
            "PRESENT" if number is not None else "NOT_APPLICABLE",
        ),
        "issuer_name": field(issuer, issuer),
        "issuer_tax_id": field(
            tax_raw,
            tax_normalized,
            "PRESENT" if tax_id is not None else "NOT_APPLICABLE",
        ),
        "issued_on": field(
            issued_on[0] if issued_on else None,
            issued_on[1] if issued_on else None,
            "PRESENT" if issued_on else "NOT_APPLICABLE",
        ),
        "due_on": field(
            due_on[0] if due_on else None,
            due_on[1] if due_on else None,
            "PRESENT" if due_on else "NOT_APPLICABLE",
        ),
        "total_amount": field(
            amount[0] if amount else None,
            amount[1] if amount else None,
            "PRESENT" if amount else "AMBIGUOUS",
        ),
        "currency": field("BRL", "BRL"),
    }


BASE_DOCUMENTS: dict[str, dict[str, Any]] = {
    "inv001": {
        "type": "INVOICE",
        "fields": document_fields(
            "INVOICE",
            "INV-2026-001",
            "AURORA SUPRIMENTOS TESTE",
            NUMERIC_CNPJS[0],
            ("15/07/2026", "2026-07-15"),
            ("30/07/2026", "2026-07-30"),
            ("R$ 1.234,56", "1234.56"),
        ),
    },
    "slip001": {
        "type": "PAYMENT_SLIP",
        "fields": document_fields(
            "PAYMENT_SLIP",
            "BOL-2026-101",
            "BETA SERVICOS SINTETICOS",
            ALPHANUMERIC_CNPJS[0],
            None,
            ("05/08/2026", "2026-08-05"),
            ("R$ 987,65", "987.65"),
        ),
    },
    "rec001": {
        "type": "RECEIPT",
        "fields": document_fields(
            "RECEIPT",
            None,
            "CASA LUMEN TESTE",
            None,
            ("16/07/2026", "2026-07-16"),
            None,
            ("R$ 245,90", "245.90"),
        ),
    },
    "inv002": {
        "type": "INVOICE",
        "fields": document_fields(
            "INVOICE",
            "INV-2026-002",
            "DELTA PAPELARIA FICTICIA",
            ALPHANUMERIC_CNPJS[1],
            ("17/07/2026", "2026-07-17"),
            ("17/08/2026", "2026-08-17"),
            ("R$ 3.210,00", "3210.00"),
        ),
    },
    "slip002": {
        "type": "PAYMENT_SLIP",
        "fields": document_fields(
            "PAYMENT_SLIP",
            "BOL-2026-202",
            "ECO ENERGIA DE TESTE",
            NUMERIC_CNPJS[1],
            None,
            ("20/08/2026", "2026-08-20"),
            ("R$ 456,78", "456.78"),
        ),
    },
    "rec002": {
        "type": "RECEIPT",
        "fields": document_fields(
            "RECEIPT",
            "REC-2026-002",
            "FLORA APOIO SINTETICO",
            ALPHANUMERIC_CNPJS[2],
            ("18/07/2026", "2026-07-18"),
            None,
            ("R$ 89,90", "89.90"),
        ),
    },
    "slip003": {
        "type": "PAYMENT_SLIP",
        "fields": document_fields(
            "PAYMENT_SLIP",
            "BOL-2026-303",
            "GAMA LOCACOES TESTE",
            NUMERIC_CNPJS[2],
            None,
            ("22/08/2026", "2026-08-22"),
            ("R$ 2.000,50", "2000.50"),
        ),
    },
    "rec003": {
        "type": "RECEIPT",
        "fields": document_fields(
            "RECEIPT",
            "REC-2026-003",
            "HORIZONTE MANUTENCAO TESTE",
            NUMERIC_CNPJS[3],
            ("19/07/2026", "2026-07-19"),
            None,
            ("R$ 710,00", "710.00"),
        ),
    },
    "inv003": {
        "type": "INVOICE",
        "fields": document_fields(
            "INVOICE",
            "INV-2026-003",
            "IRIS TECNOLOGIA FICTICIA",
            ALPHANUMERIC_CNPJS[3],
            ("20/07/2026", "2026-07-20"),
            ("20/08/2026", "2026-08-20"),
            ("R$ 5.678,90", "5678.90"),
        ),
    },
    "slip004": {
        "type": "PAYMENT_SLIP",
        "fields": document_fields(
            "PAYMENT_SLIP",
            "BOL-2026-404",
            "JARDIM TELECOM TESTE",
            ALPHANUMERIC_CNPJS[4],
            None,
            ("25/08/2026", "2026-08-25"),
            ("R$ 345,67", "345.67"),
        ),
    },
    "rec004": {
        "type": "RECEIPT",
        "fields": document_fields(
            "RECEIPT",
            "REC-2026-004",
            "KAPPA LIMPEZA TESTE",
            NUMERIC_CNPJS[4],
            ("21/07/2026", "2026-07-21"),
            None,
            ("R$ 150,00", "150.00"),
        ),
    },
    "other001": {
        "type": "OTHER",
        "fields": document_fields(
            "OTHER",
            "DOC-2026-901",
            "LAGO AZUL FICTICIO",
            ALPHANUMERIC_CNPJS[5],
            ("22/07/2026", "2026-07-22"),
            None,
            ("R$ 75,00", "75.00"),
        ),
    },
    "rec005": {
        "type": "RECEIPT",
        "fields": document_fields(
            "RECEIPT",
            "REC-2026-005",
            "MOSAICO APOIO TESTE",
            NUMERIC_CNPJS[5],
            ("23/07/2026", "2026-07-23"),
            None,
            ("R$ 630,40", "630.40"),
        ),
    },
    "other002": {
        "type": "OTHER",
        "fields": document_fields(
            "OTHER",
            "DOC-2026-902",
            "NORTE ARQUIVOS FICTICIOS",
            ALPHANUMERIC_CNPJS[6],
            ("24/07/2026", "2026-07-24"),
            None,
            ("R$ 42,00", "42.00"),
        ),
    },
}


def _mutated_document(base: str, mutation: str) -> dict[str, Any]:
    document = deepcopy(BASE_DOCUMENTS[base])
    fields = document["fields"]
    if mutation == "missing_field":
        fields["document_number"] = field(None, None, "MISSING")
    elif mutation == "date_conflict":
        fields["issued_on"] = field("30/07/2026", "2026-07-30")
        fields["due_on"] = field("20/07/2026", "2026-07-20")
    elif mutation == "invalid_amount":
        fields["total_amount"] = field("R$ VALOR ILEGIVEL", None, "AMBIGUOUS")
    elif mutation == "invalid_tax_id":
        valid = ALPHANUMERIC_CNPJS[7]
        invalid = valid[:-1] + ("0" if valid[-1] != "0" else "1")
        fields["issuer_tax_id"] = field(invalid, invalid)
    else:
        raise ValueError(f"unknown mutation: {mutation}")
    return document


def fixture_catalog() -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []

    def add(
        fixture_id: str,
        family_id: str,
        split: str,
        modality: str,
        kind: str,
        document: dict[str, Any] | None,
        assessment: str,
        routing: str,
        reason_codes: list[str],
        extension: str,
        advertised_mime: str,
        expected_mime: str,
        **extra: Any,
    ) -> None:
        scenario_group = extra.pop("scenario_group", modality)
        fixtures.append(
            {
                "id": fixture_id,
                "family_id": family_id,
                "split": split,
                "modality": modality,
                "scenario_group": scenario_group,
                "kind": kind,
                "document": deepcopy(document),
                "document_type": document["type"] if document else "OTHER",
                "assessment": assessment,
                "routing": routing,
                "reason_codes": reason_codes,
                "extension": extension,
                "advertised_mime": advertised_mime,
                "expected_mime": expected_mime,
                **extra,
            }
        )

    valid_review = ["NATIVE_TEXT_SUFFICIENT", "REVIEW_POLICY_TRIGGERED"]
    ocr_review = ["NATIVE_TEXT_ABSENT", "REVIEW_POLICY_TRIGGERED"]
    add("dev-inv001-native", "cf-inv001", "development", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["inv001"], "USE_NATIVE", "OPEN_REVIEW", valid_review, "pdf", "application/pdf", "application/pdf")
    add("dev-inv001-scan", "cf-inv001", "development", "SCAN", "scan_pdf", BASE_DOCUMENTS["inv001"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "pdf", "application/pdf", "application/pdf", derived_from="dev-inv001-native")
    add("val-slip001-native", "cf-slip001", "validation", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["slip001"], "USE_NATIVE", "OPEN_REVIEW", valid_review, "pdf", "application/pdf", "application/pdf")
    add("val-slip001-scan", "cf-slip001", "validation", "SCAN", "scan_pdf", BASE_DOCUMENTS["slip001"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "pdf", "application/pdf", "application/pdf", derived_from="val-slip001-native")
    add("dev-rec001-native", "cf-rec001", "development", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["rec001"], "USE_NATIVE", "OPEN_REVIEW", valid_review, "pdf", "application/pdf", "application/pdf")
    add("dev-rec001-scan", "cf-rec001", "development", "SCAN", "scan_pdf", BASE_DOCUMENTS["rec001"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "pdf", "application/pdf", "application/pdf", derived_from="dev-rec001-native")
    add("test-inv002-native", "cf-inv002", "test", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["inv002"], "USE_NATIVE", "OPEN_REVIEW", valid_review, "pdf", "application/pdf", "application/pdf")
    add("test-inv002-scan", "cf-inv002", "test", "SCAN", "scan_pdf", BASE_DOCUMENTS["inv002"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "pdf", "application/pdf", "application/pdf", derived_from="test-inv002-native")
    add("dev-slip002-native", "cf-slip002", "development", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["slip002"], "USE_NATIVE", "OPEN_REVIEW", valid_review, "pdf", "application/pdf", "application/pdf")
    add("test-rec002-native", "cf-rec002", "test", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["rec002"], "USE_NATIVE", "OPEN_REVIEW", valid_review, "pdf", "application/pdf", "application/pdf")
    add("test-slip003-scan", "cf-slip003", "test", "SCAN", "scan_pdf", BASE_DOCUMENTS["slip003"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "pdf", "application/pdf", "application/pdf")
    add("dev-rec003-scan", "cf-rec003", "development", "SCAN", "scan_pdf", BASE_DOCUMENTS["rec003"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "pdf", "application/pdf", "application/pdf")
    add("val-inv003-png", "cf-inv003", "validation", "IMAGE", "png", BASE_DOCUMENTS["inv003"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "png", "image/png", "image/png")
    add("dev-slip004-jpeg-deg", "cf-slip004", "development", "IMAGE", "jpeg", BASE_DOCUMENTS["slip004"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "jpg", "image/jpeg", "image/jpeg", degraded=True)
    add("dev-rec004-png-r090", "cf-rec004", "development", "IMAGE", "png", BASE_DOCUMENTS["rec004"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "png", "image/png", "image/png", rotation=90)
    add("test-other001-jpeg", "cf-other001", "test", "IMAGE", "jpeg", BASE_DOCUMENTS["other001"], "OCR_REQUIRED", "OPEN_REVIEW", ocr_review, "jpg", "image/jpeg", "image/jpeg", degraded=True)
    hybrid_codes = ["NATIVE_TEXT_PARTIAL", "HYBRID_CONTENT", "REVIEW_POLICY_TRIGGERED"]
    add("val-rec005-hybrid", "cf-rec005", "validation", "HYBRID", "hybrid_pdf", BASE_DOCUMENTS["rec005"], "REVIEW_REQUIRED", "OPEN_REVIEW", hybrid_codes, "pdf", "application/pdf", "application/pdf")
    add("dev-other002-hybrid", "cf-other002", "development", "HYBRID", "hybrid_pdf", BASE_DOCUMENTS["other002"], "REVIEW_REQUIRED", "OPEN_REVIEW", hybrid_codes, "pdf", "application/pdf", "application/pdf")
    add("dev-inv001-duplicate", "cf-inv001", "development", "BORN_DIGITAL", "duplicate", BASE_DOCUMENTS["inv001"], "USE_NATIVE", "OPEN_REVIEW", ["NATIVE_TEXT_SUFFICIENT", "DUPLICATE_CONTENT", "REVIEW_POLICY_TRIGGERED"], "pdf", "application/pdf", "application/pdf", duplicate_of="dev-inv001-native", failure_stage="intake_deduplication", scenario_group="FAILURE_LIMIT")
    add("dev-encrypted-pdf", "af-encrypted", "development", "BORN_DIGITAL", "encrypted_pdf", None, "QUARANTINE", "QUARANTINE_INPUT", ["ENCRYPTED_INPUT"], "pdf", "application/pdf", "application/pdf", failure_stage="probe", password="erp-docflow", scenario_group="FAILURE_LIMIT")
    add("test-corrupt-pdf", "cf-inv002", "test", "BORN_DIGITAL", "corrupt_pdf", BASE_DOCUMENTS["inv002"], "QUARANTINE", "QUARANTINE_INPUT", ["CORRUPT_INPUT"], "pdf", "application/pdf", "application/pdf", derived_from="test-inv002-native", failure_stage="probe", scenario_group="FAILURE_LIMIT")
    add("dev-mime-mismatch", "af-mime", "development", "BORN_DIGITAL", "text_pdf", BASE_DOCUMENTS["inv001"], "REVIEW_REQUIRED", "QUARANTINE_INPUT", ["MIME_MISMATCH"], "jpg", "image/jpeg", "application/pdf", failure_stage="probe", scenario_group="FAILURE_LIMIT")
    add("dev-unsupported-tiff", "af-unsupported", "development", "IMAGE", "tiff", BASE_DOCUMENTS["rec001"], "QUARANTINE", "QUARANTINE_INPUT", ["UNSUPPORTED_FORMAT"], "tiff", "image/tiff", "image/tiff", failure_stage="intake", scenario_group="FAILURE_LIMIT")
    add("val-resource-limit", "af-resource", "validation", "BORN_DIGITAL", "resource_limit_pdf", BASE_DOCUMENTS["inv003"], "QUARANTINE", "QUARANTINE_INPUT", ["RESOURCE_LIMIT_EXCEEDED"], "pdf", "application/pdf", "application/pdf", failure_stage="probe", scenario_group="FAILURE_LIMIT")
    invalid_cases = [
        ("dev-val-missing-field", "missing_field", "REQUIRED_FIELD_MISSING"),
        ("dev-val-date-conflict", "date_conflict", "VALIDATION_CONFLICT"),
        ("dev-val-invalid-amount", "invalid_amount", "INVALID_AMOUNT"),
        ("dev-val-invalid-taxid", "invalid_tax_id", "INVALID_TAX_ID"),
    ]
    for fixture_id, mutation, reason in invalid_cases:
        validation_reasons = [reason]
        if mutation == "invalid_amount":
            validation_reasons.insert(0, "REQUIRED_FIELD_MISSING")
        add(
            fixture_id,
            "af-invalid-taxid" if mutation == "invalid_tax_id" else "af-validation",
            "development",
            "BORN_DIGITAL",
            "text_pdf",
            _mutated_document("inv001", mutation),
            "USE_NATIVE",
            "OPEN_REVIEW",
            ["NATIVE_TEXT_SUFFICIENT", *validation_reasons, "REVIEW_POLICY_TRIGGERED"],
            "pdf",
            "application/pdf",
            "application/pdf",
            mutation=mutation,
            failure_stage="validate",
            scenario_group="FAILURE_LIMIT",
        )

    return fixtures


LABELS = {
    "document_type": "TIPO",
    "document_number": "NUMERO",
    "issuer_name": "EMISSOR",
    "issuer_tax_id": "CNPJ",
    "issued_on": "EMISSAO",
    "due_on": "VENCIMENTO",
    "total_amount": "VALOR",
    "currency": "MOEDA",
}


def document_lines(document: dict[str, Any] | None) -> list[str]:
    if not document:
        return ["ARQUIVO SINTETICO SEM CONTEUDO DE NEGOCIO"]
    lines = ["ERP DOCFLOW - DADOS SINTETICOS"]
    for name, value in document["fields"].items():
        raw = value["raw_value"]
        if raw is None:
            raw = "NAO APLICAVEL" if value["applicability"] == "NOT_APPLICABLE" else "AUSENTE"
        lines.append(f"{LABELS[name]}: {raw}")
    lines.append("SEM VALIDADE FISCAL OU FINANCEIRA")
    return lines


FONT_5X7: dict[str, tuple[str, ...]] = {
    " ": ("00000",) * 7,
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    ",": ("00000", "00000", "00000", "00000", "00110", "00110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ":": ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
}


def render_lines(
    lines: Iterable[str],
    width: int = 720,
    height: int = 480,
    scale: int = 3,
    degraded: bool = False,
    rotation: int = 0,
) -> tuple[int, int, bytes]:
    background = 222 if degraded else 255
    foreground = 50 if degraded else 0
    pixels = bytearray([background]) * (width * height)
    x0, y0 = 24, 28
    char_advance = 6 * scale
    line_advance = 9 * scale
    for line_index, line in enumerate(lines):
        y = y0 + line_index * line_advance
        for char_index, char in enumerate(line.upper()[:37]):
            glyph = FONT_5X7.get(char, FONT_5X7["?"])
            x = x0 + char_index * char_advance
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit != "1":
                        continue
                    for sy in range(scale):
                        for sx in range(scale):
                            px = x + gx * scale + sx
                            py = y + gy * scale + sy
                            if 0 <= px < width and 0 <= py < height:
                                pixels[py * width + px] = foreground
    if degraded:
        rng = random.Random(SEED + sum(pixels[:32]))
        for index in range(0, len(pixels), 7):
            pixels[index] = max(0, min(255, pixels[index] + rng.randint(-28, 28)))
    if rotation == 90:
        rotated = bytearray(width * height)
        new_width, new_height = height, width
        rotated = bytearray(new_width * new_height)
        for y in range(height):
            for x in range(width):
                nx = height - 1 - y
                ny = x
                rotated[ny * new_width + nx] = pixels[y * width + x]
        return new_width, new_height, bytes(rotated)
    return width, height, bytes(pixels)


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def encode_png(width: int, height: int, pixels: bytes) -> bytes:
    rows = b"".join(
        b"\x00" + pixels[row * width : (row + 1) * width]
        for row in range(height)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(rows, 9))
        + _png_chunk(b"IEND", b"")
    )


JPEG_QTABLE = [
    16, 11, 10, 16, 24, 40, 51, 61,
    12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56,
    14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77,
    24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101,
    72, 92, 95, 98, 112, 100, 103, 99,
]
ZIGZAG = [
    0, 1, 8, 16, 9, 2, 3, 10,
    17, 24, 32, 25, 18, 11, 4, 5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13, 6, 7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63,
]
DC_BITS = [0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
DC_VALUES = list(range(12))
AC_BITS = [0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7D]
AC_VALUES = [
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41,
    0x06, 0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91,
    0xA1, 0x08, 0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24,
    0x33, 0x62, 0x72, 0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A,
    0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38,
    0x39, 0x3A, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x53,
    0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0x63, 0x64, 0x65, 0x66,
    0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79,
    0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A, 0x92, 0x93,
    0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3, 0xA4, 0xA5,
    0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7,
    0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
    0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1,
    0xE2, 0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2,
    0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA,
]


def _huffman_codes(bits: list[int], values: list[int]) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    code = 0
    index = 0
    for length, count in enumerate(bits, start=1):
        for _ in range(count):
            result[values[index]] = (code, length)
            index += 1
            code += 1
        code <<= 1
    return result


class _BitWriter:
    def __init__(self) -> None:
        self.output = bytearray()
        self.buffer = 0
        self.count = 0

    def write(self, value: int, length: int) -> None:
        self.buffer = (self.buffer << length) | (value & ((1 << length) - 1))
        self.count += length
        while self.count >= 8:
            self.count -= 8
            byte = (self.buffer >> self.count) & 0xFF
            self.output.append(byte)
            if byte == 0xFF:
                self.output.append(0)
        self.buffer &= (1 << self.count) - 1 if self.count else 0

    def finish(self) -> bytes:
        if self.count:
            self.write((1 << (8 - self.count)) - 1, 8 - self.count)
        return bytes(self.output)


def _amplitude(value: int) -> tuple[int, int]:
    if value == 0:
        return 0, 0
    size = abs(value).bit_length()
    encoded = value if value > 0 else value + (1 << size) - 1
    return size, encoded


COSINE = [[math.cos((2 * position + 1) * frequency * math.pi / 16) for position in range(8)] for frequency in range(8)]


def _dct_quantized(block: list[list[int]]) -> list[int]:
    temp = [[0.0] * 8 for _ in range(8)]
    for frequency_x in range(8):
        for y in range(8):
            temp[frequency_x][y] = sum(
                (block[y][x] - 128) * COSINE[frequency_x][x] for x in range(8)
            )
    coefficients = [0] * 64
    for frequency_y in range(8):
        for frequency_x in range(8):
            value = sum(
                temp[frequency_x][y] * COSINE[frequency_y][y] for y in range(8)
            )
            scale = 0.25
            if frequency_x == 0:
                scale /= math.sqrt(2)
            if frequency_y == 0:
                scale /= math.sqrt(2)
            index = frequency_y * 8 + frequency_x
            coefficients[index] = round(value * scale / JPEG_QTABLE[index])
    return [coefficients[index] for index in ZIGZAG]


def _jpeg_segment(marker: int, payload: bytes) -> bytes:
    return b"\xff" + bytes([marker]) + struct.pack(">H", len(payload) + 2) + payload


def encode_jpeg(width: int, height: int, pixels: bytes) -> bytes:
    dc_codes = _huffman_codes(DC_BITS, DC_VALUES)
    ac_codes = _huffman_codes(AC_BITS, AC_VALUES)
    writer = _BitWriter()
    previous_dc = 0
    for block_y in range(0, height, 8):
        for block_x in range(0, width, 8):
            block = [
                [
                    pixels[min(block_y + y, height - 1) * width + min(block_x + x, width - 1)]
                    for x in range(8)
                ]
                for y in range(8)
            ]
            values = _dct_quantized(block)
            difference = values[0] - previous_dc
            previous_dc = values[0]
            size, amplitude = _amplitude(difference)
            code, length = dc_codes[size]
            writer.write(code, length)
            if size:
                writer.write(amplitude, size)
            run = 0
            for value in values[1:]:
                if value == 0:
                    run += 1
                    continue
                while run >= 16:
                    code, length = ac_codes[0xF0]
                    writer.write(code, length)
                    run -= 16
                size, amplitude = _amplitude(value)
                symbol = (run << 4) | size
                code, length = ac_codes[symbol]
                writer.write(code, length)
                writer.write(amplitude, size)
                run = 0
            if run:
                code, length = ac_codes[0x00]
                writer.write(code, length)
    entropy = writer.finish()
    app0 = b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    dqt = bytes([0]) + bytes(JPEG_QTABLE[index] for index in ZIGZAG)
    sof0 = struct.pack(">BHHB", 8, height, width, 1) + b"\x01\x11\x00"
    dht_dc = b"\x00" + bytes(DC_BITS) + bytes(DC_VALUES)
    dht_ac = b"\x10" + bytes(AC_BITS) + bytes(AC_VALUES)
    sos = b"\x01\x01\x00\x00\x3f\x00"
    return (
        b"\xff\xd8"
        + _jpeg_segment(0xE0, app0)
        + _jpeg_segment(0xDB, dqt)
        + _jpeg_segment(0xC0, sof0)
        + _jpeg_segment(0xC4, dht_dc)
        + _jpeg_segment(0xC4, dht_ac)
        + _jpeg_segment(0xDA, sos)
        + entropy
        + b"\xff\xd9"
    )


def encode_tiff(width: int, height: int, pixels: bytes) -> bytes:
    entries = [
        (256, 4, 1, width),
        (257, 4, 1, height),
        (258, 3, 1, 8),
        (259, 3, 1, 1),
        (262, 3, 1, 1),
        (273, 4, 1, 8 + 2 + 9 * 12 + 4),
        (277, 3, 1, 1),
        (278, 4, 1, height),
        (279, 4, 1, len(pixels)),
    ]
    header = b"II*\x00" + struct.pack("<I", 8)
    ifd = struct.pack("<H", len(entries))
    for tag, kind, count, value in entries:
        packed_value = struct.pack("<H", value) + b"\x00\x00" if kind == 3 else struct.pack("<I", value)
        ifd += struct.pack("<HHI", tag, kind, count) + packed_value
    ifd += struct.pack("<I", 0)
    return header + ifd + pixels


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(
    page_specs: list[dict[str, Any]],
    encrypted_password: str | None = None,
) -> bytes:
    objects: list[bytes | None] = [None, None, None]
    stream_ids: list[int] = []

    def add(value: bytes | None = None) -> int:
        objects.append(value)
        return len(objects)

    page_ids: list[int] = []
    for spec in page_specs:
        if spec["kind"] == "text":
            commands = ["BT", "/F1 14 Tf", "48 790 Td"]
            for line in spec["lines"]:
                commands.append(f"({_pdf_escape(line)}) Tj")
                commands.append("0 -24 Td")
            commands.append("ET")
            content = ("\n".join(commands) + "\n").encode("ascii")
            content_id = add(b"<< /Length %d >>\nstream\n" % len(content) + content + b"endstream")
            stream_ids.append(content_id)
            page_id = add()
            objects[page_id - 1] = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
            ).encode("ascii")
        else:
            width = spec["width"]
            height = spec["height"]
            compressed = zlib.compress(spec["pixels"], 9)
            image_object = (
                f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
                f"/ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode "
                f"/Length {len(compressed)} >>\nstream\n"
            ).encode("ascii") + compressed + b"\nendstream"
            image_id = add(image_object)
            stream_ids.append(image_id)
            content = f"q\n595 0 0 397 0 220 cm\n/Im0 Do\nQ\n".encode("ascii")
            content_id = add(b"<< /Length %d >>\nstream\n" % len(content) + content + b"endstream")
            stream_ids.append(content_id)
            page_id = add()
            objects[page_id - 1] = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /XObject << /Im0 {image_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode("ascii")
        page_ids.append(page_id)
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
    objects[2] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    encrypt_id = None
    file_id = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    if encrypted_password is not None:
        permissions = -4
        owner_entry, user_entry, encryption_key = _pdf_revision_2_security(
            encrypted_password,
            "erp-docflow-owner",
            permissions,
            file_id,
        )
        for object_id in stream_ids:
            value = objects[object_id - 1]
            if value is None:
                raise AssertionError(f"unset encrypted stream object {object_id}")
            length_match = re.search(rb"/Length ([0-9]+)", value)
            if length_match is None:
                raise AssertionError(f"missing stream length for object {object_id}")
            stream_length = int(length_match.group(1))
            stream_start = value.index(b"stream\n") + len(b"stream\n")
            stream_end = stream_start + stream_length
            encrypted_stream = _rc4(
                _pdf_object_key(encryption_key, object_id),
                value[stream_start:stream_end],
            )
            objects[object_id - 1] = (
                value[:stream_start] + encrypted_stream + value[stream_end:]
            )
        encrypt_id = add(
            b"<< /Filter /Standard /V 1 /R 2 /Length 40 /P -4 "
            + b"/O <" + owner_entry.hex().upper().encode("ascii") + b"> "
            + b"/U <" + user_entry.hex().upper().encode("ascii") + b"> >>"
        )
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, value in enumerate(objects, start=1):
        if value is None:
            raise AssertionError(f"unset PDF object {object_id}")
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(value)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R"
    if encrypt_id:
        file_id_hex = file_id.hex().upper()
        trailer += f" /Encrypt {encrypt_id} 0 R /ID [<{file_id_hex}><{file_id_hex}>]"
    trailer += f" >>\nstartxref\n{xref_offset}\n%%EOF\n"
    output.extend(trailer.encode("ascii"))
    return bytes(output)


def fixture_bytes(case: dict[str, Any], already_generated: dict[str, bytes]) -> tuple[bytes, int]:
    kind = case["kind"]
    lines = document_lines(case["document"])
    if kind == "duplicate":
        source = case["duplicate_of"]
        return already_generated[source], 1
    if kind == "text_pdf":
        return build_pdf([{"kind": "text", "lines": lines}]), 1
    width, height, pixels = render_lines(
        lines,
        degraded=case.get("degraded", False),
        rotation=case.get("rotation", 0),
    )
    if kind == "scan_pdf":
        return build_pdf([{"kind": "image", "width": width, "height": height, "pixels": pixels}]), 1
    if kind == "hybrid_pdf":
        return build_pdf(
            [
                {"kind": "text", "lines": ["ERP DOCFLOW - PAGINA NATIVA PARCIAL"]},
                {"kind": "image", "width": width, "height": height, "pixels": pixels},
            ]
        ), 2
    if kind == "png":
        return encode_png(width, height, pixels), 1
    if kind == "jpeg":
        return encode_jpeg(width, height, pixels), 1
    if kind == "tiff":
        return encode_tiff(width, height, pixels), 1
    if kind == "encrypted_pdf":
        return build_pdf(
            [{"kind": "text", "lines": lines}],
            encrypted_password=case["password"],
        ), 1
    if kind == "corrupt_pdf":
        return (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [BROKEN] /Count 1 >>\nendobj\n"
            b"startxref\n9999999999\n%%EOF\n",
            1,
        )
    if kind == "resource_limit_pdf":
        pdf = build_pdf(
            [
                {"kind": "text", "lines": [f"PAGINA SINTETICA {page + 1}"]}
                for page in range(MAX_PAGES + 1)
            ]
        )
        target_size = MAX_FILE_BYTES + 1
        if len(pdf) < target_size:
            pdf += b"\n% SYNTHETIC SIZE LIMIT PADDING\n" + b"0" * (target_size - len(pdf) - 32)
        return pdf, MAX_PAGES + 1
    raise ValueError(f"unknown fixture kind: {kind}")


def ground_truth(case: dict[str, Any], page_count: int) -> dict[str, Any]:
    document = case["document"]
    canonical = "\n".join(document_lines(document)) if document else ""
    evidence_page = 2 if case["modality"] == "HYBRID" else 1
    artifact_ref = f"files/{case['id']}.{case['extension']}"

    def output_field(name: str, value: dict[str, Any]) -> dict[str, Any]:
        result = deepcopy(value)
        has_evidence = (
            value["applicability"] in {"PRESENT", "AMBIGUOUS"}
            and value["raw_value"] is not None
        )
        result["evidence_refs"] = (
            [
                {
                    "artifact_ref": artifact_ref,
                    "page": evidence_page,
                    "excerpt": f"{LABELS[name]}: {value['raw_value']}",
                    "bbox": None,
                    "coordinate_space": None,
                }
            ]
            if has_evidence
            else []
        )
        return result

    expected_output = None
    if document and case["routing"] != "QUARANTINE_INPUT":
        annotated_fields = document["fields"]
        expected_output = {
            "schema_id": "payable_document",
            "schema_version": DATASET_VERSION,
            "document_type": output_field(
                "document_type", annotated_fields["document_type"]
            ),
            "fields": {
                name: output_field(name, value)
                for name, value in annotated_fields.items()
                if name != "document_type"
            },
        }
    invalid_codes = {
        "REQUIRED_FIELD_MISSING",
        "VALIDATION_CONFLICT",
        "INVALID_TAX_ID",
        "INVALID_DATE",
        "INVALID_AMOUNT",
    }
    validations = [
        {
            "code": reason,
            "status": "FAIL" if reason in invalid_codes else "PASS",
        }
        for reason in case["reason_codes"]
        if reason in invalid_codes
    ]
    if not validations and document:
        validations = [{"code": "PROFILE_FIELDS", "status": "PASS"}]
    return {
        "ground_truth_version": DATASET_VERSION,
        "fixture_id": case["id"],
        "classification": (
            {
                "label": case["document_type"],
                "allowed_alternatives": [],
            }
            if document
            else None
        ),
        "canonical_text": canonical,
        "expected_output": expected_output,
        "expected_validations": validations,
        "expected_failure_stage": case.get("failure_stage"),
        "page_count": page_count,
        "notes": ["Synthetic fixture; no fiscal or financial validity."],
    }


def generate_dataset(target: Path) -> dict[str, Any]:
    files_dir = target / "files"
    truth_dir = target / "ground_truth"
    files_dir.mkdir(parents=True, exist_ok=True)
    truth_dir.mkdir(parents=True, exist_ok=True)
    (target / ".gitattributes").write_bytes(DATASET_GIT_ATTRIBUTES)
    generated: dict[str, bytes] = {}
    manifest_fixtures: list[dict[str, Any]] = []
    for case in fixture_catalog():
        payload, page_count = fixture_bytes(case, generated)
        generated[case["id"]] = payload
        relative_file = Path("files") / f"{case['id']}.{case['extension']}"
        relative_truth = Path("ground_truth") / f"{case['id']}.json"
        (target / relative_file).write_bytes(payload)
        truth_payload = json_bytes(ground_truth(case, page_count))
        (target / relative_truth).write_bytes(truth_payload)
        manifest_fixtures.append(
            {
                "id": case["id"],
                "family_id": case["family_id"],
                "path": relative_file.as_posix(),
                "advertised_mime": case["advertised_mime"],
                "expected_mime": case["expected_mime"],
                "modality": case["modality"],
                "scenario_group": case["scenario_group"],
                "document_type": case["document_type"],
                "split": case["split"],
                "sha256": sha256_bytes(payload),
                "size_bytes": len(payload),
                "page_count": page_count,
                "generation": {
                    "kind": case["kind"],
                    "seed": SEED,
                    "parameters": {
                        key: case[key]
                        for key in ("rotation", "degraded", "mutation", "password")
                        if key in case
                    },
                },
                "ground_truth": relative_truth.as_posix(),
                "ground_truth_sha256": sha256_bytes(truth_payload),
                "ground_truth_size_bytes": len(truth_payload),
                "derived_from": case.get("derived_from"),
                "duplicate_of": case.get("duplicate_of"),
                "expected": {
                    "assessment": case["assessment"],
                    "routing": case["routing"],
                    "reason_codes": case["reason_codes"],
                    "failure_stage": case.get("failure_stage"),
                },
            }
        )
    manifest = {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "seed": SEED,
        "classification": "synthetic",
        "purpose": "Local development, benchmark and acceptance only",
        "license": "Project-generated synthetic fixtures",
        "generated_by": "tools/document_fixtures/generate.py",
        "profile_ref": "profiles/payable_document_pt_br/v1alpha/profile.json",
        "expected_output_schema_ref": "profiles/payable_document_pt_br/v1alpha/extraction.schema.json",
        "split_policy": {
            "unit": "family_id",
            "development": 0.6,
            "validation": 0.2,
            "test": 0.2,
            "leakage_rule": "all variants and duplicates of a family stay in one split",
        },
        "fixtures": manifest_fixtures,
    }
    (target / "manifest.json").write_bytes(json_bytes(manifest))
    return manifest


def relative_file_map(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
