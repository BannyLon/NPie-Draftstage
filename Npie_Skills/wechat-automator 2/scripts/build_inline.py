#!/usr/bin/env python3
"""
阶段④ 排版渲染：class-based HTML → inline style HTML
v1.5.0: 5套真正异构排版系统 — 每套有独立的组件库、HTML结构、视觉语言

Layouts: classic | cardflow | editorial | guide | letter
Palettes: teal-gold | navy-coral | forest-amber | plum-sage | slate-rose
Presets: teal/navy/forest/plum/slate (向后兼容)

铁律 2/3/4/5/7 贯穿始终。
"""
import sys, os, re
from html.parser import HTMLParser

# ══════════════════════════════════════════════════════════
# 配色方案 (5 套多对比色，16 token/套)
# ══════════════════════════════════════════════════════════

PALETTES = {
    "teal-gold":   {"name":"青蓝金","desc":"冷青蓝×暖琥珀金","primary":"#0d7377","contrast":"#c8940a","bg_light":"#e8f4f8","bg_warm":"#fef8f0","bg_dark":"#0a4d50","bg_dark_alt":"#3d2e00","text_on_dark":"#e8f4f8","text_dark":"#1a1a1a","text_body":"#3f3f3f","text_muted":"#8a9aaa","border":"#e0e7ef","border_light":"#dce3ea","card_bg":"#fafbfc","code_bg":"#f9f2f4","code_color":"#c7254e","white":"#ffffff","body_bg":"#f5f5f5","warn_bg":"#fff8f0","warn_border":"#e8a838","tip_bg":"#f0faf6","tip_border":"#4aaf87",},
    "navy-coral":  {"name":"深蓝珊瑚","desc":"深海蓝×暖珊瑚红","primary":"#2c3e6b","contrast":"#d4685c","bg_light":"#edf0f7","bg_warm":"#fdf5f4","bg_dark":"#1a2747","bg_dark_alt":"#5c1e19","text_on_dark":"#edf0f7","text_dark":"#1a1a1a","text_body":"#3f3f3f","text_muted":"#8a8f9a","border":"#dde1ed","border_light":"#d5dae5","card_bg":"#fafbfd","code_bg":"#fdf2f2","code_color":"#c0392b","white":"#ffffff","body_bg":"#f5f5f5","warn_bg":"#fff5f4","warn_border":"#e87060","tip_bg":"#f0f4fa","tip_border":"#5a7db8",},
    "forest-amber":{"name":"森语琥珀","desc":"深林绿×暖琥珀","primary":"#2d6a4f","contrast":"#d4923a","bg_light":"#e8f5ee","bg_warm":"#fef9f2","bg_dark":"#1a4230","bg_dark_alt":"#4a2d0a","text_on_dark":"#e8f5ee","text_dark":"#1a1a1a","text_body":"#3f3f3f","text_muted":"#8a9a90","border":"#d5e8dc","border_light":"#c8ddd0","card_bg":"#fafcfa","code_bg":"#f2f9f4","code_color":"#1e7a42","white":"#ffffff","body_bg":"#f5f5f5","warn_bg":"#fff9f0","warn_border":"#e0a040","tip_bg":"#f0f8f4","tip_border":"#5aaf80",},
    "plum-sage":   {"name":"梅紫灰绿","desc":"梅子紫×灰鼠尾草绿","primary":"#7c3a8c","contrast":"#6b8b7a","bg_light":"#f5edf8","bg_warm":"#f2f7f4","bg_dark":"#3d1a46","bg_dark_alt":"#2d4035","text_on_dark":"#f5edf8","text_dark":"#1a1a1a","text_body":"#3f3f3f","text_muted":"#9a8f9e","border":"#e5dded","border_light":"#dcd0e5","card_bg":"#faf9fb","code_bg":"#f8f2f9","code_color":"#8b3a7c","white":"#ffffff","body_bg":"#f5f5f5","warn_bg":"#faf2f8","warn_border":"#b060a0","tip_bg":"#f2f8f4","tip_border":"#78a888",},
    "slate-rose":  {"name":"岩灰玫瑰","desc":"都市岩灰×干枯玫瑰","primary":"#4a5568","contrast":"#c57080","bg_light":"#f0f2f5","bg_warm":"#fdf6f7","bg_dark":"#2d3545","bg_dark_alt":"#5c3038","text_on_dark":"#f0f2f5","text_dark":"#1a1a1a","text_body":"#3f3f3f","text_muted":"#8a8f98","border":"#e2e5ea","border_light":"#d5d9df","card_bg":"#fafbfc","code_bg":"#fdf5f6","code_color":"#b85060","white":"#ffffff","body_bg":"#f5f5f5","warn_bg":"#fdf6f6","warn_border":"#d08890","tip_bg":"#f2f4f6","tip_border":"#8090a0",},
}

# ══════════════════════════════════════════════════════════
# 5 套异构排版系统
# ══════════════════════════════════════════════════════════

