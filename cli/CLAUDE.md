[根目录](../CLAUDE.md) > **cli**

---

# CLI Module - Command-Line Interface

> **Module:** `cli/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation

---

## 模块职责

The `cli/` module provides the **Typer-based command-line interface** for Memento-Skills.

**Core Responsibilities:**
- **Interactive Agent** - Terminal-based agent interaction
- **Diagnostics** - Environment and configuration checks
- **Skill Verification** - Skill download, audit, and validation
- **IM Commands** - Feishu, WeChat platform management

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `memento` | `cli/main.py` | Main CLI entry point |

### Commands

```bash
# Interactive agent
memento agent

# Single message
memento agent -m "Hello"

# Diagnostics
memento doctor

# Skill verification
memento verify

# IM platforms
memento feishu
memento wechat

# GUI
memento-gui
```

---

## 对外接口

### CLI Commands

```python
# Main entry
def memento_entry():
    """CLI entry point (pyproject.toml)"""

# Agent commands
@app.command()
def agent(message: str | None = None):
    """Start interactive agent or single message"""

@app.command()
def doctor():
    """Run diagnostics"""

@app.command()
def verify():
    """Verify skills"""
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `core/` | Agent framework |
| `middleware/` | Config, LLM |
| `bootstrap.py` | Initialization |

---

## 测试与质量

### Test Structure

- **Location:** `tests/cli/`
- **Framework:** `pytest` + `cli testing helpers`

---

## 常见问题 (FAQ)

### Q: How do I add a new CLI command?
A: Add a new `@app.command()` decorated function in `cli/main.py` or a separate module in `cli/commands/`.

---

## 相关文件清单

### Core CLI
- `cli/main.py` - Main entry point
- `cli/commands/` - Command implementations

### Utilities
- `cli/utils/` - CLI helpers

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
