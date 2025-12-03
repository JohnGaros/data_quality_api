# Planning System Test Plan

This document outlines test cases for the hierarchical planning system, to be executed once slash commands are implemented in Phase 2 and Phase 3.

## Test Prerequisites

Before running these tests, ensure:
1. Phase 1 (Foundation) is complete: ✅
   - Directory structure exists
   - Templates created
   - `parse_checkpoints.py` working
   - `validate_checkpoints.py` working

2. Phase 2 (Core Commands) is complete:
   - [ ] `/planning/resume` implemented
   - [ ] `/planning/status` implemented
   - [ ] `/planning/checkpoint` implemented
   - [ ] `/planning/progress` implemented

3. Phase 3 (Scaffolding Commands) is complete:
   - [ ] `/planning/new-feature` implemented
   - [ ] `/planning/new-epic` implemented
   - [ ] `/planning/new-milestone` implemented
   - [ ] `/planning/goto-feature` implemented

---

## Test Suite 1: Context Restoration After `/clear`

**Objective:** Verify that `/planning/resume` restores context in < 10 seconds with < 500 lines loaded.

### Test Case 1.1: Resume with Active Feature

**Setup:**
1. Use `/planning/goto-feature e2e_file_testing`
2. Verify checkpoint status is `in_progress`
3. Run `/clear`

**Test Steps:**
1. Run `/planning/resume`
2. Measure time to completion
3. Count lines loaded (estimate from output size)

**Expected Results:**
- Time: < 10 seconds
- Lines loaded: < 500
- Output shows:
  - Feature name: e2e_file_testing
  - Current phase number and name
  - Next task to complete
  - Quick Reference section (< 50 lines)
  - Current phase tasks only (not all phases)

**Success Criteria:**
- ✅ Resume completes in < 10 seconds
- ✅ Output contains exactly the information needed to continue
- ✅ No unnecessary architecture context loaded
- ✅ User knows exactly what to do next

### Test Case 1.2: Resume with No Active Feature

**Setup:**
1. Delete `specs/.checkpoints/current.json` if it exists
2. Run `/clear`

**Test Steps:**
1. Run `/planning/resume`

**Expected Results:**
- Output shows: "No active feature. Use /planning/status or /planning/goto-feature <name>"
- Suggests running `/planning/progress` to see all features

**Success Criteria:**
- ✅ Graceful handling of missing active feature
- ✅ Clear guidance on next steps

### Test Case 1.3: Resume with Completed Feature

**Setup:**
1. Create a completed feature checkpoint (status: completed)
2. Set as active feature
3. Run `/clear`

**Test Steps:**
1. Run `/planning/resume`

**Expected Results:**
- Shows feature is completed
- Shows next feature in epic (if any)
- Suggests using `/planning/goto-feature` to switch

**Success Criteria:**
- ✅ Detects completed status
- ✅ Suggests next feature to work on

---

## Test Suite 2: Checkpoint Updates

**Objective:** Verify that checkpoint commands correctly update state, timestamps, and progress.

### Test Case 2.1: Complete Task

**Setup:**
1. Use `/planning/goto-feature e2e_file_testing`
2. Ensure current_phase = 3, tasks_completed = 2, tasks_total = 4

**Test Steps:**
1. Run `/planning/checkpoint --complete-task "Implement save_profiling_snapshot()"`
2. Read `.checkpoint` file
3. Verify updates

**Expected Results:**
- `tasks_completed` incremented to 3
- `last_updated` timestamp updated
- `time_spent_minutes` increased (based on session duration)
- Current phase `time_spent_minutes` increased

**Success Criteria:**
- ✅ Task count updated correctly
- ✅ Timestamps updated
- ✅ Time tracking accurate
- ✅ Progress percentage recalculated

### Test Case 2.2: Move to Next Phase

**Setup:**
1. Complete all tasks in Phase 3 (tasks_completed = 4, tasks_total = 4)

