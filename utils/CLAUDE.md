[根目录](../CLAUDE.md) > **utils**

---

# Utils Module - Utility Functions

> **Module:** `utils/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented runtime requirements checker (v0.3.0)

---

## 模块职责

The `utils/` module provides **shared utility functions** used across the codebase.

**Core Responsibilities:**
- **Logging** - Centralized logging configuration
- **Runtime Requirements** - Dependency checking and auto-install
- **Path Management** - Cross-platform path utilities
- **String Utilities** - Common string operations
- **Debug Logging** - Agent phase debug markers

---

## 入口与启动

### Key Utilities

| Utility | File | Description |
|---------|------|-------------|
| `setup_logger` | `utils/logger.py` | Configure logging |
| `check_dependencies` | `utils/runtime_requirements/` | Check/install dependencies |
| `PathManager` | `utils/path_manager.py` | Path management |

---

## 对外接口

### Logging

```python
from utils.logger import setup_logger, get_logger

# Setup logging
setup_logger(
    console_level="DEBUG",
    file_level="INFO",
    rotation="00:00",
    retention="30 days"
)

# Get logger
logger = get_logger(__name__)
logger.info("Message")
```

### Runtime Requirements

```python
from utils.runtime_requirements import check_runtime_requirements

# Check and install missing dependencies
await check_runtime_requirements()
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `middleware/` | Config |
| `loguru` | Logging |

---

## 测试与质量

### Test Structure

- **Location:** `tests/utils/`
- **Framework:** `pytest`

---

## 常见问题 (FAQ)

### Q: How do I change log levels?
A: Modify `logging.level` in `~/memento_s/config.json`.

---

## 相关文件清单

### Core Utils
- `utils/logger.py` - Logging configuration
- `utils/path_manager.py` - Path management
- `utils/strings.py` - String utilities
- `utils/debug_logger.py` - Debug logging

### Runtime Requirements
- `utils/runtime_requirements/` - Dependency checking (v0.3.0)

### Other
- `utils/log_config.py` - Log configuration
- `utils/runtime_mode.py` - Runtime mode detection

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
