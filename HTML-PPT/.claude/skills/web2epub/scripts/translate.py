#!/usr/bin/env python3
"""Translate text to Chinese.

Backends (tried in order):
  1. OpenAI API (if OPENAI_API_KEY set)
  2. Youdao Translate (via translators library, works in China, no key needed)
  3. Falls back to original text if both fail
"""

import sys
import os


def _chunk_text(text: str, max_chars: int) -> list[str]:
    paragraphs = text.split("\n")
    chunks = []
    current = []
    for para in paragraphs:
        current.append(para)
        if sum(len(p) for p in current) >= max_chars:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    return chunks or [""]


def _translate_openai(text: str, source_lang: str = "") -> str | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None

    base_url = os.environ.get("OPENAI_BASE_URL", "")
    model = os.environ.get("TRANSLATE_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    lang_hint = f"（源语言：{source_lang}）" if source_lang else ""
    system_prompt = (
        "你是一个专业翻译。将以下内容翻译成中文。"
        "要求：\n"
        "1. 保持原文的Markdown格式（标题、列表、代码块、引用等）\n"
        "2. 专业术语准确\n"
        "3. 长句合理拆分，符合中文表达习惯\n"
        "4. 保留所有链接、图片等资源引用\n"
        "5. 代码片段不翻译\n"
        "6. 只输出翻译结果，不要额外说明\n"
    )

    result_parts = []
    for chunk in _chunk_text(text, 6000):
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请翻译以下内容{lang_hint}：\n\n{chunk}"},
            ],
            temperature=0.3,
        )
        result_parts.append(resp.choices[0].message.content or "")
    return "\n\n".join(result_parts)


def _translate_youdao(text: str, source_lang: str = "") -> str | None:
    try:
        import translators as ts
    except ImportError:
        return None

    src = source_lang if source_lang else "auto"
    chunks = _chunk_text(text, 1500)
    translated = []
    for chunk in chunks:
        if not chunk.strip():
            continue
        try:
            result = ts.translate_text(chunk, translator="youdao", from_lang=src, to_lang="zh")
            translated.append(result if result else chunk)
        except Exception:
            translated.append(chunk)
    return "\n\n".join(translated) if translated else None


def translate_text(text: str, source_lang: str = "") -> str:
    result = _translate_openai(text, source_lang)
    if result:
        return result

    result = _translate_youdao(text, source_lang)
    if result:
        return result

    return text


if __name__ == "__main__":
    text = sys.stdin.read()
    source_lang = sys.argv[1] if len(sys.argv) > 1 else ""
    result = translate_text(text, source_lang)
    print(result)
