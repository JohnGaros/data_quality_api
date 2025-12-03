# Brainstorming Extension Design

**Version:** 1.0
**Status:** Design Document
**Purpose:** Enable ideation, exploration, and promotion workflows with continuity across `/clear` operations

---

## Problem Statement

The current planning system excels at **tracking implementation progress** but lacks support for:

1. **Capturing rough ideas** before they're ready for formal specs
2. **Exploring possibilities** without committing to epic/feature structure
3. **Deciding the right home** for promoted ideas (new epic vs. feature in existing epic)
4. **Preserving session notes** that survive `/clear` but don't pollute git history
5. **Resuming brainstorming context** alongside implementation context

---

## Design Goals

| Goal | Metric |
|------|--------|
| Idea capture < 5 seconds | Single command, minimal prompts |
| Draft creation < 30 seconds | Templated, low friction |
| Promotion decision guided | Interactive framework, not guesswork |
| Context restoration includes drafts | Resume shows active ideas/drafts |
| No git pollution | Session state gitignored, ideas optionally tracked |

---

## Directory Structure

```
specs/
├── drafts/                           # Pre-promotion staging area
│   ├── IDEAS.md                      # Quick capture log (git tracked)
│   ├── .session_notes                # Current session scratch (gitignored)
│   ├── .drafts_index.json            # Draft metadata registry (gitignored)
│   │
│   └── explorations/                 # Draft specs for deeper exploration
│       ├── DRAFT_advanced_caching.md
│       ├── DRAFT_realtime_validation.md
│       └── DRAFT_ml_anomaly_detection.md
│
├── .checkpoints/                     # Existing checkpoint system
│   ├── current.json                  # Active feature pointer
│   ├── current_draft.json            # Active draft pointer (NEW)
│   └── progress_summary.json
│
└── milestones/                       # Existing hierarchy (unchanged)
```

---

## File Formats

### IDEAS.md (Git Tracked)

Quick capture log for ideas that may become drafts or features. Append-only format.

```markdown
# Ideas Log

Capture rough ideas here. Promote promising ones with `/planning/draft` or `/planning/promote`.

---

## 2025-12-02

### [IDEA-001] Advanced Caching Layer
**Status:** draft_created
**Tags:** performance, infrastructure
**Created:** 2025-12-02T10:30:00Z

Implement Redis-based caching for frequently accessed contracts and catalog entries.
Could significantly reduce DB load for high-volume tenants.

**Related:** E4_OPERATIONS, profiling performance

---

### [IDEA-002] Real-time Validation Webhooks
**Status:** new
**Tags:** api, integration
**Created:** 2025-12-02T11:15:00Z

Allow external systems to subscribe to validation events in real-time.
Would enable tighter integration with Power Platform and Azure Logic Apps.

**Questions:**
- WebSocket vs Server-Sent Events vs webhook callbacks?
- How does this interact with ActionProfiles?

---
```

**Idea Status Values:**
- `new` - Just captured
- `exploring` - Being actively researched
- `draft_created` - Has a DRAFT_*.md file
- `promoted` - Converted to epic/feature
- `parked` - Intentionally deferred
- `rejected` - Won't implement (with reason)

---

### .session_notes (Gitignored)

Temporary scratch space for current session. Survives `/clear`, cleared on explicit reset.

```yaml
session_id: "2025-12-02T09:00:00Z"
last_updated: "2025-12-02T14:30:00Z"

# Current thinking / working memory
active_context: |
  Exploring caching options for catalog lookups.
  Redis seems overkill for MVP - consider in-memory LRU first.

# Quick notes that don't belong anywhere yet
scratch: |
  - Check how GE handles catalog caching
  - Ask about Azure Cache for Redis pricing
  - tenant isolation for cache keys?

# Links to related files being explored
exploring_files:
  - src/dq_catalog/repository.py
  - docs/ARCHITECTURE.md#caching

# Parking lot - things to not forget
parking_lot:
  - "Update CLAUDE.md with new planning commands"
  - "Test checkpoint restore after multi-day gap"
```

---

### .drafts_index.json (Gitignored)

Registry of draft specs with metadata for quick lookup.

