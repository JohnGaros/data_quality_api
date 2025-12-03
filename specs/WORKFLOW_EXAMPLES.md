# Planning System Workflow Examples

This document provides concrete examples of using the hierarchical planning system for daily development tasks.

## Quick Start After `/clear`

**Scenario:** You've been working on a feature, ran `/clear`, and need to resume.

```bash
/planning/resume
```

**Output:**
```
## Resuming Work Context

Last session: 2025-11-27T14:30:00Z (30 minutes ago)
Feature: e2e_file_testing
Epic: E1_CORE_VALIDATION
Milestone: M1_MVP_FOUNDATION
Status: In Progress - 42% complete

### Where You Left Off

Phase 3: File Savers
Next Task: Implement save_profiling_snapshot()

### Phase 3 Checklist

- [x] Implement save_cleansed_dataset()
- [x] Implement save_rejected_rows()
- [ ] Implement save_profiling_snapshot()
- [ ] Implement save_validation_result()

### Quick Reference

Module: dq_cleansing, dq_profiling
Key Files:
- tests/fixtures/file_savers.py
- tests/integration/test_e2e_file_workflow.py

### Ready to Continue?

- Mark task complete: /planning/checkpoint --complete-task "description"
- View full context: Read specs/milestones/.../IMPLEMENTATION.md
- View progress: /planning/progress
```

**Time:** < 10 seconds
**Lines loaded:** ~100 (vs 15,000+ for full architecture reload)

---

## Example 1: Starting a New Feature

**Scenario:** You need to implement "API Upload Endpoints" as part of the Core Validation epic.

### Step 1: Create Feature Scaffold

```bash
/planning/new-feature
```

**Interactive prompts:**
```
Feature name: api_upload_endpoints
Epic: E1_CORE_VALIDATION
Milestone: M1_MVP_FOUNDATION
Description: FastAPI endpoints for file upload with contract resolution
Estimated time (hours): 16
Primary module: dq_api
```

**What happens:**
- Creates `specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/api_upload_endpoints/`
- Generates `IMPLEMENTATION.md` (templated with Quick Reference, Architecture Context, and 7 phases)
- Generates `TASKS.md` (7 phases scaffolded with placeholders)
- Initializes `.checkpoint` (status: not_started)
- Updates `specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/EPIC.md`
- Updates `specs/README.md`

### Step 2: Start Work

```bash
/planning/goto-feature api_upload_endpoints
```

**What happens:**
- Loads minimal context (Quick Reference + Phase 1 tasks)
- Updates `specs/.checkpoints/current.json` to point to this feature
- Sets checkpoint status to `in_progress`, current_phase to `1`

**Output:**
```
## Switched to Feature: api_upload_endpoints

Epic: E1_CORE_VALIDATION
Milestone: M1_MVP_FOUNDATION
Status: In Progress - 0% complete

### Phase 1: File Structure & Dependencies

Tasks:
- [ ] Create src/dq_api/routes/upload.py
- [ ] Add FastAPI dependencies to pyproject.toml
- [ ] Create tests/integration/test_api_upload.py
- [ ] Set up fixtures for multipart file upload

Next: Start implementing Phase 1 tasks
```

### Step 3: Complete Tasks

As you implement tasks:

```bash
# After creating upload.py
/planning/checkpoint --complete-task "Create src/dq_api/routes/upload.py"

# After adding dependencies
/planning/checkpoint --complete-task "Add FastAPI dependencies"
```

**What happens:**
- Updates `.checkpoint` YAML
- Increments `tasks_completed` for current phase
- Recalculates progress percentage
- Updates `last_updated` timestamp
- Calculates time spent since `session_started`

### Step 4: Move to Next Phase

```bash
# After completing all Phase 1 tasks
/planning/checkpoint --next-phase
```

