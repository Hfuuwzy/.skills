# ~/.skills - AI Coding Skills 中央仓库

> OpenCode、Claude Code 与其他兼容客户端在本机使用的 skill source of truth。

## 核心规则

1. `~/.skills/` 保存 canonical package；全局发现目录只保留按需创建的 junction。
2. 普通 skill 按语义分类；同一上游仓库中不可拆分的集合使用 bundle 目录。
3. 一个 package root 必须直接包含 `SKILL.md`；每个非空 category 或 bundle root 同级放置一个 `.skill-sources.json` aggregate，不把嵌套的 `SKILL.md` 当成独立 package。
4. `.skill-sources.json` 位于 skill directory 旁边，不属于任何 skill package payload。它是稀疏的 URL-only map：只有来源已明确绑定的 package 才有同名 entry，来源不完整的 package 暂时省略。
5. `browser/` 是预留分类，目前只含 `.gitkeep`，没有 skill package，也没有 aggregate 文件。

## 目录结构

```text
~/.skills/
├── ai/                     # AI、生成模型、prompt 与检索
├── backend/                # 后端、服务契约与 MCP
├── browser/                # 预留浏览器分类（当前为空）
├── design/                 # 视觉、艺术、界面设计与设计优化
├── document/               # 文档格式、演示文稿、表格与 Obsidian
├── frontend/               # Web/UI 实现、界面工程与终端 UI
├── myCreatsSkills/         # 本机定制 skill
├── openspec/               # collection: Fission-AI/OpenSpec
├── research/               # 文献检索、综述、引用与研究流程
├── testing/                # 测试、TDD、代码审查与质量验证
├── tools/                  # skill 管理与通用元工具
├── writing/                # 写作、协作与内容整理
├── agent-browser/          # bundle: vercel-labs/agent-browser
├── grill/                  # bundle: mattpocock/skills
├── superpowers-plus/       # bundle: xhyqaq/superpowers-plus
├── ui-ux-pro-max-skill/    # bundle: nextlevelbuilder/ui-ux-pro-max-skill
├── src/ui-ux-pro-max/      # ui-ux-pro-max 的共享运行时数据，不是 skill package
└── README.md
```

四个 bundle 是语义分类的明确例外：`agent-browser`（`vercel-labs/agent-browser`）、`grill`（`mattpocock/skills`）、`superpowers-plus`（`xhyqaq/superpowers-plus`）、`ui-ux-pro-max-skill`（`nextlevelbuilder/ui-ux-pro-max-skill`）。`openspec` 是 `Fission-AI/OpenSpec` 的独立 collection root。bundle 或 collection 下每个直接包含 `SKILL.md` 的子目录仍是独立 package。

共享上游 repository 本身不足以建立 bundle。只有上游明确耦合的 collection、共享 runtime 或 distribution 需求，或共同维护关系成立时，才使用 bundle；普通独立 skill 仍归入 semantic category。

当前共有 15 个 aggregate 文件：`ai/`、`backend/`、`design/`、`document/`、`frontend/`、`myCreatsSkills/`、`openspec/`、`research/`、`testing/`、`tools/`、`writing/`、`agent-browser/`、`grill/`、`superpowers-plus/`、`ui-ux-pro-max-skill/`。稀疏 map 可以为空；`grill/` 当前有 11 个 entry，`myCreatsSkills/` 是目前唯一为空的 map。`browser/` 是预留空分类，因此没有 `.skill-sources.json`。

`src/ui-ux-pro-max/` 只提供运行时 `data` 与 `scripts`。`ui-ux-pro-max-skill/ui-ux-pro-max/{data,scripts}` 通过 NTFS junction 指向这些目录；不要复制、移动或把 `src/` 计入 package 数量。

## Package 结构与聚合元数据

```text
~/.skills/<category-or-bundle>/
├── <skill-name>/             # 直接包含 SKILL.md 的 package
│   ├── SKILL.md              # 必需；直接位于 package root
│   ├── references/           # 可选
│   ├── scripts/              # 可选
│   └── ...                   # 其他 package payload
├── <another-skill>/          # 另一个直接 package
└── .skill-sources.json       # 必需；root-level aggregate，位于 skill directories 旁边
```

分类扫描只认“目录直接包含 `SKILL.md`”这一规则。不要创建 wrapper 目录或在 package payload 中再放另一个独立 `SKILL.md`。

