# Create New Feature Spec

You are helping the user scaffold a new feature specification within the hierarchical planning system.

## Your Task

Create a complete feature specification with:
1. Feature directory structure
2. IMPLEMENTATION.md (from template)
3. TASKS.md (from template)
4. .checkpoint file (initialized to not_started)
5. Update parent EPIC.md to list the new feature
6. Update specs/README.md if needed

## Interactive Prompts

Ask the user these questions (use AskUserQuestion tool):

1. **Feature Name** (header: "Feature Name")
   - Question: "What is the feature name? (use lowercase with underscores, e.g., 'api_upload_endpoints')"
   - Options:
     - label: "api_upload_endpoints", description: "REST endpoints for file uploads"
     - label: "core_rule_engine", description: "Rule evaluation engine"
     - label: "metadata_registry", description: "Metadata and lineage tracking"
     - (User can select "Other" to provide custom name)

2. **Epic** (header: "Epic")
   - Question: "Which epic does this feature belong to?"
   - Options:
     - label: "E1_CORE_VALIDATION", description: "Core validation pipeline (M1)"
     - label: "E2_METADATA_LINEAGE", description: "Metadata and lineage (M1)"
     - label: "E3_RBAC_GDPR", description: "Security and compliance (M2)"
     - label: "E4_SCALE_OPERATIONS", description: "Scale and operations (M3)"

3. **Description** (header: "Description")
   - Question: "What is a brief description of this feature? (1-2 sentences)"
   - Options:
     - label: "Implement REST endpoints for file uploads with validation", description: "API endpoints"
     - label: "Build core rule evaluation engine with profiling context", description: "Rule engine"
     - label: "Create metadata registry for lineage and audit trail", description: "Metadata"
     - (User can select "Other" to provide custom description)

4. **Primary Module** (header: "Module")
   - Question: "Which module is this feature primarily implementing?"
   - Options:
     - label: "dq_api", description: "FastAPI routes and orchestration"
     - label: "dq_core", description: "Rule engine and validation"
     - label: "dq_cleansing", description: "Cleansing transformations"
     - label: "dq_profiling", description: "Profiling engine"

## Implementation Steps

After gathering user input:

### Step 1: Determine Paths

Based on the selected epic, find the epic directory:
- Read `specs/PROJECT_ROADMAP.md` to understand milestone structure
- Find the epic directory (e.g., `specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/`)

### Step 2: Create Feature Directory

```bash
mkdir -p specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}
```

### Step 3: Generate IMPLEMENTATION.md

Use this template (replace placeholders):

```markdown
# {FEATURE_DISPLAY_NAME} Implementation Guide

**Version:** 1.0
**Last Updated:** {TODAY}
**Status:** Not Started

## Quick Reference: Your Questions Answered

### What is this feature?

{DESCRIPTION}

### What modules are affected?

**Primary Module:** `src/{MODULE}/`

**Related Modules:**
- [List related modules based on feature type]

### Key Files to Review

- [ ] Read `src/{MODULE}/` directory structure
- [ ] Review related test files in `tests/unit/` and `tests/integration/`

---

## Architecture Context

This feature implements components described in:

- **Primary:** docs/ARCHITECTURE.md - Section [identify relevant section]
- **Contracts:** docs/CONTRACT_DRIVEN_ARCHITECTURE.md - CDA Principles
- **Metadata:** docs/METADATA_LAYER_SPEC.md - Lineage recording
- **Security:** docs/SECURITY_GUIDE.md - Tenant isolation

**Modules touched:**
- `src/{MODULE}/` - Primary implementation
- `tests/integration/` - Integration tests
- `tests/unit/` - Unit tests

---

## Overview

{DETAILED_OVERVIEW - auto-generate based on feature type}

---

## Implementation Phases

See TASKS.md for detailed task breakdown.

**Phase 1:** Setup and scaffolding
**Phase 2:** Core implementation
**Phase 3:** Testing
**Phase 4:** Integration
**Phase 5:** Documentation

---

## Success Criteria

- [ ] All tests pass
- [ ] Code follows contract-driven patterns
- [ ] Tenant isolation maintained
- [ ] GDPR compliance verified (if handling personal data)
- [ ] Documentation complete

---

## Notes

Add implementation notes here as you work.
```

