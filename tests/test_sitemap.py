from __future__ import annotations

from typing import Any

import pytest

from toolkit.web_tools.sitemap import fetch_sitemap_urls, generate_sitemap


def test_generate_sitemap() -> None:
    result = generate_sitemap("https://example.com", ["/", "/about"])
    assert "https://example.com/" in result
    assert "https://example.com/about" in result


def test_generate_sitemap_invalid_url() -> None:
    with pytest.raises(ValueError):
        generate_sitemap("ftp://example.com", ["/"])


def test_fetch_sitemap_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    sample = (
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
        "<url><loc>https://example.com/</loc></url>"
        "<url><loc>https://example.com/about</loc></url>"
        "</urlset>"
    )

    class FakeResponse:
        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            return None

        def read(self) -> bytes:
            return sample.encode("utf-8")

    def fake_urlopen(*args: Any, **kwargs: Any) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr("toolkit.web_tools.sitemap.urlopen", fake_urlopen)

    urls = fetch_sitemap_urls("https://example.com/sitemap.xml", timeout=5)
    assert urls == ["https://example.com/", "https://example.com/about"]