def _common_styles(p, lname):
    """所有布局共享的基础样式"""
    return {
        "#article-wrapper": f"margin:0;padding:0 16px 0;background-color:{p['white']};",
        "body": f"background-color:{p['body_bg']};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei','Helvetica Neue',sans-serif;color:{p['text_body']};-webkit-font-smoothing:antialiased;margin:0;padding:0;",
        ".header-image": "display:block;width:100%;max-width:100%;margin:0 0 28px;border-radius:0;",
        "p": f"margin:0 0 16px;font-size:15px;line-height:1.9;color:{p['text_body']};text-align:justify;",
        "strong": f"color:{p['text_dark']};font-weight:700;",
        "b": f"color:{p['text_dark']};font-weight:700;",
        "code": f"padding:2px 6px;font-family:'SF Mono','Menlo','Monaco','Courier New',monospace;font-size:13px;color:{p['code_color']};background-color:{p['code_bg']};border-radius:3px;",
        "pre": "margin:18px 0;padding:18px 20px;background-color:#282c34;color:#abb2bf;border-radius:8px;overflow-x:auto;font-size:13px;line-height:1.8;",
        ".code-block": "white-space:pre-wrap;font-family:'SF Mono','Menlo','Monaco','Courier New',monospace;margin:16px 0;padding:18px 20px;border-radius:8px;font-size:13px;line-height:1.7;",
        ".code-block-dark": "white-space:pre-wrap;font-family:monospace;margin:16px 0;padding:18px 20px;border-radius:8px;font-size:13px;line-height:1.7;background-color:#282c34;color:#abb2bf;",
        ".code-block-scroll": "white-space:pre-wrap;font-family:monospace;margin:16px 0;padding:18px 20px;border-radius:8px;font-size:13px;line-height:1.7;max-height:520px;overflow-y:auto;-webkit-overflow-scrolling:touch;",
        ".editor-note": f"margin:14px 0;padding:8px 14px;font-size:13px;color:{p['text_muted']};font-style:italic;border-left:2px solid {p['border_light']};",
        "table": "width:100%;margin:20px 0;border-collapse:collapse;font-size:13px;line-height:1.7;",
        "td": f"padding:12px 14px;border:1px solid {p['border']};color:{p['text_body']};",
        ".footer-spacer": "margin:0;padding:0;height:0;",
        ".illustration": "margin:28px 0;text-align:center;",
        ".illustration img": "display:block;width:100%;max-width:100%;border-radius:6px;",
    }

# ── 1. CLASSIC 经典左线 ──
def _classic(p):
    s = {}
    s[".article-meta"] = f"margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid {p['border']};text-align:center;"
    s[".meta-tag"] = f"display:inline-block;padding:4px 14px;font-size:12px;font-weight:600;color:{p['primary']};background-color:{p['bg_light']};border-radius:20px;margin-bottom:14px;"
    s[".meta-desc"] = f"font-size:14px;color:{p['text_muted']};line-height:1.8;"
    s[".hero-block"] = "margin:0 0 36px;text-align:center;"
    s[".hero-number"] = f"font-size:56px;font-weight:900;color:{p['primary']};line-height:1;margin-bottom:4px;"
    s[".hero-label"] = f"font-size:13px;color:{p['text_muted']};"
    s["h2"] = f"margin:44px 0 22px;padding:14px 18px;font-size:19px;font-weight:700;line-height:1.5;color:{p['text_dark']};background-color:{p['bg_light']};border-left:4px solid {p['primary']};border-radius:0 6px 6px 0;"
    s["h3"] = f"margin:34px 0 16px;padding:0 0 12px;font-size:17px;font-weight:700;color:{p['primary']};border-bottom:2px solid {p['border']};line-height:1.5;"
    s["blockquote"] = f"margin:20px 0;padding:18px 20px 18px 22px;background-color:{p['card_bg']};border-left:3px solid {p['primary']};border-radius:0 8px 8px 0;color:{p['text_muted']};font-size:14px;line-height:1.8;"
    s[".golden-quote"] = f"margin:30px 0;padding:26px 28px;background-color:{p['bg_light']};border-radius:12px;text-align:center;font-size:17px;font-weight:700;line-height:1.9;color:{p['primary']};"
    s[".highlight-box"] = f"margin:24px 0;padding:20px 22px;background-color:{p['bg_warm']};border-radius:10px;border:1px solid {p['border']};font-size:15px;line-height:1.9;color:{p['primary']};"
    s[".card-item"] = f"margin-bottom:10px;padding:15px 18px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:8px;font-size:14px;line-height:1.8;color:{p['text_body']};"
    s[".cta-footer"] = f"margin-top:44px;margin-bottom:0;padding:28px 24px;background-color:{p['bg_light']};border-radius:14px;text-align:center;"
    s[".cta-title"] = f"font-size:17px;font-weight:700;color:{p['primary']};margin-bottom:8px;"
    s["th"] = f"padding:12px 14px;background-color:{p['bg_light']};color:{p['text_dark']};font-weight:700;text-align:left;border:1px solid {p['border_light']};"
    s["hr"] = f"margin:36px 0;border:none;height:1px;background-color:{p['border_light']};"
    s[".data-num"] = f"font-size:28px;font-weight:900;color:{p['primary']};line-height:1.2;"
    s[".data-row"] = "width:100%;margin:20px 0;"
    s[".data-col"] = f"display:inline-block;width:47%;vertical-align:top;text-align:center;padding:18px 12px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:10px;margin-right:3%;"
    s[".data-label"] = f"font-size:12px;color:{p['text_muted']};margin-top:6px;"
    return s

