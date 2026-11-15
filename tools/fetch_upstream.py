#!/usr/bin/env python3
"""从 Modrinth 拉取 PneumaticCraft: Repressurized 指定 MC 版本的最新 jar,
抽出 en_us 手册与 lang 基准文件到 upstream/。

用法:
    python3 tools/fetch_upstream.py --mc 1.21.1 [--loader neoforge]
"""
import argparse
import json
import os
import shutil
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "jssda/pnc-cn-guidebook/1.0 (github.com/jssda)"
PROJECT = "pneumaticcraft-repressurized"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", required=True, help="Minecraft 版本, 例如 1.21.1")
    ap.add_argument("--loader", default="neoforge")
    args = ap.parse_args()

    versions = get(f"https://api.modrinth.com/v2/project/{PROJECT}/version"
                   f"?loaders=%5B%22{args.loader}%22%5D&game_versions=%5B%22{args.mc}%22%5D")
    if not versions:
        print(f"未找到 {PROJECT} 的 {args.loader}/{args.mc} 版本")
        return 1
    v = versions[0]  # Modrinth 按发布时间倒序
    f = next(x for x in v["files"] if x.get("primary")) or v["files"][0]
    print(f"最新: {v['version_number']}  文件: {f['filename']}")

    work = os.path.join(ROOT, ".work")
    os.makedirs(work, exist_ok=True)
    jar = os.path.join(work, f["filename"])
    if not os.path.exists(jar):
        print("下载中...")
        req = urllib.request.Request(f["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r, open(jar, "wb") as out:
            shutil.copyfileobj(r, out)

    mod_ver = v["version_number"].split("+")[0]
    book_dst = os.path.join(ROOT, "upstream", f"book_en_us_{args.mc}")
    if os.path.exists(book_dst):
        shutil.rmtree(book_dst)
    os.makedirs(book_dst, exist_ok=True)
    n = 0
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            if name.startswith("assets/pneumaticcraft/patchouli_books/book/en_us/") and name.endswith(".json"):
                rel = name.split("book/en_us/", 1)[1]
                target = os.path.join(book_dst, rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as fp:
                    fp.write(z.read(name))
                n += 1
            elif name in ("assets/pneumaticcraft/lang/en_us.json", "assets/pneumaticcraft/lang/zh_cn.json"):
                code = name.rsplit("/", 1)[-1].replace(".json", "")
                with open(os.path.join(ROOT, "upstream", f"lang_{code}_{mod_ver}.json"), "wb") as fp:
                    fp.write(z.read(name))
    print(f"抽出 en_us 手册 {n} 个文件 -> upstream/book_en_us_{args.mc}/")
    print(f"抽出 lang 基准 -> upstream/lang_(en_us|zh_cn)_{mod_ver}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
