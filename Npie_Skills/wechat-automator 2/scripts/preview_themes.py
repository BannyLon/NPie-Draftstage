#!/usr/bin/env python3
"""
阶段④ 主题预览生成器 (v1.4.0)
Layout × Palette 双层架构：展示 5 套预设组合，布局和配色可独立辨识

用法:
  python3 scripts/preview_themes.py output/article-class-html.html [--open]
"""
import sys, os, re, webbrowser

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_ROOT)

from scripts.build_inline import (
    LAYOUTS, PALETTES, PRESETS, build_styles, build_nested_overrides,
    InlineStyleConverter, recommend,
)


def extract_sample(html, max_chars=800):
    """从 class-based HTML 中提取代表性片段"""
    inner = html
    m = re.search(r'<section[^>]*>(.*)</section>', html, re.DOTALL)
    if m:
        inner = m.group(1)
    h2_match = re.search(r'<h2[^>]*>', inner)
    if h2_match:
        next_h2 = re.search(r'<h2[^>]*>', inner[h2_match.end():])
        if next_h2:
            end = h2_match.end() + next_h2.start()
        else:
            end = min(len(inner), h2_match.start() + max_chars * 2)
    else:
        end = min(len(inner), max_chars)
    sample = inner[:end].strip()
    if len(sample) > max_chars:
        last_close = sample.rfind('>')
        if last_close > max_chars // 2:
            sample = sample[:last_close + 1]
    return sample


def render_sample(sample_html, preset_key):
    """用指定预设渲染样本，返回 inline HTML"""
    preset = PRESETS[preset_key]
    layout = preset["layout"]
    palette = PALETTES[preset["palette"]]
    styles = build_styles(layout, palette)
    nested = build_nested_overrides(layout, palette)
    wrapped = f'<section style="margin:0;padding:0 16px 0;background-color:#ffffff;">{sample_html}</section>'
    converter = InlineStyleConverter(styles, nested)
    converter.feed(wrapped)
    result = converter.get_result()
    # 清理 letter-spacing
    result = re.sub(r'letter-spacing:[^;"]*;?', '', result)
    return result


