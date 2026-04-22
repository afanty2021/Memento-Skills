# Memento-S API 服务清单

本文档列出将后端转换为 HTTP API 服务所需的接口。

## 一、API 服务清单

### 1. 会话管理 API (Session)

实际路由前缀：`/api/v1/chat`

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 列出会话 | GET | `/api/v1/chat/sessions` | 列出最近会话（`?limit=20`） |
| 创建会话 | POST | `/api/v1/chat/sessions` | 创建新会话 |
| 获取会话 | GET | `/api/v1/chat/sessions/{session_id}` | 获取指定会话 |
| 更新会话 | PATCH | `/api/v1/chat/sessions/{session_id}` | 重命名会话 |
| 删除会话 | DELETE | `/api/v1/chat/sessions/{session_id}` | 删除会话（级联删除消息） |
| 会话统计 | GET | `/api/v1/chat/sessions/{session_id}/stats` | 消息数、Token、当前模型等 |
| 获取消息列表 | GET | `/api/v1/chat/sessions/{session_id}/messages` | 获取会话消息（`?limit=100`） |
| 获取 run 摘要 | GET | `/api/v1/chat/sessions/{session_id}/runs` | 获取每次 run 的 intent/plan/反思等元数据（规划中） |

### 2. 对话管理 API (Conversation)

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 创建对话 | POST | `/api/sessions/{session_id}/conversations` | 添加对话消息 |
| 获取对话 | GET | `/api/conversations/{conversation_id}` | 获取指定对话 |
| 更新对话 | PUT | `/api/conversations/{conversation_id}` | 更新对话内容 |
| 删除对话 | DELETE | `/api/conversations/{conversation_id}` | 删除对话 |
| 获取历史 | GET | `/api/sessions/{session_id}/history` | 获取会话对话历史 |

### 3. Agent 对话 API (Core)

实际路由：`POST /api/v1/chat/stream`

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 流式对话 | POST | `/api/v1/chat/stream` | SSE 流式对话，返回 `text/event-stream` |

**请求体：**
```json
{
  "session_id": "xxx",
  "content": "帮我写一个排序算法"
}
```
`session_id` 为 `null` 时自动创建新会话，首条事件为 `SESSION_CREATED`。

**响应事件类型（UniResponse 格式，`exclude_none=true` 序列化）：**

| 事件类型 | 说明 | 关键字段 |
|---------|------|---------|
| `SESSION_CREATED` | 自动创建了新会话 | `session_id` |
| `RUN_STARTED` | Agent 开始运行 | `run_id`, `thread_id` |
| `INTENT_RECOGNIZED` | 意图识别完成 | `status`（mode）, `payload.messages`（task） |
| `PLAN_GENERATED` | 计划生成完成 | `payload.steps`（计��步骤列表） |
| `STEP_STARTED` | 步骤开始 | `step` |
| `STEP_FINISHED` | 步骤结束 | `step`, `status` |
| `TEXT_MESSAGE_START` | 文本流开始 | `event_id`（message_id） |
| `TEXT_MESSAGE_CONTENT` | 文本流片段 | `payload.content`（delta） |
| `TEXT_MESSAGE_END` | 文本流结束 | `event_id`（message_id） |
| `TOOL_CALL_START` | 工具调用开始 | `event_id`（tool_call_id）, `tool_name`, `arguments` |
| `TOOL_CALL_RESULT` | 工具调用结果 | `event_id`（tool_call_id）, `tool_name`, `result` |
| `REFLECTION_RESULT` | 反思阶段结果 | `payload.arguments.decision`, `payload.arguments.reason` |
| `RUN_FINISHED` | 运行结束 | `output_text`, `reason`, `context_tokens`, `conversation_id`, `user_conversation_id` |
| `RUN_ERROR` | 运行出错 | `error` |
| `ERROR` | 流处理异常 | `error`, `code` |

**`RUN_FINISHED` 中的持久化字段说明：**

- `conversation_id`：本次 assistant 消息在数据库中的 Conversation ID
- `user_conversation_id`：对应 user 消息在数据库中的 Conversation ID

这两个字段仅在 `ChatService`（HTTP server 路径）下存在；GUI 路径通过 `conversation_controller` 单独管理。

**`reason` 枚举值：**

| 值 | 含义 |
|----|------|
| `final_answer_generated` | 正常完成 |
| `max_iterations_reached` | 达到最大迭代次数 |
| `execute_skill_failed_too_many` | 工具调用失败次数超限 |
| `execute_skill_abort` | 错误策略中止 |
| `error` | 异常退出 |

### 4. 技能管理 API (Skill)

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 发现技能 | GET | `/api/skills` | 发现可用技能 |
| 搜索技能 | GET | `/api/skills/search` | 搜索技能 |
| 获取技能详情 | GET | `/api/skills/{skill_name}` | 获取技能详情 |
| 执行技能 | POST | `/api/skills/{skill_name}/execute` | 执行技能 |
| 安装技能 | POST | `/api/skills/{skill_name}/install` | 安装云端技能 |
| 卸载技能 | DELETE | `/api/skills/{skill_name}` | 卸载技能 |

**执行技能请求体示例:**
```json
{
  "params": {
    "file_path": "/path/to/file",
    "option": "value"
  },
  "session_id": "xxx"
}
```

### 5. 配置管理 API (Config)

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 获取配置 | GET | `/api/config` | 获取全部配置 |
| 获取配置项 | GET | `/api/config/{key_path}` | 获取指定配置项 |
| 设置配置项 | PUT | `/api/config/{key_path}` | 设置配置项 |
| 保存配置 | POST | `/api/config/save` | 保存配置到磁盘 |
| 重置配置 | POST | `/api/config/reset` | 重置为默认配置 |
| 重新加载 | POST | `/api/config/reload` | 从磁盘重新加载 |

