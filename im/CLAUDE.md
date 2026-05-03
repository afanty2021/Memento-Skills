[根目录](../CLAUDE.md) > **im**

---

# IM Module - Instant Messaging Integration

> **Module:** `im/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented IM platform integrations

---

## 模块职责

The `im/` module provides **instant messaging platform integrations** for Feishu, DingTalk, WeCom, and WeChat.

**Core Responsibilities:**
- **Gateway Mode** - Unified IM gateway for all platforms
- **Feishu Integration** - WebSocket long-connection
- **DingTalk Integration** - Webhook + event subscription
- **WeCom Integration** - Enterprise WeChat
- **WeChat Integration** - Personal WeChat (iLink API)

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `EndpointService` | `server/endpoint/im/` | IM endpoint service |
| `IM Gateway` | `im/gateway/` | Gateway infrastructure |

### Initialization

```python
# Started by bootstrap.py if configured
from server.endpoint.im import EndpointService
from middleware.im.gateway import ChannelType, ConnectionMode

service = EndpointService.get_instance()
await service.start_channel(
    account_id="feishu_main",
    channel_type=ChannelType.FEISHU,
    credentials={...},
    mode=ConnectionMode.WEBSOCKET
)
```

---

## 对外接口

### Supported Platforms

| Platform | Mode | Description |
|----------|------|-------------|
| **Feishu** | WebSocket | Long-connection with per-user sessions |
| **DingTalk** | Webhook | Event subscription |
| **WeCom** | Webhook | Enterprise WeChat |
| **WeChat** | iLink API | Personal WeChat (QR code scan) |

### Configuration

```json
{
  "im": {
    "feishu": {
      "app_id": "cli_...",
      "app_secret": "...",
      "encrypt_key": "...",
      "verification_token": "..."
    },
    "dingtalk": {
      "app_key": "...",
      "app_secret": "..."
    },
    "wecom": {
      "corp_id": "...",
      "agent_id": "..."
    },
    "wechat": {
      "token": "..."
    }
  }
}
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `server/` | Endpoint service |
| `middleware/im/` | IM platform middleware |
| `core/` | Agent framework |

---

## 测试与质量

### Test Structure

- **Location:** `tests/im/`
- **Framework:** `pytest`

---

## 常见问题 (FAQ)

### Q: How do I add a new IM platform?
A: Implement the channel interface in `im/{platform}/` and register it with `EndpointService`.

---

## 相关文件清单

### Gateway
- `im/gateway/` - Gateway infrastructure

### Platforms
- `im/feishu/` - Feishu integration
- `im/dingtalk/` - DingTalk integration
- `im/wecom/` - WeCom integration

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
