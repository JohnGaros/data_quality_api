# Specifications Directory

This directory contains a hierarchical planning system for tracking platform development from project roadmap down to individual feature tasks.

## Hierarchical Structure

**Project → Milestones → Epics → Features**

```
specs/
├── PROJECT_ROADMAP.md              # Top-level project tracking
├── .checkpoints/                   # Runtime state (gitignored)
│   ├── current.json                # Active feature pointer
│   └── progress_summary.json       # Aggregated progress data
│
├── drafts/                         # Brainstorming pipeline (NEW)
│   ├── IDEAS.md                    # Quick idea capture log
│   ├── .session_notes              # Session scratch (gitignored)
│   ├── .drafts_index.json          # Draft registry (gitignored)
│   └── explorations/               # Draft specs
│       └── DRAFT_*.md              # Individual exploration docs
│
└── milestones/                     # Major project phases
    ├── M1_MVP_FOUNDATION/
    │   ├── MILESTONE.md            # Phase overview and goals
    │   ├── PROGRESS.md             # Auto-generated progress tracking
    │   └── epics/
    │       ├── E1_CORE_VALIDATION/
    │       │   ├── EPIC.md         # Multi-feature initiative
    │       │   ├── PROGRESS.md     # Auto-generated epic progress
    │       │   └── features/
    │       │       └── e2e_file_testing/
    │       │           ├── IMPLEMENTATION.md
    │       │           ├── TASKS.md
    │       │           └── .checkpoint    # Progress state (gitignored)
    │       │
    │       └── E2_METADATA_LINEAGE/
    │           └── features/
    │               └── ...
    │
    ├── M2_SECURITY_COMPLIANCE/
    │   └── epics/
    │       └── E3_RBAC_GDPR/
    │           └── features/
    │               └── ...
    │
    └── M3_SCALE_OPERATIONS/
        └── epics/
            └── E4_OPERATIONS/
                └── features/
                    └── ...
```

## Hierarchy Levels

| Level | Purpose | Contains | Tracked By |
|-------|---------|----------|------------|
| **Project** | Overall production readiness | Milestones | PROJECT_ROADMAP.md |
| **Milestone** | Major phase (MVP, Security, Scale) | Epics + goals | MILESTONE.md + PROGRESS.md |
| **Epic** | Multi-feature initiative | Related features | EPIC.md + PROGRESS.md |
| **Feature** | Atomic implementation unit | Tasks by phase | IMPLEMENTATION.md + TASKS.md + .checkpoint |
| **Draft** | Pre-promotion exploration | Research notes | DRAFT_*.md + .drafts_index.json |
| **Idea** | Quick captured thought | Single entry | IDEAS.md |

## Planning System Commands

**After `/clear` operations:**

```bash
# Restore context in < 10 seconds
/planning/resume
```

**Track progress:**

```bash
# Show current feature status
/planning/status

# View project-wide dashboard
/planning/progress

# Update checkpoint
/planning/checkpoint --complete-task "description"
/planning/checkpoint --next-phase
/planning/checkpoint --add-blocker "reason"
/planning/checkpoint --complete-feature
```

**Brainstorming commands:**

```bash
# Capture quick idea
/planning/idea <description>

# Create/open draft exploration
/planning/draft IDEA-001
/planning/draft advanced_caching

# List all drafts and ideas
/planning/drafts

# Promote draft to epic/feature
/planning/promote advanced_caching

# Session scratch notes
/planning/session-notes
/planning/session-notes --add "note"
/planning/session-notes --context "current focus"
```

## Current Milestones

### M1: MVP Foundation [In Progress] - ~20%

**Target:** 2025-12-30

Core validation pipeline with cleansing, profiling, validation, and metadata tracking.

**Epics:**
- **E1: Core Validation** (In Progress) - ~25%
  - e2e_file_testing: Excel/CSV file testing infrastructure
  - core_rule_engine: Rule engine and validation logic (Planned)
  - api_upload_endpoints: FastAPI upload routes (Planned)

- **E2: Metadata & Lineage** (Not Started) - 0%
  - metadata_registry: Job lineage and event tracking (Planned)
  - audit_trail: Immutable audit and compliance tags (Planned)

### M2: Security & Compliance [Not Started] - 0%

**Target:** 2026-01-31

Azure AD authentication, RBAC, GDPR compliance, retention policies.

**Epics:**
- **E3: RBAC & GDPR** (Not Started) - 0%
  - azure_ad_integration (Planned)
  - gdpr_compliance (Planned)
  - storage_retention (Planned)

### M3: Scale & Operations [Not Started] - 0%

**Target:** 2026-02-28

Performance, Azure Blob storage, job orchestration, observability, CI/CD.

**Epics:**
- **E4: Operations** (Not Started) - 0%
  - tenant_management (Planned)
  - observability (Planned)
  - ci_cd_pipelines (Planned)
  - azure_blob_storage (Planned)

## Feature Structure

Each feature contains:

### IMPLEMENTATION.md

- **Quick Reference** (first 50 lines) - Overview, key files, architecture context
- **Architecture Context** - Links to relevant docs/ARCHITECTURE.md sections
- **Phase-by-Phase Steps** - Detailed implementation guidance
- **Code Examples** - Complete working code snippets
- **Success Criteria** - Definition of done
- **Troubleshooting** - Common issues and solutions

### TASKS.md

- **Checkbox List** - Organized by phase (typically 7 phases)
- **Quick Commands** - Bash commands for common operations
- **Verification Steps** - How to test each phase
- **Time Estimates** - Expected duration per phase

### .checkpoint (YAML, gitignored)

Runtime state tracking:

