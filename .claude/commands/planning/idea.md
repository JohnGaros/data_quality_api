# Quick Idea Capture

Capture a rough idea to IDEAS.md for later exploration.

## Arguments

$ARGUMENTS = The idea description to capture

## Instructions

1. **Read current IDEAS.md** to get the next ID:
   - Look for `<!-- Next ID: IDEA-NNN -->` comment
   - Extract NNN as the next available ID

2. **Append the new idea** to IDEAS.md with format:
   ```markdown
   ## IDEA-NNN: <summary>

   **Captured:** YYYY-MM-DD HH:MM
   **Status:** new
   **Tags:** <!-- add relevant tags -->

   <full description from $ARGUMENTS>

   ---
   ```

3. **Update the Next ID** comment to IDEA-(NNN+1)

4. **Confirm to user:**
   ```
   Captured IDEA-NNN: <summary>

   Next steps:
   - `/planning/draft IDEA-NNN` to explore further
   - `/planning/promote IDEA-NNN` to promote directly to feature
   - `/planning/drafts` to see all ideas
   ```

## Example

User: `/planning/idea Add real-time validation feedback via WebSockets`

Result in IDEAS.md:
```markdown
## IDEA-001: Real-time validation feedback via WebSockets

**Captured:** 2025-12-03 14:30
**Status:** new
**Tags:** <!-- add relevant tags -->

Add real-time validation feedback via WebSockets

---
```