**Test Steps:**
1. Run `/planning/checkpoint --next-phase`
2. Read `.checkpoint` file
3. Verify phase transition

**Expected Results:**
- Phase 3 status = `completed`
- Phase 3 `completed_at` timestamp set
- `current_phase` = 4
- Phase 4 status = `in_progress`
- Phase 4 `started_at` timestamp set
- `session_started` reset for new phase

**Success Criteria:**
- ✅ Previous phase marked completed
- ✅ Next phase marked in_progress
- ✅ current_phase incremented
- ✅ Timestamps correctly set
- ✅ Session timer reset

### Test Case 2.3: Add Blocker

**Setup:**
1. Use `/planning/goto-feature e2e_file_testing`

**Test Steps:**
1. Run `/planning/checkpoint --add-blocker "Waiting for API contract approval"`
2. Read `.checkpoint` file
3. Verify blocker added

**Expected Results:**
- Feature status = `blocked`
- Blocker appears in `blockers` list
- `current_phase` unchanged
- `last_updated` timestamp updated

**Success Criteria:**
- ✅ Status changed to blocked
- ✅ Blocker added to list
- ✅ Current work state preserved

### Test Case 2.4: Remove Blocker

**Setup:**
1. Feature has status `blocked` with one blocker

**Test Steps:**
1. Run `/planning/checkpoint --remove-blocker "Waiting for API contract approval"`
2. Read `.checkpoint` file

**Expected Results:**
- Blocker removed from list
- If no blockers remain: status = `in_progress`
- If blockers remain: status = `blocked`

**Success Criteria:**
- ✅ Blocker removed
- ✅ Status updated correctly based on remaining blockers

### Test Case 2.5: Complete Feature

**Setup:**
1. Complete all phases (Phase 7 completed)

**Test Steps:**
1. Run `/planning/checkpoint --complete-feature`
2. Read `.checkpoint` file
3. Check epic PROGRESS.md
4. Check milestone PROGRESS.md

**Expected Results:**
- Feature status = `completed`
- All phases status = `completed`
- Epic PROGRESS.md updated with 100% for this feature
- Milestone PROGRESS.md recalculated
- Output shows next feature in epic

**Success Criteria:**
- ✅ Feature marked completed
- ✅ Parent epic/milestone progress updated
- ✅ Next feature suggested

---

## Test Suite 3: Progress Dashboard

**Objective:** Verify that `/planning/progress` shows accurate project-wide progress.

### Test Case 3.1: Project Progress Display

**Setup:**
1. Ensure multiple features exist with varying statuses:
   - e2e_file_testing: completed (100%)
   - api_upload_endpoints: in_progress (25%)
   - core_rule_engine: not_started (0%)

**Test Steps:**
1. Run `/planning/progress`
2. Verify output format and accuracy

**Expected Results:**
- Overall project percentage calculated correctly
- Each milestone shows:
  - Milestone name and target date
  - Overall milestone percentage
  - Status (Not Started / In Progress / Completed)
- Each epic shows:
  - Epic name
  - Overall epic percentage
  - Feature count
- Each feature shows:
  - Feature name
  - Status symbol (✓ ⟳ ⊘ ○)
  - Percentage
  - Current phase (if in_progress)

**Success Criteria:**
- ✅ All features displayed
- ✅ Percentages accurate (verified against manual calculation)
- ✅ Status symbols correct
- ✅ Hierarchical structure clear

### Test Case 3.2: Performance (Large Project)

**Setup:**
1. Create 3 milestones × 3 epics × 5 features = 45 features
2. Set varying progress states

**Test Steps:**
1. Run `/planning/progress`
2. Measure time to completion

**Expected Results:**
- Time: < 10 seconds
- All 45 features displayed
- Accurate aggregation at all levels

**Success Criteria:**
- ✅ Completes in < 10 seconds
- ✅ No performance degradation with many features

---

## Test Suite 4: Feature Creation and Scaffolding

**Objective:** Verify scaffolding commands create correct structure and update parent files.