**What happens:**
- Marks current phase as `completed`
- Sets `completed_at` timestamp
- Increments `current_phase` to `2`
- Sets Phase 2 status to `in_progress`
- Sets Phase 2 `started_at` timestamp
- Shows Phase 2 task checklist

### Step 5: Run `/clear` (Context Loss)

You've been working for a while and the conversation is long. You run `/clear` to reset.

```bash
/clear
```

**Context lost:**
- All conversation history gone
- Claude has no memory of the feature
- Manual navigation would require: open specs/, find feature, read docs (2-5 minutes)

### Step 6: Instant Resume

```bash
/planning/resume
```

**Time:** 5-10 seconds
**Result:** You're back in context with next task shown

### Step 7: Complete Feature

```bash
# After completing all 7 phases
/planning/checkpoint --complete-feature
```

**What happens:**
- Sets feature status to `completed`
- Sets all phases to `completed`
- Updates epic PROGRESS.md
- Updates milestone PROGRESS.md
- Shows next feature in epic (if any)

---

## Example 2: Handling Blockers

**Scenario:** You're working on Phase 4 and discover you need API contract approval before continuing.

```bash
/planning/checkpoint --add-blocker "Waiting for API contract approval from product team"
```

**What happens:**
- Adds blocker to `.checkpoint` YAML
- Sets feature status to `blocked`
- Keeps current_phase unchanged (you can resume when unblocked)

**Later, when unblocked:**

```bash
/planning/checkpoint --remove-blocker "Waiting for API contract approval from product team"
```

**What happens:**
- Removes blocker from list
- Sets status back to `in_progress` (if no other blockers remain)

---

## Example 3: Viewing Project-Wide Progress

**Scenario:** You want to see overall progress across all milestones and features.

```bash
/planning/progress
```

**Output:**
```
============================================================
Project Progress Dashboard
============================================================

Overall Progress: 18.5%

## Milestones

### M1: MVP Foundation (Target: 2025-12-30)
Status: In Progress - 27.8%

  Epic E1: Core Validation - 40.0%
    ✓ e2e_file_testing - Completed (100%)
    ⟳ api_upload_endpoints - In Progress (25%) [Phase 2/7]
    ○ core_rule_engine - Not Started (0%)

  Epic E2: Metadata & Lineage - 0%
    ○ metadata_registry - Not Started (0%)
    ○ audit_trail - Not Started (0%)

### M2: Security & Compliance (Target: 2026-01-31)
Status: Not Started - 0%

  Epic E3: RBAC & GDPR - 0%
    ○ azure_ad_integration - Not Started (0%)
    ○ gdpr_compliance - Not Started (0%)
    ○ storage_retention - Not Started (0%)

### M3: Scale & Operations (Target: 2026-02-28)
Status: Not Started - 0%

  Epic E4: Operations - 0%
    ○ tenant_management - Not Started (0%)
    ○ observability - Not Started (0%)
    ○ ci_cd_pipelines - Not Started (0%)
    ○ azure_blob_storage - Not Started (0%)

============================================================

Legend:
  ✓ Completed   ⟳ In Progress   ⊘ Blocked   ○ Not Started

Run '/planning/status' to see current feature details
Run '/planning/resume' to continue where you left off
```

---

## Example 4: Switching Between Features

**Scenario:** You're working on feature A but need to quickly check/update feature B.

### Current work on api_upload_endpoints

```bash
/planning/status
```

**Output:**
```
Current Feature: api_upload_endpoints
Epic: E1_CORE_VALIDATION
Milestone: M1_MVP_FOUNDATION
Status: In Progress - 25%
Phase: 2/7 (File Loaders)
```

### Switch to e2e_file_testing

```bash
/planning/goto-feature e2e_file_testing
```

**Output:**
```
## Switched to Feature: e2e_file_testing

Status: Completed - 100%
All 7 phases completed

Last updated: 2025-11-26T15:00:00Z
```

### Switch back to api_upload_endpoints

```bash
/planning/goto-feature api_upload_endpoints
```