### 6. LLM 管理 API

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 获取当前模型 | GET | `/api/llm/model` | 获取当前使用的模型 |
| 切换模型 | PUT | `/api/llm/model` | 切换 LLM 模型 |
| 重新加载配置 | POST | `/api/llm/reload` | 重新加载 LLM 配置 |

### 7. IM 网关 API (Gateway)

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 启动服务 | POST | `/api/gateway/start` | 启动 Gateway 服务 |
| 关闭服务 | POST | `/api/gateway/shutdown` | 关闭 Gateway 服务 |
| 获取状态 | GET | `/api/gateway/status` | 获取 Gateway 状态 |

### 8. IM 账户管理 API

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 启动账户 | POST | `/api/accounts` | 启动 IM 账户连接 |
| 停止账户 | DELETE | `/api/accounts/{account_id}` | 停止 IM 账户 |
| 列出账户 | GET | `/api/accounts` | 列出所有账户 |
| 获取账户 | GET | `/api/accounts/{account_id}` | 获取账户信息 |

**启动账户请求体示例:**
```json
{
  "account_id": "feishu_bot_01",
  "channel_type": "feishu",
  "credentials": {
    "app_id": "xxx",
    "app_secret": "xxx"
  },
  "mode": "auto",
  "permission_domain": "all"
}
```

### 9. 向量存储 API

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 保存向量 | POST | `/api/vector` | 保存向量 |
| 加载向量 | GET | `/api/vector/{name}` | 加载向量 |
| 删除向量 | DELETE | `/api/vector/{name}` | 删除向量 |
| 列出向量 | GET | `/api/vector` | 列出所有向量 |
| 搜索向量 | POST | `/api/vector/search` | 向量相似度搜索 |

### 10. 文件管理 API

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 获取数据目录 | GET | `/api/paths/data` | 获取数据目录路径 |
| 获取工作区目录 | GET | `/api/paths/workspace` | 获取工作区路径 |
| 获取日志目录 | GET | `/api/paths/logs` | 获取日志目录路径 |

### 11. 事件订阅 API (WebSocket)

| API | 方法 | 路径 | 功能 |
|-----|------|------|------|
| 事件订阅 | WebSocket | `/ws/events` | 订阅后端事件 |

**事件类型:**
- `IM_SERVICE_STARTED` / `IM_SERVICE_STOPPED`
- `GATEWAY_STARTED` / `GATEWAY_STOPPED`
- `CONFIG_CHANGED`
- `ERROR_OCCURRED`
- `AUTH_REQUIRED`

---

## 二、接口详细定义

### 2.1 Chat API (核心对话)

```
POST /api/v1/chat/stream
Content-Type: application/json

Request:
{
  "session_id": null,
  "content": "帮我写一个排序算法"
}

Response (SSE - text/event-stream，每行格式: data: {...}\n\n):

data: {"type":"SESSION_CREATED","session_id":"a3f8b2c1"}

data: {"type":"RUN_STARTED","run_id":"uuid","thread_id":"a3f8b2c1"}

data: {"type":"INTENT_RECOGNIZED","status":"agentic","payload":{"messages":"写一个排序算法"}}

data: {"type":"PLAN_GENERATED","payload":{"messages":"写一个排序算法","steps":[...]}}

data: {"type":"STEP_STARTED","step":1}

data: {"type":"TOOL_CALL_START","event_id":"call_xxx","tool_name":"execute_skill","arguments":{...}}

data: {"type":"TOOL_CALL_RESULT","event_id":"call_xxx","tool_name":"execute_skill","result":"..."}

data: {"type":"TEXT_MESSAGE_START","event_id":"msg_xxx"}

data: {"type":"TEXT_MESSAGE_CONTENT","event_id":"msg_xxx","payload":{"content":"以下是"}}

data: {"type":"TEXT_MESSAGE_END","event_id":"msg_xxx"}

data: {"type":"STEP_FINISHED","step":1,"status":"done"}

data: {"type":"RUN_FINISHED","output_text":"...","reason":"final_answer_generated",
       "context_tokens":1234,"conversation_id":"uuid-assistant","user_conversation_id":"uuid-user"}
```

### 2.2 WebSocket Chat API

```
WebSocket /ws/chat?session_id=xxx

发送:
{"type": "message", "content": "用户输入"}

接收:
{"type": "RUN_STARTED", "data": {...}}
{"type": "TEXT_MESSAGE_CONTENT", "data": {"content": "响应片段"}}
{"type": "RUN_FINISHED", "data": {...}}
```

---

## 三、认证机制

| 场景 | 方式 |
|------|------|
| 前端认证 | Header: `Authorization: Bearer <token>` |
| IM 渠道认证 | 飞书/钉钉/企微 Webhook 签名验证 |
| 内部服务 | API Key (可在配置中设置) |

---

## 四、错误响应格式

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "错误描述",
    "details": {}
  }
}
```

**常见错误码:**
- `INVALID_REQUEST` - 请求参数错误
- `NOT_FOUND` - 资源不存在
- `UNAUTHORIZED` - 未认证
- `FORBIDDEN` - 无权限
- `INTERNAL_ERROR` - 内部错误
- `SERVICE_UNAVAILABLE` - 服务不可用

---

## 五、技术选型建议

| 组件 | 推荐方案 | 说明 |
|------|---------|------|
| Web 框架 | FastAPI | 异步支持、自动化文档 |
| WebSocket | FastAPI + websockets | 原生支持 |
| SSE | fastapi-eventsource | 简化 SSE 实现 |
| 认证 | JWT | 支持 token 验证 |
| API 文档 | FastAPI Auto Schema | Swagger UI |
| CORS | fastapi.middleware.cors | 跨域支持 |