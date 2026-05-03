[根目录](../CLAUDE.md) > **core**

---

# Core Module - Agent Framework

> **Module:** `core/`
> **Version:** 0.3.0
> **Last Updated:** 2026-05-03T13:23:38Z

---

## 变更记录 (Changelog)

### 2026-05-03 - Initial Documentation
- Created comprehensive module documentation
- Documented 4-stage ReAct architecture
- Mapped skill system components
- Documented agent profile system (v0.3.0)

---

## 模块职责

The `core/` module is the heart of Memento-Skills, implementing the **4-stage ReAct agent architecture** with a self-evolving skill system.

**Core Responsibilities:**
- **Agent Orchestration** - Multi-phase reasoning loop (Intent → Planning → Execution → Reflection → Finalize)
- **Skill Management** - Skill discovery, retrieval (BM25 + vector), execution, and evolution
- **Agent Profiles** - Long-term agent identity (SoulManager) and user preferences (UserManager)
- **Session Management** - Session lifecycle, conversation history, runtime state
- **Protocol Definitions** - Communication protocols and event streaming
- **Prompt Templates** - System prompts and few-shot examples

---

## 入口与启动

### Entry Points

| Entry Point | File | Description |
|-------------|------|-------------|
| `MementoSAgent` | `memento_s/agent.py` | Main agent orchestrator |
| `SkillGateway` | `skill/gateway.py` | Skill system interface |
| `AgentProfile` | `agent_profile/` | Profile management |

### Initialization Flow

```python
# 1. Bootstrap (bootstrap.py)
await bootstrap()  # Initializes config, database, tools, skills

# 2. Create Agent
from core.memento_s import MementoSAgent
agent = MementoSAgent(session_id="...")

# 3. Run Agent
async for event in agent.run_stream(user_input):
    # Handle streaming events
    pass
```

### Key Classes

```python
# Agent Orchestrator
class MementoSAgent:
    async def run_stream(session_id: str, input_text: str) -> AsyncGenerator[dict, None]:
        """Main execution entry point - streams agent events"""

    async def reply_stream(...) -> AsyncGenerator[dict, None]:
        """Coordinate multi-phase execution with streaming"""

# Skill Gateway
class SkillGateway:
    async def discover(strategy: DiscoverStrategy) -> list[SkillManifest]:
        """Discover available skills"""

    async def recall(query: str, top_k: int = 5) -> list[SkillSearchResult]:
        """Retrieve relevant skills using BM25 + vector search"""

    async def execute(skill_name: str, kwargs: dict) -> SkillExecutionResponse:
        """Execute a skill in UV sandbox"""
```

---

## 对外接口

### Agent Phases

**Phase 1: Intent Recognition** (`phases/intent.py`)
- Classify user input: DIRECT, AGENTIC, INTERRUPT
- Route to appropriate execution path

**Phase 2: Planning** (`phases/planning.py`)
- Generate execution plan with skill selections
- Validate plan before execution

**Phase 3: Execution** (`phases/execution/`)
- Multi-step ReAct loop with tool calling
- Error recovery and loop detection
- Step boundary validation

**Phase 4: Reflection** (`phases/reflection.py`)
- Evaluate execution outcomes
- Update skill utility scores
- Trigger skill optimization if needed

**Phase 5: Finalize** (`phases/finalize.py`)
- Structured result summarization
- Extract key insights

### Skill System Interfaces

```python
# Discovery
async def discover_skills(strategy: DiscoverStrategy = DiscoverStrategy.LOCAL_ONLY)
    -> list[SkillManifest]

# Retrieval
async def recall_skills(query: str, top_k: int = 5)
    -> list[SkillSearchResult]

# Execution
async def execute_skill(
    skill_name: str,
    kwargs: dict,
    mode: ExecutionMode = ExecutionMode.SANDBOX
) -> SkillExecutionResponse

# Reflection
async def reflect_on_execution(
    skill_name: str,
    outcome: SkillExecutionResponse,
    user_feedback: str | None = None
) -> None
```

### Agent Profile Interfaces

```python
# Soul Management (Agent Identity)
class SoulManager:
    async def ensure_files() -> None
    async def read_soul() -> str
    async def update_soul(content: str) -> None

# User Management (User Preferences)
class UserManager:
    async def ensure_files() -> None
    async def read_user(user_id: str) -> str
    async def update_user(user_id: str, content: str) -> None
```

---

## 关键依赖与配置

### Dependencies

