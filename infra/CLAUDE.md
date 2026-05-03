[根目录](../CLAUDE.md) > **infra**

---

# Infra Module - Infrastructure Layer

> **Module:** `infra/`
> **Version:** 0.3.0 (New in v0.3.0)
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented memory, context, and compaction infrastructure

---

## 模块职责

The `infra/` module provides **infrastructure services** isolated from core agent logic, enabling independent evolution.

**Core Responsibilities:**
- **Memory** - Long-term and session memory implementations
- **Context** - Pluggable context providers for agent execution
- **Compaction** - Context summarization pipeline for long conversations
- **Service** - InfraService entry point wiring all services together

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `InfraService` | `infra/service.py` | Infrastructure service entry |
| `MemoryProvider` | `infra/memory/providers/` | Memory implementations |
| `ContextProvider` | `infra/context/providers/` | Context providers |

### Initialization Flow

```python
# 1. Initialize InfraService (called by bootstrap.py)
from infra.service import InfraService, InfraContextConfig
infra = InfraService(config=InfraContextConfig(...))
await infra.initialize()

# 2. Use Memory
memory = infra.get_memory_provider()
await memory.write(key="session:123", value="...")

# 3. Use Context
context = infra.get_context_provider()
ctx = await context.build_context(session_id="123")
```

---

## 对外接口

### InfraService API

```python
class InfraService:
    async def initialize(self) -> None:
        """Initialize all infrastructure services"""

    def get_memory_provider(self) -> MemoryProvider:
        """Get configured memory provider"""

    def get_context_provider(self) -> ContextProvider:
        """Get configured context provider"""

    def get_compaction_engine(self) -> CompactionEngine:
        """Get context compaction engine"""
```

### MemoryProvider API

```python
class MemoryProvider(Protocol):
    async def read(self, key: str) -> Any | None:
        """Read from memory"""

    async def write(self, key: str, value: Any) -> None:
        """Write to memory"""

    async def delete(self, key: str) -> None:
        """Delete from memory"""

    async def search(self, query: str, top_k: int = 5) -> list[MemoryResult]:
        """Search memory"""
```

### ContextProvider API

```python
class ContextProvider(Protocol):
    async def build_context(
        self,
        session_id: str,
        max_tokens: int = 8000
    ) -> ContextBlock:
        """Build context block for agent"""
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `middleware/` | Config, storage |
| `shared/` | Schemas, utilities |

### Configuration

```python
# Memory Config (from GlobalConfig)
MemoryConfig(
    enabled=True,
    provider="sqlite",  # or "vector"
    min_staging_sessions=5,
    min_staging_bytes=1024
)

# Context Config
ContextConfig(
    max_tokens=8000,
    providers=["history", "memory", "profile"]
)
```

---

## 数据模型

### ContextBlock

```python
@dataclass
class ContextBlock:
    content: str
    tokens: int
    metadata: dict[str, Any]
    sources: list[str]
```

### MemoryResult

```python
@dataclass
class MemoryResult:
    key: str
    value: Any
    score: float
    metadata: dict[str, Any]
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/infra/`
- **Framework:** `pytest` + `pytest-asyncio`

---

## 常见问题 (FAQ)

### Q: What's the difference between memory and context?
A: Memory is persistent storage (long-term), while context is transient information prepared for each agent execution.

### Q: How does compaction work?
A: When context exceeds token limits, the compaction engine summarizes older messages while preserving key information.

---

## 相关文件清单

### Memory
- `infra/memory/providers/sqlite_memory.py` - SQLite-based memory
- `infra/memory/providers/vector_memory.py` - Vector-based memory

### Context
- `infra/context/providers/history_provider.py` - Conversation history
- `infra/context/providers/memory_provider.py` - Memory context
- `infra/context/providers/profile_provider.py` - Agent profile context

### Compaction
- `infra/compact/strategies/` - Summarization strategies
- `infra/compact/storage.py` - Compaction storage

### Service
- `infra/service.py` - InfraService entry point
- `infra/shared/` - Shared utilities

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