**Output:**
```
## Switched to Feature: api_upload_endpoints

Status: In Progress - 25%
Phase: 2/7 (File Loaders)

Next Task: Implement load_multipart_file()
```

---

## Example 5: Time Tracking

**Scenario:** The planning system automatically tracks time spent per phase and feature.

### Start working (automatic)

When you run `/planning/goto-feature` or `/planning/checkpoint`:
- Sets `session_started` to current timestamp

### Update progress (automatic time tracking)

```bash
/planning/checkpoint --complete-task "Implement load_multipart_file()"
```

**What happens:**
- Calculates `session_duration = current_time - session_started`
- Adds `session_duration` to current phase's `time_spent_minutes`
- Adds `session_duration` to feature's total `time_spent_minutes`
- Resets `session_started = current_time` (start new session)

### View time report

```bash
/planning/status --verbose
```

**Output:**
```
Feature: api_upload_endpoints
Status: In Progress - 25%
Phase: 2/7 (File Loaders)

Time Tracking:
  Total time spent: 45 minutes
  Current phase: 15 minutes
  Phase 1: 30 minutes (completed)
  Phase 2: 15 minutes (in progress)

Estimated remaining: 11 hours 15 minutes (based on 16 hour estimate)
```

---

## Example 6: Creating an Epic

**Scenario:** You need to add a new epic "E5: Advanced Analytics" to M3.

```bash
/planning/new-epic
```

**Interactive prompts:**
```
Epic name: Advanced Analytics
Epic ID: E5_ADVANCED_ANALYTICS
Milestone: M3_SCALE_OPERATIONS
Description: Advanced profiling, anomaly detection, and trend analysis
Features (comma-separated): statistical_profiling,anomaly_detection,trend_analysis
```

**What happens:**
- Creates `specs/milestones/M3_SCALE_OPERATIONS/epics/E5_ADVANCED_ANALYTICS/`
- Generates `EPIC.md`
- Generates `PROGRESS.md`
- Creates `features/` subdirectory
- Scaffolds feature directories for each listed feature
- Updates milestone MILESTONE.md
- Updates specs/PROJECT_ROADMAP.md

---

## Example 7: Creating a Milestone

**Scenario:** Planning for M4 - Production Hardening.

```bash
/planning/new-milestone
```

**Interactive prompts:**
```
Milestone name: Production Hardening
Milestone ID: M4_PRODUCTION_HARDENING
Target date: 2026-04-30
Description: Performance optimization, load testing, DR planning
Epics (comma-separated): E6_PERFORMANCE,E7_RESILIENCE
```

**What happens:**
- Creates `specs/milestones/M4_PRODUCTION_HARDENING/`
- Generates `MILESTONE.md`
- Generates `PROGRESS.md`
- Creates epic directories
- Updates specs/PROJECT_ROADMAP.md

---

## Best Practices

### 1. Always Resume After `/clear`

```bash
# ❌ BAD: Manually re-reading docs
Read docs/ARCHITECTURE.md
Read specs/milestones/.../IMPLEMENTATION.md

# ✅ GOOD: Use resume command
/planning/resume
```

### 2. Update Checkpoints Frequently

```bash
# Update after completing each task
/planning/checkpoint --complete-task "description"

# Don't wait until end of phase to update
```

### 3. Use Status to Orient

```bash
# Quick orientation without full context load
/planning/status
```

### 4. Add Blockers Immediately

```bash
# As soon as you discover a blocker
/planning/checkpoint --add-blocker "Waiting for X"

# Don't work around blockers silently
```

### 5. Review Progress Regularly

```bash
# See project-wide progress
/planning/progress

# Weekly or before standup meetings
```

---

## Command Reference

### Core Commands

| Command | Purpose | Time |
|---------|---------|------|
| `/planning/resume` | Restore context after `/clear` | < 10s |
| `/planning/status` | Show current feature/phase/task | < 3s |
| `/planning/checkpoint` | Update progress | < 5s |
| `/planning/progress` | View project dashboard | < 10s |

