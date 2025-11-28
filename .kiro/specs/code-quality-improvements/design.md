# Design Document

## Overview

This design document outlines the technical approach for improving the Mingli MCP Server's code quality, test coverage, and maintainability. The improvements focus on refactoring the monolithic main entry file, achieving 80%+ test coverage, implementing comprehensive boundary testing, and enhancing error handling.

## Architecture

### Current Architecture

```
mingli_mcp.py (1389 lines - monolithic)
├── MingliMCPServer class
│   ├── MCP protocol handling
│   ├── Tool definitions (7 tools)
│   ├── Tool handlers
│   └── Transport initialization
```

### Target Architecture

```
mcp/
├── __init__.py              # Public API exports
├── server.py                # MingliMCPServer class (core logic)
├── protocol.py              # MCP protocol handling
├── tools/
│   ├── __init__.py          # Tool registry
│   ├── definitions.py       # Tool schema definitions
│   ├── ziwei_handlers.py    # Ziwei tool handlers
│   └── bazi_handlers.py     # Bazi tool handlers
mingli_mcp.py                # Entry point (minimal, imports from mcp/)
```

## Components and Interfaces

### 1. MCP Server Module (`mcp/server.py`)

```python
class MingliMCPServer:
    """Core MCP server with minimal responsibilities"""
    
    def __init__(self):
        self.transport = None
        self.protocol_handler = ProtocolHandler()
        self.tool_registry = ToolRegistry()
        
    def start(self) -> None:
        """Start the MCP server"""
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate handler"""
```

### 2. Protocol Handler (`mcp/protocol.py`)

```python
class ProtocolHandler:
    """Handles MCP protocol methods"""
    
    def handle_initialize(self, request: Dict, request_id: Any) -> Dict:
        """Handle initialize request"""
        
    def handle_tools_list(self, request_id: Any) -> Dict:
        """Handle tools/list request"""
        
    def handle_prompts_list(self, request_id: Any) -> Dict:
        """Handle prompts/list request"""
        
    def handle_resources_list(self, request_id: Any) -> Dict:
        """Handle resources/list request"""
```

### 3. Tool Registry (`mcp/tools/__init__.py`)

```python
class ToolRegistry:
    """Registry for MCP tools"""
    
    def __init__(self):
        self._tools: Dict[str, ToolHandler] = {}
        self._definitions: List[Dict] = []
        
    def register(self, name: str, handler: Callable, definition: Dict) -> None:
        """Register a tool with its handler and schema"""
        
    def get_handler(self, name: str) -> Callable:
        """Get handler for a tool"""
        
    def get_definitions(self) -> List[Dict]:
        """Get all tool definitions for tools/list"""
```

### 4. Tool Handlers (`mcp/tools/ziwei_handlers.py`, `mcp/tools/bazi_handlers.py`)

```python
# ziwei_handlers.py
def handle_get_ziwei_chart(args: Dict[str, Any]) -> str:
    """Handle get_ziwei_chart tool call"""

def handle_get_ziwei_fortune(args: Dict[str, Any]) -> str:
    """Handle get_ziwei_fortune tool call"""

def handle_analyze_ziwei_palace(args: Dict[str, Any]) -> str:
    """Handle analyze_ziwei_palace tool call"""

# bazi_handlers.py
def handle_get_bazi_chart(args: Dict[str, Any]) -> str:
    """Handle get_bazi_chart tool call"""

def handle_get_bazi_fortune(args: Dict[str, Any]) -> str:
    """Handle get_bazi_fortune tool call"""

def handle_analyze_bazi_element(args: Dict[str, Any]) -> str:
    """Handle analyze_bazi_element tool call"""
```

## Data Models

### Enhanced Validation Error

