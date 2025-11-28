# Implementation Plan

- [x] 1. Set up testing infrastructure
  - [x] 1.1 Add Hypothesis to dev dependencies in pyproject.toml
    - Add `hypothesis>=6.0.0` to `[project.optional-dependencies] dev`
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 1.2 Create tests/conftest.py with shared fixtures
    - Add fixtures for common test data (birth_info, dates, etc.)
    - _Requirements: 2.1, 2.2_

- [x] 2. Refactor mingli_mcp.py into modular structure
  - [x] 2.1 Create mcp/ package structure
    - Create `mcp/__init__.py`, `mcp/server.py`, `mcp/protocol.py`
    - Create `mcp/tools/__init__.py`, `mcp/tools/definitions.py`
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 2.2 Extract protocol handling to mcp/protocol.py
    - Move `_handle_initialize`, `_handle_tools_list`, `_handle_prompts_list`, `_handle_resources_list`, `_handle_resources_get` methods
    - Create `ProtocolHandler` class
    - _Requirements: 1.3_
  - [x] 2.3 Extract tool definitions to mcp/tools/definitions.py
    - Move all tool schema definitions from `_handle_tools_list`
    - Create functions to generate tool definitions
    - _Requirements: 1.2_
  - [x] 2.4 Extract Ziwei handlers to mcp/tools/ziwei_handlers.py
    - Move `_tool_get_ziwei_chart`, `_tool_get_ziwei_fortune`, `_tool_analyze_ziwei_palace`
    - _Requirements: 1.2_
  - [x] 2.5 Extract Bazi handlers to mcp/tools/bazi_handlers.py
    - Move `_tool_get_bazi_chart`, `_tool_get_bazi_fortune`, `_tool_analyze_bazi_element`
    - _Requirements: 1.2_
  - [x] 2.6 Create tool registry in mcp/tools/__init__.py
    - Implement `ToolRegistry` class for tool registration and lookup
    - _Requirements: 1.2_
  - [x] 2.7 Refactor MingliMCPServer to use new modules
    - Update `mcp/server.py` to use `ProtocolHandler` and `ToolRegistry`
    - Keep `mingli_mcp.py` as thin entry point
    - _Requirements: 1.4, 1.5_
  - [ ]* 2.8 Write unit tests for refactored modules
    - Test `ProtocolHandler` methods
    - Test `ToolRegistry` registration and lookup
    - _Requirements: 2.1_

- [x] 3. Checkpoint - Ensure refactoring works
  - Ensure all tests pass, ask the user if questions arise.

- [-] 4. Implement property-based tests for validators
  - [x] 4.1 Create tests/test_validators_properties.py
    - Set up Hypothesis strategies for dates and time indices
    - _Requirements: 4.1_
  - [ ]* 4.2 Write property test for valid dates in range
    - **Property 1: Valid dates in range are accepted**
    - **Validates: Requirements 4.1**
  - [ ]* 4.3 Write property test for invalid dates outside range
    - **Property 2: Invalid dates outside range are rejected**
    - **Validates: Requirements 3.2**
  - [ ]* 4.4 Write property test for leap year February 29
    - **Property 6: Leap year February 29 validation**
    - **Validates: Requirements 3.5**
  - [ ]* 4.5 Write property test for non-leap year February 29
    - **Property 7: Non-leap year February 29 rejection**
    - **Validates: Requirements 3.6**

- [x] 5. Implement property-based tests for BirthInfo
  - [x] 5.1 Create tests/test_birth_info_properties.py
    - Set up Hypothesis strategies for BirthInfo fields
    - _Requirements: 4.3_
  - [ ]* 5.2 Write property test for serialization round-trip
    - **Property 4: BirthInfo serialization round-trip**
    - **Validates: Requirements 4.3**
  - [ ]* 5.3 Write property test for time index round-trip
    - **Property 3: Time index round-trip consistency**
    - **Validates: Requirements 4.2**

- [x] 6. Implement property-based tests for solar time
  - [x] 6.1 Create tests/test_solar_time_properties.py
    - Set up Hypothesis strategies for longitude values
    - _Requirements: 4.4_
  - [ ]* 6.2 Write property test for solar time offset determinism
    - **Property 5: Solar time offset determinism**
    - **Validates: Requirements 4.4**

- [x] 7. Checkpoint - Ensure property tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement boundary tests
  - [x] 8.1 Create tests/test_boundary_cases.py
    - _Requirements: 3.1, 3.3, 3.4_
  - [x] 8.2 Add date boundary tests
    - Test 1900-01-01, 2100-12-31, 1899-12-31, 2101-01-01
    - _Requirements: 3.1, 3.2_
  - [x] 8.3 Add time_index boundary tests
    - Test time_index 0 (early Zi), 12 (late Zi), -1 (invalid), 13 (invalid)
    - _Requirements: 3.3_
  - [x] 8.4 Add lunar leap month tests
    - Test valid leap months and invalid leap month claims
    - _Requirements: 3.4_

- [x] 9. Improve error messages
  - [x] 9.1 Enhance ValidationError to include invalid value
    - Update `utils/validators.py` to include value in error messages
    - _Requirements: 5.1_
  - [x] 9.2 Enhance missing parameter error messages
    - List all missing required parameters in error
    - _Requirements: 5.2_
  - [x] 9.3 Enhance language error messages
    - Include list of supported languages in error
    - _Requirements: 5.4_
  - [ ]* 9.4 Write property test for error messages containing invalid value
    - **Property 8: Validation errors contain invalid value**
    - **Validates: Requirements 5.1**

- [x] 10. Add MCP server and tool handler tests
  - [x] 10.1 Create tests/test_mcp_server.py
    - Test server initialization
    - Test request routing
    - _Requirements: 2.1_
  - [x] 10.2 Add protocol method tests
    - Test initialize, tools/list, prompts/list, resources/list
    - _Requirements: 2.1_
  - [x] 10.3 Create tests/test_tools/test_ziwei_handlers.py
    - Test get_ziwei_chart, get_ziwei_fortune, analyze_ziwei_palace
    - _Requirements: 2.2_
  - [x] 10.4 Create tests/test_tools/test_bazi_handlers.py
    - Test get_bazi_chart, get_bazi_fortune, analyze_bazi_element
    - _Requirements: 2.2_

- [x] 11. Add formatter tests
  - [x] 11.1 Create tests/test_formatters.py
    - Test JSON output format
    - Test Markdown output format
    - _Requirements: 2.4_
  - [x] 11.2 Add Ziwei formatter tests
    - Test chart, fortune, palace formatting
    - _Requirements: 2.4_
  - [x] 11.3 Add Bazi formatter tests
    - Test chart, fortune, element formatting
    - _Requirements: 2.4_

- [x] 12. Add transport layer tests
  - [x] 12.1 Enhance tests/test_stdio_transport.py
    - Test message sending and receiving
    - Test error handling
    - _Requirements: 2.3_

- [x] 13. Final Checkpoint - Verify coverage target
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest --cov=. --cov-report=term-missing` and verify 80%+ coverage

