# Update checkpoint progress for the active feature

**Command Format:**

```
/planning-checkpoint [--flag] [value]
```

**Supported Flags:**

1. `--complete-task "task description"` - Mark a task as complete in current phase
2. `--next-phase` - Complete current phase and move to next
3. `--add-blocker "blocker description"` - Add a blocker
4. `--remove-blocker "blocker description"` - Remove a blocker
5. `--complete-feature` - Mark entire feature as completed
6. `--start-phase N` - Start a specific phase (sets current_phase)
7. `--update-note "note text"` - Update the notes field

**Your task:**

1. Read `specs/.checkpoints/current.json` to find active feature

2. Read the feature's `.checkpoint` file to get current state

3. Based on the flag provided, update the checkpoint:

   **For --complete-task:**

   - Increment `tasks_completed` for current phase
   - Calculate time since `session_started`, add to `time_spent_minutes` for phase and feature
   - Update `session_started` to current time (new session)
   - Update `last_updated` timestamp
   - Write updated .checkpoint file

   **For --next-phase:**

   - Mark current phase as `completed`
   - Set `completed_at` for current phase
   - Increment `current_phase` by 1
   - Set next phase `status` to `in_progress`
   - Set next phase `started_at`
   - Update `session_started` to current time
   - Update `last_updated` timestamp

   **For --add-blocker:**

   - Append blocker to `blockers` list with timestamp
   - Optionally set feature `status` to `blocked` if critical

   **For --remove-blocker:**

   - Remove blocker from list
   - If no blockers remain and status = blocked, set status back to in_progress

   **For --complete-feature:**

   - Set feature `status` to `completed`
   - Mark all remaining phases as `completed`
   - Calculate final time totals
   - Update `last_updated` timestamp

   **For --start-phase:**

   - Set `current_phase` to specified number
   - Set that phase `status` to `in_progress`
   - Set `started_at` for that phase
   - Set feature `status` to `in_progress` if not_started

4. Write the updated checkpoint using atomic write (temp file → rename):

   ```python
   import tempfile
   import shutil

   # Write to temp file
   with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=checkpoint_dir) as tmp:
       yaml.dump(data, tmp)
       tmp_path = tmp.name

   # Atomic rename
   shutil.move(tmp_path, checkpoint_path)
   ```

5. Display confirmation:

```
## Checkpoint Updated

Feature: [feature_name]
Action: [what was updated]
Progress: [X]% complete ([tasks]/[total] tasks)

### Current State

Phase [N]: [phase_name]
Status: [status]
Tasks: [completed]/[total]
Time: [minutes] minutes

### Next Steps

- Continue work: /planning-resume
- View progress: /planning-progress
- Update again: /planning-checkpoint [flag]
```

**If no flag provided:**
Show usage help with examples:

```
Usage: /planning-checkpoint [--flag] [value]

Examples:
  /planning-checkpoint --complete-task "Implement save_profiling_snapshot()"
  /planning-checkpoint --next-phase
  /planning-checkpoint --add-blocker "Waiting for API approval"
  /planning-checkpoint --complete-feature

Available flags:
  --complete-task "description"  Mark task complete
  --next-phase                   Move to next phase
  --add-blocker "description"    Add blocker
  --remove-blocker "description" Remove blocker
  --complete-feature             Mark feature done
  --start-phase N                Start specific phase
  --update-note "text"           Update notes
```

**Critical Implementation Details:**

1. **Time Tracking Logic:**

   ```python
   if checkpoint['session_started']:
       session_duration = (datetime.now() - session_started).total_seconds() / 60
       checkpoint['time_spent_minutes'] += session_duration
       current_phase['time_spent_minutes'] += session_duration
   checkpoint['session_started'] = datetime.now().isoformat()
   ```

2. **Atomic Writes:**
   Always use temp file → rename to prevent corruption

3. **Validation:**

   - Check phase number is valid (1-7)
   - Check tasks_completed doesn't exceed tasks_total
   - Validate status transitions (not_started → in_progress → completed)

4. **Regenerate Parent Progress Files:**
   After updating checkpoint, regenerate:
   - Parent epic's `PROGRESS.md`
   - Parent milestone's `PROGRESS.md`
     (This can be a future enhancement - skip for now if complex)
