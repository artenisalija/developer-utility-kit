from __future__ import annotations

from toolkit.core.hashing import generate_hash_report


def test_hash_report_has_expected_labels() -> None:
    report = generate_hash_report(b"hello", text_value="hello")
    labels = {item.label for item in report}
    assert "MD5 Hash Generator" in labels
    assert "SHA256 Hash Generator" in labels
    assert "Checksum Calculator" in labels
    assert len(report) == 23


def test_hash_report_ntlm_without_text() -> None:
    report = generate_hash_report(b"hello", text_value=None)
    ntlm = next(item for item in report if item.label == "NTLM Hash Generator")
    assert "Unavailable" in ntlm.value
