[根目录](../CLAUDE.md) > **shared**

---

# Shared Module - Cross-Cutting Utilities

> **Module:** `shared/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented shared utilities expanded in v0.3.0

---

## 模块职责

The `shared/` module provides **cross-cutting utilities** used across all modules.

**Core Responsibilities:**
- **Chat Manager** - Session and conversation management
- **Filesystem** - File operation helpers
- **Hooks** - Lifecycle extension points
- **Schemas** - Reusable data models
- **Security** - Path and argument validation
- **Tools** - Common tool utilities

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `ChatManager` | `shared/chat/chat_manager.py` | Chat management |
| `PolicyManager` | `shared/security/policy.py` | Security policies |
| `SkillConfig` | `shared/schema/skill_config.py` | Skill configuration |

---

## 对外接口

### ChatManager API

```python
class ChatManager:
    @classmethod
    async def create_session(cls, title: str) -> SessionInfo:
        """Create new session"""

    @classmethod
    async def create_conversation(
        cls,
        session_id: str,
        role: str,
        content: str,
        **kwargs
    ) -> str:
        """Create conversation message"""

    @classmethod
    async def get_conversation_history(
        cls,
        session_id: str,
        limit: int = 100
    ) -> list[dict]:
        """Get conversation history"""
```

### PolicyManager API

```python
class PolicyManager:
    def validate_path(self, path: Path) -> PolicyResult:
        """Validate path security"""

    def validate_args(self, args: dict, schema: dict) -> PolicyResult:
        """Validate arguments against schema"""
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `middleware/` | Config, storage |

---

## 数据模型

### SkillConfig

```python
class SkillConfig(BaseModel):
    skills_dir: Path
    execution: SkillExecutionConfig
    retrieval: SkillRetrievalConfig
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/shared/`
- **Framework:** `pytest` + `pytest-asyncio`

---

## 常见问题 (FAQ)

### Q: How do I add a custom hook?
A: Implement the hook interface and register it via the hooks system.

---

## 相关文件清单

### Chat
- `shared/chat/chat_manager.py` - ChatManager
- `shared/chat/models.py` - Chat models

### Filesystem
- `shared/fs/helpers.py` - File helpers

### Hooks
- `shared/hooks/lifecycle.py` - Lifecycle hooks

### Schemas
- `shared/schema/skill_config.py` - Skill config
- `shared/schema/common.py` - Common schemas

### Security
- `shared/security/policy.py` - Policy manager
- `shared/security/path_validator.py` - Path validation

### Tools
- `shared/tools/dispatcher.py` - Tool dispatcher
- `shared/tools/helpers.py` - Tool helpers

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