### Test Case 4.1: Create New Feature

**Setup:**
1. Epic E1_CORE_VALIDATION exists

**Test Steps:**
1. Run `/planning/new-feature`
2. Provide inputs:
   - Name: test_feature
   - Epic: E1_CORE_VALIDATION
   - Milestone: M1_MVP_FOUNDATION
   - Description: Test feature for validation
   - Estimated hours: 8
   - Primary module: dq_core

**Expected Results:**
- Directory created: `specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/test_feature/`
- Files created:
  - `IMPLEMENTATION.md` (with Quick Reference, Architecture Context, 7 phases)
  - `TASKS.md` (7 phases scaffolded)
  - `.checkpoint` (status: not_started)
- Parent epic EPIC.md updated with new feature
- specs/README.md updated

**Success Criteria:**
- ✅ All files created
- ✅ Templates populated correctly
- ✅ Parent files updated
- ✅ Checkpoint valid (passes validation script)

### Test Case 4.2: Create New Epic

**Setup:**
1. Milestone M1_MVP_FOUNDATION exists

**Test Steps:**
1. Run `/planning/new-epic`
2. Provide inputs:
   - Name: Test Epic
   - Epic ID: E99_TEST_EPIC
   - Milestone: M1_MVP_FOUNDATION
   - Description: Test epic
   - Features: feature_a,feature_b

**Expected Results:**
- Directory created: `specs/milestones/M1_MVP_FOUNDATION/epics/E99_TEST_EPIC/`
- Files created:
  - `EPIC.md`
  - `PROGRESS.md`
  - `features/` directory
  - `features/feature_a/` and `features/feature_b/` scaffolded
- Parent milestone MILESTONE.md updated
- PROJECT_ROADMAP.md updated

**Success Criteria:**
- ✅ Epic directory and files created
- ✅ Feature scaffolds created
- ✅ Parent files updated

### Test Case 4.3: Create New Milestone

**Test Steps:**
1. Run `/planning/new-milestone`
2. Provide inputs:
   - Name: Test Milestone
   - Milestone ID: M99_TEST
   - Target date: 2026-12-31
   - Description: Test milestone
   - Epics: E1_TEST,E2_TEST

**Expected Results:**
- Directory created: `specs/milestones/M99_TEST/`
- Files created:
  - `MILESTONE.md`
  - `PROGRESS.md`
  - `epics/` directory
  - Epic scaffolds
- PROJECT_ROADMAP.md updated

**Success Criteria:**
- ✅ Milestone created correctly
- ✅ Epic scaffolds created
- ✅ PROJECT_ROADMAP.md updated

---

## Test Suite 5: Feature Navigation

**Objective:** Verify that `/planning/goto-feature` switches context correctly.

### Test Case 5.1: Switch to Existing Feature

**Setup:**
1. Currently on feature_a (in_progress)

**Test Steps:**
1. Run `/planning/goto-feature feature_b`
2. Check `specs/.checkpoints/current.json`
3. Read output

**Expected Results:**
- `current.json` updated to point to feature_b
- Output shows feature_b context:
  - Feature name, epic, milestone
  - Current phase and progress
  - Next task
- feature_a checkpoint unchanged (still in_progress)

**Success Criteria:**
- ✅ Active feature switched
- ✅ Context loaded for new feature
- ✅ Previous feature state preserved

### Test Case 5.2: Switch to Non-Existent Feature

**Test Steps:**
1. Run `/planning/goto-feature nonexistent_feature`

**Expected Results:**
- Error message: "Feature not found: nonexistent_feature"
- Suggests running `/planning/progress` to see all features
- Active feature unchanged

**Success Criteria:**
- ✅ Graceful error handling
- ✅ Helpful error message

---

## Test Suite 6: Time Tracking

**Objective:** Verify automatic time tracking accuracy.

### Test Case 6.1: Session Time Calculation

**Setup:**
1. Use `/planning/goto-feature test_feature`
2. Note `session_started` timestamp