```python
@dataclass
class ValidationErrorDetail:
    field: str
    value: Any
    expected: str
    message: str

class EnhancedValidationError(ValidationError):
    def __init__(self, details: List[ValidationErrorDetail]):
        self.details = details
        message = self._format_message()
        super().__init__(message)
    
    def _format_message(self) -> str:
        lines = ["Validation failed:"]
        for d in self.details:
            lines.append(f"  - {d.field}: {d.message} (got: {d.value}, expected: {d.expected})")
        return "\n".join(lines)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, the following properties were identified as testable:

### Property 1: Valid dates in range are accepted
*For any* date string in YYYY-MM-DD format where year is between 1900 and 2100 (inclusive), and the date is a valid calendar date, the validation function should accept it without raising an error.
**Validates: Requirements 4.1**

### Property 2: Invalid dates outside range are rejected
*For any* date string where the year is less than 1900 or greater than 2100, the validation function should raise a DateRangeError.
**Validates: Requirements 3.2**

### Property 3: Time index round-trip consistency
*For any* time_index value from 0 to 12 (inclusive), converting to a time range (hour, minute) and back should produce the same time_index.
**Validates: Requirements 4.2**

### Property 4: BirthInfo serialization round-trip
*For any* valid BirthInfo object, calling `to_dict()` followed by `from_dict()` should produce an equivalent BirthInfo object with identical field values.
**Validates: Requirements 4.3**

### Property 5: Solar time offset determinism
*For any* longitude value between -180 and 180, the solar time offset calculation should be deterministic (same input always produces same output) and within expected bounds (±720 minutes, corresponding to ±12 hours).
**Validates: Requirements 4.4**

### Property 6: Leap year February 29 validation
*For any* leap year (divisible by 4, except centuries not divisible by 400), February 29 should be accepted as a valid date.
**Validates: Requirements 3.5**

### Property 7: Non-leap year February 29 rejection
*For any* non-leap year, February 29 should be rejected with a ValidationError.
**Validates: Requirements 3.6**

### Property 8: Validation errors contain invalid value
*For any* validation error caused by an invalid input value, the error message should contain a string representation of the actual invalid value that was provided.
**Validates: Requirements 5.1**

## Error Handling

### Validation Error Strategy

1. **Collect all errors**: Instead of failing on first error, collect all validation errors
2. **Include context**: Each error includes field name, invalid value, and expected format
3. **Actionable messages**: Messages tell users how to fix the issue

### System Error Strategy

1. **Log full details**: Log stack trace and context for debugging
2. **Return safe message**: Return user-friendly message without internal details
3. **Preserve error chain**: Use `raise ... from` to preserve error context

## Testing Strategy

### Dual Testing Approach

This project uses both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property-based tests**: Verify universal properties across all valid inputs

### Property-Based Testing Framework

The project will use **Hypothesis** for property-based testing in Python.

```python
from hypothesis import given, strategies as st

@given(st.dates(min_value=date(1900, 1, 1), max_value=date(2100, 12, 31)))
def test_valid_dates_accepted(d):
    """Property 1: All valid dates in range are accepted"""
    date_str = d.strftime("%Y-%m-%d")
    # Should not raise
    validate_date_range(date_str)
```

### Test Organization

```
tests/
├── conftest.py                    # Shared fixtures
├── test_mcp_server.py             # MCP server tests
├── test_protocol.py               # Protocol handler tests
├── test_tools/
│   ├── test_ziwei_handlers.py     # Ziwei tool tests
│   └── test_bazi_handlers.py      # Bazi tool tests
├── test_validators.py             # Validation tests
├── test_validators_properties.py  # Property-based validation tests
├── test_birth_info.py             # BirthInfo tests
├── test_birth_info_properties.py  # Property-based BirthInfo tests
├── test_solar_time.py             # Solar time tests
├── test_solar_time_properties.py  # Property-based solar time tests
└── test_formatters.py             # Formatter tests
```

### Test Requirements

- Each property-based test MUST be tagged with: `**Feature: code-quality-improvements, Property {number}: {property_text}**`
- Property-based tests MUST run at least 100 iterations
- Unit tests cover specific examples and edge cases
- Property tests verify universal properties

### Coverage Targets

| Module | Current | Target |
|--------|---------|--------|
| `mcp/server.py` | 0% | 90% |
| `mcp/protocol.py` | 0% | 90% |
| `mcp/tools/*` | 0% | 85% |
| `core/birth_info.py` | 83% | 95% |
| `utils/validators.py` | 100% | 100% |
| `utils/solar_time.py` | 82% | 95% |
| `transports/stdio_transport.py` | 22% | 80% |
| **Overall** | 18% | 80% |

