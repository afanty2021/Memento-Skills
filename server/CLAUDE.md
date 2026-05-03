[根目录](../CLAUDE.md) > **server**

---

# Server Module - Endpoint Services

> **Module:** `server/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:30:00Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Enhanced Documentation
- Added HTTP API endpoint documentation
- Added IM endpoint service configuration details
- Added deployment examples
- Added API usage examples

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation

---

## 模块职责

The `server/` module provides **HTTP and endpoint services** for external integrations including GUI, IM platforms, and API clients.

**Core Responsibilities:**
- **IM Endpoint Service** - Unified IM channel management and lifecycle
- **HTTP API Server** - REST API for GUI and external clients
- **Gateway Mode** - Long-running server for IM platform bridges

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `EndpointService` | `server/endpoint/im/__init__.py` | IM endpoint service |
| `HTTP API Server` | `server/api/` | REST API server |

### Starting the Server

```bash
# Start IM endpoint service (via CLI)
memento feishu start
memento dingtalk start
memento wecom start

# Or start gateway mode (all platforms)
memento gateway start

# HTTP API server starts automatically with GUI
memento-gui
# API available at http://127.0.0.1:18765
```

---

## 对外接口

### HTTP API Endpoints

The HTTP API server provides REST endpoints for GUI and external clients.

#### Base URL
```
http://127.0.0.1:18765/api/v1
```

#### Authentication

Most endpoints require Bearer token authentication:

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

#### Available Endpoints

##### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agent/chat` | Send message to agent (streaming) |
| `POST` | `/agent/chat/completions` | Non-streaming chat completion |
| `GET` | `/agent/sessions` | List all sessions |
| `POST` | `/agent/sessions` | Create new session |
| `GET` | `/agent/sessions/{id}` | Get session details |
| `DELETE` | `/agent/sessions/{id}` | Delete session |

**Example: Chat Completion**
```python
import httpx

async def chat_with_agent(message: str, session_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:18765/api/v1/agent/chat",
            json={
                "message": message,
                "session_id": session_id,
                "stream": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        async for chunk in response.aiter_text():
            print(chunk, end="")
```

##### Skill Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/skills` | List all available skills |
| `GET` | `/skills/{name}` | Get skill details |
| `POST` | `/skills/{name}/execute` | Execute a skill |
| `GET` | `/skills/market` | Browse skill market |
| `POST` | `/skills/market/install` | Install skill from market |

**Example: Execute Skill**
```python
response = await client.post(
    "http://127.0.0.1:18765/api/v1/skills/filesystem/execute",
    json={
        "operation": "read",
        "path": "/path/to/file.txt"
    },
    headers={"Authorization": f"Bearer {token}"}
)
result = response.json()
```

##### Configuration Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/config` | Get current configuration |
| `PUT` | `/config` | Update configuration |
| `GET` | `/config/schema` | Get configuration schema |

##### Session Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sessions` | List all sessions |
| `POST` | `/sessions` | Create new session |
| `GET` | `/sessions/{id}` | Get session details |
| `DELETE` | `/sessions/{id}` | Delete session |
| `GET` | `/sessions/{id}/conversations` | Get conversation history |

### IM Endpoint Service

#### EndpointService Interface

```python
class EndpointService:
    def start_in_background(self) -> None:
        """Start service in background thread"""

    async def start_channel(
        self,
        account_id: str,
        channel_type: ChannelType,
        credentials: dict,
        mode: ConnectionMode
    ) -> None:
        """Start an IM channel

        Args:
            account_id: Unique account identifier
            channel_type: Channel type (FEISHU, DINGTALK, WECOM, WECHAT)
            credentials: Platform credentials (app_id, app_secret, etc.)
            mode: Connection mode (POLLING, WEBSOCKET)
        """

    async def stop_channel(self, account_id: str) -> None:
        """Stop an IM channel"""

    async def get_channel_status(self, account_id: str) -> ChannelStatus:
        """Get channel status"""
```

