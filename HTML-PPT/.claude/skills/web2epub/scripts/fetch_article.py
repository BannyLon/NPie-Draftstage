#!/usr/bin/env python3
"""Fetch URL and extract clean article content for EPUB generation."""

import sys
import json
import re
from urllib.parse import urlparse

import requests
from trafilatura import extract, extract_metadata, bare_extraction


def fetch_url(url: str, timeout: int = 30) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()

    encoding = resp.apparent_encoding or resp.encoding or "utf-8"
    if encoding.lower() in ("ascii", "iso-8859-1"):
        match = re.search(
            rb'charset[="\s]+([a-zA-Z0-9_-]+)',
            resp.content[:5000],
            re.IGNORECASE,
        )
        if match:
            encoding = match.group(1).decode().lower()
        else:
            encoding = "utf-8"

    try:
        return resp.content.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        return resp.text


def _doc_to_dict(doc) -> dict:
    if doc is None:
        return {}
    if hasattr(doc, "title"):
        return {
            "title": doc.title or "",
            "author": doc.author or "",
            "date": doc.date or "",
            "text": doc.text or "",
            "image": doc.image or "",
            "description": doc.description or "",
        }
    if isinstance(doc, dict):
        return doc
    return {}


def extract_article(html: str, url: str = "") -> dict:
    for use_favor in ("precision", "recall"):
        result = bare_extraction(
            html,
            url=url,
            include_links=True,
            include_images=True,
            include_tables=True,
            output_format="markdown",
            favor_precision=(use_favor == "precision"),
            favor_recall=(use_favor == "recall"),
        )
        if result:
            result = result.as_dict()
            break

    metadata = extract_metadata(html, default_url=url)
    meta = _doc_to_dict(metadata)

    if result and result.get("text"):
        return {
            "title": result.get("title") or meta.get("title", ""),
            "author": result.get("author") or meta.get("author", ""),
            "date": result.get("date") or meta.get("date", ""),
            "text": result.get("text", ""),
            "image": result.get("image") or meta.get("image", ""),
            "url": url,
            "hostname": urlparse(url).netloc if url else "",
        }

    text = extract(html, url=url, output_format="markdown", favor_recall=True) or ""
    return {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "date": meta.get("date", ""),
        "text": text,
        "image": meta.get("image", ""),
        "url": url,
        "hostname": urlparse(url).netloc if url else "",
    }


def is_chinese(text: str) -> bool:
    if not text:
        return True
    sample = text[:2000]
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', sample))
    return chinese_chars > len(sample) * 0.05


def html_to_markdown(html: str, url: str = "") -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    return extract_article(str(soup), url=url)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url:
        print(json.dumps({"error": "No URL provided"}, ensure_ascii=False))
        sys.exit(1)

    html = fetch_url(url)
    article = extract_article(html, url=url)
    article["needs_translation"] = bool(article["text"]) and not is_chinese(article["text"])
    print(json.dumps(article, ensure_ascii=False))
