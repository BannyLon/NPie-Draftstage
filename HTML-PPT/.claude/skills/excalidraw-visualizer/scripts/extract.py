#!/usr/bin/env python3
"""Extract plain text from .md / .txt / .docx / .pdf"""

import sys
import os
import argparse


def extract_from_markdown(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_from_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_from_docx(path):
    try:
        import docx
    except ImportError:
        print("Error: need python-docx. Run: pip install python-docx", file=sys.stderr)
        sys.exit(1)
    doc = docx.Document(path)
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paras)


def extract_from_pdf(path):
    try:
        import markitdown
        return markitdown.MarkItDown().convert(path).text_content
    except ImportError:
        print("Error: need markitdown. Run: pip install markitdown", file=sys.stderr)
        sys.exit(1)


EXTRACTORS = {
    '.md': extract_from_markdown,
    '.txt': extract_from_text,
    '.docx': extract_from_docx,
    '.pdf': extract_from_pdf,
}


def extract(path):
    _, ext = os.path.splitext(path)
    fn = EXTRACTORS.get(ext.lower())
    if not fn:
        raise ValueError(f"Unsupported format: {ext}")
    return fn(path)


def main():
    parser = argparse.ArgumentParser(description="Extract text from documents")
    parser.add_argument("filepath", help="Path to input file")
    args = parser.parse_args()
    print(extract(args.filepath))


if __name__ == "__main__":
    main()