# ── 2. CARDFLOW 卡片流 ──
def _cardflow(p):
    s = {}
    s[".article-meta"] = f"margin-bottom:32px;text-align:center;"
    s[".meta-tag"] = f"display:inline-block;padding:5px 18px;font-size:11px;font-weight:700;color:{p['white']};background-color:{p['primary']};border-radius:3px;margin-bottom:10px;"
    s[".meta-desc"] = f"font-size:14px;color:{p['text_muted']};line-height:1.8;"
    s["h2"] = f"margin:0;padding:14px 20px;font-size:17px;font-weight:700;line-height:1.4;color:{p['white']};background-color:{p['primary']};border-radius:10px 10px 0 0;"
    s["h3"] = f"margin:24px 0 10px;padding:0;font-size:15px;font-weight:700;color:{p['text_dark']};line-height:1.6;border:none;"
    # 卡片容器：包裹 H2 + 内容
    s[".section-card"] = f"margin:0 0 28px;padding:0;background-color:{p['white']};border:1px solid {p['border']};border-radius:10px;overflow:hidden;"
    s[".section-card-body"] = f"padding:4px 20px 18px;"
    # info-card：独立信息卡片
    s[".info-card"] = f"margin:0 0 12px;padding:14px 16px;background-color:{p['card_bg']};border-left:4px solid {p['contrast']};border-radius:0 6px 6px 0;font-size:14px;line-height:1.8;color:{p['text_body']};"
    s[".info-card strong"] = f"color:{p['primary']};font-weight:700;"
    # 数据徽章
    s[".data-badge"] = f"display:inline-block;margin:4px 6px 4px 0;padding:6px 14px;background-color:{p['bg_light']};color:{p['primary']};font-size:13px;font-weight:700;border-radius:20px;"
    s["blockquote"] = f"margin:16px 0;padding:14px 18px;background-color:{p['bg_warm']};border:none;border-radius:8px;color:{p['text_body']};font-size:14px;line-height:1.8;"
    s[".golden-quote"] = f"margin:0 0 20px;padding:20px 24px;background-color:{p['bg_light']};border-radius:0 0 10px 10px;text-align:center;font-size:16px;font-weight:700;line-height:1.8;color:{p['primary']};"
    s[".highlight-box"] = f"margin:16px 0;padding:16px 20px;background-color:{p['bg_warm']};border-radius:8px;font-size:14px;line-height:1.8;color:{p['text_dark']};border-left:3px solid {p['contrast']};"
    s[".card-item"] = f"margin-bottom:8px;padding:12px 16px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:6px;font-size:14px;line-height:1.7;color:{p['text_body']};"
    s[".cta-footer"] = f"margin-top:44px;margin-bottom:0;padding:24px 20px;background-color:{p['primary']};border-radius:10px;text-align:center;"
    s[".cta-title"] = f"font-size:16px;font-weight:700;color:{p['white']};margin-bottom:6px;"
    s["th"] = f"padding:12px 14px;background-color:{p['primary']};color:{p['white']};font-weight:700;text-align:left;border:none;"
    s["hr"] = f"margin:32px 0;border:none;height:1px;background-color:{p['border_light']};"
    s[".data-num"] = f"font-size:30px;font-weight:900;color:{p['contrast']};line-height:1.1;"
    s[".data-row"] = "width:100%;margin:20px 0;"
    s[".data-col"] = f"display:inline-block;width:47%;vertical-align:top;text-align:center;padding:16px 10px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:8px;margin-right:3%;"
    s[".data-label"] = f"font-size:12px;color:{p['text_muted']};margin-top:6px;"
    return s

# ── 3. EDITORIAL 杂志流 ──
def _editorial(p):
    s = {}
    s[".article-meta"] = f"margin-bottom:32px;text-align:center;"
    s[".meta-tag"] = f"display:inline-block;padding:2px 0;font-size:11px;font-weight:600;color:{p['text_muted']};border-bottom:2px solid {p['primary']};margin-bottom:10px;"
    s[".meta-desc"] = f"font-size:15px;color:{p['text_muted']};line-height:1.8;font-style:italic;"
    # 引题段落
    s[".lead"] = f"margin:0 0 24px;font-size:17px;line-height:2.0;color:{p['text_muted']};text-align:center;font-weight:400;"
    s["h2"] = f"margin:56px 0 20px;padding:20px 0;text-align:center;font-size:20px;font-weight:800;line-height:1.4;color:{p['text_dark']};border-top:3px solid {p['primary']};border-bottom:1px solid {p['border_light']};background-color:transparent;"
    s["h3"] = f"margin:36px 0 14px;padding:0;font-size:16px;font-weight:700;color:{p['text_dark']};line-height:1.6;border:none;"
    # 装饰分隔线
    s[".ornament-divider"] = f"margin:40px auto;border:none;height:3px;background-color:{p['primary']};width:60px;"
    # 引用（戏剧化居中）
    s["blockquote"] = f"margin:36px 0;padding:18px 20px;text-align:center;font-size:20px;font-weight:600;line-height:1.9;color:{p['primary']};background-color:transparent;border:none;"
    s[".golden-quote"] = f"margin:40px 0;padding:32px 28px;background-color:{p['bg_light']};text-align:center;font-size:18px;font-weight:700;line-height:2.0;color:{p['primary']};border-top:2px solid {p['contrast']};border-bottom:2px solid {p['contrast']};"
    s[".highlight-box"] = f"margin:24px 0;padding:20px 24px;background-color:{p['bg_warm']};font-size:15px;line-height:2.0;color:{p['text_dark']};border-left:4px solid {p['contrast']};"
    s[".card-item"] = f"margin-bottom:14px;padding:18px 22px;background-color:{p['white']};border-top:3px solid {p['primary']};border-bottom:1px solid {p['border']};font-size:14px;line-height:1.8;color:{p['text_body']};"
    # 署名式 CTA
    s[".cta-footer"] = f"margin-top:52px;margin-bottom:0;padding:0;text-align:center;background-color:transparent;border:none;"
    s[".cta-title"] = f"font-size:15px;font-weight:600;color:{p['text_muted']};margin-bottom:6px;font-style:italic;"
    s["th"] = f"padding:14px 16px;background-color:{p['primary']};color:{p['white']};font-weight:700;text-align:left;border:none;"
    s["hr"] = f"margin:40px auto;border:none;height:3px;background-color:{p['primary']};width:60px;"
    s[".data-num"] = f"font-size:34px;font-weight:900;color:{p['primary']};line-height:1.1;"
    s[".data-row"] = "width:100%;margin:20px 0;"
    s[".data-col"] = f"display:inline-block;width:47%;vertical-align:top;text-align:center;padding:18px 12px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:10px;margin-right:3%;"
    s[".data-label"] = f"font-size:12px;color:{p['text_muted']};margin-top:6px;"
    # 图片框
    s[".image-frame"] = f"margin:28px 0;padding:0;border:1px solid {p['border']};border-radius:4px;overflow:hidden;"
    s[".image-caption"] = f"margin:4px 0 20px;font-size:12px;color:{p['text_muted']};text-align:center;font-style:italic;"
    return s

