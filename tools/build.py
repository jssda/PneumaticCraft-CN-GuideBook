#!/usr/bin/env python3
"""打包资源包 zip。

用法:
    python3 tools/build.py --mod-version 8.2.23 --mc 1.21.1

产物: dist/PneumaticCraft-CN-GuideBook-v<mod>+mc<mc>.zip
zip 内只含 pack.mcmeta / pack.png / assets/**, 且 pack.mcmeta 在最外层。
"""
import argparse
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCLUDE_FILES = ["pack.mcmeta", "pack.png"]
INCLUDE_DIRS = ["assets"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod-version", default="8.2.23")
    ap.add_argument("--mc", default="1.21.1")
    ap.add_argument("--outdir", default=os.path.join(ROOT, "dist"))
    args = ap.parse_args()

    name = "PneumaticCraft-CN-GuideBook-v%s+mc%s.zip" % (args.mod_version, args.mc)
    os.makedirs(args.outdir, exist_ok=True)
    out = os.path.join(args.outdir, name)

    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in INCLUDE_FILES:
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                z.write(p, f)
                n += 1
        for d in INCLUDE_DIRS:
            base = os.path.join(ROOT, d)
            for dirpath, _dirnames, filenames in os.walk(base):
                for fn in sorted(filenames):
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.relpath(full, ROOT))
                    n += 1

    with zipfile.ZipFile(out) as z:
        meta = json.loads(z.read("pack.mcmeta").decode("utf-8"))
        lang = json.loads(z.read("assets/pneumaticcraft/lang/zh_cn.json").decode("utf-8"))
        book = sum(1 for x in z.namelist() if "/patchouli_books/" in x)

    print("产出: %s (%.1f KB, %d 个文件)" % (out, os.path.getsize(out) / 1024, n))
    print("pack_format=%s supported_formats=%s 手册文件=%d lang补丁键=%d"
          % (meta["pack"].get("pack_format"), meta["pack"].get("supported_formats"), book, len(lang)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
