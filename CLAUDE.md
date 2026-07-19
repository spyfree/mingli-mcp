# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run the server (stdio mode for MCP)
python -m mingli_mcp

# Run HTTP transport (for Docker/server deployments)
TRANSPORT_TYPE=http HTTP_PORT=8080 python -m mingli_mcp
```

## Common Development Commands

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Test with coverage
pytest --cov=. --cov-report=term-missing --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/test_bazi.py

# Run specific test function
pytest tests/test_ziwei.py::test_ziwei_chart
```

### Code Quality
```bash
# Format code
black .

# Check import sorting
isort .

# Lint with flake8
flake8 .

# Type check with mypy
mypy .

# Run all quality checks at once
black --check . && isort --check-only . && flake8 . && pytest
```

### Building and Publishing
```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info

# Build package
python -m build

# Check package
twine check dist/*

# Publish to PyPI
twine upload dist/*
```

### Development Workflow
```bash
# Debug with logging
LOG_LEVEL=DEBUG python -m mingli_mcp
```

## Code Architecture

This is a **Model Context Protocol (MCP) server** for Chinese fortune telling systems with a modular, plugin-based architecture.

### Core Structure

```
ziwei_mcp/
├── pyproject.toml                 # Project metadata and dependencies
├── mingli_mcp/                    # The installable package (single top-level namespace)
│   ├── __init__.py               # Package version (__version__)
│   ├── cli.py                    # Console entry point (mingli-mcp / python -m mingli_mcp)
│   ├── config.py                 # Configuration management
│   │
│   ├── mcp_server/               # MCP protocol implementation
│   │   ├── server.py             # MingliMCPServer: request routing
│   │   ├── protocol.py           # ProtocolHandler: initialize/prompts/resources, version negotiation
│   │   ├── resources.py          # Resource contents
│   │   └── tools/                # Tool definitions and handlers
│   │
│   ├── core/                      # Abstract base layer
│   │   ├── base_system.py        # BaseFortuneSystem abstract class
│   │   ├── birth_info.py         # BirthInfo data model
│   │   └── chart_result.py       # ChartResult data model
│   │
│   ├── systems/                   # Fortune system implementations
│   │   ├── __init__.py           # System registry
│   │   ├── ziwei/                # Ziwei Doushu system (iztro-py based)
│   │   ├── bazi/                 # BaZi (Four Pillars) system
│   │   └── astrology/            # Western astrology (stub)
│   │
│   ├── transports/                # Communication transports
│   │   ├── stdio_transport.py    # stdio transport (default for MCP)
│   │   └── http_transport.py     # Streamable HTTP transport (stateless JSON mode)
│   │
│   ├── utils/                     # Validators, formatters, rate limiter, etc.
│   └── prompts/                   # Prompt templates (shipped with the package)
│
├── cloudflare/                    # Cloudflare Containers worker
│   └── container-worker.mjs
├── wrangler.jsonc                 # Cloudflare deployment config (mcp.lee.locker)
└── tests/                         # Unit tests
```

**Important**: everything lives under the single `mingli_mcp` package namespace.
Never add top-level modules/packages named `mcp`, `core`, `utils`, etc. — the PyPI
wheel would collide with other distributions (notably the official `mcp` SDK).

### Key Components

**1. MingliMCPServer** (mingli_mcp/mcp_server/server.py)
   - Main server class handling MCP protocol
   - Manages transport layer initialization
   - Handles JSON-RPC requests (initialize, tools/list, tools/call)
   - Routes tool calls to appropriate systems

**2. BaseFortuneSystem** (mingli_mcp/core/base_system.py)
   - Abstract base class for all fortune systems
   - Defines interface: `get_chart()`, `get_fortune()`, `analyze_palace()`
   - Provides `validate_birth_info()` for common validation

**3. System Registry** (mingli_mcp/systems/__init__.py)
   - `register_system(name, system_class)` - Register new systems
   - `get_system(name)` - Get system instance (cached)
   - `list_systems()` - List all registered systems
   - Auto-registers ziwei and bazi systems on import

**4. Transport Layer** (mingli_mcp/transports/)
   - **StdioTransport**: Default for MCP integration
   - **HttpTransport**: Streamable HTTP (stateless, JSON response mode; requires fastapi+uvicorn)
   - Configured via `TRANSPORT_TYPE` env var

### Adding New Fortune Systems

The codebase uses a **plugin architecture**. To add a new system:

**Step 1**: Create system class
```python
# mingli_mcp/systems/new_system/new_system.py
from mingli_mcp.core.base_system import BaseFortuneSystem

class NewSystem(BaseFortuneSystem):
    def get_system_name(self) -> str:
        return "New System"

    def get_chart(self, birth_info):
        # Implement chart generation
        return {...}
```

**Step 2**: Register system
```python
# mingli_mcp/systems/__init__.py
from .new_system import NewSystem
register_system("new_system", NewSystem)
```

**Step 3**: Add MCP tool (mingli_mcp/mcp_server/tools/)
- Add tool schema to `definitions.py` (`get_all_tool_definitions()`)
- Implement a handler and register it in `ToolRegistry._register_default_tools()` (`tools/__init__.py`)

## Configuration