#### Channel Configuration

##### Feishu Configuration

```yaml
im:
  feishu:
    enabled: true
    app_id: "cli_xxx"
    app_secret: "xxx"
    encrypt_key: "xxx"  # Optional
    verification_token: "xxx"  # Optional
    mode: "websocket"  # or "polling"
    port: 8080
```

##### DingTalk Configuration

```yaml
im:
  dingtalk:
    enabled: true
    app_key: "xxx"
    app_secret: "xxx"
    mode: "websocket"
    port: 8081
```

##### WeCom Configuration

```yaml
im:
  wecom:
    enabled: true
    corp_id: "xxx"
    agent_id: 1000001
    secret: "xxx"
    token: "xxx"
    encoding_aes_key: "xxx"
    mode: "websocket"
    port: 8082
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `im/` | IM platform integrations |
| `core/` | Agent framework |
| `middleware/` | Config, storage |

### Configuration

Server configuration is managed through `middleware/config/`:

```python
# Server Config
ServerConfig(
    host="127.0.0.1",
    port=18765,
    debug=False,
    cors_enabled=True
)

# IM Endpoint Config
IMEndpointConfig(
    feishu=FeishuConfig(
        app_id="cli_xxx",
        app_secret="xxx",
        mode="websocket"
    ),
    dingtalk=DingTalkConfig(
        app_key="xxx",
        app_secret="xxx"
    )
)
```

---

## 部署示例

### Development Deployment

```bash
# Start HTTP API server with GUI
memento-gui

# Start individual IM bridges
memento feishu start
memento dingtalk start
memento wecom start
```

### Production Deployment

#### Using systemd (Linux)

```ini
# /etc/systemd/system/memento-api.service
[Unit]
Description=Memento HTTP API Server
After=network.target

[Service]
Type=simple
User=memento
WorkingDirectory=/opt/memento-skills
Environment="PATH=/opt/memento-skills/.venv/bin"
ExecStart=/opt/memento-skills/.venv/bin/memento-gui
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable memento-api
sudo systemctl start memento-api
sudo systemctl status memento-api
```

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

EXPOSE 18765

CMD ["memento-gui"]
```

```bash
# Build and run
docker build -t memento-skills .
docker run -d -p 18765:18765 --name memento-api memento-skills
```

#### Docker Compose

```yaml
version: '3.8'

services:
  memento-api:
    build: .
    ports:
      - "18765:18765"
    environment:
      - LOG_LEVEL=INFO
      - LLM_API_KEY=${LLM_API_KEY}
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    restart: always

  memento-feishu:
    build: .
    command: memento feishu start
    environment:
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
    restart: always
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/server/`
- **Framework:** `pytest` + `pytest-asyncio`
- **Coverage:** Minimal

### Running Tests

```bash
# Run server tests
pytest tests/server/

# Test specific endpoint
pytest tests/server/test_api.py::test_chat_endpoint
```

---

## 常见问题 (FAQ)

### Q: How do I access the HTTP API?
A: The API server runs on `http://127.0.0.1:18765` by default when using `memento-gui`.

### Q: How do I configure IM platforms?
A: Add platform credentials to your config file under the `im:` section, then start the platform bridge.

### Q: Can I run multiple IM platforms simultaneously?
A: Yes, each platform runs on a separate port. Use `memento gateway start` to run all enabled platforms.

### Q: How do I secure the HTTP API in production?
A: Use reverse proxy (nginx) with SSL/TLS, enable authentication tokens, and restrict access to trusted networks.

---

## 相关文件清单

### Endpoints
- `server/endpoint/im/` - IM endpoint service
- `server/endpoint/im/__init__.py` - EndpointService implementation

### HTTP API
- `server/api/` - HTTP API endpoints
- `server/api/agent.py` - Agent endpoints
- `server/api/skills.py` - Skill endpoints
- `server/api/config.py` - Configuration endpoints
- `server/api/sessions.py` - Session endpoints

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