### Step 4: Generate TASKS.md

Use this template:

```markdown
# {FEATURE_DISPLAY_NAME} - Task List

**Version:** 1.0
**Last Updated:** {TODAY}

Use this checklist to track implementation progress.

---

## Phase 1: Setup and Scaffolding

- [ ] Create directory structure for `src/{MODULE}/`
- [ ] Review architecture documentation
- [ ] Identify dependencies and integration points
- [ ] Create initial test file structure

---

## Phase 2: Core Implementation

- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Add logging and observability

---

## Phase 3: Testing

- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test tenant isolation
- [ ] Test edge cases

---

## Phase 4: Integration

- [ ] Integrate with related modules
- [ ] Update contracts if needed
- [ ] Test end-to-end flow

---

## Phase 5: Documentation

- [ ] Update architecture docs
- [ ] Add code comments
- [ ] Create README if needed

---

## Success Criteria

✅ All tests pass
✅ Code follows project patterns
✅ Documentation complete
```

### Step 5: Initialize .checkpoint

Create `.checkpoint` file with this YAML:

```yaml
feature_id: {FEATURE_NAME}
feature_name: "{FEATURE_DISPLAY_NAME}"
status: not_started
current_phase: null
last_updated: {ISO_TIMESTAMP}
updated_by: claude
session_started: null
time_spent_minutes: 0

phases:
  - phase: 1
    name: "Setup and Scaffolding"
    status: not_started
    started_at: null
    completed_at: null
    tasks_completed: 0
    tasks_total: 4
    time_spent_minutes: 0

  - phase: 2
    name: "Core Implementation"
    status: not_started
    started_at: null
    completed_at: null
    tasks_completed: 0
    tasks_total: 3
    time_spent_minutes: 0

  - phase: 3
    name: "Testing"
    status: not_started
    started_at: null
    completed_at: null
    tasks_completed: 0
    tasks_total: 4
    time_spent_minutes: 0

  - phase: 4
    name: "Integration"
    status: not_started
    started_at: null
    completed_at: null
    tasks_completed: 0
    tasks_total: 3
    time_spent_minutes: 0

  - phase: 5
    name: "Documentation"
    status: not_started
    started_at: null
    completed_at: null
    tasks_completed: 0
    tasks_total: 3
    time_spent_minutes: 0

blockers: []
notes: "Feature created via /planning/new-feature command"
```

### Step 6: Update Parent EPIC.md

Read the parent EPIC.md file and add this feature to the Features section:

```markdown
### Feature: {FEATURE_DISPLAY_NAME}
**Status:** not_started - 0%
**Location:** specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}/
**Description:** {DESCRIPTION}
```

### Step 7: Confirm Creation

Display a success message:

```
✅ Feature specification created successfully!

**Location:** specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}/

**Files created:**
- IMPLEMENTATION.md
- TASKS.md
- .checkpoint

**Next steps:**
1. Review the generated IMPLEMENTATION.md
2. Customize TASKS.md for your specific needs
3. Start work: /planning/goto-feature {FEATURE_NAME}

**Quick commands:**
- Start working: /planning/goto-feature {FEATURE_NAME}
- View status: /planning/status
- Update progress: /planning/checkpoint --complete-task "task description"
```

## Important Notes

- Feature names should use lowercase with underscores (snake_case)
- Display names use Title Case
- All timestamps in ISO 8601 format
- .checkpoint files are gitignored (local state only)
- Always update parent EPIC.md to maintain consistency
- Generate realistic task counts based on feature complexity