### Scaffolding Commands

| Command | Purpose | Time |
|---------|---------|------|
| `/planning/new-feature` | Create feature scaffold | < 2min |
| `/planning/new-epic` | Create epic scaffold | < 2min |
| `/planning/new-milestone` | Create milestone scaffold | < 2min |

### Navigation Commands

| Command | Purpose | Time |
|---------|---------|------|
| `/planning/goto-feature` | Switch active feature | < 5s |

---

## Troubleshooting

### Problem: "No active feature" error

**Cause:** `specs/.checkpoints/current.json` is missing or invalid

**Solution:**
```bash
/planning/goto-feature <feature_name>
```

### Problem: Checkpoint validation fails

**Cause:** Manual edits to `.checkpoint` file broke schema

**Solution:**
```bash
# Run validation to see errors
python scripts/validate_checkpoints.py

# Fix errors or regenerate checkpoint
/planning/checkpoint --reset
```

### Problem: Progress percentage incorrect

**Cause:** Phase task counts don't match TASKS.md

**Solution:**
```bash
# Update phase task counts in .checkpoint
/planning/checkpoint --recalculate
```

### Problem: Time tracking seems wrong

**Cause:** Long idle periods between checkpoints

**Solution:**
```bash
# Reset session timer without updating tasks
/planning/checkpoint --reset-timer
```

---

## Integration with Git Workflow

### Recommended Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/api-upload-endpoints

# 2. Set up planning
/planning/goto-feature api_upload_endpoints

# 3. Work on tasks
# ... implement code ...

# 4. Update checkpoint
/planning/checkpoint --complete-task "Implement upload route"

# 5. Commit code (NOT checkpoint - it's gitignored)
git add src/dq_api/routes/upload.py
git commit -m "feat: add upload route for file ingestion"

# 6. Continue work
# ... implement more ...

# 7. After /clear, resume instantly
/clear
/planning/resume

# 8. Complete feature
/planning/checkpoint --complete-feature

# 9. Create PR
git push -u origin feature/api-upload-endpoints
gh pr create --title "API Upload Endpoints" --body "$(cat <<'EOF'
## Summary
- Add FastAPI upload endpoints
- Integrate with contract resolution
- Add multipart file handling

## Test plan
- [x] Unit tests for upload route
- [x] Integration tests for E2E flow
- [x] Manual testing with Postman

Generated with Claude Code
EOF
)"
```

### What Gets Committed

**Committed (version controlled):**
- `IMPLEMENTATION.md`
- `TASKS.md`
- Code changes (`src/`, `tests/`)
- Documentation (`docs/`)

**NOT committed (gitignored):**
- `.checkpoint` files (developer-local state)
- `specs/.checkpoints/current.json` (active feature pointer)

---

## Example 8: Dynamic Brainstorming Workflow

**Scenario:** You're implementing a feature when you realize a better architectural approach exists. Instead of continuing with a potentially suboptimal implementation, you use brainstorming commands to explore alternatives and adjust the plan.

### Step 1: Capture the Idea Mid-Implementation

You're working on `api_upload_endpoints` Phase 3 when you realize caching could significantly improve performance.

```bash
/planning/idea Add Redis caching layer for contract resolution - current approach makes DB call per upload
```

**What happens:**
- New idea appended to `specs/drafts/IDEAS.md` as IDEA-003
- Status set to `new`
- Timestamp recorded
- Your current feature work is uninterrupted

**Output:**
```
Captured: IDEA-003 - Add Redis caching layer for contract resolution

Location: specs/drafts/IDEAS.md