def generate_preview_page(sample_html, ranked, article_title=""):
    renders = {}
    for key in PRESETS:
        renders[key] = render_sample(sample_html, key)

    recommended_keys = {ranked[0][0], ranked[1][0]} if len(ranked) >= 2 else {ranked[0][0]}

    cards_html = ""
    for key, preset in PRESETS.items():
        layout = LAYOUTS[preset["layout"]]
        palette = PALETTES[preset["palette"]]
        is_rec = key in recommended_keys
        badge = '<span class="badge">⭐ 推荐</span>' if is_rec else ""

        # 双色 swatch 展示 primary + contrast
        swatch_html = f'''
            <div class="dual-swatch">
                <span class="swatch-p" style="background-color:{palette['primary']};"></span>
                <span class="swatch-c" style="background-color:{palette['contrast']};"></span>
            </div>'''

        cards_html += f'''
        <div class="theme-card{' recommended' if is_rec else ''}">
            <div class="card-header">
                {swatch_html}
                <div class="card-meta">
                    <span class="theme-name">{preset['name']}</span>
                    {badge}
                </div>
                <div class="theme-spec">
                    <span class="spec-layout">📐 {layout['name']}</span>
                    <span class="spec-palette">🎨 {palette['name']}</span>
                </div>
                <div class="theme-desc">{layout['desc']} · {palette['desc']}</div>
                <div class="theme-colors">
                    <span class="color-chip" style="background-color:{palette['primary']};" title="主色 {palette['primary']}"></span>
                    <span class="color-chip" style="background-color:{palette['contrast']};" title="对比色 {palette['contrast']}"></span>
                </div>
            </div>
            <div class="card-preview">{renders[key]}</div>
        </div>'''

    # 图例
    legend_items = ""
    for key, preset, score in ranked:
        palette = PALETTES[preset["palette"]]
        layout = LAYOUTS[preset["layout"]]
        bar_w = min(score * 8, 120)
        legend_items += f'''
        <div class="legend-item">
            <span class="legend-swatch" style="background-color:{palette['primary']};"></span>
            <span class="legend-name">{preset['name']}</span>
            <span class="legend-detail">({layout['name']} × {palette['name']})</span>
            <span class="legend-bar"><span style="display:inline-block;width:{bar_w}px;height:8px;background-color:{palette['primary']};border-radius:4px;"></span></span>
            <span class="legend-score">{score} 分</span>
        </div>'''

    title_display = article_title or "文章预览"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>排版风格预览 — {title_display}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: -apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
    background: #1a1d23; color: #e0e0e0; padding: 32px 24px 64px;
  }}
  .page-header {{ max-width: 1400px; margin: 0 auto 40px; text-align: center; }}
  .page-header h1 {{ font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 8px; }}
  .page-header .subtitle {{ font-size: 14px; color: #8a8f9a; }}

  .legend {{ max-width: 900px; margin: 0 auto 40px; padding: 20px 28px; background: #252830; border-radius: 12px; }}
  .legend-title {{ font-size: 13px; font-weight: 700; color: #8a8f9a; margin-bottom: 14px; }}
  .legend-item {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px; }}
  .legend-swatch {{ width: 14px; height: 14px; border-radius: 4px; flex-shrink: 0; }}
  .legend-name {{ width: 90px; flex-shrink: 0; color: #ccc; font-weight: 600; }}
  .legend-detail {{ width: 170px; flex-shrink: 0; color: #6a6f7a; font-size: 12px; }}
  .legend-bar {{ flex-shrink: 0; }}
  .legend-score {{ color: #8a8f9a; font-weight: 600; }}

  .theme-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 24px; max-width: 1400px; margin: 0 auto; }}
  .theme-card {{ background: #252830; border-radius: 14px; overflow: hidden; border: 2px solid #333840; transition: border-color .2s; }}
  .theme-card.recommended {{ border-color: #f0b90b; box-shadow: 0 0 24px rgba(240,185,11,.12); }}
  .card-header {{ padding: 18px 20px 14px; border-bottom: 1px solid #333840; }}
  .dual-swatch {{ display: inline-block; vertical-align: middle; margin-right: 10px; }}
  .swatch-p {{ display: inline-block; width: 24px; height: 24px; border-radius: 6px 0 0 6px; }}
  .swatch-c {{ display: inline-block; width: 24px; height: 24px; border-radius: 0 6px 6px 0; }}
  .card-meta {{ display: inline-block; vertical-align: middle; }}
  .theme-name {{ font-size: 16px; font-weight: 700; color: #fff; }}
  .badge {{ display: inline-block; margin-left: 8px; padding: 2px 8px; background: #f0b90b; color: #1a1d23; font-size: 11px; font-weight: 700; border-radius: 4px; vertical-align: middle; }}
  .theme-spec {{ margin-top: 8px; display: flex; gap: 14px; }}
  .spec-layout, .spec-palette {{ font-size: 12px; color: #8a8f9a; }}
  .theme-desc {{ margin-top: 4px; font-size: 13px; color: #6a6f7a; }}
  .theme-colors {{ margin-top: 8px; }}
  .color-chip {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 4px; }}
  .card-preview {{ padding: 0; max-height: 480px; overflow-y: auto; -webkit-overflow-scrolling: touch; }}
  .card-preview section {{ margin: 0 !important; }}

  .action-bar {{ max-width: 1400px; margin: 40px auto 0; text-align: center; padding: 24px; background: #252830; border-radius: 12px; }}
  .action-bar p {{ font-size: 14px; color: #8a8f9a; line-height: 1.8; }}
  .action-bar code {{ background: #333840; color: #f0b90b; padding: 2px 8px; border-radius: 4px; font-size: 13px; }}
  .action-bar .mix-note {{ font-size: 12px; color: #555a63; margin-top: 10px; }}

  @media (max-width: 420px) {{
    body {{ padding: 16px 8px 32px; }}
    .theme-grid {{ grid-template-columns: 1fr; gap: 16px; }}
    .legend-detail {{ display: none; }}
  }}
</style>
</head>
<body>

<div class="page-header">
  <h1>🎨 排版风格预览</h1>
  <p class="subtitle">{title_display}</p>
</div>

<div class="legend">
  <div class="legend-title">📊 内容匹配度（布局 × 配色）</div>
  {legend_items}
</div>

<div class="theme-grid">{cards_html}</div>

<div class="action-bar">
  <p>👆 每张卡片 = 一套 <strong>布局</strong>（📐 决定结构） × <strong>配色</strong>（🎨 决定颜色）</p>
  <p>选定后回复预设名：<code>teal</code> <code>navy</code> <code>forest</code> <code>plum</code> <code>slate</code></p>
  <p>或自由组合：<code>classic:teal-gold</code> <code>bold:navy-coral</code> <code>minimal:slate-rose</code></p>
  <p>或自定义颜色：<code>#e63946</code>（默认 classic 布局）</p>
  <p class="mix-note">可用布局: classic / magazine / minimal / bold / elegant &nbsp;|&nbsp; 可用配色: teal-gold / navy-coral / forest-amber / plum-sage / slate-rose</p>
</div>

</body>
</html>'''


def main():
    args = sys.argv[1:]
    input_file = "output/article-class-html.html"
    do_open = False
    for a in args:
        if a == "--open": do_open = True
        elif not a.startswith("--"): input_file = a

    html_path = os.path.join(SKILL_ROOT, input_file) if not os.path.isabs(input_file) else input_file
    if not os.path.exists(html_path):
        print(f"❌ 文件不存在: {html_path}"); sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        full_html = f.read()

    text = re.sub(r'<[^>]+>', '', full_html)
    text = re.sub(r'\s+', ' ', text)

    title = ""
    m = re.search(r'class="meta-desc"[^>]*>([^<]+)', full_html)
    if m: title = m.group(1).strip()

    ranked = recommend(text)
    print("📊 内容匹配分析:")
    for key, preset, score in ranked:
        layout = LAYOUTS[preset["layout"]]
        palette = PALETTES[preset["palette"]]
        marker = " ⭐" if score == ranked[0][1] else ""
        print(f"   {preset['name']:8s} | 📐{layout['name']:6s} × 🎨{palette['name']:6s} | {score:2d} 分{marker}")

    sample = extract_sample(full_html)
    print(f"\n📝 提取样本: {len(sample)} 字符")

    preview_html = generate_preview_page(sample, ranked, title)
    out_path = os.path.join(SKILL_ROOT, "output", "theme-preview.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(preview_html)

    print(f"✅ 预览页已生成: {out_path}")
    print(f"   大小: {len(preview_html)} 字符")

    if do_open:
        webbrowser.open("file://" + out_path)
        print("🌐 已在浏览器中打开")


if __name__ == "__main__":
    main()
