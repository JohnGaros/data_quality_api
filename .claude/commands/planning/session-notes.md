# Session Notes Management

Manage ephemeral session scratch notes for brainstorming and working memory.

## Arguments

$ARGUMENTS = Action and optional content:
- (empty) - Display current session notes
- `--add <note>` - Add a scratch note
- `--context <focus>` - Set active context/focus
- `--park <item>` - Add to parking lot (don't forget)
- `--file <path>` - Track file being explored
- `--clear` - Clear all session notes

## Instructions

### Display Session Notes (no args)

Read `.session_notes` and display:
```
================================================================================
SESSION NOTES
================================================================================

Session ID: 2025-12-03-1430
Last Updated: 2025-12-03 14:45

ACTIVE CONTEXT
──────────────────────────────────────────────────────────────────────────────────
Exploring WebSocket implementation options for real-time validation feedback

SCRATCH NOTES
──────────────────────────────────────────────────────────────────────────────────
- FastAPI has native WebSocket support
- Consider using channels pattern
- Need to handle tenant isolation in WS connections

EXPLORING FILES
──────────────────────────────────────────────────────────────────────────────────
- src/dq_api/routes/validation.py
- src/dq_core/engine/rule_engine.py

PARKING LOT (Don't Forget!)
──────────────────────────────────────────────────────────────────────────────────
- Check if Azure SignalR is better than raw WebSockets
- Ask John about infrastructure budget for persistent connections

================================================================================
```

### Add Scratch Note (`--add`)

1. Parse note from arguments after `--add`
2. Append to `scratch` array in `.session_notes`
3. Update `last_updated` timestamp
4. Display confirmation

### Set Context (`--context`)

1. Parse focus from arguments after `--context`
2. Replace `active_context` in `.session_notes`
3. Update `last_updated` timestamp
4. Display confirmation

### Add to Parking Lot (`--park`)

1. Parse item from arguments after `--park`
2. Append to `parking_lot` array in `.session_notes`
3. Update `last_updated` timestamp
4. Display confirmation

### Track File (`--file`)

1. Parse path from arguments after `--file`
2. Append to `exploring_files` array (avoid duplicates)
3. Update `last_updated` timestamp
4. Display confirmation

### Clear Session (`--clear`)

1. Reset `.session_notes` to initial state:
   ```yaml
   session_id: null
   last_updated: null
   active_context: |
     No active context. Use /planning/session-notes --context "your focus" to set.
   scratch: []
   exploring_files: []
   parking_lot: []
   ```
2. Confirm to user

## Session Notes File Format

`.session_notes` is YAML:
```yaml
session_id: "2025-12-03-1430"
last_updated: "2025-12-03T14:45:00Z"

active_context: |
  Exploring WebSocket implementation options for real-time validation feedback

scratch:
  - "FastAPI has native WebSocket support"
  - "Consider using channels pattern"
  - "Need to handle tenant isolation in WS connections"

exploring_files:
  - "src/dq_api/routes/validation.py"
  - "src/dq_core/engine/rule_engine.py"

parking_lot:
  - "Check if Azure SignalR is better than raw WebSockets"
  - "Ask John about infrastructure budget"
```

## Integration with Brainstorming

Session notes are:
- **Ephemeral**: Cleared between sessions or on `/clear`
- **Not committed**: `.session_notes` is gitignored
- **Transferable**: Can be copied to draft docs via `/planning/brainstorm --save`