```json
{
  "drafts": [
    {
      "draft_id": "advanced_caching",
      "file": "explorations/DRAFT_advanced_caching.md",
      "status": "exploring",
      "created": "2025-12-02T10:45:00Z",
      "last_updated": "2025-12-02T14:30:00Z",
      "source_idea": "IDEA-001",
      "tags": ["performance", "infrastructure"],
      "potential_home": {
        "type": "feature",
        "milestone": "M3_SCALE_OPERATIONS",
        "epic": "E4_OPERATIONS"
      },
      "time_spent_minutes": 45,
      "session_started": "2025-12-02T14:00:00Z"
    }
  ],
  "active_draft": "advanced_caching"
}
```

---

### DRAFT_*.md (Git Tracked - Optional)

Exploration specs that may become features or epics. More structured than ideas, less formal than IMPLEMENTATION.md.

```markdown
# DRAFT: Advanced Caching Layer

**Draft ID:** advanced_caching
**Status:** exploring
**Source Idea:** IDEA-001
**Created:** 2025-12-02
**Last Updated:** 2025-12-02

---

## Problem

Contract and catalog lookups hit the database on every request. For high-volume
tenants processing thousands of files, this creates unnecessary load.

## Hypothesis

Adding a caching layer could reduce DB queries by 80%+ for read-heavy operations
without impacting data freshness for writes.

---

## Exploration Notes

### Option A: In-Memory LRU Cache
- Simple, no infrastructure
- Per-process, not shared across workers
- Good for: single-instance deployments, MVP

### Option B: Redis Cache
- Shared across workers
- Requires infrastructure
- Good for: production multi-instance

### Option C: Postgres Materialized Views
- No new infrastructure
- Limited flexibility
- Good for: specific query patterns

---

## Questions to Answer

- [ ] What's the current query volume per tenant?
- [ ] What's the cache invalidation strategy for contract updates?
- [ ] How does multi-tenancy affect cache key design?
- [ ] What's the memory budget for in-memory caching?

## Research Done

- [x] Reviewed existing repository patterns
- [ ] Benchmarked current query latency
- [ ] Tested Redis locally

---

## Potential Home

**If promoted, this would likely become:**

- **Type:** Feature (not epic-sized)
- **Milestone:** M3_SCALE_OPERATIONS
- **Epic:** E4_OPERATIONS
- **Rationale:** Infrastructure optimization, not core functionality

---

## Decision Criteria for Promotion

- [ ] Clear problem statement with data
- [ ] Chosen approach (A, B, or C)
- [ ] Estimated effort (small/medium/large)
- [ ] Dependencies identified
- [ ] No blocking questions remaining

---

## Session Log

### 2025-12-02 - Initial exploration (45 min)
- Created draft from IDEA-001
- Reviewed repository patterns
- Identified three options
- Need: benchmark data before deciding

---
```

---

## New Commands

### /planning/idea

**Purpose:** Quick capture of a rough idea (< 5 seconds)

**File:** `.claude/planning/idea.md`

```markdown
# Capture New Idea

You are helping the user quickly capture a new idea to the IDEAS.md log.

## Your Task

1. Parse the idea description from command arguments or prompt for it
2. Generate a unique IDEA-NNN ID (increment from last ID in file)
3. Append to `specs/drafts/IDEAS.md` using the standard format
4. Optionally add tags if mentioned
5. Confirm capture with next steps

## Interactive Flow

If no description provided in command:

```
What's the idea? (1-2 sentences)
> [user input]

Tags? (comma-separated, optional - press Enter to skip)
> [user input or empty]
```

## Append Format

```markdown
---

### [IDEA-NNN] {Title extracted from first sentence}
**Status:** new
**Tags:** {tags or "untagged"}
**Created:** {ISO timestamp}

{Full description}

---
```

## Output

```
✅ Captured: IDEA-{NNN} - {Title}

Next steps:
- Explore further: /planning/draft IDEA-{NNN}
- View all ideas: Read specs/drafts/IDEAS.md
- Promote directly: /planning/promote IDEA-{NNN}
```

## Usage Examples

```bash
# With inline description
/planning/idea Add caching for catalog lookups to reduce DB load

# Interactive mode
/planning/idea
> What's the idea? Implement real-time validation webhooks for external integrations
> Tags? api, integration
```
```