Next steps:
- Explore further: /planning/draft IDEA-003
- View all ideas: Read specs/drafts/IDEAS.md
- Promote directly: /planning/promote IDEA-003
```

### Step 2: Quick Exploration Without Leaving Current Work

You can continue working but want to note context for later:

```bash
/planning/session-notes --park "IDEA-003: Check if Azure Cache for Redis fits infra profile"
```

**What happens:**
- Item added to parking lot in session notes
- Persists across conversation turns
- Won't be forgotten during current work

### Step 3: Finish Current Phase, Then Explore

After completing the immediate task:

```bash
/planning/checkpoint --complete-task "Implement contract resolution endpoint"
/planning/draft IDEA-003
```

**What happens:**
- Creates `specs/drafts/explorations/DRAFT_redis_caching_layer.md`
- Opens draft in exploration mode
- Session timer starts

**Output:**
```
Draft created: Redis caching layer for contract resolution

Location: specs/drafts/explorations/DRAFT_redis_caching_layer.md
Source: IDEA-003
Status: exploring

Quick Reference:
# DRAFT: Redis caching layer for contract resolution

**Draft ID:** redis_caching_layer
**Status:** exploring
**Source Idea:** IDEA-003
**Created:** 2025-12-03T14:30:00Z

## Problem

Current approach makes DB call per upload for contract resolution...

Suggested Next Steps:
1. Fill in the "Hypothesis" section
2. List 2-3 approach options
3. Add questions to research
4. When ready: /planning/promote redis_caching_layer
```

### Step 4: Interactive Brainstorming Session

For deeper exploration:

```bash
/planning/brainstorm --feature api_upload_endpoints
```

**What happens:**
- Loads current feature context (IMPLEMENTATION.md, TASKS.md, checkpoint)
- Presents structured exploration options
- Captures insights to session notes automatically

**Output:**
```
================================================================================
BRAINSTORM SESSION: Feature api_upload_endpoints
================================================================================
Session ID: brainstorm-2025-12-03-1445

Brainstorming modifications to: api_upload_endpoints

Current state:
- Phase: 3 of 7
- Status: in_progress
- Progress: 35%

Related exploration:
- IDEA-003: Redis caching (exploring)
- Draft: redis_caching_layer

What would you like to explore?

A) Add new tasks to current phase
B) Add new phase for caching integration
C) Modify approach for existing task
D) Discuss blockers or alternatives
E) Re-scope feature requirements

Or just start talking and I'll follow your lead.
================================================================================
```

### Step 5: Dynamically Add Phase to Feature

During the brainstorm, you decide caching should be part of this feature. You can modify the plan in real-time:

```
User: Let's add a new phase for caching integration

Claude: Adding Phase 8 to api_upload_endpoints:

## Phase 8: Redis Caching Integration

- [ ] Add Azure Cache for Redis connection config
- [ ] Implement cache-aside pattern for contract lookups
- [ ] Add cache invalidation on contract updates
- [ ] Add cache hit/miss metrics

Shall I update TASKS.md with this new phase?

User: Yes, do it
```

**What happens:**
- Claude updates `TASKS.md` with new Phase 8
- Updates `IMPLEMENTATION.md` approach section
- `.checkpoint` total phases count updated
- Brainstorm session notes capture the decision

### Step 6: Save Brainstorm Insights

```bash
/planning/brainstorm --save
```

**What happens:**
- Session insights summarized
- Appended to draft's Research Notes section
- Parking lot items preserved

**Output:**
```
Session Summary
═══════════════════════════════════════════════════════════════════════════════

Key Insights:
1. Caching should be integrated into current feature, not separate epic
2. Azure Cache for Redis fits infra profile
3. Cache-aside pattern preferred over write-through

Action Items:
- [ ] Update infra_libraries/ with Redis profile
- [ ] Add AZURE_REDIS_CONNECTION_STRING to Key Vault config

Files Explored:
- src/dq_api/routes/validation.py
- src/dq_contracts/registry.py
- infra_libraries/compute_profiles.yaml

Saved to: specs/drafts/explorations/DRAFT_redis_caching_layer.md