# ── 4. GUIDE 手册流 ──
def _guide(p):
    s = {}
    s[".article-meta"] = f"margin-bottom:28px;text-align:left;padding-bottom:20px;border-bottom:2px solid {p['primary']};"
    s[".meta-tag"] = f"display:inline-block;padding:3px 12px;font-size:11px;font-weight:700;color:{p['white']};background-color:{p['primary']};border-radius:3px;margin-bottom:10px;"
    s[".meta-desc"] = f"font-size:14px;color:{p['text_muted']};line-height:1.8;"
    s["h2"] = f"margin:44px 0 20px;padding:0;font-size:22px;font-weight:800;line-height:1.3;color:{p['text_dark']};background-color:transparent;border:none;"
    s["h3"] = f"margin:32px 0 14px;padding:0;font-size:17px;font-weight:700;color:{p['primary']};line-height:1.5;border:none;"
    # 步骤块
    s[".step-block"] = f"margin:0 0 24px;padding:0;"
    s[".step-num"] = f"display:inline-block;width:32px;height:32px;line-height:32px;text-align:center;font-size:16px;font-weight:800;color:{p['white']};background-color:{p['primary']};border-radius:50%;margin-bottom:8px;"
    s[".step-title"] = f"display:inline;margin-left:8px;font-size:17px;font-weight:700;color:{p['text_dark']};vertical-align:middle;"
    s[".step-body"] = f"margin:8px 0 0 40px;font-size:15px;line-height:1.9;color:{p['text_body']};"
    # 提示框 - 两种
    s[".tip-box"] = f"margin:18px 0;padding:14px 18px;background-color:{p['tip_bg']};border-left:4px solid {p['tip_border']};border-radius:0 6px 6px 0;font-size:14px;line-height:1.8;color:{p['text_body']};"
    s[".tip-box strong"] = f"color:{p['primary']};font-weight:700;"
    s[".warn-box"] = f"margin:18px 0;padding:14px 18px;background-color:{p['warn_bg']};border-left:4px solid {p['warn_border']};border-radius:0 6px 6px 0;font-size:14px;line-height:1.8;color:{p['text_body']};"
    s[".warn-box strong"] = f"color:{p['contrast']};font-weight:700;"
    # 清单项
    s[".checklist-item"] = f"margin-bottom:8px;padding:10px 14px;font-size:14px;line-height:1.7;color:{p['text_body']};background-color:{p['card_bg']};border-radius:6px;"
    # 前后对比
    s[".before-after"] = "width:100%;margin:20px 0;"
    s[".ba-col"] = f"display:inline-block;width:47%;vertical-align:top;padding:14px;margin-right:3%;background-color:{p['card_bg']};border-radius:8px;"
    s[".ba-label"] = f"font-size:12px;font-weight:700;color:{p['text_muted']};margin-bottom:6px;"
    s[".ba-text"] = f"font-size:14px;line-height:1.8;color:{p['text_body']};"
    # 引用
    s["blockquote"] = f"margin:16px 0;padding:12px 16px;background-color:{p['bg_warm']};border:none;border-radius:6px;color:{p['text_body']};font-size:14px;line-height:1.7;"
    s[".golden-quote"] = f"margin:28px 0;padding:22px 24px;background-color:{p['bg_dark']};border-radius:8px;text-align:center;font-size:16px;font-weight:700;line-height:1.8;color:{p['text_on_dark']};"
    s[".highlight-box"] = f"margin:20px 0;padding:16px 20px;background-color:{p['bg_warm']};border-radius:8px;font-size:14px;line-height:1.8;color:{p['text_dark']};"
    s[".card-item"] = f"margin-bottom:8px;padding:12px 16px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:6px;font-size:14px;line-height:1.7;color:{p['text_body']};"
    s[".cta-footer"] = f"margin-top:44px;margin-bottom:0;padding:24px 20px;background-color:{p['bg_light']};border-radius:10px;text-align:center;"
    s[".cta-title"] = f"font-size:16px;font-weight:700;color:{p['primary']};margin-bottom:6px;"
    s["th"] = f"padding:10px 14px;background-color:{p['bg_dark']};color:{p['text_on_dark']};font-weight:700;text-align:left;border:none;"
    s["hr"] = f"margin:32px 0;border:none;height:2px;background-color:{p['primary']};"
    s[".data-num"] = f"font-size:32px;font-weight:900;color:{p['primary']};line-height:1.1;"
    s[".data-row"] = "width:100%;margin:20px 0;"
    s[".data-col"] = f"display:inline-block;width:47%;vertical-align:top;text-align:center;padding:18px 12px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:10px;margin-right:3%;"
    s[".data-label"] = f"font-size:12px;color:{p['text_muted']};margin-top:6px;"
    return s

