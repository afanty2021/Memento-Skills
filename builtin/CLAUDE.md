[根目录](../CLAUDE.md) > **builtin**

---

# Builtin Module - Built-in Skills

> **Module:** `builtin/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:30:00Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Enhanced Documentation
- Added detailed descriptions for all 10 built-in skills
- Added skill capability matrices
- Added skill parameter documentation
- Added usage examples for each skill

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation

---

## 模块职责

The `builtin/` module contains **10 built-in skills** that serve as the starting point for the agent's skill library. These skills are managed through the core skill system and provide essential capabilities for file operations, web search, document processing, and more.

**Built-in Skills:**
1. **filesystem** - File read, write, search, directory operations
2. **web-search** - Tavily-based web search and page fetching
3. **image-analysis** - Image understanding, OCR, captioning
4. **pdf** - PDF reading, form filling, merging, splitting, OCR
5. **docx** - Word document creation and editing
6. **xlsx** - Spreadsheet processing
7. **pptx** - PowerPoint creation and editing
8. **skill-creator** - New skill creation, optimization, evaluation
9. **uv-pip-install** - Python dependency installation via UV
10. **im-platform** - IM platform integration (v0.2.0)

---

## 入口与启动

### Skill System Integration

Built-in skills are automatically registered with the `SkillGateway` during bootstrap:

```python
# Skills are discovered and registered automatically
from core.skill import init_skill_system

gateway = await init_skill_system()
# All built-in skills are now available via gateway
```

### Skill Execution

```python
# Execute a built-in skill
result = await gateway.execute(
    skill_name="filesystem",
    kwargs={
        "operation": "read",
        "path": "/path/to/file.txt"
    }
)
```

---

## 对外接口

### Built-in Skill Details

#### 1. filesystem

**Capabilities:** File operations (read, write, search, list, delete)

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | str | Operation type: `read`, `write`, `search`, `list`, `delete` |
| `path` | str | File or directory path |
| `content` | str | Content for write operations |
| `pattern` | str | Search pattern for search operations |

**Example:**
```python
result = await gateway.execute(
    skill_name="filesystem",
    kwargs={
        "operation": "read",
        "path": "/path/to/file.txt"
    }
)
```

#### 2. web-search

**Capabilities:** Web search using Tavily API, page content extraction

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | str | Search query |
| `max_results` | int | Maximum number of results (default: 10) |
| `extract_content` | bool | Extract full page content (default: false) |

**Example:**
```python
result = await gateway.execute(
    skill_name="web-search",
    kwargs={
        "query": "Memento-Skills agent framework",
        "max_results": 5
    }
)
```

#### 3. image-analysis

**Capabilities:** Image understanding, OCR, captioning, object detection

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `image_path` | str | Path to image file |
| `task` | str | Task type: `caption`, `ocr`, `detect`, `analyze` |
| `detail_level` | str | Detail level: `low`, `medium`, `high` |

**Example:**
```python
result = await gateway.execute(
    skill_name="image-analysis",
    kwargs={
        "image_path": "/path/to/image.jpg",
        "task": "caption"
    }
)
```

#### 4. pdf

**Capabilities:** PDF reading, form filling, merging, splitting, OCR

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | str | Operation type: `read`, `merge`, `split`, `fill_form`, `ocr` |
| `input_path` | str | Input PDF path |
| `output_path` | str | Output path (for merge, split, fill_form) |
| `pages` | list | Page numbers for split operation |

**Example:**
```python
result = await gateway.execute(
    skill_name="pdf",
    kwargs={
        "operation": "read",
        "input_path": "/path/to/document.pdf"
    }
)
```

#### 5. docx

**Capabilities:** Word document creation, editing, formatting

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | str | Operation type: `create`, `read`, `edit`, `format` |
| `file_path` | str | Word document path |
| `content` | str | Document content |
| `format_options` | dict | Formatting options |

**Example:**
```python
result = await gateway.execute(
    skill_name="docx",
    kwargs={
        "operation": "create",
        "file_path": "/path/to/document.docx",
        "content": "Hello, World!"
    }
)
```

#### 6. xlsx

**Capabilities:** Spreadsheet reading, writing, formula calculation

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | str | Operation type: `read`, `write`, `calculate` |
| `file_path` | str | Spreadsheet path |
| `sheet_name` | str | Sheet name (default: first sheet) |
| `data` | list | Data for write operations |

**Example:**
```python
result = await gateway.execute(
    skill_name="xlsx",
    kwargs={
        "operation": "read",
        "file_path": "/path/to/spreadsheet.xlsx"
    }
)
```

#### 7. pptx

**Capabilities:** PowerPoint creation, editing, slide management

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | str | Operation type: `create`, `add_slide`, `edit`, `export` |
| `file_path` | str | PowerPoint file path |
| `slide_content` | dict | Slide content and layout |
| `template` | str | Template name (optional) |

**Example:**
```python
result = await gateway.execute(
    skill_name="pptx",
    kwargs={
        "operation": "create",
        "file_path": "/path/to/presentation.pptx",
        "slide_content": {"title": "Hello", "content": "World"}
    }
)
```

#### 8. skill-creator

**Capabilities:** New skill creation, optimization, evaluation

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `task` | str | Task type: `create`, `optimize`, `evaluate` |
| `skill_name` | str | Name of the skill |
| `description` | str | Skill description |
| `requirements` | str | Skill requirements and specifications |
| `existing_code` | str | Existing code (for optimize) |

**Example:**
```python
result = await gateway.execute(
    skill_name="skill-creator",
    kwargs={
        "task": "create",
        "skill_name": "my-custom-skill",
        "description": "A skill that does X",
        "requirements": "Should be able to..."
    }
)
```

#### 9. uv-pip-install

**Capabilities:** Python package installation via UV package manager

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `packages` | list | List of package names |
| `version_specs` | dict | Version specifications (optional) |
| `upgrade` | bool | Upgrade if already installed (default: false) |

**Example:**
```python
result = await gateway.execute(
    skill_name="uv-pip-install",
    kwargs={
        "packages": ["requests", "beautifulsoup4"],
        "upgrade": False
    }
)
```

#### 10. im-platform

**Capabilities:** IM platform integration (Feishu, DingTalk, WeCom, WeChat)

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | str | Platform: `feishu`, `dingtalk`, `wecom`, `wechat` |
| `operation` | str | Operation type: `send_message`, `get_history`, `get_contacts` |
| `message` | str | Message content |
| `recipient` | str | Recipient ID or channel |

**Example:**
```python
result = await gateway.execute(
    skill_name="im-platform",
    kwargs={
        "platform": "feishu",
        "operation": "send_message",
        "message": "Hello from Memento!",
        "recipient": "ou_xxx"
    }
)
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `core/` | Skill framework (SkillGateway) |
| `tools/` | Tool registry for execution |
| `middleware/` | Config, sandbox (UV) |

