# Requirements Document

## Introduction

This document defines the requirements for improving the code quality, test coverage, and maintainability of the Mingli MCP Server project. The project currently has 18% test coverage and a monolithic main entry file (1389 lines). These improvements aim to achieve 80%+ test coverage, better code organization, and more robust input validation.

## Glossary

- **MCP**: Model Context Protocol - A protocol for AI tool integration
- **Mingli MCP Server**: The fortune-telling MCP server supporting Ziwei (紫微斗数) and Bazi (八字) systems
- **Test Coverage**: The percentage of code lines executed during automated tests
- **Boundary Testing**: Testing edge cases at the limits of valid input ranges
- **Code Refactoring**: Restructuring existing code without changing its external behavior

## Requirements

### Requirement 1: Refactor Main Entry File

**User Story:** As a developer, I want the main entry file to be modular and well-organized, so that I can easily understand, maintain, and extend the codebase.

#### Acceptance Criteria

1. WHEN the mingli_mcp.py file exceeds 500 lines THEN the system SHALL split it into logical modules with clear responsibilities
2. WHEN tool handlers are defined THEN the system SHALL organize them in a separate handlers module
3. WHEN MCP protocol methods are handled THEN the system SHALL organize protocol handling in a dedicated module
4. WHEN the refactoring is complete THEN the system SHALL maintain all existing functionality without breaking changes
5. WHEN importing from refactored modules THEN the system SHALL provide a clean public API through __init__.py exports

### Requirement 2: Improve Test Coverage for Core Modules

**User Story:** As a developer, I want comprehensive test coverage for core modules, so that I can confidently make changes without introducing regressions.

#### Acceptance Criteria

1. WHEN testing the MCP server THEN the system SHALL have tests covering all MCP protocol methods (initialize, tools/list, tools/call)
2. WHEN testing tool handlers THEN the system SHALL have tests for each tool (get_ziwei_chart, get_bazi_chart, etc.)
3. WHEN testing the transport layer THEN the system SHALL have tests for stdio message sending and receiving
4. WHEN testing formatters THEN the system SHALL have tests for both JSON and Markdown output formats
5. WHEN all tests pass THEN the overall test coverage SHALL be at least 80%

### Requirement 3: Implement Boundary Testing for Input Validation

**User Story:** As a user, I want the system to handle edge cases gracefully, so that I receive clear error messages for invalid inputs.

#### Acceptance Criteria

1. WHEN a date at the boundary (1900-01-01 or 2100-12-31) is provided THEN the system SHALL process it correctly or return a clear error
2. WHEN a date outside the supported range is provided THEN the system SHALL return a DateRangeError with a descriptive message
3. WHEN time_index is at boundary values (0 or 12) THEN the system SHALL process early/late Zi hour correctly
4. WHEN a lunar leap month date is provided THEN the system SHALL validate and process it correctly
5. WHEN February 29 in a leap year is provided THEN the system SHALL process it correctly
6. WHEN February 29 in a non-leap year is provided THEN the system SHALL return a ValidationError

### Requirement 4: Add Property-Based Testing for Core Algorithms

**User Story:** As a developer, I want property-based tests for core algorithms, so that I can verify correctness across a wide range of inputs.

#### Acceptance Criteria

1. WHEN testing date validation THEN the system SHALL verify that all valid dates in range are accepted
2. WHEN testing time_index conversion THEN the system SHALL verify round-trip consistency (index to time range and back)
3. WHEN testing birth_info serialization THEN the system SHALL verify that to_dict and from_dict are inverse operations
4. WHEN testing solar time calculation THEN the system SHALL verify that offset calculation is consistent with longitude

### Requirement 5: Improve Error Messages and Validation

**User Story:** As a user, I want clear and actionable error messages, so that I can understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN validation fails THEN the system SHALL return an error message that includes the invalid value and expected format
2. WHEN a required parameter is missing THEN the system SHALL list all missing parameters in the error message
3. WHEN a system error occurs THEN the system SHALL log detailed information while returning a user-friendly message
4. WHEN an unsupported language is requested THEN the system SHALL list all supported languages in the error message

