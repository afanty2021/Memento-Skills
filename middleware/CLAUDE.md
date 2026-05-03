[根目录](../CLAUDE.md) > **middleware**

---

# Middleware Module - Platform Services

> **Module:** `middleware/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented Config v2 three-layer architecture
- Mapped LLM client, storage, IM platform, and sandbox components

---

## 模块职责

The `middleware/` module provides **platform-level services** that support the core agent framework.

**Core Responsibilities:**
- **Configuration v2** - Three-layer isolation (System/User/Runtime) with auto-migration
- **LLM Client** - Multi-provider LLM access via litellm
- **Storage** - SQLite + SQLAlchemy + vector storage
- **IM Platform** - Feishu, DingTalk, WeCom, WeChat integration
- **Sandbox** - UV-based isolated execution environment
- **Utilities** - Environment detection, path security

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `ConfigManager` | `config/config_manager.py` | Configuration management |
| `LLMClient` | `llm/llm_client.py` | LLM client |
| `DatabaseManager` | `storage/core/engine.py` | Database engine |
| `UVSandbox` | `sandbox/uv_sandbox.py` | UV sandbox |

### Initialization Flow

```python
# 1. Config (bootstrap.py)
from middleware.config import g_config
config = g_config.load()

# 2. LLM Client
from middleware.llm import LLMClient
llm = LLMClient()

# 3. Database
from middleware.storage.core import get_db_manager
db = await get_db_manager()

# 4. Sandbox
from middleware.sandbox import UVSandbox
sandbox = UVSandbox()
```

---

## 对外接口

### ConfigManager API

```python
class ConfigManager:
    def load(self) -> GlobalConfig:
        """Load and merge system + user config"""

    def set(self, key: str, value: Any) -> None:
        """Update user config (triggers re-merge)"""

    def save(self) -> None:
        """Persist user config to disk"""

    def get_db_url(self) -> str:
        """Get database connection URL"""

    def get_skills_path(self) -> Path:
        """Get skills directory path"""
```

### LLMClient API

```python
class LLMClient:
    async def chat_completion(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Non-streaming chat completion"""

    async def stream_chat(
        self,
        messages: list[Message],
        **kwargs
    ) -> AsyncGenerator[ChatChunk, None]:
        """Streaming chat completion"""

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for a text"""
```

### DatabaseManager API

```python
class DatabaseManager:
    @property
    def engine(self) -> AsyncEngine:
        """SQLAlchemy async engine"""

    async def create_session(self) -> AsyncSession:
        """Create database session"""

    async def execute(self, stmt: Statement) -> Result:
        """Execute SQL statement"""
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `shared/` | Schemas, path management |
| `sqlalchemy` | ORM |
| `aiosqlite` | Async SQLite driver |
| `litellm` | Multi-provider LLM client |
| `alembic` | Database migrations |

### Configuration Files

```python
# System Config (middleware/config/system_config.json)
# Read-only, shipped with codebase

# User Config (~/memento_s/config.json)
{
  "llm": {
    "active_profile": "default",
    "profiles": {
      "default": {
        "model": "openai/gpt-4o",
        "api_key": "sk-...",
        "base_url": "https://api.openai.com/v1"
      }
    }
  },
  "skills": {
    "execution": {
      "sandbox_provider": "uv"
    }
  }
}

# MCP Config (~/memento_s/mcp_config.json)
{
  "mcpServers": {
    "filesystem": {...}
  }
}
```

---

## 数据模型

### GlobalConfig (Pydantic)

```python
class GlobalConfig(BaseModel):
    version: str
    llm: LLMConfig
    paths: PathConfig
    skills: SkillConfig
    logging: LoggingConfig
    memory: MemoryConfig
    dream: DreamConfig
    gateway: GatewayConfig
    im: IMConfig
```

### Database Models (SQLAlchemy)

```python
# Session
class Session(Base):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

# Conversation
class Conversation(Base):
    id: str
    session_id: str
    role: str  # "user", "assistant", "tool"
    content: str
    tokens: int
    created_at: datetime

# Skill
class Skill(Base):
    name: str
    version: str
    description: str
    manifest: dict
    utility_score: float
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/middleware/`
- **Framework:** `pytest` + `pytest-asyncio`
- **Coverage:** Comprehensive

### Key Test Files

| Test File | Coverage |
|-----------|----------|
| `tests/middleware/test_config.py` | Config management |
| `tests/middleware/test_llm_client.py` | LLM client |
| `tests/middleware/test_storage.py` | Database operations |
| `tests/middleware/test_sandbox.py` | Sandbox execution |

---

## 常见问题 (FAQ)

### Q: How does config auto-migration work?
A: When the config template updates, the system detects new fields and merges them into user config while preserving `x-managed-by: user` fields.

### Q: Which LLM providers are supported?
A: Any provider supported by litellm: OpenAI, Anthropic, Azure, Google, Ollama, vLLM, Kimi, MiniMax, GLM, etc.

### Q: How do I add a new database migration?
A: Create a new migration in `middleware/storage/migrations/versions/` using Alembic.

### Q: What's the difference between UVSandbox and local execution?
A: UVSandbox creates an isolated environment with separate dependencies, while local execution uses the system Python environment.

---

## 相关文件清单

### Configuration
- `middleware/config/config_manager.py` - ConfigManager
- `middleware/config/bootstrap.py` - Config initialization
- `middleware/config/migrations/` - Config migrations
- `middleware/config/schemas/` - Pydantic models
- `middleware/config/mcp_config_manager.py` - MCP config

### LLM
- `middleware/llm/llm_client.py` - LLMClient
- `middleware/llm/litellm_client.py` - LiteLLM wrapper

### Storage
- `middleware/storage/core/engine.py` - DatabaseManager
- `middleware/storage/models/` - SQLAlchemy models
- `middleware/storage/migrations/` - Alembic migrations
- `middleware/storage/vector/` - Vector storage

### IM Platform
- `middleware/im/gateway/` - Gateway infrastructure
- `middleware/im/feishu/` - Feishu integration
- `middleware/im/dingtalk/` - DingTalk integration
- `middleware/im/wecom/` - WeCom integration

### Sandbox
- `middleware/sandbox/uv_sandbox.py` - UV sandbox
- `middleware/sandbox/local_executor.py` - Local executor

### Utils
- `middleware/utils/env.py` - Environment detection
- `middleware/utils/path_security.py` - Path validation

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