```yaml
feature_id: e2e_file_testing
feature_name: "E2E File Testing"
status: in_progress  # not_started | in_progress | completed | blocked
current_phase: 3
last_updated: 2025-11-27T14:30:00Z
session_started: 2025-11-27T09:00:00Z
time_spent_minutes: 150

phases:
  - phase: 1
    name: "File Structure & Sample Data"
    status: completed
    completed_at: 2025-11-26T10:00:00Z
    tasks_completed: 10
    tasks_total: 10
    time_spent_minutes: 45

  - phase: 2
    name: "File Loaders"
    status: in_progress
    started_at: 2025-11-27T09:00:00Z
    tasks_completed: 2
    tasks_total: 3
    time_spent_minutes: 15

blockers: []
notes: "Implementing load_excel_to_dict_list() next"
```

## Context Restoration After /clear

**Problem:** After `/clear`, Claude loses all context about what you were working on.

**Solution:** Checkpoint-based resumption with minimal context loading.

### Before Checkpoints (Old Way)

1. User runs `/clear` to reset conversation
2. Claude has no memory of active feature
3. User manually:
   - Opens specs/ directory
   - Finds feature subdirectory
   - Reads IMPLEMENTATION.md (570 lines)
   - Reads TASKS.md (340 lines)
   - Remembers which task was next
4. **Time wasted:** 2-5 minutes

### With Checkpoints (New Way)

1. User runs `/clear`
2. User types: `/planning/resume`
3. Claude:
   - Reads `current.json` (1 line) → finds active feature
   - Reads `.checkpoint` (30 lines) → gets state
   - Reads IMPLEMENTATION.md lines 1-50 only (Quick Reference)
   - Reads TASKS.md current phase only (20 lines)
   - Displays resume summary with next task
4. **Total lines read:** ~100 lines (vs 15,000+ for full architecture)
5. **Time to execute:** 5-10 seconds
6. **User orientation:** Immediate - knows exactly what to do next

## Progress Tracking

### Automatic Time Tracking

Every checkpoint update tracks time automatically:

1. Session duration = `current_time - session_started`
2. Add to phase: `phase.time_spent_minutes += session_duration`
3. Add to feature: `feature.time_spent_minutes += session_duration`
4. Reset session: `session_started = current_time`

No manual time entry required. Provides automatic estimation improvement over time.

### Progress Dashboard

Run `python scripts/parse_checkpoints.py` or `/planning/progress` to see:

```
================================================================================
DATA QUALITY PLATFORM - PROGRESS DASHBOARD
================================================================================

SUMMARY
Total Features:     3
  Completed:        1
  In Progress:      1
  Blocked:          0
  Not Started:      1
Total Time Spent:   4h 30m

Overall Progress:   42.3%

================================================================================
MILESTONE: M1_MVP_FOUNDATION
================================================================================

Epic: E1_CORE_VALIDATION (42.3% - 4h 30m)
  ✓ e2e_file_testing              100.0%  Completed     3h 15m
  → core_rule_engine               25.0%  Phase 2       1h 15m
  ○ api_upload_endpoints            0.0%  Not started   0 min
```

## Adding New Features

When planning a new feature:

1. **Determine placement:** Which milestone and epic?
2. **Create directory:** `specs/milestones/{MILESTONE}/epics/{EPIC}/features/{feature_name}/`
3. **Create files:**
   - `IMPLEMENTATION.md` (use template with Quick Reference section)
   - `TASKS.md` (organize by phases, typically 7)
   - `.checkpoint` (initialize with all phases as not_started)
4. **Update parent docs:**
   - Add feature to epic's EPIC.md
   - Update milestone's MILESTONE.md if new epic
   - Update PROJECT_ROADMAP.md if new milestone

## File Naming Conventions

- **Directories:** lowercase with underscores (e.g., `e2e_file_testing`)
- **Feature files:** `IMPLEMENTATION.md`, `TASKS.md` (consistent naming)
- **Milestone files:** `MILESTONE.md`, `PROGRESS.md`
- **Epic files:** `EPIC.md`, `PROGRESS.md`
- **Checkpoint files:** `.checkpoint` (hidden, gitignored)

## Architecture Integration

Feature IMPLEMENTATION.md files link to relevant architecture docs:

```markdown
## Architecture Context

This feature implements components described in:

- **Primary:** docs/ARCHITECTURE.md - Section 4.3 (Cleansing Module)
- **Contracts:** docs/CONTRACT_DRIVEN_ARCHITECTURE.md - CDA Principles
- **Metadata:** docs/METADATA_LAYER_SPEC.md - Lineage recording
- **Security:** docs/SECURITY_GUIDE.md - Tenant isolation

**Modules touched:**
- src/dq_cleansing/ - Core implementation
- src/dq_metadata/ - Lineage recording
- tests/integration/ - E2E tests
```

This connects planning docs to architecture docs without duplication.

## Migration from Old Structure

The old flat structure (`specs/e2e_file_testing/`) has been migrated to the new hierarchy:

**Old:** `specs/e2e_file_testing/E2E_FILE_TESTING_IMPLEMENTATION.md`
**New:** `specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/e2e_file_testing/IMPLEMENTATION.md`

Benefits of new structure:
- Clear project phase visibility (milestones)
- Related features grouped (epics)
- Progress tracking at all levels
- Context restoration after `/clear`
- Automatic time tracking and estimation improvement

## Success Metrics

**Quantitative:**
- Context restoration time: < 10 seconds after /clear
- Context size loaded: < 500 lines (vs 15,000+ full reload)
- Checkpoint accuracy: 100% parseable by script
- Progress calculation: Accurate within 1%

**Qualitative:**
- User feels oriented after `/planning/resume`
- No manual navigation needed
- Progress visible at all levels
- Spec creation fast with templates
