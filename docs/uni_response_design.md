# 统一响应格式方案：UniResponse

## 一、现状问题

当前前后端协议存在多种不一致的数据格式：

| 场景 | 当前格式 | 问题 |
|------|---------|------|
| Agent 事件流 | `{type, runId, threadId, timestamp, ...payload}` | 字段命名不统一（camelCase vs snake_case） |
| GUI 消息 | `{role, content, conversation_id, timestamp, steps, ...}` | 字段冗余，结构与其他不一致 |
| SSE 错误 | `{type: "error", message}` | 结构与其他不一致 |
| HTTP 响应 | `{success, ...}` 或直接返回数据 | 无统一包装 |
| StreamEvent | `{type, content, step}` | 字段与 AG-UI 不对齐 |

### 现有格式示例

```python
# AG-UI 事件
{"type": "RUN_STARTED", "runId": "xxx", "threadId": "xxx", "timestamp": "..."}

# GUI 消息
{"role": "user", "content": "hello", "conversation_id": "xxx", "timestamp": "...", "steps": 0}

# SSE 错误
{"type": "error", "message": "something went wrong"}

# HTTP 响应
{"success": True}  # 或直接返回数据
```

## 二、设计目标

1. **统一格式** - 所有接口返回使用相同的响应结构
2. **扁平结构** - 单层级字段，减少嵌套复杂度
3. **按需字段** - 非必需字段为 `None`，不产生冗余
4. **向前兼容** - 兼容现有字段命名和用法
5. **可扩展** - 通过 `meta` 字段支持灵活扩展

## 三、UniResponse 定义

### 3.1 类型定义

`type` 字段直接使用 `AGUIEventType` 的值，扩展以下场景：

```python
# 扩展 AGUIEventType（新增非事件类型）
class AGUIEventType(StrEnum):
    # === Agent 阶段事件 ===
    RUN_STARTED = "RUN_STARTED"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"
    INTENT_RECOGNIZED = "INTENT_RECOGNIZED"
    PLAN_GENERATED = "PLAN_GENERATED"
    REFLECTION_RESULT = "REFLECTION_RESULT"
    USER_INPUT_REQUESTED = "USER_INPUT_REQUESTED"
    AWAITING_USER_INPUT = "AWAITING_USER_INPUT"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"

    # === 扩展类型 ===
    ERROR = "ERROR"            # 错误信息
    DATA = "DATA"              # 通用数据响应
    ACK = "ACK"                # 确认消息
```

### 3.2 核心模型

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class UniResponse(BaseModel):
    """统一响应格式（扁平结构）"""

    # === 核心标识 ===
    type: str                                   # 消息类型（AGUIEventType 值）
    trace_id: str | None = None                # 追踪 ID

    # === 时间与会话 ===
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str | None = None             # 会话 ID
    conversation_id: str | None = None        # 对话 ID
    reply_to: str | None = None               # 关联的上一条消息 ID

    # === 消息内容 ===
    role: str | None = None                   # "user" | "assistant" | "system" | "tool"
    content: str | None = None                # 文本内容

    # === 事件标识（统一 event_id）===
    event_id: str | None = None               # 统一事件 ID
                                                # - TOOL_CALL_* 类型时 = tool_call_id
                                                # - TEXT_MESSAGE_* 类型时 = message_id
                                                # - 其他事件时 = 事件唯一标识

    # === 事件相关 ===
    run_id: str | None = None                 # Agent 运行 ID
    thread_id: str | None = None              # 线程 ID
    step: int | None = None                   # 当前步骤
    status: str | None = None                 # 状态
    delta: str | None = None                  # 文本增量（流式）
    tool_name: str | None = None              # 工具名称
    arguments: dict | None = None             # 工具参数
    result: Any | None = None                 # 工具执行结果

    # === 响应相关 ===
    output_text: str | None = None            # 最终输出文本
    reason: str | None = None                 # 结束原因
    steps: int | None = None                  # 总步骤数
    duration_seconds: float | None = None     # 耗时
    model_name: str | None = None             # 使用的模型

    # === Token 用量 ===
    usage: dict | None = None                 # Token 用量信息
    context_tokens: int | None = None         # 上下文 Token 数

    # === 错误相关 ===
    code: str | None = None                   # 错误码
    error: str | None = None                  # 错误信息（兼容旧格式）
    detail: str | None = None                 # 错误详情

    # === 元数据 ===
    meta: dict | None = None                  # 扩展元数据（灵活扩展用）
