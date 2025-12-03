# Go to Feature - Switch Context

You are helping the user switch to a different feature and load its context.

## Your Task

1. Find the feature by name (search across all milestones/epics)
2. Update `specs/.checkpoints/current.json` to point to this feature
3. Load minimal context (similar to /planning/resume but for a different feature)
4. Display orientation summary

## Implementation Steps

### Step 1: Parse Feature Name from Command

The user will invoke this as: `/planning/goto-feature {feature_name}`

Extract the feature name from the command arguments.

### Step 2: Find Feature Directory

Search for the feature across all milestones and epics:

```bash
find specs/milestones -type d -name "{feature_name}"
```

If multiple matches found, ask user to clarify which one.

If no matches found, display error:
```
❌ Feature '{feature_name}' not found

Available features:
- e2e_file_testing
- core_rule_engine
- api_upload_endpoints
[...list all features from checkpoint files...]

Use: /planning/goto-feature <feature_name>
```

### Step 3: Read Feature Checkpoint

Read the `.checkpoint` file for the feature:

```bash
cat specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}/.checkpoint
```

Parse YAML to get:
- feature_name
- status
- current_phase
- phases (for progress calculation)
- blockers
- notes

### Step 4: Update Current Context Pointer

Create or update `specs/.checkpoints/current.json`:

```json
{
  "feature_path": "specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}",
  "feature_id": "{FEATURE_NAME}",
  "feature_name": "{FEATURE_DISPLAY_NAME}",
  "milestone": "{MILESTONE}",
  "epic": "{EPIC}",
  "last_updated": "{ISO_TIMESTAMP}",
  "updated_by": "claude"
}
```

### Step 5: Load Minimal Context

Read only these files:

1. **Quick Reference** (first 50 lines of IMPLEMENTATION.md):
   ```bash
   head -n 50 specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}/IMPLEMENTATION.md
   ```

2. **Current Phase Tasks** (if status is in_progress):
   - Parse TASKS.md for current phase section only
   - Extract checklist items

3. **Checkpoint Status**:
   - Already loaded from step 3

### Step 6: Display Orientation Summary

Show a concise summary:

```
🎯 Switched to: {FEATURE_DISPLAY_NAME}

**Location:** specs/milestones/{MILESTONE}/epics/{EPIC}/features/{FEATURE_NAME}/
**Epic:** {EPIC_DISPLAY_NAME}
**Milestone:** {MILESTONE_DISPLAY_NAME}
**Status:** {STATUS}
**Progress:** {PROGRESS_PCT}%

---

## Current State

{STATUS_MESSAGE based on status:
  - not_started: "Feature not started yet. Ready to begin Phase 1."
  - in_progress: "Currently working on Phase {N}: {PHASE_NAME}"
  - completed: "Feature completed!"
  - blocked: "Feature blocked. See blockers below."
}

{If in_progress, show current phase checklist}

## Phase {N}: {PHASE_NAME}

- [x] Completed task 1
- [x] Completed task 2
- [ ] Next task 3  ← You are here
- [ ] Pending task 4

---

## Quick Reference

{First 50 lines of IMPLEMENTATION.md "Quick Reference" section}

---

## Blockers

{If any blockers exist, list them}
{If no blockers: "No blockers"}

---

## Notes

{checkpoint.notes}

---

## Next Steps

{Suggested next actions based on status}

---

## Quick Commands

- Mark task complete: /planning/checkpoint --complete-task "description"
- Move to next phase: /planning/checkpoint --next-phase
- View full plan: Read {FEATURE_PATH}/IMPLEMENTATION.md
- View all tasks: Read {FEATURE_PATH}/TASKS.md
- View progress: /planning/progress
```

## Command Usage Examples

```bash
# Switch to e2e_file_testing feature
/planning/goto-feature e2e_file_testing

# Switch to core_rule_engine feature
/planning/goto-feature core_rule_engine

# Switch to api_upload_endpoints feature
/planning/goto-feature api_upload_endpoints
```

## Error Handling

### Feature Not Found

```
❌ Feature 'unknown_feature' not found

Did you mean:
- e2e_file_testing (E1_CORE_VALIDATION)
- core_rule_engine (E1_CORE_VALIDATION)

Available features:
Run: find specs/milestones -name ".checkpoint" -type f
```

### Multiple Matches

```
⚠️  Multiple features found with name '{feature_name}':

1. specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/{feature_name}
2. specs/milestones/M2_SECURITY_COMPLIANCE/epics/E3_RBAC/features/{feature_name}

Please specify the full path or use a more specific name.
```

### No .checkpoint File

```
❌ Feature exists but has no .checkpoint file

Location: {feature_path}

This feature may have been created manually. Create a checkpoint file using:
/planning/new-feature
```

## Important Notes

- This command changes the "active" feature context
- Updates `specs/.checkpoints/current.json` (gitignored)
- Loads minimal context (< 500 lines total)
- Does NOT modify any feature state (read-only context switch)
- Use `/planning/resume` after `/clear` to restore current context
- Use `/planning/status` to see current feature without switching
