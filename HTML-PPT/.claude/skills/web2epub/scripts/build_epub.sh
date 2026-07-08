#!/bin/bash
set -euo pipefail

# build_epub.sh - Convert markdown/text/docx/pdf/txt to clean EPUB
# Usage: build_epub.sh -i <input> -o <output> [-t <title>] [-a <author>] [--css <file>]

INPUT=""
OUTPUT=""
TITLE=""
AUTHOR=""
CSS_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--input) INPUT="$2"; shift 2 ;;
    -o|--output) OUTPUT="$2"; shift 2 ;;
    -t|--title) TITLE="$2"; shift 2 ;;
    -a|--author) AUTHOR="$2"; shift 2 ;;
    --css) CSS_FILE="$2"; shift 2 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

[ -z "$INPUT" ] && { echo "Missing -i"; exit 1; }
[ -z "$OUTPUT" ] && { echo "Missing -o"; exit 1; }

EXT="${INPUT##*.}"
LOWEXT=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

# 编码检测与转换（仅限纯文本文件）
if [ "$LOWEXT" = "txt" ] || [ "$LOWEXT" = "md" ]; then
  RAW_BYTES=$(xxd -l 8 -p "$INPUT" 2>/dev/null)
  if echo "$RAW_BYTES" | grep -q "^efbbbf"; then
    ENC="UTF-8-SIG"
  elif echo "$RAW_BYTES" | grep -q "^fffe"; then
    ENC="UTF-16LE"
  elif echo "$RAW_BYTES" | grep -q "^feff"; then
    ENC="UTF-16BE"
  else
    ENC=$(python3 -c "
import sys; sys.stdout.reconfigure(encoding='ascii')
with open(sys.argv[1], 'rb') as f:
    raw = f.read(4096)
try:
    import chardet
    r = chardet.detect(raw)
    enc = r['encoding'] or 'unknown'
except ImportError:
    enc = 'unknown'
if enc.upper() in ('UTF-8', 'UTF-8-SIG', 'ASCII'): enc = 'utf-8'
print(enc)
" "$INPUT" 2>/dev/null)
  fi
  if [ -n "$ENC" ] && [ "$ENC" != "utf-8" ] && [ "$ENC" != "unknown" ] && [ "$ENC" != "None" ]; then
    CONVERTED_INPUT=$(mktemp)
    iconv -f "$ENC" -t UTF-8 "$INPUT" > "$CONVERTED_INPUT" 2>/dev/null || cp "$INPUT" "$CONVERTED_INPUT"
    INPUT="$CONVERTED_INPUT"
  fi
fi

PANDOC_ARGS=()
[ -n "$TITLE" ] && PANDOC_ARGS+=(--metadata "title=$TITLE")
[ -n "$AUTHOR" ] && PANDOC_ARGS+=(--metadata "author=$AUTHOR")

CSS_OPTS=()
if [ -n "$CSS_FILE" ] && [ -f "$CSS_FILE" ]; then
  CSS_OPTS+=(--css="$CSS_FILE")
elif [ -z "$CSS_FILE" ]; then
  TEMP_CSS=$(mktemp)
  cat > "$TEMP_CSS" << 'CSSCONTENT'
body {
  font-family: "Noto Serif CJK SC", "Source Han Serif CN", serif;
  line-height: 1.8;
  margin: 0;
  padding: 0 1em;
  word-wrap: break-word;
}
h1, h2, h3, h4 {
  font-family: "Noto Sans CJK SC", "Source Han Sans CN", sans-serif;
  line-height: 1.3;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}
h1 { font-size: 1.6em; text-align: center; }
h2 { font-size: 1.3em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
h3 { font-size: 1.1em; }
p { text-indent: 2em; margin: 0.5em 0; }
blockquote {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 3px solid #888;
  color: #555;
  background: #f9f9f9;
}
code {
  font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
  font-size: 0.9em;
  background: #f0f0f0;
  padding: 0.1em 0.3em;
  border-radius: 3px;
}
pre {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1em;
  overflow-x: auto;
  line-height: 1.4;
}
pre code { background: none; padding: 0; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
a { color: #2563eb; text-decoration: none; }
a:hover { text-decoration: underline; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 0.5em; }
th { background: #f5f5f5; }
CSSCONTENT
  CSS_OPTS+=(--css="$TEMP_CSS")
fi

pandoc "$INPUT" -o "$OUTPUT" --toc --metadata lang=zh-CN \
  "${PANDOC_ARGS[@]}" "${CSS_OPTS[@]}" 2>/dev/null

echo "EPUB generated: $OUTPUT"