---

### /planning/draft

**Purpose:** Create or open a draft exploration spec

**File:** `.claude/planning/draft.md`

```markdown
# Create or Open Draft

You are helping the user create a new draft exploration spec or continue working on an existing one.

## Your Task

### If creating new draft (from idea or scratch):

1. If IDEA-NNN provided, read that idea from IDEAS.md
2. Create `specs/drafts/explorations/DRAFT_{slug}.md` from template
3. Update `.drafts_index.json` with new draft entry
4. Update IDEAS.md status to `draft_created` if from idea
5. Set as active draft in `specs/.checkpoints/current_draft.json`
6. Display draft with suggested exploration steps

### If opening existing draft:

1. Find draft by name/ID in `.drafts_index.json`
2. Set as active draft
3. Load draft content and show current state
4. Resume time tracking

## Interactive Prompts (for new draft)

```
Draft title: (e.g., "Advanced Caching Layer")
> [user input]

Brief problem statement:
> [user input]

Potential home - what type? (use AskUserQuestion)
Options:
- "Unknown yet" - Still exploring
- "Feature" - Single implementation unit
- "Epic" - Multi-feature initiative
- "Enhancement" - Modify existing feature
```

## Template for New Draft

[See DRAFT_*.md format above]

## Output

```
📝 Draft created: DRAFT_{slug}.md

Location: specs/drafts/explorations/DRAFT_{slug}.md
Status: exploring
Source: IDEA-{NNN} (if applicable)

## Quick Reference

{First 20 lines of draft}

## Suggested Next Steps

1. Fill in exploration notes with options
2. List questions to answer
3. Research and check off items
4. When ready: /planning/promote {slug}

## Commands

- Update notes: Edit the draft file directly
- Add session log: /planning/draft --log "notes"
- View all drafts: /planning/drafts
- Switch draft: /planning/draft {other_slug}
- Promote: /planning/promote {slug}
```

## Usage Examples

```bash
# Create from idea
/planning/draft IDEA-001

# Create from scratch
/planning/draft

# Open existing draft
/planning/draft advanced_caching

# Add session log entry
/planning/draft --log "Benchmarked queries - 50ms avg, 200ms p99"
```
```

---

### /planning/promote

**Purpose:** Convert a draft or idea into an epic or feature with guided decision-making

**File:** `.claude/planning/promote.md`

```markdown
# Promote Draft or Idea

You are helping the user convert a draft exploration or idea into a formal epic or feature specification.

## Your Task

1. Load the draft/idea content
2. Validate promotion readiness (decision criteria if draft)
3. Guide the user through placement decision
4. Create the appropriate spec (epic or feature)
5. Update source (draft/idea) status to `promoted`
6. Optionally archive or delete the draft

## Promotion Readiness Check (for drafts)

Before promoting, verify:
- [ ] Problem statement is clear
- [ ] Approach is decided (not still exploring options)
- [ ] Estimated scope is known (small/medium/large)
- [ ] No blocking questions remain
- [ ] Dependencies identified

If not ready:
```
⚠️  This draft may not be ready for promotion.

Incomplete items:
- [ ] Approach not decided - still has multiple options
- [ ] 2 blocking questions unanswered

Options:
1. Promote anyway (may need revision)
2. Continue exploration
3. Cancel
```

## Placement Decision Framework

Use AskUserQuestion with this framework:

### Question 1: Scope Assessment

```
How big is this work?

Options:
- "Small" - 1-2 days, single focus area
- "Medium" - 1-2 weeks, touches multiple files/modules
- "Large" - 2+ weeks, multiple distinct deliverables
- "Uncertain" - Need more exploration
```

### Question 2: Deliverable Structure

```
How many distinct deliverables are there?

Options:
- "One" - Single cohesive implementation
- "2-3 related" - Few related pieces, one goal
- "4+ distinct" - Multiple separate but related features
- "Uncertain" - Structure not clear yet
```

### Question 3: Existing Home Check

```
Does this fit within an existing epic?