```

## 四、格式对比

### Before（当前格式混乱）

```python
# AG-UI 事件
{"type": "RUN_STARTED", "runId": "xxx", "threadId": "xxx", "timestamp": "..."}

# GUI 消息
{"role": "user", "content": "hello", "conversation_id": "xxx", "timestamp": "...", "steps": 0}

# SSE 错误
{"type": "error", "message": "something went wrong"}

# HTTP 响应
{"success": True}  # 或直接返回数据
```

### After（统一 UniResponse）

```python
# 事件响应
{
    "type": "RUN_STARTED",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "evt_xxx",
    "run_id": "xxx",
    "thread_id": "xxx"
}

# 文本消息开始
{
    "type": "TEXT_MESSAGE_START",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "msg_xxx",          # message_id
    "run_id": "xxx"
}

# 文本消息内容（流式片段）
{
    "type": "TEXT_MESSAGE_CONTENT",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "msg_xxx",          # 关联到 TEXT_MESSAGE_START
    "delta": "你好",
    "run_id": "xxx"
}

# 工具调用开始
{
    "type": "TOOL_CALL_START",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "call_xxx",         # tool_call_id
    "tool_name": "filesystem",
    "arguments": {"path": "/tmp/test.txt"},
    "run_id": "xxx"
}

# 工具调用结果
{
    "type": "TOOL_CALL_RESULT",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "call_xxx",         # tool_call_id
    "tool_name": "filesystem",
    "result": "file content here",
    "run_id": "xxx"
}

# 运行结束
{
    "type": "RUN_FINISHED",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "evt_xxx",
    "output_text": "最终回复内容",
    "reason": "final_answer_generated",
    "usage": {"total_tokens": 1000},
    "run_id": "xxx"
}