# ── 5. LETTER 书信流 ──
def _letter(p):
    s = {}
    # 无 meta-tag/meta-desc，走书信格式
    s[".dateline"] = f"margin:0 0 28px;font-size:13px;color:{p['text_muted']};text-align:right;"
    s[".greeting"] = f"margin:0 0 24px;font-size:16px;color:{p['text_dark']};font-weight:500;line-height:1.8;"
    s[".letter-body"] = f"margin:0 0 16px;font-size:15px;line-height:2.0;color:{p['text_body']};text-align:justify;"
    # H2 在书信中极克制，只比正文略大
    s["h2"] = f"margin:40px 0 14px;padding:0;font-size:18px;font-weight:700;line-height:1.6;color:{p['text_dark']};background-color:transparent;border:none;"
    s["h3"] = f"margin:28px 0 10px;padding:0;font-size:15px;font-weight:600;color:{p['text_muted']};line-height:1.6;border:none;font-style:italic;"
    # 轻引用
    s["blockquote"] = f"margin:18px 0;padding:0 0 0 16px;font-size:14px;line-height:1.8;color:{p['text_muted']};background-color:transparent;border:none;border-left:2px solid {p['border_light']};font-style:italic;"
    # 书信中"金句"就是加大加粗的一段话，无底无边框
    s[".golden-quote"] = f"margin:28px 0;padding:0;text-align:center;font-size:18px;font-weight:600;line-height:2.0;color:{p['primary']};background-color:transparent;border:none;"
    s[".highlight-box"] = f"margin:20px 0;padding:0 0 0 14px;font-size:14px;line-height:1.9;color:{p['text_dark']};background-color:transparent;border:none;border-left:2px solid {p['contrast']};"
    s[".card-item"] = f"margin-bottom:12px;padding:0 0 10px;font-size:14px;line-height:1.8;color:{p['text_body']};background-color:transparent;border:none;border-bottom:1px solid {p['border_light']};"
    # 署名区
    s[".sign-off"] = f"margin:36px 0 12px;font-size:15px;color:{p['text_muted']};text-align:right;font-style:italic;"
    s[".signature"] = f"margin:0 0 8px;font-size:16px;font-weight:600;color:{p['text_dark']};text-align:right;"
    s[".postscript"] = f"margin:24px 0 0;padding:14px 0 0;font-size:13px;color:{p['text_muted']};line-height:1.8;border-top:1px solid {p['border_light']};font-style:italic;"
    # CTA 极克制
    s[".cta-footer"] = f"margin-top:48px;margin-bottom:0;padding:20px 0 0;text-align:center;background-color:transparent;border:none;border-top:1px solid {p['border_light']};"
    s[".cta-title"] = f"font-size:14px;font-weight:500;color:{p['primary']};margin-bottom:6px;"
    # 元信息简化
    s[".article-meta"] = f"margin-bottom:24px;text-align:right;"
    s[".meta-tag"] = f"font-size:11px;color:{p['text_muted']};font-style:italic;background:none;border:none;padding:0;display:inline;"
    s[".meta-desc"] = f"font-size:13px;color:{p['text_muted']};line-height:1.6;display:none;"
    s["th"] = f"padding:10px 12px;font-weight:600;color:{p['text_dark']};text-align:left;border:none;border-bottom:1px solid {p['border_light']};background-color:transparent;"
    s["hr"] = f"margin:32px auto;border:none;height:1px;background-color:{p['border_light']};width:40%;"
    s[".data-num"] = f"font-size:24px;font-weight:700;color:{p['text_dark']};line-height:1.2;"
    s[".data-row"] = "width:100%;margin:16px 0;"
    s[".data-col"] = f"display:inline-block;width:47%;vertical-align:top;text-align:center;padding:14px 10px;margin-right:3%;"
    s[".data-label"] = f"font-size:11px;color:{p['text_muted']};margin-top:4px;"
    return s

