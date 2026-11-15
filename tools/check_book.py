#!/usr/bin/env python3
"""校验手册汉化与上游一致性。

用法:
    python3 tools/check_book.py --mc 1.21.1

检查项:
  1. zh_cn 手册树与 upstream/book_en_us_<mc> 文件一一对应
  2. 每个 JSON 可解析, 键集合/键顺序/嵌套结构与英文源一致
  3. 非可译字段 (type/icon/item/recipe/...) 逐字节相同
  4. 可译字段 (name/title/text/description/header/link_text) 的 Patchouli
     标记 $( / $() / /$ 计数一致, $(l:...) 链接目标多重集合一致
  5. 可译字段无大段残留英文 (与英文相同的 >3 词句, 变量/ID 除外)
  6. lang 补丁键: 均存在于上游 en_us, 且不被 mod 内置 zh_cn 覆盖 (否则提示可删)
"""
import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = {"name", "title", "text", "description", "header", "link_text"}
LINK = re.compile(r"\$\(l:([^)]*)\)")


def shape(o):
    if isinstance(o, dict):
        return [(k, shape(v)) for k, v in o.items()]
    if isinstance(o, list):
        return [shape(i) for i in o]
    return type(o).__name__


def strings(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", default="1.21.1")
    args = ap.parse_args()

    zh_dir = os.path.join(ROOT, "assets/pneumaticcraft/patchouli_books/book/zh_cn")
    en_dir = os.path.join(ROOT, f"upstream/book_en_us_{args.mc}")
    if not os.path.isdir(en_dir):
        print(f"缺少上游基准 {en_dir}, 先跑 tools/fetch_upstream.py --mc {args.mc}")
        return 2

    def rels(d):
        return {os.path.relpath(os.path.join(r, f), d)
                for r, _, fs in os.walk(d) for f in fs if f.endswith(".json")}

    en_files, zh_files = rels(en_dir), rels(zh_dir)
    errs, warns = [], []
    if en_files - zh_files:
        errs += [("缺文件", f) for f in sorted(en_files - zh_files)]
    if zh_files - en_files:
        warns += [("多余文件(上游已删?)", f) for f in sorted(zh_files - en_files)]

    n_fields = 0
    for f in sorted(en_files & zh_files):
        try:
            en, zh = load(os.path.join(en_dir, f)), load(os.path.join(zh_dir, f))
        except Exception as e:
            errs.append(("JSON 解析失败", f"{f}: {e}"))
            continue
        if shape(en) != shape(zh):
            errs.append(("结构不一致", f))
            continue
        se, sz = list(strings(en)), list(strings(zh))
        link_e, link_z = collections.Counter(), collections.Counter()
        for (pe, ve), (pz, vz) in zip(se, sz):
            key = pe.rsplit(".", 1)[-1]
            link_e.update(LINK.findall(ve))
            link_z.update(LINK.findall(vz))
            if key not in TR:
                if ve != vz:
                    errs.append(("非可译字段被改动", f"{f} {pe}"))
                continue
            n_fields += 1
            for m in ("$(", "$()", "/$"):
                if ve.count(m) != vz.count(m):
                    errs.append((f"标记 {m} 计数不一致", f"{f} {pe}"))
            if ve == vz and len(ve.split()) > 3 and not ve.startswith("#") and ":" not in ve \
                    and re.search(r"[A-Za-z]{4}", ve):
                warns.append(("疑似未翻译", f"{f} {pe}: {ve[:60]}"))
        if link_e != link_z:
            errs.append(("链接目标不一致", f"{f}: {dict(link_e - link_z)} / {dict(link_z - link_e)}"))

    # lang 补丁
    up = os.path.join(ROOT, "upstream")
    sup_p = os.path.join(ROOT, "assets/pneumaticcraft/lang/zh_cn.json")
    if os.path.exists(sup_p):
        sup = load(sup_p)
        en_langs = sorted(x for x in os.listdir(up) if x.startswith("lang_en_us_"))
        zh_langs = sorted(x for x in os.listdir(up) if x.startswith("lang_zh_cn_"))
        if en_langs and zh_langs:
            en_lang, zh_lang = load(os.path.join(up, en_langs[-1])), load(os.path.join(up, zh_langs[-1]))
            for k in sup:
                if k not in en_lang:
                    errs.append(("lang 键上游不存在", k))
                elif k in zh_lang:
                    warns.append(("lang 键 mod 已自带译文, 可考虑删除", k))
        print(f"lang 补丁: {len(sup)} 键")

    print(f"文件: {len(en_files & zh_files)} 对比 / 可译字段 {n_fields} 处")
    for w in warns:
        print("WARN", *w)
    for e in errs:
        print("ERR ", *e)
    print(f"结果: 错误 {len(errs)}, 警告 {len(warns)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