## 来源定位 map

每个 category、bundle 或 collection root 的 `.skill-sources.json` 使用同一个 URL-only contract。文件顶层只能有 `skills` object；其中每个 key 必须等于该 root 下一个直接 package directory name，而且该目录必须直接包含 `SKILL.md`。

`skills` 是稀疏 map，不要求覆盖所有本地 package。每个 value 必须是一个非空、完整、具体的 GitHub tree URL，格式为 `https://github.com/<owner>/<repo>/tree/<branch>/<source-subpath>`。URL 必须定位到所选 package 自身，而不是仅定位到 repository 或 collection discovery root；当前迁移记录全部使用各 repository 的实际 default branch。

```json
{
  "skills": {
    "example-skill": "https://github.com/example/repo/tree/main/skills/example-skill"
  }
}
```

只有在安装流程验证 GitHub payload 后，才写入所选 candidate 的最终 concrete tree URL。local source、无法验证的 GitHub source，以及缺少精确 package subpath 的旧记录不写占位值，也不根据目录名、frontmatter、扫描结果或 collection 名猜测路径；它们保持省略，等待以后显式绑定。

## 全局发现与 junction 安全

中央仓库本身不是客户端发现目录。当前全局 loader roots 为：

| 客户端 | 发现目录 | 当前 leaves |
|---|---|---:|
| OpenCode | `~/.config/opencode/skills/` | 33 |
| Claude | `~/.claude/skills/` | 32 |

这些 leaves 是 NTFS directory junction，loader folder name 与中央 package name 解耦。分类迁移时只重建目标已变化的既有 leaves；不触碰未受影响的 junction，不把 bundle 其他成员自动暴露到全局，也不把普通目录当成可替换链接。

安全重定向流程：先记录 leaf 的类型与精确 target，确认它是 `Junction` 或 `SymbolicLink`，再用 `cmd /d /c rmdir` 删除该 leaf，并用 `cmd /d /c mklink /J` 指向新 package。重建后必须验证精确 target 与直接可见的 `SKILL.md`。junction 重定向后应重启 OpenCode/Claude，使当前进程丢弃已加载的旧路径。

当前仓库没有项目级 link roots。本次 taxonomy 不再使用旧的 `project/` 分类；项目级发现与分发策略将在管理 skill 重构时另行定义。

## 管理工具与延期工作

`tools/install-skill`、`tools/update-skill`、`tools/link-skills`、`tools/audit-skills` 是现有管理入口。`install-skill` 在 GitHub payload 验证后写入 URL-only aggregate locator；local 或不完整、不可验证的 GitHub candidate 会从该 selected key 省略。`update-skill` 是仅凭已存 concrete GitHub tree URL 的 URL-only 覆盖更新器，只更新已有 central package；它不修改 source map，且没有 source 的本地 package 会被排除。`link-skills` 与 `audit-skills` 的 payload 和行为保持不变。以下工作明确延期：

- 让 link/audit 原生理解语义分类、bundle 与 root-level `.skill-sources.json` aggregate。
- 设计项目级安装/链接流程。
- 执行端到端 install -> link -> audit -> unlink 集成测试。

在这些重构完成前，新增或移动 package 后应人工核对 package root 规则、URL-only aggregate contract、每个已记录 `skills` key 是否对应直接 package 目录、tree URL 是否定位到具体 package、aggregate 是否位于 package payload 之外、`browser/` 是否仍为空、junction target 与 loader leaf 数量。

## 命名与安全

- 新建或重命名 package 时，目录名使用 `[a-z0-9-]+`，`SKILL.md` frontmatter `name` 应与目录名一致。现有 `myCreatsSkills/ppt_fast` 是保留的 legacy 目录名例外；本次迁移未改写其他旧 skill 的 frontmatter 名称，旧命名差异留待后续清理。
- 不在中央仓库保存 secret 或 API key。
- 不用递归删除命令处理 junction；只对已确认的 link leaf 使用 `cmd /d /c rmdir`。
- 不递归扫描 `.codegraph`；`.codegraph`、`.omo`、`.git` 与 `src/` 都不是 skill 分类。
- 本机 NTFS 路径优先使用 directory junction；junction 是 live link，不是快照。

---

*Last updated: 2026-08-26 - Windows 11 + OpenCode + Claude Code*
