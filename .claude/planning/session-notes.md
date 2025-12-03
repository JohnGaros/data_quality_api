# Session Notes Management

You are helping the user manage session scratch notes that persist across `/clear` operations.

## Command Formats

```bash
# View current notes (default)
/planning/session-notes

# Add to scratch
/planning/session-notes --add "note text"

# Update active context
/planning/session-notes --context "new focus area"

# Add to parking lot
/planning/session-notes --park "thing to not forget"

# Add exploring file
/planning/session-notes --exploring "path/to/file.py"

# Clear notes (start fresh)
/planning/session-notes --clear
```

## File Format

The session notes are stored in `specs/drafts/.session_notes` as YAML:

```yaml
session_id: "2025-12-02T09:00:00Z"
last_updated: "2025-12-02T14:30:00Z"

active_context: |
  Current focus area or working memory.
  Can be multiple lines.

scratch:
  - "First note"
  - "Second note"
  - "Third note"

exploring_files:
  - "src/dq_catalog/repository.py"
  - "docs/ARCHITECTURE.md"

parking_lot:
  - "Thing to not forget 1"
  - "Thing to not forget 2"
```

---

## Operation: View Notes (Default)

If no flags provided, display the current session notes.

### Step 1: Read File

Read `specs/drafts/.session_notes`.
If file doesn't exist or session_id is null, show empty state.

### Step 2: Calculate Time

If session_id exists, calculate time since session started.
If last_updated exists, calculate time since last update.

### Step 3: Display

```
## Session Notes

**Session started:** {session_id} ({relative time} ago)
**Last updated:** {last_updated} ({relative time} ago)

---

### Active Context

{active_context or "No active context set."}

---

### Scratch Notes ({count})

{For each item in scratch:}
- {note}

{If empty:}
No scratch notes. Add with: /planning/session-notes --add "note"

---

### Exploring Files ({count})

{For each file in exploring_files:}
- {file_path}

{If empty:}
No files tracked. Add with: /planning/session-notes --exploring "path"

---

### Parking Lot ({count})

{For each item in parking_lot:}
- [ ] {item}

{If empty:}
Parking lot empty. Add with: /planning/session-notes --park "reminder"

---

### Quick Commands

- Add note: /planning/session-notes --add "note"
- Set context: /planning/session-notes --context "focus"
- Park item: /planning/session-notes --park "reminder"
- Track file: /planning/session-notes --exploring "path"
- Clear all: /planning/session-notes --clear
```

---

## Operation: Add Note (--add)

### Step 1: Read File

Read `specs/drafts/.session_notes`.

### Step 2: Initialize if Needed

If session_id is null, set it to current timestamp.

### Step 3: Append Note

Add the note text to the `scratch` list.

### Step 4: Update Timestamps

Set `last_updated` to current timestamp.

### Step 5: Write File

Write updated YAML back to file.

### Step 6: Confirm

```
Added to scratch: "{note text}"

Total scratch notes: {count}
```

---

## Operation: Update Context (--context)

### Step 1: Read File

Read `specs/drafts/.session_notes`.

### Step 2: Initialize if Needed

If session_id is null, set it to current timestamp.

### Step 3: Replace Context

Replace `active_context` with the new text.

### Step 4: Update Timestamps

Set `last_updated` to current timestamp.

### Step 5: Write File

Write updated YAML back to file.

### Step 6: Confirm

```
Active context updated.

New context:
{First 3 lines of context}

Use /planning/session-notes to view all notes.
```

---

## Operation: Park Item (--park)

### Step 1: Read File

Read `specs/drafts/.session_notes`.

### Step 2: Initialize if Needed

If session_id is null, set it to current timestamp.

### Step 3: Append to Parking Lot

Add the item to the `parking_lot` list.

### Step 4: Update Timestamps

Set `last_updated` to current timestamp.

### Step 5: Write File

Write updated YAML back to file.

### Step 6: Confirm

```
Parked: "{item}"

Parking lot ({count} items):
- [ ] {item 1}
- [ ] {item 2}
- [ ] {new item}
```

---

## Operation: Track File (--exploring)

### Step 1: Read File

Read `specs/drafts/.session_notes`.

### Step 2: Initialize if Needed

If session_id is null, set it to current timestamp.

### Step 3: Add File Path

Add the path to `exploring_files` list (avoid duplicates).

### Step 4: Update Timestamps

Set `last_updated` to current timestamp.

### Step 5: Write File

Write updated YAML back to file.

### Step 6: Confirm

```
Tracking: {file_path}

Exploring files ({count}):
- {file 1}
- {file 2}
- {new file}
```

---

## Operation: Clear Notes (--clear)

### Step 1: Confirm Intent

This is destructive. Ask for confirmation:

Use AskUserQuestion:
- Question: "Clear all session notes? This cannot be undone."
- Header: "Confirm"
- Options:
  - label: "Yes, clear all", description: "Start fresh with empty notes"
  - label: "Archive first", description: "Save to archive before clearing"
  - label: "Cancel", description: "Keep current notes"

### Step 2: Archive (if requested)

If user selected "Archive first":
- Create `specs/drafts/.session_notes_archive/` if not exists
- Copy current file to `specs/drafts/.session_notes_archive/{timestamp}.yaml`

### Step 3: Reset File

Write fresh session notes file:

```yaml
session_id: null
last_updated: null

active_context: |
  No active context. Use /planning/session-notes --context "your focus" to set.

scratch: []

exploring_files: []

parking_lot: []
```

### Step 4: Confirm

```
Session notes cleared.

{If archived:}
Previous notes archived to: specs/drafts/.session_notes_archive/{timestamp}.yaml

Start fresh:
- Set context: /planning/session-notes --context "focus"
- Add notes: /planning/session-notes --add "note"
```

---

## Empty State

If viewing notes with no session:

```
## Session Notes

No active session.

Session notes help you:
- Track your current focus across /clear operations
- Keep scratch notes that don't belong anywhere yet
- Remember files you're exploring
- Park things you don't want to forget

Get started:
- Set context: /planning/session-notes --context "what you're working on"
- Add note: /planning/session-notes --add "quick thought"
```

---

## Important Notes

- Session notes are gitignored (personal working memory)
- The file survives `/clear` operations
- Use `--clear` to start a fresh session (e.g., new day)
- Timestamps use ISO 8601 format
- YAML format allows multi-line active_context
- Archive is optional - most users just clear without archiving
- Keep notes concise - this is scratch space, not documentation
