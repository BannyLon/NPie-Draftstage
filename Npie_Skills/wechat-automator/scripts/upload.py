#!/usr/bin/env python3
"""
阶段⑤ 一键上传：头图注入 + 封面直用 + 创建草稿
v1.3.0: 直接使用 img/cover.png 做封面，img/header_image.png 做头图，底部自动留白

🔴 铁律1：JSON 序列化必须 ensure_ascii=False
🔴 铁律3：只传 body 片段，不传完整 HTML 文档
"""
import sys
import os
import json
import re
import struct
import zlib
import requests

# 脚本所在目录的上级 = skill 根目录
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════

def get_access_token(appid, secret):
    resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={"grant_type": "client_credential", "appid": appid, "secret": secret},
        timeout=30,
    )
    data = resp.json()
    if "access_token" in data:
        return data["access_token"]
    raise RuntimeError(f"获取 access_token 失败: {data}")


def upload_image_to_wechat(token, filepath):
    """上传图片到微信永久素材库，返回 (media_id, cdn_url)"""
    if not os.path.exists(filepath):
        return None, None
    fname = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
            files={"media": (fname, f, "image/png")},
            timeout=60,
        )
    data = resp.json()
    if "media_id" in data:
        return data["media_id"], data.get("url", "")
    raise RuntimeError(f"上传图片失败: {data}")


def generate_cover_png(w=1080, h=1080, color=(13, 115, 119)):
    """品牌色纯色 PNG fallback（仅当 img/cover.png 不存在时使用）"""
    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)
    raw = b''
    for y in range(h):
        raw += b'\x00'
        for x in range(w):
            raw += struct.pack('BBB', *color)
    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')
    return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend


def strip_section_wrapper(html):
    """去掉外层 <section ...> 和 </section>，让内容直接填充 WeChat 文章区宽度"""
    html = html.strip()
    # 去掉开头 <section ...>
    m = re.match(r'<section\b[^>]*>', html)
    if m:
        html = html[m.end():]
    # 去掉结尾 </section>
    if html.rstrip().endswith('</section>'):
        html = html.rstrip()[:-len('</section>')]
    return html.strip()


def inject_header_image(html, cdn_url):
    """在内容最前面注入头图 <img>"""
    img_tag = f'<img style="display:block;width:100%;max-width:100%;margin:0 0 28px;border-radius:0;" src="{cdn_url}">'
    return img_tag + html


def inject_footer_spacer(html):
    """在内容最后面追加底部留白"""
    spacer = '<p style="margin:0;padding:0;height:0;"><br></p>'
    return html + spacer


# ═══════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════

def main():
    # 解析参数
    args = sys.argv[1:]
    token = None
    appid = None
    secret = None
    html_file = "output/article-inline.html"
    title = None
    author = "嗯哌"
    digest = ""

    i = 0
    while i < len(args):
        if args[i] == "--token" and i + 1 < len(args):
            token = args[i + 1]; i += 2
        elif args[i] == "--appid" and i + 1 < len(args):
            appid = args[i + 1]; i += 2
        elif args[i] == "--secret" and i + 1 < len(args):
            secret = args[i + 1]; i += 2
        elif args[i] == "--html" and i + 1 < len(args):
            html_file = args[i + 1]; i += 2
        elif args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]; i += 2
        elif args[i] == "--author" and i + 1 < len(args):
            author = args[i + 1]; i += 2
        elif args[i] == "--digest" and i + 1 < len(args):
            digest = args[i + 1]; i += 2
        else:
            i += 1

    # 获取 token
    if not token:
        if appid and secret:
            token = get_access_token(appid, secret)
        else:
            print("❌ 需要 --token 或 (--appid + --secret)")
            sys.exit(1)

    print(f"🔑 Token: {token[:20]}...")

    # 读取 inline HTML
    html_path = os.path.join(SKILL_ROOT, html_file) if not os.path.isabs(html_file) else html_file
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    print(f"📄 读取 HTML: {len(html)} 字符")

    # ── 步骤 0: 去掉 section wrapper，让内容填满 WeChat 宽度 ──
    html = strip_section_wrapper(html)
    print("🔓 已去除 section wrapper")

    # ── 步骤 1: 上传头图 → 注入 ──
    header_path = os.path.join(SKILL_ROOT, "img", "header_image.png")
    if os.path.exists(header_path):
        _, header_url = upload_image_to_wechat(token, header_path)
        if header_url:
            # 微信素材返回的是 http URL，微信公众号可接受 http
            html = inject_header_image(html, header_url)
            print(f"🖼️  头图已注入: {header_url[:60]}...")
    else:
        print("⚠️  img/header_image.png 不存在，跳过头图")

    # ── 步骤 2: 底部留白 ──
    html = inject_footer_spacer(html)
    print("⬇️  底部留白已注入")

    # ── 步骤 3: 上传封面 ──
    cover_path = os.path.join(SKILL_ROOT, "img", "cover.png")
    thumb_media_id = None

    if os.path.exists(cover_path):
        thumb_media_id, cover_url = upload_image_to_wechat(token, cover_path)
        print(f"🖼️  封面: img/cover.png → media_id={thumb_media_id[:20]}...")
    else:
        # Fallback: 自动生成纯色封面
        print("⚠️  img/cover.png 不存在，自动生成品牌色封面...")
        png = generate_cover_png()
        tmp_path = os.path.join(SKILL_ROOT, "output", "_temp_cover.png")
        with open(tmp_path, "wb") as f:
            f.write(png)
        thumb_media_id, cover_url = upload_image_to_wechat(token, tmp_path)
        os.remove(tmp_path)
        print(f"🖼️  自动生成封面 → media_id={thumb_media_id[:20]}...")

    if not thumb_media_id:
        print("❌ 封面上传失败，无法创建草稿")
        sys.exit(1)

    # ── 步骤 4: 创建草稿 ──
    if not title:
        title = "未命名推文"

    if len(title) > 64:
        title = title[:63] + "…"

    payload = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest[:120] if digest else "",
            "content": html,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
    }

    # 🔴 铁律1: ensure_ascii=False
    payload_json = json.dumps(payload, ensure_ascii=False)

    resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
        data=payload_json.encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=60,
    )
    result = resp.json()

    if "media_id" in result:
        print(f"\n✅ 草稿创建成功！")
        print(f"   media_id: {result['media_id']}")
        print(f"   → 打开公众号后台 → 草稿箱 → 预览 → 群发")
    else:
        print(f"\n❌ 创建失败: {result.get('errmsg', 'unknown')} (errcode={result.get('errcode', '')})")
        sys.exit(1)


if __name__ == "__main__":
    main()