Options:
- [List existing epics with descriptions]
- "New epic needed" - Doesn't fit existing structure
- "Not sure" - Need guidance
```

## Decision Matrix

| Scope | Deliverables | Existing Epic? | → Result |
|-------|--------------|----------------|----------|
| Small | One | Yes | Feature in existing epic |
| Small | One | No | Feature in new epic (or standalone) |
| Medium | One | Yes | Feature in existing epic |
| Medium | 2-3 | Yes | Feature (may split later) |
| Medium | 2-3 | No | New epic with features |
| Large | 4+ | N/A | New epic with multiple features |
| Any | Uncertain | N/A | Continue as draft |

## Execution

Based on decision:

### If Feature in Existing Epic:
1. Run `/planning/new-feature` logic with pre-filled values
2. Populate IMPLEMENTATION.md from draft content
3. Generate TASKS.md from draft questions/research items

### If New Epic:
1. Run `/planning/new-epic` logic with pre-filled values
2. Optionally create initial feature(s) within epic
3. Populate EPIC.md from draft problem statement

### If Continue as Draft:
1. Update draft with new insights from decision process
2. Suggest specific items to resolve

## Post-Promotion

1. Update draft status to `promoted`
2. Update idea status to `promoted` (if applicable)
3. Add promotion metadata:
   ```yaml
   promoted_to:
     type: feature
     path: specs/milestones/M3.../features/caching/
     date: 2025-12-02T15:00:00Z
   ```
4. Ask: Archive draft or keep for reference?

## Output

```
🎉 Promoted: {title}

**Created:** Feature in E4_OPERATIONS
**Location:** specs/milestones/M3_SCALE_OPERATIONS/epics/E4_OPERATIONS/features/advanced_caching/

**Files created:**
- IMPLEMENTATION.md (populated from draft)
- TASKS.md (5 phases, 18 tasks)
- .checkpoint (initialized)

**Draft status:** Archived → specs/drafts/archive/DRAFT_advanced_caching.md

**Next steps:**
1. Review generated IMPLEMENTATION.md
2. Customize TASKS.md for your workflow
3. Start work: /planning/goto-feature advanced_caching
```

## Usage Examples

```bash
# Promote a draft
/planning/promote advanced_caching

# Promote an idea directly (creates minimal feature)
/planning/promote IDEA-002

# Promote with pre-selected destination
/planning/promote advanced_caching --epic E4_OPERATIONS --milestone M3_SCALE_OPERATIONS
```
```

---

### /planning/session-notes

**Purpose:** Manage session scratch notes that survive `/clear`

**File:** `.claude/planning/session-notes.md`

```markdown
# Session Notes Management

You are helping the user manage session scratch notes that persist across `/clear` operations.

## Your Task

Handle these operations:

### View current notes (default)
```bash
/planning/session-notes
```
- Read `specs/drafts/.session_notes`
- Display formatted content
- Show time since last update

### Add to scratch
```bash
/planning/session-notes --add "note text"
```
- Append to `scratch` section
- Update `last_updated`

### Update active context
```bash
/planning/session-notes --context "new context"
```
- Replace `active_context` section
- Useful when switching focus

### Add to parking lot
```bash
/planning/session-notes --park "thing to not forget"
```
- Append to `parking_lot` list

### Clear notes (new session)
```bash
/planning/session-notes --clear
```
- Archive current notes to `specs/drafts/.session_notes_archive/`
- Create fresh `.session_notes`

### Add exploring file
```bash
/planning/session-notes --exploring "path/to/file"
```
- Add to `exploring_files` list

## File Format

See .session_notes format in Directory Structure section above.

## Output Examples

### View
```
## Session Notes

**Session started:** 2025-12-02T09:00:00Z (5h 30m ago)
**Last updated:** 2025-12-02T14:30:00Z (2m ago)

### Active Context
Exploring caching options for catalog lookups.
Redis seems overkill for MVP - consider in-memory LRU first.

### Scratch
- Check how GE handles catalog caching
- Ask about Azure Cache for Redis pricing
- tenant isolation for cache keys?

### Exploring Files
- src/dq_catalog/repository.py
- docs/ARCHITECTURE.md#caching

### Parking Lot
- Update CLAUDE.md with new planning commands
- Test checkpoint restore after multi-day gap

---
Commands:
- Add note: /planning/session-notes --add "note"
- Update context: /planning/session-notes --context "new focus"
- Park item: /planning/session-notes --park "reminder"
- Clear session: /planning/session-notes --clear
```

### Add
```
✅ Added to scratch:
"Benchmark shows 50ms avg query time"