Draft status remains 'exploring' until promoted or archived.
```

---

## Example 9: Epic-Level Brainstorming

**Scenario:** You need to add multiple related features to an existing epic.

### Step 1: Start Epic Brainstorm

```bash
/planning/brainstorm --epic E2_METADATA_LINEAGE
```

**Output:**
```
================================================================================
BRAINSTORM SESSION: Epic E2_METADATA_LINEAGE
================================================================================
Session ID: brainstorm-2025-12-03-1530

Brainstorming for epic: E2_METADATA_LINEAGE

Current Status: In Progress - 15%

Existing features:
- metadata_registry (in_progress) - Core metadata storage
- audit_trail (not_started) - Audit event tracking

What would you like to explore?

A) Propose new feature for this epic
B) Re-prioritize existing features
C) Discuss cross-feature dependencies
D) Scope adjustment (add/remove features)

Or describe what you're thinking about.
================================================================================
```

### Step 2: Propose New Features

```
User: I want to add a feature for data lineage visualization

Claude: Great idea! Let me capture this:

Data lineage visualization would:
- Show upstream/downstream dependencies
- Visualize job execution flow
- Support interactive exploration

Questions to consider:
1. Should this be real-time or batch-generated?
2. What visualization library? (D3.js, Mermaid, etc.)
3. Integration with existing dq_docs module?

Shall I:
A) Create a quick idea (IDEA-NNN)
B) Create a full draft exploration
C) Create feature directly (if scope is clear)
D) Continue discussing
```

### Step 3: Create Feature from Brainstorm

If the scope is clear:

```bash
User: C - scope is clear enough

Claude: Creating feature in E2_METADATA_LINEAGE...

Created: lineage_visualization
Location: specs/milestones/M1_MVP_FOUNDATION/epics/E2_METADATA_LINEAGE/features/lineage_visualization/

Files created:
- IMPLEMENTATION.md (overview, approach from our discussion)
- TASKS.md (7 phases scaffolded)
- .checkpoint (initialized)

Epic E2_METADATA_LINEAGE updated:
- metadata_registry (in_progress)
- audit_trail (not_started)
- lineage_visualization (not_started) ← NEW

Next steps:
1. Review: Read specs/.../lineage_visualization/IMPLEMENTATION.md
2. Customize tasks as needed
3. Start when ready: /planning/goto-feature lineage_visualization
```

---

## Example 10: Idea to Feature Pipeline

**Scenario:** A quick idea evolves through exploration to become a planned feature.

### Day 1: Capture Raw Idea

```bash
/planning/idea WebSocket support for real-time validation progress updates
```

### Day 2: Start Exploration

```bash
/planning/draft IDEA-004
```

Fill in the draft template with research:

- **Option A:** WebSocket with Socket.IO
- **Option B:** Server-Sent Events (SSE)
- **Option C:** Azure SignalR Service

### Day 3: Complete Research

```bash
/planning/draft --log "Benchmarked SSE vs WebSocket - SSE simpler for one-way"
/planning/draft --log "Azure SignalR would add $50/mo cost - may be worth it for scale"
```

### Day 4: Promote to Feature

```bash
/planning/promote realtime_validation_progress
```

**Decision framework guides through:**

1. **Scope assessment:** Medium (1-2 weeks)
2. **Deliverables:** One (single cohesive implementation)
3. **Existing epic:** E1_CORE_VALIDATION fits

**Result:**
```
Promoted: Real-time validation progress

**Created:** Feature in E1_CORE_VALIDATION
**Location:** specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/realtime_validation_progress/

**Files created:**
- IMPLEMENTATION.md (populated from draft research)
- TASKS.md (7 phases generated)
- .checkpoint (initialized, time_spent: 45m carried from draft)

**Source updated:**
- Draft realtime_validation_progress → promoted
- IDEA-004 → promoted