# ── 6. WORKSHOP 极客流 ──
def _workshop(p):
    s = {}
    s[".article-meta"] = f"margin-bottom:28px;padding-bottom:20px;border-bottom:2px solid {p['primary']};text-align:left;"
    s[".meta-tag"] = f"display:inline-block;padding:3px 10px;font-size:11px;font-weight:700;color:{p['white']};background-color:{p['primary']};border-radius:3px;margin-bottom:8px;"
    s[".meta-desc"] = f"font-size:14px;color:{p['text_muted']};line-height:1.8;"
    # H2: 实验笔记风格 — 深底+等宽感
    s["h2"] = f"margin:44px 0 20px;padding:12px 18px;font-size:18px;font-weight:700;line-height:1.4;color:{p['text_on_dark']};background-color:{p['bg_dark']};border:none;border-radius:4px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
    s["h3"] = f"margin:32px 0 12px;padding:0 0 0 12px;font-size:16px;font-weight:700;color:{p['text_dark']};line-height:1.5;border:none;border-left:3px solid {p['primary']};"
    # 引用块：终端风格
    s["blockquote"] = f"margin:18px 0;padding:16px 20px;background-color:{p['bg_dark']};color:{p['text_on_dark']};font-size:14px;line-height:1.8;border:none;border-radius:6px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
    # Prompt 模板卡
    s[".prompt-card"] = f"margin:20px 0;padding:0;background-color:{p['white']};border:2px solid {p['primary']};border-radius:8px;overflow:hidden;"
    s[".prompt-card-header"] = f"margin:0;padding:10px 16px;font-size:12px;font-weight:700;color:{p['white']};background-color:{p['primary']};"
    s[".prompt-card-body"] = f"margin:0;padding:16px 18px;font-size:14px;line-height:1.8;color:{p['text_body']};white-space:pre-wrap;font-family:'SF Mono','Menlo','Monaco','Courier New',monospace;"
    # 工具徽章
    s[".tool-badge"] = f"display:inline-block;margin:2px 4px 2px 0;padding:3px 10px;font-size:12px;font-weight:600;color:{p['primary']};background-color:{p['bg_light']};border:1px solid {p['primary']};border-radius:4px;"
    # 工作流步骤
    s[".workflow-step"] = f"margin:0 0 20px;padding:0 0 0 24px;border-left:2px dashed {p['border']};position:relative;"
    s[".wf-step-num"] = f"display:inline-block;width:24px;height:24px;line-height:24px;text-align:center;font-size:13px;font-weight:800;color:{p['white']};background-color:{p['primary']};border-radius:3px;margin-bottom:6px;"
    # 金句：实验结果风
    s[".golden-quote"] = f"margin:30px 0;padding:22px 24px;background-color:{p['bg_dark']};border-radius:6px;text-align:center;font-size:16px;font-weight:700;line-height:1.8;color:{p['contrast']};"
    s[".highlight-box"] = f"margin:20px 0;padding:16px 20px;background-color:{p['bg_warm']};border-radius:6px;font-size:14px;line-height:1.8;color:{p['text_dark']};border-left:3px solid {p['contrast']};"
    s[".card-item"] = f"margin-bottom:8px;padding:12px 16px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:4px;font-size:14px;line-height:1.7;color:{p['text_body']};"
    s[".card-item strong"] = f"color:{p['primary']};font-weight:700;"
    s[".tip-box"] = f"margin:18px 0;padding:14px 18px;background-color:{p['tip_bg']};border-left:4px solid {p['tip_border']};border-radius:0 6px 6px 0;font-size:14px;line-height:1.8;color:{p['text_body']};"
    s[".warn-box"] = f"margin:18px 0;padding:14px 18px;background-color:{p['warn_bg']};border-left:4px solid {p['warn_border']};border-radius:0 6px 6px 0;font-size:14px;line-height:1.8;color:{p['text_body']};"
    s[".cta-footer"] = f"margin-top:44px;margin-bottom:0;padding:24px 20px;background-color:{p['bg_dark']};border-radius:8px;text-align:center;"
    s[".cta-title"] = f"font-size:16px;font-weight:700;color:{p['text_on_dark']};margin-bottom:6px;"
    s["th"] = f"padding:12px 14px;background-color:{p['bg_dark']};color:{p['text_on_dark']};font-weight:700;text-align:left;border:none;"
    s["hr"] = f"margin:32px 0;border:none;height:2px;background-color:{p['primary']};"
    s[".data-num"] = f"font-size:30px;font-weight:900;color:{p['contrast']};line-height:1.1;"
    s[".data-row"] = "width:100%;margin:20px 0;"
    s[".data-col"] = f"display:inline-block;width:47%;vertical-align:top;text-align:center;padding:16px 10px;background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:8px;margin-right:3%;"
    s[".data-label"] = f"font-size:12px;color:{p['text_muted']};margin-top:6px;"
    return s


LAYOUTS = {
    "classic":   {"name":"经典左线","desc":"左粗线+浅底分区，结构清晰，通用百搭","fn":_classic},
    "cardflow":  {"name":"卡片流","desc":"每段内容独立成卡，模块化可扫描","fn":_cardflow},
    "editorial": {"name":"杂志流","desc":"大标题+装饰线+引题段落，编辑感","fn":_editorial},
    "guide":     {"name":"手册流","desc":"步骤编号+提示框+对比，操作教学","fn":_guide},
    "letter":    {"name":"书信流","desc":"日期+问候+署名，极简亲密对话感","fn":_letter},
    "workshop":  {"name":"极客流","desc":"深色实验台+Prompt卡+工具徽章，技术感","fn":_workshop},
}

PRESETS = {
    "teal":   {"layout":"classic","palette":"teal-gold","name":"青蓝经典"},
    "navy":   {"layout":"editorial","palette":"navy-coral","name":"深蓝杂志"},
    "forest": {"layout":"guide","palette":"forest-amber","name":"森语手册"},
    "plum":   {"layout":"cardflow","palette":"plum-sage","name":"梅紫卡片"},
    "slate":  {"layout":"letter","palette":"slate-rose","name":"岩灰书信"},
    "amber":  {"layout":"workshop","palette":"forest-amber","name":"暖金工坊"},
}


