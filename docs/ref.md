## 1.执行环境
* 文件系统使用host的文件系统
* python使用独立的uv环境
* node依赖host环境
* 权限控制：写 -> 询问，读 -> 放行。 安全规则检测

## 2. memory / context

## 3. skill部分
* 以skill centric
* 工具集通过 tools/ 显式注册，skill 映射到具体的工具，连接更紧密
* allowed-tools是cc的标准，因为我们的tool和cc没有完全一一对应，所以这个不需要。代码中去掉
* OpenHarness的Skill 工具是只读的，不做执行映射
* Claude Code：Skill 是纯提示词，AI 自由选择工具

### 1. skill的可见范围
Claude Code 的 skill 文件位置决定可见范围：

Enterprise managed	托管设置	全组织
Personal	~/.claude/skills/	所有项目
Project	.claude/skills/	当前项目

我们要有skill可见范围限制

### 2. todo
* skill 生成，应该如何处理？生成路径，生成后是否导入到skill.json中？


## 差异化
* skill的创建能力
* skill的进化能力

## 待优化项（与 OpenHarness / learn-claude-code 对比）

以下为后续单独优化的功能模块。

### 1. 多 Agent 协作

**定位：** `core/skill/execution/agent.py` 作为底层执行 agent（sub agent），上层 `core/memento_s/agent.py` 是 planner，后续支持多 agent swarm。

OpenHarness `swarm/in_process.py`、learn-claude-code s09、s12。

**Phase 1（短期）：Subagent 模式**
- 在 `SkillAgent` 中支持 spawn 隔离上下文的 subagent
- 用于并行探索（类似 learn-claude-code s04）

**Phase 2（中期）：MessageBus + TeammateManager**
- JSONL inbox per teammate（drain-on-read 模式）
- Daemon thread 管理 idle/working/shutdown 状态机
- `shutdown_request` / `plan_approval` 协作协议工具

**Phase 3（长期）：WorktreeManager + 多后端**
- Git worktree 隔离并行任务
- 类似 OpenHarness 多后端支持（in-process / subprocess / tmux）

### 2. 权限系统增强

OpenHarness `PathRule`、`BaseTool.is_read_only()`。

**待实现：**
- `check_api_keys` 扩展为正则模式匹配（当前仅匹配含 "KEY" 的环境变量）
- 路径级 glob 规则（用户配置的 `PathRule`）
- 工具级 `is_read_only()` 接口（各工具声明是否只读）
- 权限模式（FULL_AUTO / PLAN / DEFAULT）为不同场景提供不同粒度

### 3. API Client 重试增强（已完整实现）

`middleware/llm/llm_client.py` 已完整实现：
- RetryConfig（指数退避 + 熔断器）
- CircuitBreaker（CLOSE/OPEN/HALF_OPEN 状态机）
- Retry-After header 支持
- Raw token 自愈层

无需额外优化。

### 4. 安全沙箱增强

**已有实现：** PathBoundary（3层危险命令检测）、PolicyManager（速率限制）、UV Sandbox（venv 隔离）、Node Sandbox（NODE_PATH 隔离）。

**待实现：**
- Bash PATH 收紧（跨平台：Unix 移除 `/usr/local/bin` 等，Windows 移除 `C:\Users` 等不安全路径）
- timeout 配置化（通过 `tool_props.timeout` 传入）
- `allow_roots` 配置激活（多 workspace 支持）
- 容器级沙箱（cgroup v2 / Docker，长期路线）

### 5. 上下文压缩（SkillAgent ReAct Loop）

**定位：** 在 `core/skill/execution/state.py` 中独立实现，纯内存操作，**不依赖** `core/context/compaction.py`（后者为外层 agent / Runner 专用）。

**待实现：**
- Layer 1 (microcompact)：每 turn 保留最近 3 个 tool results，其余替换为 `[Previous: used {tool_name}]`
- Layer 2 (auto_compact)：token 超阈值时用 LLM summarization，替换整个历史为一条摘要消息
- 集成到 `SkillAgent` 的 ReAct loop 中

### 6. Hook 生命周期系统

**定位：** 在 `core/skill/execution/hooks/` 新建 HookExecutor，作为 SkillAgent / SkillDispatcher 层的细粒度生命周期控制。

**待实现：**
- `HookEvent` 枚举：`BEFORE_TOOL_EXEC`、`AFTER_TOOL_EXEC`、`BEFORE_SKILL_EXEC`、`AFTER_SKILL_EXEC`
- `HookExecutor` 执行器（支持 CommandHook / HttpHook / PromptHook）
- 注入点：`adapter.py`（tool 执行前后）、`skill_dispatcher.py`（skill 执行前后）
* 