**Test Steps:**
1. Wait 5 minutes (or mock timestamp)
2. Run `/planning/checkpoint --complete-task "Test task"`
3. Read `.checkpoint` file

**Expected Results:**
- Phase `time_spent_minutes` increased by ~5
- Feature `time_spent_minutes` increased by ~5
- `session_started` reset to current time

**Success Criteria:**
- ✅ Time calculated accurately
- ✅ Session timer reset
- ✅ Time accumulated in both phase and feature

### Test Case 6.2: Time Tracking Across Phases

**Setup:**
1. Complete Phase 1 after 30 minutes
2. Move to Phase 2
3. Work for 15 minutes

**Test Steps:**
1. Run `/planning/status --verbose` (if implemented)
2. Verify time breakdown

**Expected Results:**
- Phase 1: 30 minutes (completed)
- Phase 2: 15 minutes (in progress)
- Feature total: 45 minutes

**Success Criteria:**
- ✅ Time tracked separately per phase
- ✅ Feature total = sum of all phases

---

## Test Suite 7: Validation and Error Handling

**Objective:** Verify checkpoint validation detects schema violations.

### Test Case 7.1: Valid Checkpoint

**Test Steps:**
1. Run `python scripts/validate_checkpoints.py`

**Expected Results:**
- Exit code: 0
- Output: "✅ All checkpoint files are valid!"

**Success Criteria:**
- ✅ Validation passes for valid checkpoints

### Test Case 7.2: Missing Required Field

**Setup:**
1. Manually edit `.checkpoint` to remove `feature_id`

**Test Steps:**
1. Run `python scripts/validate_checkpoints.py`

**Expected Results:**
- Exit code: 1
- Error: "Missing required field 'feature_id'"

**Success Criteria:**
- ✅ Detects missing required field
- ✅ Non-zero exit code

### Test Case 7.3: Invalid Status

**Setup:**
1. Set status to `invalid_status`

**Test Steps:**
1. Run validation

**Expected Results:**
- Error: "Invalid status 'invalid_status' (must be one of ...)"

**Success Criteria:**
- ✅ Validates enum values

### Test Case 7.4: Multiple In-Progress Phases

**Setup:**
1. Set Phase 2 and Phase 3 both to `in_progress`

**Test Steps:**
1. Run validation

**Expected Results:**
- Error: "Multiple phases (2) are in_progress (should be at most 1)"

**Success Criteria:**
- ✅ Detects multiple in-progress phases

### Test Case 7.5: Tasks Completed > Tasks Total

**Setup:**
1. Set phase `tasks_completed: 5, tasks_total: 3`

**Test Steps:**
1. Run validation

**Expected Results:**
- Error: "Phase X has tasks_completed (5) > tasks_total (3)"

**Success Criteria:**
- ✅ Validates task counts

---

## Test Suite 8: Integration with Development Workflow

**Objective:** Verify planning system integrates smoothly with typical development workflow.

### Test Case 8.1: Full Feature Lifecycle

**Scenario:** Implement a complete feature from creation to completion.

**Test Steps:**
1. Create feature: `/planning/new-feature`
2. Start work: `/planning/goto-feature <name>`
3. Complete tasks in Phase 1
4. Update checkpoint after each task
5. Move to Phase 2: `/planning/checkpoint --next-phase`
6. Run `/clear`
7. Resume: `/planning/resume`
8. Continue through all 7 phases
9. Complete feature: `/planning/checkpoint --complete-feature`
10. Verify epic/milestone progress updated

**Expected Results:**
- Smooth workflow with no errors
- Context never lost (even after `/clear`)
- Progress accurately tracked
- Parent files updated correctly

**Success Criteria:**
- ✅ Complete lifecycle works end-to-end
- ✅ No manual file edits needed
- ✅ Context restoration after `/clear` is instant

### Test Case 8.2: Parallel Feature Development

**Scenario:** Work on two features simultaneously (switching between them).

