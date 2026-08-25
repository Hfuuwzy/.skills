# ~/.skills - 个人 AI Coding Skills 中央仓库

> Source of truth for all skills used by OpenCode, Claude Code, and other Claude-compatible agents on this machine.

---

## 设计理念

把所有 skills 集中放在一个仓库，**按需链接/复制**到具体工具的发现目录，避免：

- 多工具手动重复同步
- 同名 skill 版本漂移
- 不知道当前到底加载了哪个版本
- 卸载/迁移时找不到原始来源

**核心原则**：

1. `~/.skills/` 是**唯一源**，其他位置都是它的镜像或软链接
2. **分类放置**，不平铺
3. **项目级 ≠ 全局级**：项目 skills 是局部覆盖，不替代全局
**Windows 链接策略（auto 决策）**：

| 情况 | 默认模式 | 是否要 Dev Mode |
|---|---|---|
| 本机 NTFS 路径（同盘或跨盘） | `mklink /J` junction | 不要 |
| 网络共享 / UNC / 非 NTFS | `robocopy /MIR` 镜像复制 | 不要（但不是 live link） |

`link-skills` 会优先使用 junction；只要源和目标都是本机本地目录，就算跨盘（如 `C:` → `E:`）也可以直接 `mklink /J`。也可以用 `-Mode junction|symlink|copy` 强制指定；`symlink` 主要保留给明确想用符号链接的场景。

junction 与 symlink 都是真"链"——改一处全跟随；robocopy 是快照，需要重链才能更新。

---

## 目录结构

```
~/.skills/
├── ai/             # AI 功能、RAG、prompt、search
├── browser/        # 浏览器/Playwright/页面自动化
├── creative/       # 开发与设计：前后端、UI/UX、艺术、生成式视觉
├── document/       # docx / pdf / pptx / xlsx
├── process/        # 研究流程、subagent workflow、清理
├── project/        # 项目专用 skills
├── research/       # 文献检索、综述、引用、peer-review
├── writing/        # 文档、博客、技术写作、笔记
├── tools/          # 元工具：管理 skills 自身
│   ├── install-skill/
│   ├── link-skills/
│   └── audit-skills/
└── README.md       # 本文件
```

每个 skill 是一个文件夹，里面至少有一个 `SKILL.md`：

```
~/.skills/<category>/<skill-name>/
├── SKILL.md        # 必需，YAML frontmatter + Markdown
├── reference.md    # 可选，详细参考
└── ...             # 可选附属资源
```

---

## OpenCode 发现规则（重要）

OpenCode 会在以下位置发现 skills：

| 范围 | 路径 | 用途 | 本系统管理 |
|---|---|---|---|
| 项目级（OpenCode 原生） | `<repo>/.opencode/skills/` | 项目专用 | ✅ |
| 项目级（Claude 兼容） | `<repo>/.claude/skills/` | 跨 OpenCode/Claude 共享的项目 skill | ✅ |
| 全局（OpenCode 原生） | `~/.config/opencode/skills/` | 当前主力全局目录 | ✅ |
| 全局（Claude 兼容） | `~/.claude/skills/` | Claude Code 也能用 | ✅ |
| 项目级（agent 兼容） | `<repo>/.agents/skills/` | OpenCode 也读，但本系统不管理 | ❌ |
| 全局（agent 兼容） | `~/.agents/skills/` | OpenCode 也读，但本系统不管理 | ❌ |

`link-skills` / `audit-skills` 只处理 ✅ 那 4 个目标。`.agents/skills` 不在管理范围内（OpenCode 仍会发现，但要靠手工维护）。

**关键事实**：

- 项目级 + 全局级 **同时被发现**，不互相替代
- **同名 skill 才会发生覆盖**，通常项目级优先
- `~/.skills/` 本身**不是** OpenCode 的发现目录 — 它是中央仓库，必须通过 junction 或 copy 镜像到上述位置

---

## 三个管理 skill

所有元工具放在 `~/.skills/tools/` 下，通过 `link-skills` 自身把它们链接到 `~/.config/opencode/skills/`。

### 1. `install-skill`

把外部 skill 拉进中央仓库。

输入：

- GitHub URL（`https://github.com/<owner>/<repo>` 或带 `tree/<branch>/<subpath>`）
- GitHub shorthand（`<owner>/<repo>`）
- 本地绝对路径

输出：

- `~/.skills/<category>/<skill-name>/`

**它不启用 skill**，只放进中央仓库。启用是 `link-skills` 的工作。

### 2. `link-skills`

把中央仓库的 skill 启用到具体工具/作用域。

支持四种目标：

| 目标 | 路径 |
|---|---|
| OpenCode-Global | `~/.config/opencode/skills/` |
| Claude-Global | `~/.claude/skills/` |
| OpenCode-Project | `<repo>/.opencode/skills/` |
| Claude-Project | `<repo>/.claude/skills/` |

**Windows 链接策略（auto 决策）**：

| 情况 | 默认模式 | 是否要 Dev Mode |
|---|---|---|
| 本机 NTFS 路径（同盘或跨盘，C: → C:、C: → E: 都行） | `mklink /J` junction | 不需要 |
| 网络共享 / UNC / 非 NTFS（如 `\\server\share`、FAT32） | `robocopy /MIR` 镜像（快照） | 不需要 |