### External Dependencies

| Skill | External Dependencies |
|-------|----------------------|
| `web-search` | Tavily API |
| `image-analysis` | Vision LLM (GPT-4V, Claude 3.5, etc.) |
| `pdf` | PyPDF2, pdfplumber |
| `docx` | python-docx |
| `xlsx` | openpyxl |
| `pptx` | python-pptx |
| `uv-pip-install` | UV package manager |
| `im-platform` | Platform SDKs (lark-oapi, etc.) |

---

## 测试与质量

### Test Structure

- **Location:** `tests/builtin/`
- **Framework:** `pytest`
- **Coverage:** Partial

### Test Files

| Test File | Coverage |
|-----------|----------|
| `tests/builtin/test_filesystem.py` | File operations |
| `tests/builtin/test_web_search.py` | Web search |
| `tests/builtin/test_pdf.py` | PDF operations |
| `tests/builtin/test_docx.py` | Word documents |
| `tests/builtin/test_skill_creator.py` | Skill creation |

---

## 常见问题 (FAQ)

### Q: How do I create a new built-in skill?
A: Use the `skill-creator` skill or manually create a skill directory following the skill template structure.

### Q: Can I modify built-in skills?
A: Yes, but it's recommended to copy and customize them to avoid conflicts during updates.

### Q: How are built-in skills different from downloaded skills?
A: Built-in skills are shipped with the framework and maintained by the Memento team. Downloaded skills are created by the community and managed via the skill market.

### Q: What happens if a built-in skill fails?
A: The agent will attempt error recovery, log the failure, and may trigger the skill-creator to optimize the failing skill.

---

## 相关文件清单

### Module Structure
- `builtin/__init__.py` - Module initialization
- `builtin/tools/` - Built-in tools (legacy, moved to tools/)
- `builtin/skills/` - Built-in skills (managed via core skill system)

### Documentation
- `builtin/CLAUDE.md` - This file

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
