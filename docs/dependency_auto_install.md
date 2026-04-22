# 自动依赖安装功能实现总结

## 问题背景

项目中的 skill 执行时经常因为缺少 Python 依赖而报错，原因包括：

1. **builtin skills 使用 bash 直接执行脚本**，不经过 UV 沙箱的自动依赖安装
2. **SKILL.md 中的 dependencies 仅是文档性质**，不会自动安装
3. **第三方库（如 defusedxml, lxml）未在主依赖中**，导致运行时报错
4. **只有通过 python_repl 工具执行的代码才会自动安装依赖**

## 解决方案

在 skill 执行前自动检查并安装缺失的依赖。

### 实现架构

```
SkillGateway.execute()
    ↓
run_pre_execute_gate() ✓ (API key、权限检查)
    ↓
check_missing_dependencies() 警告缺失包（不阻断）
    ↓
SkillAgent.run() (执行 skill)
    ├─ python_repl → UvLocalSandbox.install_python_deps() 自动安装
    └─ bash → CLI 工具检测警告（Python 包安装无效，bash 在系统环境执行）
```

### 核心文件

1. **`middleware/sandbox/uv.py`**
   - `UvLocalSandbox.install_python_deps()`: 唯一的 Python 依赖安装入口
   - 使用 `uv pip install` 进行环境一致的安装
   - 包含跨平台特殊处理（python-magic → python-magic-bin）

2. **`middleware/sandbox/utils.py`** (新增)
   - `check_missing_cli_tools()`: CLI 工具检测警告
   - 跨 sandbox 类型（bash/sandbox）的通用 CLI 检测逻辑

3. **`core/skill/execution/policy/pre_execute.py`** (已存在)
   - `check_missing_dependencies()`: 检查缺失依赖
   - `parse_dependency()`: 解析依赖规格

4. **`shared/tools/dependency_aliases.py`** (已存在)
   - 导入名到安装包名的映射（cv2 → opencv-python）

## 功能特性

### 1. 依赖声明格式

```yaml
---
name: xlsx
metadata:
  dependencies:
    - openpyxl              # 普通包名
    - pip:python-pptx       # 显式 pip 包
    - py:cv2                # 导入名（自动解析为 opencv-python）
    - cli:ffmpeg            # CLI 工具（仅检查）
---
```

### 2. 别名自动解析

| 导入名 | 安装包名 |
|--------|----------|
| cv2 | opencv-python |
| pil | Pillow |
| docx | python-docx |
| pptx | python-pptx |
| sklearn | scikit-learn |
| bs4 | beautifulsoup4 |

### 3. 安装行为

| 类型 | 行为 |
|------|------|
| python_repl 中的 Python 包 | 自动安装到 sandbox venv（有效） |
| bash 中的 Python 包 | 安装到 sandbox venv（**无效**，bash 在系统环境执行） |
| CLI 工具 | 仅检测并警告，不自动安装 |

**重要说明**：bash 工具路径下，Python 包安装到 sandbox venv 是无效的，因为 bash 命令在系统环境执行。如需通过 bash 安装 Python 包，应使用 `pip install --user` 或系统包管理器。

### 4. 错误响应

```json
{
  "ok": false,
  "status": "blocked",
  "error_code": "DEPENDENCY_MISSING",
  "summary": "Failed to install dependencies: ...",
  "diagnostics": {
    "error_type": "dependency_error",
    "error_detail": {
      "missing_dependencies": ["package1", "package2"],
      "error_message": "详细错误信息",
      "stage": "dependency_installation"
    }
  }
}
```

## 性能影响

- **首次运行**：需要安装依赖（10-60秒，取决于包大小）
- **后续运行**：依赖已满足，仅检查（毫秒级）
- **缓存**：安装的包持久化在 `.venv` 中

## 使用示例

### Skill 开发者

在 `SKILL.md` 中声明依赖：

```yaml
---
name: my-skill
metadata:
  dependencies:
    - pandas
    - openpyxl
---
```

系统会在执行前自动安装（通过 python_repl 路径）。

### 手动调用（不推荐）

```python
from middleware.sandbox.uv import UvLocalSandbox
from shared.tools.dependency_aliases import normalize_dependency_spec

sandbox = UvLocalSandbox()
success, error = sandbox.install_python_deps(
    deps=['pandas', 'openpyxl'],
    timeout=60,
)
```

**推荐**：直接使用 `UvLocalSandbox`，而不是通过 wrapper 层。

## 架构变更记录

### 2026-04-17 重构

- **删除** `core/skill/execution/dependency_installer.py`：该文件是历史遗留的 wrapper 层，职责与 `UvLocalSandbox.install_python_deps()` 重复，且造成架构混淆
- **删除** `core/skill/execution/tests/test_dependency_installer.py`
- **新增** `middleware/sandbox/utils.py`：统一的 CLI 工具检测逻辑
- **修改** `tools/atomics/bash.py`：删除无效的 Python 包安装调用，保留 CLI 工具检测警告
- **架构澄清**：`UvLocalSandbox.install_python_deps()` 是唯一的 Python 依赖安装入口

## 后续优化建议

1. **bash 路径的 Python 包安装**：考虑通过 `pip install --user` 或其他方式在 bash 环境中安装 Python 包
2. **并行安装**：多个包可以并行安装提升速度
3. **版本锁定**：支持 `pandas>=2.0.0` 格式的版本约束
4. **依赖冲突检测**：检测版本冲突并给出建议
