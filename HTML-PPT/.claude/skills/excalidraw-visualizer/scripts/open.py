#!/usr/bin/env python3
"""自动打开 Excalidraw 文件（骨架，二期实现）

当前功能：
  - 告知用户文件路径和手动打开方式
  - 验证文件存在

二期将实现：
  A. 通过 Excalidraw URL hash 参数自动加载 (`http://localhost:3000#json=...`)
  B. 文件监听 + WebSocket 推送刷新
  C. Electron 桌面 App IPC 直接打开
"""

import os
import sys


EXCALIDRAW_URL = os.environ.get("EXCALIDRAW_URL", "http://localhost:3000")


def open_in_excalidraw(filepath):
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        return False

    print(f"  ├─ 文件已生成: {filepath}")
    print(f"  ├─ 请拖入 Excalidraw: {EXCALIDRAW_URL}")
    print(f"  └─ 自动打开功能将在二期实现")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python open.py <filepath>")
        sys.exit(1)
    open_in_excalidraw(sys.argv[1])


if __name__ == "__main__":
    main()