事实修正：Windows 目录 junction **可以跨本地卷**（`mklink /J E:\foo C:\bar` 完全合法），同盘限制是针对**硬链接**，不是 junction。所以本机不同盘符之间也用 junction，不必降级到 symlink 或 copy。

也可以用 `-Mode junction|symlink|copy` 强制指定（symlink 主要给需要 `LinkType: SymbolicLink` 而不是 `Junction` 的特殊场景，需要 Dev Mode 或管理员）。

junction 是真链（改源即同步），robocopy 是快照（需重链才更新）。

junction 的几个好处：

- 不需要 Developer Mode
- 不需要管理员权限
- 跨本地盘符也能用
- 直接 `Get-Item` 显示 `LinkType: Junction`
- 卸载只需 `cmd /c rmdir`（不会删除源）

### 3. `audit-skills`

只读体检工具。

扫描位置：

- `~/.skills/`
- `~/.config/opencode/skills/`
- `~/.claude/skills/`
- `<closest-repo>/.opencode/skills/`
- `<closest-repo>/.claude/skills/`

报告：

- 重名 skill 在哪些位置
- 同名但内容漂移（SHA256 比对 SKILL.md）
- frontmatter 不合法
- junction 失效
- 孤儿 skill（只在 target 不在中央仓库）
- 空文件 / 格式错误

**永远只读**，不修改任何东西，建议项会指向 `install-skill` 或 `link-skills`。

---

## 推荐工作流

### 装一个新 skill

```text
1. install-skill https://github.com/<owner>/<repo>
   → 落到 ~/.skills/<category>/<skill-name>/
2. link-skills
   → 选择目标 (OpenCode-Global / Claude-Global / 项目)
3. audit-skills
   → 验证状态
```

### 给某个项目挂一个项目专用 skill

```text
1. 在 ~/.skills/project/<my-skill>/SKILL.md 写好
2. link-skills → 选 OpenCode-Project
   → 在项目根创建 .opencode/skills/<my-skill> junction
3. 团队共享：
   - 不要直接 commit junction（git 在 Windows 上对 junction 处理不一致）
   - 推荐方案 A：把 SKILL.md 源文件直接放进项目 .opencode/skills/<my-skill>/，commit 这个真实目录
   - 推荐方案 B：用 link-skills 选 -Mode copy，commit 复制出来的真实文件，团队拉下后用 audit-skills 监控漂移
```

### 升级一个已有 skill

```text
1. 直接编辑 ~/.skills/<category>/<skill-name>/SKILL.md
2. 因为 OpenCode/Claude 那边是 junction，自动同步
3. 跨盘 copy 模式则需要重新 link-skills
```

### 定期巡检

```text
audit-skills
```

---

## 命名约定

- skill 文件夹名：`[a-z0-9-]+`，不含空格
- frontmatter `name:` 必须等于文件夹名
- frontmatter `description:` 至少 30 字符，描述**何时使用**而不是**做什么**
- 项目专用 skill 加前缀，例如 `ersbyai-backend-feature`，避免遮蔽全局同名 skill

---

## Windows 注意事项

| 项 | 说明 |
|---|---|
| Dev Mode | junction 不需要；若你显式强制 `symlink`，则需要 |
| Admin | 不需要 |
| 链接方式 | 本机 NTFS（同盘或跨盘）→ `mklink /J`；网络共享 / 非 NTFS → `robocopy /MIR` 快照 |
| 路径长度 | 接近 240 字符时用 `\\?\` 前缀 |
| 路径引用 | 永远 `-LiteralPath`，永远引号 |
| jq | 不需要，使用 `ConvertFrom-Json` 或简单正则 |

---

## 安全约定

- **永远不用 `rm`**。删除一律 `Remove-Item -LiteralPath` 并显式确认。
- junction 删除**不会**删源，但 `Remove-Item -Recurse` 在某些 PowerShell 版本上对 junction 行为有坑：先用 `cmd /c rmdir <path>` 删 junction，再 `Remove-Item` 处理普通目录。
- 安装 skill 前应人工浏览 SKILL.md，避免运行恶意 prompt。
- 中央仓库不放任何 secret / API key。

---

## 同名 skill 的处理策略

如果你想**用项目级覆盖全局**：

```text
全局 ~/.skills/creative/ui-ux-pro-max/        ← canonical
项目 <repo>/.opencode/skills/ui-ux-pro-max/   ← 覆盖（同名）
```

OpenCode 发现两份同名时，项目级优先。

如果你想**项目级补充而非覆盖**：

```text
全局 ~/.skills/creative/ui-ux-pro-max/
项目 <repo>/.opencode/skills/ersbyai-ui-ux/   ← 不同名，作为补充
```

推荐后者，避免歧义。

---

## 路线图

- [x] 中央仓库目录结构
- [x] 三个管理 skill (install / link / audit)
- [x] OpenCode 全局自举
- [ ] 集成测试（end-to-end install -> link -> audit -> unlink）
- [ ] 项目级 skill 模板（`tools/new-project-skill/`）
- [ ] 版本/更新流程（从远端 pull 最新）

---

*Last updated: 2026 — Windows 11 + OpenCode + Claude Code*
