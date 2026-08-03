from __future__ import annotations

import dataclasses

import pytest

from erp_docflow_api.intake import (
    IdempotencyKey,
    IntakeDomainError,
    IntakeFingerprint,
    MimeMismatch,
    determine_mime_mismatch,
    normalize_mime,
)


def test_fingerprint_is_nfc_normalized_and_has_exact_canonical_form() -> None:
    fingerprint = IntakeFingerprint(
        content_sha256="a" * 64,
        byte_size=4096,
        advertised_mime=" Application/PDF; charset=binary ",
        original_filename="Cafe\u0301.pdf",
        source_channel=" UPLOAD ",
    )

    assert fingerprint.original_filename == "Café.pdf"
    assert fingerprint.advertised_mime == "application/pdf"
    assert fingerprint.canonical_json == (
        '{"advertised_mime":"application/pdf","byte_size":4096,'
        '"content_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
        '"original_filename":"Café.pdf","source_channel":"upload",'
        '"version":"document-intake-v1"}'
    )
    assert fingerprint.sha256 == (
        "86b1b355850f820a8cad835126c775496c8c3646a6434c77ba5ae746d5b713f9"
    )


def test_fingerprint_equivalence_uses_normalized_semantics() -> None:
    decomposed = IntakeFingerprint(
        content_sha256="b" * 64,
        byte_size=1,
        advertised_mime="IMAGE/JPEG; q=1",
        original_filename="cafe\u0301.jpg",
    )
    composed = IntakeFingerprint(
        content_sha256="b" * 64,
        byte_size=1,
        advertised_mime="image/jpeg",
        original_filename="café.jpg",
    )

    assert decomposed == composed
    assert decomposed.sha256 == composed.sha256


@pytest.mark.parametrize("value", ["", "x" * 129, "has\nnewline", "has\u200bformat"])
def test_idempotency_key_rejects_invalid_values(value: str) -> None:
    with pytest.raises(IntakeDomainError):
        IdempotencyKey.from_raw(value)


def test_idempotency_key_is_case_sensitive_and_discards_cleartext() -> None:
    lower = IdempotencyKey.from_raw("invoice-1")
    upper = IdempotencyKey.from_raw("Invoice-1")

    assert lower.digest != upper.digest
    assert "invoice-1" not in repr(lower)
    assert len(lower.digest) == 64


@pytest.mark.parametrize(
    ("advertised", "detected", "expected", "database_value"),
    [
        ("application/pdf", "APPLICATION/PDF", MimeMismatch.MATCH, False),
        ("application/pdf", "image/png", MimeMismatch.MISMATCH, True),
        (None, "application/pdf", MimeMismatch.INDETERMINATE, None),
        ("application/pdf", None, MimeMismatch.INDETERMINATE, None),
        ("   ", "application/pdf", MimeMismatch.INDETERMINATE, None),
    ],
)
def test_mime_mismatch_is_explicitly_tri_state(
    advertised: str | None,
    detected: str | None,
    expected: MimeMismatch,
    database_value: bool | None,
) -> None:
    result = determine_mime_mismatch(advertised, detected)

    assert result is expected
    assert result.database_value is database_value
    assert MimeMismatch.from_database_value(database_value) is expected


def test_mime_normalization_rejects_malformed_value() -> None:
    with pytest.raises(IntakeDomainError):
        normalize_mime("not a mime")


def test_fingerprint_is_immutable(fingerprint: IntakeFingerprint) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        fingerprint.byte_size = 2  # type: ignore[misc]