**Key Environment Variables** (mingli_mcp/config.py):
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `TRANSPORT_TYPE`: "stdio" (default) or "http"
- `HTTP_HOST`: HTTP server host (default: "0.0.0.0")
- `HTTP_PORT`: HTTP server port (default: 8080)
- `HTTP_API_KEY`: Optional Bearer token for the HTTP endpoint (empty = auth disabled)
- `ENABLE_RATE_LIMIT` / `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW`: HTTP rate limiting (default: true / 100 / 60s)
- `CORS_ORIGINS` / `CORS_ALLOW_CREDENTIALS`: CORS + Origin validation allowlist
- `MCP_SERVER_NAME`: Server name (default: "ziwei_mcp")

**Config Source Priority**:
1. Environment variables
2. .env file
3. Defaults in config.py

## Testing Strategy

**Test Locations**:
- `tests/test_ziwei.py`: Ziwei system tests
- `tests/test_bazi.py`: BaZi system tests

**Running Tests**:
```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific system
pytest tests/test_ziwei.py

# Specific function
pytest tests/test_ziwei.py::test_ziwei_chart
```

**Test Structure**: Tests import systems directly:
```python
from systems import get_system
ziwei = get_system("ziwei")
chart = ziwei.get_chart(birth_info)
```

## Dependencies

**Core** (pyproject.toml:28):
- `iztro-py>=0.1.0`: Ziwei calculation library (pure Python, 10x faster than py-iztro)
- `lunar_python>=1.4.7`: Chinese calendar support
- `bidict>=0.23.0`: Bidirectional mappings
- `python-dateutil>=2.8.0`: Date parsing
- `fastapi>=0.104.0`: HTTP transport (optional)
- `uvicorn[standard]>=0.24.0`: ASGI server (optional)

**Development** (pyproject.toml:41):
- `pytest>=7.0.0`: Testing framework
- `black>=23.0.0`: Code formatting
- `flake8>=6.0.0`: Linting
- `mypy>=1.0.0`: Type checking
- `isort>=5.12.0`: Import sorting

## Deployment

**uvx (Recommended)**:
```bash
claude mcp add mingli -- uvx mingli-mcp
```

**Docker** (docker-compose.yml):
```bash
docker-compose up -d
# Connects to http://localhost:8080/mcp
```

**Source Installation**:
```bash
pip install -e ".[dev]"
python -m mingli_mcp
```

**Cloudflare Containers** (wrangler.jsonc + cloudflare/container-worker.mjs):
```bash
npx wrangler deploy
# Deployed at https://mcp.lee.locker/mcp
# Optional auth: npx wrangler secret put HTTP_API_KEY
```

## Available MCP Tools

Defined in `mingli_mcp/mcp_server/tools/definitions.py`:

1. **get_ziwei_chart**: Get Ziwei chart with 12 palaces, stars, transformations
2. **get_ziwei_fortune**: Get Ziwei fortune (decadal, yearly, monthly, daily)
3. **analyze_ziwei_palace**: Analyze specific palace
4. **get_bazi_chart**: Get BaZi chart with 4 pillars, ten gods, 5 elements
5. **get_bazi_fortune**: Get BaZi fortune (major luck periods, yearly)
6. **analyze_bazi_element**: Analyze 5-element strength and balance
7. **list_fortune_systems**: List all available systems

## Important Files

- **mingli_mcp/cli.py**: Main entry point (console script `mingli-mcp`)
- **mingli_mcp/mcp_server/server.py**: MCP request routing
- **mingli_mcp/config.py**: Configuration management
- **DEV_COMMANDS.md**: Quick reference for development commands
- **README.md**: User documentation and API reference
- **pyproject.toml**: Python project configuration

## Development Notes

**MCP Protocol Versions**: negotiated per client, latest supported is 2025-11-25
(see `SUPPORTED_PROTOCOL_VERSIONS` in mingli_mcp/mcp_server/protocol.py). The HTTP
transport is stateless Streamable HTTP in pure-JSON response mode: notifications
get 202 Accepted, Origin headers are validated (403 on mismatch), and the
MCP-Protocol-Version header is validated (400 on unsupported versions).

**Input Validation**:
- Uses `validate_birth_info()` in BaseFortuneSystem
- Date format: YYYY-MM-DD
- Time index: 0-12 (12 two-hour periods)
- Gender: "男" or "女"
- Calendar: "solar" or "lunar"

**Error Handling**:
- Custom exceptions in `core/exceptions.py`
- ValidationError: Invalid parameters
- SystemNotFoundError: Unknown system
- SystemError: System execution error

**Logging**:
- Configured via config.py
- Use `LOG_LEVEL=DEBUG` for troubleshooting

## Troubleshooting

**ModuleNotFoundError: No module named 'uvicorn'**:
- HTTP transport needs optional dependencies
- Install: `pip install mingli-mcp[http]` or full install
- Or use stdio mode (default): `TRANSPORT_TYPE=stdio`

**Connection Failed**:
- Check LOG_LEVEL=DEBUG for verbose output
- Verify transport type in config
- For HTTP: ensure port is available

**Test Failures**:
- Run with `-v` for verbose output
- Check coverage with `pytest --cov`
- Ensure all dependencies installed: `pip install -e ".[dev]"`

## Key Design Patterns

1. **Plugin Architecture**: Systems registered via `register_system()`
2. **Transport Abstraction**: Stdio and HTTP implementations
3. **Factory Pattern**: `get_system(name)` with caching
4. **Template Method**: BaseFortuneSystem defines workflow
5. **Formatter Pattern**: Separate formatting from business logic

## Cursor Configuration Example

For IDE integration (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```
