# 数据表结构优化分析

## 1. 当前表结构概述

项目使用 SQLite + SQLAlchemy ORM，共有 3 张表：

### sessions - 会话表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) PK | UUID 主键 |
| title | String(255) | 会话标题 |
| description | Text | 会话描述 |
| status | String(32) | 状态：active/paused/completed/archived |
| meta_info | JSON | 模型配置、标签等元数据 |
| conversation_count | Integer | 对话轮数（冗余） |
| total_tokens | Integer | 总 token 消耗（冗余） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### conversations - 对话表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) PK | UUID 主键 |
| session_id | String(36) FK | 关联 sessions.id |
| sequence | Integer | 在会话中的序号 |
| role | String(32) | user/assistant/system/tool |
| title | String(255) | 内容预览 |
| content | Text | 文本内容 |
| content_detail | JSON | 详细内容（工具调用参数、多模态等） |
| tool_calls | JSON | 工具调用列表（OpenAI 格式） |
| tool_call_id | String(64) | 关联的工具调用 ID |
| tokens | Integer | 本对话 token 数（冗余） |
| meta_info | JSON | token数、模型、耗时、成本等 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### skills - 技能表（无优化建议）

---

## 2. 存在的问题

### 2.1 字段冗余

| 冗余位置 | 说明 |
|---------|------|
| `Conversation.tokens` + `meta_info['tokens']` | token 数存了两份，实际使用时可能不一致 |
| `Session.conversation_count` + `Session.total_tokens` | 每次对话都会更新这两个字段，但可从 conversations 表 COUNT/SUM 计算得出 |

### 2.2 JSON 字段过多，查询不友好

`conversations` 表有 3 个 JSON 字段：
- `meta_info` — 存 token、模型、耗时、成本
- `content_detail` — 存工具调用参数、多模态内容
- `tool_calls` — 存 OpenAI 格式工具调用

**缺点**：难以做 SQL 层面的统计分析（如按模型分组统计 token 消耗、按耗时区间分布等）。

### 2.3 可能的过度设计

`title` 字段每个 conversation 都存，但实际上：
- 侧边栏展示可以用 `content` 前 N 个字符替代
- 或者只需为 `role=user` 的对话存 title

---

## 3. 优化方案 A（推荐）

**原则**：保留 JSON 字段的灵活性，删除冗余字段，将高频统计字段提取为独立列。

### 3.1 删除冗余字段

```python
# Conversation 表
# 删除 tokens 字段，保留 meta_info['tokens']
# 或反过来，删除 meta_info['tokens']，保留 tokens 字段（推荐，见 3.2）

# Session 表
# 删除 conversation_count 和 total_tokens
# 改用服务层按需计算，或创建数据库视图
```

### 3.2 将 meta_info 中的高频统计字段提取为独立列

```python
class Conversation(Base):
    """对话表 - 优化版"""

    __tablename__ = "conversations"

    # 主键、外键、序列号（保留）
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    # 角色、内容（保留）
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 标题优化：可为 NULL，使用时取 content 前 N 字符
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 统计字段（从 meta_info 提取为独立列）
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 工具调用（保留 JSON，但简化结构）
    tool_calls: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # 详细内容（保留 JSON，用于复杂结构）
    content_detail: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # 简化后的 meta_info（仅存额外上下文）
    meta_info: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )

    # 时间戳（保留）
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
```

### 3.3 Session 表优化

```python
class Session(Base):
    """会话表 - 优化版"""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=SessionStatus.ACTIVE.value, nullable=False)

    # 删除 conversation_count 和 total_tokens
    # 如需统计，的使用时通过 SQL 计算：
    # SELECT COUNT(*), SUM(tokens) FROM conversations WHERE session_id = ?

    # 元数据（简化，仅存真正需要扩展的信息）
    meta_info: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: DateTime = mapped_column(DateTime, nullable=False)

    # 删除索引 idx_session_updated（如果不需要按更新时间排序查询）
    __table_args__ = (
        Index("idx_session_status", "status"),
        Index("idx_session_created", "created_at"),
    )
```

### 3.4 数据库视图（可选）

如果需要经常查询 conversation_count 和 total_tokens，可以创建视图：

```sql
CREATE VIEW session_stats AS
SELECT
    session_id,
    COUNT(*) as conversation_count,
    COALESCE(SUM(tokens), 0) as total_tokens
FROM conversations
GROUP BY session_id;
```

---

## 4. 改动范围

| 改动项 | 影响 |
|-------|------|
| 删除 `Conversation.tokens` | 需确认所有读取该字段的地方改用 `meta_info['tokens']` |
| 删除 `Session.conversation_count` | 需确认侧边栏等展示位置的查询逻辑 |
| 删除 `Session.total_tokens` | 同上 |
| 新增 `model_name`, `latency_ms` 列 | 向后兼容，老数据这些字段为 NULL |
| `Conversation.title` 改为 nullable | 需处理 NULL 情况的显示逻辑 |

---

## 5. 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| 历史数据迁移 | 中 | 使用 Alembic 迁移，保留回滚脚本 |
| 代码改动点分散 | 低 | grep 搜索所有使用这些字段的地方 |
| JSON 字段仍难以统计分析 | 低 | 已有独立列可满足基本统计需求 |

---

## 6. 待确认事项

1. `Conversation.tokens` 和 `meta_info['tokens']` 以哪个为准？
2. 是否需要保留 `Session.conversation_count` 和 `Session.total_tokens` 的实时更新（性能 vs 一致性）？
3. `Conversation.title` 是否确实需要？可以考虑只在 `role=user` 时生成 title。