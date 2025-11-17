<!--
SYNC IMPACT REPORT
==================
Version Change: Template → 1.0.0
Change Type: MAJOR (Initial Constitution)
Ratification Date: 2025-11-06
Last Amended: 2025-11-06

Modified Principles:
- PRINCIPLE_1: Zero Tolerance for Technical Debt
- PRINCIPLE_2: No Version Fragmentation
- PRINCIPLE_3: Simplicity First (YAGNI, KISS, SOLID)
- PRINCIPLE_4: Test-Driven Development (TDD)
- PRINCIPLE_5: Root Cause Only - No Workarounds
- PRINCIPLE_6: Context-Aware Development
- PRINCIPLE_7: Code Hygiene

Added Sections:
- Development Standards (Python-specific standards)
- Code Quality Gates (mandatory checks before merge)

Removed Sections: None (initial creation)

Templates Requiring Updates:
✅ plan-template.md - Constitution Check section references this file
✅ spec-template.md - Requirements align with TDD principle
✅ tasks-template.md - Test-first workflow aligns with TDD principle
✅ All command files reviewed - No agent-specific references except in speckit.constitution.md (acceptable)

Follow-up TODOs: None
-->

# BFF-Temporal Constitution

## Core Principles

### I. Zero Tolerance for Technical Debt

**DO NOT live with broken windows.** If there is a problem, find a proper solution to fix it or ask for help. Technical debt compounds; addressing issues immediately prevents systemic degradation.

**Rationale**: Deferred problems multiply in complexity and cost. Immediate resolution maintains system integrity and team velocity.

### II. No Version Fragmentation

**NEVER use references to v3, v2, v1 in the code.** We maintain only one main version of code. We do not need backward compatibility unless explicitly required.

**Rationale**: Version fragmentation creates maintenance burden and cognitive overhead. Single version simplifies reasoning and reduces branching complexity.

### III. Simplicity First (YAGNI, KISS, SOLID)

**Respect YAGNI (You Aren't Gonna Need It), KISS (Keep It Simple, Stupid), and SOLID principles.** Do not include:
- Timelines in plans or specifications (all coding is agent-performed)
- Concerns about backward compatibility or step-by-step migrations
- Performance concerns unless explicitly requested by the user

**Rationale**: Premature optimization and speculative features waste resources. Build what is needed now with clean architecture that can evolve.

### IV. Test-Driven Development (TDD)

**Before fixing any regression or bug, follow TDD process**:
1. Write a test that reproduces the bug
2. Run the test and verify it fails
3. Fix the code
4. Iterate until the test passes

After resolving any issue, bug, or regression, ask the user if a regression detection test should be created.

**Rationale**: TDD ensures problems are reproducible, solutions are validated, and regressions are prevented. Tests serve as executable documentation of intended behavior.

### V. Root Cause Only - No Workarounds

**CRITICAL: When fixing failing tests, NEVER use workarounds, hacks, or temporary solutions.** Always fix the root cause properly. If you cannot fix it properly, STOP and ask for help. Workarounds are NEVER acceptable.

**Rationale**: Workarounds accumulate as technical debt (see Principle I). Root cause fixes prevent cascading failures and maintain system predictability.

### VI. Context-Aware Development

**Use context7 MCP to get information on how to work with specific libraries** (e.g., "textual", "temporal.io", etc.). Leverage available tools and documentation before making assumptions.

**Rationale**: Context-aware tools provide authoritative, up-to-date information that prevents misuse patterns and accelerates correct implementation.

### VII. Code Hygiene

**When working with code**:
- Detect unused code and delete it
- When detecting overengineered code, report it to the user
- Maintain clarity and simplicity

**Rationale**: Dead code creates confusion and false dependencies. Overengineering obscures intent. Clean code communicates clearly.

## Development Standards

### Python Style Guide

This project follows Python-specific standards:

- **PEP-8**: Python Enhancement Proposal 8 - Style Guide for Python Code
  - Reference: https://peps.python.org/pep-0008/
- **Google Python Style Guide**: Additional conventions for clarity and consistency
  - Reference: https://google.github.io/styleguide/pyguide.html

All Python code MUST adhere to both style guides. Use automated linting tools (e.g., `ruff`, `black`, `pylint`) to enforce compliance.

## Code Quality Gates

Before any merge or commit, verify:

1. **Constitution Compliance**: All principles respected
2. **No Broken Windows**: No known issues deferred
3. **No Workarounds**: Only root cause fixes present
4. **Tests Pass**: All tests green, no skipped tests without justification
5. **Style Compliance**: PEP-8 and Google Python Style Guide adherence
6. **Code Hygiene**: No unused code, no overengineering
7. **TDD Evidence**: Bug fixes accompanied by regression tests

Any gate failure MUST be resolved before proceeding. Complexity or exceptions MUST be documented and justified.

## Governance

This constitution supersedes all other practices. Amendments require:
1. Documentation of rationale and impact
2. User approval
3. Semantic version increment (see below)
4. Propagation to dependent templates and command files

**Version Semantics**:
- **MAJOR**: Backward-incompatible governance changes or principle removals/redefinitions
- **MINOR**: New principles added or material expansion of guidance
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

**Compliance Review**: All pull requests, code reviews, and automated checks MUST verify constitution compliance. Violations require either fix or formal amendment.

**Runtime Guidance**: This file provides governance principles. For execution workflows, see individual command files in `.claude/commands/speckit.*.md`.

---

**Version**: 1.0.0 | **Ratified**: 2025-11-06 | **Last Amended**: 2025-11-06