Total scratch items: 4
```
```

---

### /planning/drafts

**Purpose:** List all drafts with status

**File:** `.claude/planning/drafts.md`

```markdown
# List All Drafts

You are showing the user an overview of all drafts in the exploration pipeline.

## Your Task

1. Read `specs/drafts/.drafts_index.json`
2. Read `specs/drafts/IDEAS.md` for idea counts
3. Display organized summary

## Output Format

```
## Drafts & Ideas Pipeline

### Active Draft
→ advanced_caching (exploring) - 45 min spent
  Potential: Feature in E4_OPERATIONS

### All Drafts (3)

| Draft | Status | Time | Potential Home |
|-------|--------|------|----------------|
| → advanced_caching | exploring | 45m | Feature/E4_OPERATIONS |
| realtime_validation | new | 0m | Unknown |
| ml_anomaly_detection | parked | 2h | Epic/M3 |

### Ideas Summary

- New: 3
- Exploring: 1 (→ draft)
- Draft Created: 2
- Promoted: 5
- Parked: 2

### Recent Ideas (new status)

- IDEA-008: Batch validation API endpoint
- IDEA-007: Contract diff visualization
- IDEA-006: Slack integration for alerts

---

Commands:
- View ideas: Read specs/drafts/IDEAS.md
- Create draft: /planning/draft
- Open draft: /planning/draft {name}
- Promote: /planning/promote {name}
- Capture idea: /planning/idea
```
```

---

## Updated /planning/resume

Extend the existing resume command to include brainstorming context.

**Changes to `.claude/planning/resume.md`:**

```markdown
# Restore context after /clear (UPDATED)

[...existing header...]

## Your Task (Updated)

1. Read `specs/.checkpoints/current.json` for active feature
2. **NEW:** Read `specs/.checkpoints/current_draft.json` for active draft
3. **NEW:** Read `specs/drafts/.session_notes` for session context
4. Read feature checkpoint and minimal context (existing logic)
5. **NEW:** Include draft/ideation summary in output

## Updated Output Format

```
## Resuming Work Context

### Implementation Context

Last updated: [timestamp] ([relative time] ago)
Feature: [feature_name]
Status: [status] - [progress]% complete
Phase [N]: [phase_name] - [tasks_completed]/[tasks_total] tasks

### Current Phase Checklist
[existing checklist output]

---

### Brainstorming Context (NEW SECTION)

**Active Draft:** {draft_name} (if any)
Status: {status}
Time spent: {minutes}m
Potential home: {type} in {epic}

**Session Notes:** (if any)
{First 3 lines of active_context}

**Parking Lot:** {count} items
- {first item}
- {second item}
[...]

---

### Quick Commands

**Implementation:**
- Mark task complete: /planning/checkpoint --complete-task "..."
- Next phase: /planning/checkpoint --next-phase

**Brainstorming:**
- View draft: /planning/draft {active_draft}
- Session notes: /planning/session-notes
- Capture idea: /planning/idea
- All drafts: /planning/drafts
```
```

---

## Workflow Examples

### Example 1: Quick Idea Capture During Implementation

```bash
# Working on a feature, have a tangential idea
/planning/idea Add webhook support for real-time validation events

# Continue working on current feature
# The idea is saved, won't forget it

# Later, after /clear
/planning/resume
# Shows both implementation context AND "1 new idea captured today"
```

### Example 2: Dedicated Exploration Session

```bash
# Start exploration
/planning/draft
> Title: ML-based Anomaly Detection
> Problem: Rule-based validation misses novel data quality issues
> Type: Unknown yet

# Explore and take notes
/planning/session-notes --context "Researching ML approaches for anomaly detection"
/planning/session-notes --add "Check Great Expectations anomaly plugins"
/planning/session-notes --exploring "src/dq_profiling/engine.py"

# After /clear
/planning/resume
# Shows active draft and session notes

# When ready to decide
/planning/promote ml_anomaly_detection
# Guided through: This is Large + 4+ deliverables → New Epic
```

### Example 3: Idea → Draft → Feature Pipeline

