[根目录](../CLAUDE.md) > **gui**

---

# GUI Module - Desktop Interface

> **Module:** `gui/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation

---

## 模块职责

The `gui/` module provides the **Flet-based desktop GUI** for Memento-Skills.

**Core Responsibilities:**
- **Chat Interface** - Real-time agent interaction
- **Session Management** - Create, load, rename, delete sessions
- **Workspace Browser** - File tree with drag-and-drop
- **Slash Commands** - Quick actions (/skills, /context, /compress)

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `memento-gui` | `gui/app.py:main` | GUI entry point |

### Running

```bash
# Start GUI
memento-gui

# Or directly with Python
python -m gui.app
```

---

## 对外接口

### GUI Components

```python
# Main App
def main():
    """Flet app entry point"""

# UI Components
class ChatInterface:
    """Chat UI with streaming support"""

class SessionManager:
    """Session list and management"""

class WorkspaceBrowser:
    """File tree browser"""
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `core/` | Agent framework |
| `middleware/` | Config, storage |
| `flet` | GUI framework |

---

## 测试与质量

### Test Structure

- **Location:** `tests/gui/`
- **Framework:** `pytest` + Flet testing

---

## 常见问题 (FAQ)

### Q: How do I add a new UI component?
A: Create a new Flet control class in `gui/components/` and integrate it in `gui/app.py`.

---

## 相关文件清单

### Core GUI
- `gui/app.py` - Main application
- `gui/components/` - UI components

### Features
- `gui/chat/` - Chat interface
- `gui/sessions/` - Session management
- `gui/workspace/` - Workspace browser

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
