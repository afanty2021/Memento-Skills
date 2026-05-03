[根目录](../CLAUDE.md) > **tools**

---

# Tools Module - Unified Tool Registry

> **Module:** `tools/`
> **Version:** 0.3.0 (New in v0.3.0)
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented unified tool registry architecture
- Mapped atomic tools and MCP integration

---

## 模块职责

The `tools/` module provides a **unified registry for all tools** used by the agent, replacing the previous `builtin/tools/` layer.

**Core Responsibilities:**
- **Tool Registry** - Single surface for tool registration, discovery, and execution
- **Atomic Tools** - Basic tools (bash, file ops, grep, glob, web, Python/JS REPLs, MCP wrappers)
- **MCP Integration** - Model Context Protocol client for external tool servers
- **OpenAI Schema Generation** - Auto-generate tool schemas for LLM function calling
- **Execution Statistics** - Track call counts, success rates, latency

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `get_registry()` | `tools/__init__.py` | Get singleton ToolRegistry instance |
| `ToolRegistry` | `tools/registry.py` | Main registry class |
| `bootstrap()` | `tools/bootstrap.py` | Initialize tools with MCP servers |

### Initialization Flow

```python
# 1. Bootstrap (called by bootstrap.py)
await tools_bootstrap(mcp_config=mcp_config)

# 2. Get Registry
from tools import get_registry
registry = get_registry()

# 3. Register Tools
@registry.register
async def my_tool(arg1: str) -> str:
    """Tool description"""
    return f"Processed: {arg1}"

# 4. Call Tools
result = await registry.call("my_tool", {"arg1": "test"})
```

---

## 对外接口

### ToolRegistry API

```python
class ToolRegistry:
    def register(self, name: str | None = None) -> Callable:
        """Register a tool function (decorator)"""

    async def call(self, name: str, kwargs: dict) -> Any:
        """Execute a tool by name"""

    def get_tool(self, name: str) -> ToolDefinition:
        """Get tool definition by name"""

    def list_tools(self) -> list[str]:
        """List all registered tool names"""

    def get_openai_schema(self) -> list[dict]:
        """Generate OpenAI function calling schema for all tools"""

    def get_stats(self, name: str) -> ToolStats:
        """Get execution statistics for a tool"""

    def reset_stats(self, name: str | None = None):
        """Reset statistics (specific tool or all)"""
```

### Atomic Tools

| Tool | Description | File |
|------|-------------|------|
| `bash` | Execute shell commands | `tools/atomics/bash.py` |
| `file_read` | Read file contents | `tools/atomics/file_ops.py` |
| `file_write` | Write file contents | `tools/atomics/file_ops.py` |
| `grep` | Search file contents | `tools/atomics/grep.py` |
| `glob` | Find files by pattern | `tools/atomics/glob.py` |
| `list_directory` | List directory contents | `tools/atomics/list_dir.py` |
| `web_search` | Web search (Tavily) | `tools/atomics/web.py` |
| `python_repl` | Python code execution | `tools/atomics/python_repl.py` |
| `js_repl` | JavaScript code execution | `tools/atomics/js_repl.py` |
| `mcp_call` | Call MCP server tool | `tools/atomics/mcp_wrapper.py` |

### MCP Integration

```python
# MCP Client
from tools.mcp import MCPClient

# Connect to MCP server
client = MCPClient(server_name="my-server")
await client.connect(stdio_command="node server.js")

# List available tools
tools = await client.list_tools()

# Call MCP tool
result = await client.call_tool("tool_name", {"arg": "value"})
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `middleware/mcp_config_manager` | MCP server configuration |
| `shared/` | Schemas, security primitives |
| `mcp` (package) | MCP client library |

### Configuration

```python
# MCP Config (~/memento_s/mcp_config.json)
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    }
  }
}

# Tool Config (from global config)
config = {
  "tools": {
    "bash_enabled": true,
    "web_search_enabled": true,
    "mcp_enabled": true
  }
}
```

---

## 数据模型

### ToolDefinition

```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
    handler: Callable  # Sync or async
    metadata: dict[str, Any]
```

### ToolStats

```python
@dataclass
class ToolStats:
    call_count: int
    total_duration_ms: float
    error_count: int
    timeout_count: int
    last_called: float

    @property
    def avg_duration_ms(self) -> float: ...

    @property
    def success_rate(self) -> float: ...
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/tools/`
- **Framework:** `pytest` + `pytest-asyncio`
- **Coverage:** Comprehensive

### Key Test Files

| Test File | Coverage |
|-----------|----------|
| `tests/tools/test_registry.py` | Registry operations |
| `tests/tools/test_atomics.py` | Atomic tool execution |
| `tests/tools/test_mcp.py` | MCP integration |

---

## 常见问题 (FAQ)

### Q: How do I add a new atomic tool?
A: Create a file in `tools/atomics/`, implement the tool function, and register it in `tools/atomics/__init__.py`.

### Q: How do I integrate an external MCP server?
A: Add the server configuration to `~/memento_s/mcp_config.json` and restart the application.

### Q: What's the difference between tools and skills?
A: Tools are low-level functions (bash, file ops), while skills are high-level capabilities composed of multiple tools and prompts.

### Q: How are tools secured?
A: All tools go through `PolicyManager` validation for path security, argument sanitization, and execution policies.

---

## 相关文件清单

### Core Registry
- `tools/registry.py` - ToolRegistry implementation
- `tools/__init__.py` - Public API and bootstrap
- `tools/bootstrap.py` - Initialization logic

### Atomic Tools
- `tools/atomics/bash.py` - Shell command execution
- `tools/atomics/file_ops.py` - File operations
- `tools/atomics/grep.py` - Content search
- `tools/atomics/glob.py` - File pattern matching
- `tools/atomics/list_dir.py` - Directory listing
- `tools/atomics/web.py` - Web search and fetch
- `tools/atomics/python_repl.py` - Python REPL
- `tools/atomics/js_repl.py` - JavaScript REPL
- `tools/atomics/mcp_wrapper.py` - MCP tool wrapper

### MCP Integration
- `tools/mcp/client.py` - MCP client
- `tools/mcp/transport.py` - Transport layer (stdio, SSE)

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