```bash
# Day 1: Capture idea
/planning/idea Implement contract versioning with diff visualization

# Day 2: Explore as draft
/planning/draft IDEA-003
# Creates DRAFT_contract_versioning.md
# Explore options, answer questions

# Day 3: Ready to implement
/planning/promote contract_versioning
# Decision: Medium scope, single deliverable, fits E1_CORE_VALIDATION
# Creates feature in existing epic

# Day 4: Start implementation
/planning/goto-feature contract_versioning
```

---

## Integration with Existing System

### Backward Compatibility

- All existing commands work unchanged
- New files are additive (no modifications to existing structure)
- `/planning/resume` gracefully handles missing brainstorming files

### Git Strategy

**Tracked (shared with team):**
- `specs/drafts/IDEAS.md` - Ideas are shared knowledge
- `specs/drafts/explorations/DRAFT_*.md` - Drafts can be collaborative

**Gitignored (personal/session state):**
- `specs/drafts/.session_notes` - Personal scratch
- `specs/drafts/.drafts_index.json` - Local registry
- `specs/.checkpoints/current_draft.json` - Active draft pointer

### .gitignore Additions

```gitignore
# Brainstorming session state
specs/drafts/.session_notes
specs/drafts/.session_notes_archive/
specs/drafts/.drafts_index.json
specs/.checkpoints/current_draft.json
```

---

## Implementation Plan

### Phase 1: Directory Structure & Core Files
1. Create `specs/drafts/` directory
2. Create `specs/drafts/explorations/` directory
3. Initialize `IDEAS.md` with header template
4. Add `.gitignore` entries

### Phase 2: Idea Capture
1. Create `.claude/planning/idea.md` command
2. Implement ID generation and append logic
3. Test idea capture workflow

### Phase 3: Draft Management
1. Create `.claude/planning/draft.md` command
2. Create `.claude/planning/drafts.md` command
3. Implement draft index management
4. Create DRAFT template

### Phase 4: Session Notes
1. Create `.claude/planning/session-notes.md` command
2. Implement YAML read/write for session notes
3. Add archive functionality

### Phase 5: Promotion Workflow
1. Create `.claude/planning/promote.md` command
2. Implement decision framework with AskUserQuestion
3. Integrate with existing `/planning/new-feature` and `/planning/new-epic`
4. Add status updates to drafts/ideas

### Phase 6: Resume Integration
1. Update `.claude/planning/resume.md`
2. Add brainstorming context section
3. Handle missing files gracefully
4. Test full workflow with `/clear`

### Phase 7: Documentation & Polish
1. Update `.claude/planning/README.md`
2. Update `specs/README.md`
3. Add workflow examples to `specs/WORKFLOW_EXAMPLES.md`
4. Update `CLAUDE.md` with new commands

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Idea capture time | < 5 seconds |
| Draft creation time | < 30 seconds |
| Resume includes brainstorming | 100% when drafts/notes exist |
| Promotion decision guided | Interactive framework used |
| No session state in git | .gitignore verified |
| Backward compatible | All existing commands unchanged |

---

## Open Questions

1. **Should IDEAS.md be date-sectioned or flat?**
   - Current design: Date-sectioned for easy scanning
   - Alternative: Flat with sort/filter commands

2. **Draft collaboration model?**
   - Current: DRAFT_*.md tracked, personal index gitignored
   - Alternative: Full drafts gitignored, explicit "share" command

3. **Promotion to existing feature (enhancement)?**
   - Current: Not explicitly supported
   - Could add: Update existing feature's TASKS.md with new phase

4. **Archive vs delete for promoted drafts?**
   - Current: Archive to `specs/drafts/archive/`
   - Alternative: Delete after promotion (git history preserves)

---

## Appendix: Command Summary

| Command | Purpose | Time |
|---------|---------|------|
| `/planning/idea` | Quick capture rough idea | < 5s |
| `/planning/draft` | Create/open exploration spec | < 30s |
| `/planning/drafts` | List all drafts with status | < 3s |
| `/planning/promote` | Convert draft → epic/feature | 1-2 min |
| `/planning/session-notes` | Manage session scratch | < 5s |

**Updated existing:**
| Command | Change |
|---------|--------|
| `/planning/resume` | Includes brainstorming context |