# 错误响应
{
    "type": "ERROR",
    "timestamp": "2026-04-14T12:00:00Z",
    "event_id": "evt_xxx",
    "error": "content is required",
    "code": "VALIDATION_ERROR"
}
```

## 五、类型与字段映射

| type (AGUIEventType) | event_id 语义 | 关键字段 | 说明 |
|----------------------|---------------|---------|------|
| `RUN_STARTED` | 事件 ID | `run_id`, `thread_id` | Agent 开始运行 |
| `STEP_STARTED` | 事件 ID | `step`, `run_id` | 步骤开始 |
| `STEP_FINISHED` | 事件 ID | `step`, `status`, `run_id` | 步骤完成 |
| `TEXT_MESSAGE_START` | message_id | `run_id` | 文本消息开始 |
| `TEXT_MESSAGE_CONTENT` | message_id | `delta`, `run_id` | 文本消息片段（流式） |
| `TEXT_MESSAGE_END` | message_id | `run_id` | 文本消息结束 |
| `TOOL_CALL_START` | tool_call_id | `tool_name`, `arguments`, `run_id` | 工具调用开始 |
| `TOOL_CALL_RESULT` | tool_call_id | `tool_name`, `result`, `run_id` | 工具调用结果 |
| `INTENT_RECOGNIZED` | 事件 ID | `mode`, `run_id` | 意图识别完成 |
| `PLAN_GENERATED` | 事件 ID | `plan`, `run_id` | 计划生成完成 |
| `REFLECTION_RESULT` | 事件 ID | `reflection`, `run_id` | 反思结果 |
| `USER_INPUT_REQUESTED` | 事件 ID | `prompt`, `run_id` | 请求用户输入 |
| `AWAITING_USER_INPUT` | 事件 ID | `run_id` | 等待用户输入 |
| `RUN_FINISHED` | 事件 ID | `output_text`, `reason`, `usage`, `context_tokens`, `run_id` | Agent 运行结束 |
| `RUN_ERROR` | 事件 ID | `error`, `detail` | 运行错误 |
| `ERROR` | 事件 ID | `code`, `error`, `detail` | 通用错误 |
| `DATA` | 事件 ID | `meta` | 通用数据响应 |
| `ACK` | 事件 ID | `meta` | 确认消息 |

## 六、工厂方法

```python
class UniResponse(BaseModel):
    """统一响应格式（扁平结构）"""

    @classmethod
    def run_started(cls, run_id: str, thread_id: str | None = None) -> "UniResponse":
        """RUN_STARTED 事件"""
        return cls(type="RUN_STARTED", run_id=run_id, thread_id=thread_id)

    @classmethod
    def text_content(cls, delta: str, run_id: str) -> "UniResponse":
        """TEXT_MESSAGE_CONTENT 事件（流式文本片段）"""
        return cls(type="TEXT_MESSAGE_CONTENT", delta=delta, run_id=run_id)

    @classmethod
    def tool_call_start(
        cls,
        tool_call_id: str,
        tool_name: str,
        arguments: dict | None = None,
        run_id: str | None = None
    ) -> "UniResponse":
        """TOOL_CALL_START 事件"""
        return cls(
            type="TOOL_CALL_START",
            event_id=tool_call_id,
            tool_name=tool_name,
            arguments=arguments,
            run_id=run_id
        )

    @classmethod
    def tool_call_result(
        cls,
        tool_call_id: str,
        tool_name: str,
        result: Any,
        run_id: str | None = None
    ) -> "UniResponse":
        """TOOL_CALL_RESULT 事件"""
        return cls(
            type="TOOL_CALL_RESULT",
            event_id=tool_call_id,
            tool_name=tool_name,
            result=result,
            run_id=run_id
        )

    @classmethod
    def run_finished(
        cls,
        output_text: str,
        reason: str | None = None,
        usage: dict | None = None,
        run_id: str | None = None
    ) -> "UniResponse":
        """RUN_FINISHED 事件"""
        return cls(
            type="RUN_FINISHED",
            output_text=output_text,
            reason=reason,
            usage=usage,
            run_id=run_id
        )

    @classmethod
    def error(
        cls,
        error: str,
        code: str | None = None,
        detail: str | None = None
    ) -> "UniResponse":
        """错误响应"""
        return cls(type="ERROR", error=error, code=code, detail=detail)

    def to_sse(self) -> str:
        """转换为 SSE 格式"""
        import json
        return f"data: {json.dumps(self.model_dump(mode='json'), ensure_ascii=False)}\n\n"
```

## 七、实现步骤

### 阶段 1：扩展 AGUIEventType 枚举

在 `core/protocol/events.py` 中扩展 `AGUIEventType`，新增 `ERROR`、`DATA`、`ACK` 类型。

### 阶段 2：定义 UniResponse 模型

```
server/schema/uni_response.py  # UniResponse
```

### 阶段 3：创建工厂方法

在 `UniResponse` 类中实现各类型的工厂方法（参考第六节）。

### 阶段 4：逐接口改造

- SSE 流式端点 `/api/v1/chat/stream` → 返回 `UniResponse.to_sse()`
- HTTP REST 接口 → 统一返回 `UniResponse` 实例

### 阶段 5：前端适配

- GUI 统一通过 `UniResponse.type` 判断处理方式
- 根据 `type` 值（如 `RUN_STARTED`、`TEXT_MESSAGE_CONTENT`）触发对应 UI 更新

## 八、优势总结

1. **类型安全** - Pydantic 模型校验，支持自动补全
2. **可追溯** - 统一 `trace_id` 串联请求全链路
3. **易扩展** - 新增类型只需扩展 `AGUIEventType` 枚举
4. **前后端对齐** - `type` 直接使用 AGUIEventType，前端无需额外映射
5. **扁平结构** - 解析简单，无嵌套访问
6. **向后兼容** - 复用现有 AG-UI 事件类型，新增类型最小化