# ══════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════

def derive_palette(hex_color):
    r,g,b = int(hex_color[1:3],16),int(hex_color[3:5],16),int(hex_color[5:7],16)
    def mix(ratio):
        return f"#{int(r*ratio+255*(1-ratio)):02x}{int(g*ratio+255*(1-ratio)):02x}{int(b*ratio+255*(1-ratio)):02x}"
    def darken(ratio):
        return f"#{int(r*ratio):02x}{int(g*ratio):02x}{int(b*ratio):02x}"
    return {"name":f"自定义 {hex_color}","desc":f"从 {hex_color} 推导","primary":hex_color,"contrast":mix(0.35),"bg_light":mix(0.18),"bg_warm":mix(0.08),"bg_dark":darken(0.55),"bg_dark_alt":darken(0.35),"text_on_dark":mix(0.15),"text_dark":"#1a1a1a","text_body":"#3f3f3f","text_muted":"#8a9aaa","border":"#e0e7ef","border_light":"#dce3ea","card_bg":"#fafbfc","code_bg":"#f9f2f4","code_color":"#c7254e","white":"#ffffff","body_bg":"#f5f5f5","warn_bg":"#fff8f0","warn_border":"#e8a838","tip_bg":"#f0faf6","tip_border":"#4aaf87",}

def analyze_content(text):
    kw = {
        "navy":["商业","行业","市场","数据","报告","战略","投资","利润","竞争","企业","增长","收入"],
        "forest":["教程","步骤","操作","配置","代码","实战","指南","工具","方法","技巧","实现"],
        "teal":["分析","深度","观点","评论","趋势","解读","思考","本质","逻辑","复盘"],
        "plum":["产品","设计","体验","品牌","审美","创意","风格","质感","表达"],
        "slate":["我","经历","感受","故事","生活","日常","朋友","记录","随笔"],
        "amber":["Prompt","API","Agent","Workflow","模型","token","部署","自动化","编程","脚本","调试","开源","GitHub","命令行","参数"],
    }
    scores = {}
    for k, kws in kw.items():
        s = sum(len(re.findall(kw, text)) for kw in kws)
        fl = text.split('\n')[0] if text else ""
        s += sum(2 for kw in kws if kw in fl)
        scores[k] = s
    return scores

def recommend(text):
    scores = analyze_content(text)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(k, PRESETS[k], sc) for k, sc in ranked if k in PRESETS]

def resolve_theme(theme_arg):
    if theme_arg is None: theme_arg = "teal"
    if theme_arg in PRESETS:
        p = PRESETS[theme_arg]
        return p["layout"], PALETTES[p["palette"]]
    if ":" in theme_arg:
        parts = theme_arg.split(":",1)
        l, pn = parts[0].strip(), parts[1].strip()
        if l in LAYOUTS and pn in PALETTES:
            return l, PALETTES[pn]
    if re.match(r'^#[0-9a-fA-F]{6}$', theme_arg):
        return "classic", derive_palette(theme_arg)
    print(f"⚠️  未知 '{theme_arg}'，回退 teal")
    return "classic", PALETTES["teal-gold"]

def build_styles(layout_name, p):
    fn = LAYOUTS[layout_name]["fn"]
    styles = _common_styles(p, layout_name)
    styles.update(fn(p))
    return styles

def build_nested_overrides(layout_name, p):
    # 布局特定的嵌套覆盖
    base = {
        ("blockquote","p"): f"margin:0 0 8px;font-size:14px;line-height:1.8;color:{p['text_muted']};text-align:justify;",
        ("pre","code"): "font-size:13px;line-height:1.8;",
        ("golden-quote","p"): f"margin:0 0 8px;font-size:17px;font-weight:700;line-height:1.9;color:{p['primary']};text-align:center;",
        ("highlight-box","strong"): f"color:{p['contrast']};font-weight:700;",
        ("cta-footer","p"): f"margin:0 0 10px;font-size:14px;font-weight:500;line-height:1.8;color:{p['primary']};text-align:center;",
        ("highlight-box","p"): f"margin:0 0 8px;font-size:15px;line-height:1.9;color:{p['text_dark']};text-align:justify;",
    }
    if layout_name == "cardflow":
        base[("cta-footer","p")] = f"margin:0 0 10px;font-size:14px;font-weight:500;line-height:1.8;color:{p['white']};text-align:center;"
    if layout_name == "editorial":
        base[("blockquote","p")] = f"margin:0;font-size:20px;font-weight:600;line-height:1.9;color:{p['primary']};text-align:center;"
    if layout_name == "letter":
        base[("golden-quote","p")] = f"margin:0;font-size:18px;font-weight:600;line-height:2.0;color:{p['primary']};text-align:center;"
        base[("cta-footer","p")] = f"margin:0 0 8px;font-size:13px;color:{p['text_muted']};text-align:center;"
    if layout_name == "workshop":
        base[("blockquote","p")] = f"margin:0 0 8px;font-size:14px;line-height:1.8;color:{p['text_on_dark']};text-align:justify;"
        base[("cta-footer","p")] = f"margin:0 0 10px;font-size:14px;font-weight:500;line-height:1.8;color:{p['text_on_dark']};text-align:center;"
        base[("golden-quote","p")] = f"margin:0;font-size:16px;font-weight:700;line-height:1.8;color:{p['contrast']};text-align:center;"
    return base


# ══════════════════════════════════════════════════════════
# InlineStyleConverter (unchanged)
# ══════════════════════════════════════════════════════════

