[根目录](../CLAUDE.md) > **daemon**

---

# Daemon Module - Background Services

> **Module:** `daemon/`
> **Version:** 0.3.0 (New in v0.3.0)
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented agent profile evolver and dream loop (v0.3.0)

---

## 模块职责

The `daemon/` module provides **background services** that run independently of the main agent loop.

**Core Responsibilities:**
- **Agent Profile Evolver** - Periodically refines agent soul and user profiles
- **Dream Loop** - Consolidates recent experiences into long-term memory
- **Background Tasks** - Async task scheduling and execution

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `AgentProfileEvolverDaemon` | `daemon/agent_profile/` | Profile evolver |
| `DreamDaemon` | `daemon/dream/` | Dream loop |

### Initialization

```python
# Started automatically by bootstrap.py if enabled
from daemon.agent_profile import AgentProfileEvolverDaemon
from daemon.dream import DreamDaemon

# Agent Profile Evolver
AgentProfileEvolverDaemon.start()

# Dream Daemon
DreamDaemon.start(config=dream_config)
```

---

## 对外接口

### AgentProfileEvolverDaemon

```python
class AgentProfileEvolverDaemon:
    @classmethod
    def start(cls) -> None:
        """Start the evolver daemon"""

    async def evolve_soul(self) -> None:
        """Evolve agent soul profile"""

    async def evolve_user(self, user_id: str) -> None:
        """Evolve user profile"""
```

### DreamDaemon

```python
class DreamDaemon:
    @classmethod
    def start(cls, config: DreamConfig) -> None:
        """Start dream daemon"""

    async def consolidate(self) -> None:
        """Consolidate recent experiences"""
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `core/` | Agent profiles |
| `infra/` | Memory, compaction |
| `middleware/` | Config, storage |

### Configuration

```python
# Dream Config
DreamConfig(
    enabled=True,
    interval_seconds=3600  # Run every hour
)

# Memory Config
MemoryConfig(
    enabled=True,
    poll_interval_seconds=300  # Check every 5 minutes
)
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/daemon/`
- **Framework:** `pytest` + `pytest-asyncio`

---

## 常见问题 (FAQ)

### Q: When do daemons run?
A: Daemons run in the background at configured intervals, independent of agent sessions.

### Q: How do I disable daemons?
A: Set `dream.enabled=False` or `memory.enabled=False` in config.

---

## 相关文件清单

### Agent Profile Evolver
- `daemon/agent_profile/orchestrator.py` - Evolver orchestrator
- `daemon/agent_profile/soul_evolver.py` - Soul evolution
- `daemon/agent_profile/user_evolver.py` - User evolution

### Dream Loop
- `daemon/dream/loop.py` - Dream loop
- `daemon/dream/consolidator.py` - Experience consolidation

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