**Next steps:**
1. Review generated IMPLEMENTATION.md
2. Customize TASKS.md phases
3. Start work: /planning/goto-feature realtime_validation_progress
```

---

## Example 11: Managing Multiple Drafts

**Scenario:** You have several ideas in exploration and need to track them.

### View All Drafts

```bash
/planning/drafts
```

**Output:**
```
================================================================================
DRAFTS DASHBOARD
================================================================================

Active Draft: redis_caching_layer
Time this session: 12m

## Drafts (3)

| Status     | ID                        | Summary                      | Time  |
|------------|---------------------------|------------------------------|-------|
| exploring  | redis_caching_layer       | Contract resolution caching  | 45m   |
| ready      | batch_validation_api      | Bulk upload endpoint         | 120m  |
| exploring  | graphql_endpoint          | Alternative API surface      | 15m   |

## Ideas Not Yet Drafted (2)

| ID       | Title                          | Created    | Tags           |
|----------|--------------------------------|------------|----------------|
| IDEA-005 | Webhook retry with backoff     | 2025-12-02 | api, resilience|
| IDEA-006 | Contract diff visualization    | 2025-12-03 | docs, ui       |

================================================================================

Commands:
- Open draft: /planning/draft {id}
- Promote ready draft: /planning/promote batch_validation_api
- Create from idea: /planning/draft IDEA-005
- New idea: /planning/idea <description>
```

### Promote Ready Draft

The `batch_validation_api` draft shows `ready` status (all decision criteria met):

```bash
/planning/promote batch_validation_api
```

Since criteria are complete, promotion proceeds directly to placement questions.

---

## Brainstorming Command Reference

### Quick Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/planning/idea <desc>` | Capture rough idea | Tangential thought during work |
| `/planning/session-notes --park "item"` | Save reminder | Don't forget this later |
| `/planning/draft --log "note"` | Add exploration log | Capture research finding |

### Exploration Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/planning/draft IDEA-NNN` | Start exploring idea | Ready to research further |
| `/planning/draft {name}` | Open existing draft | Continue exploration |
| `/planning/drafts` | View all drafts/ideas | Need overview of pipeline |
| `/planning/brainstorm <topic>` | Interactive exploration | Open-ended exploration |
| `/planning/brainstorm --feature X` | Feature brainstorm | Modify existing feature |
| `/planning/brainstorm --epic X` | Epic brainstorm | Add features to epic |

### Promotion Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/planning/promote {draft}` | Draft → feature/epic | Exploration complete |
| `/planning/promote IDEA-NNN` | Idea → feature directly | Scope is clear |

### State Flow

```
Idea (new)
    ↓ /planning/draft IDEA-NNN
Draft (exploring)
    ↓ research, session-notes
Draft (ready)
    ↓ /planning/promote
Feature (not_started)
    ↓ /planning/goto-feature
Feature (in_progress)
```

### Integration with Implementation Workflow

The brainstorming system integrates seamlessly with implementation tracking:

```bash
# During implementation work
/planning/checkpoint --complete-task "Add endpoint"

# Quick idea without losing context
/planning/idea Batch processing could be 10x faster with async

# Back to implementation
/planning/checkpoint --next-phase

# Later - explore the idea
/planning/draft IDEA-007
```

---

## Summary

The planning system enables:

1. **Fast context restoration** after `/clear` (< 10 seconds)
2. **Clear progress visibility** across project/milestone/epic/feature levels
3. **Automatic time tracking** for better estimation
4. **Blocker management** to surface impediments
5. **Minimal overhead** through slash commands
6. **Dynamic plan adjustment** via brainstorming commands
7. **Idea-to-feature pipeline** for capturing and evolving rough ideas

**Key insight:** The system loads < 500 lines for resume (vs 15,000+ full architecture reload), making it practical for daily use.

**Brainstorming insight:** Ideas captured mid-implementation don't interrupt flow, and the `idea → draft → feature` pipeline ensures nothing gets lost while maintaining structured progression from rough concept to planned work.
