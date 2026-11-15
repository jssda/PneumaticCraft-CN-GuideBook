#!/usr/bin/env python3
"""在 Modrinth 创建本项目 (幂等: 已存在则只打印信息)。

用法:
    python3 tools/create_project.py [--dry-run]

Token 来源同 publish_modrinth.py (MODRINTH_TOKEN / ~/.config/modrinth/token / pass:modrinth/token)。
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from publish_modrinth import read_token, multipart, UA, PROJECT_SLUG  # noqa: E402

DESCRIPTION = """**气动工艺：再加压**（[PneumaticCraft: Repressurized](https://modrinth.com/mod/pneumaticcraft-repressurized)）内置 **Patchouli 参考手册**的简体中文汉化资源包。

## 为什么需要这个包

mod 本体已内置 CFPAOrg 提供的 zh_cn 语言文件（物品名、GUI 有中文），但 **Patchouli 手册只有 en_us / ja_jp / pt_br**，游戏里打开手册仍是英文。本资源包补充手册的 `zh_cn` 语言文件夹，游戏语言为简体中文时自动生效；另附带 44 个 mod 内置 zh_cn 缺失键的补译。

## 安装

1. 下载 zip 放入 `.minecraft/resourcepacks/`（HMCL 版本隔离实例放 `versions/<实例名>/resourcepacks/`）
2. 游戏内「选项 → 资源包」启用本包
3. 游戏语言设为简体中文

不修改模组本体；NeoForge / Forge / Fabric 均可（手册显示需要 Patchouli）。

## 内容

- 手册全套 236 个 JSON（17 分类 + 215 条目 + 4 模板），对应 mod **8.2.23** / MC **1.21.1**
- lang 补丁 44 键（与 mod 内置 zh_cn 按键合并）
- 术语与 mod 官方 zh_cn（CFPA）严格对齐：压力管道、充气站、编程器、亚马龙、转管机枪……

## 致谢与来源

- 以 2020 年**迷途之家汉化组**（AnECAnSaiTin、Yakumo_Ringo、冴月麟）的 1.16 版手册汉化为措辞参考逐页移植；英文已更新处按现行英文重译，60 个新增条目全新翻译
- 源码 / 校验工具 / 术语表：<https://github.com/jssda/PneumaticCraft-CN-GuideBook>
- 发现错译漏译欢迎提 Issue / PR

## 许可

MIT。模组本体及其内置翻译版权归 desht / TeamPneumatic 及各自译者所有。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass-entry", default="modrinth/token")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token, src = read_token(args.pass_entry)
    if not token:
        print("没有找到 Modrinth token (MODRINTH_TOKEN / ~/.config/modrinth/token / pass:modrinth/token)")
        return 3
    print("token 来源: %s" % src)

    # 幂等: 已存在则直接返回
    try:
        req = urllib.request.Request("https://api.modrinth.com/v2/project/%s" % PROJECT_SLUG,
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            p = json.load(r)
        print("项目已存在: %s (%s)  https://modrinth.com/resourcepack/%s" % (p["id"], p["title"], p["slug"]))
        return 0
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print("查询项目失败 HTTP %s: %s" % (e.code, e.read().decode()[:300]))
            return 1

    data = {
        "name": "PneumaticCraft-CN-GuideBook",
        "slug": PROJECT_SLUG,
        "summary": "气动工艺：再加压 Patchouli 手册简体中文汉化资源包 (mod 8.2.23 / MC 1.21.1)",
        "description": DESCRIPTION,
        "categories": ["locale"],
        "client_side": "required",
        "server_side": "unsupported",
        "license_id": "MIT",
        "project_type": "resourcepack",
        "source_url": "https://github.com/jssda/PneumaticCraft-CN-GuideBook",
        "issues_url": "https://github.com/jssda/PneumaticCraft-CN-GuideBook/issues",
        "initial_versions": [],
    }
    print("将创建项目: %s (%s)" % (data["name"], data["slug"]))
    if args.dry_run:
        print("(--dry-run, 未发送)")
        return 0

    body, ctype = multipart({"data": json.dumps(data, ensure_ascii=False)},
                            [("icon", os.path.join(ROOT, "pack.png"))])
    req = urllib.request.Request("https://api.modrinth.com/v2/project", data=body, method="POST",
                                 headers={"User-Agent": UA, "Authorization": token, "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        print("创建失败 HTTP %s\n%s" % (e.code, e.read().decode("utf-8", "replace")[:800]))
        if e.code == 401:
            print("提示: token 无效或缺少 PROJECT_CREATE 权限")
        return 1
    print("项目创建成功: %s (%s)" % (res["id"], res["slug"]))
    print("页面: https://modrinth.com/resourcepack/%s" % res["slug"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
