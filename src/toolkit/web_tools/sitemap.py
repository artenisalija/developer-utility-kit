"""Sitemap generation and fetching utilities."""

from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from defusedxml import ElementTree as DefusedET  # type: ignore[import-untyped]

DEFAULT_TIMEOUT = 10
_SCHEME_RE = re.compile(r"^https?$")


def generate_sitemap(base_url: str, paths: Iterable[str]) -> str:
    """Generate sitemap XML from base URL and relative/absolute paths."""
    _validate_url(base_url)
    urlset = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for path in paths:
        normalized = path.strip()
        if not normalized:
            continue
        full_url = _normalize_url(base_url, normalized)
        _validate_url(full_url)
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = full_url
    ET.indent(urlset, space="  ")
    return ET.tostring(urlset, encoding="unicode")


def fetch_sitemap_urls(url: str, timeout: int = DEFAULT_TIMEOUT) -> list[str]:
    """Fetch sitemap from URL and return contained links."""
    _validate_url(url)
    xml_content = _fetch_url(url, timeout=timeout)
    try:
        root = DefusedET.fromstring(xml_content)
    except DefusedET.ParseError as exc:
        raise ValueError(f"Invalid sitemap XML: {exc}") from exc
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    found = root.findall("sm:url/sm:loc", namespace)
    return [node.text for node in found if node.text]


def _fetch_url(url: str, timeout: int) -> str:
    request = Request(  # noqa: S310  # nosec B310
        url, headers={"User-Agent": "developer-utility-toolkit/0.1.0"}
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310  # nosec B310
        data: bytes = response.read()
    return data.decode("utf-8")


def _normalize_url(base_url: str, path: str) -> str:
    parsed = urlparse(path)
    if parsed.scheme and parsed.netloc:
        return path
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if not parsed.netloc or not _SCHEME_RE.match(parsed.scheme):
        raise ValueError("URL must be a valid http/https URL")
