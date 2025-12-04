Restore context after /clear by loading minimal checkpoint information AND brainstorming state.

**Your task:**

## Part A: Implementation Context

1. Read `specs/.checkpoints/current.json` to find the active feature path
   - If file doesn't exist or is empty, check for any in_progress features by finding all .checkpoint files
   - Note: It's OK if no active feature exists - continue to Part B

2. If active feature found, read the feature's `.checkpoint` file to get current state:
   - feature_name, status, current_phase
   - Phase status (which phase is in_progress)
   - tasks_completed / tasks_total for current phase
   - time_spent_minutes
   - blockers
   - notes

3. Read the **first 50 lines only** of the feature's `IMPLEMENTATION.md` (Quick Reference section)

4. Read the feature's `TASKS.md` and extract **only the current phase section** (based on current_phase from checkpoint)

## Part B: Brainstorming Context

5. Read `specs/drafts/.drafts_index.json` to find the active draft (if any)
   - If active_draft exists, note: draft_id, status, time_spent_minutes, potential_home

6. Read `specs/drafts/.session_notes` for session scratch (if exists)
   - Extract: active_context (first 3 lines), parking_lot count, scratch count

7. Quickly scan `specs/drafts/IDEAS.md` to count ideas by status:
   - Count ideas with status=new (capture in summary)

## Part C: Display Combined Resume

Display a concise resume summary in this format:

```
## Resuming Work Context

### Implementation

{If active feature exists:}
Last updated: [timestamp from checkpoint] ([relative time] ago)
Feature: [feature_name]
Status: [status] - [progress_percentage]% complete
Location: [feature_path]

**Where You Left Off:**
Phase [N]: [phase_name]
Progress: [tasks_completed]/[tasks_total] tasks

**Current Phase Checklist:**
[Show task list from TASKS.md for current phase only - preserve checkbox format]

**Blockers:** [List blockers if any, otherwise "None"]

{If no active feature:}
No active feature.
Use /planning-goto-feature to start one, or /planning-status to see all features.

---

### Brainstorming

{If active draft exists:}
**Active Draft:** [draft_id] ([status])
Time spent: [time_spent_minutes]m
Potential: [type] in [epic or "Unknown"]

{If session notes have content:}
**Session Context:**
[First 3 lines of active_context]

**Parking Lot:** [count] items
[List first 2 items if any]

{If new ideas exist:}
**New Ideas:** [count] captured (use /planning-drafts to review)

{If no brainstorming context:}
No active drafts or session notes.
Use /planning-idea to capture ideas or /planning-draft to start exploring.

---

### Quick Commands

**Implementation:**
- Mark task complete: /planning-checkpoint --complete-task "description"
- Move to next phase: /planning-checkpoint --next-phase
- Full context: Read [path to IMPLEMENTATION.md]

**Brainstorming:**
- View draft: /planning-draft [active_draft]
- Session notes: /planning-session-notes
- Capture idea: /planning-idea
- All drafts: /planning-drafts

**Overview:**
- Project progress: /planning-progress
- Current status: /planning-status
```

**CRITICAL REQUIREMENTS:**
- Load LESS than 500 total lines of content
- Complete context restoration in under 10 seconds
- DO NOT read full architecture docs (ARCHITECTURE.md, etc.)
- DO NOT read other features' files
- DO NOT read full draft files - only index metadata
- Focus on actionable "what's next" rather than history
- Gracefully handle missing files (brainstorming files may not exist yet)

**If checkpoint shows status = completed:**
Suggest next feature in the epic or congratulate and show /planning-progress

**If checkpoint shows status = blocked:**
Highlight blockers prominently and suggest addressing them first

**If only brainstorming context exists (no implementation):**
Focus the output on the active draft and session notes, suggest promoting when ready

**Empty state (no implementation or brainstorming):**
```
## Resuming Work Context

No active work context found.

Get started:
- View features: /planning-status
- Start feature: /planning-goto-feature {name}
- Capture idea: /planning-idea
- Create draft: /planning-draft

Use /planning-progress for project-wide dashboard.
```