class InlineStyleConverter(HTMLParser):
    def __init__(self, styles, nested_overrides):
        super().__init__(convert_charrefs=False)
        self.styles = styles; self.nested_overrides = nested_overrides
        self.output = []; self.tag_stack = []
        self._void_elements = {'hr','br','img','input','meta','link'}
        self._last_container_cls = None  # 🔴 追踪上一个闭合容器元素的 class，用于兄弟间距防叠加
    def _get_base_style(self, tag, cls):
        if cls:
            ck = f".{cls}"
            if ck in self.styles: return self.styles[ck]
        if tag in self.styles: return self.styles[tag]
        return None
    def _get_nested_override(self, tag):
        if not self.tag_stack: return None
        pt, pc = self.tag_stack[-1]
        if pc:
            ov = self.nested_overrides.get((pc, tag))
            if ov: return ov
        return self.nested_overrides.get((pt, tag))
    def _build_style_attr(self, tag, cls, extra_style=None):
        base = self._get_base_style(tag, cls)
        override = self._get_nested_override(tag)
        final = override or base
        if extra_style:
            final = (final.rstrip(';')+';'+extra_style) if final else extra_style
        return f' style="{final}"' if final else ""
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', None)
        extra_style = attrs_dict.get('style', None)
        attr_parts = [f'{k}="{v}"' for k,v in attrs if k not in ('class','style')]
        style_str = self._build_style_attr(tag, cls, extra_style)

        # 🔴 兄弟间距防叠加：golden-quote → cta-footer 紧邻时压缩 margin-top
        if cls == 'cta-footer' and self._last_container_cls == 'golden-quote' and style_str:
            style_str = re.sub(r'margin-top:\s*\d+px', 'margin-top:12px', style_str)

        if style_str: attr_parts.append(style_str)
        attr_str = (' '+' '.join(attr_parts)) if attr_parts else ''
        self.output.append(f'<{tag}{attr_str}>')
        if tag not in self._void_elements:
            self.tag_stack.append((tag, cls))
    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')
        if self.tag_stack and self.tag_stack[-1][0] == tag:
            _, cls = self.tag_stack.pop()
            # 🔴 记录容器级元素的 class，供兄弟间距防叠加使用
            if tag in ('blockquote','section'):
                self._last_container_cls = cls
    def handle_data(self, data): self.output.append(data)
    def handle_entityref(self, name): self.output.append(f'&{name};')
    def handle_charref(self, name): self.output.append(f'&#{name};')
    def get_result(self): return ''.join(self.output)


# ══════════════════════════════════════════════════════════
# 验证 & CLI
# ══════════════════════════════════════════════════════════

def validate_output(html):
    clean = re.sub(r'<code[^>]*>.*?</code>','',html,flags=re.DOTALL)
    clean = re.sub(r'<pre[^>]*>.*?</pre>','',clean,flags=re.DOTALL)
    errors = []
    if re.search(r'<style[^>]*>',clean,re.IGNORECASE): errors.append("❌ <style>")
    if re.search(r'\sclass\s*=',clean): errors.append("❌ class=")
    if re.search(r'<div[\s>]',clean,re.IGNORECASE): errors.append("❌ <div>")
    if 'linear-gradient' in clean.lower(): errors.append("❌ linear-gradient")
    if 'letter-spacing' in clean.lower(): errors.append("❌ letter-spacing")
    if errors:
        print("\n".join(errors)); return False
    print("✅ 验证通过: 零 style/div/class/linear-gradient/letter-spacing")
    return True

def main():
    args = sys.argv[1:]
    theme_arg = "teal"; layout_arg = None; palette_arg = None
    input_file = "output/article-class-html.html"
    output_file = "output/article-inline.html"
    pos_count = 0; i = 0
    while i < len(args):
        if args[i] == "--theme" and i+1 < len(args): theme_arg = args[i+1]; i += 2
        elif args[i] == "--layout" and i+1 < len(args): layout_arg = args[i+1]; i += 2
        elif args[i] == "--palette" and i+1 < len(args): palette_arg = args[i+1]; i += 2
        elif not args[i].startswith("--"):
            if pos_count == 0: input_file = args[i]
            else: output_file = args[i]
            pos_count += 1; i += 1
        else: i += 1

    if layout_arg and palette_arg and palette_arg in PALETTES and layout_arg in LAYOUTS:
        layout_name, palette = layout_arg, PALETTES[palette_arg]
    else:
        layout_name, palette = resolve_theme(theme_arg)

    li = LAYOUTS[layout_name]
    print(f"📐 布局: {li['name']} ({li['desc']})")
    print(f"🎨 配色: {palette['name']} ({palette['desc']})")
    print(f"   主色: {palette['primary']}  |  对比色: {palette['contrast']}")

    styles = build_styles(layout_name, palette)
    nested = build_nested_overrides(layout_name, palette)

    with open(input_file,'r',encoding='utf-8') as f: html = f.read()
    converter = InlineStyleConverter(styles, nested)
    converter.feed(html)
    result = converter.get_result()
    result = re.sub(r'letter-spacing:[^;"]*;?','',result)

    with open(output_file,'w',encoding='utf-8') as f: f.write(result)
    print(f"✅ 转换完成: {input_file} → {output_file}")
    print(f"   输出大小: {len(result)} 字符")
    validate_output(result)

if __name__ == '__main__':
    main()