| Module | Purpose |
|--------|---------|
| `infra/` | Memory, context, compaction services |
| `tools/` | Tool registry for execution |
| `middleware/` | Config, LLM, storage |
| `shared/` | Chat manager, schemas, security |

### Configuration

```python
# Skill Config (from shared.schema)
SkillConfig(
    skills_dir=Path("~/memento_s/skills"),
    execution=SkillExecutionConfig(
        sandbox_provider="uv",  # or "local"
        timeout_seconds=120
    ),
    retrieval=SkillRetrievalConfig(
        use_bm25=True,
        use_vector=True,
        top_k=5
    )
)

# Agent Config (from core.memento_s.schemas)
AgentRuntimeConfig(
    max_steps=10,
    tool_call_timeout=120,
    enable_reflection=True
)
```

---

## 数据模型

### Key Schemas

```python
# Skill Manifest
class SkillManifest:
    name: str
    description: str
    version: str
    author: str
    tags: list[str]
    parameters: dict[str, Any]
    entry_point: str

# Skill Execution Response
class SkillExecutionResponse:
    success: bool
    result: Any
    error: str | None
    error_code: SkillErrorCode | None
    execution_time: float
    metadata: dict[str, Any]

# Agent Event (Protocol)
class AgentEvent:
    type: str  # "intent", "plan", "step", "reflection", "finalize"
    data: dict[str, Any]
    timestamp: float
    step_id: str | None
```

---

## 测试与质量

### Test Structure

- **Location:** `tests/core/`
- **Framework:** `pytest` + `pytest-asyncio`
- **Coverage:** Comprehensive (agent phases, skill system, profiles)

### Key Test Files

| Test File | Coverage |
|-----------|----------|
| `tests/core/test_agent.py` | Agent orchestration |
| `tests/core/test_skill_gateway.py` | Skill system |
| `tests/core/test_skill_execution.py` | Skill execution |
| `tests/core/test_agent_profile.py` | Profile system |
| `tests/core/test_retrieval.py` | Skill retrieval |

### Running Tests

```bash
# Run all core tests
pytest tests/core/

# Run specific test
pytest tests/core/test_skill_gateway.py::test_discover_skills

# Run with coverage
pytest --cov=core --cov-report=html
```

---

## 常见问题 (FAQ)

### Q: How do I add a new agent phase?
A: Create a new file in `core/memento_s/phases/` and integrate it into the agent's execution flow in `agent.py`.

### Q: How does skill retrieval work?
A: Skills are retrieved using hybrid BM25 (keyword) + vector (semantic) search. The system ranks skills by relevance and utility scores.

### Q: What's the difference between SoulManager and UserManager?
A: `SoulManager` manages the agent's long-term identity (traits, policies), while `UserManager` manages per-user preferences and history.

### Q: How do I customize agent behavior?
A: Modify prompts in `core/prompts/`, adjust phase logic in `core/memento_s/phases/`, or update the agent profile via `SOUL.md`.

### Q: What happens when skill execution fails?
A: The reflection phase analyzes the failure, updates utility scores, and may trigger skill optimization or regeneration.

---

## 相关文件清单

### Core Agent
- `core/memento_s/agent.py` - Main orchestrator
- `core/memento_s/phases/` - Execution phases (intent, planning, execution, reflection, finalize)
- `core/memento_s/schemas.py` - Agent runtime config
- `core/memento_s/skill_dispatch.py` - Skill dispatcher

### Skill System
- `core/skill/gateway.py` - Skill gateway interface
- `core/skill/loader/` - Skill discovery and loading
- `core/skill/retrieval/` - BM25 + vector retrieval
- `core/skill/execution/` - Sandbox execution and policies
- `core/skill/store/` - Skill persistence backends
- `core/skill/market.py` - Skill market
- `core/skill/schema.py` - Skill data models

### Agent Profiles (v0.3.0)
- `core/agent_profile/manager.py` - Profile manager
- `core/agent_profile/soul_manager.py` - Agent identity
- `core/agent_profile/user_manager.py` - User preferences

### Session & Context
- `core/context/session.py` - Session management
- `core/context/session_context.py` - Session context
- `core/context/runtime_state.py` - Runtime state store

### Protocol & Prompts
- `core/protocol/` - Communication protocols
- `core/prompts/` - Prompt templates

---

*This documentation is part of the Memento-Skills AI context. See [root CLAUDE.md](../CLAUDE.md) for project-level documentation.*
