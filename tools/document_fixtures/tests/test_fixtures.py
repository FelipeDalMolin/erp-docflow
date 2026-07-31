from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

from fixturelib import (  # noqa: E402
    ALPHANUMERIC_CNPJS,
    NUMERIC_CNPJS,
    _pdf_object_key,
    _pdf_revision_2_security,
    _rc4,
    fixture_catalog,
    generate_dataset,
    make_cnpj,
    relative_file_map,
    valid_cnpj,
)
from validate import validate_dataset  # noqa: E402


class FixtureGenerationTests(unittest.TestCase):
    def test_cnpj_numeric_and_alphanumeric_vectors(self) -> None:
        self.assertEqual(make_cnpj("123456780001"), "12345678000195")
        self.assertEqual(make_cnpj("12ABC34501DE"), "12ABC34501DE35")
        self.assertTrue(valid_cnpj("12.345.678/0001-95"))
        self.assertTrue(valid_cnpj("12.ABC.345/01DE-35"))
        for value in NUMERIC_CNPJS + ALPHANUMERIC_CNPJS:
            self.assertTrue(valid_cnpj(value), value)
        invalid = ALPHANUMERIC_CNPJS[0][:-1] + ("0" if ALPHANUMERIC_CNPJS[0][-1] != "0" else "1")
        self.assertFalse(valid_cnpj(invalid))
        self.assertFalse(valid_cnpj("00000000000000"))
        self.assertFalse(valid_cnpj("12ABC34501DÉ35"))

    def test_catalog_has_expected_families_and_no_split_leakage(self) -> None:
        catalog = fixture_catalog()
        self.assertEqual(len(catalog), 28)
        family_splits: dict[str, set[str]] = {}
        for item in catalog:
            family_splits.setdefault(item["family_id"], set()).add(item["split"])
        self.assertEqual(len(family_splits), 20)
        self.assertTrue(all(len(splits) == 1 for splits in family_splits.values()))
        self.assertEqual(
            Counter(item["scenario_group"] for item in catalog),
            Counter(
                {
                    "BORN_DIGITAL": 6,
                    "SCAN": 6,
                    "IMAGE": 4,
                    "HYBRID": 2,
                    "FAILURE_LIMIT": 10,
                }
            ),
        )

    def test_generation_is_byte_deterministic_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir) / "dataset"
            second = Path(second_dir) / "dataset"
            generate_dataset(first)
            generate_dataset(second)
            self.assertEqual(relative_file_map(first), relative_file_map(second))
            self.assertEqual(validate_dataset(first), [])
            manifest = json.loads((first / "manifest.json").read_text())
            truth_path = first / manifest["fixtures"][0]["ground_truth"]
            truth_path.write_bytes(truth_path.read_bytes() + b" ")
            self.assertTrue(
                any("ground truth sha256 mismatch" in error for error in validate_dataset(first))
            )

    def test_generated_magic_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "dataset"
            manifest = generate_dataset(target)
            by_id = {item["id"]: item for item in manifest["fixtures"]}
            self.assertTrue((target / by_id["dev-inv001-native"]["path"]).read_bytes().startswith(b"%PDF-"))
            self.assertTrue((target / by_id["val-inv003-png"]["path"]).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            jpeg = (target / by_id["dev-slip004-jpeg-deg"]["path"]).read_bytes()
            self.assertTrue(jpeg.startswith(b"\xff\xd8"))
            self.assertTrue(jpeg.endswith(b"\xff\xd9"))
            self.assertTrue((target / by_id["dev-unsupported-tiff"]["path"]).read_bytes().startswith(b"II*\x00"))

    def test_encrypted_pdf_uses_revision_2_stream_encryption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "dataset"
            manifest = generate_dataset(target)
            fixture = next(
                item for item in manifest["fixtures"] if item["id"] == "dev-encrypted-pdf"
            )
            payload = (target / fixture["path"]).read_bytes()
            self.assertIn(b"/Encrypt", payload)
            self.assertNotIn(b"ARQUIVO SINTETICO", payload)
            stream = re.search(
                rb"([0-9]+) 0 obj\n<< /Length ([0-9]+) >>\nstream\n",
                payload,
            )
            self.assertIsNotNone(stream)
            assert stream is not None
            object_id = int(stream.group(1))
            stream_length = int(stream.group(2))
            encrypted = payload[stream.end() : stream.end() + stream_length]
            owner, user, key = _pdf_revision_2_security(
                "erp-docflow",
                "erp-docflow-owner",
                -4,
                bytes.fromhex("00112233445566778899AABBCCDDEEFF"),
            )
            self.assertIn(owner.hex().upper().encode("ascii"), payload)
            self.assertIn(user.hex().upper().encode("ascii"), payload)
            plaintext = _rc4(_pdf_object_key(key, object_id), encrypted)
            self.assertIn(b"ARQUIVO SINTETICO", plaintext)


if __name__ == "__main__":
    unittest.main()