**Test Steps:**
1. Start feature_a: `/planning/goto-feature feature_a`
2. Complete some tasks
3. Switch to feature_b: `/planning/goto-feature feature_b`
4. Complete some tasks
5. Run `/clear`
6. Resume: `/planning/resume`
7. Verify correct feature restored (last active)
8. Switch back to feature_a
9. Verify feature_a state preserved

**Expected Results:**
- Both features maintain independent state
- Switching is instant
- Resume restores last active feature
- No interference between features

**Success Criteria:**
- ✅ Independent feature state
- ✅ Clean context switching
- ✅ Correct resume behavior

---

## Test Suite 9: Edge Cases

**Objective:** Handle unusual scenarios gracefully.

### Test Case 9.1: Empty Specs Directory

**Setup:**
1. Create empty `specs/` directory

**Test Steps:**
1. Run `/planning/progress`

**Expected Results:**
- Message: "No milestones found. Run /planning/new-milestone to create one."

**Success Criteria:**
- ✅ Handles empty state gracefully

### Test Case 9.2: Corrupted Checkpoint File

**Setup:**
1. Write invalid YAML to `.checkpoint`

**Test Steps:**
1. Run `/planning/resume`

**Expected Results:**
- Error: "Checkpoint file is corrupted. Run /planning/checkpoint --reset to regenerate."

**Success Criteria:**
- ✅ Detects corruption
- ✅ Suggests recovery action

### Test Case 9.3: Checkpoint Schema Migration

**Scenario:** Checkpoint schema changes (e.g., new field added)

**Test Steps:**
1. Add new optional field to schema
2. Load old checkpoint file
3. Verify backward compatibility

**Expected Results:**
- Old checkpoint loads successfully
- Missing optional fields use defaults
- Update adds new fields

**Success Criteria:**
- ✅ Backward compatible
- ✅ Graceful migration

---

## Performance Benchmarks

### Benchmark 1: Resume Speed

**Target:** < 10 seconds

**Measurement:**
- Time from command invocation to output completion
- Across various checkpoint sizes

**Expected:**
- Small feature (3 phases): < 5s
- Medium feature (7 phases): < 8s
- Large feature (10 phases): < 10s

### Benchmark 2: Progress Dashboard

**Target:** < 10 seconds

**Measurement:**
- Time to aggregate and display all features
- Test with 10, 25, 50, 100 features

**Expected:**
- 10 features: < 3s
- 25 features: < 5s
- 50 features: < 8s
- 100 features: < 10s

### Benchmark 3: Context Size

**Target:** < 500 lines loaded for resume

**Measurement:**
- Total lines of text loaded during `/planning/resume`

**Expected:**
- Quick Reference: ~50 lines
- Current phase tasks: ~20 lines
- Checkpoint summary: ~30 lines
- Total: ~100 lines

---

## Acceptance Criteria Summary

For Phase 4 (Integration & Polish) to be considered complete:

- ✅ All Phase 2 commands implemented and tested
- ✅ All Phase 3 commands implemented and tested
- ✅ Test Suite 1-9 all pass
- ✅ Performance benchmarks met
- ✅ Validation script detects all schema violations
- ✅ Full feature lifecycle works end-to-end
- ✅ `/clear` → `/resume` workflow validated (< 10s)
- ✅ Documentation complete (WORKFLOW_EXAMPLES.md)
- ✅ Integration with CLAUDE.md verified
- ✅ Architecture docs updated

---

## Test Execution Log

**To be filled in during testing:**

| Test ID | Status | Date | Notes |
|---------|--------|------|-------|
| 1.1 | ⏳ Pending | - | Awaiting Phase 2 completion |
| 1.2 | ⏳ Pending | - | Awaiting Phase 2 completion |
| 1.3 | ⏳ Pending | - | Awaiting Phase 2 completion |
| ... | ... | ... | ... |

**Legend:** ⏳ Pending | ✅ Pass | ❌ Fail | 🔄 In Progress
