# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run the server (stdio mode for MCP)
python mingli_mcp.py

# Run HTTP transport (for Docker/server deployments)
TRANSPORT_TYPE=http HTTP_PORT=8080 python mingli_mcp.py
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
LOG_LEVEL=DEBUG python mingli_mcp.py

# Test individual fortune systems
python -m systems.ziwei.ziwei_system
python -m systems.bazi.bazi_system
```

## Code Architecture

This is a **Model Context Protocol (MCP) server** for Chinese fortune telling systems with a modular, plugin-based architecture.

### Core Structure

```
ziwei_mcp/
├── mingli_mcp.py              # Main MCP server entry point (mingli_mcp.py:1)
├── config.py                  # Configuration management (config.py:1)
├── pyproject.toml            # Project metadata and dependencies (pyproject.toml:1)
│
├── core/                      # Abstract base layer
│   ├── base_system.py        # BaseFortuneSystem abstract class (core/base_system.py:14)
│   ├── birth_info.py         # BirthInfo data model
│   └── chart_result.py       # ChartResult data model
│
├── systems/                   # Fortune system implementations
│   ├── __init__.py           # System registry (systems/__init__.py:1)
│   ├── ziwei/                # Ziwei Doushu system
│   │   ├── ziwei_system.py   # ZiweiSystem implementation
│   │   └── formatter.py      # Ziwei result formatting
│   ├── bazi/                 # BaZi (Four Pillars) system
│   │   ├── bazi_system.py    # BaziSystem implementation
│   │   └── formatter.py      # BaZi result formatting
│   └── astrology/            # Western astrology (stub)
│
├── transports/                # Communication transports
│   ├── base_transport.py     # Transport base class
│   ├── stdio_transport.py    # stdio transport (default for MCP)
│   └── http_transport.py     # HTTP transport (optional, needs uvicorn)
│
├── utils/                     # Utilities
│   ├── validators.py         # Parameter validation
│   ├── formatters.py         # Response formatting
│   ├── rate_limiter.py       # Rate limiting
│   └── metrics.py            # Metrics collection
│
└── tests/                     # Unit tests
    ├── test_ziwei.py         # Ziwei system tests
    └── test_bazi.py          # BaZi system tests
```

### Key Components

**1. MingliMCPServer** (mingli_mcp.py:31)
   - Main server class handling MCP protocol
   - Manages transport layer initialization
   - Handles JSON-RPC requests (initialize, tools/list, tools/call)
   - Routes tool calls to appropriate systems

**2. BaseFortuneSystem** (core/base_system.py:14)
   - Abstract base class for all fortune systems
   - Defines interface: `get_chart()`, `get_fortune()`, `analyze_palace()`
   - Provides `validate_birth_info()` for common validation

**3. System Registry** (systems/__init__.py:17)
   - `register_system(name, system_class)` - Register new systems
   - `get_system(name)` - Get system instance (cached)
   - `list_systems()` - List all registered systems
   - Auto-registers ziwei and bazi systems on import

**4. Transport Layer** (transports/)
   - **StdioTransport**: Default for MCP integration
   - **HttpTransport**: Optional HTTP server (requires fastapi+uvicorn)
   - Configured via `TRANSPORT_TYPE` env var

### Adding New Fortune Systems

The codebase uses a **plugin architecture**. To add a new system:

**Step 1**: Create system class
```python
# systems/new_system/new_system.py
from core.base_system import BaseFortuneSystem

class NewSystem(BaseFortuneSystem):
    def get_system_name(self) -> str:
        return "New System"

    def get_chart(self, birth_info):
        # Implement chart generation
        return {...}
```

**Step 2**: Register system
```python
# systems/__init__.py
from .new_system import NewSystem
register_system("new_system", NewSystem)
```

**Step 3**: Add MCP tool (mingli_mcp.py:140)
- Add tool definition to `_handle_tools_list()`
- Implement handler method `_tool_new_system_method()`

## Configuration

**Key Environment Variables** (config.py):
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `TRANSPORT_TYPE`: "stdio" (default) or "http"
- `HTTP_HOST`: HTTP server host (default: "localhost")
- `HTTP_PORT`: HTTP server port (default: 8080)
- `MCP_SERVER_NAME`: Server name (default: "ziwei_mcp")
- `MCP_SERVER_VERSION`: Server version

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
python mingli_mcp.py
```

## Available MCP Tools

Defined in `mingli_mcp.py:140-410`:

1. **get_ziwei_chart**: Get Ziwei chart with 12 palaces, stars, transformations
2. **get_ziwei_fortune**: Get Ziwei fortune (decadal, yearly, monthly, daily)
3. **analyze_ziwei_palace**: Analyze specific palace
4. **get_bazi_chart**: Get BaZi chart with 4 pillars, ten gods, 5 elements
5. **get_bazi_fortune**: Get BaZi fortune (major luck periods, yearly)
6. **analyze_bazi_element**: Analyze 5-element strength and balance
7. **list_fortune_systems**: List all available systems

## Important Files

- **mingli_mcp.py**: Main entry point, handles MCP protocol
- **config.py**: Configuration management
- **DEV_COMMANDS.md**: Quick reference for development commands
- **README.md**: User documentation and API reference
- **pyproject.toml**: Python project configuration

## Development Notes

**MCP Protocol Version**: 2024-11-05 (mingli_mcp.py:35)

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
