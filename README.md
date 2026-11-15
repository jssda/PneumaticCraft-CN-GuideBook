# PneumaticCraft-CN-GuideBook

[气动工艺：再加压 PneumaticCraft: Repressurized](https://modrinth.com/mod/pneumaticcraft-repressurized)（作者 desht / TeamPneumatic）内置 **Patchouli 参考手册**的简体中文汉化**资源包**。

Modrinth: <https://modrinth.com/resourcepack/pneumaticcraft-repressurized-guidebook-cn>

- 汉化方式：纯资源包，不改动模组本体。mod jar 内置的手册只有 `en_us / ja_jp / pt_br` 三个语言文件夹，本包补充 `zh_cn`；游戏语言为简体中文时 Patchouli 自动加载。
- 附带 lang 补丁：补译 mod 8.2.23 内置 zh_cn.json（CFPAOrg 提供）缺失的 44 个键（资源包 lang 与模组 lang 按键合并，高优先级覆盖）。
- 支持加载器：NeoForge / Forge / Fabric 均可（与加载器无关，只依赖 Patchouli）。
- 翻译来源：以 2020 年[迷途之家汉化组](https://github.com/5huxiaoyang6/PneumaticCraft-Repressurized--Patchouli--localization)的 1.16 版手册汉化（覆盖 176/236 文件）为措辞参考逐页移植；英文已更新处按现行英文重译；60 个新增条目全新翻译。术语与 mod 官方 zh_cn lang（CFPA）严格对齐（见 `docs/glossary.md`）。

## 版本对照

| 汉化版本 | 对应模组版本 | Minecraft | pack_format |
|---|---|---|---|
| 1.0.0 | 8.2.23 | 1.21 / 1.21.1 | 34（声明支持 34–55） |

> 手册 JSON 的结构（页数、页面类型）随模组版本变化，换模组版本请按下面「更新到新版本」重新核对，别直接复用。

## 安装

把 `dist/PneumaticCraft-CN-GuideBook-v<mod>+mc<mc>.zip` 放进 `.minecraft/resourcepacks/`（HMCL 版本隔离实例放 `versions/<实例名>/resourcepacks/`），游戏内「选项 → 资源包」启用，游戏语言设为**简体中文**。

## 仓库结构

```
pack.mcmeta                     # 资源包描述 (pack_format 34)
pack.png                        # 资源包图标 (mod 手册物品贴图)
assets/pneumaticcraft/patchouli_books/book/zh_cn/   # 手册汉化 (236 个 JSON)
assets/pneumaticcraft/lang/zh_cn.json               # lang 补缺 (44 键, 与 mod 内置 zh_cn 按键合并)
upstream/book_en_us_<mc>/       # 上游手册英文基准 (用于比对)
upstream/lang_en_us_*.json      # 上游 mod lang 基准
upstream/lang_zh_cn_*.json      # mod 内置官方 zh_cn (术语基准)
tools/fetch_upstream.py         # 从 Modrinth 拉取指定 MC 版本的最新 jar, 抽出 en_us 手册与 lang
tools/check_book.py             # 校验: JSON 结构/标记配对/链接目标/残留英文/lang 键
tools/build.py                  # 打包 dist/*.zip
tools/create_project.py         # 在 Modrinth 创建项目 (幂等, 首次用; 新项目必须 is_draft 再单独提审)
tools/publish_modrinth.py       # 发布到 Modrinth (令牌走 pass:modrinth/token, 支持 --dry-run)
changelog/<版本号>.md           # 版本更新说明 (发布时自动带上)
docs/glossary.md                # 术语对照表 (英文名 → 官方 zh_cn 译名)
.github/workflows/release.yml   # 打 tag 自动校验 + 打包 + 发 Release
```

## 日常维护

```bash
# 1. 拉上游基准 (模组更新后先跑这个)
python3 tools/fetch_upstream.py --mc 1.21.1

# 2. 校验汉化与上游一致性 (结构/Patchouli 标记/链接/残留英文/lang 键)
python3 tools/check_book.py --mc 1.21.1

# 3. 打包
python3 tools/build.py --mod-version 8.2.23 --mc 1.21.1

# 4. 发布到 Modrinth (先 --dry-run 预览)
python3 tools/publish_modrinth.py --file dist/PneumaticCraft-CN-GuideBook-v8.2.23+mc1.21.1.zip --version-number 1.0.0 --dry-run
python3 tools/publish_modrinth.py --file dist/PneumaticCraft-CN-GuideBook-v8.2.23+mc1.21.1.zip --version-number 1.0.0
```

## 更新到新版本

1. `tools/fetch_upstream.py --mc <MC版本>` 拉新基准；
2. `tools/check_book.py` 看哪些文件结构漂移（shape mismatch / 页数变化）或英文源已改（对漂移文件逐页比对 upstream 新旧英文）；
3. 只重译漂移/变更的文件，未变的沿用；改名条目参考 difflib 匹配 + 人工核对；
4. 校验 → 改 `pack.mcmeta` 描述与 `changelog/` → 打包发布。

发布：给 commit 打 tag（格式 `v<模组版本>+mc<MC版本>`，如 `v8.2.23+mc1.21.1`）并推送，CI 自动校验、打包并发 GitHub Release；Modrinth 用 `tools/publish_modrinth.py`。

## 参与

发现翻译错误或漏译，欢迎提 Issue / PR。提 PR 前请先跑 `python3 tools/check_book.py`。

## 许可

MIT（见 LICENSE）。模组本体及其内置翻译版权归 desht / TeamPneumatic 及各自译者所有；本包部分译文移植自迷途之家汉化组（AnECAnSaiTin、Yakumo_Ringo、冴月麟）的旧版汉化，特此致谢。
